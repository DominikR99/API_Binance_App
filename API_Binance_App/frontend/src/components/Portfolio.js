import React, { useState } from 'react';
import axios from 'axios';
import './styles/Portfolio.css';

const Portfolio = ({ username }) => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPortfolioData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/api/binance/portfolio/balance/',
        { username }, // Przekazanie nazwy użytkownika
      );

      setPortfolioData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch portfolio data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="portfolio-container">
      <h2>Portfel konta Binance</h2>
      <button onClick={fetchPortfolioData} disabled={loading}>
        {loading ? 'Loading...' : 'Pokaż porfel'}
      </button>

      {error && <div className="error-message">Error: {error}</div>}

      {portfolioData && (
        <div>
          <h3>Wartość wszystkich aktywów: {portfolioData.total_balance_in_usdt.toFixed(2)} USDT</h3>
          <h3>Największe aktywa:</h3>
          <ul>
            {portfolioData.topAssets.map((asset, index) => (
              <li key={index}>
                {asset.symbol}: {asset.value_in_usdt} USDT
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Portfolio;
