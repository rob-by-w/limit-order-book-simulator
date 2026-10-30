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
    assert simulator_result.final_book_state == {Side.BID: [(95,15)], Side.ASK: []}

def test_cancel_resting_order(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, Cancel("ORD_0001",2))
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


def test_crossing_orders(simulator):
    events = [
        (2, New("ORD_0001", Side.BID, 95, 15, 1)),
        (3, New("ORD_0002", Side.ASK, 94, 6, 2))
    ]

    simulator_result = simulator.run(events)

    assert simulator_result.trades == [Trade("TRD_0001", "ORD_0001", "ORD_0002", "ORD_0002", 95, 6, 2)]
    assert simulator_result.rejections == []
    assert simulator_result.final_book_state == {Side.BID: [(95, 9)], Side.ASK: []}