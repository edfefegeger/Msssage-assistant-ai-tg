import logging


# Конфигурация логгера
logging.basicConfig(filename='LOGS.log', level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')


def log_and_print(*messages):
    formatted_message = ' '.join(map(str, messages))
    if 'ошибка' in formatted_message or 'Ошибка' in formatted_message or 'Error' in formatted_message:
        logging.error(formatted_message)


    else:
        logging.warn(formatted_message)
        print(formatted_message)
