import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/TransactionHistory.css';

const TransactionHistory = ({ username }) => {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [transactions, setTransactions] = useState([]);
  const [totalResult, setTotalResult] = useState(0);

  // Fetch strategies for the dropdown menu
  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/strategies/', {
          params: { username }
        });
        setStrategies(response.data);
      } catch (error) {
        console.error('Error fetching strategies:', error);
      }
    };

    fetchStrategies();
  }, [username]);

  // Fetch transaction history
  const fetchTransactions = async () => {
    try {
      const params = {
        username,
        strategy: selectedStrategy !== 'all' ? selectedStrategy : undefined,
        startTime: startDate || undefined,
        endTime: endDate || undefined,
        symbol: symbol !== 'all' ? symbol : undefined
      };

      const response = await axios.get('http://127.0.0.1:8000/api/transactions-history/', { params });
      setTransactions(response.data);
      calculateTotalResult(response.data);
      if(response.error){
        alert(response.error)
      }
    } catch (error) {
        if (error.response) {
          // Serwer odpowiedział z kodem statusu innym niż 2xx
          console.error('Błąd z odpowiedzi serwera:', error.response.data);
          alert(error.response.data.error || 'Błąd przy pobieraniu danych transakcji.');
        } else if (error.request) {
          // Brak odpowiedzi od serwera
          console.error('Brak odpowiedzi od serwera:', error.request);
          alert('Brak odpowiedzi od serwera. Sprawdź połączenie.');
        } else {
          // Inny błąd (np. problem z konfiguracją zapytania)
          console.error('Błąd podczas konfiguracji zapytania:', error.message);
          alert('Błąd podczas konfiguracji zapytania.');
        }
      }
  };

    // Calculate total result from transactions
    const calculateTotalResult = (data) => {
        const total = data.reduce((acc, transaction) => {
          const result = transaction.isBuyer
            ? -parseFloat(transaction.price) * parseFloat(transaction.qty) // Buying is a cost
            : parseFloat(transaction.price) * parseFloat(transaction.qty); // Selling is a profit
          return acc + result;
        }, 0);
    
        setTotalResult(total.toFixed(2)); // Keep two decimal places
      };

  return (
    <div className="transaction-history">
      <h2>Transaction History</h2>

      {/* Filter Controls */}
      <div className="filters">
        <div className="filter-item">
          <label htmlFor="strategy-select">Strategy:</label>
          <select
            id="strategy-select"
            value={selectedStrategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
          >
            <option value="all">All</option>
            {strategies.map((strategy) => (
              <option key={strategy.id} value={strategy.id}>
                {strategy.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-item">
          <label htmlFor="symbol-select">Symbol:</label>
          <input
            id="symbol-select"
            type="string"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
          />
        </div>

        <div className="filter-item">
          <label htmlFor="start-date">Start Date:</label>
          <input
            id="start-date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div className="filter-item">
          <label htmlFor="end-date">End Date:</label>
          <input
            id="end-date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        <button onClick={fetchTransactions}>Filter</button>
      </div>

      {/* Transactions Table */}
      <table className="transactions-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Time</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {transactions.length > 0 ? (
            transactions.map((transaction, index) => (
              <tr key={index}>
                <td>{transaction.symbol}</td>
                <td>{transaction.price}</td>
                <td>{transaction.qty}</td>
                <td>{transaction.time}</td>
                <td>{transaction.isBuyer ? 'BUY' : 'SELL'}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">No transactions found.</td>
            </tr>
          )}
        </tbody>
      </table>
      {/* Total Result */}
      <div className="transaction-total">
        <h3>Total: {totalResult} USDT</h3>
      </div>
    </div>
  );
};

export default TransactionHistory;
