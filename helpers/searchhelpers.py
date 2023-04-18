import json

def filter_search_locations(data) -> list:
    """Возвращает отфильтрованный"""
    return list(filter(lambda city: city["type"] == 'CITY', data))