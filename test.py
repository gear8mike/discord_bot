import discord
import asyncio
from json import load
from os import path
from random import randint
from lichess import create_puzzle
from responses import post_puzzle

def load_config(filepath):
    with open(filepath, 'r') as file:
        config = load(file)
    return config

CURRENT_DIR = path.dirname(path.abspath(__file__))
config = load_config(path.join(CURRENT_DIR, 'config.json'))

# Bot token from Discord developer portal
TOKEN = config["token"]

# ID of the channel to post the message
CHANNEL_ID = config["channelId"]

# Path to the image
# IMAGE_PATH = './puzzles/image.JPG'
IMAGE_PATH = '*puzzle.png'

# The message to post
MESSAGE = "Hello, this is a test message from the bot!"

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

client = discord.Client(intents=intents)

async def send_message(message, user_message):
    if not user_message:
        print("It was empty message!")
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response = await get_response(message, user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as exept:
        print(exept)

@client.event
async def on_ready():
    print(f"{client.user} is now running!")
    channel = client.get_channel(CHANNEL_ID)
    if channel is not None:
        with open(IMAGE_PATH, 'rb') as f:
            picture = discord.File(f)
            await channel.send(MESSAGE, file=picture)
            print(f'Picture posted in {channel.name}')
    else:
        print(f'Channel with ID {CHANNEL_ID} not found')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


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
    commands_list = "List of commands:\n"
    commands_list += "\n".join(commands)
    return commands_list

async def get_response(message, user_input):
    lowered = user_input.lower()
    list_of_commands = ["/help", "/hello", "/roll dice", "/puzzle", "/daily puzzle", "/solution"]
    if lowered == "/help":
        return print_commands(list_of_commands)
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
    # else:
    #     return "sorry, something is wrong. Please type /help"

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
