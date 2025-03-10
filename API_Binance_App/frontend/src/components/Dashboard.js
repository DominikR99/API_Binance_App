import React, { useState } from 'react';
import DataAnalysisModule from './DataAnalysisModule';
import Strategy from './Strategy';
import Portfolio from './Portfolio';
import TransactionHistory from './TransactionHistory';
import './styles/Dashboard.css';


const Dashboard = ({ username, onLogout }) => {
  //const { total_balance_in_usdt, topAssets } = userData;

  const [activeTab, setActiveTab] = useState('portfolio'); // Zmienna dla aktywnej zakładki

  return (
    <div className="dashboard">
      <nav className="dashboard-menu">
        <button onClick={() => setActiveTab('portfolio')} className={activeTab === 'portfolio' ? 'active' : ''}>
          Portfel
        </button>
        <button onClick={() => setActiveTab('history')} className={activeTab === 'history' ? 'active' : ''}>
          Historia Transakcji
        </button>
        <button onClick={() => setActiveTab('analysis')} className={activeTab === 'analysis' ? 'active' : ''}>
          Dane Historyczne
        </button>
        <button onClick={() => setActiveTab('strategy')} className={activeTab === 'strategy' ? 'active' : ''}>
          Strategia handlowa
        </button>
        <button onClick={onLogout}>Wyloguj</button>
      </nav>

      {activeTab === 'portfolio' && <Portfolio username={username} />}

      {activeTab === 'history' && <TransactionHistory username={username} />}

      {activeTab === 'analysis' && <DataAnalysisModule />}

      {activeTab === 'strategy' && <Strategy username={username} />}
    </div>
  );
};

export default Dashboard;
