import pytest

from orderbook.events import New, Cancel, RejectionCode, Rejection
from orderbook.simulator import Simulator, SimulationResult, RejectedEvent, BusinessRejectionCode
from orderbook.order import Side, Trade

UNEXPECTED_EVENT_TYPE_ERROR_MSG = "Unexpected event type: "


@pytest.fixture
def simulator():
    return Simulator()


def test_add_new_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == []
    assert simulator_result.final_book_state == {Side.BID: [(95, 15)], Side.ASK: []}


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 98, 6, 2))
      ], [], [], {Side.BID: [(95, 15)], Side.ASK: [(98, 6)]}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 97, 4, 2))
      ], [], [], {Side.BID: [(97, 4)], Side.ASK: [(100, 12)]}),
])
def test_no_trades(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 6, 2))
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)], [], {Side.BID: [(95, 9)], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 18, 2))
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [], {Side.BID: [], Side.ASK: [(94, 3)]}),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 15, 2))
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 100, 4, 2))
      ], [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 4, 2)], [], {Side.BID: [], Side.ASK: [(100, 8)]}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 13, 2))
      ], [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)], [], {Side.BID: [(101, 1)], Side.ASK: []}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 102, 12, 2))
      ], [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)], [], {Side.BID: [], Side.ASK: []})
])
def test_single_trade(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 4))
     ], [
         Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
         Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 4)
     ], [], {Side.BID: [(95, 4), (94, 3)], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 15, 4))
     ], [
         Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
         Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4),
         Trade("TRD_0003", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 4)
     ], [], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 20, 4))
     ], [
         Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
         Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4),
         Trade("TRD_0003", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 4)
     ], [], {Side.BID: [], Side.ASK: [(94, 5)]}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 92, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 20, 4))
     ], [
         Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
         Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4)
     ], [], {Side.BID: [(92, 3)], Side.ASK: [(94, 8)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 4, 4))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
         Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 1, 4)
     ], [], {Side.BID: [], Side.ASK: [(105, 4), (106, 6)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 108, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 10, 4))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
         Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4)
     ], [], {Side.BID: [(106, 2)], Side.ASK: [(108, 6)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 10, 4))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
         Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4),
         Trade("TRD_0003", "ORD_0004", "ORD_0003", "ORD_0004", 106, 2, 4)
     ], [], {Side.BID: [], Side.ASK: [(106, 4)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 20, 4))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
         Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4),
         Trade("TRD_0003", "ORD_0004", "ORD_0003", "ORD_0004", 106, 6, 4)
     ], [], {Side.BID: [(106, 6)], Side.ASK: []}),

])
def test_multiple_trades(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


def test_cancel_resting_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, Cancel("ORD_0001", 2))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == []
    assert simulator_result.final_book_state == {Side.BID: [], Side.ASK: []}


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, Cancel("ORD_0001", 2))
      ], [], [RejectedEvent(2, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, Cancel("ORD_0003", 4)),
      ], [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [(95, 15)], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.ASK, 105, 9, 1)),
      (3, Cancel("ORD_0003", 4)),
      ], [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: [(105, 9)]}),
])
def test_cancel_unknown_order(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 6, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)], [], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 18, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5))
     ], [
         Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
         Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
     ], [], {Side.BID: [(94, 2)], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0002", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5))
     ], [
         Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 5),
         Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 5)
     ], [], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 107, 7, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 7, 2)], [], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 107, 15, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)], [], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 4, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 8, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 108, 6, 5))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 4, 5),
         Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 2, 5),
     ], [], {Side.BID: [], Side.ASK: [(106, 6)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 4, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 8, 3)),
         (5, Cancel("ORD_0002", 4)),
         (6, New("ORD_0004", Side.BID, 108, 15, 5))
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 12, 5),
         Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 3, 5),
     ], [], {Side.BID: [], Side.ASK: [(106, 5)]})
])
def test_cancel_after_partial_fill(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 15, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)],
     [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 17, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)],
     [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: [(94, 2)]}),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 14, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)],
     [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [(106, 2)], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 12, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)],
     [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
])
def test_cancel_on_filled_orders(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 9, 2)),
      (4, Cancel("ORD_0001", 4)),
      (5, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 9, 2)],
     [RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
     ], [
         Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
         Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
     ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [(94, 2)], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
         (8, New("ORD_0005", Side.BID, 92, 8, 8)),
         (9, Cancel("ORD_0001", 9)),
     ], [
         Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
         Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
     ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID),
         RejectedEvent(9, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [(94, 2), (92, 8)], Side.ASK: []}),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 7, 2)),
      (4, Cancel("ORD_0001", 4)),
      (5, Cancel("ORD_0001", 4)),
      ], [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 7, 2)],
     [RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 7, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 5, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 107, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 7, 5),
         Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 1, 5)
     ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: [(106, 4)]}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 7, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 5, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 107, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
         (8, New("ORD_0005", Side.ASK, 106, 4, 8)),
         (9, Cancel("ORD_0001", 9)),
     ], [
         Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 7, 5),
         Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 1, 5)
     ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID),
         RejectedEvent(9, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [], Side.ASK: [(106, 8)]}),
])
def test_double_cancel(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([(2, Rejection(RejectionCode.MISSING_ORDER_ID))], [], [RejectedEvent(2, RejectionCode.MISSING_ORDER_ID)],
     {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, Rejection(RejectionCode.INVALID_PRICE))
     ], [], [RejectedEvent(3, RejectionCode.INVALID_PRICE)],
     {Side.BID: [], Side.ASK: [(105, 12)]})
])
def test_rejection_parse_time(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize("events, trades, rejections, final_book_state", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0001", Side.BID, 95, 7, 2)),
     ], [], [RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)], {Side.BID: [(95, 5)], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0001", Side.BID, 95, 7, 2)),
         (4, New("ORD_0002", Side.BID, 95, 7, 3))
     ], [], [RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)], {Side.BID: [(95, 12)], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0001", 2)),
         (4, New("ORD_0001", Side.BID, 94, 3, 3))
     ], [], [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0003", 2)),
         (4, New("ORD_0002", Side.BID, 95, 7, 3)),
         (5, New("ORD_0003", Side.BID, 94, 3, 4))
     ], [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], {Side.BID: [(95, 12), (94, 3)], Side.ASK: []}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 13, 2)),
      (4, New("ORD_0003", Side.ASK, 100, 12, 3))
      ], [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)],
     [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)], {Side.BID: [(101, 1)], Side.ASK: []}),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 15, 2)),
      (4, New("ORD_0003", Side.ASK, 100, 12, 3)),
      (5, New("ORD_0005", Side.ASK, 99, 3, 5))
      ], [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2),
          Trade("TRD_0002", "ORD_0004", "ORD_0005", "ORD_0005", 101, 3, 5)],
     [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)], {Side.BID: [], Side.ASK: []}),
])
def test_rejection_duplicate_order_id(simulator, events, trades, rejections, final_book_state):
    simulator_result = simulator.run(events)

    assert simulator_result.trades == trades
    assert simulator_result.rejections == rejections
    assert simulator_result.final_book_state == final_book_state


