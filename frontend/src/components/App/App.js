import React, { Component } from 'react';
import jwt_decode from 'jwt-decode';

import './App.css';
import ClientService from '../../services/clientService';
import Form from '../Form/Form'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      logged: false,
      registerMenu: false,
      error: undefined,
      token: undefined,
      loginPercentage: undefined,
      loginMessage: undefined,
    };
  }

  handleRegisterSubmit = (email, password, signalToken) => {
    ClientService.register(email, password, signalToken)
      .then(response => {
        if (response.status === 201) {
          this.setState({logged: true, token: response.data.token});
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      })
      .catch(error => {
        this.setState({error: 'There was an error'});
        console.log(error);
      });
  }

  handleLoginSubmit = (email, password, signalToken) => {
    ClientService.login(email, password, signalToken)
      .then(response => {
        if (response.status === 200) {
          this.setState({
            logged: true,
            token: response.data.token,
            loginPercentage: response.data.percentage,
            loginMessage: response.data.message
          });
        } else {
          console.log(`Unexpected response code ${response.status}`);
        }
      })
      .catch(error => {
        if (error.response && error.response.status === 401) {
          this.setState({
            error: `${error.response.data.message} - Signal percentage: %${parseInt(error.response.data.percentage * 100, 10)}`
          });
        } else {
          console.log(error);
        }
      });
  }

  switchRegisterMenu = () => {
    this.setState(prevState => ({registerMenu: !prevState.registerMenu, error: undefined}));
  }

  render() {
    return (
      <div className="App container">
        <div className="row">
          <div className="col-sm-6 offset-md-3">
            <h1>BAD Client demo</h1>
          </div>
        </div>
        <div className="row">
          {this.state.logged
            ?
              <div className="col-sm-8 offset-md-1">
                <h2 className="LoginMessage">{this.state.loginMessage}</h2>
                {
                  this.state.loginPercentage && <h2 className="LoginPercentage">Porcenaje de similitud: %{parseInt(this.state.loginPercentage * 100, 10)}</h2>
                }
                <h4>Email: {jwt_decode(this.state.token).email}</h4>
              </div>
            : (
              <div className="col-sm-8 offset-md-1">
                <Form
                  onSubmit={this.state.registerMenu ? this.handleRegisterSubmit : this.handleLoginSubmit}
                  submitText={this.state.registerMenu ? 'Registrarse' : 'Inicial sesión'}
                  externalError={this.state.error}
                  belowSubmitText1={this.state.registerMenu ? 'Ya tenés una cuenta?' : "No tenés una cuenta?"}
                  belowSubmitText2={this.state.registerMenu ? 'Inicial sesión' : 'Registrate'}
                  onBelowSubmitClick={this.switchRegisterMenu}
                />
              </div>
              )
           }
        </div>
      </div>
    );
  }
}

export default App;
