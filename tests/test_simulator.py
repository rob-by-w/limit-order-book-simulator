import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from orderbook.events import New, Cancel, RejectionCode, Rejection, read_order_flow_csv
from orderbook.simulator import Simulator, SimulationResult, RejectedEvent, BusinessRejectionCode, BookSnapshot
from orderbook.order import Side, Trade, Level

UNEXPECTED_EVENT_TYPE_ERROR_MSG = "Unexpected event type: "


@pytest.fixture
def booksnapshot_sample():
    return BookSnapshot(
        (Level(101, 2), Level(99, 6), Level(97, 7), Level(96, 10), Level(95, 3), Level(94, 14), Level(92, 5)),
        (Level(102, 8), Level(104, 7), Level(105, 13), Level(107, 6), Level(109, 12), Level(111, 15), Level(113, 7))
    )


@pytest.fixture
def simulator():
    return Simulator()


def test_booksnapshot_is_immutable(booksnapshot_sample):
    with pytest.raises(FrozenInstanceError):
        booksnapshot_sample.bids = (Level(96, 10), Level(100, 3))


def test_booksnapshot_level_is_immutable(booksnapshot_sample):
    with pytest.raises(FrozenInstanceError):
        booksnapshot_sample.bids[0].quantity = 8


def test_booksnapshot_bids_is_tuple(booksnapshot_sample):
    assert type(booksnapshot_sample.bids) is tuple


def test_booksnapshot_asks_is_tuple(booksnapshot_sample):
    assert type(booksnapshot_sample.asks) is tuple


@pytest.mark.parametrize("booksnapshot_1, booksnapshot_2", [
    (BookSnapshot((), ()), BookSnapshot((), ())),
    (BookSnapshot((Level(95, 15),), (Level(98, 6),)), BookSnapshot((Level(95, 15),), (Level(98, 6),)))
])
def test_same_booksnapshots_are_equal(booksnapshot_1, booksnapshot_2):
    assert booksnapshot_1 == booksnapshot_2


def test_booksnapshot_immutability_after_a_run(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1))
    ]

    simulator_result = simulator.run(events)

    with pytest.raises(FrozenInstanceError):
        simulator_result.book_state.bids = (Level(96, 10), Level(100, 3))


def test_booksnapshot_level_immutability_after_a_run(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1))
    ]

    simulator_result = simulator.run(events)

    with pytest.raises(FrozenInstanceError):
        simulator_result.book_state.bids[0].price = 105


def test_booksnapshot_bids_and_ask_are_tuples_after_a_run(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, New("ORD_0002", Side.ASK, 105, 10, 2))
    ]

    simulator_result = simulator.run(events)

    assert type(simulator_result.book_state.bids) is tuple
    assert type(simulator_result.book_state.asks) is tuple


