import requests
from os import getenv
from typing import Optional, Any
import json


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
                               params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
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
                timeout=4.0
            )

    def __internal_post_request(self, end_point: str, *, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        """Выполнение POST-запроса к АПИ"""
        request_url = '/'.join(["https://hotels4.p.rapidapi.com/v2/get-meta-data", end_point])
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
                headers=header
            )


    def __is_good_response(self, data: 'Response'):
        return data and data.status_code == 200
    def get_metadata(self):
        response = self.__internal_get_request(
            end_point="v2/get-meta-data"
        )
        if self.__is_good_response(response):
            return json.loads(response.text)