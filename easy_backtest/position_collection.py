from typing import List, Optional
from .position import Position

class PositionCollection:
    def __init__(self):
        self.positions: List[Position] = []

    def add_position(self, position: Position):
        """Adds a new position to the collection."""
        self.positions.append(position)

    def remove_position(self, position: Position):
        """Removes a position from the collection."""
        self.positions.remove(position)

    def find_by_tag(self, tag: str) -> Optional[Position]:
        """Finds a position by its tag."""
        for position in self.positions:
            if position.tag == tag:
                return position
        return None

    def __len__(self):
        return len(self.positions)

    def __getitem__(self, index):
        return self.positions[index]

    def __iter__(self):
        return iter(self.positions)

    def __repr__(self):
        return f"PositionCollection(positions={self.positions})"
