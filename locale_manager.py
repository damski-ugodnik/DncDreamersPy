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
            return ['Enroll', 'Your enrollments']
        case 'Українська':
            return ['Записатися', 'Ваші записи']


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


def age_categories(lang: str):
    match lang:
        case 'English':
            return [['Under 10', 'Under 12', 'Under 14', 'Under 16'], ['Under 19', 'Under 21', 'Over 21']]
        case 'Українська':
            return [['До 10 років', 'До 12 років', 'До 14 років', 'До 16 років'],
                    ['До 19 років', 'До 21 року', 'Більше 21 року']]