@pytest.mark.parametrize(
    "events_run_1, simulation_result_1, events_run_2, simulation_result_2",
    [
        ([
             (2, New("ORD_0001", Side.BID, 95, 5, 1)),
             (3, New("ORD_0001", Side.BID, 95, 7, 2)),
         ], SimulationResult(
            trades=[],
            rejections=[RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
            final_book_state={Side.BID: [(95, 5)], Side.ASK: []}),
         [
             (2, New("ORD_0001", Side.BID, 101, 15, 5)),
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                final_book_state={Side.BID: [(95, 5)], Side.ASK: []}),
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 5, 1)),
             (3, Cancel("ORD_0001", 2)),
         ], SimulationResult(
            trades=[],
            rejections=[],
            final_book_state={Side.BID: [], Side.ASK: []}),
         [
             (2, New("ORD_0001", Side.BID, 101, 15, 5)),
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                final_book_state={Side.BID: [], Side.ASK: []}),
        ),
        ([
             (2, New("ORD_0003", Side.ASK, 100, 12, 1)),
             (3, New("ORD_0004", Side.BID, 101, 15, 2)),

         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)],
            rejections=[],
            final_book_state={Side.BID: [(101, 3)], Side.ASK: []}),
         [
             (4, New("ORD_0003", Side.ASK, 100, 12, 3)),
             (5, New("ORD_0005", Side.ASK, 99, 3, 5))
         ], SimulationResult(
                trades=[Trade("TRD_0002", "ORD_0004", "ORD_0005", "ORD_0005", 101, 3, 5)],
                rejections=[RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                final_book_state={Side.BID: [], Side.ASK: []}
            )
        )
    ])
