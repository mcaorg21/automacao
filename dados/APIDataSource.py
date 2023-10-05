from dados.dados_apis import (
    uris_get, uris_post, uris_put)
from typing import Dict, Tuple
import requests
from requests import Response
from dados.dados_apis.keys import DEFAULT_KEY
import json

class APIDataSource:

    def __init__(self):
        self.__endpoint_get: Dict[str] = uris_get.GET
        self.__endpoint_post: Dict[str] = uris_post.POST
        self.__endpoint_put: Dict[str] = uris_put.PUT
        self.status_code: int = 0
        self.key = DEFAULT_KEY

    def get(self, nome_endpoint: str) -> str:
        return self.__endpoint_get[nome_endpoint]

    def post(self, nome_endpoint: str) -> str:
        return self.__endpoint_post[nome_endpoint]

    def put(self, nome_endpoint: str) -> str:
        return self.__endpoint_put[nome_endpoint]

    def get_request(self, nome_endpoint: str, **kwargs) -> Response:
        url: str = self.get(nome_endpoint)

        edit: Tuple[str] = kwargs.get("edit", ("", ""))
        if edit[0] and edit[1]:
            url: str = self.get(nome_endpoint).replace(*edit)
        kwargs.update({"key": self.key})

        data = {"key": self.key, **kwargs}

        print(f"API-GET: url: {url}\ndata: {data}")
        result = requests.get(
            url=url,
            params=data
        )
        self.status_code = result.status_code
        return result

    def post_request(self, nome_endpoint: str, **kwargs) -> Response:
        url: str = self.post(nome_endpoint)

        edit: Tuple[str] = kwargs.get("edit", ("", ""))
        if edit[0] and edit[1]:
            url: str = self.post(nome_endpoint).replace(*edit)

        result = requests.post(
            url=url,
            data=kwargs.update(key=self.key)
        )
        self.status_code = result.status_code
        return result

    def post_request_v2(self, nome_endpoint: str, dados) -> Response:
        url: str = self.post(nome_endpoint)
        print(dados)
        result = requests.post(
            url=url,
            data=dados,
        )
        self.status_code = result.status_code
        return result


    def post_request_v3(self, nome_endpoint: str, dados) -> Response:
        url: str = self.post(nome_endpoint)
        print(dados)
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        result = requests.post(
            url=url,
            data=json.dumps(dados),
            headers=headers
        )
        self.status_code = result.status_code
        return result



    def put_request(self, nome_endpoint: str, **kwargs) -> Response:
        result = requests.put(
            url=self.put(nome_endpoint),
            data=kwargs.update(key=self.key)
        )
        self.status_code = result.status_code
        return result


class ApiResponseException(Exception):
    def __init__(self, status_code, msg):
        self.status_code = status_code
        self.message = msg
        self.exc = (f"Status Code: {self.status_code}. "
                    f"Mensagem: {self.message}")

    def __repr__(self):
        return self.exc
