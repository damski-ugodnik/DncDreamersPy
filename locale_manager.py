
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
        case 'English': return 'Main menu'
        case 'Українська': return 'Головне меню'


def menu_buttons(lang: str):
    match lang:
        case 'English': return ['Enroll', 'Your enrollments']
        case 'Українська': return ['Записатися', 'Ваші записи']
