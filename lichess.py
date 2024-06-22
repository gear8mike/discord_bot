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

# Function to create a chessboard image from FEN string
def create_chessboard_image(fen, output_file, size=800):
    board = chess.Board(fen)
    svg_board = chess.svg.board(
        board, 
        size=size,
        colors={
            'square light': '#FFFFFF',  # white
            'square dark': '#97a976',  # black
            # 'square dark': '#0000FF',   # blue
        }
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
    initial_ply = daily_puzzle['puzzle']['initialPly']
    
    # Read the PGN and get the board position at the given ply
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    
    for move in list(game.mainline_moves())[:initial_ply]:
        print(move)
        board.push(move)
    
    # Get the FEN string for the position at initial_ply
    puzzle_fen = board.fen()
    
    # Define the output image file
    output_file = 'daily_puzzle.png'
    
    # Create the chessboard image with higher resolution
    create_chessboard_image(puzzle_fen, output_file, size=800)
    print(f'Daily puzzle image saved as {output_file}')

if __name__ == "__main__":
    main()
