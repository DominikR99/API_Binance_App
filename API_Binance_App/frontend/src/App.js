import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import './App.css';

const App = () => {
  const [username, setUserName] = useState(null);

  const handleLogin = ( username) => {
    setUserName(username);
  };

  const handleLogout = () => {
    setUserName(null);
  };

  return (
    <div className="app">
      {!username ? (
        <LoginForm onLogin={handleLogin} />
      ) : (
        <Dashboard username={username} onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;
