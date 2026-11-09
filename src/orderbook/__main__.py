import argparse
import pathlib

from orderbook.events import read_order_flow_csv
from orderbook.simulator import Simulator


def read_user_input():
    parser = argparse.ArgumentParser(description='Orderbook CLI')
    parser.add_argument("input_file", type=pathlib.Path)

    args = parser.parse_args()

    if not args.input_file.exists():
        parser.error(f"{args.input_file} does not exist")

    if args.input_file.suffix.lower() != ".csv":
        parser.error(f"{args.input_file} is not a .csv file")

    return args.input_file


def print_output_trades(simulation_result_trade):
    print(f"{'=' * 5}Simulation result{'=' * 5}\n")
    print(f"{'-' * 3}Trades{'-' * 3}")
    if len(simulation_result_trade) == 0:
        print("No trades executed")
    else:
        max_quantity_digit = max(len(str(trade.quantity)) for trade in simulation_result_trade)
        max_price_digit = max(len(str(trade.price)) for trade in simulation_result_trade)
        for trade in simulation_result_trade:
            print(
                f"ID: {trade.id}, Buyer: {trade.buy_order_id}, Seller: {trade.sell_order_id}, Quantity: "
                f"{str(trade.quantity).rjust(max_quantity_digit)}, "
                f"Price: {str(trade.price).rjust(max_price_digit)}")

    print()


def print_output_rejections(simulation_result_rejection):
    print(f"{'-' * 3}Rejections{'-' * 3}")
    if len(simulation_result_rejection) == 0:
        print("No rejections found, all lines are accepted")
    else:
        max_line_number_digit = max(len(str(rejection.line_number)) for rejection in simulation_result_rejection)
        for rejection in simulation_result_rejection:
            print(f"Line number: {str(rejection.line_number).rjust(max_line_number_digit)}, Reason: {rejection.reason}")

    print()


def print_output_book_state(simulation_result_book_state):
    print(f"{'-' * 3}Book Snapshot{'-' * 3}")
    bid_level = simulation_result_book_state.bids
    ask_level = simulation_result_book_state.asks

    max_digit_to_print = max(
        [bid.price for bid in bid_level] + [bid.quantity for bid in bid_level] + [ask.price for ask in ask_level] + [
            ask.quantity for ask in ask_level], default=0)
    col_width = max(16, len(str(max_digit_to_print)) + 2)

    print(
        f"{'Bid Quantity':^{col_width}}|{'Bid Price':^{col_width}}|{'Ask Price':^{col_width}}|"
        f"{'Ask Quantity':^{col_width}}")

    if not bid_level and not ask_level:
        print(f"{'':^{col_width}}|{'':^{col_width}}|{'':^{col_width}}|{'':^{col_width}}")

    for ask in reversed(ask_level):
        print(f"{'':^{col_width}}|{'':^{col_width}}|{str(ask.price):^{col_width}}|{str(ask.quantity):^{col_width}}")

    for bid in bid_level:
        print(f"{str(bid.quantity):^{col_width}}|{str(bid.price):^{col_width}}|{'':^{col_width}}|{'':^{col_width}}")


if __name__ == "__main__":
    input_file = read_user_input()
    print(f"Input file: {input_file}\n")

    input_events = read_order_flow_csv(input_file)

    simulator = Simulator()
    simulation_result = simulator.run(input_events)

    print_output_trades(simulation_result.trades)
    print_output_rejections(simulation_result.rejections)
    print_output_book_state(simulation_result.book_state)
