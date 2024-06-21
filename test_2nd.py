import discord
import asyncio
import aiohttp
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
        print("It was an empty message!")
        return
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:]

    try:
        response = await get_response(message, user_message)
        if response:  # Ensure that we only send a message if there is a response
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
    except Exception as ex:
        print(ex)

@client.event
async def on_ready():
    print(f"{client.user} is now running!")

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
    elif "puzle" in lowered:
        await post_picture(message)
        return "Here is your puzzle!"
        # return None  # No need to send an additional text message
    elif "daily_puzzle" in lowered:
        await post_daily_puzzle(message)
        return None  # No need to send an additional text message
    else:
        return choice(["Roll dice", "Say hello", "Good bye!"])

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
    
async def fetch_daily_puzzle():
    url = 'https://lichess.org/api/puzzle/daily'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

async def post_daily_puzzle(message):
    puzzle = await fetch_daily_puzzle()
    if puzzle:
        title = puzzle['game']['name']
        url = f"https://lichess.org/training/{puzzle['puzzle']['id']}"
        fen = puzzle['puzzle']['fen']
        white_move = puzzle['puzzle']['moves'].split()[0]
        
        description = f"FEN: {fen}\nFirst Move: {white_move}"
        
        embed = discord.Embed(title=title, url=url, description=description)
        
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("Failed to fetch the daily puzzle.")

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
