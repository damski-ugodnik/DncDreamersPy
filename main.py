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


def gen_main_menu():
    main_menu = types.InlineKeyboardMarkup()
    main_menu.add(
        types.InlineKeyboardButton("enroll", callback_data="enroll"),
        types.InlineKeyboardButton("show", callback_data="check_enrollments")
    )
    return main_menu


@bot.callback_query_handler(func=lambda call: call.data == 'enroll')
def enroll_user(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id,text="okay then")


@bot.message_handler(commands=['start'])
def start_msg(message: types.Message):
    user_id = message.from_user.id
    db_object.execute(f"SELECT telegram_id FROM users WHERE telegram_id= %s", (user_id,))
    result = db_object.fetchone()
    if not result:
        choose_lang(message)
    else:
        db_object.execute(f"SELECT lang FROM users WHERE telegram_id = %s", (user_id,))
        lang = f"{db_object.fetchone()[0].strip()}"
        bot.send_message(message.chat.id, locale_manager.greeting(lang), reply_markup=gen_main_menu())


@bot.message_handler(func=lambda message: message.text == 'English' or message.text == 'Українська')
def lang_chosen(message: types.Message):
    lang = message.text
    user_id = message.from_user.id
    db_object.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (user_id,))
    result = db_object.fetchone()
    msg_to_send: str
    if not result:
        db_object.execute("INSERT INTO users(telegram_id, lang) VALUES (%s, %s)", (user_id, lang))
        msg_to_send = locale_manager.greeting(language=lang)
    else:
        db_object.execute("UPDATE users SET lang = %s WHERE telegram_id = %s", (lang, user_id))
        msg_to_send = locale_manager.lang_choice(lang)
    db_connection.commit()
    bot.send_message(message.chat.id, msg_to_send, reply_markup=types.ReplyKeyboardRemove())


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