def test_rejection_duplicate_order_id_multiple_run(simulator, events_run_1, simulation_result_1, events_run_2,
                                                   simulation_result_2):
    simulator_result = simulator.run(events_run_1)
    assert simulator_result == simulation_result_1

    simulator_result = simulator.run(events_run_2)
    assert simulator_result == simulation_result_2


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, Rejection(RejectionCode.MISSING_ORDER_ID)),
         (3, New("ORD_0003", Side.ASK, 100, 12, 1)),
         (4, New("ORD_0003", Side.ASK, 100, 12, 1))
     ], SimulationResult(
        trades=[],
        rejections=[RejectedEvent(2, RejectionCode.MISSING_ORDER_ID),
                    RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
        final_book_state={Side.BID: [], Side.ASK: [(100, 12)]})
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 5, 1)),
         (3, Rejection(RejectionCode.INVALID_SIDE)),
         (4, New("ORD_0002", Side.BID, 106, 7, 3)),
         (5, Cancel("ORD_0001", 4))
     ], SimulationResult(
        trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 5, 3)],
        rejections=[RejectedEvent(3, RejectionCode.INVALID_SIDE),
                    RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        final_book_state={Side.BID: [(106, 2)], Side.ASK: []})
    ),
    ([
         (2, New("ORD_0001", Side.BID, 95, 6, 1)),
         (3, New("ORD_0001", Side.ASK, 104, 5, 2)),
         (4, New("ORD_0002", Side.ASK, 94, 9, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, Rejection(RejectionCode.MISSING_TIMESTAMP))
     ], SimulationResult(
        trades=[Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 3)],
        rejections=[RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID),
                    RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID),
                    RejectedEvent(6, RejectionCode.MISSING_TIMESTAMP)],
        final_book_state={Side.BID: [], Side.ASK: [(94, 3)]})
    ),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 15, 2)),
      (4, Rejection(RejectionCode.UNSUPPORTED_EVENT_TYPE)),
      (5, New("ORD_0003", Side.ASK, 100, 12, 3)),
      (6, New("ORD_0005", Side.ASK, 99, 3, 5)),
      (7, Rejection(RejectionCode.MISSING_QUANTITY))
      ],
     SimulationResult(
         trades=[Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2),
                 Trade("TRD_0002", "ORD_0004", "ORD_0005", "ORD_0005", 101, 3, 5)],
         rejections=[RejectedEvent(4, RejectionCode.UNSUPPORTED_EVENT_TYPE),
                     RejectedEvent(5, BusinessRejectionCode.DUPLICATE_ORDER_ID),
                     RejectedEvent(7, RejectionCode.MISSING_QUANTITY)],
         final_book_state={Side.BID: [], Side.ASK: []}),
     )
])
def test_rejection_parse_time_and_business_rejections(simulator, events, simulation_result):
    simulator_result = simulator.run(events)
    assert simulator_result == simulation_result


def test_run_empty_events(simulator):
    simulator_result = simulator.run([])
    assert simulator_result == SimulationResult(trades=[], rejections=[], final_book_state={Side.BID: [], Side.ASK: []})


