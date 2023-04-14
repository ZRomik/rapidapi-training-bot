from setups import Users, History
from peewee import *
from helpers.idgenerator import get__new_search_id


def get_user_id(id: int) -> int:
    """Возвращает локальный идентификатор пользователя """
    try:
        user = Users.get(Users.tg_id == id)
        return user
    except:
        return None
    query = Users.select(["id"]).where(Users.tg_id == id)
    for user_id in query:
        if user_id:
            return user_id
    return None


def add_user(id: int) -> int:
    """Добавляет нового пользователя в таблицу пользователей и возвращает локальный идентификатор"""
    user_id = get_user_id(id=id)
    if user_id:
        return user_id
    return Users.create(tg_id = id).save()

def add_search(user_id: int, kind: str) -> int:
    """
    Добавляет в таблицу истории запись о новом поиске и возвращает идентификатор поиска
    :param user_id:
    :param kind:
    :return:
    """
    search_id = get__new_search_id()
    return History.create(user_id=user_id, search_id=search_id, search_kind=kind).save()