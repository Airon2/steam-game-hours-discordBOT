import discord  # Importing the Discord library
from discord import app_commands  # Importing app_commands module from discord
from steam import Steam  # Importing Steam class from the steam module
from decouple import config  # Importing config function from the decouple module for reading environment variables
import asyncio  # Importing asyncio for asynchronous operations
import json  # Importing json module for working with JSON data

# Retrieving API key for Steam and Discord token from environment variables or .env file
KEY = config("STEAM_API_KEY")  # Retrieving Steam API key
TOKEN = config("Discord_API_TOKEN")  # Retrieving Discord API token

# Initializing Steam API client with the provided API key
steam = Steam(KEY)

# Defining app ID for Squad (the game ID on Steam)
squad_app_id = 393380
RON_app_id = 1144200

# List of allowed channel IDs where commands can be executed
allowed_channel_ids = [1111391658026729483, 591661218410790912]

# Setting up Discord intents to access message content
intents = discord.Intents.all()

# Creating a Discord client instance with specified intents
client = discord.Client(intents=intents)
intents.message_content = True  # Enabling message content intent

# Creating a command tree for managing slash commands with the Discord client
tree = app_commands.CommandTree(client)

# Dictionary to store user information
users = {}

# Function to check if a channel ID is allowed
def is_allowed_channel(channel_id):
    return channel_id in allowed_channel_ids

# Function to validate a Steam ID format
def check_steamid(steam_id):
    if len(steam_id) == 17 and steam_id.isdigit():
        return True
    return False

# Function to retrieve Steam ID from users.json file based on Discord ID
def get_steam_id_from_json(discord_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
            if str(discord_id) in users:
                return users[str(discord_id)]["steam_id"]
    except FileNotFoundError:
        print("File users.json not found.")
    return None

# Function to retrieve playtime in Squad from user's game list
def get_playtime(games, squad_app_id):
    for game in games:
        if game.get('appid') == squad_app_id:
            return game.get('playtime_forever', None)
    return None

def get_ron_playtime(games, RON_app_id):
    for game in games:
        if game.get('appid') == RON_app_id:
            return game.get('playtime_forever', None)
    return None

# Function for assigning a role based on playtime hours in Squad
async def assign_role_based_on_playtime(guild, member, squad_playtime_hours):
    role_to_assign = None

    if squad_playtime_hours >= 2000:
        role_to_assign = discord.utils.get(guild.roles, name="🔱Army General")
    elif squad_playtime_hours >= 1000:
        role_to_assign = discord.utils.get(guild.roles, name="🔱Colonel General")
    elif squad_playtime_hours >= 800:
        role_to_assign = discord.utils.get(guild.roles, name="🏵️Colonel")
    elif squad_playtime_hours >= 700:
        role_to_assign = discord.utils.get(guild.roles, name="🏵️Lieutenant Colonel")
    elif squad_playtime_hours >= 500:
        role_to_assign = discord.utils.get(guild.roles, name="🌟Major")
    elif squad_playtime_hours >= 400:
        role_to_assign = discord.utils.get(guild.roles, name="🌟Captain")
    elif squad_playtime_hours >= 350:
        role_to_assign = discord.utils.get(guild.roles, name="⭐Senior Lieutenant")
    elif squad_playtime_hours >= 300:
        role_to_assign = discord.utils.get(guild.roles, name="⭐Lieutenant")
    elif squad_playtime_hours >= 250:
        role_to_assign = discord.utils.get(guild.roles, name="🔰Senior Sergeant")
    elif squad_playtime_hours >= 100:
        role_to_assign = discord.utils.get(guild.roles, name="🔰Sergeant")
    elif squad_playtime_hours >= 50:
        role_to_assign = discord.utils.get(guild.roles, name="Private")
    
    if role_to_assign:
        # Check if the user already has this role
        if role_to_assign not in member.roles:
            try:
                # Remove previous roles based on conditions
                roles_to_remove = [
                    discord.utils.get(guild.roles, name="Private"),
                    discord.utils.get(guild.roles, name="🔰Sergeant"),
                    discord.utils.get(guild.roles, name="🔰Senior Sergeant"),
                    discord.utils.get(guild.roles, name="⭐Lieutenant"),
                    discord.utils.get(guild.roles, name="⭐Senior Lieutenant"),
                    discord.utils.get(guild.roles, name="🌟Captain"),
                    discord.utils.get(guild.roles, name="🌟Major"),
                    discord.utils.get(guild.roles, name="🏵️Lieutenant Colonel"),
                    discord.utils.get(guild.roles, name="🏵️Colonel"),
                    discord.utils.get(guild.roles, name="🔱Colonel General"),
                    discord.utils.get(guild.roles, name="🔱Army General")
                ]
                roles_to_remove = [role for role in roles_to_remove if role is not None]
                await member.remove_roles(*roles_to_remove)
                
                # Add the new role
                await member.add_roles(role_to_assign)
                print(f"Role '{role_to_assign.name}' assigned to {member.name}")
            except discord.HTTPException as e:
                print(f"Failed to assign role to {member.name}: {e}")
    else:
        print("No role assigned based on Squad playtime.")

# Loading user data from users.json file
def load_users():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print("File users.json not found.")

# Saving user data to users.json file
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
    # Load user data when the bot starts
    load_users()

# Slash command to display Squad statistics
@tree.command(name="squadstats", description="Displays playtime in Squad")
async def squad_command(interaction: discord.Interaction):
    # Check if the command was sent from an allowed channel
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("This command is only available in 🤖bot-chat.")
        return
    
    # Get Discord user
    member = interaction.user

    # Get Steam ID of the user from the database
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Your Steam ID is not found in the database.")
        return

    # Get user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")
        return

    # Extract game list
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Access to your game data is restricted.")
        return

    # Find Squad in the game list
    playtime_forever = get_playtime(games, squad_app_id)

    # Display the result
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"Squad playtime: {playtime_hours:.1f} hours")
    else:
        await interaction.response.send_message("Squad is not in your game list")

