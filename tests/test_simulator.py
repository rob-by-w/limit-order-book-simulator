import pytest

from orderbook.events import New, Cancel
from orderbook.simulator import Simulator, SimulationResult, RejectedEvent, BusinessRejectionCode
from orderbook.order import Side, Trade


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


def test_cancel_resting_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, Cancel("ORD_0001", 2))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == []
    assert simulator_result.final_book_state == {Side.BID: [], Side.ASK: []}


def test_cancel_unknown_order(simulator):
    events = [
        (2, Cancel("ORD_0001", 2))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == [RejectedEvent(2, BusinessRejectionCode.UNKNOWN_ORDER_ID)]
    assert simulator_result.final_book_state == {Side.BID: [], Side.ASK: []}


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
