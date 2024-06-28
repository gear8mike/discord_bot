import requests
import chess
import chess.svg
import chess.pgn
from cairosvg import svg2png
from json import load, dump
from os import path
from io import StringIO
import pandas as pd


def load_config(filepath):
    with open(filepath, "r") as file:
        config = load(file)
    return config


CURRENT_DIR = path.dirname(path.abspath(__file__))
config = load_config(path.join(CURRENT_DIR, "config.json"))
# Set your Lichess API token here
API_TOKEN = config["token_lichess"]


# Function to get the daily puzzle from Lichess
def get_puzzle(api_token, puzzle_id="daily"):
    url = "https://lichess.org/api/puzzle/" + puzzle_id
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# Function to get the solution from the daily puzzle
def get_solution(puzzle, initial_ply):
    solution_moves = puzzle["puzzle"]["solution"]
    pgn = puzzle["game"]["pgn"]
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()

    for move in list(game.mainline_moves())[:initial_ply]:
        board.push(move)

    for move in solution_moves:
        move_obj = chess.Move.from_uci(move)
        board.push(move_obj)

    return board.fen()


# Function to get a random puzzle from CSV file within a rating range
def get_random_puzzle_from_csv(df, min_rating, max_rating):
    # df = pd.read_csv(filepath)
    filtered_puzzles = df[(df["Rating"] >= min_rating) & (df["Rating"] <= max_rating)]
    if filtered_puzzles.empty:
        raise ValueError(
            f"No puzzles found with Rating between {min_rating} and {max_rating}"
        )
    return filtered_puzzles.sample(n=1).iloc[0]


# Function to create a chessboard image from FEN string
def create_chessboard_image(fen, output_file, size=800, flipped=False):
    board = chess.Board(fen)
    svg_board = chess.svg.board(
        board,
        size=size,
        colors={
            "square light": "#E2F9DD",  # white
            "square dark": "#80A379",  # dark green
        },
        orientation=chess.BLACK if flipped else chess.WHITE,
    )
    svg2png(bytestring=svg_board, write_to=output_file)


# Main function
def create_puzzle(df, type="daily_puzzle.png", rating= 1800):
    # Get the daily puzzle
    if type == "daily_puzzle.png":
        puzzle = get_puzzle(API_TOKEN)
    else:
        # csv_filepath=path.join(CURRENT_DIR, "puzzles", "lichess_db_puzzle.csv")
        puzzle_random = get_random_puzzle_from_csv(df,rating - 100, rating + 100)
        puzzle_id = str(puzzle_random['PuzzleId'])
        print(f'Chosen PuzzleId: {puzzle_id}')
        puzzle = get_puzzle(API_TOKEN, puzzle_id=puzzle_id)

    # Save the JSON data to a file
    json_output_file = path.join(CURRENT_DIR, "puzzle.json")
    with open(json_output_file, "w") as json_file:
        dump(puzzle, json_file, indent=4)
    print(f"The puzzle JSON saved as {json_output_file}")

    # Parse the PGN to get the initial board position
    pgn = puzzle["game"]["pgn"]
    initial_ply = puzzle["puzzle"]["initialPly"] + 1

    # Read the PGN and get the board position at the given ply
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()

    for move in list(game.mainline_moves())[:initial_ply]:
        board.push(move)

    # Determine if the board should be flipped
    flipped = board.turn == chess.BLACK

    # Get the FEN string for the position at initial_ply
    puzzle_fen = board.fen()

    # Create the chessboard image with higher resolution
    create_chessboard_image(puzzle_fen, type, size=800, flipped=flipped)
    print(f"Your puzzle image saved as {type}")

    # Get the final position after the solution and save it
    final_solution_fen = get_solution(puzzle, initial_ply)
    output_file_solution = "solution.png"
    create_chessboard_image(
        final_solution_fen, output_file_solution, size=800, flipped=flipped
    )
    print(f"Final solution image saved as {output_file_solution}")


# def create_random_puzzle_from_csv(
#     csv_filepath=path.join(CURRENT_DIR, "puzzles", "lichess_db_puzzle.csv"),
#     output_file="puzzle.png",
#     solution_file="solution.png",
# ):
#     # Get a random puzzle from the CSV file within the specified rating range
#     puzzle = get_random_puzzle_from_csv(csv_filepath)

#     # Print the PuzzleId
#     puzzle_id = puzzle['PuzzleId']
#     print(f'Chosen PuzzleId: {puzzle_id}')

#     # Extract puzzle details
#     fen = puzzle["FEN"]
#     solution_moves = puzzle["Moves"].split()

#     # Create the chessboard image with higher resolution
#     flipped = chess.Board(fen).turn == chess.BLACK
#     create_chessboard_image(fen, output_file, size=800, flipped=flipped)
#     print(f"Puzzle image saved as {output_file}")

#     # Apply the solution moves to the board
#     board = chess.Board(fen)
#     for move in solution_moves:
#         move_obj = chess.Move.from_uci(move)
#         board.push(move_obj)

#     # Create the final solution image
#     final_solution_fen = board.fen()
#     create_chessboard_image(
#         final_solution_fen, solution_file, size=800, flipped=flipped
#     )
#     print(f"Solution image saved as {solution_file}")


# Example usage
# create_daily_puzzle()  # For daily puzzle
# create_random_puzzle_from_csv('lichess_db_puzzle.csv')

# if __name__ == "__main__":
#     main()
