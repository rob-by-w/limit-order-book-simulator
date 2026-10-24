import pytest

from orderbook.order import Order, Side, Trade
from orderbook.book import OrderBook
from orderbook.matching import MatchingEngine

DUPLICATE_ORDER_ID_ERROR_MSG = "Duplicate order ID"


@pytest.fixture
def orderbook_with_two_resting_orders(order_bid_id_1_7_at_100, order_bid_id_2_13_at_98, order_ask_id_11_6_at_103,
                                      order_ask_id_12_2_at_106):
    # Bid: 7@100, 13@98
    # Ask: 6@103, 2@106

    orderbook = OrderBook()

    orderbook.add_order(order_bid_id_1_7_at_100)
    orderbook.add_order(order_bid_id_2_13_at_98)

    orderbook.add_order(order_ask_id_11_6_at_103)
    orderbook.add_order(order_ask_id_12_2_at_106)

    return orderbook


@pytest.fixture
def orderbook_with_resting_orders_at_same_price(order_bid_id_3_6_at_103, order_bid_id_102_6_at_103,
                                                order_ask_id_12_2_at_106, order_ask_id_13_5_at_106):
    # Bid: {103: [[#102, #3], 12]}
    # Ask: {106: [[#12, #13], 7]}

    orderbook = OrderBook()

    orderbook.add_order(order_bid_id_3_6_at_103)
    orderbook.add_order(order_bid_id_102_6_at_103)

    orderbook.add_order(order_ask_id_12_2_at_106)
    orderbook.add_order(order_ask_id_13_5_at_106)

    return orderbook


@pytest.fixture
def order_bid_id_1_7_at_100():
    return Order(
        id="ORD_0001",
        side=Side.BID,
        price=100,
        order_quantity=7,
        timestamp=1,
        seq_number=1
    )


@pytest.fixture
def order_bid_id_2_13_at_98():
    return Order(
        id="ORD_0002",
        side=Side.BID,
        price=98,
        order_quantity=13,
        timestamp=2,
        seq_number=2
    )


@pytest.fixture
def order_bid_id_3_6_at_103():
    return Order(
        id="ORD_0003",
        side=Side.BID,
        price=103,
        order_quantity=6,
        timestamp=3,
        seq_number=3
    )


@pytest.fixture
def order_bid_id_101_5_at_101():
    return Order(
        id="ORD_0101",
        side=Side.BID,
        price=101,
        order_quantity=5,
        timestamp=101,
        seq_number=101
    )


@pytest.fixture
def order_bid_id_102_6_at_103():
    return Order(
        id="ORD_0102",
        side=Side.BID,
        price=103,
        order_quantity=6,
        timestamp=102,
        seq_number=102
    )


@pytest.fixture
def order_bid_id_103_8_at_108():
    return Order(
        id="ORD_0103",
        side=Side.BID,
        price=108,
        order_quantity=8,
        timestamp=103,
        seq_number=103
    )


@pytest.fixture
def order_bid_id_104_10_at_104():
    return Order(
        id="ORD_0104",
        side=Side.BID,
        price=104,
        order_quantity=10,
        timestamp=104,
        seq_number=104
    )


@pytest.fixture
def order_bid_id_105_1_at_105():
    return Order(
        id="ORD_0105",
        side=Side.BID,
        price=105,
        order_quantity=1,
        timestamp=105,
        seq_number=105
    )


@pytest.fixture
def order_bid_id_106_12_at_107():
    return Order(
        id="ORD_0106",
        side=Side.BID,
        price=107,
        order_quantity=12,
        timestamp=106,
        seq_number=106
    )


@pytest.fixture
def order_bid_id_107_1_at_106():
    return Order(
        id="ORD_0107",
        side=Side.BID,
        price=106,
        order_quantity=1,
        timestamp=107,
        seq_number=107
    )


@pytest.fixture
def order_bid_id_108_2_at_106():
    return Order(
        id="ORD_0108",
        side=Side.BID,
        price=106,
        order_quantity=2,
        timestamp=108,
        seq_number=108
    )


@pytest.fixture
def order_bid_id_109_4_at_109():
    return Order(
        id="ORD_0109",
        side=Side.BID,
        price=109,
        order_quantity=4,
        timestamp=109,
        seq_number=109
    )

