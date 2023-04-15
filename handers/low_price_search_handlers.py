from setups import dp
from helpers import add_user, add_new_search
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import logging
from helpers import add_user, add_new_search, RapidapiHelper, update_history
from keyboards import main_menu_keybord, choice_keyboard, cancel_keyboard

class LowPriceSearchStates(StatesGroup):
    low_price_get_city_name = State()
    low_price_get_check_in_date = State()
    low_price_get_check_out_date = State()
    low_price_get_adults_count = State()
    low_price_get_children = State()


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
    update_history(data["search"]["id"], {"cancelled": True, "user_cancel": True})


@dp.message_handler(commands=["lowprice"], state=None)
async def start_low_price_search(message: Message, state: FSMContext) -> None:
    """Начало поиска топа дешевых отелей"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Пользователь {message.from_user.id} начал поиск самых дешевых отелей."
    )
    # получаем идентификатор пользователя.
    user_id = add_user(id=message.from_user.id)
    await LowPriceSearchStates.low_price_get_city_name.set()
    # заполняем словарь со служебной информацией о поиске
    command = message.text[1:]
    search_id = add_new_search(user_id=user_id, kind=command)
    data = {
        "user": {
            "tg id": message.from_user.id,
            "id": user_id
        },
        "location": {
            "name": "",
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
        }
    }
    await state.set_data(data)
    await message.answer(
        "Вы хотите найти топ самых дешевых отелей в городе. Я помогу вам.\nВведите название города:",
        reply_markup=cancel_keyboard
    )


@dp.message_handler(state=LowPriceSearchStates.low_price_get_city_name)
async def get_city_name(message: Message, state: FSMContext) -> None:
    """Получение названия города и первичный поиск."""
    city_name = message.text
    data = await state.get_data()
    data["location"]["name"] = city_name
    await state.set_data(data)