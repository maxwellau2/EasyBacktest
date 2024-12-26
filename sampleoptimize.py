import pprint

import numpy as np
from easy_backtest.backtest_engine import BacktestEngine

import yfinance as yf



# Step 1: Create a new class that inherits from BacktestEngine
# The crux of the backtesting process is the strategy() method, which is called for each row in the data stream

class MyBacktest(BacktestEngine):
    def preprocess_data(self):
        # Custom preprocessing logic
        self.data_stream['moving_avg'] = self.data_stream['close'].rolling(window=100).mean()

    def strategy(self, row):
        # position size
        position_size = 100
        # Custom strategy logic
        long_tp = row.close * (1 + self.states['params']["tp_pct"])
        long_sl = row.close * (1 - self.states['params']["sl_pct"])
        short_tp = row.close * (1 - self.states['params']["tp_pct"])
        short_sl = row.close * (1 + self.states['params']["sl_pct"])
        current_price = row.close
        qty = position_size / current_price

        long_position = self.position_book.get_position_by_tag("long1")
        short_position = self.position_book.get_position_by_tag("short1")

        if row.close > row.moving_avg:
            if long_position is None:
                self.position_book.open_long_position(quantity=qty, open_price=row.close, tag="long1", open_time=row.Index, tp=long_tp, sl=long_sl)

        elif row.close < row.moving_avg:
            if short_position is None:
                self.position_book.open_short_position(quantity=qty, open_price=row.close, tag="short1", open_time=row.Index, tp=short_tp, sl=short_sl)

    def before_step(self, index, row):
        # Custom logic before step
        super().before_step(index, row)  # Retain TP/SL logic
        # Additional pre-step actions
        print(f"Processing row {index} with close price {row.close}")


if __name__ == "__main__":
    position_size = 100
    # Example usage
    # 2. Create a new backtest instance
    backtest = MyBacktest(commission=0.01)
    # define the parameters to optimize
    params = {
        "tp_pct" : 0.07,
        "sl_pct" : 0.03,
    }
    backtest.states['params'] = params

    # Step 3. import your data from any source in a pandas DataFrame
    # In this case, we fetch historical data for Bitcoin (BTC-USD) using Yahoo Finance
    btc_data = yf.download('BTC-USD', start='2024-01-01', interval='1h')
    print(btc_data.head())
    # Ensure that the columns include open, high, low, close and volume
    # rename columns to lowercase, if necessary
    print(btc_data.columns)
    btc_data.columns = [col[0].lower() for col in btc_data.columns]

    # Step 4: Add the data stream to the backtest instance
    backtest.add_data_stream(data_stream=btc_data)

    # Step 5: Define the target metric to optimize
    optimize_target = "sharpe_ratio"

    # Step 6: Define the parameter choices
    param_choices = {
        "tp_pct": np.arange(0.01,0.07,0.01).tolist(),
        "sl_pct": np.arange(0.01,0.07,0.01).tolist(),
    }
    # Step 7: Run optimization
    result = backtest.optimize(param_choices,
                                optimize_target=optimize_target,
                                # add optional constraints based on states
                                constraints = lambda params: params['tp_pct'] > params['sl_pct'])  

    print("Best Parameters:", result["best_params"])
    print("Best Target Value:", result["best_target_value"])
    print("Best Stats:", result["best_stats"])

    backtest.plot_trading_stats()
