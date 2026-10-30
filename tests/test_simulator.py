import pytest

from orderbook.events import New, Cancel
from orderbook.simulator import Simulator, SimulationResult
from orderbook.order import Side

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