@pytest.fixture
def order_bid_id_110_1_at_106():
    return Order(
        id="ORD_0110",
        side=Side.BID,
        price=106,
        order_quantity=1,
        timestamp=110,
        seq_number=110
    )


@pytest.fixture
def order_ask_id_11_6_at_103():
    return Order(
        id="ORD_0011",
        side=Side.ASK,
        price=103,
        order_quantity=6,
        timestamp=1,
        seq_number=11
    )


@pytest.fixture
def order_ask_id_12_2_at_106():
    return Order(
        id="ORD_0012",
        side=Side.ASK,
        price=106,
        order_quantity=2,
        timestamp=3,
        seq_number=12
    )


@pytest.fixture
def order_ask_id_13_5_at_106():
    return Order(
        id="ORD_0013",
        side=Side.ASK,
        price=106,
        order_quantity=5,
        timestamp=4,
        seq_number=13
    )


@pytest.fixture
def order_ask_id_1_30_at_95():
    return Order(
        id="ORD_0001",
        side=Side.ASK,
        price=95,
        order_quantity=30,
        timestamp=1111,
        seq_number=1111
    )


@pytest.fixture
def order_ask_id_201_4_at_105():
    return Order(
        id="ORD_0201",
        side=Side.ASK,
        price=105,
        order_quantity=4,
        timestamp=201,
        seq_number=201
    )


@pytest.fixture
def order_ask_id_202_7_at_100():
    return Order(
        id="ORD_0202",
        side=Side.ASK,
        price=100,
        order_quantity=7,
        timestamp=202,
        seq_number=202
    )


@pytest.fixture
def order_ask_id_203_20_at_95():
    return Order(
        id="ORD_0203",
        side=Side.ASK,
        price=95,
        order_quantity=20,
        timestamp=203,
        seq_number=203
    )


@pytest.fixture
def order_ask_id_204_8_at_99():
    return Order(
        id="ORD_0204",
        side=Side.ASK,
        price=99,
        order_quantity=8,
        timestamp=204,
        seq_number=204
    )


@pytest.fixture
def order_ask_id_205_2_at_99():
    return Order(
        id="ORD_0205",
        side=Side.ASK,
        price=99,
        order_quantity=2,
        timestamp=205,
        seq_number=205
    )


@pytest.fixture
def order_ask_id_206_30_at_95():
    return Order(
        id="ORD_0206",
        side=Side.ASK,
        price=95,
        order_quantity=30,
        timestamp=206,
        seq_number=206
    )


@pytest.mark.parametrize(
    "orderbook, incoming_order", [
        ("orderbook_with_two_resting_orders", "order_bid_id_1_7_at_100"),
        ("orderbook_with_two_resting_orders", "order_ask_id_12_2_at_106"),
        ("orderbook_with_two_resting_orders", "order_ask_id_1_30_at_95")
    ])
def test_incoming_order_with_duplicate_id(orderbook, incoming_order, request):
    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))

    initial_best_bid = matching_engine.orderbook.best_bid()
    initial_best_ask = matching_engine.orderbook.best_ask()
    initial_bid_depth = matching_engine.orderbook.depth(Side.BID, 10)
    initial_ask_depth = matching_engine.orderbook.depth(Side.ASK, 10)

    with pytest.raises(ValueError, match=DUPLICATE_ORDER_ID_ERROR_MSG):
        matching_engine.submit(request.getfixturevalue(incoming_order))

    assert matching_engine.orderbook.best_bid() == initial_best_bid
    assert matching_engine.orderbook.best_ask() == initial_best_ask
    assert matching_engine.orderbook.depth(Side.BID, 10) == initial_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == initial_ask_depth


@pytest.mark.parametrize("orderbook, incoming_order, expected_bid_depth, expected_ask_depth", [
    ("orderbook_with_two_resting_orders", "order_bid_id_101_5_at_101", [(101, 5), (100, 7), (98, 13)],
     [(103, 6), (106, 2)]),
    ("orderbook_with_two_resting_orders", "order_ask_id_201_4_at_105", [(100, 7), (98, 13)],
     [(103, 6), (105, 4), (106, 2)])
])
def test_no_filled_incoming_order(orderbook, incoming_order, expected_bid_depth, expected_ask_depth,
                                  request):
    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))
    output_trade = matching_engine.submit(request.getfixturevalue(incoming_order))

    assert output_trade == []
    assert matching_engine.orderbook.best_bid() < matching_engine.orderbook.best_ask()
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth


