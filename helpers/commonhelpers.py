from typing import Any

commands_desc = {
    "lowprice": "топ самых дешёвых отелей в городе",
    "highprice": "топ самых дорогих отелей в городе",
    "bestdeal": "топ отелей, наиболее подходящих по цене и расположению от центра"
}

def find_sub_dict(data, key) -> dict:
    """Находит и возвращает словарь с переданным ключом"""
    if isinstance(data, list):
        for i_elem in data:
            result = find_sub_dict(i_elem, key)
            if result:
                return result
    elif isinstance(data, dict):
        if key in data:
            return data
        else:
            for i_value in data.values():
                result = find_sub_dict(i_value, key)
                if result:
                    return result
        return None

def get_value(data, key) -> Any:
    """
    Находит и возвращает значение переданного ключа в переданном объекте.
    Если ключ не найден, возвращает None
    """
    sub_dict = find_sub_dict(data, key)
    if sub_dict:
        return sub_dict[key]
    else:
        return None

def set_value(data, key, value) -> None:
    """
    Находит в переданном словаре ключ и устанавливает его в переданное значение.
    Если ключ не найден, создается новый ключ и инициализируется переданным значением.
    """
    sub_dict = find_sub_dict(data, key)
    if sub_dict:
        sub_dict[key] = value
    else:
        data[key] = value

def format_date_time(text: str) -> str:
    """Форматирует переданную строку в определенный формат даты и времени"""
    return text.strftime("%d.%m.%Y %H:%M:%S").split()
