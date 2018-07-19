import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './Tutorial.css';
import RefreshIcon from '../../assets/refresh.png';
import SignalService from '../../services/signalService';
import ClientService from '../../services/clientService';
import CustomChart from '../CustomChart/CustomChart';
import SettingsSliders from '../SettingsSliders/SettingsSliders';

class Tutorial extends Component {
  constructor(props) {
    super(props);
    this.state = {
      step: 1,
      readerIP: undefined,
      signalUUID: undefined,
      deviceOptions: [],
      started: false,
      settings: {
        windowSize: 0,
        spikeThreshold: 0,
        zeroThreshold: 0,
        zeroLength: 0,
      }
    };
  }

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

  stepForward = () => this.setState({ step: this.state.step + 1 });

  deviceName = device => `${device.name} ${device.ip}`;

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

  handleDeviceChange = event => {
    const name = event.target.value;
    const device = this.state.deviceOptions.filter(a => a.name === name)[0];
    this.setState({
      readerIP: device.ip,
      step: 2,
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
          this.setState({started: true, signalUUID: response.data.signalUUID}, () => window.scrollTo(0, document.body.scrollHeight));
        } else {
          console.log(`Unexpected response code ${response.status}`);
        }
      });
  };

  cancelReading = () => {
    this.setState({
      started: false,
      signalUUID: undefined,
    });
    SignalService.cancel(this.state.readerIP, this.state.signalUUID);
  };

  componentDidMount() {
    this.refreshItems();
  }

  componentWillUnmount() {
    if (this.state.signalUUID) {
      this.cancelReading();
    }
    this.setState({
      signalUUID: undefined,
      started: false,
    });
  }

  render() {
    const readerOptions = this.state.deviceOptions.map(deviceInfo => {
      return (
        <option key={deviceInfo.name} value={deviceInfo.name}>
          {this.deviceName(deviceInfo)}
        </option>
      );
    });

    let stepShow = null;

    if (this.state.step === 1) {
      stepShow =
        <div className="FirstStep">
          <h2>Primero, elige el dispositivo:</h2>
          <div className="form-group DevicesSelect">
            <select className="form-control" onChange={this.handleDeviceChange}>
              {readerOptions}
            </select>
            <img src={RefreshIcon} onClick={this.refreshItems} />
          </div>
        </div>;
    }
    else if (this.state.step === 2) {
      stepShow =
        <div className="SecondStep">
          <div className="InstructionsButtons">
            <h2>Segundo, colocate los electrodos:</h2>
            <button className="btn btn-primary" onClick={this.stepForward}>Continuar</button>
          </div>
          <div className="Instructions">
            <p>El electrodo marcado con la letra <strong>"D"</strong> es el de referencia.</p>
            <p>Los electrodos marcados con las letras <strong>"R"</strong> y <strong>"L"</strong> son los que mediran la señal.</p>
            <img src="https://ai2-s2-public.s3.amazonaws.com/figures/2017-08-08/a01c13d7403bdda5a635a4da3593b6c4725eb9e2/2-Figure3-1.png" />
          </div>
        </div>;
    }
    else if (this.state.step === 3) {
      stepShow =
        <div className="ThirdStep">
          <h2>Tercero, comienza a leer:</h2>
          <div className="SlidersExplanation">
            <p>Con los sliders que se encuentran abajo podrás personalizar la captura de la señal.</p>
            <p>El valor <strong>"Tamaño ventana"</strong> especifica la cantidad de puntos que tomará un pico.</p>
            <p>El valor <strong>"Umbral de pico"</strong> especifica el valor que debe superarse para considerar un 1.</p>
            <p>El valor <strong>"Longitud de cero"</strong> especifica cuantos valores de la señal sin un pico forman un 0.</p>
            <SettingsSliders
              windowSize={this.state.settings.windowSize}
              spikeThreshold={this.state.settings.spikeThreshold}
              zeroThreshold={this.state.settings.zeroThreshold}
              zeroLength={this.state.settings.zeroLength}
              onWindowSizeChange={this.handleWindowSizeChange}
              onSpikeThresholdChange={this.handleSpikeThresholdChange}
              // onZeroThresholdChange={this.handleZeroThresholdChange}
              onZeroLengthChange={this.handleZeroLengthChange}
            />
          </div>
          {
            this.state.signalUUID &&
              <div className="TutorialCharts">
                <CustomChart reading={this.state.started} url={this.state.readerIP} token={this.state.signalUUID} />
              </div>
          }
          <div className="TutorialButtonsContainer">
            <button className="btn btn-info" disabled={!this.state.readerIP} onClick={this.startReading}>Comenzar lectura</button>
            <button className="btn btn-danger" disabled={!this.state.started} onClick={this.cancelReading}>Cancelar</button>
            <button className="btn btn-warning" onClick={this.props.closeTutorial}>Cerrar tutorial</button>
          </div>
        </div>;
    }

    return (
      <div className="col-sm-10 offset-md-1">
        <div className="TutorialContainer">
          {stepShow}
        </div>
      </div>
    );
  }
}

Tutorial.propTypes = {
  closeTutorial: PropTypes.func.isRequired,
};

export default Tutorial;
