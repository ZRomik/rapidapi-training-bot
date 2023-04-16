from setups import dp
from helpers import add_user, add_new_search
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import logging
from helpers import add_user, add_new_search, RapidapiHelper, cancel_search_by_user, update_city_name, update_city_id,\
    get_key_value, set_key_value
from keyboards import main_menu_keybord, choice_keyboard, cancel_keyboard
import json
from aiogram_calendar import SimpleCalendar, simple_cal_callback


class SearchStates(StatesGroup):
    get_city_name = State()
    get_check_in_date = State()
    get_check_out_date = State()
    get_adults_count = State()
    get_children = State()
    get_min_price = State()
    get_max_price = State()
    check_data = State()


@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_search(message: Message, state: FSMContext) -> None:
    """Отмена поиска."""
    data = await state.get_data()
    logger = logging.getLogger(__name__)
    logger.error(
        "Пользователь отменил поиск"
    )
    await message.answer(
        "Поиск отменен",
        reply_markup=main_menu_keybord
    )
    cancel_search_by_user(search_id=data["search"]["id"])

@dp.message_handler(commands=["lowprice"], state=None)
async def start_search(message: Message, state: FSMContext) -> None:
    """Начало поиска топа дешевых отелей"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Пользователь {message.from_user.id} начал поиск самых дешевых отелей."
    )
    # получаем идентификатор пользователя.
    user_id = add_user(id=message.from_user.id)
    await SearchStates.get_city_name.set()
    # заполняем словарь со служебной информацией о поиске
    command = message.text[1:]
    search_id = add_new_search(user_id=user_id, kind=command)
    helper = RapidapiHelper.get_helper()
    # получим метаданные для последующих запросов
    metadata = helper.get_metadata()
    if metadata:
        site_id = get_key_value(metadata, "siteId")
        eap_id = get_key_value(metadata, "EAPID")
    data = {
        "user": {
            "tg id": message.from_user.id,
            "id": user_id
        },
        "location": {
            "city name": "",
            "id": ""
        },
        "settlers": {
            "adults": None,
            "children": None
        },
        "dates": {
            "check in": "",
            "check out": ""
        },
        "command": {
            "name": command
        },
        "search": {
            "id": search_id
        },
        "metadata": {
            "site id": str(site_id),
            "eapid": eap_id
        },
        "price": {
            "min price": "",
            "max price": ""
        }
    }
    await state.set_data(data)
    await message.answer(
        "Вы хотите найти топ самых дешевых отелей в городе. Я помогу вам.\nВведите название города:",
        reply_markup=cancel_keyboard
    )


@dp.message_handler(state=SearchStates.get_city_name)
async def get_city_name(message: Message, state: FSMContext) -> None:
    """Получение названия города и первичный поиск."""
    city_name = message.text
    data = await state.get_data()
    data["location"]["name"] = city_name
    await state.set_data(data)
    update_city_name(search_id=data["search"]["id"], city_name=city_name)
    await message.answer(
        f"Поиск данных о городе '{city_name}'"
    )
    helper = RapidapiHelper.get_helper()
    metadata = data["metadata"]
    result = helper.search_location(
        name=city_name,
        metadata=metadata
    )
    # проверим, что получили верные данные
    if result and result["rc"] == "OK":
        # обработка полученных данных
        city_data = result["sr"]
        city_list = list(filter(lambda city: city["type"] == "CITY", city_data))
        # если в списке только 1 город, запоминаем его идентификатор и идем дальше
        if len(city_list) == 1:
            city_id = get_key_value(city_list[0], 'gaiaId')
            set_key_value(data, "city id", city_id)
            await state.set_data(data)
            await message.answer(
                "Запомнил."
            )
            await SearchStates.next()
            await message.answer(
                "Выберите дате въезда:",
                reply_markup= await SimpleCalendar().start_calendar()
            )


@dp.callback_query_handler(simple_cal_callback.filter(), state=SearchStates.get_check_in_date)
async def get_check_in_date(callback_query: CallbackQuery, callback_data: dict) -> None:
    """
    Получение даты въезда.
    """
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        state = dp.current_state()
        data = await state.get_data()
        check_in = date.strftime("%d.%m.%Y")
        set_key_value(data, "check in", check_in)
        await state.set_data(data)
        await callback_query.message.answer(
            check_in,
            reply_markup=ReplyKeyboardRemove()
        )
        await SearchStates.next()
        await callback_query.message.answer(
            "Выберите дату выезда:",
            reply_markup= await SimpleCalendar().start_calendar()
        )


@dp.callback_query_handler(simple_cal_callback.filter(), state=SearchStates.get_check_out_date)
async def get_check_out_date(callback_query: CallbackQuery, callback_data: dict) -> None:
    """
    Получение даты выезда.
    """
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        state = dp.current_state()
        data = await state.get_data()
        check_out = date.strftime("%d.%m.%Y")
        set_key_value(data, "check in", check_out)
        await state.set_data(data)
        await callback_query.message.answer(
            check_out,
            reply_markup=ReplyKeyboardRemove()
        )
        await SearchStates.next()
        await callback_query.message.answer(
            "Введите количество взрослых постояльцев:",
            reply_markup=cancel_keyboard
        )


@dp.message_handler(state=SearchStates.get_adults_count)
async def get_adults_count(message: Message, state: FSMContext) -> None:
    """
    Получение количества взрослых постояльцев.
    """
    text = message.text
    if not text.isnumeric() or text == "0":
        await message.answer(
            "Ошибка! Ожидается число выше нуля. Повторите ввод."
        )
    else:
        adults_count = int(text)
        data = await state.get_data()
        set_key_value(data, "adults", adults_count)
        await state.set_data(data)
        await SearchStates.next()
        await message.answer(
            "Если среди постояльцев будут дети - введите возраст каждого ребенка через пробел.\nИначе введите ноль.",
            reply_markup=cancel_keyboard
        )


@dp.message_handler(state=SearchStates.get_children)
async def get_children(message: Message, state: FSMContext) -> None:
    """
    Получение возраста детей.
    """
    text = message.text
    # детей нет, идем дальше
    data = await state.get_data()
    if text == "0":
        set_key_value(data, "chlildren", [])
    else:
        children = []
        for i_age in text.split():
            if not i_age.isnumeric():
                await message.answer(
                    "Ошибка! Вы ввели не число."
                )
                await message.answer(
                    "Если среди постояльцев будут дети - введите возраст каждого ребенка "\
                    "через пробел.\nИначе введите ноль.",
                    reply_markup=cancel_keyboard
                )
                return
            else:
                children.append(
                    {"age": i_age}
                )
        set_key_value(data, "children", children)
        await state.set_data(data)
        await SearchStates.next()
        await message.answer(
            "Введите минимальную цену номера за сутки:",
            reply_markup=cancel_keyboard
        )


@dp.message_handler(state=SearchStates.get_min_price)
async def get_min_price(message: Message, state: FSMContext) -> None:
    """
    Получение минимальной цены номера.
    """
    text = message.text
    if  not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Пjвторите ввод.",
            reply_markup=cancel_keyboard
        )
    elif text == "0" or text.startswith("-"):
        await message.answer(
            "Ошибка! Цена должна быть выше нуля. Повторите ввод."
        )