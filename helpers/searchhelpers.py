import json
from .commonhelpers import get_value

def filter_search_locations(data) -> list:
    """Возвращает отфильтрованный"""
    return list(filter(lambda city: city["type"] == 'CITY', data))

def filter_props_list(props_list: list) -> list:
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