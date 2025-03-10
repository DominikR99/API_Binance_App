import React from 'react';
import './styles/Strategy.css';

const StrategyForm = ({ formData, onInputChange, onSubmit, onTest }) => {
    return (
        <div className="strategy-form">
            <h3>Konfiguracja Strategii</h3>
            <div className="strategy-field">
                <label htmlFor="name">Nazwa strategii:</label>
                <input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={onInputChange}
                    placeholder="Wpisz nazwę strategii"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="symbol">Para kryptowalutowa:</label>
                <select
                    id="symbol"
                    name="symbol"
                    value={formData.symbol}
                    onChange={onInputChange}
                >
                    <option value="BTCUSDT">BTCUSDT</option>
                    <option value="ETHUSDT">ETHUSDT</option>
                </select>
            </div>

            <div className="strategy-field">
                <label htmlFor="strategy_duration">Czas trwania strategii (s):</label>
                <input
                    id="strategy_duration"
                    name="strategy_duration"
                    type="string"
                    value={formData.strategy_duration}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="timeframe">Interval:</label>
                <input
                    id="timeframe"
                    name="timeframe"
                    type="string"
                    value={formData.timeframe}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="short_window">SMA short:</label>
                <input
                    id="short_window"
                    name="short_window"
                    type="number"
                    value={formData.short_window}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="long_window">SMA long:</label>
                <input
                    id="long_window"
                    name="long_window"
                    type="number"
                    value={formData.long_window}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="stop_loss_percentage">Stop-loss:</label>
                <input
                    id="stop_loss_percentage"
                    name="stop_loss_percentage"
                    type="number"
                    step="0.01"
                    value={formData.stop_loss_percentage}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość w procentach"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="rsi_period">RSI Perrriod</label>
                <input
                    id="rsi_period"
                    name="rsi_period"
                    type="number"
                    value={formData.rsi_period}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość"
                />
            </div>

            <div className="strategy-field">
                <label htmlFor="trade_amount">Wartość handlowa:</label>
                <input
                    id="trade_amount"
                    name="trade_amount"
                    type="number"
                    step="0.01"
                    value={formData.trade_amount}
                    onChange={onInputChange}
                    placeholder="Wpisz wartość w USDT"
                />
            </div>

            <button onClick={onSubmit} className="start-button">
                Uruchom Strategię
            </button>
            <button onClick={onTest} className="test-button">
                Testuj Strategię
            </button>
        </div>
    );
};

export default StrategyForm;
