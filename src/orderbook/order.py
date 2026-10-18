"""Core data models for the order book: Side, Order and Trade.

Design notes:
- Prices are integers (multiples of the tick size) to avoid float
  comparison errors. Conversion to display prices happens at the edges.
- Order is mutable because its filled quantity changes on partial fills.
- Trade is immutable and refers to orders by ID, so it stays a stable
  record of what happened.
- Time priority is determined by seq_number, not timestamp.
"""

from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    """Which side of the book an order is on.

    BID is a buy order (willing to pay up to its price).
    ASK is a sell order (willing to sell at or above its price).
    """

    BID = 1
    ASK = 2


@dataclass
class Order:
    """A limit order to buy or sell a quantity at a given price or better.

    price is an integer number of ticks, not a currency amount.
    order_quantity is the original size and never changes. filled_quantity
    is how much has executed so far; remaining_quantity is what can still
    execute. Orders at the same price are served in seq_number order
    (lower first).
    """

    id: str
    side: Side
    price: int
    order_quantity: int
    timestamp: int
    seq_number: int
    filled_quantity: int = 0

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price cannot be negative or 0")

        if self.order_quantity <= 0:
            raise ValueError("Order quantity cannot be negative or 0")

        if self.filled_quantity < 0:
            raise ValueError("Filled quantity cannot be negative")

        if self.filled_quantity > self.order_quantity:
            raise ValueError("Filled quantity cannot be greater than order quantity")

    @property
    def remaining_quantity(self):
        return self.order_quantity - self.filled_quantity


@dataclass(frozen=True)
class Trade:
    """An immutable record of a match between one buy and one sell order.

    Orders are referenced by ID rather than by object, so the record does
    not change when the orders are later filled further. taker_order_id is
    the incoming order that triggered the match, and the other order is the
    resting (maker) order. price is in ticks and quantity is the amount
    executed in this single match.
    """

    id: str
    buy_order_id: str
    sell_order_id: str
    taker_order_id: str
    price: int
    quantity: int
    timestamp: int

    def __post_init__(self):
        if self.buy_order_id == self.sell_order_id:
            raise ValueError("Buyer and seller cannot be the same")

        if self.taker_order_id not in (self.buy_order_id, self.sell_order_id):
            raise ValueError("Taker order ID must be the same as either buy or sell order ID")

        if self.price <= 0:
            raise ValueError("Price cannot be negative or 0")

        if self.quantity <= 0:
            raise ValueError("Quantity cannot be negative or 0")
