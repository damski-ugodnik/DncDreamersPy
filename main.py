import os
import telebot
from telebot import types
import logging
import nice_words_generator
import psycopg2
from flask import Flask, request
from config import *
import locale_manager

bot = telebot.TeleBot(BOT_TOKEN)
app_server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def get_lang_from_db(user_id: int):
    db_object.execute(f"SELECT lang FROM users WHERE telegram_id = %s", (user_id,))
    lang = f"{db_object.fetchone()[0].strip()}"
    return lang


@bot.message_handler(commands=['mainmenu'])
def show_menu(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang_from_db(user_id=user_id)
    bot.send_message(user_id, locale_manager.main_menu(lang=lang), reply_markup=gen_main_menu(lang=lang))


def gen_main_menu(lang: str):
    main_menu = types.InlineKeyboardMarkup()
    buttons_text = locale_manager.menu_buttons(lang=lang)
    main_menu.add(
        types.InlineKeyboardButton(f"{buttons_text[0]}", callback_data="enroll"),
        types.InlineKeyboardButton(f"{buttons_text[1]}", callback_data="check_enrollments")
    )
    return main_menu


@bot.callback_query_handler(func=lambda call: call.data == 'enroll')
def enroll_user(call: types.CallbackQuery):
    pass


@bot.message_handler(commands=['start'])
def start_msg(message: types.Message):
    user_id = message.from_user.id
    db_object.execute(f"SELECT telegram_id FROM users WHERE telegram_id= %s", (user_id,))
    result = db_object.fetchone()
    if not result:
        choose_lang(message)
    else:
        lang = get_lang_from_db(user_id=user_id)
        bot.send_message(message.chat.id, locale_manager.greeting(lang), reply_markup=types.ReplyKeyboardRemove())
        show_menu(message=message)


@bot.message_handler(func=lambda message: message.text == 'English' or message.text == 'Українська')
def lang_chosen(message: types.Message):
    lang = message.text
    user_id = message.from_user.id
    db_object.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (user_id,))
    result = db_object.fetchone()
    msg_to_send: str
    if not result:
        db_object.execute("INSERT INTO users(telegram_id, lang) VALUES (%s, %s)", (user_id, lang))
        msg_to_send = locale_manager.greeting(lang=lang)
    else:
        db_object.execute("UPDATE users SET lang = %s WHERE telegram_id = %s", (lang, user_id))
        msg_to_send = locale_manager.lang_choice(lang)
    db_connection.commit()
    bot.send_message(message.chat.id, msg_to_send, reply_markup=types.ReplyKeyboardRemove())
    show_menu(message=message)


@bot.message_handler(commands=['changelang'])
def choose_lang(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Українська", "English"]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Please choose language / Будь-ласка оберіть мову', reply_markup=markup)


@bot.message_handler(commands=['slavaukraini'])
def nicewords_msg(message: telebot.types.Message):
    bot.send_message(message.chat.id, nice_words_generator.generate_some_taunts())


@app_server.route("/" + BOT_TOKEN, methods=["POST"])
def redirect_msg():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    app_server.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