@pytest.mark.parametrize(
    "events_run_1, simulation_result_1, events_run_2, simulation_result_2",
    [
        ([], SimulationResult(
            trades=[],
            rejections=[],
            final_book_state={Side.BID: [], Side.ASK: []}),
         [], SimulationResult(
                trades=[],
                rejections=[],
                final_book_state={Side.BID: [], Side.ASK: []}),
         ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1)),
             (3, New("ORD_0002", Side.ASK, 94, 6, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)],
            rejections=[],
            final_book_state={Side.BID: [(95, 9)], Side.ASK: []}),
         [
             (2, New("ORD_0003", Side.ASK, 94, 10, 3))
         ], SimulationResult(
                trades=[Trade("TRD_0002", "ORD_0001", "ORD_0003", "ORD_0003", 95, 9, 3)],
                rejections=[],
                final_book_state={Side.BID: [], Side.ASK: [(94, 1)]}),
        ),
        ([
             (2, New("ORD_0001", Side.ASK, 101, 8, 1)),
             (3, New("ORD_0002", Side.BID, 101, 10, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 101, 8, 2)],
            rejections=[],
            final_book_state={Side.BID: [(101, 2)], Side.ASK: []}),
         [
             (2, New("ORD_0003", Side.ASK, 103, 7, 3))
         ], SimulationResult(
                trades=[],
                rejections=[],
                final_book_state={Side.BID: [(101, 2)], Side.ASK: [(103, 7)]}),
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1)),
             (3, New("ORD_0002", Side.ASK, 94, 6, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)],
            rejections=[],
            final_book_state={Side.BID: [(95, 9)], Side.ASK: []}),
         [], SimulationResult(
                trades=[],
                rejections=[],
                final_book_state={Side.BID: [(95, 9)], Side.ASK: []}),
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1))
         ], SimulationResult(
            trades=[],
            rejections=[],
            final_book_state={Side.BID: [(95, 15)], Side.ASK: []}),
         [
             (2, New("ORD_0001", Side.BID, 96, 7, 3))
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                final_book_state={Side.BID: [(95, 15)], Side.ASK: []}),
        ),
        ([
             (2, New("ORD_0001", Side.ASK, 106, 12, 1))
         ], SimulationResult(
            trades=[],
            rejections=[],
            final_book_state={Side.BID: [], Side.ASK: [(106, 12)]}),
         [
             (2, New("ORD_0001", Side.BID, 108, 7, 2)),
             (3, New("ORD_0002", Side.BID, 108, 7, 2))
         ], SimulationResult(
                trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 106, 7, 2)],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                final_book_state={Side.BID: [], Side.ASK: [(106, 5)]}),
        ),
    ])
def test_multiple_runs(simulator, events_run_1, simulation_result_1, events_run_2, simulation_result_2):
    simulator_result_1 = simulator.run(events_run_1)
    assert simulator_result_1 == simulation_result_1

    simulator_result_2 = simulator.run(events_run_2)
    assert simulator_result_1 == simulation_result_1
    assert simulator_result_2 == simulation_result_2


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, Rejection(RejectionCode.MISSING_ORDER_ID)),
         (3, New("ORD_0001", Side.ASK, 100, 12, 1)),
         (4, New("ORD_0002", Side.BID, 100, 12, 1))
     ], SimulationResult(
        trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 100, 12, 1)],
        rejections=[RejectedEvent(2, RejectionCode.MISSING_ORDER_ID)],
        final_book_state={Side.BID: [], Side.ASK: []})
    ), ([
            (2, New("ORD_0001", Side.BID, 95, 5, 1)),
            (3, New("ORD_0002", Side.BID, 95, 7, 2)),
            (4, New("ORD_0003", Side.BID, 94, 3, 3)),
            (5, New("ORD_0004", Side.ASK, 94, 8, 4))
        ], SimulationResult(
        trades=[
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 4)
        ],
        rejections=[],
        final_book_state={Side.BID: [(95, 4), (94, 3)], Side.ASK: []})
    ),
])
def test_two_simulators_give_same_result(events, simulation_result):
    simulator_1 = Simulator()
    simulator_2 = Simulator()

    simulator_result_1 = simulator_1.run(events)
    assert simulator_result_1 == simulation_result

    simulator_result_2 = simulator_2.run(events)
    assert simulator_result_2 == simulation_result


