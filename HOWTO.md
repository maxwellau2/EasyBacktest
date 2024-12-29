**Step-by-Step Guide to Using the Backtest Framework with a Moving Average Crossover Strategy**

### **Introduction to the Framework**

The backtest framework is designed for flexibility and extensibility, allowing you to implement and evaluate trading strategies. This guide will use a Moving Average Crossover strategy as an example to illustrate the key components and best practices.

At a high level, the framework consists of:

-   **Data Stream**: The input market data processed row by row.
-   **Position Book**: Manages open and closed positions, calculates profits/losses, and tracks trades.
-   **Hooks**: Pre- and post-row processing for custom logic.
-   **Optimization Engine**: Evaluates parameter combinations to identify the best-performing strategy configurations.

---

### **1. Best Practices for Running Backtests**

-   **Start Small**: Use a subset of your data for initial testing to ensure the strategy logic is correct.
-   **Incremental Development**: Develop and test in small steps, starting with basic logic and adding complexity over time.
-   **Log Key Events**: Use logging to track actions taken during the backtest, such as trade entries and exits.
-   **Validate Data**: Ensure your data stream has no missing or corrupted values.
-   **Save Results**: Save trade history and statistics after each run for later analysis.
-   **Use Meaningful Variables**: Assign meaningful names to variables when managing positions, such as `long_position` or `short_position`, for better readability.
-   **Add Comments**: Include comments to explain the purpose of each step, especially for complex logic.
-   **Set Take Profit and Stop Loss Levels**: Use meaningful percentage values for TP/SL based on strategy needs.

#### **Setting TP and SL Levels**

```python
# Example within the strategy method
tp_long = row.close * (1 + self.states['params']['tp_pct'])
sl_long = row.close * (1 - self.states['params']['sl_pct'])

self.position_book.open_long_position(
    quantity=1,
    open_price=row.close,
    tag="long",
    tp=tp_long,
    sl=sl_long,
    open_time=row.Index
)
```

---

### **2. Proposed Flow of Events When Backtesting**

#### **High-Level Steps Done in `run()` Method**

1. **Preprocess Data**: The framework first preprocesses the data using the `preprocess_data` method.
2. **Iterate Over Data**: Each row of data is processed in sequence.
3. **Call Before Step Hook**: The `before_step` hook is executed to update states or check preconditions.
4. **Execute Strategy**: The `strategy` method is invoked to evaluate and apply the trading logic.
5. **Call After Step Hook**: The `after_step` hook is called for any post-processing actions.

```python
# Example high-level steps in the `run()` method
engine.run()
```

---

### **3. Steps to Do Parameter Optimizations**

#### **High-Level Steps done by the `optimize()` Method**

1. **Generate Parameter Combinations**: Create all possible combinations of parameters using grid search.
2. **Apply Constraints**: Filter out invalid combinations using user-defined constraints to reduce search space.
3. **Distribute Tasks**: Utilize `ProcessPoolExecutor` to parallelize the evaluation of combinations, using at least 80% of available CPU resources.
4. **Evaluate Performance**: Run the backtest for each combination and collect results.
5. **Save Results**: Save all results to a JSON file for further analysis.
6. **Find Pareto-Optimal Set**: Identify parameter combinations that achieve the best trade-offs between optimization metrics.

```python
# Example optimization process
pareto_results = engine.optimize(
    param_choices={
        "tp_pct": [0.01, 0.02, 0.03],
        "sl_pct": [0.01, 0.02, 0.03]
    },
    optimize_metrics=["sharpe_ratio", "win_rate"],
    constraints=lambda params: params['tp_pct'] >= params['sl_pct'] * 0.8
)
```

---

### **4. Introduction to States**

-   **What Are States?**: States are variables stored in the framework to track conditions or parameters across the backtest.
-   **Examples**:
    -   Track the number of bars since a specific condition was met.
    -   Store indicator values or thresholds.
    -   Maintain flags for valid entry/exit points.
-   **How to Use**: Initialize states in the `preprocess_data` method and update them in `before_step` and `strategy` methods.

---

### **5. Pre-event and Post-event Hooks**

-   **Before Step (`before_step`)**:
    -   Triggered before processing each row of data.
    -   Use this to update states or perform checks based on the current market conditions.
-   **After Step (`after_step`)**:
    -   Triggered after processing each row of data.
    -   Ideal for cleanup actions or additional calculations.

---

### **6. Backend Logic Overview**

-   **Position Book**:
    -   Handles all position-related operations, including opening, closing, and calculating profit/loss.
    -   Manages stop loss (SL) and take profit (TP) triggers via the `incur_tp_sl` method.
