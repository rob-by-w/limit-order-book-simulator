import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError

from orderbook.events import New, Cancel, read_order_flow_csv, create_event, Rejection, RejectionCode
from orderbook.order import Side

MISSING_COLUMN_ERROR_MSG = "Missing fields in order flow csv: "
DUPLICATE_COLUMN_ERROR_MSG = "Order flow csv has duplicate fields: "


@pytest.fixture
def new_valid_bid_order_event_1():
    return {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15',
            'timestamp': '1'}


@pytest.fixture
def new_valid_ask_order_event_3():
    return {'event_type': 'NEW', 'order_id': 'ORD_0003', 'side': 'ASK', 'price': '104', 'quantity': '16',
            'timestamp': '4'}


@pytest.fixture
def new_valid_cancel_order_event_3():
    return {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': '8'}


@pytest.mark.parametrize("new_order_event, order_side",
                         [("new_valid_bid_order_event_1", Side.BID), ("new_valid_ask_order_event_3", Side.ASK)])
def test_new_valid_order_event(new_order_event, order_side, request):
    new_order_event_local = request.getfixturevalue(new_order_event)

    output = create_event(new_order_event_local)

    assert isinstance(output, New)
    assert output.side == order_side
    assert output.price == int(new_order_event_local['price'])
    assert output.order_quantity == int(new_order_event_local['quantity'])
    assert output.timestamp == int(new_order_event_local['timestamp'])


@pytest.mark.parametrize("new_cancel_event",
                         ["new_valid_cancel_order_event_3"])
def test_new_valid_cancel_event(new_cancel_event, request):
    new_cancel_local = request.getfixturevalue(new_cancel_event)

    output = create_event(new_cancel_local)

    assert isinstance(output, Cancel)
    assert output.timestamp == int(new_cancel_local['timestamp'])


@pytest.mark.parametrize("new_event", [
    {'event_type': '', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': None, 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'}
])
def test_missing_event_type(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_EVENT_TYPE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'UPDATE', 'order_id': 'ORD_0001', 'side': '', 'price': '94', 'quantity': '', 'timestamp': '17'},
    {'event_type': 1, 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': '125', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'}
])
def test_unsupported_event_type(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.UNSUPPORTED_EVENT_TYPE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': '', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': None, 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'CANCEL', 'order_id': '', 'side': '', 'price': '', 'quantity': '', 'timestamp': '8'},
    {'event_type': 'CANCEL', 'order_id': None, 'side': '', 'price': '', 'quantity': '', 'timestamp': '8'}
])
def test_missing_order_id(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_ORDER_ID


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': '', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': None, 'price': '95', 'quantity': '15', 'timestamp': '1'},
])
def test_missing_side(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_SIDE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BUY', 'price': '95', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 7, 'price': '95', 'quantity': '15', 'timestamp': '1'}
])
def test_invalid_side(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.INVALID_SIDE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': None, 'quantity': '15', 'timestamp': '1'}
])
def test_missing_price(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_PRICE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': 'abc', 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': 10.5, 'quantity': '15', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '17.5', 'quantity': '15', 'timestamp': '1'}
])
def test_invalid_price(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.INVALID_PRICE


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': None, 'timestamp': '1'}
])
def test_missing_quantity(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_QUANTITY


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': 'abc', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': 10.5, 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '10.5', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '0', 'timestamp': '1'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '-15', 'timestamp': '1'}
])
def test_invalid_quantity(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.INVALID_QUANTITY


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': ''},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': None},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': ''},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': None}
])
def test_missing_timestamp(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.MISSING_TIMESTAMP


@pytest.mark.parametrize("new_event", [
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': 'abc'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': 8.5},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '10.5'},
    {'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': '15', 'timestamp': '-5'},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': 'abc'},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': 8.5},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': '8.5'},
    {'event_type': 'CANCEL', 'order_id': 'ORD_0003', 'side': '', 'price': '', 'quantity': '', 'timestamp': '-2'}
])
def test_invalid_timestamp(new_event):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == RejectionCode.INVALID_TIMESTAMP


@pytest.mark.parametrize("new_event, rejection_code", [
    ({'event_type': None, 'order_id': None, 'side': '', 'price': '95', 'quantity': '15', 'timestamp': '10'},
     RejectionCode.MISSING_EVENT_TYPE),
    ({'event_type': 'NEW', 'order_id': None, 'side': 'BID', 'price': None, 'quantity': '15', 'timestamp': '10'},
     RejectionCode.MISSING_ORDER_ID),
    ({'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': None, 'price': None, 'quantity': None, 'timestamp': None},
     RejectionCode.MISSING_TIMESTAMP),
    ({'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': None, 'price': None, 'quantity': None, 'timestamp': '10'},
     RejectionCode.MISSING_SIDE),
    ({'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': None, 'quantity': None, 'timestamp': '5'},
     RejectionCode.MISSING_PRICE),
    ({'event_type': 'NEW', 'order_id': 'ORD_0001', 'side': 'BID', 'price': '95', 'quantity': None, 'timestamp': '5'},
     RejectionCode.MISSING_QUANTITY),
    ({'event_type': 'NEW', 'order_id': 'ORD_0003', 'side': 'ASK', 'price': '105', 'quantity': '10', 'timestamp': None},
     RejectionCode.MISSING_TIMESTAMP)
])
def test_missing_multiple_fields(new_event, rejection_code):
    output = create_event(new_event)

    assert isinstance(output, Rejection)
    assert output.reason == rejection_code


