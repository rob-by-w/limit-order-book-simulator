"""The order book: resting limit orders organized by side and price level.

Design notes:
- Each side keeps a dict of price -> level, where a level is a dict of
  order id -> Order. Dicts preserve insertion order, so a level is a FIFO
  queue (time priority) that also supports O(1) cancel by id.
- Each side also keeps a heap of prices to find the best price quickly.
  Bid prices are stored negated, because heapq is a min-heap.
- The levels dict is the source of truth and the heap is only a hint.
  Cancels never touch the heap (lazy deletion), so it can hold stale or
  duplicate prices. Lookups discard them as they reach them.
- An index of order id -> Order lets cancel find an order without scanning.
"""
import heapq

from orderbook.order import Side


class UnknownOrderError(Exception):
    pass


def _best_price(side_levels, side_heap, side_price_sign):
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
    """Resting orders for one instrument, with price-time priority.

    Supports adding and cancelling orders, best bid/ask, spread, and depth.
    Prices are integer ticks. Orders are not matched yet: adding a crossing
    order simply rests it, so the book can be crossed until matching exists.
    """

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
            raise UnknownOrderError("No such order")

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
        return _best_price(self.bid_levels, self.bid_heap, -1)

    def best_ask(self):
        return _best_price(self.ask_levels, self.ask_heap, 1)

    def spread(self):
        current_best_bid = self.best_bid()
        current_best_ask = self.best_ask()

        if (current_best_bid is None) or (current_best_ask is None):
            return None

        return current_best_ask - current_best_bid

    def depth(self, side, n):
        if n <= 0:
            raise ValueError("Invalid depth level input")

        depth_levels = []

        if side == Side.BID:
            side_levels = self.bid_levels
            depth_heap = heapq.nlargest(n, side_levels)
        elif side == Side.ASK:
            side_levels = self.ask_levels
            depth_heap = heapq.nsmallest(n, side_levels)
        else:
            raise ValueError("Unregistered side, side is not BID or ASK")

        for price in depth_heap:
            depth_levels.append(
                (price,
                 sum(current_order.remaining_quantity for current_order in side_levels[price].values()))
            )

        return depth_levels

    def get_top_order(self, side):
        if side == Side.BID:
            current_best_price = self.best_bid()

            if current_best_price is None:
                return None

            current_best_level = self.bid_levels[current_best_price]
        elif side == Side.ASK:
            current_best_price = self.best_ask()

            if current_best_price is None:
                return None

            current_best_level = self.ask_levels[current_best_price]
        else:
            raise ValueError("Unregistered side, side is not BID or ASK")

        return next(iter(current_best_level.values()))
