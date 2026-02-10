from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import sqlite3
from create_bot import bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline_kb import get_note_inl_kb, accept_decline, edit_inl_kb, edit_player_inl_kb

player_handler = Router()

class Player(StatesGroup):
    id = State()
    nickname = State()
    note = State()
    heroes = State()
    hero = State()
    teammates = State()
    teammate = State()


class FindPlayer(StatesGroup):
    nickname = State()
    hero = State()
    teammate = State()


@player_handler.message(F.text == 'Добавить игрока')
async def cmd_add_player(message: Message, state: FSMContext):
    await state.set_state(Player.nickname)
    await message.answer('Введи никнейм игрока')


@player_handler.message(Player.nickname)
async def get_nickname(message: Message, state: FSMContext):
    text = message.text.split()[0]  
    await state.update_data(nickname=text)
    data = await state.get_data()
    nickname = data['nickname']

    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM players WHERE nickname = '%s'" % (nickname,) )
        result = cursor.fetchall()
        if result:
            await message.answer('Игрок с таким ником уже записан в базу')
            await state.clear()
        else:
            await message.answer('Добавь описание игрока')
            await state.set_state(Player.note)


@player_handler.message(Player.note)
async def get_note(message: Message, state: FSMContext):
    await state.update_data(note=message.text)
    await state.update_data(heroes='')
    await state.update_data(teammates='')
    await message.answer('Отлично. Выбери следующее действие', reply_markup=get_note_inl_kb())


@player_handler.callback_query(F.data == 'add_heroes')
async def ask_heroes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Напиши имя(кличку) персонажа', reply_markup=None)
    await state.set_state(Player.hero)


@player_handler.message(Player.hero)
async def get_hero(message: Message, state: FSMContext):
    await state.update_data(hero=message.text.split()[0])
    data = await state.get_data()
    heroes = set(data['heroes'].split('&'))    
    heroes.add(data['hero'])
    await state.update_data(heroes='&'.join(list(heroes)))
    await message.answer('Отлично. Выбери следующее действие', reply_markup=get_note_inl_kb())


@player_handler.callback_query(F.data == 'add_teammate')
async def ask_heroes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Напиши никнейм тиммейта', reply_markup=None)
    await state.set_state(Player.teammate)


@player_handler.message(Player.teammate)
async def get_hero(message: Message, state: FSMContext):
    await state.update_data(teammate=message.text.split()[0])
    data = await state.get_data()
    teammates = set(data['teammates'].split('&'))    
    teammates.add(data['teammate'])
    await state.update_data(teammates='&'.join(list(teammates)))
    await message.answer('Отлично. Выбери следующее действие', reply_markup=get_note_inl_kb())


