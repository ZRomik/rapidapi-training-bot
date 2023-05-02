import datetime
from setups import dp
from helpers import add_user, add_new_search, filter_search_locations
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import logging
from helpers import add_user, add_new_search, RapidapiHelper, cancel_search_by_user, update_city_name, update_city_id,\
    get_value, set_value, build_hotels_list, sort_hotels_by_score, filter_image_list, cancel_search_by_error,\
    update_history_data, commands_desc, succes_end_search, filter_hotels_by_price, slice_list, sort_hotels_by_ds,\
    sort_hotels_by_price_and_score
from keyboards import main_menu_keybord, choice_keyboard, cancel_keyboard
import json
from aiogram_calendar import SimpleCalendar, simple_cal_callback
import emoji


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

sort_orders = {
    "lowprice": "PRICE_LOW_TO_HIGH",
    "highprice": "топ самых дорогих отелей в городе",
    "bestdeal": "DISTANCE"
}

NO_PHOTO_URL = 'https://thumbs.dreamstime.com/b/'\
    'no-image-available-icon-photo-camera-flat-vector-illustration-132483141.jpg'

distance_dict = {
    "kilometer": "км.",
    "mile": "мл."
}


@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_search(message: Message, state: FSMContext) -> None:
    """Отмена поиска."""
    data = await state.get_data()
    logger = logging.getLogger(__name__)
    logger.error(
        f"Пользователь {message.from_user.id} отменил поиск"
    )
    cancel_search_by_user(search_id=get_value(data, "search id"))
    await state.finish()
    await message.answer(
        "Поиск отменен",
        reply_markup=main_menu_keybord
    )

