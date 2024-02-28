import discord
from steam import Steam
from decouple import config

KEY = config("STEAM_API_KEY")
steam = Steam(KEY)
squad_app_id = 393380
TOKEN = config("Discord_API_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Add this line to enable message content access

client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print("Бот Discord запущен.")

@client.event
async def on_message(message):
  if message.content.startswith("!squadstats"):
        await message.channel.send("Введите ваш Steam ID:")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        steam_id = await client.wait_for('message', check=check)

        user_games = steam.users.get_owned_games(steam_id.content)

        try:
            games = user_games['games']
        except KeyError:
            await message.channel.send("Откройте доступ к вашим играм в настройках конфиденциальности.")
            return

        playtime_forever = None
        for game in games:
            if game['appid'] == squad_app_id:
                playtime_forever = game.get('playtime_forever', None)
                break

        if playtime_forever is not None:
            playtime_hours = round(playtime_forever / 60, 1)  # конвертация минут в часы и округление до .1
            await message.channel.send("Время игры в Squad: {} часов".format(playtime_hours))
        else:
            await message.channel.send("Игра Squad не найдена в списке игр пользователя.")

client.run(TOKEN)
