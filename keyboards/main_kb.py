from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from create_bot import admins


def make_main_kb(user_telegram_id: int):
    kb_list = [
                [KeyboardButton(text='Описание бота')],
                [KeyboardButton(text='Найти игрока'), KeyboardButton(text='Добавить игрока')],
                [KeyboardButton(text='Список игроков + описание')]
    ]

    if user_telegram_id in admins:
        kb_list.append(
                        [KeyboardButton(text='Список пользователей')]
        )

    keyboard =  ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Юзай клаву')
    return keyboard