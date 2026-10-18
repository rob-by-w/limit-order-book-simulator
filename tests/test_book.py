import pytest

from orderbook.order import Order, Side
from orderbook.book import OrderBook

DUPLICATE_ORDER_ID_ERROR_MSG = "Duplicate order ID"
UNKNOWN_SIDE_ERROR_MSG = "Unregistered side, side is not BID or ASK"
UNKNOWN_CANCEL_ID_ERROR_MSG = "Order is not available"


@pytest.fixture
def order_bid_1():
    return Order(
        id="ORD_0001",
        side=Side.BID,
        price=100,
        order_quantity=10,
        timestamp=1,
        seq_number=1
    )


@pytest.fixture
def order_bid_2():
    return Order(
        id="ORD_0002",
        side=Side.BID,
        price=100,
        order_quantity=15,
        timestamp=2,
        seq_number=2
    )


@pytest.fixture
def order_bid_3():
    return Order(
        id="ORD_0003",
        side=Side.BID,
        price=101,
        order_quantity=8,
        timestamp=3,
        seq_number=3
    )


@pytest.fixture
def order_bid_4():
    return Order(
        id="ORD_0004",
        side=5,
        price=104,
        order_quantity=2,
        timestamp=4,
        seq_number=4
    )


@pytest.fixture
def order_bid_5():
    return Order(
        id="ORD_0011",
        side=Side.BID,
        price=104,
        order_quantity=2,
        timestamp=4,
        seq_number=4
    )


@pytest.fixture
def order_bid_6():
    return Order(
        id="ORD_0006",
        side=Side.BID,
        price=100,
        order_quantity=6,
        timestamp=5,
        seq_number=5
    )


@pytest.fixture
def order_ask_1():
    return Order(
        id="ORD_0011",
        side=Side.ASK,
        price=105,
        order_quantity=5,
        timestamp=1,
        seq_number=11
    )


@pytest.fixture
def order_ask_2():
    return Order(
        id="ORD_0012",
        side=Side.ASK,
        price=105,
        order_quantity=3,
        timestamp=2,
        seq_number=12
    )


@pytest.fixture
def order_ask_3():
    return Order(
        id="ORD_0013",
        side=Side.ASK,
        price=107,
        order_quantity=10,
        timestamp=3,
        seq_number=13
    )


@pytest.fixture
def order_ask_4():
    return Order(
        id="ORD_0014",
        side=6,
        price=112,
        order_quantity=1,
        timestamp=4,
        seq_number=14
    )


def test_valid_orderbook_is_created():
    OrderBook()


def test_add_new_bid_order(order_bid_1):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_1.id: order_bid_1}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.ask_levels == {}
    assert orderbook.ask_heap == []
    assert orderbook.index == {order_bid_1.id: order_bid_1}


def test_add_same_price_bid_orders(order_bid_1, order_bid_2):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_2)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_1.id: order_bid_1, order_bid_2.id: order_bid_2}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.index == {order_bid_1.id: order_bid_1, order_bid_2.id: order_bid_2}


def test_add_different_price_bid_orders(order_bid_1, order_bid_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_3)

    assert orderbook.bid_levels == {
        order_bid_1.price: {
            order_bid_1.id: order_bid_1
        }, order_bid_3.price: {
            order_bid_3.id: order_bid_3
        }
    }
    assert orderbook.bid_heap == [-1 * order_bid_3.price, -1 * order_bid_1.price]
    assert orderbook.index == {order_bid_1.id: order_bid_1, order_bid_3.id: order_bid_3}


def test_add_duplicate_bid_orders(order_bid_1):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)

    with pytest.raises(ValueError, match=DUPLICATE_ORDER_ID_ERROR_MSG):
        orderbook.add_order(order_bid_1)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_1.id: order_bid_1}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.ask_levels == {}
    assert orderbook.ask_heap == []
    assert orderbook.index == {order_bid_1.id: order_bid_1}


def test_add_bid_order_with_unknown_side(order_bid_1, order_bid_4):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)

    with pytest.raises(ValueError, match=UNKNOWN_SIDE_ERROR_MSG):
        orderbook.add_order(order_bid_4)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_1.id: order_bid_1}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.ask_levels == {}
    assert orderbook.ask_heap == []
    assert orderbook.index == {order_bid_1.id: order_bid_1}


def test_add_new_ask_order(order_ask_1):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == []
    assert orderbook.ask_levels == {order_ask_1.price: {order_ask_1.id: order_ask_1}}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1}


def test_add_same_price_ask_orders(order_ask_1, order_ask_2):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_2)

    assert orderbook.ask_levels == {order_ask_1.price: {order_ask_1.id: order_ask_1, order_ask_2.id: order_ask_2}}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1, order_ask_2.id: order_ask_2}


