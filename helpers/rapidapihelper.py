import requests
from os import getenv


class RapidapiHelper:
    @classmethod
    def get_helper(cls) -> "RapudapiHelper":
        """
        Реализация паттерна одиночка.
        """
        instance = getattr(cls, "__instance")
        if not instance:
            instance = RapidapiHelper()
            setattr(cls, "__instance", instance)
        return instance

    def __internal_get_request(self, end_point: str, params: dict, headers: dict = None) -> 'Response':
        request_url = '/'.join(["https://hotels4.p.rapidapi.com/v2/get-meta-data", end_point])
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
                timeout=7.0
            )