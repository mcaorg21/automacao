from typing import Dict

from sites.baseRobos.core.data_helpers import strip_zero_left


class DadosBancarios:
    def __init__(self, contrato: Dict[str, str]):
        self.__dados: Dict[str] = contrato

    @property
    def formaCredito(self):
        return self.__dados['formaCredito']

    @property
    def numeroBanco(self):
        return self.__dados['banco']['numeroBanco']

    @property
    def agencia(self):
        return self.__dados['banco']['agencia']

    @property
    def digitoAgencia(self):
        return self.__dados['banco']['digitoAgencia']

    @property
    def finalidadeCredito(self):
        return self.__dados['finalidadeCredito']

    @property
    def numeroConta(self):
        return self.__dados['banco']['numeroConta']

    @property
    def digitoConta(self):
        return self.__dados['banco']['digitoConta']



