import discord
import asyncio
from json import load
from os import path
from random import choice, randint

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
IMAGE_PATH = './puzzles/image.JPG'

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
        response = get_response(user_message)
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

async def get_response(message, user_input):
    lowered = user_input.lower()
    if lowered == "":
        return "You are silent ....zzzzz"
    elif "hello" in lowered:
        return "Hello Buddy!"
    elif "roll dice" in lowered:
        return f"You rolled a dice: {randint(1, 6)}"
    elif "puzzle" in lowered:
        await post_picture(message)
        return None  # No need to send an additional text message
    # else:
    #     return choice(["Roll dice", "Say hello", "Good bye!"])

async def post_picture(message):
    try:
        with open(IMAGE_PATH, 'rb') as f:
            picture = discord.File(f)
            await message.channel.send(file=picture)
            return "Here is your puzzle!"
    except FileNotFoundError:
        return f'Image file not found at {IMAGE_PATH}'
    except Exception as ex:
        print(f'Failed to send image: {ex}')
        return "Failed to send image"

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()





