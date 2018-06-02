import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import './Form.css';

class Form extends PureComponent {
  render() {
    return (
      <form onSubmit={this.props.onSubmit}>
        <div className="form-group">
          <label htmlFor="emailInput">Email</label>
          <input
            type="email"
            className="form-control"
            id="emailInput"
            aria-describedby="emailHelp"
            placeholder="johndoe@gmail.com"
            value={this.props.email}
            onChange={this.props.onEmailChange}
          />
        </div>
        <div className="form-group">
          <label htmlFor="passwordInput">Password</label>
          <input
            type="password"
            className="form-control"
            id="passwordInput"
            placeholder="Password"
            value={this.props.password}
            onChange={this.props.onPasswordChange}
          />
        </div>
        <button type="submit" className="btn btn-primary">{this.props.submitText}</button>
      </form>
    );
  }
}

Form.defaultProps = {
  submitText: 'Submit',
};

Form.propTypes = {
  email: PropTypes.string.isRequired,
  password: PropTypes.string.isRequired,
  submitText: PropTypes.string.isRequired,
  onPasswordChange: PropTypes.func.isRequired,
  onEmailChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

export default Form;
