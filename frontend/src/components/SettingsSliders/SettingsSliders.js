import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';

import './SettingsSliders.css';
import CustomSlider from '../CustomSlider/CustomSlider';

class SettingsSliders extends PureComponent {
  render() {
    return (
      <div className="SlidersContainer">
        <CustomSlider
          value={this.props.windowSize}
          onChange={this.props.onWindowSizeChange}
          text="Tamaño ventana"
          max={300}
        />
        <CustomSlider
          value={this.props.spikeThreshold}
          onChange={this.props.onSpikeThresholdChange}
          text="Umbral de pico"
          max={1023}
        />
        {/* <CustomSlider
          value={this.props.zeroThreshold}
          onChange={this.handleZeroThresholdChange}
          text="Umbral de cero"
          max={1023}
        /> */}
        <CustomSlider
          value={this.props.zeroLength}
          onChange={this.props.onZeroLengthChange}
          text="Longitud de cero"
        />
      </div>
    );
  }
}

SettingsSliders.defaultProps = {
};

SettingsSliders.propTypes = {
  windowSize: PropTypes.number.isRequired,
  spikeThreshold: PropTypes.number.isRequired,
  // zeroThreshold: PropTypes.number.isRequired,
  zeroLength: PropTypes.number.isRequired,
  onWindowSizeChange: PropTypes.func.isRequired,
  onSpikeThresholdChange: PropTypes.func.isRequired,
  // onZeroThresholdChange: PropTypes.func.isRequired,
  onZeroLengthChange: PropTypes.func.isRequired,
};

export default SettingsSliders;
