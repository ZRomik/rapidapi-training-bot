import datetime
from setups import Users, History, CommandsInfo


def get_user_id(id: int) -> int:
    """Возвращает идентификатор пользователя в БД"""
    try:
        user = Users.get(Users.tg_id == id)
        return user.id
    except:
        return None

def add_user(id: int) -> int:
    """Добавляет нового пользователя в таблицу пользователей и возвращает локальный идентификатор"""
    user_id = get_user_id(id=id)
    if user_id:
        return user_id
    return Users.insert(tg_id = id).execute()

def add_new_search(user_id: int, kind: str) -> int:
    """
    Добавляет в таблицу истории запись о новом поиске и возвращает идентификатор поиска
    :param user_id: (int) идентификатор пользователя
    :param kind: (str) имя команды
    :return: (int) идентификатор записи
    """
    return (
        History.insert(
            user_id=user_id,
            command_id=CommandsInfo.select().where(CommandsInfo.command == kind)
            # search_kind=kind
        )
        .execute()
    )

def cancel_search_by_user(search_id: int) -> None:
    """
    Обновляет таблицу истории. Выставляет флаг отмены поиска пользователем.
    :param search_id: (int) идентификатор записи в таблице истории
    """
    History.update(
        {"cancelled": True,
         "user_cancel": True,
         "end_date": datetime.datetime.now()})\
        .where(id == search_id).execute()

def cancel_search_by_error(search_id: int) -> None:
    """
    Обновляет таблицу истории. Выставляет флаг отмены поиска из-за ошибки.
    :param search_id: (int) идентификатор записи в таблице истории
    """
    History.update(
        {
            "cancelled": True,
            "error_cancel": True
        }
    ).where(
        id == search_id
    ).execute()

def update_city_name(search_id: int, city_name: str) -> None:
    """
    Обновляет таблицу истории. Устанавливает название города.
    :param search_id: (int) идентификатор записи в таблице истории
    """
    History.update({"city_name": city_name}).where(id == search_id).execute()

def update_city_id(search_id: int, city_id: str) -> None:
    """
    Обновляет таблицу истории. Устанавливает id города.
    :param search_id: (int) идентификатор записи в таблице истории
    """
    History.update({"city_id": city_id}).where(id == search_id).execute()

def update_history_data(id: int, data: dict) -> None:
    """
    Обновляет таблицу истории.
    :param id: (int) идентификатор поиска
    :param values: (dict) новые поля и значения
    """
    History.update(data).where(History.id == id).execute()

def get_history(user_id: int, limit: int) -> list:
    """
    Возвращает список словарей с данными о завершенных поисках пользователя.
    :param user_id: (int) тг-идентификатор пользователя
    :param limit: (int) сколько записей вернуть
    :return: (list) результат поиска
    """
    query = History.select().where(History.user_id == user_id).limit(limit)
    return [
        {
            "start date": i_rec.start_date,
            "kind": i_rec.search_kind,
            "city name": i_rec.city_name,
            "cancelled": i_rec.cancelled,
            "user cancel": i_rec.user_cancel,
            "error cancel": i_rec.error_cancel,
            "end date": i_rec.end_date,
            "adults": i_rec.adults,
            "children": i_rec.children
        }
        for i_rec in query
    ]

def succes_end_search(search_id: int) -> None:
    """Обновляет таблицу истории записью, завершающей поиск"""
    History.update(
        {"end_date": datetime.datetime.now()}
    ).where(
        History.id == search_id
    ).execute()