"""Simulator: feeds a stream of events into the book and collects output.

TODO (Milestone 6):
- Read events in order (sequence matters: it defines time priority).
- Dispatch each event to the book / matching engine.
- Collect and expose emitted trades.
- Optionally print/log top-of-book after each event.
- Provide a command-line entry point that takes a path to a sample stream in data/.
"""
from dataclasses import dataclass, field

from orderbook.book import OrderBook
from orderbook.events import New, Cancel, Rejection
from orderbook.matching import MatchingEngine
from orderbook.order import Trade, Order, Side


@dataclass
class SimulationResult:
    trades: list[Trade] = field(default_factory=list)
    rejections: list[Rejection] = field(default_factory=list)
    final_book_state: dict = field(default_factory=dict)


class Simulator:
    def __init__(self) -> None:
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)
        self.order_sequence_number = 1

    def run(self, events: list[tuple[int, New | Cancel | Rejection]]) -> SimulationResult:
        for line_number, event in events:
            match event:
                case New():
                    self.matching_engine.submit(self._handle_new(event))
                case Cancel():
                    self.order_book.cancel_order(self._handle_cancel(event))

        return SimulationResult(
            trades=[],
            rejections=[],
            final_book_state={
                Side.BID: self.order_book.depth(Side.BID, 5),
                Side.ASK: self.order_book.depth(Side.ASK, 5)
            },
        )

    def _handle_new(self, new_order_event: New) -> Order:
        self.order = Order(id=new_order_event.id,
                           side=new_order_event.side,
                           price=new_order_event.price,
                           order_quantity=new_order_event.order_quantity,
                           timestamp=new_order_event.timestamp,
                           seq_number=self.order_sequence_number
                           )
        self.order_sequence_number += 1

        return self.order

    def _handle_cancel(self, cancel_event: Cancel) -> str:
        return cancel_event.id