@pytest.mark.parametrize("events", [
    [
        (2, "Unknown Type")
    ], [
        (2, New("ORD_0001", Side.BID, 95, 5, 1)),
        (3, "Garbage"),
        (4, New("ORD_0003", Side.BID, 94, 3, 3)),
        (5, New("ORD_0004", Side.ASK, 94, 8, 4))
    ]
])
def test_run_type_error(simulator, events):
    with pytest.raises(TypeError, match=UNEXPECTED_EVENT_TYPE_ERROR_MSG + str(events)):
        simulator.run(events)


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.BID, 98, 5, 2)),
         (4, New("ORD_0003", Side.BID, 98, 7, 3)),
         (5, New("ORD_0004", Side.BID, 99, 6, 4)),
         (6, New("ORD_0005", Side.BID, 99, 1, 5)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [(99, 7), (98, 15)], Side.ASK: []})
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 98, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 98, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 98, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 99, 6, 4)),
         (6, New("ORD_0005", Side.ASK, 99, 1, 5)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [], Side.ASK: [(98, 15), (99, 7)]})
    ),
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.BID, 98, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 103, 10, 3)),
         (5, New("ORD_0004", Side.BID, 98, 7, 4)),
         (6, New("ORD_0005", Side.BID, 99, 6, 5)),
         (7, New("ORD_0006", Side.ASK, 105, 7, 6)),
         (8, New("ORD_0007", Side.ASK, 105, 5, 7)),
         (9, New("ORD_0008", Side.BID, 99, 1, 8)),
         (10, New("ORD_0009", Side.ASK, 103, 4, 9)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [(99, 7), (98, 15)], Side.ASK: [(103, 14), (105, 12)]})
    ),
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.BID, 98, 5, 2)),
         (4, New("ORD_0003", Side.BID, 98, 7, 3)),
         (5, New("ORD_0004", Side.BID, 99, 6, 4)),
         (6, New("ORD_0005", Side.BID, 99, 1, 5)),
         (7, New("ORD_0006", Side.ASK, 99, 2, 6)),
     ], SimulationResult(
        trades=[Trade("TRD_0001", "ORD_0004", "ORD_0006", "ORD_0006", 99, 2, 6)],
        rejections=[],
        final_book_state={Side.BID: [(99, 5), (98, 15)], Side.ASK: []})
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 98, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 98, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 98, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 99, 6, 4)),
         (6, New("ORD_0005", Side.ASK, 99, 1, 5)),
         (7, New("ORD_0006", Side.BID, 98, 2, 6)),
     ], SimulationResult(
        trades=[Trade("TRD_0001", "ORD_0006", "ORD_0001", "ORD_0006", 98, 2, 6)],
        rejections=[],
        final_book_state={Side.BID: [], Side.ASK: [(98, 13), (99, 7)]})
    ),
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.BID, 98, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 103, 10, 3)),
         (5, New("ORD_0004", Side.BID, 98, 7, 4)),
         (6, New("ORD_0005", Side.BID, 99, 6, 5)),
         (7, New("ORD_0006", Side.ASK, 105, 7, 6)),
         (8, New("ORD_0007", Side.ASK, 105, 5, 7)),
         (9, New("ORD_0008", Side.BID, 99, 1, 8)),
         (10, New("ORD_0009", Side.ASK, 103, 4, 9)),
         (11, New("ORD_0010", Side.ASK, 99, 5, 10)),
         (12, New("ORD_0011", Side.BID, 103, 4, 11)),
     ], SimulationResult(
        trades=[
            Trade("TRD_0001", "ORD_0005", "ORD_0010", "ORD_0010", 99, 5, 10),
            Trade("TRD_0002", "ORD_0011", "ORD_0003", "ORD_0011", 103, 4, 11)
        ],
        rejections=[],
        final_book_state={Side.BID: [(99, 2), (98, 15)], Side.ASK: [(103, 10), (105, 12)]})
    ),
])
def test_simulator_result_depth_aggregation(simulator, events, simulation_result):
    simulator_result = simulator.run(events)
    assert simulator_result == simulation_result


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.BID, 100, 5, 2)),
         (4, New("ORD_0003", Side.BID, 95, 7, 3)),
         (5, New("ORD_0004", Side.BID, 99, 6, 4)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [(100, 5), (99, 6), (98, 3), (95, 7)], Side.ASK: []})
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 98, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 100, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 96, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 99, 6, 4)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [], Side.ASK: [(96, 7), (98, 3), (99, 6), (100, 5)]})
    ),
    ([
         (2, New("ORD_0001", Side.BID, 98, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 108, 18, 2)),
         (4, New("ORD_0003", Side.BID, 100, 5, 3)),
         (5, New("ORD_0005", Side.BID, 99, 6, 5)),
         (6, New("ORD_0006", Side.ASK, 105, 4, 6)),
         (7, New("ORD_0009", Side.ASK, 107, 11, 9)),
         (8, New("ORD_0010", Side.ASK, 109, 3, 10)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        final_book_state={Side.BID: [(100, 5), (99, 6), (98, 3)],
                          Side.ASK: [(105, 4), (107, 11), (108, 18), (109, 3)]})
    ),
])
def test_simulator_result_depth_order(simulator, events, simulation_result):
    simulator_result = simulator.run(events)
    assert simulator_result == simulation_result
