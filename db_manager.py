from typing import Any

import main
from main import db_object, db_connection, bot, types
from datetime import date
import locale_manager
from main import lang


def init_enrollment(event_id: int, user_id: int):
    db_object.execute(f"SELECT telegram_id FROM users WHERE telegram_id = {user_id}")
    if not db_object.fetchone():
        db_object.execute(f"INSERT INTO users(telegram_id) VALUES ({user_id})")
        db_connection.commit()
    db_object.execute(f"SELECT enrollment_id FROM enrollments WHERE filled = FALSE AND user_id = {user_id}")
    res = db_object.fetchall()
    if not not res:
        for i in res:
            db_object.execute(f"DELETE FROM enrollments WHERE enrollment_id = {i[0]}")
    db_object.execute(f"INSERT INTO enrollments(event_id, user_id, filled) VALUES({event_id},{user_id}, {False})")
    db_connection.commit()
    db_object.execute(f"UPDATE users SET current_operation = %s WHERE telegram_id = {user_id}", ('set_type',))
    db_connection.commit()


def set_type(user_id: int, participant: str):
    set_str_param_and_operation(user_id=user_id, param_name='participant_type', param_value=participant,
                                operation_name='set_name')


def set_name(user_id: int, name: str):
    main.logger.debug("setting name")
    set_str_param_and_operation(user_id=user_id, param_name='participant_name', param_value=name,
                                operation_name='set_town')


def set_town(user_id: int, town: str):
    set_str_param_and_operation(user_id=user_id, param_name='town', param_value=town,
                                operation_name='set_club')


def set_club(user_id: int, club: str):
    db_object.execute(f"SELECT participant_type FROM enrollments WHERE user_id = {user_id} AND filled = FALSE")
    p_type = db_object.fetchone()[0]
    eg = locale_manager.participant(main.lang)["coach"]
    operation: str
    if str(p_type).strip().__eq__(eg):
        operation = 'set_phone_number'
        phone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(locale_manager.phone_number(lang), request_contact=True)
        phone_markup.add(button)
        bot.send_message(user_id, locale_manager.insert_phone_number(lang), reply_markup=phone_markup)
    else:
        operation = 'set_coach'
        bot.send_message(user_id, locale_manager.insert_coach(lang))
    set_str_param_and_operation(user_id=user_id, param_name='club', param_value=club,
                                operation_name=operation)


def set_coach(user_id: int, coach: str):
    set_str_param_and_operation(user_id=user_id, param_name='coach', param_value=coach,
                                operation_name='set_program')


def set_age_category(user_id: int, age_category: str):
    set_str_param_and_operation(
        user_id=user_id, param_name='age_category', param_value=age_category, operation_name='set_class'
    )


def set_program(user_id: int, dance_program: str):
    set_str_param_and_operation(user_id, param_name='dance_program', param_value=dance_program,
                                operation_name='set_age_category')


def set_class(user_id: int, _class: str):
    set_str_param_and_operation(user_id, param_name='dance_class', param_value=_class,
                                operation_name='set_phone_number')


def set_phone_number(user_id: int, phone_number: str):
    set_str_param_and_operation(user_id=user_id, param_name='phone_number', param_value=phone_number,
                                operation_name='set_info_processing')


def set_info_processing(user_id: int, allows: bool):
    set_str_param_and_operation(user_id=user_id, param_name='allows_info_processing', param_value=str(allows),
                                operation_name=str(None))


def set_str_param_and_operation(user_id: int, param_name: str, param_value: str, operation_name: str):
    db_object.execute(f"UPDATE enrollments SET {param_name.strip()} = %s WHERE user_id = {user_id} AND filled = FALSE",
                      (param_value,))
    db_connection.commit()
    db_object.execute(f"UPDATE users SET current_operation = %s WHERE telegram_id = {user_id}",
                      (operation_name.strip(),))
    db_connection.commit()


