import React, { Component } from 'react';

import './Start.css';
import ClientService from '../../services/clientService';
import Form from '../Form/Form'
import App from '../App/App';
import Tutorial from '../Tutorial/Tutorial';

class Start extends Component {
  constructor(props) {
    super(props);
    this.state = {
      tutorial: false,
      logged: false,
      registerMenu: false,
      error: undefined,
      token: undefined,
      loginPercentage: undefined,
      loginMessage: undefined,
    };
  }

  handleTutorialSwap = () => this.setState({tutorial: !this.state.tutorial});

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
    const mainBody = this.state.tutorial
      ? <Tutorial closeTutorial={this.handleTutorialSwap} />
      : this.state.logged
        ?
          <App
            loginPercentage={this.state.loginPercentage}
            loginMessage={this.state.loginMessage}
            token={this.state.token}
          />
        : <Form
            onSubmit={this.state.registerMenu ? this.handleRegisterSubmit : this.handleLoginSubmit}
            submitText={this.state.registerMenu ? 'Registrarse' : 'Inicial sesión'}
            externalError={this.state.error}
            belowSubmitText1={this.state.registerMenu ? 'Ya tenés una cuenta?' : "No tenés una cuenta?"}
            belowSubmitText2={this.state.registerMenu ? 'Inicial sesión' : 'Registrate'}
            onBelowSubmitClick={this.switchRegisterMenu}
          />;

    const header =
      <div class="jumbotron Header">
        <h1 class="display-4">BAD Client demo</h1>
        {
          !this.state.logged &&
            <div>
              <hr class="my-4"/>
              {
                this.state.tutorial
                ? <p class="lead">Si crees que estás listo para iniciar sesión podés <a className="Link" onClick={this.handleTutorialSwap}>cerrar el tutorial</a></p>
                : <p class="lead">Si es la primera vez que entras, podés realizar el <a className="Link" onClick={this.handleTutorialSwap}>tutorial</a></p>
              }
            </div>
        }
      </div>;

    return (
      <div className="container">
        <div className="row">
          <div className="col-sm-10 offset-md-1">
            {header}
          </div>
        </div>
        <div className="row">
          {mainBody}
        </div>
      </div>
    );
  }
}

export default Start;
