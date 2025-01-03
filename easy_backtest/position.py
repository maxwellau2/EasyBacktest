from datetime import datetime


class Position:
    def __init__(self, quantity: float, open_price: float, commission: float, mode: str, tag: str = None, tp: float = None, sl: float = None, open_time: datetime = None, close_time: datetime = None):
        """
        quantity: the quantity of the position
        open_price: the price at which the position is opened
        commission: the commission charged for the position
        mode: the mode of the position ("long" or "short")
        tag: an optional tag for the position
        tp: the take profit price for the position
        sl: the stop loss price for the position
        """
        self.quantity = quantity
        self.open_price = open_price
        self.commission = commission
        assert mode in ["long", "short"], "Invalid position mode, must be 'long' or 'short'"
        self.mode = mode
        self.tag = tag
        if mode == "long":
            if tp:
                assert tp > open_price, "Long position: take profit price must be greater than the open price"
            if sl:
                assert sl < open_price, "Long position: Stop loss price must be less than the open price"
        elif mode == "short":
            if tp:
                assert tp < open_price, "Short position: take profit price must be less than the open price"
            if sl:
                assert sl > open_price, "Short position: Stop loss price must be greater than the open price"
        self.tp = tp
        self.sl = sl
        self.open_time = open_time
        self.close_time = close_time

    def __repr__(self):
        return f"Position(quantity={self.quantity}, price={self.open_price}, commission={self.commission})"
    
    def get_pnl(self, current_price: float):
        """
        returns the profit and loss for the position
        current_price: the current price of the asset
        """
        if self.mode == "long":
            profit = (current_price - self.open_price) * self.quantity * (1-self.commission)
            pct = (current_price - self.open_price) / (self.open_price) * (1-self.commission)
        else :
            profit = (self.open_price - current_price) * self.quantity * (1-self.commission)
            pct = (self.open_price - current_price) / (self.open_price) * (1-self.commission)
        
        return {"profit": profit, "pct": pct}
    
    def is_long(self):
        return self.mode == "long"
    
    def is_short(self):
        return self.mode == "short"

    def close_position(self, close_price: float, close_amt: float = 1):
        """
        closes the position at the given price,
        close_price: the price at which the position is to be closed
        close_amt: the percentage of the position to be closed
        returns:
        profit: the profit of the position
        pct: the percentage of the position that was closed
        remaining: the remaining quantity of the position
        """
        # check if close_amt is between 0 and 1
        commision_amount = self.commission * self.quantity * close_amt * close_price
        if not (0 <= close_amt <= 1):
            raise ValueError("close_amt must be between 0 and 1")
        if self.is_long():
            profit = (close_price - self.open_price) * self.quantity * close_amt  - commision_amount
            pct = profit/self.open_price
        else :
            profit = (self.open_price - close_price) * self.quantity * close_amt - commision_amount
            pct = profit/self.open_price
        if close_amt == 1:
            return {"profit": profit, "pct": pct, "remaining": 0}
        self.quantity -= self.quantity * close_amt
        return {"profit": profit, "pct": pct, "remaining": self.quantity}
