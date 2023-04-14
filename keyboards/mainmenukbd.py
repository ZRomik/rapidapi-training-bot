from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_buttons = [
    [KeyboardButton("/lowprice"), KeyboardButton("/highprice")],
    [KeyboardButton("/bestdeal"), KeyboardButton("/help")]
]

main_menu_keybord = ReplyKeyboardMarkup(
    one_time_keyboard=False,
    resize_keyboard=True
)

main_menu_keybord.add(*main_menu_buttons)