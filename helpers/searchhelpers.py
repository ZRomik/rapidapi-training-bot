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
        "score": int(get_value(i_prop, "score")),
        "amount": round(float(get_value(i_prop, "amount")), 2)
    }
    for i_prop in props_list
    ]

def get_values_for_sort_by_price_and_score(data):
    price = float(get_value(data, "amount"))
    score = float(get_value(data, "score"))
    return price, score

def sort_hotels_by_price_and_score(hotels_list: list) -> list:
    """
    Возвращает отсортированный по оценке клиентов список отелей.
    :param hotels_list: (list) переданный список отелей.
    :param min_price: (int) минимальная цена проживания
    :param max_price: (int) максимальная цена проживания
    :return: (list) отсортированный список отелей.
    """
    return sorted(hotels_list, key=get_values_for_sort_by_price_and_score)

def filter_image_list(images_list: list) -> list:
    """Фильтрует переданный список и исключает записи с адресом googleapis"""
    return list(filter(lambda no_google: "googleapis" not in no_google["image"]["url"], images_list))

def filter_hotels_by_price(raw_list: list, min_price: int, max_price: int) -> list:
    """
    Фильтрует переданный список отелей, удаляя записи, не попадающие в пределы цен
    :param raw_list: (list) неотфильтрованный списое отелей
    :param min_price: (int) минимальная цена номера.
    :param max_price: (int) максимальная цена номера.
    :return: (list) отфильтрованный список отелей
    """
    return list(filter(lambda price: min_price <= int(get_value(price, "amount")) <= max_price, raw_list))