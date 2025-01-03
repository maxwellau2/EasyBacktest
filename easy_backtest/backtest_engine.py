from concurrent.futures import ProcessPoolExecutor
import datetime
import json
import random
from tqdm import tqdm
from .position_book import PositionBook
import itertools
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BacktestEngine(ABC):
    def __init__(self, commission: float, portfolio_size: float=100):
        self.commission = commission
        # we store portfolio size in position book in order to calculate pnl based on portfolio size
        self.position_book = PositionBook(commission=commission, portfolio_size=portfolio_size)
        self.data_stream = None
        self.other_data_steams = {}
        self.has_run = False
        # use this to store any state information
        self.states = {}
        self._portfolio_size = portfolio_size

    def get_portfolio_size(self):
        return self.position_book.get_portfolio_size()

    def add_data_stream(self, data_stream: pd.DataFrame):
        required_columns = {"open", "high", "low", "close", "volume"}
        missing_columns = required_columns - set(data_stream.columns)
        assert not missing_columns, f"Data stream must contain the following columns: {missing_columns}"
        assert isinstance(data_stream, pd.DataFrame), "Data stream must be a Pandas DataFrame"
        self.data_stream = data_stream

    def add_other_data_stream(self, data_stream: pd.DataFrame, name: str):
        self.other_data_steams[name] = data_stream

    def preprocess_data(self):
        # optional if you want to preprocess the data before running the backtest
        # else you can directly pass in the dataframe via add_data_stream
        return self.data_stream
    
    @abstractmethod
    def strategy(self):
        pass

    def before_step(self, index, row):
        """
        Hook for logic to execute before processing each row.
        Default implementation handles TP/SL triggers.
        """
        self.position_book.incur_tp_sl(current_close=row.close, current_high=row.high, current_low=row.low, current_open=row.open, current_time=row.Index)

    def after_step(self, index, row):
        """Optional hook to execute logic after processing each row."""
        pass

    def run(self):
        """
        Executes the backtest by iterating through the data stream.
        """
        assert self.data_stream is not None, "Data stream must be added before running the backtest"
        df = self.preprocess_data()
        self.has_run = True
        for i, row in enumerate(df.itertuples()):
            self.before_step(i, row)
            self.strategy(row)
            self.after_step(i, row)


    def get_trade_history(self):
        return self.position_book.trade_history

    def get_trading_stats(self):
        return self.position_book.trade_history.get_stats(initial_portfolio=self._portfolio_size)
    
    def evaluate_combination(self, param_values):
        """
        Evaluates a single parameter combination by running the backtest.
        """
        params = dict(zip(self.param_names, param_values))
        self.states["params"] = params

        # Reset and run the backtest
        position_book = PositionBook(self.commission, self._portfolio_size)  # Reset the position book
        self.position_book = position_book
        self.has_run = False
        self.run()

        # Get stats and evaluate the target metric
        stats = self.get_trading_stats()
        return {"params": params, **stats}
    
    def pareto_front(self, results, metrics):
        """
        Finds the Pareto front for multi-objective optimization.

        Args:
            results (list): List of dictionaries containing parameter stats.
            metrics (list): List of metrics to optimize.

        Returns:
            list: Pareto-optimal parameter sets.
        """
        pareto_set = []
        for res in results:
            dominated = False
            for other in results:
                if all(other[metric] >= res[metric] for metric in metrics) and any(other[metric] > res[metric] for metric in metrics):
                    dominated = True
                    break
            if not dominated:
                pareto_set.append(res)
        return pareto_set
    
    

    def evaluate_and_store(self, param_combination, optimize_metrics):
        """
        Evaluates a single parameter combination and returns the results.

        Args:
            param_combination (tuple): A single combination of parameter values.
            optimize_metrics (list): Metrics to optimize.
            constraints (callable): Function to apply constraints to parameter combinations.

        Returns:
            dict: Results for the parameter combination.
        """
        params = dict(zip(self.param_names, param_combination))
        # Example mock implementation for backtesting
        # Replace this with actual backtesting logic
        result = {
            "params": params,
            "metrics": {metric: random.uniform(0, 1) for metric in optimize_metrics},
        }
        return result

    
    def optimize_random(self, param_choices: dict, optimize_metrics: list, constraints=None, n_samples=1000):
        """
        Optimizes the strategy parameters using random search with parallel processing.

        Args:
            param_choices (dict): Dictionary of parameter names and their possible values.
            optimize_metrics (list): Metrics to optimize.
            constraints (callable, optional): A function that checks if a parameter combination is valid.
            n_samples (int): Number of random samples to evaluate.

        Returns:
            list: Pareto-optimal results.
        """
        assert self.data_stream is not None, "Data stream must be added before optimizing."

        self.param_names = list(param_choices.keys())
        param_combinations = list(itertools.product(*param_choices.values()))

        if constraints:
            all_combinations = [combo for combo in param_combinations if constraints(dict(zip(self.param_names, combo)))]

        # Randomly select parameter combinations
        sampled_combinations = random.sample(all_combinations, min(n_samples, len(all_combinations)//10))

        results = []
        print(f"{len(sampled_combinations)} random combinations to test, please wait...")

        with ProcessPoolExecutor() as executor:
            with tqdm(total=len(sampled_combinations), desc="Optimizing Parameters") as pbar:
                futures = [
                    executor.submit(self.evaluate_combination, combo)
                    for combo in sampled_combinations
                ]
                for future in futures:
                    results.append(future.result())
                    pbar.update(1)

        # Save results to a JSON file
        with open(f"optimization_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as json_file:
            json.dump(results, json_file, indent=4)

        # Extract Pareto-optimal results
        pareto_set = self.pareto_front(results, optimize_metrics)
        return pareto_set


    def optimize(self, param_choices: dict, optimize_metrics: list, constraints=None):
        """
        Optimizes the strategy parameters using grid search with parallel processing.

        Args:
            param_choices (dict): Dictionary of parameter names and their possible values.
            optimize_target (str): The metric to maximize. Default is "sharpe_ratio".
            constraints (callable, optional): A function that checks if a parameter combination is valid.

        Returns:
            dict: Best parameters and their corresponding stats.
        """
        assert self.data_stream is not None, "Data stream must be added before optimizing."
        # assert not self.has_run, "Engine must be reset before optimization."

        # Generate all parameter combinations
        self.param_names = list(param_choices.keys())  # Store for evaluate_combination
        param_combinations = list(itertools.product(*param_choices.values()))

        if constraints:
            param_combinations = [combo for combo in param_combinations if constraints(dict(zip(self.param_names, combo)))]

        # Initialize tracking
        best_params = None
        best_target_value = float("-inf")
        best_stats = None
        best_trade_history = None
        results = []
        print(f"{len(param_combinations)} combinations to test, please wait...")
        # Run parameter combinations in parallel
        with ProcessPoolExecutor() as executor:
            with tqdm(total=len(param_combinations), desc="Optimizing Parameters") as pbar:
                futures = [
                    executor.submit(self.evaluate_combination, combo)
                    for combo in param_combinations
                ]
                for future in futures:
                    results.append(future.result())
                    pbar.update(1)

        # Update the position_book with the best trade history for future plotting
        with open(f"optimization_results{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as json_file:
            json.dump(results, json_file, indent=4)
        pareto_set = self.pareto_front(results, optimize_metrics)
        return pareto_set
    
    def plot_trading_stats(self):
        """
        Plots an OHLC chart with trades represented as red (short) or green (long) dotted lines,
        displays cumulative PnL as a subplot, and shows trading stats in a table format below the chart.
        """
        assert self.data_stream is not None, "Data stream must be added before plotting trades"
        assert self.has_run, "Backtest must be run before plotting trades"

        # Get trade history and stats
        trade_history_df = self.get_trade_history().to_dataframe()
        trading_stats = self.get_trading_stats()

        # Calculate cumulative PnL
        trade_history_df["cumulative_pnl"] = trade_history_df["profit"].cumsum() + self._portfolio_size

        # Create subplots with 3 rows: one for OHLC, one for cumulative PnL, and one for the table
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]],
            row_heights=[0.2, 0.6, 0.2]
        )

        # Add OHLC candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data_stream.index,
                open=self.data_stream["open"],
                high=self.data_stream["high"],
                low=self.data_stream["low"],
                close=self.data_stream["close"],
                name="OHLC"
            ),
            row=2,
            col=1
        )

        # Plot trades as dotted lines
        for _, trade in trade_history_df.iterrows():
            color = "green" if trade["mode"] == "long" else "red"
            fig.add_trace(
                go.Scatter(
                    x=[trade["open_time"], trade["close_time"]],
                    y=[trade["open_price"], trade["close_price"]],
                    mode="lines+markers",
                    line=dict(color=color, dash="dot"),
                    name=f"Trade ({trade['mode']})"
                ),
                row=2,
                col=1
            )

        # Add cumulative PnL line chart
        fig.add_trace(
            go.Scatter(
                x=trade_history_df["close_time"],
                y=trade_history_df["cumulative_pnl"],
                mode="lines",
                line=dict(color="blue"),
                name="Cumulative PnL"
            ),
            row=1,
            col=1
        )

        # Prepare trading stats for the table
        headers = []
        values = []
        for key, value in trading_stats.items():
            headers.append(key)
            if isinstance(value, (int, float)):
                # Round to 4 significant figures using numpy
                values.append(float(np.format_float_positional(value, precision=4, unique=False, fractional=False, trim="k")))
            else:
                # Keep non-numeric values unchanged
                values.append(value)

        # Add trading stats table
        headers = []
        values = []
        for key, value in trading_stats.items():
            headers.append(key)
            if isinstance(value, (int, float)):
                # Round to 4 significant figures using numpy
                values.append(float(np.format_float_positional(value, precision=4, unique=False, fractional=False, trim="k")))
            else:
                # Keep non-numeric values unchanged
                values.append(value)

        # Add trading stats table
        fig.add_trace(go.Table(header=dict(values=headers), cells=dict(values=values)),
            row=3,
            col=1,
        )

        # Update layout
        fig.update_layout(
            annotations=[
            dict(
                text="Cumulative PnL",
                x=0.5,
                y=1.0,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="white")
            ),
            dict(
                text="OHLC Chart with Trades",
                x=0.5,
                y=0.66,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="white")
            ),
            dict(
                text="Trading Stats",
                x=0.5,
                y=0.2,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="white")
            ),
        ],

            title="OHLC Chart with Trades, Cumulative PnL, and Stats",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=1080,
            showlegend=True
        )

        fig.update_xaxes(rangeslider_visible=False)
        fig.show()
    