@player_handler.callback_query(F.data == 'done_create')
async def create_player(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data['heroes']:
        data['heroes'] = '--'
    if not data['teammates']:
        data['teammates'] = '--'
    
    await callback.message.edit_text(f'Отлично\nПолучилась следующуя запись:\n\
<b>Игрок</b>: {data['nickname']}\n\
<b>Описание</b>: {data['note']}\n\
<b>Персонажи</b>: {', '.join(data['heroes'][1:].split('&'))}\n\
<b>Тиммейты в пати</b>: {', '.join(data['teammates'][1:].split('&'))}\n\n\
<b>Все верно?</b>', reply_markup=accept_decline())
    

@player_handler.callback_query(F.data == 'accept')
async def cmd_create_player(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['heroes'] == '--':
        heroes = data['heroes']
    else:
        heroes = list(data['heroes'][1:].split('&'))

    if data['teammates'] == '--':
        teammates = data['teammates']
    else:
        teammates = list(data['teammates'][1:].split('&'))
    
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO players (nickname, note) VALUES (?, ?)', (data['nickname'], data['note']))
        connection.commit()
        
        cursor.execute("SELECT id FROM players WHERE nickname = '%s'" % (data['nickname'],))
        p_id = cursor.fetchall()[0][0]

        if heroes == '--':
            pass
        else:
            for hero in heroes:
                cursor.execute('INSERT INTO heroes (player_id, hero) VALUES (?, ?)', (p_id, hero))
        connection.commit()

        if teammates == '--':
            pass
        else:
            for teammate in teammates:
                cursor.execute('INSERT INTO stacks (player_id, friend_nickname) VALUES (?, ?)', (p_id, teammate))
        connection.commit()

    await callback.message.edit_text('Готово', reply_markup=None)
    await state.clear()


@player_handler.callback_query(F.data == 'decline')
async def cmd_decline(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Действие отменено', reply_markup=None)
    await state.clear()



@player_handler.message(F.text == 'Найти игрока')
async def cmd_find_player(message: Message, state: FSMContext):
    await state.set_state(FindPlayer.nickname)
    await message.answer('Введи никнейм игрока')


@player_handler.message(FindPlayer.nickname)
async def find_player(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    nickname = message.text.split()[0]

    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()

        cursor.execute(f"SELECT id, note FROM players WHERE nickname = '{nickname}'")
        result = cursor.fetchall()
        if not result:
            await message.answer('Такого игрока не найдено')
        else:
            p_id, note = result[0][0], result[0][1]
            await state.update_data(id=p_id)

            cursor.execute(f'SELECT DISTINCT hero FROM heroes WHERE player_id = {p_id}')
            heroes = list(
                map(
                    lambda x: x[0],
                    cursor.fetchall()
                )
            )
            if not heroes:
                heroes = []

            cursor.execute(f'SELECT DISTINCT friend_nickname FROM stacks WHERE player_id = {p_id}')
            teammates = list(
                map(
                    lambda x: x[0],
                    cursor.fetchall()
                )
            )
            if not teammates:
                teammates = []
        
            await message.answer(f"Игрок найден\n\n\
<b>Никнейм</b>\n{nickname}\n\n\
<b>Описание</b>\n{note}\n\n\
<b>Персонажи</b>\n{', '.join(heroes)}\n\n\
<b>Тиммейты в пати</b>\n{', '.join(teammates)}\n\n", reply_markup=edit_inl_kb(message.from_user.id))
            

@player_handler.callback_query(F.data == 'delete_player')
async def delete_player(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    p_id = data['id']

    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM players WHERE id = ?', (p_id,))
        connection.commit()
        await callback.message.edit_text('Игрок успешно удален', reply_markup=None)
    await state.clear()


@player_handler.callback_query(F.data == 'edit_player')
async def edit_player(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=edit_player_inl_kb())


@player_handler.callback_query(F.data == 'edit_heroes')
async def edit_heroes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Напиши имя(кличку) персонажа', reply_markup=None)
    await state.set_state(FindPlayer.hero)


@player_handler.message(FindPlayer.hero)
async def edit_heroes_add_hero(message: Message, state: FSMContext):
    await state.update_data(hero=message.text.split()[0])
    data = await state.get_data()
    hero = data['hero']
    p_id = data['id']
    nickname = data['nickname']
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO heroes (player_id, hero) VALUES(?, ?)', (p_id, hero))
        connection.commit()
        
        cursor.execute(f'SELECT note FROM players WHERE id = {p_id}')
        note = cursor.fetchall()[0][0]

        cursor.execute(f'SELECT DISTINCT hero FROM heroes WHERE player_id = {p_id}')
        heroes = list(
            map(
                lambda x: x[0],
                cursor.fetchall()
            )
        )
        if not heroes:
            heroes = []

        cursor.execute(f'SELECT DISTINCT friend_nickname FROM stacks WHERE player_id = {p_id}')
        teammates = list(
            map(
                lambda x: x[0],
                cursor.fetchall()
            )
        )
        if not teammates:
            teammates = []
        await message.answer(f"<b>Никнейм</b>\n{nickname}\n\n\
<b>Описание</b>\n{note}\n\n\
<b>Персонажи</b>\n{', '.join(heroes)}\n\n\
<b>Тиммейты в пати</b>\n{', '.join(teammates)}\n\n", reply_markup=edit_inl_kb(message.from_user.id))
        

@player_handler.callback_query(F.data == 'edit_teammates')
async def edit_teammates(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Напиши никнейм тиммейта', reply_markup=None)
    await state.set_state(FindPlayer.teammate)


@player_handler.message(FindPlayer.teammate)
async def edit_teammates_add_teammate(message: Message, state: FSMContext):
    await state.update_data(teammate=message.text.split()[0])
    data = await state.get_data()
    teammate = data['teammate']
    p_id = data['id']
    nickname = data['nickname']
    with sqlite3.connect('PlayerNotes.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO stacks (player_id, friend_nickname) VALUES(?, ?)', (p_id, teammate))
        connection.commit()
        
        cursor.execute(f'SELECT note FROM players WHERE id = {p_id}')
        note = cursor.fetchall()[0][0]

        cursor.execute(f'SELECT DISTINCT hero FROM heroes WHERE player_id = {p_id}')
        heroes = list(
            map(
                lambda x: x[0],
                cursor.fetchall()
            )
        )
        if not heroes:
            heroes = []

        cursor.execute(f'SELECT DISTINCT friend_nickname FROM stacks WHERE player_id = {p_id}')
        teammates = list(
            map(
                lambda x: x[0],
                cursor.fetchall()
            )
        )
        if not teammates:
            teammates = []
        await message.answer(f"<b>Никнейм</b>\n{nickname}\n\n\
<b>Описание</b>\n{note}\n\n\
<b>Персонажи</b>\n{', '.join(heroes)}\n\n\
<b>Тиммейты в пати</b>\n{', '.join(teammates)}\n\n", reply_markup=edit_inl_kb(message.from_user.id))


@player_handler.callback_query(F.data == 'edit_done')
async def edit_done(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=edit_inl_kb(callback.from_user.id))