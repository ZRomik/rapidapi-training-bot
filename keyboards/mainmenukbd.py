from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_buttons = [
    [KeyboardButton("/lowprice"), KeyboardButton("/highprice")],
    [KeyboardButton("/bestdeal"), KeyboardButton("/help")],
    [KeyboardButton("/history")]
]

main_menu_keybord = ReplyKeyboardMarkup(
    one_time_keyboard=False,
    resize_keyboard=True,
    keyboard=main_menu_buttons
)