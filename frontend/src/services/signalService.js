import axios from 'axios';

const service = (() => {
  const HTTPService = axios.create({
    timeout: 30000,
    headers: { Accept: 'application/json' },
  });

  const buildUrl = host => `http://${host}:5001/api/v1`;

  return {
    start: readerHost => HTTPService
      .post(`${buildUrl(readerHost)}/start`)
      .catch(error => console.log(error)),

    stop: (readerHost, token) => HTTPService
      .post(`${buildUrl(readerHost)}/stop`, {
        signalUUID: token,
      })
      .catch(error => console.log(error)),

    cancel: (readerHost, token) => HTTPService
      .post(`${buildUrl(readerHost)}/cancel`, {
        signalUUID: token,
      })
      .then(() => console.log('Successfully canceled reading'))
      .catch(error => console.log(error)),

    read: (readerHost, token) => HTTPService
      .get(`${buildUrl(readerHost)}/read?signalUUID=${token}`)
      .catch(error => console.log(error)),

    updateSettings: (
      readerHost,
      windowSize,
      spikeThreshold,
      zeroThreshold,
      zeroLength,
    ) => HTTPService
      .put(`${buildUrl(readerHost)}/settings`, {
        window_size: windowSize,
        spike_threshold: spikeThreshold,
        zero_threshold: zeroThreshold,
        zero_length: zeroLength,
      }).catch(error => console.log(error)),

    getSettings: readerHost => HTTPService
      .get(`${buildUrl(readerHost)}/settings`)
      .catch(error => console.log(error)),
  };
})();

export default service;
