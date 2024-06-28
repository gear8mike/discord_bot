import discord
import asyncio
import pandas as pd
from json import load
from os import path
from random import randint
from lichess import create_puzzle
from responses import post_puzzle


def load_config(filepath):
    with open(filepath, "r+") as file:
        config = load(file)
    return config


def load_csv(filepath):
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None


CURRENT_DIR = path.dirname(path.abspath(__file__))
config = load_config(path.join(CURRENT_DIR, "config.json"))

# Bot token from Discord developer portal
TOKEN = config["token"]

# ID of the channel to post the message
CHANNEL_ID = config["channelId"]

# Path to the image
# IMAGE_PATH = './puzzles/image.JPG'
IMAGE_PATH = path.join(CURRENT_DIR, "puzzle.png")

# Path to csv data base
CSV_FILEPATH = path.join(CURRENT_DIR, "puzzles", "lichess_db_puzzle.csv")
puzzles_df = load_csv(CSV_FILEPATH)

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

client = discord.Client(intents=intents)

user_states = {}  # Dictionary to store user states


async def send_message(message, user_message):
    if not user_message:
        print("It was empty message!")
        return
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]

    try:
        response = await get_response(message, user_message)
        (
            await message.author.send(response)
            if is_private
            else await message.channel.send(response)
        )
    except Exception as exept:
        print(f"Error sending message: {exept}")


@client.event
async def on_ready():
    print(f"{client.user} is now running!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    username = str(message.author)
    user_message = message.content.strip()
    channel = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    if username in user_states:
        if user_states[username] == "awaiting_rating":
            try:
                rating = int(user_message)
                if 100 <= rating <= 3000:
                    user_states[username] = "rating_received"
                    await send_message(
                        message, f"Received rating: {rating}. Generating puzzle..."
                    )
                    # create_puzzle(df=puzzles_df, type="puzzle.png", min_rating=rating-50, max_rating=rating+50)
                    create_puzzle(df=puzzles_df, type="puzzle.png", rating=rating)
                    await post_puzzle(message, path.join(CURRENT_DIR, "puzzle.png"))
                    await message.channel.send("Here is your random puzzle, enjoy!")
                else:
                    await message.channel.send(
                        "Please enter a valid rating between 100 and 3000."
                    )
            except ValueError:
                await message.channel.send(
                    "Please enter a numeric value for the rating."
                )
            del user_states[username]  # Reset the user state after handling the rating
        return

    if user_message.lower() == "/puzzle":
        user_states[username] = "awaiting_rating"
        await message.channel.send(
            "Please enter the desired rating for the puzzle (0-3000):"
        )
        return

    await send_message(message, user_message)


async def post_puzzle(message, path_to_puzzle):
    try:
        with open(path_to_puzzle, "rb") as f:
            picture = discord.File(f)
            await message.channel.send(file=picture)
            return "Here is your puzzle!"
    except FileNotFoundError:
        return f"Image file not found at {path_to_puzzle}"
    except Exception as ex:
        print(f"Failed to send image: {ex}")
        return "Failed to send image"


def print_commands(commands):
    commands_list = "List of commands:\n"
    commands_list += "\n".join(commands)
    return commands_list


async def get_response(message, user_input):
    global puzzles_df
    lowered = user_input.lower()
    list_of_commands = [
        "/help",
        "/hello",
        "/roll dice",
        "/puzzle",
        "/daily puzzle",
        "/solution",
        "/id",
        "/moves",
        "/rating",
        "/themes",
    ]
    try:
        if "/help" in lowered:
            return print_commands(list_of_commands)
        elif "/daily puzzle" in lowered:
            create_puzzle(df=puzzles_df)
            await post_puzzle(message, path.join(CURRENT_DIR, "daily_puzzle.png"))
            return "Here is the daily puzzle from lichess.org"
        elif "/hello" in lowered:
            return "Hello Buddy!"
        elif "/roll dice" in lowered:
            return f"You rolled a dice: {randint(1, 6)}"
        # elif "/puzzle" in lowered:
        #     create_puzzle(df = puzzles_df, type="puzzle.png")
        #     await post_puzzle(message, path.join(CURRENT_DIR, 'puzzle.png'))
        #     return "Here is your random puzzle, enjoy!"
        elif "/moves" in lowered:
            info = load_config(path.join(CURRENT_DIR, "puzzle.json"))
            moves = len(info["puzzle"]["solution"])
            return f"Total number of moves is {moves}, good luck!"
        elif "/id" in lowered:
            info = load_config(path.join(CURRENT_DIR, "puzzle.json"))
            id = info["puzzle"]["id"]
            return f"Puzzle ID is {id}, good luck!"
        elif "/rating" in lowered:
            info = load_config(path.join(CURRENT_DIR, "puzzle.json"))
            rating = info["puzzle"]["rating"]
            return f"Puzzle rating is {rating}, good luck!"
        elif "/themes" in lowered:
            info = load_config(path.join(CURRENT_DIR, "puzzle.json"))
            themes = info["puzzle"]["themes"]
            return f"Puzzle themes are {themes}, good luck!"
        elif "/solution" in lowered:
            await post_puzzle(message, path.join(CURRENT_DIR, "solution.png"))
            return "The right solution is here, check with your!"
    except Exception as e:
        print(f"Error in get_response: {e}")
        return "Sorry, something went wrong. Please try again."


def main():
    client.run(TOKEN)


if __name__ == "__main__":
    main()
