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

@dp.message_handler(commands=["start"], state="*")
async def process_start_command(message: Message, state: FSMContext):
    if not state is None:
        await state.finish()
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
            for i_num, i_info in enumerate(history_list):
                search_id = i_num + 1
                start_at = i_info["start date"]
                end_at = i_info["end date"]
                search_kind = i_info["command_desc"]
                city_name = i_info["city name"]
                cancelled = i_info["cancelled"]
                user_cancel = i_info["user cancel"]
                error_cancel = i_info["error cancel"]
                adults_count = i_info["adults"]
                children_count = i_info["children"]
                if start_at:
                    start_date, start_time = start_at.strftime(
                        "%d.%m%Y %H:%M:%S"
                    ).split()
                if end_at:
                    end_date, end_time = end_at.strftime(
                        "%d.%m%Y %H:%M:%S"
                    ).split()
                text_list = [
                    f"Поиск #{search_id}",
                    f"Поиск начат {start_date} в {start_time}"
                ]
                # если поиск отменен
                if cancelled:
                    text_list.append(
                        f"Поиск отменен {end_date} в {end_time}"
                    )
                    # нет смысла продолжать
                    if user_cancel:
                        text_list.append(
                            "Поиск отменен пользователем."
                        )
                    elif error_cancel:
                        text_list.append(
                            "Поиск отменен из-за ошибки."
                        )
                    msg = '\n'.join(
                        text_list
                    )
                    await message.answer(
                        msg,
                        reply_markup=ReplyKeyboardRemove()
                    )
                    # иначе покажем информацию.
                else:
                    if city_name:
                        text_list.append(
                            f"В городе '{city_name}' вы хотели найти {search_kind}."
                        )
                        text_list.append(
                            f"Постояльцы:"
                        )
                        text_list.append(
                            f"Взрослые: {adults_count}"
                        )
                        text_list.append(
                            f"Дети: {children_count}"
                        )
                        text_list.append(
                            f"Поиск завершен {end_date} в {end_time}"
                        )
                        text_list.append(
                            "Поиск завершен без ошибок."
                        )
                        msg = '\n'.join(text_list)
                        await message.answer(
                            msg
                        )
            await state.finish()
            await message.answer(
                "Вывод завершен.",
                reply_markup=main_menu_keybord
            )