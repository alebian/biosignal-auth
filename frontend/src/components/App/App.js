import React, { PureComponent } from 'react';
import jwt_decode from 'jwt-decode';
import PropTypes from 'prop-types';

import './App.css';

class App extends PureComponent {
  render() {
    return (
      <div className="col-sm-8 offset-md-1">
        <h2 className="LoginMessage">{this.props.loginMessage}</h2>
        {
          this.props.loginPercentage && <h2 className="LoginPercentage">Porcenaje de similitud: %{parseInt(this.props.loginPercentage * 100, 10)}</h2>
        }
        <h4>Email: {jwt_decode(this.props.token).email}</h4>
      </div>
    );
  }
}

App.propTypes = {
  loginPercentage: PropTypes.string.isRequired,
  loginMessage: PropTypes.string.isRequired,
  token: PropTypes.string.isRequired,
};

export default App;
