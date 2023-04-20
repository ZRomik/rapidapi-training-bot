from setups import dp
import logging
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from helpers import add_user, get_user_id, add_new_search, RapidapiHelper
from keyboards import main_menu_keybord, choice_keyboard, cancel_keyboard

class ShowHistoryStates(StatesGroup):
    get_record_count = State()

@dp.message_handler(commands=["start"])
async def process_start_command(message: Message):
    """Обработка команды start."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Обработка команды start. Регистрация пользователя и вывод приветственного сообщения."
    )
    # регистрируем пользователя.
    add_user(message.from_user.id)
    msg =\
    "Привет!\n"\
    "Я поисковый бот турагентства Too Easy Travel.\n"\
    "Я могу помочь найти подходящий вам отель в любом городе мира!\n"\
    "Чтобы ознакомиться со списком достуных мне команд введите команду /help."
    await message.answer(
        msg,
        reply_markup=main_menu_keybord
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


@dp.message_handler(Text(equals="отменить", ignore_case=True), state="*")
async def cancel_command(message: Message, state: FSMContext) -> None:
    """Отмена команды"""
    await message.answer(
        "Выполнение отменено."
    )
    await state.finish()


@dp.message_handler(commands=["history"], state="*")
async def process_history_command(message: Message, state: FSMContext) -> None:
    """Обработка команды history. Запрос кол-ва записей"""
    await ShowHistoryStates.get_record_count.set()
    await message.answer(
        "Сколько записей показывать?"
    )
    data = {
        "count": 0
    }
    await state.set_data(data)


@dp.message_handler(state=ShowHistoryStates.get_record_count)
async def get_records_count(message: Message, state: FSMContext) -> None:
    """Получение кол-ва записей для показа"""
    text = message.text
    # введено отрицательное число или ноль
    if text.startswith("-") or text == "0":
        await message.answer(
            "Ошибка! Число должно быть выше нуля. Повторите ввод.",
            reply_markup=cancel_keyboard
        )
    # ыыедено не число
    elif not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод."
        )
    # все нормально. Показываем историю.
    else:
        pass