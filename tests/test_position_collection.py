import pytest
from easy_backtest.position import Position
from easy_backtest.position_collection import PositionCollection  # Assuming the class is in `position_collection.py`

def test_add_position():
    # Test adding a position
    collection = PositionCollection()
    position = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")

    collection.add_position(position)
    assert len(collection) == 1
    assert collection[0] == position

def test_remove_position():
    # Test removing a position
    collection = PositionCollection()
    position = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")

    collection.add_position(position)
    collection.remove_position(position)
    assert len(collection) == 0

def test_find_by_tag():
    # Test finding a position by tag
    collection = PositionCollection()
    position1 = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")
    position2 = Position(quantity=5, open_price=150, commission=0.02, mode="short", tag="pos2")

    collection.add_position(position1)
    collection.add_position(position2)

    found = collection.find_by_tag("pos1")
    assert found == position1

    found = collection.find_by_tag("pos2")
    assert found == position2

    found = collection.find_by_tag("nonexistent")
    assert found is None

def test_len():
    # Test __len__
    collection = PositionCollection()
    assert len(collection) == 0

    position = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")
    collection.add_position(position)
    assert len(collection) == 1

def test_getitem():
    # Test __getitem__
    collection = PositionCollection()
    position1 = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")
    position2 = Position(quantity=5, open_price=150, commission=0.02, mode="short", tag="pos2")

    collection.add_position(position1)
    collection.add_position(position2)

    assert collection[0] == position1
    assert collection[1] == position2

def test_iter():
    # Test __iter__
    collection = PositionCollection()
    position1 = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")
    position2 = Position(quantity=5, open_price=150, commission=0.02, mode="short", tag="pos2")

    collection.add_position(position1)
    collection.add_position(position2)

    positions = list(collection)
    assert positions == [position1, position2]

def test_repr():
    # Test __repr__
    collection = PositionCollection()
    position1 = Position(quantity=10, open_price=100, commission=0.01, mode="long", tag="pos1")
    position2 = Position(quantity=5, open_price=150, commission=0.02, mode="short", tag="pos2")

    collection.add_position(position1)
    collection.add_position(position2)

    repr_string = repr(collection)
    assert repr_string == f"PositionCollection(positions={collection.positions})"
