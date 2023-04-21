from setups import dp
import logging
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from helpers import add_user, get_user_id, add_new_search, RapidapiHelper, get_history, get_value, commands_desc,\
    format_date_time
from keyboards import main_menu_keybord, choice_keyboard, cancel_keyboard
import datetime

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
    # введено не число
    elif not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод."
        )
    # все нормально. Показываем историю.
    else:
        user_id = get_user_id(
            id = message.from_user.id
        )
        history_list = get_history(
            user_id=user_id,
            limit=int(text)
        )
        if history_list:
            for i_num, i_rec in enumerate(history_list):
                text_list = []
                start_date,start_time = format_date_time(get_value(i_rec, "start date"))
                end_date, end_time = format_date_time(get_value(i_rec, "end date"))
                city_name = get_value(i_rec, "city name")
                cancelled = get_value(i_rec, "cancelled")
                user_cancel = get_value(i_rec, "user cancel")
                adults = get_value(i_rec, "adults")
                children = get_value(i_rec, "children")
                kind = get_value(i_rec, "kind")
                text_list.append(f"Поиск #{i_num + 1}")
                text_list.append(f"Поиск начат {start_date} в {start_time}")
                if city_name:
                    text_list.append(f"Вы искали отели в городе {city_name}")
                text_list.append(f"Вы искали: {get_value(commands_desc, kind)}")
                text_list.append(f"Поиск закончен {end_date} в {end_time}")
                text = "Результат: "
                if cancelled:
                    if user_cancel:
                        text += "поиск отменен пользователем."
                    else:
                        text += "поиск завершился ошибкой."
                else:
                    text += "поиск завершен без ошибок."
                text_list.append(text)
                msg = '\n'.join(text_list)
                await message.answer(
                    msg,
                    reply_markup=ReplyKeyboardRemove()
                )
            await message.answer(
                "Вывод завершен.",
                reply_markup=main_menu_keybord
            )
            await state.finish()
        else:
            await message.answer(
                "Ваша история поиска пуста.",
                reply_markup=main_menu_keybord
            )
