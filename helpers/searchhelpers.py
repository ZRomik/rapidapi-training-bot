from .commonhelpers import get_value
from typing import Any


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
            "amount": round(float(get_value(i_prop, "amount")), 2),
            #тут будет либо расстояние до центра, либо None. Зависит от типа поиска
            "distance": get_value(i_prop, "value"),
            "units": get_value(i_prop, "unit")
        }
        for i_prop in props_list
    ]

def get_values_for_sort_by_price_and_score(data: Any) -> tuple:
    amount = get_value(
        data,
        "amount"
    )
    score = get_value(
        data,
        "score"
    )
    return amount, score

def get_values_for_sort_by_ds(data: Any) -> tuple:
    score = float(
        get_value(
            data, "amount"
        )
    )
    distance = float(
        get_value(
            data, "distance"
        )
    )
    return distance, score


def sort_hotels_by_score(hotels_list: list) -> list:
    """
    Возвращает отсортированный оценке клиентов список отелей.
    :param hotels_list: (list) переданный список отелей.
    :return: (list) отсортированный список отелей.
    """
    return sorted(
        hotels_list,
        key=lambda score: score["score"]
    )

def sort_hotels_by_ds(hotels_list: list) -> list:
    """
    dsp - distance&score&price
    Сортирует переданный список отелей по расстоянию от центра, оценке постояльцев и цене
    :param hotels_list: (list) переданный список отелей
    :return: (list) отсортированный список отелей
    """
    return sorted(
        hotels_list,
        key=get_values_for_sort_by_ds
    )

def filter_image_list(images_list: list) -> list:
    """Фильтрует переданный список и исключает записи с адресом googleapis"""
    return list(filter(lambda no_google: "googleapis" not in no_google["image"]["url"], images_list))


def filter_hotels_by_price(raw_list: list, min_price: int, max_price: int) -> list:
    """
    Фильтрует переданный список отелей, удаляя записи, не попадающие в пределы цен
    :param raw_list: (list) нефильтрованный список отелей
    :param min_price: (int) минимальная цена номера.
    :param max_price: (int) максимальная цена номера.
    :return: (list) отфильтрованный список отелей
    """
    return list(filter(lambda price: min_price <= int(price["amount"]) <= max_price, raw_list))


def slice_list(raw_list: list, count: int) -> list:
    """
    Возвращает срез переданного списка
    :param raw_list: (list) переданный список
    :param count: (int) длина среза
    :return: (list) полученный срез
    """
    list_len = len(raw_list)
    if list_len > count:
        return raw_list[:count]
    else:
        return raw_list[:]

def sort_hotels_by_price_and_score(hotels_list: list, is_reverse: bool = False) -> list:
    """
    Сортирует переданный список отелей по цене и оценке посетителей
    :param hotels_list: (list) "сырой" список отелей
    :param is_reverse: (bool) флаг реверсной сортировки.
    :returns (list) результат сортировки
    """
    return sorted(
        hotels_list,
        key=get_values_for_sort_by_price_and_score,
        reverse=is_reverse
    )