def test_add_different_price_ask_orders(order_ask_1, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_3)

    assert orderbook.ask_levels == {
        order_ask_1.price: {
            order_ask_1.id: order_ask_1
        }, order_ask_3.price: {
            order_ask_3.id: order_ask_3
        }
    }
    assert orderbook.ask_heap == [order_ask_1.price, order_ask_3.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1, order_ask_3.id: order_ask_3}


def test_add_duplicate_ask_orders(order_ask_1):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)

    with pytest.raises(ValueError, match=DUPLICATE_ORDER_ID_ERROR_MSG):
        orderbook.add_order(order_ask_1)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == []
    assert orderbook.ask_levels == {order_ask_1.price: {order_ask_1.id: order_ask_1}}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1}


def test_add_ask_orders_with_unknown_side(order_ask_1, order_ask_4):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)

    with pytest.raises(ValueError, match=UNKNOWN_SIDE_ERROR_MSG):
        orderbook.add_order(order_ask_4)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == []
    assert orderbook.ask_levels == {order_ask_1.price: {order_ask_1.id: order_ask_1}}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1}


def test_add_duplicate_orders_with_opposing_side(order_ask_1, order_bid_5):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)

    with pytest.raises(ValueError, match=DUPLICATE_ORDER_ID_ERROR_MSG):
        orderbook.add_order(order_bid_5)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == []
    assert orderbook.ask_levels == {order_ask_1.price: {order_ask_1.id: order_ask_1}}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {order_ask_1.id: order_ask_1}


def test_cancel_one_of_two_orders_with_same_price(order_bid_1, order_bid_2):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_2)

    orderbook.cancel_order(order_bid_1.id)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_2.id: order_bid_2}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.index == {order_bid_2.id: order_bid_2}


def test_cancel_only_order_at_a_price(order_bid_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_3)
    orderbook.cancel_order(order_bid_3.id)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == [-1 * order_bid_3.price]
    assert orderbook.index == {}


def test_cancel_unknown_order_id(order_bid_1, order_bid_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)

    with pytest.raises(ValueError, match=UNKNOWN_CANCEL_ID_ERROR_MSG):
        orderbook.cancel_order(order_bid_3.id)

    assert orderbook.bid_levels == {order_bid_1.price: {order_bid_1.id: order_bid_1}}
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.index == {order_bid_1.id: order_bid_1}


def test_cancel_same_order_twice(order_ask_1):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)
    orderbook.cancel_order(order_ask_1.id)

    with pytest.raises(ValueError, match=UNKNOWN_CANCEL_ID_ERROR_MSG):
        orderbook.cancel_order(order_ask_1.id)

    assert orderbook.ask_levels == {}
    assert orderbook.ask_heap == [order_ask_1.price]
    assert orderbook.index == {}


def test_cancel_order_on_opposite_side(order_bid_2, order_ask_2):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_2)
    orderbook.add_order(order_ask_2)

    orderbook.cancel_order(order_bid_2.id)

    assert orderbook.bid_levels == {}
    assert orderbook.bid_heap == [-1 * order_bid_2.price]
    assert orderbook.ask_levels == {order_ask_2.price: {order_ask_2.id: order_ask_2}}
    assert orderbook.ask_heap == [order_ask_2.price]
    assert orderbook.index == {order_ask_2.id: order_ask_2}


def test_cancel_middle_order(order_bid_1, order_bid_2, order_bid_6):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_2)
    orderbook.add_order(order_bid_6)

    orderbook.cancel_order(order_bid_2.id)

    assert orderbook.bid_levels == {
        order_bid_1.price: {
            order_bid_1.id: order_bid_1,
            order_bid_6.id: order_bid_6
        }
    }
    assert orderbook.bid_heap == [-1 * order_bid_1.price]
    assert orderbook.index == {
        order_bid_1.id: order_bid_1,
        order_bid_6.id: order_bid_6
    }
    assert list(orderbook.bid_levels[order_bid_1.price]) == [order_bid_1.id, order_bid_6.id]


def test_add_same_price_order_after_cancellation(order_ask_1, order_ask_2):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)

    orderbook.cancel_order(order_ask_1.id)

    orderbook.add_order(order_ask_2)

    assert orderbook.ask_levels == {order_ask_2.price: {order_ask_2.id: order_ask_2}}
    assert orderbook.ask_heap == [order_ask_1.price, order_ask_2.price]
    assert orderbook.index == {order_ask_2.id: order_ask_2}


def test_best_bid_ask_from_empty_orderbook():
    orderbook = OrderBook()

    assert orderbook.best_bid() is None
    assert orderbook.best_ask() is None


