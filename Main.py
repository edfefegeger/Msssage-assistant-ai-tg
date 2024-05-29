import configparser
from openai import OpenAI
client = OpenAI()
import telebot
config = configparser.ConfigParser()
config.read('congig.conf')
Telegram_bot_tolen = config['API']['Telegram_bot']

bot = telebot.TeleBot(Telegram_bot_tolen)

create_texts = {}

# Обработчик команды /create

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Этот бот отвечает на вопросы по процедурам массажа и взаимодействия с клиентами. Для того чтобы задать вопрос используй - /ask 'твой вопрос'")

@bot.message_handler(commands=['ask'])
def make(message):
    try:
        print("Dalle")

        command_text = message.text.replace('/ask', '').strip()
        create_texts[message.chat.id] = command_text

        bot.send_message(message.chat.id, f"Generating... Your request: {message.text}")
        print(command_text)

        response = client.images.generate(
            model="dall-e-3",
            prompt=command_text,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Получаем URL сгенерированного изображения
        image_url = response.data[0].url
        print(image_url)


        try:
            bot.send_photo(message.chat.id, image_url, reply_to_message_id=message.message_id)

            print("Изображение отправлено в чат")

        except Exception as e:
            print(f"Ошибка при отправке изображения {image_url}: {e}")
    except Exception as e:
        print(f"Ошибка {e}")

# Запускаем бота
bot.polling(none_stop=True, timeout=123)

