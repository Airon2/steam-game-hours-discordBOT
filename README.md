This bot shows the number of hours you have played in a specific game, which you can customize. Enter the statistics with the "!squadstats" command, then enter our Steam ID and the bot will show the number of hours we have spent playing.
To change the game, you need to change the "squad_app_id" to the game's ID.

1) Creating an Application:

- First, we need to create a Discord application. To do this, follow this link: https://discord.com/developers/applications. After successfully logging in to your Discord account, click on the "New Application" button and give the application a name.

- After creating the application, go to the "Bot" tab and click on "Reset Token". Save the token in a file called "Discord_API_TOKEN" in the "venv" directory. Also, tick all the checkboxes below "Privileged Gateway Intents".

2) Connecting our bot to your server:

In order to connect our bot to your Discord server, follow these simple instructions:

- Go to the OAuth2 section in the OAuth2 URL generator, select the "bot parameter", and in the "BOT PERMISSIONS" section, select the necessary permissions for your bot. In our case, these include "Send Messages", "Read Messages/View Channels", and "Use Slash Commands".
 
- Once you've selected these options, copy the "GENERATED URL" and paste it into the browser. Add your bot to your server by adding the URL to a line in your browser and connecting it to your server.

3) Creating the Steam API:

- To get the Steam API, simply click the link and create a new web API key for your bot on Steam. We can name the domain any way we want, and don't forget to save the key in a file called .venv in the "STEAM_API_KEY" parameter.
https://steamcommunity.com/dev/apikey

4) Launching the Bot:
- Run the Python virtual environment by running the command ` python -m venv myvenv `
- Activate the virtual environment running ` myvenv\Scripts\activate `.
- Install the pip packages by running ` pip install -r requirements.txt `.
- Launch main.py

Этот бот отображает количество часов, сыгранных в конкретной игре, которое можно настроить. 
Вводим статистику командой !squadstats, затем наш Steam ID, и bot отобразит количество сыгранных нами часов.
Чтобы изменить игру, вам нужно изменить squad_app_id на идентификатор игры

1) Создание Application'a:

- Для начала нам нужно создать Discord Application, для этого мы должны перейти по этой ссылке: https://discord.com/developers/applications. После успешного входа в ваш аккаунт Discord, вам нужно нажать на кнопку New Application и выбрать имя для приложения.

- После создания Application'а мы должны перейти во вкладку Bot, а затем нажамаем на Reset Token и сохраняем его в файле .venv в параметре Discord_API_TOKEN 
- Также ставим галочки на все пункты ниже Privileged Gateway Intents

2) Подключаем нашего бота к серверу:

- Для того чтобы подключить бота к вашему серверу Дискорд, нужно следовать простым инструкциям:

- Заходим в OAuth2 в пункте OAuth2 URL Generator выбираем параметр bot, в BOT PERMISSIONS выбираем нужные разрешение в нашем случае это Send Messages,Read Messages/View Channels, Use Slash Commands и копируем GENERATED URL и вставляем в строку в браузере и добавляем бот на наш сервер.

3) Создание API Steam:

- Для получения API Steam просто переходим по ссылке и регистрируем новый ключ веб-API Steam.Домен называем как хотим и не забываем сохранить его в файле .venv в параметре STEAM_API_KEY
https://steamcommunity.com/dev/apikey

4) Запуск Бота

- Запустить виртуалку 
`python -m venv myvenv`

- Активируйте ее 
`myvenv\Scripts\activate`

- скачайте библиотеки 
`pip install requirements.txt`

- запускаем main.py

Қазақша нұсқасы: 
Бұл бот белгілі бір ойында ойналатын сағат санын көрсетеді, оны теңшеуге болады. Статистиканы топпен енгізіңіз !squadstats, содан кейін Біздің Steam ID және bot біз ойнаған сағаттардың санын көрсетеді. Ойынды өзгерту үшін squad_app_id файлын ойын идентификаторына өзгерту керек

1) Application Құру:

- Бастау үшін біз Discord Application құруымыз керек, ол үшін мына сілтемеге өтуіміз керек: https://discord.com/developers/applications. Discord есептік жазбаңызға сәтті кіргеннен кейін жаңа қолданба түймесін басып, қолданбаның атын таңдау керек.

- Application жасағаннан кейін біз Bot қойындысына өтуіміз керек, содан кейін Reset Token түймесін басып, оны файлға сақтаймыз .venv Discord_API_TOKEN параметрінде біз сонымен қатар Privileged Gateway Intents астындағы барлық элементтерді белгілейміз

2) біздің ботты серверге қосыңыз:

- Ботты Дискорд серверіне қосу үшін қарапайым нұсқауларды орындау керек:

- Біз OAuth2-ге OAuth2 GL Generator тармағында bot параметрін таңдаймыз, BOT PERMISSIONS - те қажетті рұқсатты таңдаймыз біздің жағдайда бұл Send Messages,Read Messages/View Channels, Use Slash commands және generated URL мекенжайын көшіріп, браузердегі жолға қойып, ботты біздің серверге қосамыз.

3) Steam API құру:

- Steam API алу үшін сілтемеге өтіп, жаңа Steam веб - API кілтін тіркеңіз.Доменді біз қалағандай атаймыз және оны файлға сақтауды ұмытпаңыз .STEAM_API_KEY параметріндегі venv https://steamcommunity.com/dev/apikey

4) Ботты Іске Қосу

- `Python-m venv myvenv` виртуалды ортаны жасаңыз

- `myvenv\Scripts\activate` виртуалды ортаны іске қосыңыз

- `PIP install - r requirements` кітапханаларын жүктеп алыңыз

- main.py іске қосу 

