import logging
import os

import psycopg2
import telebot
from flask import Flask, request
from telebot import types
import datetime

import db_manager
import locale_manager
import nice_words_generator
from config import *

bot = telebot.TeleBot(BOT_TOKEN)
app_server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()
lang = 'Українська'


def terminate_operations(user_id: int):
    db_object.execute("DELETE FROM enrollments WHERE filled = FALSE AND user_id = %s", (user_id,))
    db_connection.commit()
    db_object.execute("UPDATE users SET current_operation = null WHERE telegram_id = %s", (user_id,))
    db_connection.commit()


# def get_lang_from_db(user_id: int):
#     db_object.execute(f"SELECT lang FROM users WHERE telegram_id = %s", (user_id,))
#     lang = db_object.fetchone()
#     if not lang:
#         return ''
#     return lang


@bot.callback_query_handler(func=lambda call: str(call.data).find('_delete') > -1)
def delete_enrollment(call: types.CallbackQuery):
    enr_id = int(call.data[:str(call.data).find('_delete')])
    db_manager.delete_enr(enr_id)
    bot.answer_callback_query(call.id, f"Deleted")
    back(call)


@bot.message_handler(commands=['menu'])
def show_menu(message: types.Message):
    user_id = message.from_user.id
    terminate_operations(user_id)
    bot.send_message(user_id, locale_manager.main_menu(lang=lang), reply_markup=gen_main_menu())


def gen_main_menu():
    main_menu = types.InlineKeyboardMarkup()
    buttons_text = locale_manager.menu_buttons(lang=lang)
    main_menu.add(
        types.InlineKeyboardButton(f"{buttons_text[0]}", callback_data="show_events"),
        types.InlineKeyboardButton(f"{buttons_text[1]}", callback_data="check_enrollments")
    )
    return main_menu


def create_enrollments_list(enrollments: dict[str, str]):
    enrollments_menu = types.InlineKeyboardMarkup(row_width=1)
    for key in enrollments:
        text = enrollments[key]
        button = types.InlineKeyboardButton(text=text, callback_data=key + "_enrollment")
        enrollments_menu.add(button)
    enrollments_menu.add(types.InlineKeyboardButton(text='⬅', callback_data='menu'))
    return enrollments_menu


@bot.callback_query_handler(func=lambda call: call.data == 'check_enrollments')
def check_enrollments(call: types.CallbackQuery):
    user_id = call.from_user.id
    enrollments = db_manager.fetch_enrollments(user_id)
    text = "Your enrollments:" if lang == 'English' else "Ваші записи:"
    bot.send_message(user_id, text, reply_markup=create_enrollments_list(enrollments))


@bot.callback_query_handler(func=lambda call: str(call.data).find('_enrollment') > -1)
def show_chosen_enrollment(call: types.CallbackQuery):
    enrollment_id = int(call.data[:call.data.find('_enrollment')])

    def configure_enrollment_msg():
        user_id = call.from_user.id
        enrollment = db_manager.fetch_enrollment(enrollment_id)

        def gen_markup_for_enrollment_msg():
            markup = types.InlineKeyboardMarkup(row_width=3)
            match lang:
                case 'English':
                    markup.add(types.InlineKeyboardButton('Delete', callback_data=f'{enrollment_id}_delete'),
                               types.InlineKeyboardButton('Back', callback_data='check_enrollments'))
                case 'Українська':
                    markup.add(types.InlineKeyboardButton('Видалити', callback_data=f'{enrollment_id}_delete'),
                               types.InlineKeyboardButton('Назад', callback_data='check_enrollments'))

            return markup

        def configure_text():
            if enrollment[3] == 'Тренер':
                return locale_manager.enrollment_msg_coach_format(lang).format(
                    participant_name=enrollment[0],
                    event=enrollment[1],
                    date=enrollment[2],
                    type=enrollment[3]
                )
            else:
                return locale_manager.enrollment_msg_format(lang).format(
                    participant_name=enrollment[0],
                    event=enrollment[1],
                    date=enrollment[2],
                    type=enrollment[3],
                    age_category=enrollment[4],
                    dance_class=enrollment[5],
                    dance_program=enrollment[6]
            )

        bot.send_message(user_id, configure_text(), reply_markup=gen_markup_for_enrollment_msg())

    configure_enrollment_msg()


