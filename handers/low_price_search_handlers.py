from setups import dp
from helpers import add_user, add_new_search, filter_search_locations
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import logging
from helpers import add_user, add_new_search, RapidapiHelper, cancel_search_by_user, update_city_name, update_city_id,\
    get_value, set_value, filter_props_list
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
    get_result_count = State()
    user_choice = State()

commands_desc = {
    "lowprice": "топ самых дешёвых отелей в городе",
    "highprice": "топ самых дорогих отелей в городе",
    "bestdeal": "топ отелей, наиболее подходящих по цене и расположению от центра"
}
sort_orders = {
    "lowprice": "PRICE_LOW_TO_HIGH",
    "highprice": "топ самых дорогих отелей в городе",
    "bestdeal": "топ отелей, наиболее подходящих по цене и расположению от центра"
}


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
    cancel_search_by_user(search_id=get_value(data, "search id"))

@dp.message_handler(commands=["lowprice"], state=None)
async def start_search(message: Message, state: FSMContext) -> None:
    """Начало поиска топа дешевых отелей"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Пользователь {message.from_user.id} начал поис."
    )
    await message.answer(
        "Получение метаданных для поиска."
    )
    # получаем идентификатор пользователя.
    user_id = add_user(id=message.from_user.id)
    await SearchStates.get_city_name.set()
    # заполняем словарь со служебной информацией о поиске
    command = message.text[1:]
    search_id = add_new_search(user_id=user_id, kind=command)
    helper = RapidapiHelper.get_helper()
    # получим метаданные для последующих запросов
    data = {
        "user": {
            "tg id": message.from_user.id,
            "user id": user_id
        },
        "location": {
            "city name": "",
            "city id": ""
        },
        "settlers": {
            "adults": None,
            "children": []
        },
        "dates": {
            "check in": "",
            "check out": ""
        },
        "command": {
            "cmd name": command
        },
        "search data": {
            "search id": search_id
        },
        "price": {
            "min price": None,
            "max price": None
        }
    }
    await state.set_data(data)
    await message.answer(
        f"Вы хотите найти {commands_desc[command]}. Я помогу вам.\nВведите название города:",
        reply_markup=cancel_keyboard
    )


@dp.message_handler(state=SearchStates.get_city_name)
async def get_city_name(message: Message, state: FSMContext) -> None:
    """Получение названия города и первичный поиск."""
    city_name = message.text
    data = await state.get_data()
    set_value(data, "city name", city_name)
    await state.set_data(data)
    update_city_name(search_id=get_value(data, "search id"), city_name=city_name)
    await message.answer(
        f"Поиск данных о городе '{city_name}'"
    )
    helper = RapidapiHelper.get_helper()
    metadata = get_value(data, "metadata")
    result = helper.search_location(
        name=city_name
    )
    # проверим, что получили верные данные
    if result and result["rc"] == "OK":
        # обработка полученных данных
        city_data = result["sr"]
        city_list = filter_search_locations(city_data)
        # если в списке только 1 город, запоминаем его идентификатор и идем дальше
        if len(city_list) == 1:
            city_id = get_value(city_list[0], 'gaiaId')
            set_value(data, "city id", city_id)
            await state.set_data(data)
            await message.answer(
                "Запомнил."
            )
            await SearchStates.next()
            await message.answer(
                "Выберите дате въезда:",
                reply_markup= await SimpleCalendar().start_calendar()
            )
        else:
            # попросим уточнить город у пользователя
            buttons_list = [
                InlineKeyboardButton(
                    text=get_value(i_city, "fullName"),
                    callback_data=get_value(i_city, "gaiaId")
                )
                for i_city in city_list
            ]
            city_kbd = InlineKeyboardMarkup(
                row_width=1
            )
            city_kbd.add(*buttons_list)
            await message.answer(
                "Уточните город:",
                reply_markup=city_kbd
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
        set_value(data, "check in", check_in)
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
        set_value(data, "check out", check_out)
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
        set_value(data, "adults", adults_count)
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
        set_value(data, "children", [])
        await SearchStates.next()
        await message.answer(
            "Введите минимальную цену номера за сутки: ",
            reply_markup=cancel_keyboard
        )
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
                    {"age": int(i_age)}
                )
        set_value(data, "children", children)
        await state.set_data(data)
        await SearchStates.next()
        await message.answer(
            "Введите минимальную цену номера за сутки:",
            reply_markup=cancel_keyboard
        )


@dp.message_handler(state=SearchStates.get_min_price)
async def get_min_price(message: Message, state: FSMContext) -> None:
    """
    Получение минимальной цены номера за сутки.
    """
    text = message.text
    if  not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод.",
            reply_markup=cancel_keyboard
        )

    elif text == "0" or text.startswith("-"):
        await message.answer(
            "Ошибка! Цена должна быть выше нуля. Повторите ввод."
        )
    else:
        data = await state.get_data()
        set_value(data, "min price", int(text))
        await state.set_data(data)
        await SearchStates.next()
        await message.answer(
            "Введите максимальную цену номера",
            reply_markup=cancel_keyboard
        )

@dp.message_handler(state=SearchStates.get_max_price)
async def get_max_price(message: Message, state: FSMContext) -> None:
    """
    Получение максимальной цены номера за сутки.
    """
    text = message.text
    if  not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод.",
            reply_markup=cancel_keyboard
        )
    elif text == "0" or text.startswith("-"):
        await message.answer(
            "Ошибка! Цена должна быть выше нуля. Повторите ввод."
        )
    else:
        data = await state.get_data()
        set_value(data, "max price", int(text))
        await state.set_data(data)
        await SearchStates.next()
        await message.answer(
            "Сколько отелей показывать в ответе?",
            reply_markup=cancel_keyboard
        )

@dp.callback_query_handler(state=SearchStates.get_city_name)
async def get_city_id(query: CallbackQuery, state: FSMContext) -> None:
    """
    Получение идентификатора города.
    """
    city_id = query.data
    data = await state.get_data()
    set_value(data, "city id", city_id)
    search_id = get_value(data, "search id")
    update_city_id(search_id=search_id, city_id=city_id)
    await SearchStates.next()
    await state.set_data(data)
    await query.message.answer(
        "Выберите дату въезда: ",
        reply_markup= await SimpleCalendar().start_calendar()
    )


@dp.message_handler(Text(equals="искать",  ignore_case=True))
async def search_offers(message: Message, state: FSMContext) -> None:
    """Поиск предложений и вывод результатов."""
    data = await state.get_data()
    await message.answer(
        "Поиск предложений...",
        reply_markup=ReplyKeyboardRemove()
    )
    cmd_name = get_value(data, "cmd name")
    helper = RapidapiHelper.get_helper()
    properties = helper.get_properties_list(data=data, sort_order=sort_orders[cmd_name])
    if properties and not "errors" in properties:
        props_list = get_value(properties, "properties")
        if props_list:
            await message.answer(
                "Сортировка списка."
            )
            hotels_data = filter_props_list(props_list=props_list)
            if hotels_data:
                sorted_hotels_list = sorted(hotels_data, key=lambda hotel: hotel["score"], reverse=True)
                data = await state.get_data()
                count = get_value(data, "result count")
                for index in range(count):
                    hotel = sorted_hotels_list[index]
                    msg =\
                    f"Отель: {hotel['name']}\n"\
                    f"Цена за сутки: {hotel['amount']}\n"\
                    f"Средняя оценка: {hotel['score']}"
                    await message.answer(
                        msg,
                        reply_markup=ReplyKeyboardRemove()
                    )
                await message.answer(
                    "Поиск успешно завершен.",
                    reply_markup=main_menu_keybord
                )
                await state.finish()
    else:
        await message.answer(
            "Сервис поиска вернул ошибку.\nПопробуйте изменить критерии поиска  или повторить поиск позднее."
        )


@dp.message_handler(state=SearchStates.get_result_count)
async def get_result_count(message: Message, state: FSMContext) -> None:
    """Получение кол-ва отелей в ответе"""
    text = message.text
    if not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод:",
            reply_markup=cancel_keyboard
        )
    elif text.startswith("-"):
        await message.answer(
            "Ошибка! Число должно быть выше нуля. Повторите ввод.",
            reply_markup=cancel_keyboard
        )
    else:
        data = await state.get_data()
        set_value(data, "result count", int(text))
        await state.set_data(data)
        await SearchStates.next()
        city_name = get_value(data, "city name")
        cmd = get_value(data, "cmd name")
        cmd_desc = commands_desc[cmd]
        adults_count = get_value(data, "adults")
        children_count = len(get_value(data, "children"))
        check_in = get_value(data, "check in")
        check_out = get_value(data, "check out")
        min_price = get_value(data, " min price")
        max_price = get_value(data, "max price")

        msg =\
        f"Проверьте данные поиска.\n"\
        f"Вы хотите найти {cmd_desc}.\n"\
        f"Постояльцы:\n"\
        f"Взрослые: {adults_count}.\n"\
        f"Дети: {children_count}.\n"\
        f"Дата въезда: {check_in}.\n"\
        f"Дата выезда: {check_out}.\n"\
        f"Отелей в ответе: {text}"
        f"Начать поиск?"
        await SearchStates.next()
        await message.answer(
            msg,
            reply_markup=choice_keyboard
        )