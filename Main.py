import configparser
import threading
import time
from openai import OpenAI
import telebot
from logger import log_and_print

# Инициализация клиента OpenAI
client = OpenAI()

# Чтение конфигурационного файла
config = configparser.ConfigParser()
config.read('congig.conf')  # Исправление опечатки
Telegram_bot_token = config['API']['Telegram_bot']
assistant_id = config["API"]['assistant_id']

# Инициализация TeleBot
bot = telebot.TeleBot(Telegram_bot_token)

create_texts = {}
user_request_counts = {}

# Удаление webhook
bot.remove_webhook()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Этот бот отвечает на вопросы по процедурам массажа и взаимодействия с клиентами. Для того чтобы задать вопрос, просто напиши его здесь.")


# Обработчик всех остальных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_text_messages(message):
    handle_question(message)

def handle_question(message):
    try:
        print("Assistant")

        user_id = message.from_user.id
        command_text = message.text.strip()
        create_texts[message.chat.id] = command_text

        # Увеличение счетчика запросов для пользователя
        if user_id in user_request_counts:
            user_request_counts[user_id] += 1
        else:
            user_request_counts[user_id] = 1

        if user_request_counts[user_id] > 3:
            bot.send_message(message.chat.id, f"Извините, вы превысили лимит попыток на сегодня. Лимит - 3 запроса в день.")
            return

        request_count = user_request_counts[user_id]

        bot.send_message(message.chat.id, f"Формирование ответа, подождите... \nВаш запрос: {message.text}")
        print(command_text)
        log_and_print(f"Новый запрос от пользователя: {user_id} Запрос: {command_text}")

        # Создание новой темы (thread)
        thread = client.beta.threads.create()

        # Отправка сообщения пользователя в тему
        user_message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=command_text
        )

        # Запуск ассистента
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=""
        )

        if run.status == 'completed':
            # Получение сообщений из темы
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            ).data
            # Извлечение текста ответа от ассистента
            response_content = ""
            for msg in messages:
                if msg.role == 'assistant':
                    response_content = msg.content[0].text.value
                    break

            log_and_print(f"Ответ GPT: {response_content}")
            log_and_print(f"Пользователь {user_id} сделал {request_count} запрос(ов).")
        else:
            print(run.status)

        if response_content == 'Данной информации нет в нашей базе знаний, но есть ответ в интернете.':
            user_request_counts[user_id] -= 1

        try:
            bot.send_message(message.chat.id, response_content, reply_to_message_id=message.message_id)

            if response_content == 'Данной информации нет в нашей базе знаний, но есть ответ в интернете.':
                bot.send_message(message.chat.id, 'Попытка не засчитана, счетчик остался тем же.', reply_to_message_id=message.message_id)

            print("Сообщение отправлено в чат")
        except Exception as e:
            log_and_print(f"Ошибка при отправке сообщения {response_content}: {e}")
            user_request_counts[user_id] -= 1

        bot.send_message(message.chat.id, f"Хочешь задать еще вопрос? Пиши снова! Ты уже сделал {request_count} запрос(ов).")

    except Exception as e:
        log_and_print(f"Ошибка {e}")
        user_request_counts[user_id] -= 1

def reset_request_counts():
    while True:
        time.sleep(86400)  # 86400 секунд = 24 часа
        user_request_counts.clear()
        log_and_print("Прошло 24 часа, счетчики запросов сброшены для всех пользователей.")

# Запуск функции сброса счетчиков в отдельном потоке
reset_thread = threading.Thread(target=reset_request_counts)
reset_thread.daemon = True
reset_thread.start()

# Запуск бота
bot.polling(none_stop=True, timeout=123)
