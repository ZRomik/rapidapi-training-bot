from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


choice_buttons = [
    KeyboardButton(
        "Искать"
    ),
    KeyboardButton(
        "Отмена"
    )
]

choice_keyboard = ReplyKeyboardMarkup(
    one_time_keyboard=False,
    resize_keyboard=True,
    keyboard=choice_buttons
)

cancel_keyboard = ReplyKeyboardMarkup(
    one_time_keyboard=False,
    resize_keyboard=True,
    keyboard=[KeyboardButton("Отмена")]
)