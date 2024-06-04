import logging
import telebot
from telebot import types
import configparser

config = configparser.ConfigParser()
config.read('congig.conf', encoding='utf-8')
TELEGRAM_BOT_TOKEN = config['API']['notify_bot']

CHAT_ID = '783897764'
CHAT_ID2 = '783897764'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

logging.basicConfig(filename='LOGS.log', level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')


def log_and_print(*messages):
    formatted_message = ' '.join(map(str, messages))
    if 'ошибка' in formatted_message or 'Ошибка' in formatted_message or 'Error' in formatted_message:
        logging.error(formatted_message)


    else:
        logging.warn(formatted_message)
        print(formatted_message)
        bot.send_message(CHAT_ID, formatted_message)
        if CHAT_ID2!= CHAT_ID:
            bot.send_message(CHAT_ID2, formatted_message)
#226308337