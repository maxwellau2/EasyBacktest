import pytest
import pandas as pd
from easy_backtest.trade_history import Trade, TradeHistory  # Assuming the classes are in `trade_history.py`

def test_trade_creation():
    # Test creating a Trade object
    trade = Trade(
        tag="trade1",
        mode="long",
        quantity=10,
        open_price=100.0,
        close_price=110.0,
        profit=99.0,
        pct=0.099
    )

    assert trade.tag == "trade1"
    assert trade.mode == "long"
    assert trade.quantity == 10
    assert trade.open_price == 100.0
    assert trade.close_price == 110.0
    assert trade.profit == 99.0
    assert trade.pct == 0.099
    assert repr(trade) == (
        "Trade(tag=trade1, mode=long, quantity=10, open_price=100.0, close_price=110.0, profit=99.0, pct=0.099)"
    )

def test_trade_history_add_trade():
    # Test adding trades to TradeHistory
    trade_history = TradeHistory()

    trade1 = trade_history.add_trade(
        tag="trade1",
        mode="long",
        quantity=10,
        open_price=100.0,
        close_price=110.0,
        profit=99.0,
        pct=0.099
    )

    trade2 = trade_history.add_trade(
        tag="trade2",
        mode="short",
        quantity=5,
        open_price=150.0,
        close_price=140.0,
        profit=49.5,
        pct=0.066
    )

    assert len(trade_history.trades) == 2
    assert trade_history.trades[0] == trade1
    assert trade_history.trades[1] == trade2

def test_trade_history_to_dataframe():
    # Test converting trade history to a Pandas DataFrame
    trade_history = TradeHistory()

    trade_history.add_trade(
        tag="trade1",
        mode="long",
        quantity=10,
        open_price=100.0,
        close_price=110.0,
        profit=99.0,
        pct=0.099
    )
    trade_history.add_trade(
        tag="trade2",
        mode="short",
        quantity=5,
        open_price=150.0,
        close_price=140.0,
        profit=49.5,
        pct=0.066
    )

    df = trade_history.to_dataframe()

    # Verify the DataFrame structure and content
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["tag", "mode", "quantity", "open_price", "close_price", "profit", "pct", "open_time", "close_time"]
    assert len(df) == 2
    assert df.iloc[0]["tag"] == "trade1"
    assert df.iloc[1]["tag"] == "trade2"
    assert df.iloc[0]["profit"] == 99.0
    assert df.iloc[1]["pct"] == 0.066

def test_trade_history_to_dataframe_empty():
    # Test converting an empty trade history to a DataFrame
    trade_history = TradeHistory()
    df = trade_history.to_dataframe()

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["tag", "mode", "quantity", "open_price", "close_price", "profit", "pct", "open_time", "close_time"]
    assert df.empty