# Slash command to bind Steam ID to user profile
@tree.command(name="bindsteamid", description="Binds your Steam ID to your profile")
async def bind_command(interaction: discord.Interaction):
    global users
    
    # Check if the command was sent from an allowed channel
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("This command is only available in 🤖bot-chat.")
        return
    
    # Check if the user already has a bound Steam ID
    if get_steam_id_from_json(interaction.user.id):
        await interaction.response.send_message("Your Steam ID is already bound to your profile.")
        return
    
    # Ask for user's Steam ID
    await interaction.response.send_message("Enter your Steam ID:")

    # Define a check function to filter messages from the same user
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        # Wait for the user to send their Steam ID
        steam_id_message = await client.wait_for('message', check=check, timeout=60)  # Wait for a message for up to 60 seconds
    except asyncio.TimeoutError:
        await interaction.followup.send("Timeout reached. Please try again.")
        return

    # Get Steam ID from the user's message
    steam_id = steam_id_message.content

    # Validate the Steam ID
    if not check_steamid(steam_id):
        await interaction.followup.send("Invalid Steam ID. Please enter a 17-digit numeric code.")
        return

    # Add user data to the users dictionary
    users[interaction.user.id] = {
        "discord_id": interaction.user.id,
        "steam_id": steam_id,
    }

    # Save user data to users.json file
    save_users()

    # Send a message indicating successful binding
    await interaction.followup.send(f"Your Steam ID has been successfully bound: {steam_id}")

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

@tree.command(name='rank', description='Shows all roles of a user and their playtime in Squad')
async def show_ranks(interaction: discord.Interaction):
    # Check if the command was sent from an allowed channel
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("This command is only available in 🤖bot-chat.")
        return
    
    # Get the Discord user
    member = interaction.user
    guild = interaction.guild
    
    # Get the user's nickname
    user_name = member.name

    # Get the user's roles
    roles = "\n".join([role.name for role in member.roles if role.name != '@everyone'])

    # Get the user's Steam ID from the database
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Your Steam ID was not found in the database.")
        return

    # Get the user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Error retrieving user data: {e}")
        return

    # Extract the game list
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Error: user games not found.")
        return

    # Find Squad and Ready Or Not in the game list
    squad_playtime = None
    ron_playtime = None
    
    for game in games:
        if game.get('appid') == squad_app_id:
            squad_playtime = game.get('playtime_forever', None)
        elif game.get('appid') == RON_app_id:
            ron_playtime = game.get('playtime_forever', None)

    # Create the message to send
    message = f"User Name: {user_name}\nUser Roles:\n{roles}\n"

    if squad_playtime is not None:
        squad_playtime_hours = round(squad_playtime / 60, 1)
        message += f"Squad Playtime: {squad_playtime_hours:.1f} hours\n"
        
    else:
        message += "User has not played Squad\n"

    if ron_playtime is not None:
        ron_playtime_hours = round(ron_playtime / 60, 1)
        message += f"Ready Or Not Playtime: {ron_playtime_hours:.1f} hours\n"
    else:
        message += "User has not played Ready Or Not\n"

    # Send the message
    await interaction.response.send_message(message)
    # Call the function to assign role based on Squad playtime
    await assign_role_based_on_playtime(guild, member, squad_playtime_hours)


@tree.command(name="ronstats", description="Playtime in Ready Or Not")
async def ron_command(interaction: discord.Interaction):
    # Check if the command was sent from an allowed channel
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("This command is only available in 🤖bot-chat.")
        return
    
    # Get the Discord user
    member = interaction.user

    # Get the user's Steam ID from the database
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Your Steam ID was not found in the records.")
        return

    # Get the user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")
        return

    # Extract the game list
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Error: user games not found")
        return

    # Find Ready Or Not in the game list
    playtime_forever = get_ron_playtime(games, RON_app_id)

    # Output the result
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"Ready Or Not Playtime: {playtime_hours:.1f} hours")
    else:
        await interaction.response.send_message("User has not played Ready Or Not")


@tree.command(name="steamid", description="Displays names and Steam IDs of linked users")
async def show_steamids(interaction: discord.Interaction):
    # Check if the command was sent from an allowed channel
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("This command is only available in 🤖bot-chat.")
        return
    
    # Create a list of users with linked Steam IDs for display
    guild = interaction.guild
    steamid_data = []

    for member in guild.members:
        steam_id = get_steam_id_from_json(member.id)
        if steam_id:  # Check if the user has a linked Steam ID
            steamid_data.append(f"{member.name}: {steam_id}")

    if not steamid_data:
        await interaction.response.send_message("No users have linked their Steam IDs.")
        return

    # Form a single string with all the data
    message = "\n".join(steamid_data)

    # Send a message with the full list of users and their Steam IDs
    try:
        await interaction.response.send_message(message)
    except discord.errors.HTTPException as e:
        if e.status == 400 and e.code == 50035:  # Check for message length limit error
            # If the message is too long, split the data into parts and send sequentially
            chunks = [message[i:i + 1900] for i in range(0, len(message), 1900)]  # Split into parts of 1900 characters
            for chunk in chunks:
                await interaction.followup.send(chunk)


# Run the bot
client.run(TOKEN)
