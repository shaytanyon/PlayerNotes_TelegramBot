from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import sqlite3
from create_bot import bot
from keyboards.main_kb import make_main_kb


start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()

        cursor.execute(f'SELECT id FROM users WHERE telegram_id = {message.from_user.id}')
        result = cursor.fetchall()

        if not result:
            cursor.execute('INSERT INTO users (name, telegram_id) VALUES (?, ?)', (message.from_user.username, message.from_user.id))

    await message.answer('Здаров. Юзай тг меню около клавиатуры', reply_markup=make_main_kb(message.from_user.id))


@start_router.message(F.text == 'Описание бота')
async def cmd_about(message: Message):
    with open('about.txt', 'r', encoding='utf-8') as f:
        text = ''.join(f.readlines())
        await message.answer(text)


@start_router.message(F.text == 'Список пользователей')
async def cmd_users(message: Message):
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM users')
        result = "\n".join(
                        list(
                            map(
                                lambda x: " || ".join([ str(x[0]), str(x[1]), str(x[2]) ]),
                                cursor.fetchall()
                                )
                            )
                        )
        
        if result:
            await message.answer(result)
        else:
            await message.answer('Пустота')


@start_router.message(F.text == 'Список игроков + описание')
async def cmd_get_players(message: Message):
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT nickname, note FROM players')
        result = '\n\n'.join(
            list(
                map(
                    lambda x: ': '.join( [str(x[0]), str(x[1])] ),
                    cursor.fetchall()
                )
            )
        )
        if result:
            await message.answer(result)
        else:
            await message.answer('Пока тут пусто')