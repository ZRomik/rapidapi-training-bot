from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from os import getenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

mem_storage = MemoryStorage()

load_dotenv('.env')
token = getenv('TOKEN')
if not token:
    raise ValueError("Не удалось получить токен бота. Запуск невозможен!")

if not getenv("KEY"):
    raise ValueError("Не удалось получить АПИ-ключ. Запуск невозможен!")

bot = Bot(
    token=token
)

dp = Dispatcher(
    bot=bot,
    storage=mem_storage
)