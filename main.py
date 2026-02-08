import json
import threading
import time
import requests
from config import AVAILABLE_LANGUAGES, AVAILABLE_LANGUAGES_DESCRIPTION
import mysql_db_functions as db
from urllib3.util import Timeout
from urllib3 import request
from googletrans import Translator
import dotenv
import os

dotenv.load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN', '')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TG_TOKEN}'
BASE_URL = ''

def send_message(chat_id, text, **kwargs):
    url = f'{TELEGRAM_API_URL}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, **kwargs}
    r = requests.post(url, json=payload)
    return r.json()

def edit_message(chat_id, message_id, text):
    url = f'{TELEGRAM_API_URL}/editMessageText'
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
    r = requests.post(url, json=payload)
    return r.json()

def delete_message(chat_id, message_id):
    url = f'{TELEGRAM_API_URL}/deleteMessage'
    payload = {'chat_id': chat_id, 'message_id': message_id}
    r = requests.post(url, json=payload)
    return r.json()

def inline_handler(inline_query_id, user_id, message):
    
    if message == '':
        '''Inline button without text'''
        results = [{
            "type": "article",
            "id": "1",
            "title": "Information",
            #"thumb_url": f"{BASE_URL}/INFO.png",
            "input_message_content": {"message_text": 'Для перевода на любой язык введите двухбуквеный код языка, пример: "@transmebot FR Привет!" . Для изменения стандратного языка перевода(без вставки кода) перейдите в бота @transmebot.'},
            "description": "Получить информацию о работе бота" }]
        
    elif (message.split(' ')[0].upper() in AVAILABLE_LANGUAGES): 
        '''With language code: @bot EN <text>'''
        lang = message.split(' ')[0].upper()
        try:
            translated = translate(message[3:], lang)
        except:
            translated = ' '

        results = [{
            "type": "article",
            "id": "1",
            "title": AVAILABLE_LANGUAGES_DESCRIPTION[lang],
            #"thumb_url": f"{BASE_URL}/{lang}.png",
            "input_message_content": {"message_text": translated},
            "description": translated }]
    
    else:
        '''Without language code: @bot <text> - standard language'''
        if db.check_user_exists(user_id):
            lang = db.get_user(user_id).translate_lang  #get user saved language from db
        else:
            lang = 'EN'  
        
        
        translated = translate(message, lang)
        
        results = [{
            "type": "article",
            "id": "1",
            "title": AVAILABLE_LANGUAGES_DESCRIPTION[lang],
            #"thumb_url": f"{BASE_URL}/{lang}.png",
            "input_message_content": {"message_text": translated},
            "description": translated
        }]
    
    inline_answer = {'inline_query_id':inline_query_id, 'results': results}

    headers = { 'Content-Type': 'application/json' }
    inline_answer = json.dumps(inline_answer).encode('utf-8')
    request('POST', f"{TELEGRAM_API_URL}/answerInlineQuery", headers=headers, body=inline_answer).data
    pass

def translate(message, lang="EN"):
    """translate with googletrans"""
    try:
        translator = Translator()
        
        # language code for googletrans (lowercase)
        target_lang = lang.lower()
        
        # translation
        result = translator.translate(message, dest=target_lang)
        return result.text
    except Exception as e:
        return f"Ошибка перевода! Обратитесь в администрацию!"

def command_handler(message):
    user_id = message.get('from').get('id')
    if not db.check_user_exists(user_id):
        try: 
            user_lang = message.get('from').get('language_code').upper()
        except:
            user_lang = 'RU'
        db.create_user(user_id, user_lang = user_lang, translate_lang='EN')
    menu_with_langs(user_id, hello='Здравствуйте! ')

def message_handler(message):
    chat_id = message.get('chat').get('id')
    user_id = message.get('from').get('id')
    if not db.check_user_exists(user_id):
        try: 
            user_lang = message.get('from').get('language_code').upper()
        except:
            user_lang = 'RU'
        db.create_user(user_id, user_lang = user_lang, translate_lang='EN')
    if message.get('chat').get('type') == 'private':
        if message.get('text').upper() in AVAILABLE_LANGUAGES:
            send_message(user_id, 'Вы выбрали: '+ AVAILABLE_LANGUAGES_DESCRIPTION[message.get('text').upper()], reply_markup = {'inline_keyboard':[[{'text': 'Change (Изменить)', 'callback_data':'change'}]]})
            db.update_user_data(user_id, translate_lang = message.get('text').upper())
        else:
            menu_with_langs(user_id)
    else:
        send_message(chat_id, translate(message.get('text'), db.get_user(user_id).translate_lang))

def button_click_handler(message):
    user_id = message.get('from').get('id')
    if not db.check_user_exists(user_id):
        try: 
            user_lang = message.get('from').get('language_code').upper()
        except:
            user_lang = 'RU'
        db.create_user(user_id, user_lang = user_lang, translate_lang='EN')

    callback_data = message.get('data')
    if callback_data == 'whatever':
        send_message(user_id, json.dumps(AVAILABLE_LANGUAGES_DESCRIPTION,  ensure_ascii=False).replace(',', '\n').replace('{','').replace('}', ''))
    elif callback_data == 'change':
        menu_with_langs(user_id)
    else:
        db.update_user_data(user_id, translate_lang = callback_data.upper())
        send_message(user_id, "Вы выбрали: " + AVAILABLE_LANGUAGES_DESCRIPTION[callback_data.upper()], reply_markup = {'inline_keyboard':[[{'text': 'Change (Изменить)', 'callback_data':'change'}]]})

