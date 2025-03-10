import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StrategyTable from './StrategyTable';
import StrategyForm from './StrategyForm';
import TestStrategyWithFormData from './TestStrategyWithFormData'; // Importujemy komponent TestStrategy
import './styles/Strategy.css';

const Strategy = ({ username }) => {
    const [formData, setFormData] = useState({
        username: username,
        name: '',
        symbol: 'BTCUSDT',
        strategy_duration: '3600',
        timeframe: '1h',
        short_window: 10,
        long_window: 30,
        stop_loss_percentage: 0.02,
        rsi_period: 7,
        trade_amount: 0.0001
    });
    const [activeStrategies, setActiveStrategies] = useState([]);
    const [viewedStrategy, setViewedStrategy] = useState(null);
    const [testModalVisible, setTestModalVisible] = useState(false);

    useEffect(() => {
        const fetchActiveStrategies = async () => {
            if (!username) {
                console.error('Brak username do pobrania strategii');
                return;
            }
    
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/strategies/', {
                    params: { username: username }
                });
                setActiveStrategies(response.data);
            } catch (error) {
                console.error('Błąd przy pobieraniu aktywnych strategii:', error);
            }
        };
    
        fetchActiveStrategies();
    }, [username]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleStartStrategy = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/start-strategy/', formData);
            setActiveStrategies((prev) => [...prev, response.data]);
            alert('Strategia została uruchomiona!');
        } catch (error) {
            console.error('Błąd przy uruchamianiu strategii:', error);
            alert('Nie udało się uruchomić strategii. Spróbuj ponownie.');
        }
    };

    const handleViewParams = (strategy) => {
        setViewedStrategy(strategy);
    };

    const handleTestStrategy = () => {
        setTestModalVisible(true); // Otwieramy modal dla testowania strategii
    };

    const closeTestModal = () => {
        setTestModalVisible(false); // Zamykamy modal
    };

    return (
        <div className="strategy-container">
            <div className="strategy-config">
                <StrategyForm
                    formData={formData}
                    onInputChange={handleInputChange}
                    onSubmit={handleStartStrategy}
                    onTest={handleTestStrategy}
                />
            </div>
            <StrategyTable
                strategies={activeStrategies}
                onViewParams={handleViewParams}
                username={username}
            />
            {viewedStrategy && (
                <div className="view-params-modal">
                    <h4>Parametry Strategii: {viewedStrategy.name}</h4>
                    <p>Pair: {viewedStrategy.pair}</p>
                    <p>Interval: {viewedStrategy.time_frame}</p>
                    <p>SMA Short: {viewedStrategy.short_window}</p>
                    <p>SMA Long: {viewedStrategy.long_window}</p>
                    <p>Stop Loss: {viewedStrategy.stop_loss_percentage}</p>
                    <p>RSI Period: {viewedStrategy.rsi_period}</p>
                    <p>Trade Amount: {viewedStrategy.trade_amount}</p>
                    <button onClick={() => setViewedStrategy(null)} className="close-button">
                        Zamknij
                    </button>
                </div>
            )}
            {testModalVisible && (
                <div className="test-strategy-modal-container">
                    <TestStrategyWithFormData
                        formData={formData}
                        username={username}
                        onCancel={closeTestModal}
                    />
                </div>
            )}
        </div>
    );
};

export default Strategy;