@dp.message_handler(commands=["lowprice", "highprice", "bestdeal"], state=None)
async def start_search(message: Message, state: FSMContext) -> None:
    """Начало поиска топа дешевых отелей"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Пользователь {message.from_user.id} начал поиск."
    )
    # получаем идентификатор пользователя.
    user_id = add_user(id=message.from_user.id)
    await SearchStates.get_city_name.set()
    # заполняем словарь со служебной информацией о поиске
    command = message.text[1:]
    search_id = add_new_search(user_id=user_id, kind=command)
    helper = RapidapiHelper.get_helper()
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
        },
        "count": {
            "value": 5
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
    update_city_name(
        search_id=get_value(data, "search id"),
        city_name=city_name,
        user_tg_id=message.from_user.id
    )
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
            # обновим название города в таблице
            search_id = get_value(data, "search id")
            update_city_name(
                search_id=search_id,
                city_name=city_name,
                user_tg_id=message.from_user.id
            )
            await SearchStates.next()
            await message.answer(
                "Выберите дате въезда:",
                reply_markup= await SimpleCalendar().start_calendar()
            )
        elif  len(city_list) == 0:
            await message.answer(
                f"Я не нашел никаких данных о городе '{city_name}'. Уточните название и повторите поиск.",
                reply_markup=main_menu_keybord
            )
            await state.finish()
            cancel_search_by_error(search_id=get_value(data, "search id"))
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
        current_date = datetime.datetime.now()
        if date < current_date:
            await callback_query.message.answer(
                "Ошибка! Дата въезда не может быть раньше текущей даты!",
                reply_markup=ReplyKeyboardRemove()
            )
            await callback_query.message.answer(
                "Выберите дату въезда:",
                reply_markup= await SimpleCalendar().start_calendar()
            )
        else:
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
    state = dp.current_state()
    data = await state.get_data()
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        check_in = datetime.datetime.strptime(get_value(data, "check in"), "%d.%m.%Y")
        current_date = datetime.datetime.now()
        if date < current_date:
            await callback_query.message.answer(
                "Ошибка! Дата выезда не может быть раньше текущей даты!",
                reply_markup=ReplyKeyboardRemove()
            )
            await callback_query.message.answer(
                "Выберите дату выезда: ",
                reply_markup= await SimpleCalendar().start_calendar()
            )
        elif date < check_in:
            await callback_query.message.answer(
                "Ошибка! Дата выезда не может быть раньше даты въезда!",
                reply_markup=ReplyKeyboardRemove()
            )
            await callback_query.message.answer(
                "Выберите дату выезда: ",
                reply_markup= await SimpleCalendar().start_calendar()
            )
        else:
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
        update_history_data(
            id=get_value(data, "search id"),
            data={"adults": adults_count}
        )
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
        update_history_data(
            id=get_value(data, "search id"),
            data={"children": len(children)}
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
        min_price = get_value(data, "min price")
        max_price = int(text)
        if max_price < min_price:
            await message.answer(
                "Ошибка! Максимальная цена не может быть меньше минимальной. Повторите ввод"
            )
            return
        set_value(data, "max price", max_price)
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



@dp.message_handler(state=SearchStates.get_result_count)
async def get_result_count(message: Message, state: FSMContext) -> None:
    """Получение кол-ва отелей в ответе и проверка данных поиска"""
    text = message.text
    # отрицательное число или равно нулю
    if text.startswith("-") or text == "0":
        await message.answer(
            "Ошибка! Число должно быть выше нуля. Повторите ввод.",
            reply_markup=cancel_keyboard
        )
    # введено не число
    elif not text.isnumeric():
        await message.answer(
            "Ошибка! Вы ввели не число. Повторите ввод.",
            reply_markup=cancel_keyboard
        )
    else:
        count = int(text)
        data = await state.get_data()
        set_value(data, "value", count)
        await state.set_data(data)
        # попросим проверить собранные данные перед началом поиска
        city_name = get_value(data, "city name")
        kind = commands_desc[get_value(data, "cmd name")]
        check_in = get_value(data, "check in")
        check_out = get_value(data, "check out")
        adults_count = get_value(data, "adults")
        child_count = len(get_value(data, "children"))
        min_price = get_value(data, "min price")
        max_price = get_value(data, "max price")
        msg =\
        f"Проверьте данные поиска:\n"\
        f"В {city_name} вы ищете {kind}.\n"\
        f"Постояльцы:\n"\
        f"Взрослые: {adults_count}.\n"\
        f"Дети: {child_count}\n"\
        f"Дата въезда: {check_in}.\n"\
        f"Дата выезда: {check_out}.\n"\
        f"Мин. цена: {min_price}.\n"\
        f"Макс. цена: {max_price}.\n"\
        f"Кол-во отелей в ответе: {count}.\n"\
        f"Начать поиск?"
        await SearchStates.next()
        await message.answer(
            msg,
            reply_markup=choice_keyboard
        )

@dp.message_handler(Text(equals="искать",  ignore_case=True), state=SearchStates.user_choice)
async def search_offers(message: Message, state: FSMContext) -> None:
    """Поиск предложений и вывод результатов."""
    #region поиск данных
    data = await state.get_data()
    command = get_value(data, "cmd name")
    search_id = get_value(data, "search id")
    await message.answer(
        "Ищу предложения...",
        reply_markup=ReplyKeyboardRemove()
    )
    helper = RapidapiHelper.get_helper()
    prop_data = helper.get_properties_list(
        data=data,
        sort_order=commands_desc[command]
    )
    #endregion
    #region обработка данных
    # нет данных
    if not prop_data:
        await message.answer(
            "Поисковый сервис не вернул данных. Попробуйте изменить критерии поиска или повторить позднее.",
            reply_markup=main_menu_keybord
        )
        await state.finish()
        cancel_search_by_error(
            search_id=search_id
        )
    # ошибка поиска
    elif "errors" in prop_data:
        await message.answer(
            "Поисковый сервис вернул ошибку. Попробуйте изменить критерии поиска или повторить позднее.",
            reply_markup=main_menu_keybord
        )
        await state.finish()
    # данные есть, можно работать
    else:
        # получим "сырой" список отелей
        raw_hotels_list = build_hotels_list(
            props_list=get_value(
                data=prop_data,
                key="properties"
            )
        )
        # выкинем отели, не подходящие по диапазону цен
        min_price = get_value(data, "min price")
        max_price = get_value(data, "max price")
        hotels_list_filtered_by_price = filter_hotels_by_price(
            raw_list=raw_hotels_list,
            min_price=min_price,
            max_price=max_price
        )
        # для каждой команды своя сортировка
        await message.answer(
            "Сортирую данные..."
        )
        if command == "lowprice":
            # сортировка для топа дешевых отелей
            sorted_hotels_list = sort_hotels_by_score(
                hotels_list=hotels_list_filtered_by_price
            )
        elif command == "highprice":
            # сортировка для топа дорогих отелей
            sorted_hotels_list = sort_hotels_by_price_and_score(
                hotels_list=hotels_list_filtered_by_price,
                is_reverse=True
            )
        else:
            sorted_hotels_list = sort_hotels_by_ds(
                hotels_list=hotels_list_filtered_by_price
            )
        # обрежем список до нужного размера
        count = get_value(data, "value")
        result_hotels_list = slice_list(
            raw_list=sorted_hotels_list,
            count=count
        )
    #endregion
    #region загрузка фотографий
        await message.answer(
            "Изучаю фотографии..."
        )
        for i_hotel in result_hotels_list:
            hotel_details = helper.get_hotel_details(
                id=i_hotel["id"]
            )
            if hotel_details:
                set_value(i_hotel, "address", get_value(hotel_details, "addressLine"))
                images_list = filter_image_list(
                    images_list=get_value(hotel_details, "images")
                )
                if images_list:
                    set_value(
                        i_hotel,
                        "image",
                        get_value(images_list[0], "url")
                    )
                else:
                    set_value(
                        i_hotel,
                        "image",
                        NO_PHOTO_URL
                    )
            else:
                set_value(
                    i_hotel,
                    "image",
                    NO_PHOTO_URL
                )
    #endregion
    #region вывод результата
    await message.answer(
        "Вот, что я нашел:"
    )
    for i_hotel in result_hotels_list:
        hotel_address = i_hotel["address"]
        hotel_name = i_hotel["name"]
        image = i_hotel["image"]
        score = i_hotel["score"]
        amount = i_hotel["amount"]
        distance = i_hotel["distance"]
        units = i_hotel["units"]
        text_list = [
            hotel_name,
            hotel_address,
            f"{score} {score * emoji.emojize(':star:')}",
            str(amount)
        ]
        if distance:
            text_list.append(f"{distance} {distance_dict[units.lower()]} от центра")
        msg = '\n'.join(
            text_list
        )
        await message.answer_photo(
            photo=image,
            caption=msg
        )
    succes_end_search(search_id=search_id)
    await state.finish()
    await message.answer(
        "Поиск успешно завершен.",
        reply_markup=main_menu_keybord
    )
    #endregion