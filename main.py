import discord
from steam import Steam
from decouple import config

# Get Steam API key and Discord token from environment variables or .env file
KEY = config("STEAM_API_KEY")
TOKEN = config("Discord_API_TOKEN")

# Initialize Steam API client
steam = Steam(KEY)

# Define app ID for Squad (Steam game ID)
squad_app_id = 393380

# Set up Discord intents to access message content
intents = discord.Intents.default()
intents.message_content = True

# Create Discord client
client = discord.Client(intents=intents)

# Define the command tree
tree = discord.app_commands.CommandTree(client)

# Event handler for when the bot is ready and connected to Discord
@client.event
async def on_ready():
    print("Discord bot is ready.")
    # Synchronize commands with Discord (may take up to 1 hour)
    await tree.sync()

# Slash command to get Squad playtime
@tree.command(name="squadstats", description="Get Squad playtime")
async def squad_command(interaction):
    # Request the user's Steam ID
    await interaction.response.send_message("Enter your Steam ID:")

    # Define a check function to filter messages from the same user
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    # Wait for the user to send their Steam ID
    steam_id = await client.wait_for('message', check=check)

    # Get the user's game list from Steam
    try:
        user_games = steam.users.get_owned_games(steam_id.content)
    except Exception as e:
        await interaction.followup.send(f"Error retrieving user information:")
        return

    # Extract the list of games
    try:
        games = user_games['games']
    except KeyError:
        await interaction.followup.send_message("Grant access to your games in privacy settings")
        return

    # Search for Squad in the game list
    playtime_forever = None
    for game in games:
        if game.get('appid') == squad_app_id:
            playtime_forever = game.get('playtime_forever', None)
            break

    # Send the result
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.followup.send(f"Squad playtime: {playtime_hours:.1f} hours")
    else:
        await interaction.followup.send("Squad not found in user's game list.")

# Run the Discord bot
client.run(TOKEN)
