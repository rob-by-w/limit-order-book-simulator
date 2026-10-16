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
