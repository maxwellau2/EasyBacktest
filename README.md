# EasyBacktest Framework

## Overview

The **EasyBacktest Framework** is a Python-based library designed to help traders and developers test, evaluate, and optimize trading strategies. With its modular design, it supports the rapid development of custom strategies, grid search optimization for parameters, and detailed trade analysis. It’s built to minimize redundancy while providing flexibility and comprehensive tools for trade evaluation.

---

## Features

### Core Features

-   **Position Management**:
    -   Open and close long/short positions with optional take-profit (TP) and stop-loss (SL) levels.
    -   Calculate real-time profit and loss (PnL) for all open positions.
-   **Trade History Tracking**:
    -   Logs all trades into a history for detailed performance analysis.
    -   Outputs a trade history as a Pandas DataFrame for further insights.
-   **Parameter Optimization**:
    -   Optimizes strategy parameters using grid search and parallel processing.
    -   Supports constraints to reduce the search space and speed up optimization.
-   **Pre- and Post-Step Hooks**:
    -   Add custom logic before or after each row of data is processed.
-   **Customizable Strategies**:
    -   Define trading strategies by implementing the `strategy` method.
    -   Use the `preprocess_data` method to prepare your data for backtesting.
-   **Data Visualization**:
    -   Candlestick charting with trade annotations.
    -   Cumulative profit and loss visualization.
    -   Detailed trade statistics table.

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

To create your own strategy, subclass the `BacktestEngine` and implement the `strategy` and optional `preprocess_data` methods.

```python
from backtest_framework.backtest_engine import BacktestEngine

class MovingAverageCrossover(BacktestEngine):
    def preprocess_data(self):
        self.data_stream["short_ma"] = self.data_stream["close"].rolling(window=10).mean()
        self.data_stream["long_ma"] = self.data_stream["close"].rolling(window=30).mean()

    def strategy(self, row):
        long_position = self.position_book.get_position_by_tag("long")
        if row.short_ma > row.long_ma and not long_position:
            # Open long position
            tp = row.close * 1.02  # Take Profit at 2% increase
            sl = row.close * 0.98  # Stop Loss at 2% decrease
            self.position_book.open_long_position(quantity=1, open_price=row.close, tp=tp, sl=sl, open_time=row.Index)
        elif row.short_ma < row.long_ma and long_position:
            # Close long position
            self.position_book.close_position(tag="long", close_price=row.close, close_time=row.Index)
```

---

### 2. Fetch Market Data

Use any source that provides a Pandas DataFrame with `open`, `high`, `low`, `close`, and `volume` columns. For example:

```python
import yfinance as yf
btc_data = yf.download("BTC-USD", start="2024-01-01", interval="1h")
btc_data.columns = [col.lower() for col in btc_data.columns]  # Ensure lowercase column names
```

---

### 3. Run the Backtest

```python
# Initialize the engine and add data
engine = MovingAverageCrossover(commission=0.001)
engine.add_data_stream(btc_data)

# Execute the backtest
engine.run()

# Visualize results
engine.plot_trading_stats()

# Access trade history
results = engine.get_trade_history().to_dataframe()
print(results)
```

---

### 4. Optimize Parameters

To find the best-performing parameters, define a parameter grid and optimization constraints:

```python
param_choices = {
    "tp_pct": [0.01, 0.02, 0.03],
    "sl_pct": [0.01, 0.02, 0.03],
    "short_window": [10, 20],
    "long_window": [30, 50]
}

def constraints(params):
    return params["short_window"] < params["long_window"] and params["tp_pct"] >= params["sl_pct"] * 0.8

# Run optimization
pareto_results = engine.optimize(
    param_choices,
    optimize_metrics=["sharpe_ratio"],
    constraints=constraints
)
```

---

## Explanation of Key Functions

### `run()` Method

1. **Preprocess Data**: The `preprocess_data` method is called to prepare the data (e.g., calculate indicators).
2. **Iterate Over Data**: Each row of the dataset is processed sequentially.
3. **Before Step Hook**: Custom logic can be added before processing each row.
4. **Strategy Execution**: The `strategy` method is called to evaluate trade conditions.
5. **After Step Hook**: Post-row processing logic is executed.

### `optimize()` Method

1. **Grid Search**: Generates all possible parameter combinations from the input grid.
2. **Apply Constraints**: Filters out invalid combinations to reduce the search space.
3. **Parallel Processing**: Distributes tasks across available CPU cores (utilizing at least 80% of resources).
4. **Evaluate Performance**: Runs the backtest for each valid parameter set.
5. **Pareto Analysis**: Identifies the best-performing parameter combinations based on specified metrics.

---

## Advanced Topics

### Managing Positions

-   Open positions with optional take-profit and stop-loss levels:
    ```python
    self.position_book.open_long_position(
        quantity=1,
        open_price=row.close,
        tp=row.close * 1.02,
        sl=row.close * 0.98,
        open_time=row.Index
    )
    ```
-   Close positions:
    ```python
    self.position_book.close_position(
        tag="long",
        close_price=row.close,
        close_time=row.Index
    )
    ```

### Pre- and Post-Step Hooks

-   **Before Step**: Use `before_step` to update states or evaluate conditions.
-   **After Step**: Use `after_step` for cleanup or additional calculations.

### Visualization

Visualize trades, cumulative PnL, and trade stats:

```python
engine.plot_trading_stats()
```

---

## Benefits of Using This Framework

-   **Flexibility**: Easily adapt to new strategies and data sources.
-   **Scalability**: Optimize strategies efficiently with parallel processing.
-   **Transparency**: Detailed trade history and statistics provide insights into strategy performance.
-   **Ease of Use**: Minimal boilerplate code required for complex strategies.
-   **Customizability**: Designed to be easily extended and customized for specific trading strategies.
-   **For more examples**: Check out HOWTO.md for more detailed examples.

---

## Contributing

We welcome contributions! Fork the repository, create a feature branch, and submit a pull request.

---
