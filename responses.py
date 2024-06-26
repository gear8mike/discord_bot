import discord
from random import randint
from os import path
from lichess import create_puzzle



CURRENT_DIR = path.dirname(path.abspath(__file__))

async def post_puzzle(message, path_to_puzzle):
    try:
        with open(path_to_puzzle, 'rb') as f:
            picture = discord.File(f)
            await message.channel.send(file=picture)
            return "Here is your puzzle!"
    except FileNotFoundError:
        return f'Image file not found at {path_to_puzzle}'
    except Exception as ex:
        print(f'Failed to send image: {ex}')
        return "Failed to send image"

def print_commands(commands):
    print("List of commands:")
    for command in commands:
        print(command)
    return None

async def get_response(message, user_input):
    lowered = user_input.lower()
    list_of_commands = ["/help", "/hello", "/roll dice", "/puzzle", "/daily puzzle", "/solution"]
    if lowered == "/help":
        print_commands(list_of_commands)
    elif "/daily puzzle" in lowered:
        create_puzzle()
        await post_puzzle(message, path.join(CURRENT_DIR, 'daily_puzzle.png'))
        return "Here is the daily puzzle from lichess.org"
    elif "/hello" in lowered:
        return "Hello Buddy!"
    elif "/roll_dice" in lowered:
        return f"You rolled a dice: {randint(1, 6)}"
    elif "/puzzle" in lowered:
        create_puzzle(type="puzzle.png")
        await post_puzzle(message, path.join(CURRENT_DIR, 'puzzle.png'))
        return "Here is your puzzle, enjoy!"
    elif "/solution" in lowered:
        await post_puzzle(message, path.join(CURRENT_DIR, 'solution.png'))
        return "The right solution is here, check with your!"
    else:
        return "sorry, something is wrong. Please type /help"