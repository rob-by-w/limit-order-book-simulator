"""Core data models: Side, Order, Trade.

TODO (Milestone 2):
- Side: bid/ask, as an Enum. Consider whether a helper for "the opposite side" would be useful later.
- Order: id, side, price, quantity, timestamp/sequence number.
    * Decide how to represent price (float vs int ticks vs Decimal) and be ready to defend it.
    * Decide how to represent time priority. Is wall-clock time a good idea? What about ties?
    * Does an order need to track remaining quantity separately from original quantity?
    * Should Order be mutable? Think about what happens on a partial fill.
- Trade: what two orders matched, at what price, for what quantity, and when.
    * Which order's price does the trade execute at: the resting or the incoming one?
- Edge cases to validate: non-positive quantity, non-positive price, duplicate order ids.
"""
