from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    TimeoutException, WebDriverException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver import Chrome

from sites.baseRobos.core.captcha import FalhaScreenShotCaptcha, TwoCaptcha
from sites.elementos import Button, TextInput, Select
from sites.elementos.ContainerElements.TextContainer import TextContainer
from sites.ibConsig.libs.dto.Contrato import Contrato
from datetime import datetime as dt


class FormDadosIniciais:
    def __init__(self, contrato: Contrato, **kwargs):
        self.__dados: Contrato = contrato
        self.dados_captcha: dict = {}
        self.iptDataFator: TextInput = kwargs.get("iptDataFator")
        self.iptDataNasc: TextInput = kwargs.get("iptDataNasc")
        self.iptCodigoLoja: TextInput = kwargs.get("iptCodigoLoja")
        self.iptDataRenda: TextInput = kwargs.get("iptDataRenda")
        self.iptValorRenda: TextInput = kwargs.get("iptValorRenda")
        self.selectUFBeneficio: Select = kwargs.get("selectUFBeneficio")
        self.iptTipoBeneficio: TextInput = kwargs.get("iptTipoBeneficio")
        self.iptNPeculio: TextInput = kwargs.get("iptNPeculio")
        self.iptProfissao: TextInput = kwargs.get("iptProfissao")
        self.iptMargem: TextInput = kwargs.get("iptMargem")
        self.selectGrauInstrucao: Select = kwargs.get("selectGrauInstrucao")

    def preencherDataFator(self):
        dataFator = dt.now().strftime('%d/%m/%Y').replace("/", "")
        print(f"Preenchendo Data Fator: {dataFator}")
        self.iptDataFator.carregar_elemento()
        self.iptDataFator.act.click()
        self.iptDataFator.apagar_caracteres(12, delay=0.01, END=True)
        self.iptDataFator.enviar_texto(dataFator, clear=False)
        self.iptDataFator.press_TAB()

    def preencherDataNascimento(self):
        print(f"Preenchendo Data Nascimento: {self.__dados.dataNascimento}")
        self.iptDataNasc.carregar_elemento()
        self.iptDataNasc.act.click()
        self.iptDataNasc.enviar_texto(self.__dados.dataNascimento)
        self.iptDataNasc.press_TAB()

    def preencherCodigoLoja(self):
        print(f"Preenchendo Codigo Loja: {self.__dados.codigoLoja}")
        self.iptCodigoLoja.carregar_elemento()
        self.iptCodigoLoja.act.click()
        self.iptCodigoLoja.enviar_texto(self.__dados.codigoLoja)
        self.iptCodigoLoja.press_TAB()

    def preencherDataRenda(self):
        print(f"Preenchendo Data Renda: {self.__dados.dataRenda}")
        try:
            self.iptDataRenda.carregar_elemento()
            self.iptDataRenda.act.click()
            self.iptDataRenda.enviar_texto(self.__dados.dataRenda)
            self.iptDataRenda.press_TAB()
        except ElementClickInterceptedException as e:
            print(e)
            sleep(0.2)
            self.preencherDataRenda()

    def preencherValorRenda(self):
        print(f"Preenchendo Valor Renda: {self.__dados.valorRenda}")
        self.iptValorRenda.carregar_elemento()
        self.iptValorRenda.act.click()
        self.iptValorRenda.enviar_texto(self.__dados.valorRenda)
        self.iptValorRenda.press_TAB()

    def selecionarUFBeneficio(self):
        print(f"Preenchendo UF Beneficio: {self.__dados.ufBeneficio}")
        self.selectUFBeneficio.carregar_elemento()
        self.selectUFBeneficio.selecionar_opcao(self.__dados.ufBeneficio)

    def preencherTipoBeneficio(self):
        print(f"Preenchendo Tipo Beneficio: {self.__dados.tipoBeneficio}")
        self.iptTipoBeneficio.carregar_elemento()
        self.iptTipoBeneficio.act.click()
        self.iptTipoBeneficio.enviar_texto(self.__dados.tipoBeneficio)
        self.iptTipoBeneficio.press_TAB()

    def selecionarGrauInstrucao(self):
        print(f"Selecionando Grau Instrução: {self.__dados.grauInstrucao}")
        self.selectGrauInstrucao.carregar_elemento()
        self.selectGrauInstrucao.selecionar_opcao(self.__dados.grauInstrucao)