def test_add_new_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == []
    assert simulator_result.book_state == BookSnapshot((Level(95, 15),), ())


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 98, 6, 2))
      ], SimulationResult([], [], BookSnapshot((Level(95, 15),), (Level(98, 6),)))
     ),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 97, 4, 2))
      ], SimulationResult([], [], BookSnapshot((Level(97, 4),), (Level(100, 12),)))
     ),
])
def test_no_trades(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 6, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)], [],
                          BookSnapshot((Level(95, 9),), ())
                          )),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 18, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [],
                          BookSnapshot((), (Level(94, 3),))
                          )),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 15, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [],
                          BookSnapshot((), ())
                          )),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 100, 4, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 4, 2)], [],
                          BookSnapshot((), (Level(100, 8),))
                          )),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 13, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)], [],
                          BookSnapshot((Level(101, 1),), ())
                          )),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 102, 12, 2))
      ], SimulationResult([Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)], [],
                          BookSnapshot((), ())
                          )),
])
def test_single_trade(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 4)
        ], [], BookSnapshot((Level(95, 4), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 15, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4),
            Trade("TRD_0003", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 4)
        ], [], BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 20, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4),
            Trade("TRD_0003", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 4)
        ], [], BookSnapshot((), (Level(94, 5),))
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 92, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 20, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 4)
        ], [], BookSnapshot((Level(92, 3),), (Level(94, 8),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 4, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 1, 4)
        ], [], BookSnapshot((), (Level(105, 4), Level(106, 6)))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 108, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 10, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4)
        ], [], BookSnapshot((Level(106, 2),), (Level(108, 6),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 10, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4),
            Trade("TRD_0003", "ORD_0004", "ORD_0003", "ORD_0004", 106, 2, 4)
        ], [], BookSnapshot((), (Level(106, 4),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 20, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 5, 4),
            Trade("TRD_0003", "ORD_0004", "ORD_0003", "ORD_0004", 106, 6, 4)
        ], [], BookSnapshot((Level(106, 6),), ())
    )),
])
def test_multiple_trades(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


def test_cancel_resting_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, Cancel("ORD_0001", 2))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == []
    assert simulator_result.rejections == []
    assert simulator_result.book_state == BookSnapshot((), ())


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, Cancel("ORD_0001", 2))
      ], SimulationResult(
        [], [RejectedEvent(2, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((), ())
    )),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, Cancel("ORD_0003", 4)),
      ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((Level(95, 15),), ())
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 9, 1)),
      (3, Cancel("ORD_0003", 4)),
      ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((), (Level(105, 9),))
    )),
])
def test_cancel_unknown_order(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 6, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)], [], BookSnapshot((), ())
    )),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 18, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)], [], BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
            Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
        ], [], BookSnapshot((Level(94, 2),), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0002", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 5),
            Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 3, 5)
        ], [], BookSnapshot((), ())
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 107, 7, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 7, 2)], [], BookSnapshot((), ())
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 107, 15, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)], [], BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 4, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 8, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 108, 6, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 4, 5),
            Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 2, 5),
        ], [], BookSnapshot((), (Level(106, 6),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 4, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 8, 3)),
         (5, Cancel("ORD_0002", 4)),
         (6, New("ORD_0004", Side.BID, 108, 15, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 12, 5),
            Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 3, 5),
        ], [], BookSnapshot((), (Level(106, 5),))
    ))
])
def test_cancel_after_partial_fill(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 15, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)],
        [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), ())
    )),
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 17, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 15, 2)],
        [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((), (Level(94, 2),))
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 14, 2)),
      (4, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)],
        [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((Level(106, 2),), ())
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 12, 2)),
      (4, Cancel("ORD_0002", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 12, 2)],
        [RejectedEvent(4, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((), ())
    )),
])
def test_cancel_on_filled_orders(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, New("ORD_0001", Side.BID, 95, 15, 1)),
      (3, New("ORD_0002", Side.ASK, 94, 9, 2)),
      (4, Cancel("ORD_0001", 4)),
      (5, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 9, 2)],
        [RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
            Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
        ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((Level(94, 2),), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
         (8, New("ORD_0005", Side.BID, 92, 8, 8)),
         (9, Cancel("ORD_0001", 9)),
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0002", "ORD_0004", "ORD_0004", 95, 7, 5),
            Trade("TRD_0002", "ORD_0003", "ORD_0004", "ORD_0004", 94, 1, 5)
        ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID),
            RejectedEvent(9, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((Level(94, 2), Level(92, 8)), ())
    )),
    ([(2, New("ORD_0001", Side.ASK, 105, 12, 1)),
      (3, New("ORD_0002", Side.BID, 106, 7, 2)),
      (4, Cancel("ORD_0001", 4)),
      (5, Cancel("ORD_0001", 4)),
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 105, 7, 2)],
        [RejectedEvent(5, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 7, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 5, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 107, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 7, 5),
            Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 1, 5)
        ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), (Level(106, 4),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 7, 2)),
         (4, New("ORD_0003", Side.ASK, 106, 5, 3)),
         (5, Cancel("ORD_0001", 4)),
         (6, New("ORD_0004", Side.BID, 107, 8, 5)),
         (7, Cancel("ORD_0001", 7)),
         (8, New("ORD_0005", Side.ASK, 106, 4, 8)),
         (9, Cancel("ORD_0001", 9)),
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0002", "ORD_0004", 105, 7, 5),
            Trade("TRD_0002", "ORD_0004", "ORD_0003", "ORD_0004", 106, 1, 5)
        ], [RejectedEvent(7, BusinessRejectionCode.UNKNOWN_ORDER_ID),
            RejectedEvent(9, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), (Level(106, 8),))
    )),
])
def test_double_cancel(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([(2, Rejection(RejectionCode.MISSING_ORDER_ID))],
     SimulationResult([], [RejectedEvent(2, RejectionCode.MISSING_ORDER_ID)],
                      BookSnapshot((), ()))),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 12, 1)),
         (3, Rejection(RejectionCode.INVALID_PRICE))
     ], SimulationResult([], [RejectedEvent(3, RejectionCode.INVALID_PRICE)],
                         BookSnapshot((), (Level(105, 12),))))
])
def test_rejection_parse_time(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0001", Side.BID, 95, 7, 2)),
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)], BookSnapshot((Level(95, 5),), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0001", Side.BID, 95, 7, 2)),
         (4, New("ORD_0002", Side.BID, 95, 7, 3))
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)], BookSnapshot((Level(95, 12),), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0001", 2)),
         (4, New("ORD_0001", Side.BID, 94, 3, 3))
     ], SimulationResult(
        [], [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)], BookSnapshot((), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0003", 2)),
         (4, New("ORD_0002", Side.BID, 95, 7, 3)),
         (5, New("ORD_0003", Side.BID, 94, 3, 4))
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)], BookSnapshot((Level(95, 12), Level(94, 3)), ())
    )),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 13, 2)),
      (4, New("ORD_0003", Side.ASK, 100, 12, 3))
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)],
        [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
        BookSnapshot((Level(101, 1),), ())
    )),
    ([(2, New("ORD_0003", Side.ASK, 100, 12, 1)),
      (3, New("ORD_0004", Side.BID, 101, 15, 2)),
      (4, New("ORD_0003", Side.ASK, 100, 12, 3)),
      (5, New("ORD_0005", Side.ASK, 99, 3, 5))
      ], SimulationResult(
        [Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2),
         Trade("TRD_0002", "ORD_0004", "ORD_0005", "ORD_0005", 101, 3, 5)],
        [RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
        BookSnapshot((), ())
    )),
])
def test_rejection_duplicate_order_id(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize(
    "events_run_1, simulation_result_1, events_run_2, simulation_result_2",
    [
        ([
             (2, New("ORD_0001", Side.BID, 95, 5, 1)),
             (3, New("ORD_0001", Side.BID, 95, 7, 2)),
         ], SimulationResult(
            trades=[],
            rejections=[RejectedEvent(3, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
            book_state=BookSnapshot((Level(95, 5),), ())),
         [
             (2, New("ORD_0001", Side.BID, 101, 15, 5)),
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                book_state=BookSnapshot((Level(95, 5),), ())),
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 5, 1)),
             (3, Cancel("ORD_0001", 2)),
         ], SimulationResult(
            trades=[],
            rejections=[],
            book_state=BookSnapshot((), ())),
         [
             (2, New("ORD_0001", Side.BID, 101, 15, 5)),
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                book_state=BookSnapshot((), ())),
        ),
        ([
             (2, New("ORD_0003", Side.ASK, 100, 12, 1)),
             (3, New("ORD_0004", Side.BID, 101, 15, 2)),

         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0004", "ORD_0003", "ORD_0004", 100, 12, 2)],
            rejections=[],
            book_state=BookSnapshot((Level(101, 3),), ())),
         [
             (4, New("ORD_0003", Side.ASK, 100, 12, 3)),
             (5, New("ORD_0005", Side.ASK, 99, 3, 5))
         ], SimulationResult(
                trades=[Trade("TRD_0002", "ORD_0004", "ORD_0005", "ORD_0005", 101, 3, 5)],
                rejections=[RejectedEvent(4, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                book_state=BookSnapshot((), ())
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
        book_state=BookSnapshot((), (Level(100, 12),)))
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
        book_state=BookSnapshot((Level(106, 2),), ()))
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
        book_state=BookSnapshot((), (Level(94, 3),)))
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
         book_state=BookSnapshot((), ())),
     )
])
def test_rejection_parse_time_and_business_rejections(simulator, events, simulation_result):
    simulator_result = simulator.run(events)
    assert simulator_result == simulation_result


