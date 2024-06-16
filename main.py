import discord
import asyncio
from json import load
from os import path

def load_config(filepath):
    with open(filepath, 'r') as file:
        config = load(file)
    return config

CURRENT_DIR =path.dirname(path.abspath(__file__))

config = load_config(path.join(CURRENT_DIR, 'config.json'))

# bot token from discord dev
TOKEN = config["token"]

# ID of chess channel
CHANNEL_ID = config["channelId"]

# Replace 'path/to/your/image.jpg' with the path to your image
IMAGE_PATH = './puzzles/image.JPG'

# The message you want to post
MESSAGE = "Hello, this is a test message from the bot!"

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        channel = self.get_channel(CHANNEL_ID)
        if channel is not None:
            with open(IMAGE_PATH, 'rb') as f:
                picture = discord.File(f)
                await channel.send(file=picture)
                print(f'Picture posted in {channel.name}')
        else:
            print(f'Channel with ID {CHANNEL_ID} not found')

        await self.close()

client = MyClient(intents=intents)

client.run(TOKEN)