def create_events_list(events):
    events_menu = types.InlineKeyboardMarkup(row_width=1)
    for event in events:
        button = types.InlineKeyboardButton(text=f"{event.name}", callback_data=f"{event.event_id}" + "_event")
        events_menu.add(button, row_width=1)
    events_menu.add(types.InlineKeyboardButton(text='⬅', callback_data='menu'))
    return events_menu


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def back(call: types.CallbackQuery):
    user_id = call.from_user.id
    bot.send_message(user_id, locale_manager.main_menu(lang=lang), reply_markup=gen_main_menu())


@bot.callback_query_handler(func=lambda call: call.data == 'show_events')
def show_events(call: types.CallbackQuery):
    events = db_manager.fetch_events()
    user_id = call.from_user.id
    text = "Upcoming events:" if lang == 'English' else "Майбутні заходи"
    bot.send_message(chat_id=user_id, text=text, reply_markup=create_events_list(events=events))


@bot.callback_query_handler(func=lambda call: str(call.data).find('_event') > -1)
def show_chosen_event(call: types.CallbackQuery):
    event_id = int(call.data[:call.data.find('_event')])

    def configure_event_msg():
        user_id = call.from_user.id
        event = db_manager.fetch_event(event_id=event_id)

        def gen_markup_for_event_msg():
            markup = types.InlineKeyboardMarkup(row_width=2)
            match lang:
                case 'English':
                    markup.add(types.InlineKeyboardButton('Enroll', callback_data=f'{event_id}_enroll'),
                               types.InlineKeyboardButton('Back', callback_data='show_events'),
                               )
                    if event.url is not None:
                        markup.add(types.InlineKeyboardButton('Full information', url=event.url))
                case 'Українська':
                    markup.add(types.InlineKeyboardButton('Записатися', callback_data=f'{event_id}_enroll'),
                               types.InlineKeyboardButton('Назад', callback_data='show_events'))
                    if event.url is not None:
                        markup.add(types.InlineKeyboardButton('Повна інформація', url=event.url))
            return markup

        def configure_text():
            if str(event.date_until).__eq__('None'):
                text = locale_manager.event_msg_format(lang)
                return text.format(event_name=event.name,
                                   date=event.date_of_issue,
                                   town=event.town,
                                   address=event.place)
            else:
                text = locale_manager.event_msg_long_format(lang)
                return text.format(event_name=event.name,
                                   date=event.date_of_issue,
                                   date_until=event.date_until,
                                   town=event.town,
                                   address=event.place)

        bot.send_message(user_id, configure_text(), reply_markup=gen_markup_for_event_msg())

    configure_event_msg()


def not_command(text: str):
    return text.find("/") != 0


