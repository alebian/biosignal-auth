import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import Slider from 'react-rangeslider';

import './CustomSlider.css';

class CustomSlider extends PureComponent {
  render() {
    return (
      <div className="SliderContainer">
        {
          this.props.text && <p>{this.props.text} <bold>({this.props.value})</bold></p>
        }
        <Slider
          value={this.props.value}
          orientation={this.props.orientation}
          onChange={this.props.onChange}
          min={this.props.min}
          max={this.props.max}
          step={this.props.step}
          tooltip={this.props.tooltip}
        />
      </div>
    );
  }
}

CustomSlider.defaultProps = {
  text: '',
  max: 2000,
  min: 0,
  step: 10,
  orientation: 'horizontal',
  tooltip: false,
};

CustomSlider.propTypes = {
  value: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  text: PropTypes.string,
  max: PropTypes.number,
  min: PropTypes.number,
  step: PropTypes.number,
  orientation: PropTypes.string,
  tooltip: PropTypes.bool,
};

export default CustomSlider;
