from typing import Dict

from sites.baseRobos.core.data_helpers import strip_zero_left


class DadosPessoais:
    def __init__(self, contrato: Dict[str, str]):
        self.__dados: Dict[str] = contrato

    @property
    def nome(self):
        return self.__dados['nome']

    @property
    def sexo(self):
        return self.__dados['sexo']

    @property
    def estadoCivil(self):
        return self.__dados['estadoCivil']

    @property
    def nomeConjuge(self):
        return self.__dados['nomeConjuge']

    @property
    def nomeMae(self):
        return self.__dados['nomeMae']

    @property
    def nomePai(self):
        return self.__dados['nomePai']

    @property
    def cidadeNascimento(self):
        return self.__dados['cidadeNascimento']

    @property
    def ufNascimento(self):
        return self.__dados['ufNascimento']

    @property
    def nacionalidade(self):
        return self.__dados['nacionalidade']

    @property
    def tipoIdentidade(self):
        return self.__dados['tipoIdentidade']

    @property
    def numeroIdentidade(self):
        return self.__dados['identidade']['numero']

    @property
    def orgaoEmissor(self):
        return self.__dados['identidade']['emissor']

    @property
    def ufIdentidade(self):
        return self.__dados['identidade']['uf']

    @property
    def dataEmissao(self):
        return self.__dados['identidade']['dataEmissao']




