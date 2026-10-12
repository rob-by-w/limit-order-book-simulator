"""Unit tests for the Order and Trade models: construction and validation."""

import dataclasses

import pytest

from orderbook.order import Order, Side, Trade

INVALID_ERROR_PRICE_MSG = "Price cannot be negative or 0"
INVALID_ORDER_QUANTITY_ERROR_MSG = "Order quantity cannot be negative or 0"
INVALID_FILLED_QUANTITY_ERROR_MSG = "Filled quantity cannot be negative"
FILLED_GREATER_THAN_ORDER_QUANTITY_ERROR_MSG = "Filled quantity cannot be greater than order quantity"
SAME_BUYER_AND_SELLER_ERROR_MSG = "Buyer and seller cannot be the same"
INVALID_TAKER_ORDER_ID_ERROR_MSG = "Taker order ID must be the same as either buy or sell order ID"
INVALID_TRADE_QUANTITY_ERROR_MSG = "Quantity cannot be negative or 0"


@pytest.fixture
def sample_order():
    return Order(
        id="ORD_0001",
        side=Side.BID,
        price=100,
        order_quantity=10,
        timestamp=1,
        seq_number=1
    )


def test_valid_order_is_created_with_defaults(sample_order):
    assert sample_order.price == 100
    assert sample_order.order_quantity == 10
    assert sample_order.filled_quantity == 0


def test_order_with_one_quantity():
    order = Order(
        id="ORD_0001",
        side=Side.BID,
        price=100,
        order_quantity=1,
        timestamp=1,
        seq_number=1
    )

    assert order.order_quantity == 1


def test_order_with_zero_quantity():
    with pytest.raises(ValueError, match=INVALID_ORDER_QUANTITY_ERROR_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=100,
            order_quantity=0,
            timestamp=1,
            seq_number=1
        )


def test_order_with_negative_order_quantity():
    with pytest.raises(ValueError, match=INVALID_ORDER_QUANTITY_ERROR_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=100,
            order_quantity=-10,
            timestamp=1,
            seq_number=1
        )


def test_order_with_filled_quantity_greater_than_order_quantity():
    with pytest.raises(ValueError, match=FILLED_GREATER_THAN_ORDER_QUANTITY_ERROR_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=100,
            order_quantity=10,
            filled_quantity=20,
            timestamp=1,
            seq_number=1
        )


def test_order_with_filled_quantity_equal_to_order_quantity():
    order = Order(
        id="ORD_0001",
        side=Side.BID,
        price=100,
        order_quantity=10,
        filled_quantity=10,
        timestamp=1,
        seq_number=1
    )

    assert order.filled_quantity == order.order_quantity


def test_order_with_negative_filled_quantity():
    with pytest.raises(ValueError, match=INVALID_FILLED_QUANTITY_ERROR_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=100,
            order_quantity=10,
            filled_quantity=-1,
            timestamp=1,
            seq_number=1
        )


def test_order_with_zero_price():
    with pytest.raises(ValueError, match=INVALID_ERROR_PRICE_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=0,
            order_quantity=10,
            timestamp=1,
            seq_number=1
        )


def test_order_with_negative_price():
    with pytest.raises(ValueError, match=INVALID_ERROR_PRICE_MSG):
        Order(
            id="ORD_0001",
            side=Side.BID,
            price=-15,
            order_quantity=10,
            timestamp=1,
            seq_number=1
        )


def test_valid_trade_is_created():
    trade = Trade(
        id="TRD_0001",
        buy_order_id="ORD_0001",
        sell_order_id="ORD_0002",
        taker_order_id="ORD_0002",
        price=100,
        quantity=5,
        timestamp=5
    )

    assert trade.price == 100
    assert trade.quantity == 5


def test_trade_with_invalid_taker_order_id():
    with pytest.raises(ValueError, match=INVALID_TAKER_ORDER_ID_ERROR_MSG):
        Trade(
            id="TRD_0001",
            buy_order_id="ORD_0001",
            sell_order_id="ORD_0002",
            taker_order_id="ORD_0012",
            price=100,
            quantity=5,
            timestamp=5
        )


def test_trade_with_same_buyer_and_seller():
    with pytest.raises(ValueError, match=SAME_BUYER_AND_SELLER_ERROR_MSG):
        Trade(
            id="TRD_0001",
            buy_order_id="ORD_0001",
            sell_order_id="ORD_0001",
            taker_order_id="ORD_0001",
            price=100,
            quantity=5,
            timestamp=5
        )


def test_trade_with_one_quantity():
    trade = Trade(
        id="TRD_0001",
        buy_order_id="ORD_0001",
        sell_order_id="ORD_0002",
        taker_order_id="ORD_0002",
        price=100,
        quantity=1,
        timestamp=5
    )

    assert trade.quantity == 1


def test_trade_with_zero_quantity():
    with pytest.raises(ValueError, match=INVALID_TRADE_QUANTITY_ERROR_MSG):
        Trade(
            id="TRD_0001",
            buy_order_id="ORD_0001",
            sell_order_id="ORD_0002",
            taker_order_id="ORD_0002",
            price=100,
            quantity=0,
            timestamp=5
        )


def test_trade_with_one_price():
    trade = Trade(
        id="TRD_0001",
        buy_order_id="ORD_0001",
        sell_order_id="ORD_0002",
        taker_order_id="ORD_0002",
        price=1,
        quantity=10,
        timestamp=5
    )

    assert trade.price == 1


def test_trade_with_zero_price():
    with pytest.raises(ValueError, match=INVALID_ERROR_PRICE_MSG):
        Trade(
            id="TRD_0001",
            buy_order_id="ORD_0001",
            sell_order_id="ORD_0002",
            taker_order_id="ORD_0002",
            price=0,
            quantity=10,
            timestamp=5
        )


def test_trade_with_negative_price():
    with pytest.raises(ValueError, match=INVALID_ERROR_PRICE_MSG):
        Trade(
            id="TRD_0001",
            buy_order_id="ORD_0001",
            sell_order_id="ORD_0002",
            taker_order_id="ORD_0002",
            price=-100,
            quantity=10,
            timestamp=5
        )


def test_trade_is_immutable():
    trade = Trade(
        id="TRD_0001",
        buy_order_id="ORD_0001",
        sell_order_id="ORD_0002",
        taker_order_id="ORD_0002",
        price=100,
        quantity=5,
        timestamp=5
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        trade.quantity = 10
