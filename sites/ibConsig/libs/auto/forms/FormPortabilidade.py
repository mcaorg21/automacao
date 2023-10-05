from time import sleep

from selenium.common.exceptions import ElementClickInterceptedException

from sites.elementos import TextInput
from sites.ibConsig.libs.dto.Contrato import Contrato


class FormPortabilidade:
    def __init__(self, contrato: Contrato, **kwargs):
        self.__dados: Contrato = contrato
        self.dados_captcha: dict = {}
        self.iptSaldoDevedor: TextInput = kwargs.get("iptSaldoDevedor")
        self.iptValorParcela: TextInput = kwargs.get("iptValorParcela")
        self.iptQtdParcelas: TextInput = kwargs.get("iptQtdParcelas")
        self.iptQtdParcelasPagas: TextInput = kwargs.get("iptQtdParcelasPagas")
        self.iptNoContrato: TextInput = kwargs.get("iptNoContrato")
        self.iptUltimoVencimento: TextInput = kwargs.get("iptUltimoVencimento")
        self.iptPrimeiroVencimento: TextInput = kwargs.get("iptPrimeiroVencimento")
        self.iptCnpj: TextInput = kwargs.get("iptCnpj")
        self.iptCodigoBanco: TextInput = kwargs.get("iptCodigoBanco")

    def preencherIptSaldoDevedor(self):
        print("Preenchendo Saldo Devedor:", self.__dados.portabilidade.saldoDevedor)
        self.iptSaldoDevedor.carregar_elemento()
        self.iptSaldoDevedor.act.click()
        self.iptSaldoDevedor.enviar_texto(
            self.__dados.portabilidade.saldoDevedor)
        self.iptSaldoDevedor.press_TAB()

    def preencherIptValorParcela(self, carregarElemento=True):
        print("Preenchendo Valor Parcela:", self.__dados.portabilidade.valorParcela)
        if carregarElemento:
            self.iptValorParcela.carregar_elemento()
        try:
            self.iptValorParcela.act.click()
        except ElementClickInterceptedException:
            print("Falha ao preencher campo, tentando novamente")
            sleep(0.5)
            self.preencherIptValorParcela(carregarElemento=False)
        self.iptValorParcela.enviar_texto(
            self.__dados.portabilidade.valorParcela)
        self.iptValorParcela.press_TAB()

    def preencherIptQtdParcelas(self):
        print("Preenchendo Qtde Parcelas:", self.__dados.portabilidade.quantidadeParcelas)
        self.iptQtdParcelas.carregar_elemento()
        self.iptQtdParcelas.act.click()
        self.iptQtdParcelas.enviar_texto(
            self.__dados.portabilidade.quantidadeParcelas)
        self.iptQtdParcelas.press_TAB()

    def preencherIptQtdParcelasPagas(self):
        print("Preenchendo Qtde Parcelas Pagas:",
              self.__dados.portabilidade.quantidadeParcelasPagas)
        self.iptQtdParcelasPagas.carregar_elemento()
        self.iptQtdParcelasPagas.act.click()
        self.iptQtdParcelasPagas.enviar_texto(
            self.__dados.portabilidade.quantidadeParcelasPagas)
        self.iptQtdParcelasPagas.press_TAB()

    def preencherIptNoContrato(self):
        print("Preenchendo Numero do Contrato:",
              self.__dados.portabilidade.numeroContrato)
        self.iptNoContrato.carregar_elemento()
        self.iptNoContrato.act.click()
        self.iptNoContrato.enviar_texto(
            self.__dados.portabilidade.numeroContrato.replace('-',''))
        self.iptNoContrato.press_TAB()

    def preencherIptUltimoVencimento(self):
        print("Preenchendo Data Ultimo Vencimento:",
              self.__dados.portabilidade.dataUltimoVencimento)
        self.iptUltimoVencimento.carregar_elemento()
        self.iptUltimoVencimento.act.click()
        self.iptUltimoVencimento.enviar_texto(
            self.__dados.portabilidade.dataUltimoVencimento)
        self.iptUltimoVencimento.press_TAB()

    def preencherIitPrimeiroVencimento(self):
        print("Preenchendo Data Primeiro Vencimento:",
              self.__dados.portabilidade.dataPrimeiroVencimento)
        self.iptPrimeiroVencimento.carregar_elemento()
        self.iptPrimeiroVencimento.act.click()
        self.iptPrimeiroVencimento.enviar_texto(
            self.__dados.portabilidade.dataPrimeiroVencimento)
        self.iptPrimeiroVencimento.press_TAB()

    def preencherIptCodigoBanco(self):
        print("Preenchendo numero do banco:",
              self.__dados.portabilidade.codigoBanco)
        self.iptCodigoBanco.carregar_elemento()
        self.iptCodigoBanco.act.click()
        self.iptCodigoBanco.enviar_texto(
            self.__dados.portabilidade.codigoBanco)
        self.iptCodigoBanco.press_TAB()
