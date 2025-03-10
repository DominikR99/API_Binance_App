import React, { useState } from 'react';
import axios from 'axios';
import './styles/LoginForm.css';

const LoginForm = ({ onLogin }) => {
  const [apiKey, setApiKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [testnet, setTestnet] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();

    axios.post('http://127.0.0.1:8000/api/login/', { 
        api_key: apiKey, 
        secret_key: secretKey, 
        testnet 
      })
      .then(response => {
        if (response.data.message === "Logged in successfully") {
          // Zapisz API i Secret Key oraz token w stanie lub w localStorage
          onLogin(apiKey, secretKey, response.data.username);
        } else {
          setError("Invalid API Key or Secret Key. Please try again.");
        }
      })
      .catch(() => {
        setError("Failed to login. Please check your credentials.");
      });
  };

  return (
    <div className="login-form">
      <h2>Login to Binance</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Enter your API Key" 
          value={apiKey} 
          onChange={(e) => setApiKey(e.target.value)} 
        />
        <input 
          type="text" 
          placeholder="Enter your Secret Key" 
          value={secretKey} 
          onChange={(e) => setSecretKey(e.target.value)} 
        />
        <div className="testnet-checkbox">
          <input 
            type="checkbox" 
            id="testnet" 
            checked={testnet} 
            onChange={(e) => setTestnet(e.target.checked)} 
          />
          <label htmlFor="testnet">TESTNET</label>
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginForm;