@pytest.mark.parametrize(
    "orderbook, incoming_order, expected_trades, expected_bid_depth, expected_ask_depth, expected_new_top_order", [
        ("orderbook_with_two_resting_orders", "order_ask_id_202_7_at_100",
         [Trade(id="TRD_0001", buy_order_id="ORD_0001", sell_order_id="ORD_0202", taker_order_id="ORD_0202", price=100,
                quantity=7, timestamp=202)], [(98, 13)], [(103, 6), (106, 2)], "order_bid_id_2_13_at_98"),
        ("orderbook_with_two_resting_orders", "order_bid_id_102_6_at_103",
         [Trade(id="TRD_0001", buy_order_id="ORD_0102", sell_order_id="ORD_0011", taker_order_id="ORD_0102", price=103,
                quantity=6, timestamp=102)], [(100, 7), (98, 13)], [(106, 2)], "order_ask_id_12_2_at_106"),
        ("orderbook_with_resting_orders_at_same_price", "order_ask_id_11_6_at_103",
         [Trade(id="TRD_0001", buy_order_id="ORD_0003", sell_order_id="ORD_0011", taker_order_id="ORD_0011", price=103,
                quantity=6, timestamp=1)], [(103, 6)], [(106, 7)], "order_bid_id_102_6_at_103"),
        ("orderbook_with_resting_orders_at_same_price", "order_bid_id_108_2_at_106",
         [Trade(id="TRD_0001", buy_order_id="ORD_0108", sell_order_id="ORD_0012", taker_order_id="ORD_0108", price=106,
                quantity=2, timestamp=108)], [(103, 12)], [(106, 5)], "order_ask_id_13_5_at_106")
    ])
def test_match_incoming_order_with_top_order(orderbook, incoming_order, expected_trades, expected_bid_depth,
                                             expected_ask_depth, expected_new_top_order, request):
    incoming_order_local = request.getfixturevalue(incoming_order)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))
    output_trade = matching_engine.submit(incoming_order_local)
    top_order_after_execution = matching_engine.orderbook.get_top_order(
        Side.BID if incoming_order_local.side == Side.ASK else Side.ASK)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.best_bid() < matching_engine.orderbook.best_ask()
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
    assert top_order_after_execution is request.getfixturevalue(expected_new_top_order)
    assert incoming_order_local.id not in matching_engine.orderbook.index


@pytest.mark.parametrize(
    "orderbook, incoming_order, expected_trades, expected_best_bid, expected_best_ask, expected_bid_depth, "
    "expected_ask_depth",
    [
        ("orderbook_with_two_resting_orders", "order_ask_id_203_20_at_95",
         [Trade(id="TRD_0001", buy_order_id="ORD_0001", sell_order_id="ORD_0203", taker_order_id="ORD_0203", price=100,
                quantity=7, timestamp=203),
          Trade(id="TRD_0002", buy_order_id="ORD_0002", sell_order_id="ORD_0203", taker_order_id="ORD_0203", price=98,
                quantity=13, timestamp=203)
          ], None, 103, [], [(103, 6), (106, 2)]),
        ("orderbook_with_two_resting_orders", "order_bid_id_103_8_at_108",
         [Trade(id="TRD_0001", buy_order_id="ORD_0103", sell_order_id="ORD_0011", taker_order_id="ORD_0103", price=103,
                quantity=6, timestamp=103),
          Trade(id="TRD_0002", buy_order_id="ORD_0103", sell_order_id="ORD_0012", taker_order_id="ORD_0103", price=106,
                quantity=2, timestamp=103)
          ], 100, None, [(100, 7), (98, 13)], [])
    ])
def test_take_all_resting_orders_in_orderbook(orderbook, incoming_order, expected_trades, expected_best_bid,
                                              expected_best_ask, expected_bid_depth, expected_ask_depth, request):
    incoming_order_local = request.getfixturevalue(incoming_order)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))
    output_trade = matching_engine.submit(incoming_order_local)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.best_bid() == expected_best_bid
    assert matching_engine.orderbook.best_ask() == expected_best_ask
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
    assert incoming_order_local.id not in matching_engine.orderbook.index


