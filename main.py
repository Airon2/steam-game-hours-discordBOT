import discord
from discord import app_commands
from steam import Steam
from decouple import config
import asyncio
import json
# Получаем ключ API Steam и токен Discord из переменных среды или файла .env
KEY = config("STEAM_API_KEY")
TOKEN = config("Discord_API_TOKEN")

# Инициализируем клиент API Steam
steam = Steam(KEY)

# Определяем app ID для Squad (ID игры в Steam)
squad_app_id = 393380
RON_app_id = 1144200
pubg_app_id = 578080

allowed_channel_ids = [1111391658026729483, 591661218410790912]  # Идентификаторы разрешенных каналов

# Настраиваем намерения Discord для доступа к содержимому сообщений
intents = discord.Intents.all()

# Создаем клиент Discord
client = discord.Client(intents=intents)
intents.message_content = True

# Определяем дерево команд
tree = app_commands.CommandTree(client)

# Словарь для хранения информации о пользователях
users = {}

# Функция для проверки разрешенного канала
def is_allowed_channel(channel_id):
    return channel_id in allowed_channel_ids

# Функция для проверки валидности Steam ID
def check_steamid(steam_id):
    if len(steam_id) == 17 and steam_id.isdigit():
        return True
    return False

# Функция для извлечения Steam ID из файла users.json по Discord ID
def get_steam_id_from_json(discord_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
            if str(discord_id) in users:
                return users[str(discord_id)]["steam_id"]
    except FileNotFoundError:
        print("Файл users.json не найден.")
    return None

# Функция для получения времени игры 
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

def get_pubg_playtime(games, pubg_app_id):
    for game in games:
        if game.get('appid') == pubg_app_id:
            return game.get('playtime_forever', None)
    return None


# Функция для выдачи роли на основе часов игры в Squad
async def assign_role_based_on_playtime(guild, member, squad_playtime_hours):
    role_to_assign = None

    if squad_playtime_hours >= 2000:
        role_to_assign = discord.utils.get(guild.roles, name="🔱Генерал армии")
    elif squad_playtime_hours >= 1000:
        role_to_assign = discord.utils.get(guild.roles, name="🔱Генерал-полковник")
    elif squad_playtime_hours >= 800:
        role_to_assign = discord.utils.get(guild.roles, name="🏵️Полковник")
    elif squad_playtime_hours >= 700:
        role_to_assign = discord.utils.get(guild.roles, name="🏵️Подполковник")
    elif squad_playtime_hours >= 500:
        role_to_assign = discord.utils.get(guild.roles, name="🌟Майор")
    elif squad_playtime_hours >= 400:
        role_to_assign = discord.utils.get(guild.roles, name="🌟Капитан")
    elif squad_playtime_hours >= 350:
        role_to_assign = discord.utils.get(guild.roles, name="⭐Старший лейтенант")
    elif squad_playtime_hours >= 300:
        role_to_assign = discord.utils.get(guild.roles, name="⭐Лейтенант")
    elif squad_playtime_hours >= 250:
        role_to_assign = discord.utils.get(guild.roles, name="🔰Старший сержант")
    elif squad_playtime_hours >= 100:
        role_to_assign = discord.utils.get(guild.roles, name="🔰Сержант")
    elif squad_playtime_hours >= 50:
        role_to_assign = discord.utils.get(guild.roles, name="Рядовой")
    else:
        role_to_assign = discord.utils.get(guild.roles, name="Рядовой")  # Роль для всех с менее чем 50 часами
    
    if role_to_assign:
        # Проверяем, есть ли у пользователя уже данная роль
        if role_to_assign not in member.roles:
            try:
                # Удаляем предыдущие роли в зависимости от условий
                roles_to_remove = [
                    discord.utils.get(guild.roles, name="Рядовой"),
                    discord.utils.get(guild.roles, name="🔰Сержант"),
                    discord.utils.get(guild.roles, name="🔰Старший сержант"),
                    discord.utils.get(guild.roles, name="⭐Лейтенант"),
                    discord.utils.get(guild.roles, name="⭐Старший лейтенант"),
                    discord.utils.get(guild.roles, name="🌟Капитан"),
                    discord.utils.get(guild.roles, name="🌟Майор"),
                    discord.utils.get(guild.roles, name="🏵️Подполковник"),
                    discord.utils.get(guild.roles, name="🏵️Полковник"),
                    discord.utils.get(guild.roles, name="🔱Генерал-полковник"),
                    discord.utils.get(guild.roles, name="🔱Генерал армии")
                ]
                roles_to_remove = [role for role in roles_to_remove if role is not None]
                await member.remove_roles(*roles_to_remove)
                
                # Добавляем новую роль
                await member.add_roles(role_to_assign)
                print(f"Роль '{role_to_assign.name}' назначен на {member.name}")
            except discord.HTTPException as e:
                print(f"Не удалось назначить роль {member.name}: {e}")
    else:
        print("No role assigned based on Squad playtime.")

# Загрузка данных о пользователях из файла users.json
def load_users():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print("Файл users.json не найден.")

# Сохранение данных о пользователях в файл users.json
def save_users():
    global users
    with open("users.json", "w") as f:
        json.dump(users, f)

# Обработчик события, когда бот готов и подключен к Discord
@client.event
async def on_ready():
    print("Бот Discord запущен.")
    try:
        synced = await tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(e)
    # Загрузка данных о пользователях при запуске бота
    load_users()

@tree.command(name="bindsteamid", description="Привязывает ваш Steam ID к профилю")
async def bind_command(interaction: discord.Interaction):
    global users
    
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Проверяем, есть ли у пользователя уже привязанный Steam ID
    if get_steam_id_from_json(interaction.user.id):
        await interaction.response.send_message("Сіздің Steam id профильге байланған.")
        return
    
    # Запрашиваем Steam ID пользователя
    await interaction.response.send_message("Steam ID енгізіңіз:")

    # Определяем функцию проверки для фильтрации сообщений от одного и того же пользователя
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        # Ожидаем от пользователя отправки его Steam ID
        steam_id_message = await client.wait_for('message', check=check, timeout=60)  # Ожидаем сообщение в течение 60 секунд
    except asyncio.TimeoutError:
        await interaction.followup.send("Жауап күту уақыты аяқталды. Қайталап көріңіз")
        return

    # Получаем Steam ID из сообщения пользователя
    steam_id = steam_id_message.content

    # Проверка валидности Steam ID
    if not check_steamid(steam_id):
        await interaction.followup.send("Қате Steam ID. 17 таңбалы сандық кодты енгізіңіз.")
        return

    # Добавляем данные пользователя в словарь users
    users[interaction.user.id] = {
        "discord_id": interaction.user.id,
        "steam_id": steam_id,
    }

    # Сохраняем данные пользователей в файл users.json
    save_users()

    # Отправляем сообщение о успешной привязке
    await interaction.followup.send(f"Сіздің Steam id профильге сәтті байланған: {steam_id}")

@tree.command(name="unbindsteamid", description="Отвязывает ваш Steam ID от профиля")
async def unbind_command(interaction: discord.Interaction):
    global users
    
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Проверяем, был ли привязан Steam ID к этому пользователю
    steam_id = get_steam_id_from_json(interaction.user.id)
    if not steam_id:
        await interaction.response.send_message("Сіздің Steam ID профильге байланбаған.")
        return

    # Удаляем данные пользователя из файла users.json
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print("Файл users.json не найден.")
        users = {}

    if str(interaction.user.id) in users:
        del users[str(interaction.user.id)]
        # Сохраняем изменения в файл users.json
        with open("users.json", "w") as f:
            json.dump(users, f)
        
        # Отправляем сообщение об успешной отвязке
        await interaction.response.send_message("Сіздің Steam ID профильден сәтті ажыратылды.")
    else:
        await interaction.response.send_message("Сіздің Steam ID профильге байланбаған.")

@tree.command(name="steamid", description="Отображает имена и Steam ID привязанных пользователей")
async def show_steamids(interaction: discord.Interaction):
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Создаем список пользователей с привязанными Steam ID для отображения
    guild = interaction.guild
    steamid_data = []

    for member in guild.members:
        steam_id = get_steam_id_from_json(member.id)
        if steam_id:  # Проверяем, есть ли привязанный Steam ID у пользователя
            steamid_data.append(f"{member.name}: {steam_id}")

    if not steamid_data:
        await interaction.response.send_message("Ни один пользователь не привязал свой Steam ID.")
        return

    # Формируем одну строку со всеми данными
    message = "\n".join(steamid_data)

    # Отправляем сообщение с полным списком пользователей и их Steam ID
    try:
        await interaction.response.send_message(message)
    except discord.errors.HTTPException as e:
        if e.status == 400 and e.code == 50035:  # Проверяем ошибку ограничения длины сообщения
            # Если сообщение слишком длинное, разделяем данные на части и отправляем по очереди
            chunks = [message[i:i + 1900] for i in range(0, len(message), 1900)]  # Разбиваем на части по 1900 символов
            for chunk in chunks:
                await interaction.followup.send(chunk)

@tree.command(name='rank', description='Показывает все роли пользователя и его часы в играх')
async def show_ranks(interaction: discord.Interaction):
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Получаем пользователя Discord
    member = interaction.user
    guild = interaction.guild
    
    # Получаем ник пользователя
    user_name = member.name

    # Получаем список ролей пользователя
    roles = "\n".join([role.name for role in member.roles if role.name != '@everyone'])

    # Получаем Steam ID пользователя из базы данных
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Сіздің Steam ID базада табылмады ")
        return

    # Получаем список игр пользователя из Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Пайдаланушы туралы ақпарат алу кезіндегі қате: {e}")
        return

    # Извлекаем список игр
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Қате: пайдаланушы ойындары табылмады")
        return

   # Ищем Squad и Ready Or Not и pubg в списке игр
    squad_playtime = None
    ron_playtime = None
    pubg_playtime = None
    
    for game in games:
        if game.get('appid') == squad_app_id:
            squad_playtime = game.get('playtime_forever', None)
        elif game.get('appid') == RON_app_id:
            ron_playtime = game.get('playtime_forever', None)
        elif game.get('appid') == pubg_app_id:
            pubg_playtime = game.get('playtime_forever', None)

    # Формируем сообщение для отправки
    message = f"Пайдаланушы аты: {user_name}\nПайдаланушы рөлдері:\n{roles}\n"

    if squad_playtime is not None:
        squad_playtime_hours = round(squad_playtime / 60, 1)
        message += f"Squad ойын уақыты: {squad_playtime_hours:.1f} cағат\n"
        
    else:
        message += "Squad ойыны пайдаланушының ойындар тізімінде жоқ\n"

    if ron_playtime is not None:
        ron_playtime_hours = round(ron_playtime / 60, 1)
        message += f"Ready Or Not ойын уақыты: {ron_playtime_hours:.1f} cағат\n"
    else:
        message += "Ready Or Not ойыны пайдаланушының ойындар тізімінде жоқ\n"
        
    if pubg_playtime is not None:
        pubg_playtime_hours = round(pubg_playtime / 60, 1)
        message += f"PUBG ойын уақыты: {pubg_playtime_hours:.1f} cағат\n"
    else:
        message += "PUBG ойыны пайдаланушының ойындар тізімінде жоқ\n"

    # Отправляем сообщение
    await interaction.response.send_message(message)
    # Вызываем функцию для присвоения роли на основе часов игры в Squad
    await assign_role_based_on_playtime(guild, member, squad_playtime_hours)

@tree.command(name="squadstats", description="Время игры в Squad")
async def squad_command(interaction: discord.Interaction): 
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Получаем пользователя Discord
    member = interaction.user

    # Получаем Steam ID пользователя из базы данных
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Сіздің Steam ID дерекқордан табылмады.")
        return

    # Получаем список игр пользователя из Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Қате: {e}")
        return

    # Извлекаем список игр
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Құпиялылық параметрлерінде ойындарыңызға доступ ашыңыз")
        return

    # Ищем Squad в списке игр
    playtime_forever = get_playtime(games, squad_app_id)

    # Выводим результат
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"Squad ойын уақыты: {playtime_hours:.1f} cағат")
    else:
        await interaction.response.send_message("Squad ойыны пайдаланушының ойындар тізімінде жоқ")

