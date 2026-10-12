"""Input events: the messages that drive the simulator.

TODO (Milestone 6):
- Define event types: NEW, CANCEL, (later) MODIFY.
- Decide what fields each event carries (e.g. NEW needs side/price/qty/id; CANCEL needs only an id).
- Define the input file format (CSV or JSON lines) and write a parser from raw rows to events.
- Edge cases: malformed rows, unknown event types, bad numbers. Fail loudly or skip? Justify the choice.
"""
