"""Matching engine: decides when an incoming order trades against the book.

TODO (Milestone 5):
- Given an incoming limit order, determine whether it crosses the opposite side.
- Walk the opposite side from best price outward, FIFO within a level, until:
    * the incoming order is fully filled, or
    * the next price no longer crosses the incoming limit price, or
    * the opposite side is exhausted.
- Emit a Trade for each match (one incoming order can produce many trades).
- Handle partial fills on both the incoming order and the resting order.
- Any unfilled remainder of the incoming order rests in the book.
- Edge cases: exact price match, incoming order sweeping multiple levels,
  self-trade (same participant on both sides, if you model participants), empty book.
"""
