import random
from helpers.db_helper import Users, History

ID_LEN = 6
alpha = "125485abcdABCDFG()/.jkd"

def get__new_search_id() -> str:
    """Генерирует случайный строковой идентификатор"""
    count = History().select().count
    symbols = [
        random.choice(alpha)
        for val in range(ID_LEN)
    ]