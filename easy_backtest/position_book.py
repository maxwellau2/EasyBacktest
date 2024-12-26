from datetime import datetime
from .position_collection import PositionCollection
from .position import Position
from .trade_history import TradeHistory

class PositionBook:
    def __init__(self, commission: float):
        self.commission = commission
        self.position_collection = PositionCollection()
        self.trade_history = TradeHistory()

    def get_position_by_tag(self, tag: str):
        return self.position_collection.find_by_tag(tag)

    def open_long_position(self, quantity: float, open_price: float, tag: str = None, tp: float = None, sl: float = None, open_time: datetime = None):
        self.open_position(quantity=quantity, open_price=open_price, mode="long", tag=tag, tp=tp, sl=sl, open_time=open_time)


    def open_short_position(self, quantity: float, open_price: float, tag: str = None, tp: float = None, sl: float = None, open_time: datetime = None):
        self.open_position(quantity=quantity, open_price=open_price, mode="short", tag=tag, tp=tp, sl=sl, open_time=open_time)

    def open_position(self, quantity: float, open_price: float, mode: str, tag: str = None, tp: float = None, sl: float = None, open_time: datetime = None):
        """Opens a new position."""
        pos = Position(quantity=quantity, open_price=open_price, commission=self.commission, mode=mode, tag=tag, tp=tp, sl=sl, open_time=open_time)
        self.position_collection.add_position(pos)

    def close_position(self, tag: str, close_price: float, close_amt: float = 1, close_time: datetime = None):
        """Closes a position with the given tag."""
        pos: Position = self.position_collection.find_by_tag(tag)
        if pos is None:
            raise ValueError(f"Position with tag '{tag}' not found.")

        result = pos.close_position(close_price=close_price, close_amt=close_amt)

        self.trade_history.add_trade(
            tag=pos.tag,
            mode=pos.mode,
            quantity=pos.quantity,
            open_price=pos.open_price,
            close_price=close_price,
            profit=result["profit"],
            pct=result["pct"],
            open_time=pos.open_time,
            close_time=close_time
        )

        if close_amt == 1 or result["remaining"] == 0:
            self.position_collection.remove_position(pos)

        return result

    def get_all_pnls(self, current_price: float):
        """Calculates the PnL for all open positions."""
        return {pos.tag: pos.get_pnl(current_price) for pos in self.position_collection}

    def incur_tp_sl(self, current_close: float, current_high: float, current_low: float, current_open: float, current_time: datetime):
        """Closes positions based on take profit (TP) and stop loss (SL)."""
        for pos in list(self.position_collection):
            if pos.tp is not None and pos.sl is not None:
                if pos.is_long() and (current_high >= pos.tp or current_low <= pos.sl):
                    self.close_position(tag=pos.tag, close_price=current_close, close_amt=1, close_time=current_time)
                elif pos.is_short() and (current_low <= pos.tp or current_high >= pos.sl):
                    self.close_position(tag=pos.tag, close_price=current_close, close_amt=1, close_time=current_time)

    def __repr__(self):
        return f"Positions(position_collection={self.position_collection}, trade_history={self.trade_history})"
