import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)


def parse_homework_status(homework):
    status = {'reviewing': 'Работа взята в ревью',
              'approved': ('Ревьюеру всё понравилось,'
                           ' можно приступать к следующему уроку.'),
              'rejected': 'К сожалению в работе нашлись ошибки.'}
    try:
        verdict = status[homework['status']]
        homework_name = homework['homework_name']
    except Exception as e:
        logging.error('При разборе статуса домашки'
                      f' произошла ошибка: {e}')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            API_URL,
            headers=headers,
            params=params
        )
    except Exception as e:
        logging.error('При запросе статуса домашки'
                      f' произошла ошибка: {e}')
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    logging.debug('Бот запущен')
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status
                    (new_homework.get('homeworks')[0]),
                    bot_client
                )
                logging.info('Отправлено сообщение')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            try:
                send_message(f'Бот столкнулся с ошибкой: {e}', bot_client)
            except Exception as error:
                logging.error('При отправке сообщения об ошибке,'
                              f' произошла ошибка: {error}')
            time.sleep(5)


if __name__ == '__main__':
    main()
