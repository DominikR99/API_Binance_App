import React, { useState } from 'react';
import axios from 'axios';
import './styles/TestStrategy.css';

const TestStrategy = ({ formData, onCancel, username }) => {
  const [testDates, setTestDates] = useState({ startDate: '', endDate: '' });
  const [testResults, setTestResults] = useState([]); // Wyniki testu
  const [loading, setLoading] = useState(false);
  const [totalResult, setTotalResult] = useState(0);

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setTestDates((prev) => ({ ...prev, [name]: value }));
  };

  const calculateTotalResult = (transactions) => {
    let total = 0;
    transactions.forEach((transaction) => {
      const tradeValue = transaction.action === 'BUY'
        ? -transaction.price * transaction.amount // Kupno zmniejsza saldo
        : transaction.price * transaction.amount; // Sprzedaż zwiększa saldo
      total += tradeValue;
    });
    setTotalResult(total.toFixed(2));
  };

  const handleTestStrategy = async () => {

    try {
      setLoading(true);
      const response = await axios.post('http://127.0.0.1:8000/api/test-strategy/', {
        username: username,
        formData,
        startDate: testDates.startDate,
        endDate: testDates.endDate,
      });
      const transactions = response.data.transactions || [];
      setTestResults(transactions);
      calculateTotalResult(transactions);
    } catch (error) {
      console.error('Błąd podczas testowania strategii:', error);
      alert('Nie udało się przetestować strategii. Spróbuj ponownie.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="test-strategy-modal">
      {  (
        <>
          <h4>Testuj Strategię</h4>
          <div className="test-dates">
            <label>
              Data od:
              <input
                type="date"
                name="startDate"
                value={testDates.startDate}
                onChange={handleDateChange}
              />
            </label>
            <label>
              Data do:
              <input
                type="date"
                name="endDate"
                value={testDates.endDate}
                onChange={handleDateChange}
              />
            </label>
          </div>
          <div className="strategy-params">
            <h5>Parametry Strategii:</h5>
            <p>Para: {formData.symbol}</p>
            <p>Interval: {formData.timeframe}</p>
            <p>SMA Short: {formData.short_window}</p>
            <p>SMA Long: {formData.long_window}</p>
            <p>Stop Loss: {formData.stop_loss_percentage}</p>
            <p>RSI Period: {formData.rsi_period}</p>
            <p>Kwota transakcji: {formData.trade_amount}</p>
          </div>
          <div className="test-strategy-buttons">
            <button onClick={handleTestStrategy} className="action-button" disabled={loading}>
              {loading ? 'Testowanie...' : 'Testuj'}
            </button>
            <button onClick={onCancel} className="cancel-button">
              Anuluj
            </button>
          </div>
          {testResults.length > 0 && (
            <div className="test-results">
              <h5>Wyniki Testu:</h5>
              <table>
                <thead>
                  <tr>
                    <th>Akcja</th>
                    <th>Cena</th>
                    <th>Ilość</th>
                    <th>Czas</th>
                  </tr>
                </thead>
                <tbody>
                  {testResults.map((result, index) => (
                    <tr key={index}>
                      <td>{result.action}</td>
                      <td>{result.price.toFixed(2)}</td>
                      <td>{result.amount}</td>
                      <td>{result.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="total-result">
                <strong>Łączny wynik testu: {totalResult} USDT</strong>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TestStrategy;
