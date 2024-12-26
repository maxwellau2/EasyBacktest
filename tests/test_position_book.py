from datetime import datetime
import pytest
from easy_backtest.position_book import PositionBook
from easy_backtest.position import Position

def test_open_long_position():
    # Test opening a long position
    book = PositionBook(commission=0.01)
    book.open_long_position(quantity=10, open_price=100.0, tag="pos1")

    assert len(book.position_collection) == 1
    pos = book.position_collection.find_by_tag("pos1")
    assert pos is not None
    assert pos.mode == "long"
    assert pos.quantity == 10
    assert pos.open_price == 100.0

def test_open_short_position():
    # Test opening a short position
    book = PositionBook(commission=0.01)
    book.open_short_position(quantity=5, open_price=150.0, tag="pos2")

    assert len(book.position_collection) == 1
    pos = book.position_collection.find_by_tag("pos2")
    assert pos is not None
    assert pos.mode == "short"
    assert pos.quantity == 5
    assert pos.open_price == 150.0

def test_close_position_full():
    # Test closing a position fully
    book = PositionBook(commission=0.01)
    book.open_long_position(quantity=10, open_price=100.0, tag="pos1")

    result = book.close_position(tag="pos1", close_price=110.0, close_amt=1)
    assert len(book.position_collection) == 0  # Position should be removed
    assert result["profit"] == pytest.approx(99.0)  # Profit = (110 - 100) * 10 * (1 - 0.01)

    # Verify trade history
    assert len(book.trade_history.trades) == 1
    trade = book.trade_history.trades[0]
    assert trade.tag == "pos1"
    assert trade.mode == "long"
    assert trade.quantity == 10
    assert trade.profit == pytest.approx(99.0)

def test_close_position_partial():
    # Test closing a position partially
    book = PositionBook(commission=0.01)
    book.open_short_position(quantity=10, open_price=150.0, tag="pos2")

    result = book.close_position(tag="pos2", close_price=140.0, close_amt=0.5)
    assert len(book.position_collection) == 1  # Position should remain
    pos = book.position_collection.find_by_tag("pos2")
    assert pos.quantity == 5  # Remaining quantity after partial close

    # Verify trade history
    assert len(book.trade_history.trades) == 1
    trade = book.trade_history.trades[0]
    assert trade.tag == "pos2"
    assert trade.mode == "short"
    assert trade.quantity == 5  # Quantity closed
    assert trade.profit == pytest.approx(49.5)  # Profit = (150 - 140) * 5 * (1 - 0.01)

def test_get_all_pnls():
    # Test getting PnL for all positions
    book = PositionBook(commission=0.01)
    book.open_long_position(quantity=10, open_price=100.0, tag="pos1")
    book.open_short_position(quantity=5, open_price=150.0, tag="pos2")

    pnls = book.get_all_pnls(current_price=110.0)
    assert pnls["pos1"]["profit"] == pytest.approx(99.0)  # (110 - 100) * 10 * (1 - 0.01)
    assert pnls["pos2"]["profit"] == pytest.approx(198.0)  # (150 - 110) * 5 * (1 - 0.01)

def test_incur_tp_sl():
    # Test closing positions based on TP and SL
    book = PositionBook(commission=0.01)
    pos1 = Position(quantity=10, open_price=100.0, commission=0.01, mode="long", tag="pos1", tp=110.0, sl=90.0)
    pos2 = Position(quantity=5, open_price=150.0, commission=0.01, mode="short", tag="pos2", tp=110.0, sl=160.0)
    book.position_collection.add_position(pos1)
    book.position_collection.add_position(pos2)

    # Trigger TP for pos1 and SL for pos2
    book.incur_tp_sl(current_close=110.0, current_high=110.0, current_low=100.0, current_open=100.0, current_time=datetime.now())

    # Verify positions
    assert len(book.position_collection) == 0  # Both positions should be closed

    # Verify trade history
    assert len(book.trade_history.trades) == 2
    trade1 = book.trade_history.trades[0]
    assert trade1.tag == "pos1"
    assert trade1.profit == pytest.approx(99.0)  # (110 - 100) * 10 * (1 - 0.01)

    trade2 = book.trade_history.trades[1]
    assert trade2.tag == "pos2"
    assert trade2.profit == pytest.approx(198.0)  # (150 - 110) * 5 * (1 - 0.01)
