"""The order book: resting orders organized by side and price level.

TODO (Milestones 3-4):
- Store bids and asks so that:
    * best bid = highest price, best ask = lowest price
    * orders at the same price are served FIFO (time priority)
    * cancel by order id is fast
  Think about the complexity of each operation (add, cancel, best price, depth) for your chosen structures.
- Operations to support:
    * add a resting order
    * cancel by order id (what if the id is unknown or already filled?)
    * best bid / best ask (what if a side is empty?)
    * spread (what if one side is empty?)
    * depth: total quantity at each price level, top N levels per side
- Keep the invariant in mind: no empty price levels should linger in the book.
"""
import heapq

from orderbook.order import Side


def best_price(side_levels, side_heap, side_price_sign):
    """Return the best live price on one side, or None if it is empty.

    Pops stale heap entries (levels emptied by cancels) as a side effect.
    side_price_sign is -1 for bids (heap stores negated prices), 1 for asks.
    """

    while side_heap:
        current_best_price = side_price_sign * side_heap[0]
        if current_best_price in side_levels:
            return current_best_price
        else:
            heapq.heappop(side_heap)

    return None


class OrderBook:
    def __init__(self):
        self.bid_levels = dict()
        self.ask_levels = dict()
        self.bid_heap = []
        self.ask_heap = []
        self.index = dict()

    def add_order(self, order):
        if order.id in self.index.keys():
            raise ValueError("Duplicate order ID")

        if order.side == Side.BID:
            side_levels = self.bid_levels
            side_heap = self.bid_heap
            side_price = -1 * order.price
        elif order.side == Side.ASK:
            side_levels = self.ask_levels
            side_heap = self.ask_heap
            side_price = order.price
        else:
            raise ValueError("Unregistered side, side is not BID or ASK")

        self.index[order.id] = order

        if order.price not in side_levels:
            side_levels[order.price] = {}
            heapq.heappush(side_heap, side_price)

        side_levels[order.price][order.id] = order

    def cancel_order(self, order_id):
        if order_id not in self.index:
            raise ValueError("Order is not available")

        order_to_cancel = self.index[order_id]
        if order_to_cancel.side == Side.BID:
            side_levels = self.bid_levels
        elif order_to_cancel.side == Side.ASK:
            side_levels = self.ask_levels
        else:
            raise ValueError("Unregistered side, side is not BID or ASK")

        side_levels[order_to_cancel.price].pop(order_id)

        if not side_levels[order_to_cancel.price]:
            side_levels.pop(order_to_cancel.price)

        self.index.pop(order_id)

    def best_bid(self):
        return best_price(self.bid_levels, self.bid_heap, -1)

    def best_ask(self):
        return best_price(self.ask_levels, self.ask_heap, 1)
