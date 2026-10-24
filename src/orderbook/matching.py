"""Matching engine: trades incoming limit orders against the order book.

Design notes:
- Matching follows price-time priority: an incoming order trades against the
  best opposite price first, and against the oldest order within a price level.
- A trade executes at the resting (maker) order's price, so the incoming
  (taker) order can receive a better price than its limit.
- A resting order that is partially filled keeps its place in the queue.
- Whatever is left of an incoming order after matching rests in the book.
  An order that fills completely never enters the book or its index.
- The engine changes the book only through its public methods.
"""

from orderbook.book import OrderBook
from orderbook.order import Order, Side, Trade


def _crosses(order, best_opposite_price):
    """Return True if the order's limit price can trade at best_opposite_price.

    Equal prices cross: a bid at 103 trades against an ask at 103.
    """

    if order.side == Side.BID:
        return order.price >= best_opposite_price
    else:
        return order.price <= best_opposite_price


class MatchingEngine:
    """Matches incoming orders against an OrderBook and reports the trades.

    The engine keeps no trade history: submit() returns the trades it produced
    and the caller decides what to do with them. It only remembers a counter
    that gives each trade a sequential, deterministic ID (TRD_0001, ...), so
    replaying the same input gives the same IDs.
    """

    orderbook: OrderBook
    trade_id_counter: int

    def __init__(self, orderbook: OrderBook):
        self.orderbook = orderbook
        self.trade_id_counter = 1

    def submit(self, order: Order):
        """Match an incoming limit order and return its trades, oldest first.

        Any unfilled remainder rests in the book, and the order's
        filled_quantity is updated in place. Raises ValueError, before any
        trade, if the ID is already resting or the side is invalid.
        """

        executed_trade = []

        if order.id in self.orderbook.index:
            raise ValueError("Duplicate order ID")

        if order.side == Side.BID:
            orderbook_side = Side.ASK
        elif order.side == Side.ASK:
            orderbook_side = Side.BID
        else:
            raise ValueError("Unregistered side, side is not BID or ASK")

        while order.remaining_quantity > 0:
            top_order = self.orderbook.get_top_order(orderbook_side)
            if top_order is None:
                self.orderbook.add_order(order)
                return executed_trade

            if not _crosses(order, top_order.price):
                self.orderbook.add_order(order)

                return executed_trade

            executed_quantity = min(order.remaining_quantity, top_order.remaining_quantity)
            executed_trade.append(Trade(
                id=f"TRD_{self.trade_id_counter:04d}",
                buy_order_id=order.id if order.side == Side.BID else top_order.id,
                sell_order_id=order.id if order.side == Side.ASK else top_order.id,
                taker_order_id=order.id,
                price=top_order.price,
                quantity=executed_quantity,
                timestamp=order.timestamp,
            ))

            top_order.filled_quantity += executed_quantity
            order.filled_quantity += executed_quantity

            self.trade_id_counter += 1

            if top_order.remaining_quantity == 0:
                self.orderbook.cancel_order(top_order.id)

        return executed_trade
