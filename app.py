# Import required modules
import discord
from discord.ext import commands
import sqlite3
from functions import *
import json

with open("env.json", "r") as file:
    env_keys = json.load(file)

    bot_token = env_keys.get("botToken")
    print(bot_token)

# Intents configuration for the bot
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='/', intents=intents)

# Establish SQLite Database Connection
conn = sqlite3.connect('items.db')
c = conn.cursor()

# Creating table if not exists, magical column removed
c.execute('''CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL
)''')
conn.commit()

# Bot event for when it's ready
@bot.event
async def on_ready():
      # Use your channel ID here
    global channel
    channel = bot.get_channel(836424457954263080) #party inventory
    # channel = bot.get_channel(1156005749818933361) #bot
    print("Bot is ready.")

@bot.command()
async def populate(ctx):
    await display_table(channel)

# Register commands and events
bot.add_command(addItem)
bot.add_command(removeItem)
bot.add_command(updateQuantity)
bot.add_command(updateName)
bot.add_command(updateCategory)
bot.event(on_ready)

# Start the bot
bot.run(bot_token) 
