import React, { Component } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

import './App.css';
import Form from '../Form/Form'

const WEBAPP_URL = 'http://localhost:5000/api/v1';

const logSubmit = state => {
  console.log(
    `Form submitted:
     Email: ${state.formInfo.email}
     Password: ${state.formInfo.password}
     Signal Token: ${state.formInfo.signalToken}
     Signal: ${state.formInfo.signal}`
  );
};

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      logged: false,
      registerMenu: false,
      error: undefined,
      token: undefined,
      formInfo: {
        email: '',
        password: '',
        signalToken: '',
        signal: []
      }
    };
  }

  handlePasswordChange = event => {
    this.setState({formInfo: {...this.state.formInfo, password: event.target.value}});
  };

  handleEmailChange = event => {
    this.setState({formInfo: {...this.state.formInfo, email: event.target.value}});
  };

  handleSignalChange = signal => {
    this.setState({formInfo: {...this.state.formInfo, signal: signal}});
  };

  handleSignalTokenChange = signalToken => {
    this.setState({formInfo: {...this.state.formInfo, signalToken: signalToken}});
  };

  handleRegisterSubmit = event => {
    event.preventDefault();
    logSubmit(this.state);
    axios.post(`${WEBAPP_URL}/register`, this.state.formInfo)
      .then(response => {
        if (response.status === 201) {
          this.setState({logged: true, token: response.data.token});
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      })
      .catch(error => {
        if (error.response.status === 400) {
          this.setState({error: 'There was an error in the parameters'});
        } else {
          console.log(error);
        }
      });
  }

  handleLoginSubmit = event => {
    event.preventDefault();
    logSubmit(this.state);
    axios.post(`${WEBAPP_URL}/login`, this.state.formInfo)
      .then(response => {
        if (response.status === 200) {
          this.setState({logged: true, token: response.data.token});
        } else {
          this.setState({error: `Unexpected response code ${response.status}`});
        }
      })
      .catch(error => {
        if (error.response.status === 401) {
          this.setState({error: 'Incorrect email or password'})
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
        <div class="row">
          <div class="col-sm-6 offset-md-3">
            <h1>BioSignal auth demo</h1>
          </div>
        </div>
        <div class="row">
          {this.state.logged
            ? (
              <p>{JSON.stringify(jwt_decode(this.state.token), null, 2)}</p>
            )
            : (
              <div class="col-sm-6 offset-md-3">
                {
                  this.state.error
                    ? <div class="alert alert-warning" role="alert">{this.state.error}</div>
                    : null
                }
                <Form
                  email={this.state.formInfo.email}
                  password={this.state.formInfo.password}
                  onPasswordChange={this.handlePasswordChange}
                  onEmailChange={this.handleEmailChange}
                  onSubmit={this.state.registerMenu ? this.handleRegisterSubmit : this.handleLoginSubmit}
                  submitText={this.state.registerMenu ? 'Sign up' : 'Log in'}
                />
                {
                  this.state.registerMenu
                  ? <small class="form-text text-muted">Already have an account? <a href="#" onClick={this.switchRegisterMenu}>Log in</a></small>
                  : <small class="form-text text-muted">Don't have an account? <a href="#" onClick={this.switchRegisterMenu}>Sign up</a></small>
                }
              </div>
              )
           }
        </div>
      </div>
    );
  }
}

export default App;
