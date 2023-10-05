from typing import Union

from requests import Request, PreparedRequest, Session, Response
import requests


class RequestHandler:
    def __init__(self, **kwargs):
        self.url: str = kwargs.get("url")
        self.method: str = kwargs.get("method")
        self.auth: str = kwargs.get("auth")
        self.headers = kwargs.get("headers")
        self.data = kwargs.get("data")
        self.params = kwargs.get("params")
        self.__response: Union[Response, None] = None

    def send(self):
        print(self.params)
        r = requests.request(
            method=self.method,
            url=self.url,
            params=self.params,
            data=self.data,
            headers=self.headers
        )
        print(r.content)
        self.__response = r

    @property
    def receive(self) -> Response:
        return self.__response

    @property
    def receiveAsJson(self) -> dict:
        if self.__response is None:
            raise NullRequestResponseException(self.url)
        return self.__response.json()

    def checkForErrors(self):
        if self.__response.status_code != 200:
            raise Exception(f"ERROR: {self.__response.status_code}")


class NullRequestResponseException(Exception):
    def __init__(self, apiName):
        self.msg = f"Request returned null response in {apiName}"

    def __repr__(self):
        return self.msg