def test_run_empty_events(simulator):
    simulator_result = simulator.run([])
    assert simulator_result == SimulationResult(trades=[], rejections=[], book_state=BookSnapshot((), ()))


@pytest.mark.parametrize(
    "events_run_1, simulation_result_1, events_run_2, simulation_result_2",
    [
        ([], SimulationResult(
            trades=[],
            rejections=[],
            book_state=BookSnapshot((), ())),
         [], SimulationResult(
                trades=[],
                rejections=[],
                book_state=BookSnapshot((), ())),
         ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1)),
             (3, New("ORD_0002", Side.ASK, 94, 6, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)],
            rejections=[],
            book_state=BookSnapshot((Level(95, 9),), ())),
         [
             (2, New("ORD_0003", Side.ASK, 94, 10, 3))
         ], SimulationResult(
                trades=[Trade("TRD_0002", "ORD_0001", "ORD_0003", "ORD_0003", 95, 9, 3)],
                rejections=[],
                book_state=BookSnapshot((), (Level(94, 1),))),
        ),
        ([
             (2, New("ORD_0001", Side.ASK, 101, 8, 1)),
             (3, New("ORD_0002", Side.BID, 101, 10, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 101, 8, 2)],
            rejections=[],
            book_state=BookSnapshot((Level(101, 2),), ())),
         [
             (2, New("ORD_0003", Side.ASK, 103, 7, 3))
         ], SimulationResult(
                trades=[],
                rejections=[],
                book_state=BookSnapshot((Level(101, 2),), (Level(103, 7),)))
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1)),
             (3, New("ORD_0002", Side.ASK, 94, 6, 2))
         ], SimulationResult(
            trades=[Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)],
            rejections=[],
            book_state=BookSnapshot((Level(95, 9),), ())),
         [], SimulationResult(
                trades=[],
                rejections=[],
                book_state=BookSnapshot((Level(95, 9),), ())),
        ),
        ([
             (2, New("ORD_0001", Side.BID, 95, 15, 1))
         ], SimulationResult(
            trades=[],
            rejections=[],
            book_state=BookSnapshot((Level(95, 15),), ())),
         [
             (2, New("ORD_0001", Side.BID, 96, 7, 3))
         ], SimulationResult(
                trades=[],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                book_state=BookSnapshot((Level(95, 15),), ())),
        ),
        ([
             (2, New("ORD_0001", Side.ASK, 106, 12, 1))
         ], SimulationResult(
            trades=[],
            rejections=[],
            book_state=BookSnapshot((), (Level(106, 12),))),
         [
             (2, New("ORD_0001", Side.BID, 108, 7, 2)),
             (3, New("ORD_0002", Side.BID, 108, 7, 2))
         ], SimulationResult(
                trades=[Trade("TRD_0001", "ORD_0002", "ORD_0001", "ORD_0002", 106, 7, 2)],
                rejections=[RejectedEvent(2, BusinessRejectionCode.DUPLICATE_ORDER_ID)],
                book_state=BookSnapshot((), (Level(106, 5),))),
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
        book_state=BookSnapshot((), ()))
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
        book_state=BookSnapshot((Level(95, 4), Level(94, 3)), ()))
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
        book_state=BookSnapshot((Level(99, 7), Level(98, 15)), ()))
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
        book_state=BookSnapshot((), (Level(98, 15), Level(99, 7))))
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
        book_state=BookSnapshot((Level(99, 7), Level(98, 15)), (Level(103, 14), Level(105, 12))))
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
        book_state=BookSnapshot((Level(99, 5), Level(98, 15)), ()))
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
        book_state=BookSnapshot((), (Level(98, 13), Level(99, 7))))
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
        book_state=BookSnapshot((Level(99, 2), Level(98, 15)), (Level(103, 10), Level(105, 12))))
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
        book_state=BookSnapshot((Level(100, 5), Level(99, 6), Level(98, 3), Level(95, 7)), ()))
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 98, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 100, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 96, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 99, 6, 4)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot((), (Level(96, 7), Level(98, 3), Level(99, 6), Level(100, 5))))
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
        book_state=BookSnapshot(
            (Level(100, 5), Level(99, 6), Level(98, 3)),
            (Level(105, 4), Level(107, 11), Level(108, 18), Level(109, 3))
        ))
    ),
])
def test_simulator_result_depth_order(simulator, events, simulation_result):
    simulator_result = simulator.run(events)
    assert simulator_result == simulation_result


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 3, 1)),
         (3, New("ORD_0002", Side.BID, 92, 5, 2)),
         (4, New("ORD_0003", Side.BID, 97, 7, 3)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (Level(97, 7), Level(95, 3), Level(92, 5)),
            ()
        ))
    ),
    ([
         (2, New("ORD_0001", Side.BID, 95, 3, 1)),
         (3, New("ORD_0002", Side.BID, 92, 5, 2)),
         (4, New("ORD_0003", Side.BID, 97, 7, 3)),
         (5, New("ORD_0004", Side.BID, 99, 6, 4)),
         (6, New("ORD_0005", Side.BID, 101, 2, 5)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (Level(101, 2), Level(99, 6), Level(97, 7), Level(95, 3), Level(92, 5)),
            ()
        ))
    ),
    ([
         (2, New("ORD_0001", Side.BID, 95, 3, 1)),
         (3, New("ORD_0002", Side.BID, 92, 5, 2)),
         (4, New("ORD_0003", Side.BID, 97, 7, 3)),
         (5, New("ORD_0004", Side.BID, 99, 6, 4)),
         (6, New("ORD_0005", Side.BID, 101, 2, 5)),
         (7, New("ORD_0006", Side.BID, 96, 10, 6)),
         (8, New("ORD_0007", Side.BID, 94, 14, 7)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (Level(101, 2), Level(99, 6), Level(97, 7), Level(96, 10), Level(95, 3), Level(94, 14), Level(92, 5)),
            ()
        ))
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 13, 1)),
         (3, New("ORD_0002", Side.ASK, 111, 15, 2)),
         (4, New("ORD_0003", Side.ASK, 104, 7, 3)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (),
            (Level(104, 7), Level(105, 13), Level(111, 15))
        ))
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 13, 1)),
         (3, New("ORD_0002", Side.ASK, 111, 15, 2)),
         (4, New("ORD_0003", Side.ASK, 104, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 107, 6, 4)),
         (6, New("ORD_0005", Side.ASK, 102, 8, 5)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (),
            (Level(102, 8), Level(104, 7), Level(105, 13), Level(107, 6), Level(111, 15))
        ))
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 13, 1)),
         (3, New("ORD_0002", Side.ASK, 111, 15, 2)),
         (4, New("ORD_0003", Side.ASK, 104, 7, 3)),
         (5, New("ORD_0004", Side.ASK, 107, 6, 4)),
         (6, New("ORD_0005", Side.ASK, 102, 8, 5)),
         (7, New("ORD_0006", Side.ASK, 113, 7, 6)),
         (8, New("ORD_0007", Side.ASK, 109, 12, 7)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (),
            (Level(102, 8), Level(104, 7), Level(105, 13), Level(107, 6), Level(109, 12), Level(111, 15), Level(113, 7))
        ))
    ),
    ([
         (2, New("ORD_0001", Side.BID, 95, 3, 1)),
         (3, New("ORD_0002", Side.BID, 92, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 105, 13, 3)),
         (5, New("ORD_0004", Side.ASK, 104, 7, 4)),
         (6, New("ORD_0005", Side.BID, 97, 7, 5)),
         (7, New("ORD_0006", Side.BID, 99, 6, 6)),
         (8, New("ORD_0007", Side.BID, 101, 2, 7)),
         (9, New("ORD_0008", Side.ASK, 111, 15, 8)),
         (10, New("ORD_0009", Side.ASK, 113, 7, 9)),
         (11, New("ORD_0010", Side.BID, 96, 10, 10)),
         (12, New("ORD_0011", Side.ASK, 107, 6, 11)),
         (13, New("ORD_0012", Side.ASK, 102, 8, 12)),
         (14, New("ORD_0013", Side.ASK, 109, 12, 13)),
         (15, New("ORD_0014", Side.BID, 94, 14, 14)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=
        BookSnapshot(
            (Level(101, 2), Level(99, 6), Level(97, 7), Level(96, 10), Level(95, 3), Level(94, 14), Level(92, 5)),
            (Level(102, 8), Level(104, 7), Level(105, 13), Level(107, 6), Level(109, 12), Level(111, 15), Level(113, 7))
        ))
    ),
])
def test_simulator_result_depth_level(simulator, events, simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == simulation_result


@pytest.mark.parametrize("events, simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 3, 1)),
         (3, New("ORD_0002", Side.BID, 92, 5, 12)),
         (4, New("ORD_0003", Side.BID, 97, 7, 3)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (Level(97, 7), Level(95, 3), Level(92, 5)),
            ()
        ))
    ),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 13, 1)),
         (3, New("ORD_0002", Side.ASK, 111, 15, 12)),
         (4, New("ORD_0003", Side.ASK, 104, 7, 3)),
     ], SimulationResult(
        trades=[],
        rejections=[],
        book_state=BookSnapshot(
            (),
            (Level(104, 7), Level(105, 13), Level(111, 15))
        ))
    ),
])
def test_backward_timestamp_is_acceptable(simulator, events, simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 2)),
         (3, New("ORD_0002", Side.BID, 95, 7, 1)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 4)
        ], [], BookSnapshot((Level(95, 4), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (6, New("ORD_0005", Side.ASK, 93, 2, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 5),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 5),
            Trade("TRD_0003", "ORD_0002", "ORD_0005", "ORD_0005", 95, 2, 4),
        ], [], BookSnapshot((Level(95, 2), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 1)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 4)),
         (6, New("ORD_0005", Side.ASK, 93, 2, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 4),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 4),
            Trade("TRD_0003", "ORD_0002", "ORD_0005", "ORD_0005", 95, 2, 5),
        ], [], BookSnapshot((Level(95, 2), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 3)),
         (5, New("ORD_0004", Side.ASK, 94, 8, 5)),
         (6, New("ORD_0005", Side.ASK, 93, 2, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0001", "ORD_0004", "ORD_0004", 95, 5, 5),
            Trade("TRD_0002", "ORD_0002", "ORD_0004", "ORD_0004", 95, 3, 5),
            Trade("TRD_0003", "ORD_0002", "ORD_0005", "ORD_0005", 95, 2, 5),
        ], [], BookSnapshot((Level(95, 2), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 2)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 3)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 1)),
         (5, New("ORD_0004", Side.BID, 106, 4, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 1, 4)
        ], [], BookSnapshot((), (Level(105, 4), Level(106, 6)))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 108, 6, 3)),
         (5, New("ORD_0004", Side.BID, 108, 6, 6)),
         (5, New("ORD_0005", Side.BID, 109, 4, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 6),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 3, 6),
            Trade("TRD_0003", "ORD_0005", "ORD_0002", "ORD_0005", 105, 2, 4),
            Trade("TRD_0004", "ORD_0005", "ORD_0003", "ORD_0005", 108, 2, 4),
        ], [], BookSnapshot((), (Level(108, 4),))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 1)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 3)),
         (5, New("ORD_0004", Side.BID, 106, 4, 4))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 4),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 1, 4)
        ], [], BookSnapshot((), (Level(105, 4), Level(106, 6)))
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 2)),
         (4, New("ORD_0003", Side.ASK, 108, 6, 3)),
         (5, New("ORD_0004", Side.BID, 108, 6, 5)),
         (6, New("ORD_0005", Side.BID, 109, 4, 5))
     ], SimulationResult(
        [
            Trade("TRD_0001", "ORD_0004", "ORD_0001", "ORD_0004", 105, 3, 5),
            Trade("TRD_0002", "ORD_0004", "ORD_0002", "ORD_0004", 105, 3, 5),
            Trade("TRD_0003", "ORD_0005", "ORD_0002", "ORD_0005", 105, 2, 5),
            Trade("TRD_0004", "ORD_0005", "ORD_0003", "ORD_0005", 108, 2, 5),
        ], [], BookSnapshot((), (Level(108, 4),))
    )),
])
def test_trade_priority_follows_arrival_not_timestamp(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result


@pytest.mark.parametrize("events, expected_simulation_result", [
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0003", 4)),
         (4, New("ORD_0002", Side.BID, 95, 7, 5)),
         (5, New("ORD_0003", Side.BID, 94, 3, 3)),
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((Level(95, 12), Level(94, 3)), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, Cancel("ORD_0003", 4)),
         (4, New("ORD_0002", Side.BID, 95, 7, 5)),
         (5, New("ORD_0003", Side.BID, 94, 3, 3)),
         (6, Cancel("ORD_0003", 8)),
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((Level(95, 12),), ())
    )),
    ([
         (2, New("ORD_0001", Side.BID, 95, 5, 1)),
         (3, New("ORD_0002", Side.BID, 95, 7, 2)),
         (4, New("ORD_0003", Side.BID, 94, 3, 6)),
         (5, Cancel("ORD_0003", 4)),
     ], SimulationResult(
        [], [],
        BookSnapshot((Level(95, 12),), ())
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, Cancel("ORD_0002", 5)),
         (4, New("ORD_0002", Side.ASK, 105, 5, 3)),
         (5, New("ORD_0003", Side.ASK, 106, 6, 4)),
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), (Level(105, 8), Level(106, 6))),
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, Cancel("ORD_0002", 5)),
         (4, New("ORD_0002", Side.ASK, 105, 5, 3)),
         (5, New("ORD_0003", Side.ASK, 106, 6, 4)),
         (6, Cancel("ORD_0002", 7)),
     ], SimulationResult(
        [], [RejectedEvent(3, BusinessRejectionCode.UNKNOWN_ORDER_ID)],
        BookSnapshot((), (Level(105, 3), Level(106, 6))),
    )),
    ([
         (2, New("ORD_0001", Side.ASK, 105, 3, 1)),
         (3, New("ORD_0002", Side.ASK, 105, 5, 8)),
         (4, New("ORD_0003", Side.ASK, 106, 6, 4)),
         (5, Cancel("ORD_0002", 5)),
     ], SimulationResult(
        [], [],
        BookSnapshot((), (Level(105, 3), Level(106, 6))),
    )),
])
def test_cancel_priority_follows_arrival_not_timestamp(simulator, events, expected_simulation_result):
    simulator_result = simulator.run(events)

    assert simulator_result == expected_simulation_result

