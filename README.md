# Limit Order Book Simulator

A limit order book simulator in Python. It reads a stream of order events from a CSV file, maintains a book with
price-time priority, matches crossing orders, and reports the trades, rejected lines, and the final book state.

Built as a learning project to understand the data structures and matching rules behind electronic trading and
market-making systems.

## Features

**Implemented**

- Limit orders with price-time priority (FIFO within each price level)
- Cancel by order id
- Matching engine with partial fills and multi-level sweeps
- Trades execute at the resting order's price
- Book queries: best bid, best ask, spread, depth
- CSV event stream processing with validation and per-line rejections
- Command-line entry point with trade, rejection, and book snapshot output
- pytest suite covering the order models, book, event parsing, matching, and end-to-end simulation

**Planned**

- Market orders, IOC / FOK
- Order modify (`UPDATE` events are currently rejected as `unsupported_event_type`)
- L2 snapshot output and simple visualization
- Benchmarks
- Heap compaction (see [Design decisions](#design-decisions))

## Install and run

Requires Python 3.11+ (uses `enum.StrEnum`). Developed and tested on Python 3.14.8.

```bash
git clone https://github.com/rob-by-w/limit-order-book-simulator.git
cd limit-order-book-simulator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Run the simulator on a sample stream:

```bash
python -m orderbook data/sample_orders.csv
```

## Example

Input (`data/sample_orders.csv`):

```csv
event_type,order_id,side,price,quantity,timestamp
NEW,ORD_0001,BID,95,15,1
NEW,ORD_0002,BID,98,8,3
NEW,ORD_0002,BID,99,12,4
NEW,ORD_0003,ASK,104,16,4
NEW,ORD_0002,ASK,97,3,5
NEW,ORD_0004,ASK,104,6,5
NEW,ORD_0005,BID,105,6,7
CANCEL,ORD_0003,,,,8
NEW,ORD_0006,,123,8,10
NEW,ORD_0006,ASK,95,11,10
CANCEL,ORD_1111,,,,11
CANCEL,ORD_0002,,,,13
NEW,ORD_0007,BID,105,30,15
NEW,ORD_0008,ASK,106,8,14
NEW,ORD_1112,ASK,ASK,8,16
UPDATE,ORD_0001,,94,,17
```

Output:

```text
Input file: data/sample_orders.csv

=====Simulation result=====

---Trades---
ID: TRD_0001, Buyer: ORD_0005, Seller: ORD_0003, Quantity: 6, Price: 104
ID: TRD_0002, Buyer: ORD_0002, Seller: ORD_0006, Quantity: 8, Price:  98
ID: TRD_0003, Buyer: ORD_0001, Seller: ORD_0006, Quantity: 3, Price:  95
ID: TRD_0004, Buyer: ORD_0007, Seller: ORD_0004, Quantity: 6, Price: 104

---Rejections---
Line number:  4, Reason: duplicate_order_id
Line number:  6, Reason: duplicate_order_id
Line number: 10, Reason: missing_side
Line number: 12, Reason: unknown_order_id
Line number: 13, Reason: unknown_order_id
Line number: 16, Reason: invalid_price
Line number: 17, Reason: unsupported_event_type

---Book Snapshot---
  Bid Quantity  |   Bid Price    |   Ask Price    |  Ask Quantity
                |                |      106       |       8
       24       |      105       |                |
       12       |       95       |                |
```

Prices and quantities are shown as raw integer ticks.

## Input format

CSV with a header row and these columns:

| Column       | Description                                 |
|--------------|---------------------------------------------|
| `event_type` | `NEW` or `CANCEL`                           |
| `order_id`   | Unique order identifier                     |
| `side`       | `BID` or `ASK`                              |
| `price`      | Integer price in ticks                      |
| `quantity`   | Integer quantity                            |
| `timestamp`  | Integer timestamp (epoch format is assumed) |

- `NEW` rows need all six columns. `CANCEL` rows only need `event_type`, `order_id`, and `timestamp`; any other
  fields on a `CANCEL` row are accepted and ignored.
- Columns may appear in any order, and extra columns are ignored. Duplicate column names are rejected.
- Events are processed in **file order**. Arrival order, not the `timestamp` value, determines time priority. The
  timestamp is only validated as an integer.
- Line numbers in rejections count the header row, so the first data row is line 2.
- Invalid lines are not dropped silently. Each is reported as a rejection with a line number and a reason code.
- Empty input (a zero-byte file, or a header with no rows) is a valid run that produces an empty result.

### Rejection codes

Rejected while parsing and validating a line:

| Code                                                                                                               | Meaning                          |
|--------------------------------------------------------------------------------------------------------------------|----------------------------------|
| `missing_event_type`, `missing_order_id`, `missing_side`, `missing_price`, `missing_quantity`, `missing_timestamp` | A required field is empty        |
| `invalid_side`, `invalid_price`, `invalid_quantity`, `invalid_timestamp`                                           | A field has an unusable value    |
| `unsupported_event_type`                                                                                           | Event type is not `NEW`/`CANCEL` |

Rejected by the book while processing a valid line:

| Code                 | Meaning                                             |
|----------------------|-----------------------------------------------------|
| `duplicate_order_id` | A `NEW` reuses an order id already seen in this run |
| `unknown_order_id`   | A `CANCEL` names an order that is not resting       |

Sample streams in `data/`:

| File                            | Purpose                                                  |
|---------------------------------|----------------------------------------------------------|
| `sample_orders.csv`             | Mixed stream: trades, rejections, non-empty final book   |
| `sample_orders_with_errors.csv` | Rows with invalid format                                 |
| `sample_full_filled_orders.csv` | One bid fully filled by one ask; ends with an empty book |
| `sample_header_only.csv`        | Header with no rows                                      |
| `sample_empty_zero_byte.csv`    | Intentionally 0 bytes                                    |

## Design decisions

### Price levels: dict of dicts, plus a heap of prices

Each side keeps a dict of `price -> level`, and each level is a dict of `order id -> Order`. A separate index maps
`order id -> Order`, so cancel finds an order without scanning.

### Lazy deletion for price heaps

Each side keeps a heap of prices for fast best-price lookup, while the dict of price levels is the source of truth.
Cancels remove the order from its level (and the level if empty) without touching the heap, making cancel O(1) on
average. Stale heap entries are discarded when they reach the top during `best_bid()` / `best_ask()`, so each is popped
once at O(log n).

The trade-off: stale entries can accumulate between lookups, increasing memory, and a single lookup can occasionally be
slow after a burst of cancels (amortized cheap, spiky worst case). Periodic heap compaction is listed under future work.

### Time priority within a level

Each price level is an insertion-ordered dict of order id to order. Orders are processed sequentially in arrival order,
so insertion order is time priority and the oldest order is always first. Compared to a list, this gives O(1) cancel by
id instead of an O(n) scan and shift.

A partial fill mutates the resting order's remaining quantity in place, so it keeps its queue position. Only a full fill
removes the order from its level and from the id index.

### Integer ticks for price

Prices are stored as integer multiples of the tick size, never floats. Price levels are dict keys and crossing is
decided by price comparison, so two prices that should be equal must be exactly equal. Floats can differ in the last
bit (e.g. `0.1 + 0.2 != 0.3`), which would split one level into two or misjudge a crossing. Integers also make spread
and depth arithmetic exact. Real exchanges use fixed-point or integer prices for the same reason.

### Matching

An incoming limit order matches against the opposite side while the book is crossed (bid price ≥ best ask, or ask
price ≤ best bid), walking price levels from best to worst and orders within a level in time priority. Each trade
executes at the resting order's price. Fully filled resting orders are removed from their level and the id index;
partially filled ones are updated in place. Any unfilled remainder rests at the order's own limit price, at the back of
that level's queue.

After every event, either the best bid is strictly below the best ask or one side is empty.

### Separation of engine and presentation

`Simulator.run()` returns a `SimulationResult` containing trades, rejections, and an immutable snapshot of book depth.
All printing lives in `__main__.py`, so the engine is easy to test and reuse.

## Tests

```bash
pip install pytest
python -m pytest
```

The suite lives in `tests/`, with one file per module:

| File                | Covers                                                         |
|---------------------|----------------------------------------------------------------|
| `test_order.py`     | Order, side, and level data models                             |
| `test_book.py`      | Add, cancel, best bid/ask, spread, depth                       |
| `test_events.py`    | CSV parsing, validation, and rejection codes                   |
| `test_matching.py`  | Crossing, partial fills, multi-level sweeps                    |
| `test_simulator.py` | End-to-end runs, rejections, snapshots, arrival-order priority |

## Project structure

```text
src/orderbook/
  order.py       Order, Side, Level, Trade data models
  book.py        OrderBook: levels, cancel, best bid/ask, spread, depth
  matching.py    Matching engine for crossing limit orders
  events.py      CSV parsing, validation, rejections
  simulator.py   Runs an event stream, returns SimulationResult
  __main__.py    Command-line entry point
tests/           pytest suite
data/            Sample order streams
```

## Future work

- Test that `best bid < best ask` holds after every event in a stream
- Benchmarks (orders/second, cancel latency)
- Market orders, IOC / FOK, modify
- Heap compaction
- L2 snapshot output and visualization

## Releases

| Tag    | Milestone                  |
|--------|----------------------------|
| v0.1.0 | Core models                |
| v0.2.0 | Order book                 |
| v0.3.0 | Matching engine            |
| v0.4.0 | Event parser and simulator |
| v0.5.0 | CLI entry point            |