import os
import telebot
from telebot import types
import logging
import nice_words_generator
import psycopg2
from flask import Flask, request
from config import *
import locale_manager
import db_manager

bot = telebot.TeleBot(BOT_TOKEN)
app_server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def get_lang_from_db(user_id: int):
    db_object.execute(f"SELECT lang FROM users WHERE telegram_id = %s", (user_id,))
    lang = db_object.fetchone()[0].strip()
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
        types.InlineKeyboardButton(f"{buttons_text[0]}", callback_data="show_events"),
        types.InlineKeyboardButton(f"{buttons_text[1]}", callback_data="check_enrollments")
    )
    return main_menu


def create_events_list(events: list):
    events_menu = types.InlineKeyboardMarkup(row_width=1)
    for event in events:
        button = types.InlineKeyboardButton(text=f"{event.name}", callback_data=f"{event.event_id}" + "_event")
        events_menu.add(button, row_width=1)
    return events_menu


@bot.callback_query_handler(func=lambda call: call.data == 'show_events')
def show_events(call: types.CallbackQuery):
    events = db_manager.fetch_events()
    user_id = call.from_user.id
    bot.answer_callback_query(callback_query_id=call.id, text="available events")
    bot.send_message(chat_id=user_id, text="events:", reply_markup=create_events_list(events=events))


@bot.callback_query_handler(func=lambda call: str(call.data).find('_event') > -1)
def show_chosen_event(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id, text=call.data)
    event_id = int(call.data[:call.data.find('_event')])

    def configure_event_msg():
        user_id = call.from_user.id
        event = db_manager.fetch_event(event_id=event_id)

        def gen_markup_for_event_msg():
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton('Enroll', callback_data=f'{event_id}_enroll'),
                       types.InlineKeyboardButton('Back', callback_data='show_events'))
            return markup

        def configure_text():
            text = f"{event.name}\n" \
                   f"{event.date_of_issue}\n" \
                   f"{event.town}\n" \
                   f"{event.place}\n" \
                   f"{event.price}\n" \
                   f"{event.additional}\n"
            return text

        bot.send_message(user_id, configure_text(), reply_markup=gen_markup_for_event_msg())

    configure_event_msg()


@bot.callback_query_handler(func=lambda call: call.data.find("_enroll"))
def enroll_event(call: types.CallbackQuery):
    event_id = int(call.data[:call.data.find("_enroll")])
    db_manager.init_enrollment(event_id=event_id, user_id=call.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = locale_manager.participant(get_lang_from_db(call.from_user.id))
    buttons = [text["couple"], text["solo"], text["coach"]]
    markup.add(*buttons)
    bot.send_message(call.from_user.id, "are you:", reply_markup=markup)


@bot.message_handler(func=lambda message: whether_participant_type(message=message))
def set_participant_type(message: types.Message):
    if whether_participant_type(message):
        db_manager.set_type(message.from_user.id, message.text)
        text: str
        if message.text == locale_manager.participant(get_lang_from_db(message.from_user.id))["couple"]:
            text = "Insert your name and surname and the name of your partner (You/Partner):"
        else:
            text = "Insert your name and surname:"
        bot.send_message(message.from_user.id, text, reply_markup=types.ReplyKeyboardRemove())


def whether_participant_type(message: types.Message):
    lang = get_lang_from_db(message.from_user.id)
    typ = locale_manager.participant(lang=lang)
    return message.text == str(typ["couple"]) or message.text == str(typ["solo"]) or message.text == str(typ["coach"])


@bot.message_handler(func=lambda message: (determine_operation(message.from_user.id) == "set_name"))
def set_name(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_name(user_id=user_id, name=message.text)
    bot.send_message(user_id, "Insert your town:")


@bot.message_handler(func=lambda message: determine_operation(message.from_user.id) == 'set_town')
def set_town(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_town(user_id=user_id, town=message.text)
    bot.send_message(user_id, "Insert your club:")


@bot.message_handler(func=lambda message: determine_operation(message.from_user.id) == 'set_club')
def set_club(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_club(user_id,message.text)
    bot.send_message(user_id, "Insert your coach: ")


@bot.message_handler(func= lambda message: determine_operation(message.from_user.id) == 'set_coach')
def set_coach(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_coach(user_id, message.text)
    buttons = ['U16', 'U19', 'U21']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*buttons)
    bot.send_message(user_id, "Insert your age category", reply_markup=markup)


def determine_operation(user_id: int):
    db_object.execute(f"SELECT current_operation FROM users WHERE telegram_id = {user_id}")
    result = db_object.fetchone()
    bot.send_message(user_id, str(result[0]))
    return str(result[0])



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
