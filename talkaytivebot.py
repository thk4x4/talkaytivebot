from telegram.ext import CommandHandler, Updater, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup
import requests
import logging
import os
import datetime
from pprint import pprint
import random
import nltk

from dotenv import load_dotenv

load_dotenv()

secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token=secret_token)

URL_CATS = 'https://api.thecatapi.com/v1/images/search'
URL_DOGS = 'https://api.thedogapi.com/v1/images/search'
URL_WEATHER = 'https://wttr.in'
BOT_CONFIG = {
    'intents': {
        'hello': {
            'examples': ['Приветики', 'Здравствуй',
                         'Здарова', 'Привет', 'Алоха'],
            'responses': ['Хай!', 'Прив)', 'Хэллоу', 'Дарова', 'Салют']},
        'bye': {
            'examples': ['Пока', 'Сайонара',
                         'Покедова', 'Досвидули', 'До свидания'],
            'responses': ['До свиданья', 'Увидимся', 'Пока-пока!']
        },
        'how_are_you': {
            'examples': ['Как ты', 'Как дела',
                         'Как сам', 'Че каво', 'Как делишки'],
            'responses': ['У бота всегда прекрасно', 'Отлично',
                          'Что-то грустненько, раскажи что-нибудь']
        },
        'what_are_you_do': {
            'examples': ['Чем занмаешься', 'Че делаешь',
                         'Расскажи что делаешь', 'Чем занят'],
            'responses': ['Прекрасно провожу время, общаясь с тобой',
                          'Оптимизирую свои алгоритмы',
                          'Работаю во благо людей']
        }
    }
}


def clean(text):
    cleaned_text = ''
    for char in text.lower():
        if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            cleaned_text = cleaned_text + char
    return cleaned_text


def get_intent(text):
    for intent in BOT_CONFIG['intents'].keys():
        for example in BOT_CONFIG['intents'][intent]['examples']:
            clean_example = clean(example)
            clean_text = clean(text)
            if nltk.edit_distance(clean_example, clean_text) / max(len(clean_example), len(clean_text)) < 0.4:
                return intent
    return 'intent not found'


def say_hi(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    text = update.message.text
    intent = get_intent(text)
    if intent == 'intent not found':
        text = '{}, я не очень понял вас, я спрошу.'.format(name)
    else:
        text = random.choice(BOT_CONFIG['intents'][intent]['responses'])
    buttons = ReplyKeyboardMarkup([
                ['/menu']],
            resize_keyboard=True
            )
    context.bot.send_message(
        chat_id=chat.id,
        text=text,
        reply_markup=buttons
        )


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup([
                ['/newcat', '/newdog'],
                ['/now_time', '/weather']],
            resize_keyboard=True
            )
    context.bot.send_message(
        chat_id=chat.id,
        text='Рад приветствовать тебя, {}! Чем могу быть полезен?'.format(name),
        reply_markup=buttons
        )

def get_new_image_cats():
    try:
        response = requests.get(URL_CATS)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = URL_DOGS
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_new_image_dogs():
    try:
        response = requests.get(URL_DOGS)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = URL_CATS
        response = requests.get(new_url)

    response = response.json()
    random_dog = response[0].get('url')
    return random_dog

def new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image_cats())


def new_dog(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image_dogs())

def show_cats_image(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newcat', '/menu']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='{}. Посмотри, какого котика я тебе нашёл! Показать еще?'.format(name),
        reply_markup=button
    )

    context.bot.send_photo(chat.id, get_new_image_cats())


def show_dogs_image(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newdog', '/menu']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='{}. Посмотри, как тебе пёсик, а! Показать еще?'.format(name),
        reply_markup=button
    )

    context.bot.send_photo(chat.id, get_new_image_dogs())


def show_now_time(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/menu']], resize_keyboard=True)
    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name='МСК')
    now_time_in_moscow = datetime.datetime.now(tz=tz)
    context.bot.send_message(
        chat_id=chat.id,
        text='Сегодня {}. Московское время {}'.format(now_time_in_moscow.strftime("%d-%m-%Y"), now_time_in_moscow.strftime("%H:%M")),
        reply_markup=button
    )


def get_weather():
    weather_parameters = {
        '0': '',
        'T': '',
        "M": '',
        'lang': 'ru'
    }
    try:
        response = requests.get(URL_WEATHER, params=weather_parameters)
    except Exception as error:
        logging.error(f'Ошибка при запросе к погодному API: {error}')

    response = response.text
    return response


def weather(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/menu']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=get_weather(),
        reply_markup=button
    )


def telegram_id(update, context):
    pprint(update)
    telegram_id = update.message.chat.id
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/menu']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Ваш id {} .'.format(telegram_id),
        reply_markup=button
    )


def main():
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', show_cats_image))
    updater.dispatcher.add_handler(CommandHandler('newdog', show_dogs_image))
    updater.dispatcher.add_handler(CommandHandler('menu', wake_up))
    updater.dispatcher.add_handler(CommandHandler('now_time', show_now_time))
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('telegram_id', telegram_id))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling(poll_interval=5.0)
    updater.idle()


if __name__ == '__main__':
    main()
