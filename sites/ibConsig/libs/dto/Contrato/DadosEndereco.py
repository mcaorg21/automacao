from typing import Dict

from sites.baseRobos.core.data_helpers import strip_zero_left


class DadosEndereco:
    def __init__(self, contrato: Dict[str, str]):
        self.__dados: Dict[str] = contrato

    @property
    def cep(self):
        return self.__dados['endereco']["cep"]

    @property
    def numero(self):
        return self.__dados['endereco']["numero"]

    @property
    def logradouro(self):
        return self.__dados['endereco']['logradouro']

    @property
    def bairro(self):
        return self.__dados['endereco']['bairro']

    @property
    def complemento(self):
        return self.__dados['endereco']['complemento']

    @property
    def dddTelefone(self):
        return self.__dados['telefone']['ddd']

    @property
    def numeroTelefone(self):
        return self.__dados['telefone']['numero']

    @property
    def dddCelular(self):
        return self.__dados['celular1']['ddd']

    @property
    def numeroCelular(self):
        return self.__dados['celular1']['numero']

