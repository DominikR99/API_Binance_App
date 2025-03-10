import React, { useState } from 'react';
import './styles/StrategyTable.css';
import TestStrategy from './TestStrategy';

const StrategyTable = ({ strategies, onTest, onViewParams, username }) => {
    const [selectedStrategy, setSelectedStrategy] = useState(null);
    const [testDates, setTestDates] = useState({ startDate: '', endDate: '' });

    const handleDateChange = (e) => {
        const { name, value } = e.target;
        setTestDates((prev) => ({ ...prev, [name]: value }));
    };

    const handleCancelTest = () => {
        setSelectedStrategy(null);
        setTestDates({ startDate: '', endDate: '' }); // Resetujemy daty
    };

    return (
        <div className="strategy-table-container">
            <h3>Lista Strategii</h3>
            <table className="strategy-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nazwa Strategii</th>
                        <th>Data Rozpoczęcia</th>
                        <th>Data Zakończenia</th>
                        <th>Status</th>
                        <th>Akcje</th>
                    </tr>
                </thead>
                <tbody>
                    {strategies.map((strategy) => (
                        <tr key={strategy.id}>
                            <td>{strategy.id}</td>
                            <td>{strategy.name}</td>
                            <td>{strategy.start_time}</td>
                            <td>{strategy.end_time}</td>
                            <td>{strategy.status}</td>
                            <td>
                                <button
                                    onClick={() => onViewParams(strategy)}
                                    className="action-button"
                                >
                                    Podgląd
                                </button>
                                <button
                                    onClick={() => setSelectedStrategy(strategy)}
                                    className="action-button"
                                >
                                    Testuj
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {selectedStrategy && (
            <TestStrategy
                selectedStrategy={selectedStrategy}
                onCancel={() => setSelectedStrategy(null)}
                username={username}
            />
            )}
            
        </div>
    );
};

export default StrategyTable;
