import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './Form.css';
import ClientService from '../../services/clientService';
import SignalService from '../../services/signalService';
import CustomChart from '../CustomChart/CustomChart';
import SettingsSliders from '../SettingsSliders/SettingsSliders';
import RefreshIcon from '../../assets/refresh.png';

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
      settings: {
        windowSize: 50,
        spikeThreshold: 650,
        zeroThreshold: 250,
        zeroLength: 500,
      }
    };
  }

  handlePasswordChange = event => {
    this.setState({password: event.target.value});
  };

  handleEmailChange = event => {
    this.setState({email: event.target.value});
  };

  handleSettingChange = (label, value) => {
    const newSettings = { ...this.state.settings };
    newSettings[label] = value;
    this.setState({
      settings: newSettings
    });
    SignalService.updateSettings(this.state.readerIP, newSettings.windowSize, newSettings.spikeThreshold, newSettings.zeroThreshold, newSettings.zeroLength)
      .then(response => {
        if (response.status === 200) {
          console.log('Settings changed');
          console.log(response.data);
        }
      });
  }

  handleWindowSizeChange = value => {
    this.handleSettingChange('windowSize', value);
  };

  handleSpikeThresholdChange = value => {
    this.handleSettingChange('spikeThreshold', value);
  };

  handleZeroThresholdChange = value => {
    this.handleSettingChange('zeroThreshold', value);
  };

  handleZeroLengthChange = value => {
    this.handleSettingChange('zeroLength', value);
  };

  deviceName = device => `${device.name} ${device.ip}`;

  handleDeviceChange = event => {
    const name = event.target.value;
    const device = this.state.deviceOptions.filter(a => a.name === name)[0];
    this.setState({
      readerIP: device.ip
    }, () => {
      SignalService.getSettings(this.state.readerIP)
        .then(response => {
          this.setState({
            settings: {
              windowSize: response.data.window_size,
              spikeThreshold: response.data.spike_threshold,
              zeroThreshold: response.data.zero_threshold,
              zeroLength: response.data.zero_length,
            }
          });
        });
    });
  };

  startReading = () => {
    SignalService.start(this.state.readerIP)
      .then(response => {
        if (response.status === 201) {
          this.setState({started: true, signalUUID: response.data.signalUUID, readyToSend: false}, () => window.scrollTo(0, document.body.scrollHeight));
        } else {
          console.log(`Unexpected response code ${response.status}`);
        }
      });
  };

  stopReading = () => {
    SignalService.stop(this.state.readerIP, this.state.signalUUID)
      .then(response => {
        if (response.status === 200) {
          this.setState({started: false});
          this.checkIfSignalArrived();
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      });
  };

  checkIfSignalArrived = () => {
    this.timer = setInterval(() => {
      if (!this.state.readyToSend) {
        ClientService.signalExist(this.state.signalUUID)
          .then(response => this.setState({ readyToSend: true }));
      }
    }, 500);
  };

  refreshItems = () => {
    ClientService.devices()
      .then(response => {
        const mapped_response = response.data.map(info => ({ name: info.id, ip: info.ip_address }));
        mapped_response.unshift({name: '', ip: ''});
        this.setState({
          deviceOptions: mapped_response
        });
      });
  };

  cancelReading = () => {
    this.setState({
      started: false,
      signalUUID: '',
    });
    SignalService.cancel(this.state.readerIP, this.state.signalUUID);
  };

  componentDidMount() {
    this.refreshItems();
  }

  componentWillUnmount() {
    if (this.state.started && this.state.signalUUID) {
      this.cancelReading();
    }
  }

  render() {
    const readerOptions = this.state.deviceOptions.map(deviceInfo => {
      return (
        <option key={deviceInfo.name} value={deviceInfo.name}>
          {this.deviceName(deviceInfo)}
        </option>
      );
    });

    return (
      <div className="col-sm-10 offset-md-1">
        <div className="flex-column">
          {
            (this.state.error || this.props.externalError) &&
              <div className="alert alert-danger" role="alert">{this.state.error || this.props.externalError}</div>
          }
          <div className="FormInputs">
            <div className="form-group">
              <label htmlFor="emailInput">Email</label>
              <input type="email" className="form-control" value={this.state.email} onChange={this.handleEmailChange} />
            </div>

            <div className="form-group">
              <label htmlFor="passwordInput">Contraseña</label>
              <input type="password" className="form-control" value={this.state.password} onChange={this.handlePasswordChange} />
            </div>

            <div className="form-group">
              <label htmlFor="passwordInput">Dispositivo</label>
              <div className="DevicesSelect">
                <select className="form-control" onChange={this.handleDeviceChange}>
                  {readerOptions}
                </select>
                <img src={RefreshIcon} onClick={this.refreshItems} />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="tokenInput">ID de señal</label>
              <input type="text" className="form-control" id="tokenInput" value={this.state.signalUUID} disabled />
            </div>
          </div>

          <div className="FormButtonInputs">
            {
              this.state.started
              ? [
                  <button className="btn btn-info" onClick={this.stopReading}>Parar</button>,
                  <button className="btn btn-danger" onClick={this.cancelReading}>Cancelar</button>
                ]
              : <button className="btn btn-info" disabled={!this.state.readerIP} onClick={this.startReading}>Comenzar lectura</button>
            }
          </div>

          <div className="FormChartsContainer">
            {
              this.state.readerIP &&
                [
                  <SettingsSliders
                    windowSize={this.state.settings.windowSize}
                    spikeThreshold={this.state.settings.spikeThreshold}
                    zeroThreshold={this.state.settings.zeroThreshold}
                    zeroLength={this.state.settings.zeroLength}
                    onWindowSizeChange={this.handleWindowSizeChange}
                    onSpikeThresholdChange={this.handleSpikeThresholdChange}
                    // onZeroThresholdChange={this.handleZeroThresholdChange}
                    onZeroLengthChange={this.handleZeroLengthChange}
                  />,
                  <div>
                    {
                      this.state.signalUUID &&
                        <CustomChart reading={this.state.started} url={this.state.readerIP} token={this.state.signalUUID} />
                    }
                  </div>
                ]
            }
          </div>
          {
            this.state.signalUUID &&
              <div className="SubmitContainer">
                <button disabled={!this.state.readyToSend} className="btn btn-primary" onClick={() => this.props.onSubmit(this.state.email, this.state.password, this.state.signalUUID)}>
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
          }
        </div>
      </div>
    );
  }
}

Form.defaultProps = {
  submitText: 'Enviar',
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