-   **Trade History**:
    -   Tracks all closed trades with relevant statistics like profit percentage and timestamps.
-   **Optimization Engine**:
    -   Uses grid search with parallel processing to evaluate combinations of parameters.
    -   Supports multi-objective optimization by calculating Pareto-optimal sets.
-   **Hooks**:
    -   Allow customization of logic before or after processing each row of data, enhancing flexibility.

---

### **7. Implementation Examples**

#### **7.1 Simple Backtest**

```python
class SimpleMACross(BacktestEngine):
    def strategy(self, row):
        # Assign meaningful variables for clarity
        short_ma = row.short_ma
        long_ma = row.long_ma

        # Check for existing positions
        long_position = self.position_book.get_position_by_tag("long")

        # Entry and exit logic with meaningful comments
        if short_ma > long_ma and not long_position:
            # Open a long position if the short MA crosses above the long MA
            tp_long = row.close * 1.02
            sl_long = row.close * 0.98
            self.position_book.open_long_position(quantity=1, open_price=row.close, tag="long", tp=tp_long, sl=sl_long, open_time=row.Index)
        elif short_ma < long_ma and long_position:
            # Close the long position if the short MA crosses below the long MA
            self.position_book.close_position(tag="long", close_price=row.close, close_time=row.Index)

# Usage
engine = SimpleMACross(commission=0.001)
data = pd.read_csv("data.csv")
data["short_ma"] = data["close"].rolling(window=10).mean()
data["long_ma"] = data["close"].rolling(window=30).mean()
engine.add_data_stream(data)
engine.run()
```

#### **7.2 Backtest with Input Parameters**

```python
class ParametrizedMACross(BacktestEngine):
    def preprocess_data(self):
        # Extract parameter values from states
        df = self.data_stream
        short_window = self.states["params"]["short_window"]
        long_window = self.states["params"]["long_window"]

        # Calculate moving averages
        df["short_ma"] = df["close"].rolling(window=short_window).mean()
        df["long_ma"] = df["close"].rolling(window=long_window).mean()
        return df

    def strategy(self, row):
        # Assign variables for positions
        long_position = self.position_book.get_position_by_tag("long")

        # Entry and exit logic
        if row.short_ma > row.long_ma and not long_position:
            tp_long = row.close * (1 + self.states['params']['tp_pct'])
            sl_long = row.close * (1 - self.states['params']['sl_pct'])
            self.position_book.open_long_position(quantity=1, open_price=row.close, tag="long", tp=tp_long, sl=sl_long, open_time=row.Index)
        elif row.short_ma < row.long_ma and long_position:
            self.position_book.close_position(tag="long", close_price=row.close, close_time=row.Index)

# Usage
params = {"short_window": 10, "long_window": 30, "tp_pct": 0.02, "sl_pct": 0.01}
engine = ParametrizedMACross(commission=0.001)
engine.states["params"] = params
data = pd.read_csv("data.csv")
engine.add_data_stream(data)
engine.run()
```

#### **7.3 Backtest with Parameter Optimization**

```python
class OptimizedMACross(BacktestEngine):
    def preprocess_data(self):
        # Extract parameter values from states
        df = self.data_stream
        short_window = self.states["params"]["short_window"]
        long_window = self.states["params"]["long_window"]

        # Calculate moving averages
        df["short_ma"] = df["close"].rolling(window=short_window).mean()
        df["long_ma"] = df["close"].rolling(window=long_window).mean()
        return df

    def strategy(self, row):
        # Assign variables for positions
        long_position = self.position_book.get_position_by_tag("long")

        # Entry and exit logic
        if row.short_ma > row.long_ma and not long_position:
            tp_long = row.close * (1 + self.states['params']['tp_pct'])
            sl_long = row.close * (1 - self.states['params']['sl_pct'])
            self.position_book.open_long_position(quantity=1, open_price=row.close, tag="long", tp=tp_long, sl=sl_long, open_time=row.Index)
        elif row.short_ma < row.long_ma and long_position:
            self.position_book.close_position(tag="long", close_price=row.close, close_time=row.Index)

# Define parameter choices and constraints
param_choices = {
    "short_window": [10, 20, 30],
    "long_window": [50, 100, 150],
    "tp_pct": [0.01, 0.02, 0.03],
    "sl_pct": [0.01, 0.02, 0.03]
}

def constraints(params):
    return params["short_window"] < params["long_window"] and params['tp_pct'] >= params['sl_pct'] * 0.8

engine = OptimizedMACross(commission=0.001)
pareto_results = engine.optimize(param_choices, optimize_metrics=["sharpe_ratio"], constraints=constraints)
```

---
