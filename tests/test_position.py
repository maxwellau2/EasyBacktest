import pytest
from easy_backtest.position import Position  # Assuming the class is saved in a file named `position.py`

def test_position_initialization():
    # Valid initialization
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="Test")
    assert pos.quantity == 10
    assert pos.open_price == 100
    assert pos.commission == 0.01
    assert pos.mode == "long"
    assert pos.tag == "Test"
    
    # Invalid mode
    with pytest.raises(AssertionError, match="Invalid position mode, must be 'long' or 'short'"):
        Position(quantity=10, open_price=100, commission=0.01, mode="invalid")

def test_get_pnl_long():
    # Test PnL for long position
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="long")
    pnl = pos.get_pnl(current_price=110)
    assert pnl["profit"] == pytest.approx(99.0)  # (110 - 100) * 10 * (1 - 0.01)
    assert pnl["pct"] == pytest.approx(0.099)  # (110 - 100) / 100 * (1 - 0.01)

def test_get_pnl_short():
    # Test PnL for short position
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="short")
    pnl = pos.get_pnl(current_price=90)
    assert pnl["profit"] == pytest.approx(99.0)  # (100 - 90) * 10 * (1 - 0.01)
    assert pnl["pct"] == pytest.approx(0.099)  # (100 - 90) / 100 * (1 - 0.01)

def test_close_position_full_long():
    # Test closing a long position fully
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="long")
    result = pos.close_position(close_price=110, close_amt=1)
    assert result["profit"] == pytest.approx(99.0)  # (110 - 100) * 10 * (1 - 0.01)
    assert result["pct"] == pytest.approx(0.099)  # (110 - 100) / 100 * (1 - 0.01)
    assert result["remaining"] == 0

def test_close_position_partial_long():
    # Test partially closing a long position
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="long")
    result = pos.close_position(close_price=110, close_amt=0.5)
    assert result["profit"] == pytest.approx(49.5)  # Half the quantity
    assert result["pct"] == pytest.approx(0.099)
    assert result["remaining"] == 5  # 50% of 10

def test_close_position_full_short():
    # Test closing a short position fully
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="short")
    result = pos.close_position(close_price=90, close_amt=1)
    assert result["profit"] == pytest.approx(99.0)  # (100 - 90) * 10 * (1 - 0.01)
    assert result["pct"] == pytest.approx(0.099)
    assert result["remaining"] == 0

def test_close_position_partial_short():
    # Test partially closing a short position
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="short")
    result = pos.close_position(close_price=90, close_amt=0.5)
    assert result["profit"] == pytest.approx(49.5)
    assert result["pct"] == pytest.approx(0.099)
    assert result["remaining"] == 5

def test_invalid_close_amt():
    # Test invalid close amount
    pos = Position(quantity=10, open_price=100, commission=0.01, mode="long")
    with pytest.raises(ValueError, match="close_amt must be between 0 and 1"):
        pos.close_position(close_price=110, close_amt=1.5)
