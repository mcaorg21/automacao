from typing import Dict


class Portabilidade:
    def __init__(self, contrato: Dict[str, str]):
        self.__dados: Dict[str] = contrato

    @property
    def saldoDevedor(self):
        return self.__dados['dados_portabilidade']['saldoDevedorFinal'].replace(".", ",")

    @property
    def valorParcela(self):
        return self.__dados['dados_portabilidade']['parcela'].replace(".", ",")

    @property
    def quantidadeParcelas(self):
        return self.__dados['dados_portabilidade']['parcelasTotais']

    @property
    def quantidadeParcelasPagas(self):
        return self.__dados['dados_portabilidade']['parcelasPagas']

    @property
    def numeroContrato(self):
        return self.__dados['dados_portabilidade']['numeroContrato']

    @property
    def dataUltimoVencimento(self):
        return self.__dados['dados_portabilidade']['dataFimContrato'].replace("/", "")

    @property
    def dataPrimeiroVencimento(self):
        return self.__dados['dados_portabilidade']['dataInicioContrato']

    @property
    def cnpj(self):     # TODO: AUSENTE NA API
        return self.__dados['dados_portabilidade']['dataInicioContrato']

    @property
    def codigoBanco(self):
        return self.__dados['dados_portabilidade']['numeroBanco']

    @property
    def nomeBanco(self):
        return self.__dados['dados_portabilidade']['nomeBanco']
