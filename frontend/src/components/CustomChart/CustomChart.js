import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './CustomChart.css';
import SignalService from '../../services/signalService';
import ReactChartkick, { LineChart } from 'react-chartkick';
import Chart from 'chart.js';

ReactChartkick.addAdapter(Chart);

class CustomChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      values: [],
      interpreted_values: [],
    };
  }

  componentDidMount() {
    if (this.props.url && this.props.token) {
      this.timer = setInterval(() => {
        if (this.props.reading) {
          SignalService.read(this.props.url, this.props.token)
            .then((response) => {
              if (response && response.status === 200) {
                this.setState({
                  values: response.data.signal,
                  interpreted_values: response.data.interpreted_signal,
                });
              }
            });
        }
      }, 500);
    }
  }

  componentWillUnmount() {
    clearInterval(this.timer);
    this.setState({ values: [] });
  }

  render() {
    return (
      <div className="ChartsContainer">
        <LineChart
          data={this.state.values}
          width="500px"
          height="225px"
        />
        <LineChart
          data={this.state.interpreted_values}
          width="500px"
          height="225px"
        />
      </div>
    );
  }
}

CustomChart.propTypes = {
  reading: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
  token: PropTypes.string.isRequired,
};

export default CustomChart;