def test_order_flow_output_in_order(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity,timestamp",
                  "NEW,ORD_0001,BID,95,15,1",
                  "NEW,ORD_0002,BID,98,8,3",
                  "NEW,ORD_0003,ASK,104,16,4",
                  "CANCEL,ORD_0003,,,,10"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output[0] == (2, New("ORD_0001", Side.BID, 95, 15, 1))
    assert output[1] == (3, New("ORD_0002", Side.BID, 98, 8, 3))
    assert output[2] == (4, New("ORD_0003", Side.ASK, 104, 16, 4))
    assert output[3] == (5, Cancel("ORD_0003", 10))


def test_bad_row_does_not_terminate(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity,timestamp",
                  "NEW,ORD_0001,BID,95,15,1",
                  "NEW,ORD_0002,,98,8,3",
                  "NEW,ORD_0003,ASK,104,16,4"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output[0] == (2, New("ORD_0001", Side.BID, 95, 15, 1))
    assert output[1] == (3, Rejection(RejectionCode.MISSING_SIDE))
    assert output[2] == (4, New("ORD_0003", Side.ASK, 104, 16, 4))


def test_blank_row_in_the_middle(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity,timestamp",
                  "NEW,ORD_0001,BID,95,15,1",
                  "",
                  "NEW,ORD_0003,ASK,104,16,4"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output[0] == (2, New("ORD_0001", Side.BID, 95, 15, 1))
    assert output[1] == (4, New("ORD_0003", Side.ASK, 104, 16, 4))


@pytest.mark.parametrize("order_flow", [
    ["event_type,order_id,side,price,quantity,timestamp"],
    [],
    [""]
])
def test_file_without_data(tmp_path: Path, order_flow):
    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output == []


def test_file_with_missing_column(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity",
                  "NEW,ORD_0001,BID,95,15",
                  "NEW,ORD_0002,BID,98,8",
                  "NEW,ORD_0003,ASK,104,16"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))

    with pytest.raises(KeyError, match=MISSING_COLUMN_ERROR_MSG + 'timestamp'):
        output = read_order_flow_csv(file_path)


def test_file_with_swapped_column(tmp_path: Path):
    order_flow = ["event_type,side,price,quantity,timestamp,order_id",
                  "NEW,BID,95,15,1,ORD_0001",
                  "NEW,BID,98,8,3,ORD_0002",
                  "NEW,ASK,104,16,4,ORD_0003",
                  "CANCEL,,,,10,ORD_0003"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output[0] == (2, New("ORD_0001", Side.BID, 95, 15, 1))
    assert output[1] == (3, New("ORD_0002", Side.BID, 98, 8, 3))
    assert output[2] == (4, New("ORD_0003", Side.ASK, 104, 16, 4))
    assert output[3] == (5, Cancel("ORD_0003", 10))


def test_file_with_extra_column(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity,timestamp,notes",
                  "NEW,ORD_0001,BID,95,15,1,New order",
                  "NEW,ORD_0002,BID,98,8,3,",
                  "NEW,ORD_0003,ASK,104,16,4,Test",
                  "CANCEL,ORD_0003,,,,10,Test"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))
    output = read_order_flow_csv(file_path)

    assert output[0] == (2, New("ORD_0001", Side.BID, 95, 15, 1))
    assert output[1] == (3, New("ORD_0002", Side.BID, 98, 8, 3))
    assert output[2] == (4, New("ORD_0003", Side.ASK, 104, 16, 4))
    assert output[3] == (5, Cancel("ORD_0003", 10))


def test_file_with_duplicate_column(tmp_path: Path):
    order_flow = ["event_type,order_id,price,side,price,quantity,timestamp",
                  "NEW,ORD_0001,98,BID,95,15,1,",
                  "NEW,ORD_0002,99,BID,98,8,3",
                  "NEW,ORD_0003,103,ASK,104,16,4",
                  "CANCEL,ORD_0003,,,,,10"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))

    with pytest.raises(KeyError, match=DUPLICATE_COLUMN_ERROR_MSG + 'price'):
        output = read_order_flow_csv(file_path)


def test_nonexistent_path(tmp_path: Path):
    order_flow = ["event_type,order_id,side,price,quantity,timestamp",
                  "NEW,ORD_0001,BID,95,15,1",
                  "NEW,ORD_0002,BID,98,8,3",
                  "NEW,ORD_0003,ASK,104,16,4"
                  ]

    file_path = tmp_path / 'order_flow_sample.csv'
    file_path.write_text('\n'.join(order_flow))

    with pytest.raises(FileNotFoundError):
        output = read_order_flow_csv('order_flow.csv')


def test_new_is_immutable():
    new_order = New("ORD_0001", Side.BID, 95, 15, 1)

    with pytest.raises(FrozenInstanceError):
        new_order.timestamp = 10


def test_cancel_is_immutable():
    cancel_order = Cancel("ORD_0003", 10)

    with pytest.raises(FrozenInstanceError):
        cancel_order.timestamp = 10


def test_rejection_is_immutable():
    rejection = Rejection(RejectionCode.MISSING_SIDE)

    with pytest.raises(FrozenInstanceError):
        rejection.reason = RejectionCode.INVALID_PRICE