@pytest.mark.parametrize(
    "orderbook, incoming_order, expected_trades, expected_best_bid, expected_best_ask, expected_bid_depth, "
    "expected_ask_depth",
    [
        ("orderbook_with_two_resting_orders", "order_ask_id_204_8_at_99",
         [Trade(id="TRD_0001", buy_order_id="ORD_0001", sell_order_id="ORD_0204", taker_order_id="ORD_0204", price=100,
                quantity=7, timestamp=204)], 98, 99, [(98, 13)], [(99, 1), (103, 6), (106, 2)]),
        ("orderbook_with_two_resting_orders", "order_ask_id_206_30_at_95",
         [Trade(id="TRD_0001", buy_order_id="ORD_0001", sell_order_id="ORD_0206", taker_order_id="ORD_0206", price=100,
                quantity=7, timestamp=206),
          Trade(id="TRD_0002", buy_order_id="ORD_0002", sell_order_id="ORD_0206", taker_order_id="ORD_0206", price=98,
                quantity=13, timestamp=206)
          ], None, 95, [], [(95, 10), (103, 6), (106, 2)]),
        ("orderbook_with_two_resting_orders", "order_bid_id_104_10_at_104",
         [Trade(id="TRD_0001", buy_order_id="ORD_0104", sell_order_id="ORD_0011", taker_order_id="ORD_0104", price=103,
                quantity=6, timestamp=104)], 104, 106, [(104, 4), (100, 7), (98, 13)], [(106, 2)]),
        ("orderbook_with_two_resting_orders", "order_bid_id_106_12_at_107",
         [Trade(id="TRD_0001", buy_order_id="ORD_0106", sell_order_id="ORD_0011", taker_order_id="ORD_0106", price=103,
                quantity=6, timestamp=106),
          Trade(id="TRD_0002", buy_order_id="ORD_0106", sell_order_id="ORD_0012", taker_order_id="ORD_0106", price=106,
                quantity=2, timestamp=106)
          ], 107, None, [(107, 4), (100, 7), (98, 13)], [])
    ])
def test_partial_fill_incoming_order(orderbook, incoming_order, expected_trades, expected_best_bid,
                                     expected_best_ask, expected_bid_depth, expected_ask_depth,
                                     request):
    incoming_order_local = request.getfixturevalue(incoming_order)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))
    output_trade = matching_engine.submit(incoming_order_local)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.best_bid() == expected_best_bid
    assert matching_engine.orderbook.best_ask() == expected_best_ask
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
    assert incoming_order_local.id in matching_engine.orderbook.index


@pytest.mark.parametrize("orderbook, incoming_order, expected_trades, expected_bid_depth, expected_ask_depth", [
    ("orderbook_with_two_resting_orders", "order_ask_id_205_2_at_99",
     [Trade(id="TRD_0001", buy_order_id="ORD_0001", sell_order_id="ORD_0205", taker_order_id="ORD_0205", price=100,
            quantity=2, timestamp=205)], [(100, 5), (98, 13)], [(103, 6), (106, 2)]),
    ("orderbook_with_two_resting_orders", "order_bid_id_105_1_at_105",
     [Trade(id="TRD_0001", buy_order_id="ORD_0105", sell_order_id="ORD_0011", taker_order_id="ORD_0105", price=103,
            quantity=1, timestamp=105)], [(100, 7), (98, 13)], [(103, 5), (106, 2)]),
    ("orderbook_with_resting_orders_at_same_price", "order_ask_id_205_2_at_99",
     [Trade(id="TRD_0001", buy_order_id="ORD_0003", sell_order_id="ORD_0205", taker_order_id="ORD_0205", price=103,
            quantity=2, timestamp=205)], [(103, 10)], [(106, 7)]),
    ("orderbook_with_resting_orders_at_same_price", "order_bid_id_107_1_at_106",
     [Trade(id="TRD_0001", buy_order_id="ORD_0107", sell_order_id="ORD_0012", taker_order_id="ORD_0107", price=106,
            quantity=1, timestamp=107)], [(103, 12)], [(106, 6)])
])
def test_partial_fill_top_resting_order(orderbook, incoming_order, expected_trades, expected_bid_depth,
                                        expected_ask_depth,
                                        request):
    incoming_order_local = request.getfixturevalue(incoming_order)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))
    top_order_before_execution = matching_engine.orderbook.get_top_order(
        Side.BID if incoming_order_local.side == Side.ASK else Side.ASK)

    output_trade = matching_engine.submit(incoming_order_local)
    top_order_after_execution = matching_engine.orderbook.get_top_order(
        Side.BID if incoming_order_local.side == Side.ASK else Side.ASK)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
    assert top_order_before_execution is top_order_after_execution
    assert incoming_order_local.id not in matching_engine.orderbook.index