def fetch_event(event_id: int):
    db_object.execute(f"SELECT * FROM events WHERE id = {event_id}")

    result = db_object.fetchone()
    if not result:
        return None
    res_event = Event(event_id=result[0],
                      name=result[1],
                      date_of_issue=result[2],
                      date_until=result[3],
                      town=result[4],
                      place=result[5],
                      additional="",
                      info_url=result[6])
    return res_event


def fetch_events():
    db_object.execute(f"SELECT * FROM events")
    result = db_object.fetchall()
    events = list()
    for event_row in result:
        event = Event(event_id=event_row[0],
                      name=event_row[1],
                      date_of_issue=event_row[2],
                      date_until=event_row[3],
                      town=event_row[4],
                      place=event_row[5],
                      additional="",
                      info_url=event_row[6])
        events.append(event)
    return events


def fetch_enrollments(user_id: int):
    db_object.execute(
        f"SELECT event_name, participant_name, enrollment_id FROM events INNER JOIN enrollments e on events.id = e.event_id and e.user_id = {user_id}")
    result = db_object.fetchall()
    brief_enrollments = dict()
    for enrollment_row in result:
        enrollment_str = enrollment_row[0].__str__().strip() + " - " + enrollment_row[1].__str__().strip()
        brief_enrollments[enrollment_row[2].__str__()] = enrollment_str
    return brief_enrollments


def fetch_enrollment(enrollment_id):
    db_object.execute(
        f"SELECT participant_name, event_name, date_of_issue, participant_type, age_category, dance_class, dance_program FROM enrollments INNER JOIN events e on e.id = enrollments.event_id and enrollment_id = {enrollment_id}")
    result = db_object.fetchone()
    return result


def delete_enr(enrollment_id: int):
    db_object.execute(f"DELETE FROM enrollments WHERE enrollment_id = {enrollment_id}")
    db_connection.commit()


class Enrollment:
    __event_id: int
    __user_id: int
    __participant_name: str
    __town: str
    __participant_type: str
    __club: str
    __coach: str
    __age_category: str
    __phone_number: str
    __allows_info_processing: bool
    __paid: bool

    def __init__(self, event_id: int, user_id: int, participant_name: str, town: str, participant_type: str,
                 club: str, coach: str, age_category: str, phone_number: str,
                 allows_info_processing: bool, paid: bool):
        self.__event_id = event_id
        self.__user_id = user_id
        self.__participant_name = participant_name
        self.__town = town
        self.__participant_type = participant_type
        self.__club = club
        self.__coach = coach
        self.__age_category = age_category
        self.__phone_number = phone_number
        self.__allows_info_processing = allows_info_processing
        self.__paid = paid

    @property
    def event_id(self):
        return self.__event_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def participant_name(self):
        return self.__participant_name

    @property
    def town(self):
        return self.__town

    @property
    def participant_type(self):
        return self.__participant_type

    @property
    def club(self):
        return self.__club

    @property
    def coach(self):
        return self.__coach

    @property
    def age_category(self):
        return self.__age_category

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def allows_info_processing(self):
        return self.__allows_info_processing

    @property
    def paid(self):
        return self.__paid


class Event:
    __event_id: int
    __name: str
    __date_of_issue: date
    __date_until: Any
    __town: str
    __place: str
    __price: Any
    __additional: Any
    __info_url: Any

    def __init__(self, event_id: int, name: str, date_of_issue: date, date_until: Any, town: str, place: str,
                 additional: Any, info_url: Any):
        self.__event_id = event_id
        self.__name = name
        self.__date_of_issue = date_of_issue
        self.__date_until = date_until
        self.__town = town
        self.__place = place
        self.__additional = additional
        self.__info_url = info_url

    @property
    def event_id(self):
        return self.__event_id

    @property
    def name(self):
        return self.__name

    @property
    def date_of_issue(self):
        return self.__date_of_issue

    @property
    def town(self):
        return self.__town

    @property
    def place(self):
        return self.__place

    @property
    def price(self):
        return self.__price

    @property
    def additional(self):
        return self.__additional

    @property
    def url(self):
        return self.__info_url

    @property
    def date_until(self):
        return self.__date_until
