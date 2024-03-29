def greeting(lang: str):
    if lang == 'English':
        return 'Hello, this bot is created to make event enrollments easier and faster'
    elif lang == 'Українська':
        return 'Привіт, цей бот створений, щоб зробити запис на заходи зручнішим та швидшим'


def lang_choice(lang: str):
    if lang == 'English':
        return f'Language successfully set to : {lang}'
    elif lang == 'Українська':
        return f'Мову успішно встановлено на: {lang}'


def main_menu(lang: str):
    match lang:
        case 'English':
            return 'Main menu'
        case 'Українська':
            return 'Головне меню'


def menu_buttons(lang: str):
    match lang:
        case 'English':
            return 'Enroll', 'Your enrollments'
        case 'Українська':
            return 'Записатися', 'Ваші записи'


def participant(lang: str):
    eng_dict = {
        'couple': 'Couple',
        'solo': 'Solo',
        'coach': 'Coach'
    }
    ukr_dict = {
        'couple': 'Пара',
        'solo': 'Соло',
        'coach': 'Тренер'
    }
    match lang:
        case 'English':
            return eng_dict
        case 'Українська':
            return ukr_dict


def insert_your_name_single(lang: str):
    match lang:
        case 'English':
            return 'Insert your name and surname:'
        case 'Українська':
            return 'Введіть ваше прізвище та ім\'я'


def insert_your_name_couple(lang: str):
    match lang:
        case 'English':
            return 'Insert name and surname of you and your partner'
        case 'Українська':
            return 'Введіть ваше прізвище та ім\'я та П.І. партнера'


def dance_programs(lang: str):
    match lang:
        case 'English':
            return ['Ballroom', 'Latin', '10 dance']
        case 'Українська':
            return ['Стандарт', 'Латина', '10 танців']


def insert_program(lang: str):
    match lang:
        case 'English':
            return 'Insert your dancing program'
        case 'Українська':
            return 'Введіть вашу танцювальну програму'


def age_categories(lang: str):
    match lang:
        case 'English':
            return [['Under 10', 'Under 12', 'Under 14', 'Under 16'], ['Under 19', 'Under 21', 'Over 21', 'Pro-Am']]
        case 'Українська':
            return [['До 10 років', 'До 12 років', 'До 14 років', 'До 16 років'],
                    ['До 19 років', 'До 21 року', 'Більше 21 року', 'Про-Ам']]


def classes(lang: str):
    match lang:
        case 'English':
            return [['Attestation', 'N', 'E'], ['D', 'C', 'Rating']]
        case 'Українська':
            return [['Аттестація', 'N', 'E'],
                    ['D', 'C', 'Рейтинг']]


def insert_town(lang: str):
    match lang:
        case 'English':
            return 'Insert your town:'
        case 'Українська':
            return 'Введіть ваше місто:'


def insert_club(lang: str):
    match lang:
        case 'English':
            return 'Insert your club'
        case 'Українська':
            return 'Введіть назву вашого клубу'


def insert_coach(lang: str):
    match lang:
        case 'English':
            return 'Insert your coach Name and Surname'
        case 'Українська':
            return 'Введіть прізвище та ім\'я вашого тренера'


def insert_phone_number(lang: str):
    match lang:
        case 'English':
            return 'Insert your phone number\n' \
                   'Press the button below⬇️'
        case 'Українська':
            return 'Введіть ваш номер телефону\n' \
                   'Натисність кнопку внизу ⬇️'


def phone_number(lang: str):
    match lang:
        case 'English':
            return 'Phone number'
        case 'Українська':
            return 'Номер телефону'


def insert_age_category(lang: str):
    match lang:
        case 'English':
            return 'Insert your age category'
        case 'Українська':
            return 'Введіть вашу вікову категорію'


def info_processing(lang: str):
    match lang:
        case 'English':
            return 'You consent to the processing of personal data (According to Law No. 34 "On the Protection of Personal Data")\n' \
                   'Answer (Yes) (if the answer is no, the bot will not accept this enrollment)'
        case 'Українська':
            return 'Даєте згоду на обробку особистих даних (Згідно з законом  №34 «Про захист персональних даних»)\n' \
                   'Відповідь (Так) (якщо відповідь – ні, бот не прийме цей запис)'


def yes(lang: str):
    match lang:
        case 'English':
            return 'Yes'
        case 'Українська':
            return 'Так'


def no(lang: str):
    match lang:
        case 'English':
            return 'No'
        case 'Українська':
            return 'Ні'


def enrollment_thanks(lang: str):
    match lang:
        case 'English':
            return 'Thank you for enrollment'
        case 'Українська':
            return 'Дякуємо за ваш запис'


def enrollment_not_accepted(lang: str):
    match lang:
        case 'English':
            return 'Enrollment can not be processed'
        case 'Українська':
            return 'Запис не може бути опрацьований'


def ask_for_type(lang: str):
    match lang:
        case 'English':
            return 'Insert the type of participant'
        case 'Українська':
            return 'Введіть тип учасника'


def insert_class(lang: str):
    match lang:
        case 'English':
            return 'Insert your dancing class'
        case 'Українська':
            return 'Введіть ваш танцювальний клас'


def event_msg_format(lang: str):
    match lang:
        case 'English':
            return "Name:    {event_name}\n" \
                   "Date:    {date}\n" \
                   "Town:    {town}\n" \
                   "Address: {address}\n"
        case 'Українська':
            return "Назва:  {event_name}\n" \
                   "Дата:   {date}\n" \
                   "Місто:  {town}\n" \
                   "Адреса: {address}\n"


def enrollment_msg_format(lang: str):
    match lang:
        case 'English':
            return "Participant:  {participant_name}\n" \
                   "Event:        {event}\n" \
                   "Date:         {date}\n" \
                   "Age category: {age_category}\n"
        case 'Українська':
            return "Учасник:          {participant_name}\n" \
                   "Захід:            {event}\n" \
                   "Дата:             {date}\n" \
                   "Тип:              {type}\n" \
                   "Вікова категорія: {age_category}\n" \
                   "Клас:             {dance_class}\n" \
                   "Програма:         {dance_program}"


def enrollment_msg_coach_format(lang: str):
    match lang:
        case 'English':
            return "Participant:  {participant_name}\n" \
                   "Event:        {event}\n" \
                   "Date:         {date}\n" \
                   "Age category: {age_category}\n"
        case 'Українська':
            return "Учасник:  {participant_name}\n" \
                   "Захід:    {event}\n" \
                   "Дата:     {date}\n" \
                   "Тип:      {type}"


def event_msg_long_format(lang: str):
    match lang:
        case 'English':
            return "Name:    {event_name}\n" \
                   "Dates:   {date} - {date_until}\n" \
                   "Town:    {town}\n" \
                   "Address: {address}\n"
        case 'Українська':
            return "Назва:  {event_name}\n" \
                   "Дати:   {date} - {date_until}\n" \
                   "Місто:  {town}\n" \
                   "Адреса: {address}\n"


def events(lang: str):
    match lang:
        case 'English':
            return 'Events:'
        case 'Українська':
            return 'Заходи:'
