from setups import Users, History
from peewee import *

def add_user(id: int) -> int:
    """Добавляет нового пользователя в таблицу пользователей и возвращает идентификатор"""
    query = Users.select().where(Users.tg_id == id)
    for user_id in query:
        if user_id:
            return user_id
    return Users.create(tg_id = id).save()