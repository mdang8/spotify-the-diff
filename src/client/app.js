import React from 'react';
import { render } from 'react-dom';
import App from './components/App';

if (document.getElementById('root')) {
  render(<App />, document.getElementById('root'));
}
