import requests
import chess
import chess.svg
import chess.pgn
from cairosvg import svg2png
from json import load, dump
from os import path
from io import StringIO

def load_config(filepath):
    with open(filepath, 'r') as file:
        config = load(file)
    return config

CURRENT_DIR = path.dirname(path.abspath(__file__))
config = load_config(path.join(CURRENT_DIR, 'config.json'))
# Set your Lichess API token here
API_TOKEN = config['token_lichess']

# Function to get the daily puzzle from Lichess
def get_daily_puzzle(api_token):
    url = "https://lichess.org/api/puzzle/daily"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Function to get the solution from the daily puzzle
def get_solution(daily_puzzle, initial_ply):
    solution_moves = daily_puzzle['puzzle']['solution']
    pgn = daily_puzzle['game']['pgn']
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    
    for move in list(game.mainline_moves())[:initial_ply]:
        board.push(move)
    
    for move in solution_moves:
        move_obj = chess.Move.from_uci(move)
        board.push(move_obj)
    
    return board.fen()

# Function to create a chessboard image from FEN string
def create_chessboard_image(fen, output_file, size=800, flipped=False):
    board = chess.Board(fen)
    svg_board = chess.svg.board(
        board, 
        size=size,
        colors={
            'square light': '#E2F9DD',  # white
            'square dark': '#80A379',  # dark green
        },
        orientation=chess.BLACK if flipped else chess.WHITE
    )
    svg2png(bytestring=svg_board, write_to=output_file)

# Main function
def main():
    # Get the daily puzzle
    daily_puzzle = get_daily_puzzle(API_TOKEN)

    # Save the JSON data to a file
    json_output_file = path.join(CURRENT_DIR, 'daily_puzzle.json')
    with open(json_output_file, 'w') as json_file:
        dump(daily_puzzle, json_file, indent=4)
    print(f'Daily puzzle JSON saved as {json_output_file}')
    
    # Parse the PGN to get the initial board position
    pgn = daily_puzzle['game']['pgn']
    initial_ply = daily_puzzle['puzzle']['initialPly'] + 1
    
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
    
    # Define the output image file for the initial puzzle position
    output_file = 'daily_puzzle.png'
    
    # Create the chessboard image with higher resolution
    create_chessboard_image(puzzle_fen, output_file, size=800, flipped=flipped)
    print(f'Daily puzzle image saved as {output_file}')

    # Get the final position after the solution and save it
    final_solution_fen = get_solution(daily_puzzle, initial_ply)
    output_file_solution = 'final_solution.png'
    create_chessboard_image(final_solution_fen, output_file_solution, size=800, flipped=flipped)
    print(f'Final solution image saved as {output_file_solution}')

if __name__ == "__main__":
    main()