@pytest.mark.parametrize(
    "orderbook, incoming_order, expected_trades, expected_top_trade, expected_bid_depth, expected_ask_depth", [
        ("orderbook_with_resting_orders_at_same_price", "order_ask_id_204_8_at_99",
         [Trade(id="TRD_0001", buy_order_id="ORD_0003", sell_order_id="ORD_0204", taker_order_id="ORD_0204", price=103,
                quantity=6, timestamp=204),
          Trade(id="TRD_0002", buy_order_id="ORD_0102", sell_order_id="ORD_0204", taker_order_id="ORD_0204", price=103,
                quantity=2, timestamp=204)
          ], "order_bid_id_102_6_at_103", [(103, 4)], [(106, 7)]),
        ("orderbook_with_resting_orders_at_same_price", "order_bid_id_109_4_at_109",
         [Trade(id="TRD_0001", buy_order_id="ORD_0109", sell_order_id="ORD_0012", taker_order_id="ORD_0109", price=106,
                quantity=2, timestamp=109),
          Trade(id="TRD_0002", buy_order_id="ORD_0109", sell_order_id="ORD_0013", taker_order_id="ORD_0109", price=106,
                quantity=2, timestamp=109)
          ], "order_ask_id_13_5_at_106", [(103, 12)], [(106, 3)])

    ])
def test_fill_multiple_resting_order(orderbook, incoming_order, expected_trades, expected_top_trade, expected_bid_depth,
                                     expected_ask_depth, request):
    incoming_order_local = request.getfixturevalue(incoming_order)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))

    output_trade = matching_engine.submit(incoming_order_local)
    top_order_after_execution = matching_engine.orderbook.get_top_order(
        Side.BID if incoming_order_local.side == Side.ASK else Side.ASK)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
    assert top_order_after_execution is request.getfixturevalue(expected_top_trade)
    assert incoming_order_local.id not in matching_engine.orderbook.index


@pytest.mark.parametrize(
    "orderbook, incoming_order_1, incoming_order_2, expected_trades, expected_bid_depth, expected_ask_depth", [
        ("orderbook_with_resting_orders_at_same_price", "order_ask_id_11_6_at_103", "order_ask_id_205_2_at_99",
         [Trade(id="TRD_0001", buy_order_id="ORD_0003", sell_order_id="ORD_0011", taker_order_id="ORD_0011", price=103,
                quantity=6, timestamp=1),
          Trade(id="TRD_0002", buy_order_id="ORD_0102", sell_order_id="ORD_0205", taker_order_id="ORD_0205", price=103,
                quantity=2, timestamp=205)
          ], [(103, 4)], [(106, 7)]),
        ("orderbook_with_resting_orders_at_same_price", "order_bid_id_109_4_at_109", "order_bid_id_110_1_at_106",
         [Trade(id="TRD_0001", buy_order_id="ORD_0109", sell_order_id="ORD_0012", taker_order_id="ORD_0109", price=106,
                quantity=2, timestamp=109),
          Trade(id="TRD_0002", buy_order_id="ORD_0109", sell_order_id="ORD_0013", taker_order_id="ORD_0109", price=106,
                quantity=2, timestamp=109),
          Trade(id="TRD_0003", buy_order_id="ORD_0110", sell_order_id="ORD_0013", taker_order_id="ORD_0110", price=106,
                quantity=1, timestamp=110)
          ], [(103, 12)], [(106, 2)])

    ])
def test_multiple_incoming_orders(orderbook, incoming_order_1, incoming_order_2, expected_trades,
                                  expected_bid_depth, expected_ask_depth, request):
    incoming_order_1_local = request.getfixturevalue(incoming_order_1)
    incoming_order_2_local = request.getfixturevalue(incoming_order_2)

    matching_engine = MatchingEngine(request.getfixturevalue(orderbook))

    output_trade = matching_engine.submit(incoming_order_1_local)
    output_trade += matching_engine.submit(incoming_order_2_local)

    assert output_trade == expected_trades
    assert matching_engine.orderbook.depth(Side.BID, 10) == expected_bid_depth
    assert matching_engine.orderbook.depth(Side.ASK, 10) == expected_ask_depth
