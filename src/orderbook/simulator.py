"""Simulator: feeds parsed events into the order book and collects the output.

run() takes (line_number, event) tuples, as produced by read_order_flow_csv,
and returns a SimulationResult for that call only: the trades, the rejections,
and a BookSnapshot of the book afterward. The book, the order-id registry and
the sequence counter persist across calls, so run() can be called repeatedly.

Dispatch:
- New: rejected if the id was already seen, otherwise sent to the matching engine.
- Cancel: removes a resting order straight from the book (no matching involved);
  an unknown or already-finished id is rejected.
- Rejection: a parse-time rejection is passed through with its line number.
- Any other event type raises TypeError.

Priority: orders are sequenced by arrival, not by timestamp. Timestamps come
from the sender, are informational, and may go backwards. Within a price
level the earlier arrival fills first, and a trade carries the aggressor's
timestamp.

Order ids are unique per session: a reused id is rejected as a duplicate even
if the earlier order was filled or cancelled. A rejected event never changes
the book or consumes a sequence number.

Rejections are reported as RejectedEvent(line_number, reason), where reason is
a parser RejectionCode or a simulator BusinessRejectionCode.

BookSnapshot is an immutable L2 view: bids highest price first, asks lowest
price first, with total quantity per level.
"""
from dataclasses import dataclass, field
from enum import StrEnum

from orderbook.book import OrderBook, UnknownOrderError
from orderbook.events import New, Cancel, Rejection, RejectionCode
from orderbook.matching import MatchingEngine
from orderbook.order import Trade, Order, Side, Level


class BusinessRejectionCode(StrEnum):
    UNKNOWN_ORDER_ID = "unknown_order_id"
    DUPLICATE_ORDER_ID = "duplicate_order_id"


@dataclass(frozen=True)
class RejectedEvent:
    line_number: int
    reason: BusinessRejectionCode | RejectionCode


@dataclass(frozen=True)
class BookSnapshot:
    bids: tuple[Level, ...]
    asks: tuple[Level, ...]


@dataclass
class SimulationResult:
    trades: list[Trade] = field(default_factory=list)
    rejections: list[RejectedEvent] = field(default_factory=list)
    book_state: BookSnapshot = field(default_factory=BookSnapshot((), ()))


class Simulator:
    def __init__(self) -> None:
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)
        self.order_sequence_number = 1
        self.seen_order_ids = set()

    def run(self, events: list[tuple[int, New | Cancel | Rejection]]) -> SimulationResult:
        trade_list = []
        rejection_list = []

        for line_number, event in events:
            match event:
                case New():
                    self._handle_new(line_number, event, trade_list, rejection_list)

                case Cancel():
                    self._handle_cancel(line_number, event, rejection_list)

                case Rejection():
                    self._handle_rejection(line_number, event, rejection_list)

                case _:
                    raise TypeError(f"Unexpected event type: {event}")

        return SimulationResult(
            trades=trade_list,
            rejections=rejection_list,
            book_state=BookSnapshot(self.order_book.depth(Side.BID), self.order_book.depth(Side.ASK))
        )

    def _handle_new(self, line_number, new_order_event: New, trade_list, rejection_list) -> None:
        if new_order_event.id in self.seen_order_ids:
            rejection_list.append(RejectedEvent(line_number, BusinessRejectionCode.DUPLICATE_ORDER_ID))
            return

        order = Order(id=new_order_event.id,
                      side=new_order_event.side,
                      price=new_order_event.price,
                      order_quantity=new_order_event.order_quantity,
                      timestamp=new_order_event.timestamp,
                      seq_number=self.order_sequence_number
                      )

        self.order_sequence_number += 1
        self.seen_order_ids.add(order.id)

        submit_output = self.matching_engine.submit(order)
        trade_list.extend(submit_output)

    def _handle_cancel(self, line_number, cancel_event: Cancel, rejection_list) -> None:
        try:
            self.order_book.cancel_order(cancel_event.id)
        except UnknownOrderError:
            rejection_list.append(RejectedEvent(line_number, BusinessRejectionCode.UNKNOWN_ORDER_ID))

    def _handle_rejection(self, line_number, event, rejection_list) -> None:
        rejection_list.append(RejectedEvent(line_number, event.reason))
