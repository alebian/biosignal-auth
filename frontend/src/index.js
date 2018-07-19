import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap';
import 'react-rangeslider/lib/index.css';

import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Start from './components/Start/Start';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(<Start />, document.getElementById('root')); // eslint-disable-line no-undef
registerServiceWorker();
