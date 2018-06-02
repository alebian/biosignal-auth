import React, { Component } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import './Form.css';

const READERAPP_URL = 'http://localhost:5001/api/v1';

class Form extends Component {
  constructor(props) {
    super(props);
    this.state = {
      started: false,
      error: undefined,
      email: '',
      password: '',
      signalToken: ''
    };
  }

  handlePasswordChange = event => {
    this.setState({password: event.target.value});
  };

  handleEmailChange = event => {
    this.setState({email: event.target.value});
  };

  startReading = () => {
    axios.post(`${READERAPP_URL}/start`)
      .then(response => {
        if (response.status === 201) {
          this.setState({started: true, signalToken: response.data.signalToken});
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
    axios.post(`${READERAPP_URL}/stop`, {signalToken: this.state.signalToken})
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

  componentWillUnmount() {
    if (this.state.started && this.state.signalToken) {
      axios.post(`${READERAPP_URL}/cancel`, {signalToken: this.state.signalToken})
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
            ? <div className="alert alert-warning" role="alert">{this.state.error || this.props.externalError}</div>
            : null
        }
        <form>
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
            <label htmlFor="tokenInput">Signal Token</label>
            <input
              type="text"
              className="form-control"
              id="tokenInput"
              value={this.state.signalToken}
              disabled
            />
          </div>
          {
            this.state.started
            ? <button className="btn btn-info" onClick={this.stopReading}>Stop reading</button>
            : <button className="btn btn-info" onClick={this.startReading}>Start reading</button>
          }
          <br/>
          <br/>
          <button
            className="btn btn-primary"
            onClick={() => this.props.onSubmit({email: this.state.email, password: this.state.password, signalToken: this.state.signalToken})}
          >
            {this.props.submitText}
          </button>
        </form>
      </div>
    );
  }
}

Form.defaultProps = {
  submitText: 'Submit',
};

Form.propTypes = {
  externalError: PropTypes.string,
  submitText: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

export default Form;