def test_best_bid_from_orderbook_with_single_bid_order(order_bid_1):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)

    assert orderbook.best_bid() == order_bid_1.price
    assert orderbook.best_ask() is None


def test_best_bid_ask_from_orderbook_with_multiple_levels(order_bid_1, order_bid_2, order_bid_3, order_ask_1,
                                                          order_ask_2, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_2)
    orderbook.add_order(order_bid_3)
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_2)
    orderbook.add_order(order_ask_3)

    assert orderbook.best_bid() == max([order_bid_1.price, order_bid_2.price, order_bid_3.price])
    assert orderbook.best_ask() == min([order_ask_1.price, order_ask_2.price, order_ask_3.price])


def test_best_bid_ask_after_cancellation(order_bid_1, order_bid_3, order_ask_1, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_3)
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_3)

    orderbook.cancel_order(order_bid_1.id)
    orderbook.cancel_order(order_ask_1.id)

    assert orderbook.best_bid() == order_bid_3.price
    assert orderbook.best_ask() == order_ask_3.price


def test_best_bid_ask_on_stacked_stale_prices_in_heap(order_bid_2, order_bid_3, order_ask_2, order_ask_3):
    orderbook = OrderBook()

    orderbook.add_order(order_bid_3)
    orderbook.cancel_order(order_bid_3.id)
    orderbook.add_order(order_bid_3)
    orderbook.cancel_order(order_bid_3.id)
    orderbook.add_order(order_bid_2)

    orderbook.add_order(order_ask_2)
    orderbook.cancel_order(order_ask_2.id)
    orderbook.add_order(order_ask_2)
    orderbook.cancel_order(order_ask_2.id)
    orderbook.add_order(order_ask_3)

    assert orderbook.best_bid() == order_bid_2.price
    assert orderbook.best_ask() == order_ask_3.price
    assert orderbook.bid_heap == [-1 * order_bid_2.price]
    assert orderbook.ask_heap == [order_ask_3.price]


def test_multiple_calls_on_best_bid_ask(order_bid_1, order_bid_3, order_ask_1, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_3)
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_3)

    assert orderbook.best_bid() == order_bid_3.price
    assert orderbook.bid_heap == [-1 * order_bid_3.price, -1 * order_bid_1.price]
    assert orderbook.best_bid() == order_bid_3.price
    assert orderbook.bid_heap == [-1 * order_bid_3.price, -1 * order_bid_1.price]

    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.ask_heap == [order_ask_1.price, order_ask_3.price]
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.ask_heap == [order_ask_1.price, order_ask_3.price]


def test_spread_when_both_sides_are_populated(order_bid_1, order_bid_3, order_ask_1, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_3)
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_3)

    assert orderbook.best_bid() == order_bid_3.price
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.spread() == 4      # bid_3 = 101, ask_1 = 105


def test_spread_when_only_bids_are_available(order_bid_1, order_bid_2):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_2)

    assert orderbook.best_bid() == order_bid_1.price
    assert orderbook.best_ask() is None
    assert orderbook.spread() is None


def test_spread_when_only_asks_are_available(order_ask_1, order_ask_2):
    orderbook = OrderBook()
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_2)

    assert orderbook.best_bid() is None
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.spread() is None


def test_spread_when_no_orders():
    orderbook = OrderBook()

    assert orderbook.best_bid() is None
    assert orderbook.best_ask() is None
    assert orderbook.spread() is None


def test_spread_widen_after_cancelling_higher_bid(order_bid_1, order_bid_3, order_ask_1):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_bid_3)
    orderbook.add_order(order_ask_1)

    assert orderbook.best_bid() == order_bid_3.price
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.spread() == 4      # bid_3 = 101, ask_1 = 105

    orderbook.cancel_order(order_bid_3.id)

    assert orderbook.best_bid() == order_bid_1.price
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.spread() == 5      # bid_1 = 100, ask_1 = 105


def test_spread_widen_after_cancelling_lower_ask(order_bid_1, order_ask_1, order_ask_3):
    orderbook = OrderBook()
    orderbook.add_order(order_bid_1)
    orderbook.add_order(order_ask_1)
    orderbook.add_order(order_ask_3)

    assert orderbook.best_bid() == order_bid_1.price
    assert orderbook.best_ask() == order_ask_1.price
    assert orderbook.spread() == 5      # bid_1 = 100, ask_1 = 105

    orderbook.cancel_order(order_ask_1.id)

    assert orderbook.best_bid() == order_bid_1.price
    assert orderbook.best_ask() == order_ask_3.price
    assert orderbook.spread() == 7      # bid_1 = 100, ask_3 = 107
