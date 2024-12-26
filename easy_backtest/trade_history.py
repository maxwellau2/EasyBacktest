from datetime import datetime
import numpy as np
import pandas as pd

class Trade:
    def __init__(self, tag: str, mode: str, quantity: float, open_price: float, close_price: float, profit: float, pct: float, open_time: datetime = None, close_time: datetime = None):
        """
        Represents the trade log for a closed position.
        tag: the tag of the closed position
        mode: the mode of the position ("long" or "short")
        quantity: the quantity of the position that was closed
        open_price: the price at which the position was opened
        close_price: the price at which the position was closed
        profit: the profit from the closed position
        pct: the percentage profit/loss from the closed position
        open_time: the time at which the position was opened
        close_time: the time at which the position was closed
        """
        self.tag = tag
        self.mode = mode
        self.quantity = quantity
        self.open_price = open_price
        self.close_price = close_price
        self.profit = profit
        self.pct = pct
        self.open_time = open_time
        self.close_time = close_time

    def __repr__(self):
        return (f"Trade(tag={self.tag}, mode={self.mode}, quantity={self.quantity}, "
                f"open_price={self.open_price}, close_price={self.close_price}, profit={self.profit}, pct={self.pct})")


class TradeHistory:
    def __init__(self):
        self.trades: list[Trade] = []

    def add_trade(self, tag: str, mode: str, quantity: float, open_price: float, close_price: float, profit: float, pct: float, open_time: datetime = None, close_time: datetime = None):
        trade = Trade(tag, mode, quantity, open_price, close_price, profit, pct, open_time, close_time)
        self.trades.append(trade)
        return trade
    
    def _convert_types(self, stats: dict) -> dict:
        """
        Converts numpy data types to native Python data types for a dictionary.

        Args:
            stats (dict): Dictionary with potentially numpy data types.

        Returns:
            dict: Dictionary with all values converted to native Python types.
        """
        return {key: (float(value) if isinstance(value, (np.float32, np.float64))
                      else int(value) if isinstance(value, (np.int32, np.int64))
                      else value)
                for key, value in stats.items()}

    def to_dataframe(self):
        """
        Converts the trade history to a Pandas DataFrame.
        Each trade is represented as a row in the DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the trade history.
        """
        if not self.trades:
            return pd.DataFrame(columns=["tag", "mode", "quantity", "open_price", "close_price", "profit", "pct", "open_time", "close_time"])

        return pd.DataFrame([{
            "tag": trade.tag,
            "mode": trade.mode,
            "quantity": trade.quantity,
            "open_price": trade.open_price,
            "close_price": trade.close_price,
            "profit": trade.profit,
            "pct": trade.pct,
            "open_time": trade.open_time,
            "close_time": trade.close_time
        } for trade in self.trades])

    def get_stats(self, annualization_factor: float = 365 * 24):
        """
        Calculates various statistics to evaluate the trading strategy.
        annualization_factor: the factor to annualize the profit and loss values, defaults to 365 * 24 for hourly data

        Returns:
            dict: Dictionary containing calculated metrics.
        """
        # get the timeframe of the datastream for annualization

        df = self.to_dataframe()

        if df.empty:
            return {
                "total_trades": 0,
                "total_profit": 0.0,
                "average_profit": 0.0,
                "win_rate": 0.0,
                "max_profit": 0.0,
                "max_loss": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "max_consecutive_wins": 0,
                "max_consecutive_losses": 0,
                "avg_consecutive_wins": 0.0,
                "avg_consecutive_losses": 0.0,
                "expectancy": 0.0,
                "max_drawdown_percent": 0.0
            }

        # Metrics calculations
        total_trades = len(df)
        total_profit = df["profit"].sum()
        average_profit = df["profit"].mean()
        wins = df[df["profit"] > 0]
        losses = df[df["profit"] <= 0]
        win_rate = len(wins) / total_trades if total_trades > 0 else 0.0
        max_profit = df["profit"].max()
        max_loss = df["profit"].min()
        profit_factor = wins["profit"].sum() / abs(losses["profit"].sum()) if not losses.empty else float("inf")
        average_win = wins["profit"].mean() if not wins.empty else 0.0
        average_loss = losses["profit"].mean() if not losses.empty else 0.0

        # Consecutive wins and losses
        profit_signs = (df["profit"] > 0).astype(int)  # 1 for win, 0 for loss
        streaks = profit_signs.diff().ne(0).cumsum()
        streaks_counts = profit_signs.groupby(streaks).sum()
        streaks_lengths = profit_signs.groupby(streaks).size()

        win_streaks_lengths = streaks_lengths[profit_signs.groupby(streaks).mean() == 1]
        loss_streaks_lengths = streaks_lengths[profit_signs.groupby(streaks).mean() == 0]

        max_consecutive_wins = win_streaks_lengths.max() if not win_streaks_lengths.empty else 0
        max_consecutive_losses = loss_streaks_lengths.max() if not loss_streaks_lengths.empty else 0
        avg_consecutive_wins = win_streaks_lengths.mean() if not win_streaks_lengths.empty else 0.0
        avg_consecutive_losses = loss_streaks_lengths.mean() if not loss_streaks_lengths.empty else 0.0

        # Sharpe Ratio (simplified, assuming risk-free rate = 0)
        if total_trades > 1:
            sharpe_ratio = df["profit"].mean() / df["profit"].std() * np.sqrt(annualization_factor)
        else:
            sharpe_ratio = 0.0

        # Expectancy calculation
        expectancy = (win_rate * average_win) + ((1 - win_rate) * average_loss)

        # Adjusted Max Drawdown %
        df["cumulative_pnl"] = df["profit"].cumsum()
        df["peak_pnl"] = df["cumulative_pnl"].cummax()
        df["drawdown"] = df["cumulative_pnl"] - df["peak_pnl"]

        # Avoid division by zero; handle cases where peak_pnl == 0

        max_drawdown_percent = df["drawdown"].min()  # Min value represents the largest drawdown

        stats = {
            "total_trades": total_trades,
            "total_profit": total_profit,
            "win_rate": win_rate,
            "expectancy": expectancy,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_percent": max_drawdown_percent,
            "average_profit": average_profit,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "profit_factor": profit_factor,
            "average_win": average_win,
            "average_loss": average_loss,
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            "avg_consecutive_wins": avg_consecutive_wins,
            "avg_consecutive_losses": avg_consecutive_losses,
        }

        # Convert numpy types to native Python types
        stats = self._convert_types(stats)
        return stats



    def __repr__(self):
        return f"TradeHistory(trades={self.trades})"