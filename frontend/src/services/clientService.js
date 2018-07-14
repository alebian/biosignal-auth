import axios from 'axios';

const service = (() => {
  const HTTPService = axios.create({
    baseURL: 'http://localhost:8000/api/v1/',
    timeout: 30000,
    headers: { Accept: 'application/json' },
  });

  return {
    devices: () => HTTPService
      .get('/devices')
      .catch(error => console.log(`Error fetching devices: ${error}`)),

    signalExist: token => HTTPService
      .get(`/signal/${token}`)
      .catch(error => console.log(error)),

    register: (email, password, signalToken) => HTTPService
      .post('/register', {
        email, password, signalToken,
      }),

    login: (email, password, signalToken) => HTTPService
      .post('/login', {
        email, password, signalToken,
      }),
  };
})();

export default service;
