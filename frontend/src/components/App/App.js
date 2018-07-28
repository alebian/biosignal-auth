import React, { PureComponent } from 'react';
import jwt_decode from 'jwt-decode';
import PropTypes from 'prop-types';

import './App.css';

class App extends PureComponent {
  render() {
    return (
      <div className="col-sm-10 offset-md-1">
        <div className="alert alert-success" role="alert">
          Logueado correctamente. {this.props.loginPercentage && `Porcentaje de similitud: %${parseInt(this.props.loginPercentage * 100, 10)}`}
        </div>
        <h2>Bienvenido {jwt_decode(this.props.token).email}!</h2>

      </div>
    );
  }
}

App.propTypes = {
  loginPercentage: PropTypes.string.isRequired,
  token: PropTypes.string.isRequired,
};

export default App;