@tree.command(name="ronstats", description="Время игры в Ready Or Not")
async def ron_command(interaction: discord.Interaction):
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Получаем пользователя Discord
    member = interaction.user

    # Получаем Steam ID пользователя из базы данных
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Сіздің Steam ID дерекқордан табылмады.")
        return

    # Получаем список игр пользователя из Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Қате: {e}")
        return

    # Извлекаем список игр
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Құпиялылық параметрлерінде ойындарыңызға доступ ашыңыз")
        return

    # Ищем Ready Or Not в списке игр
    playtime_forever = get_ron_playtime(games, RON_app_id)

    # Выводим результат
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"Ready Or Not ойын уақыты: {playtime_hours:.1f} cағат")
    else:
        await interaction.response.send_message("Ready Or Not ойыны пайдаланушының ойындар тізімінде жоқ")

@tree.command(name="pubgstats", description="Время игры в PUBG")
async def pubg_command(interaction: discord.Interaction):
    # Проверяем, что команда была отправлена из разрешенного канала
    if not is_allowed_channel(interaction.channel_id):
        await interaction.response.send_message("Бұл команда тек 🤖bot-chat - та қол жетімді.")
        return
    
    # Получаем пользователя Discord
    member = interaction.user

    # Получаем Steam ID пользователя из базы данных
    steam_id = get_steam_id_from_json(member.id)

    if not steam_id:
        await interaction.response.send_message("Сіздің Steam ID дерекқордан табылмады.")
        return

    # Получаем список игр пользователя из Steam
    try:
        user_games = steam.users.get_owned_games(steam_id)
    except Exception as e:
        await interaction.response.send_message(f"Қате: {e}")
        return

    # Извлекаем список игр
    try:
        games = user_games['games']
    except KeyError:
        await interaction.response.send_message("Құпиялылық параметрлерінде ойындарыңызға доступ ашыңыз")
        return

    # Ищем pubg в списке игр
    playtime_forever = get_pubg_playtime(games, pubg_app_id)

    # Выводим результат
    if playtime_forever is not None:
        playtime_hours = round(playtime_forever / 60, 1)
        await interaction.response.send_message(f"PUBG ойын уақыты: {playtime_hours:.1f} cағат")
    else:
        await interaction.response.send_message("PUBG ойыны пайдаланушының ойындар тізімінде жоқ")

# Запуск бота
client.run(TOKEN)

    
