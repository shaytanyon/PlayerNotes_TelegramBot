from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from create_bot import admins


def get_note_inl_kb():
    kb_list = [
        [InlineKeyboardButton(text='Добавить персонажа', callback_data='add_heroes'),
         InlineKeyboardButton(text='Добавить тиммейта', callback_data='add_teammate')],
         [InlineKeyboardButton(text='Готово', callback_data='done_create')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb_list)


def accept_decline():
    kb_list = [
        [InlineKeyboardButton(text='Подтвердить', callback_data='accept')],
        [InlineKeyboardButton(text='Отменить запись', callback_data='decline')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb_list)


def edit_inl_kb(user_id: int):
    kb_list = [
        [InlineKeyboardButton(text='Редактировать', callback_data='edit_player')]
    ]

    if user_id in admins:
        kb_list.append([InlineKeyboardButton(text='Удалить', callback_data='delete_player')])
    
    return InlineKeyboardMarkup(inline_keyboard=kb_list)


def edit_player_inl_kb():
    kb_list = [
        [InlineKeyboardButton(text='Добавить персонажей', callback_data='edit_heroes')],
        [InlineKeyboardButton(text='Добавить тиммейтов', callback_data='edit_teammates')],
        [InlineKeyboardButton(text='Готово', callback_data='edit_done')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb_list)