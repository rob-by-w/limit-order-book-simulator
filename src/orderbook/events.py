"""Input events: the messages that drive the simulator.

TODO (Milestone 6):
- Define event types: NEW, CANCEL, (later) MODIFY.
- Decide what fields each event carries (e.g. NEW needs side/price/qty/id; CANCEL needs only an id).
- Define the input file format (CSV or JSON lines) and write a parser from raw rows to events.
- Edge cases: malformed rows, unknown event types, bad numbers. Fail loudly or skip? Justify the choice.
"""
import csv
import re
from dataclasses import dataclass
from enum import StrEnum

from orderbook.order import Side


class RejectionCode(StrEnum):
    MISSING_EVENT_TYPE = "missing_event_type"
    MISSING_ORDER_ID = "missing_order_id"
    MISSING_SIDE = "missing_side"
    MISSING_PRICE = "missing_price"
    MISSING_QUANTITY = "missing_quantity"
    MISSING_TIMESTAMP = "missing_timestamp"

    INVALID_SIDE = "invalid_side"
    INVALID_PRICE = "invalid_price"
    INVALID_QUANTITY = "invalid_quantity"
    INVALID_TIMESTAMP = "invalid_timestamp"

    UNSUPPORTED_EVENT_TYPE = "unsupported_event_type"


@dataclass(frozen=True)
class New:
    id: str
    side: Side
    price: int
    order_quantity: int
    timestamp: int


@dataclass(frozen=True)
class Cancel:
    id: str
    timestamp: int


@dataclass(frozen=True)
class Rejection:
    reason: RejectionCode


def is_valid_integer(input_string, minimum_value=None):
    if re.fullmatch(r'^[+-]?[0-9]+$', str(input_string)):
        output = int(input_string)

        if minimum_value is not None:
            if output >= minimum_value:
                return True
        else:
            return True

    return False


def read_order_flow_csv(order_flow_csv):
    output = []

    required_fields = ['event_type', 'order_id', 'side', 'price', 'quantity', 'timestamp']

    with open(order_flow_csv, 'r') as order_flow_file:
        if not [line for line in order_flow_file]:
            return output

    with open(order_flow_csv, newline='') as order_flow_file:
        order_reader = csv.DictReader(order_flow_file)

        if len(order_reader.fieldnames) != len(set(order_reader.fieldnames)):
            raise KeyError(f"Order flow csv has duplicate fields: {', '.join([field for field in order_reader.fieldnames if order_reader.fieldnames.count(field) > 1])}")

        if not (set(order_reader.fieldnames) >= set(required_fields)):
            raise KeyError(
                f"Missing fields in order flow csv: "
                f"{', '.join([field for field in required_fields if field not in order_reader.fieldnames])}")

        for row in order_reader:
            output.append((order_reader.line_num, create_event(row)))

    return output


def create_event(event_row):
    event_type = event_row['event_type']
    event_order_id = event_row['order_id']
    event_side = event_row['side']
    event_price = event_row['price']
    event_quantity = event_row['quantity']
    event_timestamp = event_row['timestamp']

    if not event_type:
        return Rejection(RejectionCode.MISSING_EVENT_TYPE)

    if str(event_type).upper() not in ["NEW", "CANCEL"]:
        return Rejection(RejectionCode.UNSUPPORTED_EVENT_TYPE)

    if not event_order_id:
        return Rejection(RejectionCode.MISSING_ORDER_ID)

    if not event_timestamp:
        return Rejection(RejectionCode.MISSING_TIMESTAMP)
    else:
        if is_valid_integer(str(event_timestamp).strip(), 0):
            event_timestamp = int(event_timestamp)

        else:
            return Rejection(RejectionCode.INVALID_TIMESTAMP)

    if event_type.strip().upper() == 'NEW':
        if not event_side:
            return Rejection(RejectionCode.MISSING_SIDE)
        else:
            if not isinstance(event_side, str):
                return Rejection(RejectionCode.INVALID_SIDE)

            if event_side.strip().upper() not in ["BID", "ASK"]:
                return Rejection(RejectionCode.INVALID_SIDE)

            event_side = Side.BID if event_side.strip().upper() == "BID" else Side.ASK

        if not event_price:
            return Rejection(RejectionCode.MISSING_PRICE)
        else:
            if is_valid_integer(str(event_price).strip()):
                event_price = int(event_price)
            else:
                return Rejection(RejectionCode.INVALID_PRICE)

        if not event_quantity:
            return Rejection(RejectionCode.MISSING_QUANTITY)
        else:
            if is_valid_integer(str(event_quantity).strip(), 1):
                event_quantity = int(event_quantity)

            else:
                return Rejection(RejectionCode.INVALID_QUANTITY)

        return New(
            id=event_order_id.strip(),
            side=event_side,
            price=event_price,
            order_quantity=event_quantity,
            timestamp=event_timestamp
        )
    elif event_type.strip().upper() == 'CANCEL':
        return Cancel(
            id=event_order_id.strip(),
            timestamp=event_timestamp,
        )
    else:
        return Rejection(RejectionCode.UNSUPPORTED_EVENT_TYPE)
