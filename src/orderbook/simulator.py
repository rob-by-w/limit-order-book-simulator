"""Simulator: feeds a stream of events into the book and collects output.

TODO (Milestone 6):
- Read events in order (sequence matters: it defines time priority).
- Dispatch each event to the book / matching engine.
- Collect and expose emitted trades.
- Optionally print/log top-of-book after each event.
- Provide a command-line entry point that takes a path to a sample stream in data/.
"""