@bot.callback_query_handler(func=lambda call: call.data.find("_enroll") >= 0)
def enroll_event(call: types.CallbackQuery):
    if call.data.endswith("_enroll"):
        event_id = int(call.data[:call.data.find("_enroll")])
        user_id = call.from_user.id
        db_manager.init_enrollment(event_id=event_id, user_id=user_id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        text = locale_manager.participant(lang)
        buttons = [text["couple"], text["solo"], text["coach"]]
        markup.add(*buttons)
        bot.send_message(call.from_user.id, locale_manager.ask_for_type(lang=lang), reply_markup=markup)


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_type') and not_command(message.text))
def set_participant_type(message: types.Message):
    user_id = message.from_user.id
    text: str
    typ = locale_manager.participant(lang)
    for t in typ:
        if message.text.__eq__(typ[t]):
            db_manager.set_type(user_id, message.text)
            if message.text == locale_manager.participant(lang)["couple"]:
                text = locale_manager.insert_your_name_couple(lang)
            else:
                text = locale_manager.insert_your_name_single(lang)
            bot.send_message(message.from_user.id, text, reply_markup=types.ReplyKeyboardRemove())
            return
    bot.send_message(user_id, locale_manager.ask_for_type(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_name') and not_command(message.text))
def set_name(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_name(user_id=user_id, name=message.text)
    bot.send_message(user_id, locale_manager.insert_town(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_town') and not_command(message.text))
def set_town(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_town(user_id=user_id, town=message.text)
    bot.send_message(user_id, locale_manager.insert_club(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_club') and not_command(message.text))
def set_club(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_club(user_id, message.text)


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_program') and not_command(message.text))
def set_program(message: types.Message):
    user_id = message.from_user.id
    programs = locale_manager.dance_programs(lang)
    for pr in programs:
        if message.text.__eq__(pr):
            db_manager.set_program(user_id, message.text)
            buttons = locale_manager.age_categories(lang)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*buttons[0])
            markup.add(*buttons[1])
            bot.send_message(user_id, locale_manager.insert_age_category(lang), reply_markup=markup)
            return
    bot.send_message(user_id, locale_manager.insert_program(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_coach') and not_command(message.text))
def set_coach(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_coach(user_id, message.text)
    buttons = locale_manager.dance_programs(lang)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*buttons)
    bot.send_message(user_id, locale_manager.insert_program(lang), reply_markup=markup)


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_age_category') and not_command(message.text))
def set_age_category(message: types.Message):
    user_id = message.from_user.id
    categories = locale_manager.age_categories(lang)
    for s in categories:
        for category in s:
            if message.text.__eq__(category):
                db_manager.set_age_category(user_id, message.text)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                classes = locale_manager.classes(lang)
                markup.add(*classes[0])
                markup.add(*classes[1])
                bot.send_message(user_id, locale_manager.insert_class(lang), reply_markup=markup)
                return
    bot.send_message(user_id, locale_manager.insert_age_category(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_class') and not_command(message.text))
def set_class(message: types.Message):
    user_id = message.from_user.id
    classes = locale_manager.classes(lang)
    for s in classes:
        for _class in s:
            if message.text.__eq__(_class):
                db_manager.set_class(user_id, message.text)
                phone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button = types.KeyboardButton(locale_manager.phone_number(lang), request_contact=True)
                phone_markup.add(button)
                bot.send_message(user_id, locale_manager.insert_phone_number(lang), reply_markup=phone_markup)
                return
    bot.send_message(user_id, locale_manager.insert_class(lang))


@bot.message_handler(
    func=lambda message: determine_operation(message.from_user.id, 'set_phone_number'),
    content_types=['contact'])
def set_phone_number(message: types.Message):
    user_id = message.from_user.id
    db_manager.set_phone_number(user_id, message.contact.phone_number)
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_yes = types.InlineKeyboardButton(locale_manager.yes(lang), callback_data='True')
    button_no = types.InlineKeyboardButton(locale_manager.no(lang), callback_data='False')
    markup.add(button_yes, button_no)
    bot.send_message(user_id, locale_manager.info_processing(lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: determine_operation(call.from_user.id, 'set_info_processing'))
def set_info_processing(call: types.CallbackQuery):
    user_id = call.from_user.id
    if call.data.__eq__('True'):
        db_manager.set_info_processing(user_id, True)
    else:
        bot.send_message(user_id, locale_manager.enrollment_not_accepted(lang),
                         reply_markup=types.ReplyKeyboardRemove())

    bot.send_message(user_id, locale_manager.enrollment_thanks(lang), reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(user_id, locale_manager.main_menu(lang=lang), reply_markup=gen_main_menu())
    db_object.execute(f"UPDATE enrollments SET filled = {True} WHERE user_id = {user_id}")
    db_connection.commit()


def determine_operation(user_id: int, operation_name: str):
    try:
        db_object.execute(f"SELECT current_operation FROM users WHERE telegram_id = {user_id}")
        result = db_object.fetchone()
        if not result:
            return ""
        res = str(result[0]).strip().__eq__(operation_name.strip())
        return res
    except psycopg2.DatabaseError:
        db_object.execute("ROLLBACK")


@bot.message_handler(commands=['start'])
def start_msg(message: types.Message):
    user_id = message.from_user.id
    terminate_operations(user_id)
    db_object.execute(f"SELECT telegram_id FROM users WHERE telegram_id= %s", (user_id,))
    result = db_object.fetchone()
    if not result:
        db_object.execute("INSERT INTO users(telegram_id, lang) VALUES (%s, %s)", (user_id, lang))
    bot.send_message(message.chat.id, locale_manager.greeting(lang), reply_markup=types.ReplyKeyboardRemove())
    show_menu(message=message)


@bot.callback_query_handler(func=lambda call: call.data == "English" or call.data == "Українська")
def lang_chosen(call: types.CallbackQuery):
    user_id = call.from_user.id
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
    bot.send_message(user_id, msg_to_send, reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(user_id, locale_manager.main_menu(lang=lang), reply_markup=gen_main_menu())


@bot.message_handler(commands=['changelang'])
def choose_lang(message: types.Message):
    terminate_operations(message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("English", callback_data="English"))
    markup.add(types.InlineKeyboardButton("Українська", callback_data="Українська"))
    bot.send_message(message.chat.id, 'Please choose language / Будь-ласка оберіть мову', reply_markup=markup)


@bot.message_handler(commands=['slavaukraini'])
def nicewords_msg(message: telebot.types.Message):
    terminate_operations(message.from_user.id)
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
