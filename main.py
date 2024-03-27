# Importing necessary libraries
import discord  # Importing the Discord library
from discord import app_commands  # Importing the app_commands module from Discord
from steam import Steam  # Importing the Steam module
from decouple import config  # Importing the config function from the decouple module for managing environment variables
import asyncio  # Importing the asyncio module for handling asynchronous tasks
import json  # Importing the JSON module for working with JSON data
# Getting the Steam API key and Discord token from environment variables or .env file
KEY = config("STEAM_API_KEY")  # Retrieving the Steam API key
TOKEN = config("Discord_API_TOKEN")  # Retrieving the Discord token

# Initializing the Steam API client
steam = Steam(KEY)

# Defining the app ID for Squad (the game's ID on Steam)
squad_app_id = 393380

# Setting up Discord intents to access message content
intents = discord.Intents.all()

# Creating a Discord client
client = discord.Client(intents=intents)
intents.message_content = True

# Defining the command tree
tree = app_commands.CommandTree(client)

# Dictionary to store user information
users = {}

# Function to check the validity of a Steam ID
def check_steamid(steam_id):
    if len(steam_id) == 17 and steam_id.isdigit():
        return True
    return False

# Function to extract Steam ID from the users.json file based on Discord ID
def get_steam_id_from_json(discord_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
            if str(discord_id) in users:
                return users[str(discord_id)]["steam_id"]
    except FileNotFoundError:
        print("File users.json not found.")
    return None

# Function to retrieve playtime in Squad
def get_playtime(games, squad_app_id):
    for game in games:
        if game.get('appid') == squad_app_id:
            return game.get('playtime_forever', None)
    return None

# Loading user data from the users.json file
def load_users():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print("File users.json not found.")

# Saving user data to the users.json file
def save_users():
    global users
    with open("users.json", "w") as f:
        json.dump(users, f)

# Event handler for when the bot is ready and connected to Discord
@client.event
async def on_ready():
    print("Discord bot is running.")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    # Loading user data when the bot starts
    load_users()

# Slash command to display Squad statistics
@tree.command(name="squadstats", description="Playtime in Squad")
async def squad_command(interaction: discord.Interaction):
    # Getting the Discord user
    member = interaction.user

    # Getting the Steam ID of the user from the database
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Your Steam ID was not found in the database.")
        return

    # Getting the user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")
        return

    # Extracting the game list
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Open access to your games in privacy settings.")
        return

    # Finding Squad in the game list
    playtime_forever = get_playtime(games, squad_app_id)

    # Sending the result
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"Playtime in Squad: {playtime_hours:.1f} hours")
    else:
        await interaction.response.send_message("Squad game not found in the user's game list")

# Slash command to bind Steam ID to the profile
@tree.command(name="bindsteamid", description="Binds your Steam ID to the profile")
async def bind_command(interaction: discord.Interaction):
    global users
    
    # Checking if the user is already in the database
    if interaction.user.id in users:
        await interaction.response.send_message("Your Steam ID is already bound to the profile.")
        return
    
    # Asking for the user's Steam ID
    await interaction.response.send_message("Enter your Steam ID:")

    # Defining the check function to filter messages from the same user
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        # Waiting for the user to send their Steam ID
        steam_id_message = await client.wait_for('message', check=check, timeout=60)  # Waiting for the message for 60 seconds
    except asyncio.TimeoutError:
        await interaction.followup.send("Waiting time exceeded. Please try again.")
        return

    # Getting the Steam ID from the user's message
    steam_id = steam_id_message.content

    # Checking the validity of the Steam ID
    if not check_steamid(steam_id):
        await interaction.followup.send("Invalid Steam ID. Please enter a 17-digit numeric code.")
        return

    # Adding the user's data to the users dictionary
    users[interaction.user.id] = {
        "discord_id": interaction.user.id,
        "steam_id": steam_id,
    }

    # Saving user data to the users.json file
    save_users()

    # Sending a message about successful binding
    await interaction.followup.send(f"Your Steam ID has been successfully bound to the profile: {steam_id}")

# Slash command to unbind Steam ID from the profile
@tree.command(name="unbindsteamid", description="Unbinds your Steam ID from the profile")
async def unbind_command(interaction: discord.Interaction):
    global users

    # Checking if the Steam ID is bound to this user
    if interaction.user.id not in users:
        await interaction.response.send_message("Your Steam ID is not bound to the profile.")
        return

    # Removing the user's data from the users dictionary
    del users[interaction.user.id]

    # Saving user data to the users.json file
    save_users()

    # Sending a message about successful unbinding
    await interaction.response.send_message("Your Steam ID has been successfully unbound from the profile.")

# Slash command to show all user roles and their playtime in Squad
@tree.command(name='rank', description='Shows all user roles and their playtime in Squad')
async def show_ranks(interaction: discord.Interaction):
    # Getting the Discord user
    member = interaction.user
    
    # Getting the user's nickname
    user_name = member.name

    # Getting the list of user roles
    roles = "\n".join([role.name for role in member.roles if role.name != '@everyone'])
    
    # Getting the user's Steam ID from the database
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Your Steam ID was not found in the database.")
        return

    # Getting the user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Error retrieving user information: {e}")
        return

    # Extracting the game list
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Error: User's games not found.")
        return

    # Finding Squad in the game list
    playtime_forever = None
    for game in games:
        if game.get('appid') == squad_app_id:
            playtime_forever = game.get('playtime_forever', None)
            break

    # Forming the message to send
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        message = f"User Name: {user_name}\nUser Roles:\n{roles}\nPlaytime in Squad: {playtime_hours:.1f} hours"
    else:
        message = f"User Name: {user_name}\nUser Roles:\n{roles}\n\nError: Squad game not found in the user's game list"

    # Sending the message
    await interaction.response.send_message(message)


# Running the bot
client.run(TOKEN)

