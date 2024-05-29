import configparser
import sys
from openai import OpenAI
import telebot

# Инициализация клиента OpenAI
client = OpenAI()

# Чтение конфигурационного файла
config = configparser.ConfigParser()
config.read('congig.conf')  # Исправление опечатки
Telegram_bot_token = config['API']['Telegram_bot']

# Инициализация TeleBot
bot = telebot.TeleBot(Telegram_bot_token)

create_texts = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Этот бот отвечает на вопросы по процедурам массажа и взаимодействия с клиентами. Для того чтобы задать вопрос, просто напиши его.")



# Обработчик всех остальных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_text_messages(message):
    handle_question(message)

def handle_question(message):
    try:
        print("Assistant")

        command_text = message.text.strip()
        create_texts[message.chat.id] = command_text

        bot.send_message(message.chat.id, f"Идет генерация ответа, подождите... Ваш запрос: {message.text}")
        print(command_text)

        # Убедитесь, что assistant_id корректен и существует
        assistant_id = "asst_XmZXcXUH2JKU1NqdIspSCcKC"  # Замените на ваш действительный ID ассистента

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
            instructions="Пожалуйста, обращайтесь к пользователю как Джейн Доу. У пользователя премиум-аккаунт."
        )

        if run.status == 'completed':
            # Получение сообщений из темы
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            response_content = messages[-1].content  # Предполагается, что последнее сообщение - это ответ ассистента
            print(response_content)
        else:
            response_content = f"Ошибка: {run.status}"
            print(run.status)

        try:
            bot.send_message(message.chat.id, response_content, reply_to_message_id=message.message_id)
            print("Сообщение отправлено в чат")
        except Exception as e:
            print(f"Ошибка при отправке сообщения {response_content}: {e}")

    except Exception as e:
        print(f"Ошибка {e}")

# Запуск бота
bot.polling(none_stop=True, timeout=123)
