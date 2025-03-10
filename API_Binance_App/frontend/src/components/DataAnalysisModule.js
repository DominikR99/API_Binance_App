import React, { useState, useEffect } from 'react';
import Chart from 'react-apexcharts';
import axios from 'axios';
import './styles/DataAnalysisModule.css';

const DataAnalysisModule = () => {
  
  const getCurrentDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const [pair, setPair] = useState('BTCUSDT'); // Domyślna para kryptowalutowa
  const [interval, setInterval] = useState('15m'); // Domyślny interwał
  const [startTime, setStartTime] = useState(getCurrentDate()); // Data początkowa
  const [endTime, setEndTime] = useState(''); // Data końcowa
  const [smaShort, setSmaShort] = useState(10); // Domyślny okres dla SMA Short
  const [smaLong, setSmaLong] = useState(30); // Domyślny okres dla SMA Long
  const [rsiPeriod, setRsiPeriod] = useState(7); // Domyślny okres dla RSI
  const [chartData, setChartData] = useState(null);
  const [rsiData, setRsiData] = useState(null); // Dane RSI
  const [testnet, setTestnet] = useState(false);

  const intervals = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']; // Dostępne interwały

  const baseUrl = testnet
    ? 'https://testnet.binance.vision/api/v3/klines' // Endpoint testnetu
    : 'https://api.binance.com/api/v3/klines'; // Endpoint produkcji

  const calculateSMA = (data, period) => {
    return data.map((_, index, arr) => {
      if (index < period - 1) return null; // Brak danych na początku
      const slice = arr.slice(index - period + 1, index + 1);
      const sum = slice.reduce((acc, val) => acc + parseFloat(val), 0);
      return sum / period;
    });
  };

  const calculateRSI = (data, period) => {
    let gains = [];
    let losses = [];
    let rsi = [];

    data.forEach((value, index) => {
      if (index === 0) return;

      const change = parseFloat(value) - parseFloat(data[index - 1]);
      if (change > 0) {
        gains.push(change);
        losses.push(0);
      } else {
        gains.push(0);
        losses.push(Math.abs(change));
      }

      if (index >= period) {
        const avgGain = gains.slice(-period).reduce((acc, val) => acc + val, 0) / period;
        const avgLoss = losses.slice(-period).reduce((acc, val) => acc + val, 0) / period;
        const rs = avgGain / (avgLoss || 1); // Zapobiega dzieleniu przez 0
        rsi.push(100 - 100 / (1 + rs));
      } else {
        rsi.push(null);
      }
    });

    return rsi;
  };

  const fetchChartData = async () => {
    try {
      const params = {
        symbol: pair,
        interval: interval,
      };
  
      if (startTime) params.startTime = new Date(startTime).getTime();
      if (endTime) params.endTime = new Date(endTime).getTime();
  
      const response = await axios.get(baseUrl, { params });
      const formattedData = response.data.map(([time, open, high, low, close]) => ({
        x: new Date(time),
        y: [parseFloat(open), parseFloat(high), parseFloat(low), parseFloat(close)],
        open: parseFloat(open),
        high: parseFloat(high),
        low: parseFloat(low),
        close: parseFloat(close),
      }));
  
      const closePrices = formattedData.map((d) => d.close);
      const smaShortData = calculateSMA(closePrices, smaShort);
      const smaLongData = calculateSMA(closePrices, smaLong);
      const rsiValues = calculateRSI(closePrices, rsiPeriod);
  
setChartData({
  options: {
    chart: {
      type: 'candlestick',
    },
    title: {
      text: `Historical Data for ${pair}`,
      align: 'center',
    },
    xaxis: {
      type: 'datetime',
    },
    tooltip: {
      shared: true,
      x: {
        format: 'yyyy-MM-dd HH:mm:ss', // Format daty i godziny
      },
      custom: ({ series, seriesIndex, dataPointIndex, w }) => {
        // Bierzemy dane tylko ze świec
        if (seriesIndex === 0) {
          const candleData = formattedData[dataPointIndex]; // Dane świecy z formattedData
          if (!candleData) return 'No data';

          const { y: [open, high, low, close] } = candleData;
          const smaShortValue = smaShortData[dataPointIndex]?.toFixed(2) || 'N/A';
          const smaLongValue = smaLongData[dataPointIndex]?.toFixed(2) || 'N/A';

          const dateUTC = new Date(candleData.x).toISOString().slice(0, 19).replace('T', ' ');

          return `
            <div>
              <strong>Date:</strong> ${dateUTC}<br/>
              <strong>Price:</strong><br/>
              Open: ${open.toFixed(2)}<br/>
              High: ${high.toFixed(2)}<br/>
              Low: ${low.toFixed(2)}<br/>
              Close: ${close.toFixed(2)}<br/>
              <strong>SMA ${smaShort}:</strong> ${smaShortValue}<br/>
              <strong>SMA ${smaLong}:</strong> ${smaLongValue}
            </div>
          `;
        }
        return null; // Dla innych serii tooltip jest pusty
      },
    },
  },
  series: [
    {
      name: 'Price',
      type: 'candlestick',
      data: formattedData,
    },
    {
      name: `SMA ${smaShort}`,
      type: 'line',
      data: smaShortData.map((val, index) => ({ x: formattedData[index]?.x, y: val })).filter((d) => d.y),
      enable: false,
      tooltip: { enabled: false }, // Wyłącz tooltip dla SMA
    },
    {
      name: `SMA ${smaLong}`,
      type: 'line',
      data: smaLongData.map((val, index) => ({ x: formattedData[index]?.x, y: val })).filter((d) => d.y),
      enable: false,
      tooltip: { enabled: false }, // Wyłącz tooltip dla SMA
    },
  ],
});
  
      setRsiData({
        options: {
          chart: {
            type: 'line',
          },
          title: {
            text: `RSI for ${pair}`,
            align: 'center',
          },
          xaxis: {
            type: 'datetime',
          },
          yaxis: {
            min: 0,
            max: 100,
          },
          tooltip: {
            shared: true,
          
            x: {
              format: 'yyyy-MM-dd HH:mm:ss', // Format daty i godziny
            },
          },
        },
        series: [
          {
            name: 'RSI',
            data: rsiValues.map((val, index) => ({ x: formattedData[index]?.x, y: val })).filter((d) => d.y),
          },
        ],
      });
    } catch (error) {
      console.error('Error fetching data from Binance:', error);
    }
  };

  useEffect(() => {
    fetchChartData();
  }, [pair, interval, startTime, endTime, smaShort, smaLong, rsiPeriod]);

  return (
    <div className="data-analysis-module">
      <h2>Historical Data Analysis</h2>
      <div className="controls">
        <label>
          Pair:
          <select value={pair} onChange={(e) => setPair(e.target.value)}>
            <option value="BTCUSDT">BTC/USDT</option>
            <option value="ETHUSDT">ETH/USDT</option>
            <option value="BNBUSDT">BNB/USDT</option>
          </select>
        </label>
        <label>
          Interval:
          <select value={interval} onChange={(e) => setInterval(e.target.value)}>
            {intervals.map((int) => (
              <option key={int} value={int}>
                {int}
              </option>
            ))}
          </select>
        </label>
        <label>
          Start Time:
          <input type="date" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
        </label>
        <label>
          End Time:
          <input type="date" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
        </label>
        <label>
          SMA Short:
          <input type="number" value={smaShort} onChange={(e) => setSmaShort(e.target.value)} />
        </label>
        <label>
          SMA Long:
          <input type="number" value={smaLong} onChange={(e) => setSmaLong(e.target.value)} />
        </label>
        <label>
          RSI Period:
          <input type="number" value={rsiPeriod} onChange={(e) => setRsiPeriod(e.target.value)} />
        </label>
        <button onClick={fetchChartData}>Fetch Data</button>
      </div>
      {chartData ? (
        <Chart options={chartData.options} series={chartData.series} height={500} />
      ) : (
        <p>Loading chart...</p>
      )}
      {rsiData ? (
        <Chart options={rsiData.options} series={rsiData.series} height={200} />
      ) : (
        <p>Loading RSI chart...</p>
      )}
    </div>
  );
};

export default DataAnalysisModule;

