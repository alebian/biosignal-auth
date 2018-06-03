import React, { Component } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

import ReactChartkick, { ScatterChart } from 'react-chartkick';
import Chart from 'chart.js';

ReactChartkick.addAdapter(Chart);

const READERAPP_URL = 'http://localhost:5001/api/v1';

class CustomChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      values: [],
    };
  }

  componentDidMount() {
    this.timer = setInterval(() => {
      axios
        .get(`${READERAPP_URL}/read?signalToken=${this.props.token}`)
        .then(response => this.setState({ values: response.data }))
        .catch(error => console.log(error));
    }, 500);
  }

  componentWillUnmount() {
    clearInterval(this.timer);
  }

  render() {
    return (
      <ScatterChart
        data={this.state.values}
        width="500px"
        height="300px"
      />
    );
  }
}

CustomChart.propTypes = {
  token: PropTypes.string.isRequired,
};

export default CustomChart;
