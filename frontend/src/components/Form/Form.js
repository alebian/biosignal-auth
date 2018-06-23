import React, { Component } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';

import './Form.css';
import CustomChart from '../CustomChart/CustomChart';

const WEBAPP_URL = 'http://localhost:8000/api/v1';

class Form extends Component {
  constructor(props) {
    super(props);
    this.state = {
      started: false,
      error: undefined,
      email: undefined,
      password: undefined,
      deviceOptions: [],
      signalUUID: undefined,
      readyToSend: false,
      readerIP: undefined,
    };
  }

  handlePasswordChange = event => {
    this.setState({password: event.target.value});
  };

  handleEmailChange = event => {
    this.setState({email: event.target.value});
  };

  deviceName = device => `${device.name} ${device.ip}`;

  handleDeviceChange = event => {
    const name = event.target.value;
    const device = this.state.deviceOptions.filter(a => a.name === name)[0];
    this.setState({
      readerIP: device.ip
    });
  };

  startReading = () => {
    axios.post(`http://${this.state.readerIP}:5001/api/v1/start`)
      .then(response => {
        if (response.status === 201) {
          this.setState({started: true, signalUUID: response.data.signalUUID, readyToSend: false});
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      })
      .catch(error => {
        this.setState({error: 'There was an error'});
        console.log(error);
      });
  };

  stopReading = () => {
    axios.post(`http://${this.state.readerIP}:5001/api/v1/stop`, {signalUUID: this.state.signalUUID})
      .then(response => {
        if (response.status === 200) {
          this.setState({started: false});
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      })
      .catch(error => {
        this.setState({error: 'There was an error'});
        console.log(error);
      });
  };

  checkIfSignalArrived = () => {
    this.timer = setInterval(() => {
      if (!this.state.readyToSend) {
        axios
          .get(`${WEBAPP_URL}/signal/${this.state.signalUUID}`)
          .then(response => this.setState({ readyToSend: true }))
          .catch(error => console.log(error));
      }
    }, 500);
  };

  componentDidMount() {
    axios.get(`${WEBAPP_URL}/devices`)
      .then(response => {
        this.setState({
          deviceOptions: response.data.map(info => ({ name: info.id, ip: info.ip_address }))
        });
      })
      .catch(error => {
        console.log(`Error fetching devices: ${error}`);
      });
  }

  componentWillUnmount() {
    if (this.state.started && this.state.signalUUID) {
      axios.post(`http://${this.state.readerIP}:5001/api/v1/cancel`, {signalUUID: this.state.signalUUID})
      .then(response => {
        console.log('Successfully canceled reading');
      })
      .catch(error => {
        console.log(`Error canceling reading: ${error}`);
      });
    }
  }

  render() {
    return (
      <div>
        {
          this.state.error || this.props.externalError
            ? <div className="alert alert-danger" role="alert">{this.state.error || this.props.externalError}</div>
            : null
        }
        <div className="horizontal-split">
          <div>
            <div className="form-group">
              <label htmlFor="emailInput">Email</label>
              <input
                type="email"
                className="form-control"
                id="emailInput"
                aria-describedby="emailHelp"
                placeholder="johndoe@example.com"
                value={this.state.email}
                onChange={this.handleEmailChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="passwordInput">Password</label>
              <input
                type="password"
                className="form-control"
                id="passwordInput"
                value={this.state.password}
                onChange={this.handlePasswordChange}
              />
            </div>
            <div className="form-group">
              <select className="form-control" onChange={this.handleDeviceChange}>
                {
                  this.state.deviceOptions.map(deviceInfo => <option key={deviceInfo.name} value={deviceInfo.name}>{this.deviceName(deviceInfo)}</option>)
                }
              </select>
            </div>
            {
              this.state.readerIP
              ? <div>
                  <div className="form-group">
                    <label htmlFor="tokenInput">Signal Token</label>
                    <input
                      type="text"
                      className="form-control"
                      id="tokenInput"
                      value={this.state.signalUUID}
                      disabled
                    />
                  </div>
                  {
                    this.state.started
                    ? <button className="btn btn-info" onClick={this.stopReading}>Stop reading</button>
                    : <button className="btn btn-info" onClick={this.startReading}>Start reading</button>
                  }
                </div>
              : null
            }
          </div>
          <div className="chart-container">
            {
              this.state.readerIP && this.state.signalUUID &&
              <CustomChart
                reading={this.state.started}
                url={`http://${this.state.readerIP}:5001/api/v1/read`}
                token={this.state.signalUUID}
              />
            }
          </div>
        </div>
        <br/>
        <button
          disabled={!this.state.readyToSend}
          className="btn btn-primary"
          onClick={() => this.props.onSubmit({email: this.state.email, password: this.state.password, signal_token: this.state.signalUUID})}
        >
          {this.props.submitText}
        </button>
        <p className="form-text text-muted">
          {this.props.belowSubmitText1}
          {' '}
          <a className="Link" onClick={this.props.onBelowSubmitClick}>
            {this.props.belowSubmitText2}
          </a>
        </p>
      </div>
    );
  }
}

Form.defaultProps = {
  submitText: 'Submit',
};

Form.propTypes = {
  externalError: PropTypes.string,
  submitText: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
  belowSubmitText1: PropTypes.string.isRequired,
  belowSubmitText2: PropTypes.string.isRequired,
  onBelowSubmitClick: PropTypes.func.isRequired,
};

export default Form;
