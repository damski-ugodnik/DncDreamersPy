import os
import telebot
from telebot import types
import logging
import nice_words_generator
import psycopg2
from flask import Flask, request
from config import *
import localization_manager

bot = telebot.TeleBot(BOT_TOKEN)
app_server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
taunts = nice_words_generator.TauntsGenerator()
db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


@bot.message_handler(content_types=['text'])
def msg_handler(message: types.Message):
    user_id = message.from_user.id
    db_object.execute("SELECT Language FROM Users Where TelegramID = %s", user_id)
    lang = db_object.fetchone()
    bot.send_message(message.chat.id, localization_manager.greeting(language=lang))


@bot.message_handler(commands=['start'])
def start_msg(message: types.Message):
    user_id = message.from_user.id
    db_object.execute("SELECT TelegramID FROM Users WHERE TelegramID= %s", user_id)
    result = db_object.fetchone()
    if not result:
        choose_lang(message)
    else:
        db_object.execute("SELECT Language FROM Users Where TelegramID = %s", user_id)
        lang = db_object.fetchone()
        bot.send_message(message.chat.id, localization_manager.greeting(language=lang))


@bot.message_handler(func=lambda message: message.text == 'English' or message.text == 'Українська')
def lang_chosen(message: types.Message):
    user_id = message.from_user.id
    db_object.execute("SELECT TelegramID FROM Users WHERE TelegramID = %s", user_id)
    result = db_object.fetchone()
    if not result:
        db_object.execute("INSERT INTO Users(TelegramID, Language) VALUES (%s, %s)", (user_id, message.text))
    else:
        db_object.execute("UPDATE Users SET Language = %s WHERE TelegramID = %s", (message.text,user_id))
    db_connection.commit()


def choose_lang(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Українська", "English"]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Please choose language / Будь-ласка оберіть мову', reply_markup=markup)


@bot.message_handler(commands=['slavaukraini'])
def nicewords_msg(message: telebot.types.Message):
    bot.send_message(message.chat.id, taunts.generate_some_taunts())


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