def menu_with_langs(chat_id, hello = ''):
    menu = {
                "inline_keyboard": [
                    [{'text':'🇺🇸 🇬🇧 EN(English, Английский)', 'callback_data':'EN'}],
                    [{'text':'🇫🇷 FR(French, Français, Французский)', 'callback_data':'FR'}],
                    [{'text':'🇩🇪 DE(German, Deutsch, Немецкий)', 'callback_data':'DE'}],
                    [{'text':'🇷🇺 RU(Russian, Русский)', 'callback_data':'RU'}],
                    [{'text':'🇮🇹 IT(Italian, Italiano, Итальянский)', 'callback_data':'IT'}],
                    [{'text':'🇪🇸 ES(Spanish, Español, Испанский)', 'callback_data':'ES'}],
                    [{'text':'🇯🇵 JA(Japanese, 日本語, Японский)', 'callback_data':'JA'}],
                    [{'text':'🇰🇷 KO(Korean, 한국어, Корейский)', 'callback_data':'KO'}],
                    [{'text':'🇨🇳 ZH(Chinese, 中文, Китайский)', 'callback_data':'ZH'}],
                    [{'text':'🇸🇦 AR(Arabic, العربية, Арабский)', 'callback_data':'AR'}],
                    [{'text':'🇮🇳 HI(Hindi, हिन्दी, Хинди)', 'callback_data':'HI'}],
                    [{'text':'🇹🇷 TR(Turkish, Türkçe, Турецкий)', 'callback_data':'TR'}],
                    [{"text": "🌍 Отобразить все доступные языки", "callback_data": "whatever"}],]
            }
    send_message(chat_id, hello + 'Выберите язык из меню или введите двухбуквенный код', reply_markup = menu)

def process_update(update):
    try:    
        response = json.loads(update.data)  
    except:
        return
    
    if response.get('ok'):
        # all updates
        for i in response.get('result'):
            if i.get('inline_query'):
                inline_handler(i.get('inline_query').get('id'), i.get('inline_query').get('from').get('id'), i.get('inline_query').get('query'))

            #button click
            elif i.get('callback_query'):
                button_click_handler(i.get('callback_query'))
                
            #message
            elif i.get('message'): 
                if i.get('message').get('entities'):
                    #is command
                    if i.get('message').get('text')[0] == '/' and i.get('message').get('entities')[0].get('type') == 'bot_command' and i.get('message').get('chat').get('type') == 'private':
                        command_handler(i.get('message'))
                    #unknown attribute -> just message
                    else:
                        message_handler(i.get('message'))
                #just message
                elif i.get('message').get('text'):
                    message_handler(i.get('message'))
        try:
            db.edit_update(response.get('result')[-1].get('update_id'))
        except:
            pass

def get_updates_with_long_polling():
    #infinite long polling
    while True:
        try:
            url = f'{TELEGRAM_API_URL}/getUpdates'
            headers = { 'Content-Type': 'application/json' }
            timeout = Timeout(connect=5.0, read=15.0, total=None) #
            body = {
                'offset': str(db.get_update() + 1),
                'limit': '100',
                'timeout': 10  
            }
            body = json.dumps(body).encode('utf-8')
            
            try:
                response = request('POST', url, headers=headers, body=body, timeout=timeout)
                process_update(response)
            except Exception as e:
                return
            
                
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            time.sleep(5)  #if error pause before next request

def webhook_handler(environ, start_response):
    """WSGI- webhook handler"""
    try:
        method = environ.get('REQUEST_METHOD', '')
        path = environ.get('PATH_INFO', '')
                
        if method == 'POST' and path == '/webhook': #path for webhook: domain.com/webhook
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length)
            update = json.loads(post_data.decode('utf-8'))

            process_update(update)
            
            status = '200 OK' #Telegram always get back 200 
            headers = [('Content-Type', 'application/json')]
            response_body = json.dumps({'ok': True}).encode('utf-8')
        else:
            # unknown endpoint
            status = '404 Not Found'
            headers = [('Content-Type', 'text/plain')]
            response_body = b'Not Found'
        
        start_response(status, headers)
        return [response_body]
        
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        response_body = b'Internal Server Error'
        start_response(status, headers)
        return [response_body]

def start_long_polling_thread():
    """Запуск потока для long polling в фоне"""
    thread = threading.Thread(target=get_updates_with_long_polling, daemon=True)
    thread.start()
    thread.join()

# WSGI application
application = webhook_handler

if __name__ == '__main__':
    #check token
    me = json.loads(request('GET', f'{TELEGRAM_API_URL}/getMe').data)
    if not me.get('ok'):
        print('Invalid token')
        exit()

    # init db
    db.create_tables()
    db.check_update()
    
    # long polling
    get_updates_with_long_polling()

