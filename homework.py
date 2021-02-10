import os
import time

import logging
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAIN_URL = 'https://praktikum.yandex.ru/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def parse_homework_status(homework):
    logging.debug('Получение названия домашки')
    homework_name = homework.get('homework_name')
    logging.debug('Получение статуса домашки')
    homework_status = homework.get('status')
    logging.info('Проверка статуса')
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework_status == 'reviewing':
        return f'работа "{homework_name}" взята в ревью'
    else:
        verdict = 'Ревьюеру всё понравилось, \
можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    api = 'api/'
    user_api = 'user_api/'
    homework_status = 'homework_statuses/'
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            '{0}{1}{2}{3}'.format(
                MAIN_URL,
                api,
                user_api,
                homework_status),
            params=params,
            headers=headers)
        return homework_statuses.json()
    except requests.RequestException as error:
        logging.error(error)
        return dict()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Запуск бота')
    bot = telegram.Bot(token=str(TELEGRAM_TOKEN))
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            getting_homeworks = new_homework.get('homeworks')
            if getting_homeworks:
                logging.info('Отправка сообщения')
                send_message(parse_homework_status(
                    getting_homeworks[0]),
                    bot)
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            time.sleep(1200)
            current_timestamp = int(time.time())
        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
