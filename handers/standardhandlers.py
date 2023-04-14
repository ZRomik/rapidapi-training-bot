from setups import dp
import logging
from aiogram.types import Message

@dp.message_handler(commands=["start"])
async def process_start_command(message: Message):
    """Обработка команды start."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Обработка команды start. Вывод приветственного сообщения"
    )
    msg =\
    "Привет!\n"\
    "Я поисковый бот турагентства Too Easy Travel.\n"\
    "Я могу помочь найти подходящий вам отель в любом городе мира!\n"\
    "Чтобы ознакомиться со списком достуных мне команд введите команду /help."
    await message.answer(
        msg
    )


@dp.message_handler(commands=["help"])
async def process_help_command(message: Message):
    """Обработка команды help."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Обработка команды help. Вывод информации о доступных командах."
    )
    msg =\
    "/help - это сообщение.\n"\
    "/lowprice - узнать топ самых дешёвых отелей в городе.\n"\
    "/highprice - узнать топ самых дорогих отелей в городе.\n"\
    "/bestdeal - узнать топ отелей, наиболее подходящих по цене и расположению от центра.\n"\
    "/history - узнать историю поиска отелей."
    await message.answer(
        msg
    )