@pytest.mark.parametrize("input_file, expected_result_file", [
    ("sample_orders.csv", "sample_orders.expected.json"),
    ("sample_orders_with_errors.csv", "sample_orders_with_errors.expected.json")
])
def test_end_to_end(simulator, input_file, expected_result_file):
    current_dir = Path(__file__).resolve().parents[0]
    root_dir = Path(__file__).resolve().parents[1]

    input_file = root_dir / "data" / input_file
    input_events = read_order_flow_csv(input_file)
    simulator_result = simulator.run(input_events)

    with open(current_dir / "expected" / expected_result_file) as expected_json_file:
        expected_output = json.load(expected_json_file)

    expected_trades = [Trade(**trade) for trade in expected_output["trades"]]

    expected_rejections = []
    for rejection in expected_output["rejected_rows"]:
        try:
            rejection_reason = BusinessRejectionCode(rejection["reason"])
        except ValueError:
            rejection_reason = RejectionCode(rejection["reason"])

        expected_rejections.append(
            RejectedEvent(rejection["line"], rejection_reason)
        )

    expected_book_state = BookSnapshot(
        tuple([Level(*depth) for depth in expected_output["final_bid_depth"]]),
        tuple([Level(*depth) for depth in expected_output["final_ask_depth"]])
    )

    expected_result = SimulationResult(
        expected_trades, expected_rejections, expected_book_state
    )

    assert expected_result == simulator_result
