import os
import telebot
import logging
import nice_words_generator
from flask import Flask, request
from config import *

bot = telebot.TeleBot(BOT_TOKEN)
app_server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
def start_msg(message: telebot.types.Message):
    username = message.from_user.username
    bot.reply_to(message, f"Hello, {username}")

@bot.message_handler(commands=['slavaukraini'])
def nicewords_msg(message: telebot.types.Message):
    bot.reply_to(message, nice_words_generator.TauntsGenerator.generate_some_taunts())


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
