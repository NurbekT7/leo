from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_start_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да! Погнали 🚀")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_gender_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Я парень 👦"), KeyboardButton(text="Я девушка 👧")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_search_gender_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Парни 👦"), KeyboardButton(text="Девушки 👧")],
            [KeyboardButton(text="Все равно 🤝")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_name_kb(tg_name: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"Оставить как в ТГ ({tg_name})")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить геолокацию 📍", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_main_menu_kb(is_active=True):
    kb = [
        [KeyboardButton(text="Смотреть анкеты 🔥")],
        [KeyboardButton(text="👤 Моя анкета")]
    ]

    if is_active:
        kb.append([KeyboardButton(text="Скрыть анкету 🚫")])
    else:
        kb.append([KeyboardButton(text="Опубликовать анкету ✅")])

    kb.append([KeyboardButton(text="Заполнить заново 📝")])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_finish_media_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Готово ✅")]
        ]
    )

def get_browse_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️"), KeyboardButton(text="👎"), KeyboardButton(text="💤")]
        ],
        resize_keyboard=True
    )

def get_profile_edit_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Заполнить заново 📝")],
            [KeyboardButton(text="Назад в меню 🏠")]
        ],
        resize_keyboard=True
    )