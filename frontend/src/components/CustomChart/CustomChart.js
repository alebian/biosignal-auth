import React, { Component } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

import ReactChartkick, { LineChart } from 'react-chartkick';
import Chart from 'chart.js';

ReactChartkick.addAdapter(Chart);

class CustomChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      values: [],
    };
  }

  componentDidMount() {
    if (this.props.url && this.props.token) {
      this.timer = setInterval(() => {
        if (this.props.reading) {
          axios
            .get(`${this.props.url}?signalUUID=${this.props.token}`)
            .then(response => this.setState({ values: response.data }))
            .catch(error => console.log(error));
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
      <LineChart
        data={this.state.values}
        width="500px"
        height="300px"
      />
    );
  }
}

CustomChart.propTypes = {
  reading: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
  token: PropTypes.string.isRequired,
};

export default CustomChart;
