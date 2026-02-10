import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv
import sqlite3


load_dotenv()
token = getenv('TOKEN')
admins = set(map(int, getenv('ADMINS').split(',')))


with sqlite3.connect('PlayerNotes.db') as connection:
    cursor = connection.cursor()
    """
    Список пользователей тг использующих бота
    """
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, \
                   name VARCHAR(255), telegram_id INT)')
    
    
    """
    Список игроков с их описаниями
    """
    cursor.execute('CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, \
                   nickname VARCHAR(255), note TEXT)')
    
    
    """
    Список героев, на которых играют игроки
    """
    cursor.execute('CREATE TABLE IF NOT EXISTS heroes (id INTEGER PRIMARY KEY, \
                   player_id INT, hero VARCHAR(255))')
    

    """
    Список предполагаемых друзей игроков
    """
    cursor.execute('CREATE TABLE IF NOT EXISTS stacks (id INTEGER PRIMARY KEY, \
                   player_id INT, friend_nickname TEXT)')
    

    connection.commit()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())