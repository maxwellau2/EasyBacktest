# Easy Backtest Library

## Overview
The **Easy Backtest Library** is a Python-based framework designed for developing, running, and optimizing trading strategies. By leveraging its modular architecture, traders and developers can easily test and analyze trading ideas without reinventing the wheel. This library supports position management, trade history tracking, parameter optimization, and comprehensive data visualization.

---

## Features

### Core Features
- **Position Management**:
  - Open and close long/short positions.
  - Supports take-profit (TP) and stop-loss (SL) levels.
- **Trade History Tracking**:
  - Logs all executed trades with details.
  - Provides a complete trade history in a Pandas DataFrame.
- **Performance Metrics**:
  - Calculates statistics such as:
    - Total Profit/Loss
    - Win Rate
    - Sharpe Ratio
    - Profit Factor
    - Maximum Drawdown
    - Expectancy
  - Supports custom annualization factors for metrics.
- **Customizable Strategies**:
  - Create strategies by implementing custom logic in the `strategy` method.
  - Flexible hooks for preprocessing data and defining logic before and after each step.
- **Data Visualization**:
  - OHLC candlestick chart with trade markers.
  - Cumulative PnL visualization.
  - Trade statistics table.
- **Parameter Optimization**:
  - Perform grid search optimization on strategy parameters.
  - Supports constraints for parameter combinations.

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/maxwellau2/EasyBacktest.git
```
2. Navigate to the project directory:
```bash
cd EasyBacktest
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Getting Started

### 1. Define a Custom Backtest
Start by inheriting from the `BacktestEngine` class and implementing your own methods. The two most critical methods are:
- `preprocess_data`: For data preprocessing.
- `strategy`: Defines the core trading logic.

```python
from easy_backtest.backtest_engine import BacktestEngine

class MyBacktest(BacktestEngine):
    def preprocess_data(self):
        # Add a 100-period moving average to the data stream
        self.data_stream['moving_avg'] = self.data_stream['close'].rolling(window=100).mean()

    def strategy(self, row):
        position_size = 100
        qty = position_size / row.close
        long_tp = row.close * 1.1
        long_sl = row.close * 0.95

        # Open a long position if the close price is above the moving average
        if row.close > row.moving_avg:
            self.position_book.open_long_position(quantity=qty, open_price=row.close, tp=long_tp, sl=long_sl, open_time=row.Index)
```

### 2. Fetch Market Data
You can use any data source that outputs a Pandas DataFrame with the required columns: `open`, `high`, `low`, `close`, and `volume`. The example below uses Yahoo Finance.

```python
import yfinance as yf
btc_data = yf.download('BTC-USD', start='2024-01-01', interval='1h')
btc_data.columns = [col.lower() for col in btc_data.columns]  # Ensure lowercase column names
```

### 3. Run the Backtest

```python
backtest = MyBacktest(commission=0.01)
backtest.add_data_stream(data_stream=btc_data)
backtest.run()
backtest.plot_trading_stats()
results = backtest.get_trade_history().to_dataframe()
print(results)
```

### 4. Optimize Parameters
Perform parameter optimization to fine-tune your strategy. Define the parameter grid and target metric.

```python
param_choices = {
    "tp_pct": [0.05, 0.1, 0.2],
    "sl_pct": [0.03, 0.05, 0.1]
}
result = backtest.optimize(param_choices, optimize_target="sharpe_ratio")
print("Best Parameters:", result["best_params"])
```

---

## Detailed Usage

### Backtest Workflow
1. **Initialize the Engine**:
   Create an instance of a class inheriting from `BacktestEngine`.
2. **Add Data Stream**:
   Add a Pandas DataFrame containing historical market data.
3. **Define Strategy**:
   Implement trading logic in the `strategy` method.
4. **Run Backtest**:
   Execute the backtest and visualize the results.
5. **Optimize Parameters**:
   Perform grid search on defined parameters.

### Key Classes
- **`BacktestEngine`**:
  The base class for running backtests. Extend this class to define your own strategies.
- **`PositionBook`**:
  Manages open positions and tracks executed trades.
- **`TradeHistory`**:
  Records trade details and computes performance metrics.
- **`Position`**:
  Represents an individual trade position.
- **`PositionCollection`**:
  Maintains a collection of all open positions.

### Key Methods
- `add_data_stream(data_stream)`: Adds a Pandas DataFrame containing market data.
- `run()`: Executes the backtest.
- `plot_trading_stats()`: Visualizes the backtest results.
- `optimize(param_choices, optimize_target)`: Optimizes parameters using grid search.

---

## Examples

### Basic Backtest
Refer to `samplebacktest.py` for a moving average crossover strategy implementation.

### Parameter Optimization
See `sampleoptimize.py` for a detailed example of optimizing take-profit and stop-loss percentages.

---

## Advanced Topics

### Custom Hooks
The `BacktestEngine` supports hooks for additional logic:
- `before_step(index, row)`: Execute custom logic before processing each data point.
- `after_step(index, row)`: Execute custom logic after processing each data point.

### Visualizing Trades
The `plot_trading_stats` method generates:
1. OHLC candlestick chart with trade markers.
2. Cumulative PnL over time.
3. Tabular summary of trade statistics.

---

## Contributing
We welcome contributions! Please fork the repository, create a feature branch, and submit a pull request.

---

