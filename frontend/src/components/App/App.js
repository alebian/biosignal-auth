import React, { Component } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

import './App.css';
import Form from '../Form/Form'

const WEBAPP_URL = 'http://localhost:5000/api/v1';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      logged: false,
      registerMenu: false,
      error: undefined,
      token: undefined
    };
  }

  handleRegisterSubmit = formInfo => {
    axios.post(`${WEBAPP_URL}/register`, formInfo)
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

  handleLoginSubmit = formInfo => {
    axios.post(`${WEBAPP_URL}/login`, formInfo)
      .then(response => {
        if (response.status === 200) {
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

  switchRegisterMenu = () => {
    this.setState(prevState => ({registerMenu: !prevState.registerMenu, error: undefined}));
  }

  render() {
    return (
      <div className="App container">
        <div className="row">
          <div className="col-sm-6 offset-md-3">
            <h1>BioSignal auth demo</h1>
          </div>
        </div>
        <div className="row">
          {this.state.logged
            ? (
              <p>{JSON.stringify(jwt_decode(this.state.token), null, 2)}</p>
            )
            : (
              <div className="col-sm-8 offset-md-1">
                <Form
                  onSubmit={this.state.registerMenu ? this.handleRegisterSubmit : this.handleLoginSubmit}
                  submitText={this.state.registerMenu ? 'Sign up' : 'Log in'}
                  externalError={this.state.error}
                />
                {
                  this.state.registerMenu
                  ? <small className="form-text text-muted">Already have an account? <a href="#" onClick={this.switchRegisterMenu}>Log in</a></small>
                  : <small className="form-text text-muted">Don't have an account? <a href="#" onClick={this.switchRegisterMenu}>Sign up</a></small>
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
