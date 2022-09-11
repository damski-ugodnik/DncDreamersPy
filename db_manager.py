from main import db_object, db_connection
from datetime import date


def init_enrollment(event_id: int, user_id: int):
    db_object.execute(f"SELECT enrollment_id FROM enrollments WHERE filled = FALSE AND user_id = {user_id}")
    res = db_object.fetchall()
    if not not res:
        for i in res:
            db_object.execute(f"DELETE FROM enrollments WHERE enrollment_id = {i[0]}")
    db_object.execute(f"INSERT INTO enrollments(event_id, user_id, filled) VALUES({event_id},{user_id}, {False})")
    db_connection.commit()


def set_type(user_id: int, participant):
    db_object.execute(
        f"UPDATE enrollments SET participant_type = %s WHERE user_id = {user_id} AND filled = FALSE", (participant,))
    db_connection.commit()


def fetch_event(event_id: int):
    db_object.execute(f"SELECT * FROM events WHERE id = {event_id}")

    result = db_object.fetchone()

    res_event = Event(event_id=result[0],
                      name=result[1].strip(),
                      date_of_issue=result[2],
                      town=result[3].strip(),
                      place=result[4].strip(),
                      price=int(result[5]),
                      additional=result[6].strip())
    return res_event


def fetch_events():
    db_object.execute(f"SELECT * FROM events")
    result = db_object.fetchall()
    events = list()
    for event_row in result:
        event = Event(event_id=event_row[0],
                      name=event_row[1].strip(),
                      date_of_issue=event_row[2],
                      town=event_row[3].strip(),
                      place=event_row[4].strip(),
                      price=int(event_row[5]),
                      additional=event_row[6].strip())
        events.append(event)
    return events


def fetch_enrollments(user_id: int):
    db_object.execute(f"SELECT * FROM enrollments WHERE user_id = {user_id}")
    result = db_object.fetchall()
    enrollments = list()
    for enrollment_row in result:
        enrollment = Enrollment(event_id=enrollment_row[0],
                                user_id=enrollment_row[1],
                                first_name=enrollment_row[2].strip(),
                                last_name=enrollment_row[3].strip(),
                                town=enrollment_row[4].strip(),
                                participant_type=enrollment_row[5].strip(),
                                club=enrollment_row[6].strip(),
                                coach=enrollment_row[7].strip(),
                                age_category=enrollment_row[8].strip(),
                                date_of_birth=enrollment_row[9],
                                phone_number=enrollment_row[10].strip(),
                                allows_info_processing=enrollment_row[11],
                                paid=enrollment_row[12]
                                )
        enrollments.append(enrollment)
    return enrollments


class Enrollment:
    __event_id: int
    __user_id: int
    __first_name: str
    __last_name: str
    __town: str
    __participant_type: str
    __club: str
    __coach: str
    __age_category: str
    __date_of_birth: date
    __phone_number: str
    __allows_info_processing: bool
    __paid: bool

    def __init__(self, event_id: int, user_id: int, first_name: str, last_name: str, town: str, participant_type: str,
                 club: str, coach: str, age_category: str, date_of_birth: date, phone_number: str,
                 allows_info_processing: bool, paid: bool):
        self.__event_id = event_id
        self.__user_id = user_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__town = town
        self.__participant_type = participant_type
        self.__club = club
        self.__coach = coach
        self.__age_category = age_category
        self.__date_of_birth = date_of_birth
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
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

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
    def date_of_birth(self):
        return self.__date_of_birth

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
    __town: str
    __place: str
    __price: int
    __additional: str

    def __init__(self, event_id: int, name: str, date_of_issue: date, town: str, place: str, price: int,
                 additional: str):
        self.__event_id = event_id
        self.__name = name
        self.__date_of_issue = date_of_issue
        self.__town = town
        self.__place = place
        self.__price = price
        self.__additional = additional

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
