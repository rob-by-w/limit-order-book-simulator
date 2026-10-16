import pytest

from orderbook.order import Order, Side
from orderbook.book import OrderBook

DUPLICATE_ORDER_ID_ERROR_MSG = "Duplicate order ID"
UNKOWN_SIDE_ERROR_MSG = "Unregistered side, side is not BID or ASK"


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

    with pytest.raises(ValueError, match=UNKOWN_SIDE_ERROR_MSG):
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

    with pytest.raises(ValueError, match=UNKOWN_SIDE_ERROR_MSG):
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