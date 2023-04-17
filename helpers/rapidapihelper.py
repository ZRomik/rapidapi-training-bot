import requests
from os import getenv
from typing import Optional, Any
import json
import logging
from .commonhelpers import get_key_value

def from_str_date_to_dict_date(str_date: str) -> dict:
    """
    Переводит переданную дату в текстовом формате в дату в формате словаря для АПИ-запроса
    :param str_date: (str) дата в текстоваом формате.
    :return: (dict) дата в формате словаря для АПИ-запроса.
    """
    day, month, year = list(map(int, str_date.split(".")))
    return {
        "day": day,
        "month": month,
        "year": year
    }


class RapidapiHelper:
    @classmethod
    def get_helper(cls) -> "RapudapiHelper":
        """
        Реализация паттерна одиночка.
        """
        instance = getattr(cls, "__instance", None)
        if not instance:
            instance = RapidapiHelper()
            setattr(cls, "__instance", instance)
        return instance

    def __internal_get_request(self, end_point: str, *,
                               params: Optional[dict] = None, headers: Optional[dict] = None) -> "Response":
        """
        Выполнение GET-запроса к АПИ
        :param end_point: (str) точка запроса
        :param params: (dict) Опционально. Параметры запроса
        :param headers: (dict) Опционально. Заголовок запроса
        """
        request_url = '/'.join(["https://hotels4.p.rapidapi.com", end_point])
        if headers:
            header = headers.copy()
        else:
            header = {
                "X-RapidAPI-Key": getenv("KEY"),
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            }
            return requests.request(
                method='GET',
                params=params,
                url=request_url,
                headers=header,
                timeout=10
            )

    def __internal_post_request(self, end_point: str, *, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        """Выполнение POST-запроса к АПИ"""
        request_url = '/'.join(["https://hotels4.p.rapidapi.com", end_point])
        if headers:
            header = headers.copy()
        else:
            header = {
                "content-type": "application/json",
                "X-RapidAPI-Key": getenv("KEY"),
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            }
            return requests.request(
                method='POST',
                url=request_url,
                json=params,
                headers=header,
                timeout=10
            )


    def __is_good_response(self, data: 'Response'):
        return data and data.status_code == 200
    def get_metadata(self):
        response = self.__internal_get_request(
            end_point="v2/get-meta-data"
        )
        if self.__is_good_response(response):
            return response.json()
        else:
            code = response.status_code
            if code == 0:
                pass

    def search_location(self, name: str, metadata: dict) -> json:
        """
        Осуществляет поиск города по переданному названию.
        """
        query_params = {
            "q": name,
            "locale": "ru_RU",
            "langid": "1049",
            "siteid": metadata["site id"]
        }
        response = self.__internal_get_request(
            end_point="locations/v3/search",
            params=query_params
        )
        if self.__is_good_response(response):
            return response.json()
        else:
            logger = logging.getLogger(__name__)
            logger.error(
                f"Сервер вернул код: {response.status_code}"
            )
            return {}


    def get_properties_list(self, data: dict, sort_order: str) -> json:
        metadata = data["metadata"]
        children = get_key_value(data, "children")
        age_list = [
            {"age": i_age}
            for i_age in children
        ]
        query_params = {
            "currency": "USD",
            "eapid": metadata["eapid"],
            "locale": "ru_RU",
            "destination": {"regionId": get_key_value(data, "city id")},
        "checkInDate": from_str_date_to_dict_date(get_key_value(data, "check in")),
        "checkOutDate": from_str_date_to_dict_date(get_key_value(data, "check out")),
        "rooms": [
            {
                "adults": get_key_value(data, "adults"),
                "children": age_list
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": sort_order,
        "filters": {
            "price": {
                "max": get_key_value(data, "max price"),
                "min": get_key_value(data, "min price")
            }
        }
        }
        response = self.__internal_post_request(
            end_point="properties/v2/list",
            params=query_params
        )
        if self.__is_good_response(response):
            return response.json()
        else:
            logger = logging.getLogger(__name__)
            logger.error(
                f"Сервер вернул код: {response.status_code}"
            )
            return {}