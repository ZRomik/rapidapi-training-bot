import random
from helpers.db_helper import Users, History

ID_LEN = 4
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def get__new_search_id() -> str:
    """Генерирует случайный строковой идентификатор"""
    count = History().select().count
    symbols = [
        random.choice(alphabet)
        for val in range(ID_LEN)
    ]
    return ''.join(symbols)