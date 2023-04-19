import json
from .commonhelpers import get_value

def filter_search_locations(data) -> list:
    """Возвращает отфильтрованный"""
    return list(filter(lambda city: city["type"] == 'CITY', data))

def build_hotels_list(props_list: list) -> list:
    """Возвращает список словарей с данными об отеле"""
    return [
        {
        "id": get_value(i_prop, "id"),
        "name": get_value(i_prop, "name"),
        "score": float(get_value(i_prop, "score")),
        "amount": get_value(i_prop, "amount")
    }
    for i_prop in props_list
    ]

def sort_hotels_by_score(hotels_list: list) -> list:
    """
    Возвращает отсортированный по оценке клиентов список отелей.
    :param hotels_list: (list) переданный список отелей.
    :return: (list) отсортированный список отелей.
    """
    return sorted(hotels_list, key=lambda score: score["score"], reverse=True)

def build_images_list(images_list: list) -> list:
    """Фильтрует переданный список и исключает записи с адресом googleapis"""
    return list(filter(lambda no_google: "googleapis" not in no_google["image"]["url"], images_list))