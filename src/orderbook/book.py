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
