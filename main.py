import discord
from steam import Steam
from decouple import config

# Get the Steam API key and Discord API token from environment variables or .env file
KEY = config("STEAM_API_KEY")
TOKEN = config("Discord_API_TOKEN")

# Initialize the Steam API client
steam = Steam(KEY)

# Define the app ID for Squad (Steam game ID)
squad_app_id = 393380

# Set up Discord intents to allow access to message content
intents = discord.Intents.default()
intents.message_content = True

# Create a Discord client with the specified intents
client = discord.Client(intents=intents)

# Event handler for when the bot is ready and connected to Discord
@client.event
async def on_ready():
    print("Discord bot is running.")  # Print a message indicating that the Discord bot is running

# Event handler for when a message is received
@client.event
async def on_message(message):
    # Check if the message starts with the command "!squadstats"
    if message.content.startswith("!squadstats"):
        # Prompt the user to enter their Steam ID
        await message.channel.send("Enter your Steam ID:")

        # Define a check function to filter messages from the same user and channel
        def check(m):
            return m.author == message.author and m.channel == message.channel

        # Wait for the user to send their Steam ID
        steam_id = await client.wait_for('message', check=check)

        # Get the list of owned games for the user from Steam
        user_games = steam.users.get_owned_games(steam_id.content)

        try:
            # Try to access the 'games' key in the user_games dictionary
            games = user_games['games']
        except KeyError:
            # If 'games' key is not found, prompt the user to open access to their games
            await message.channel.send("Open access to your games in privacy settings.")
            return

        # Initialize playtime_forever variable
        playtime_forever = None
        for game in games:
            # Iterate through the list of games
            if game['appid'] == squad_app_id:
                # Check if the game's appid matches the Squad app ID
                playtime_forever = game.get('playtime_forever', None)
                break

        if playtime_forever is not None:
            # If playtime_forever is not None, calculate playtime in hours and round to 1 decimal place
            playtime_hours = round(playtime_forever / 60, 1)
            await message.channel.send("Time played in Squad: {} hours".format(playtime_hours))
        else:
            # If playtime_forever is None, inform the user that Squad is not found in their game list
            await message.channel.send("Squad game not found in user's game list.")

# Run the Discord bot with the specified token
client.run(TOKEN)
