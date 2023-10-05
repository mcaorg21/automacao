from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    TimeoutException, WebDriverException, ElementNotInteractableException
from selenium.webdriver import Chrome

from sites.baseRobos.core.captcha import FalhaScreenShotCaptcha, TwoCaptcha
from sites.elementos import Button, TextInput, Select
from sites.elementos.ContainerElements.TextContainer import TextContainer
from sites.ibConsig.libs.dto.Contrato import Contrato


class FormIdentificacao:
    def __init__(self, driver: Chrome, contrato: Contrato, **kwargs):
        self.__driver: Chrome = driver
        self.__dados: Contrato = contrato
        self.dados_captcha: dict = {}
        self.btnMenuExpandir: Button = kwargs.get("btnMenuExpandir")
        self.btnMenuExpandido: Button = kwargs.get("btnMenuExpandido")
        self.btnMenuExpandido2: Button = kwargs.get("btnMenuExpandido2")
        self.inputEntidade: TextInput = kwargs.get("inputEntidade")
        self.selectServico: Select = kwargs.get("selectServico")
        self.inputMatricula: TextInput = kwargs.get("inputMatricula")
        self.inputDataNascimento: TextInput = kwargs.get("inputDataNascimento")
        self.inputCpf: TextInput = kwargs.get("inputCpf")
        self.inputCaptcha: TextInput = kwargs.get("inputCaptcha")
        self.btnConfirmar: Button = kwargs.get("btnConfirmar")
        self.divErro: TextContainer = kwargs.get("divErro")
        self.btnPropostaAndamento: Button = kwargs.get("btnPropostaAndamento")
        self.captchaCorreto = False
        self.captchaDisponivel = False

    @property
    def erroApiCaptcha(self):
        return "error" in self.dados_captcha["resp"].lower()

    @property
    def captchaResolvido(self):
        return self.captchaCorreto and self.captchaDisponivel

    def clicarBtnMenuExpandir(self):
        print("Clicando no Botão Expandir Menu",)
        self.btnMenuExpandir.carregar_elemento()
        self.btnMenuExpandir.act.click()

    def clicarBtnMenuExpandido(self):
        print("Clicando no Link Da Operação")
        self.btnMenuExpandido.carregar_elemento()
        self.btnMenuExpandido.act.click()

    def clicarBtnMenuExpandido2(self):
        print("Clicando no Link Da Operação Portabilidade")
        self.btnMenuExpandido2.carregar_elemento()
        self.btnMenuExpandido2.act.click()

    def clicarBtnMenuExpandido2(self):
        print("Clicando no Link Da Operação Portabilidade")
        self.btnMenuExpandido2.carregar_elemento()
        self.btnMenuExpandido2.act.click()

    def preencherInputEntidade(self):
        print(f"Preenchendo Entidade:  {self.__dados.entidade}")
        self.inputEntidade.carregar_elemento()
        #self.inputEntidade.act.click()
        self.inputEntidade.act.send_keys(self.__dados.entidade)
        self.inputEntidade.press_TAB()

    def selecionarSelectServico(self, value=1):
        print("Selecionando serviço opção:", value)
        self.selectServico.carregar_elemento()
        try:
            self.selectServico.selecionar_opcao(value)
        except NoSuchElementException:
            print("Opção não encontrada ou já selecionada")
        except StaleElementReferenceException:
            sleep(0.5)
            self.selecionarSelectServico(value)

    def preencherInputCpf(self):
        print(f"Preenchendo CPF: {self.__dados.cpf}")
        try:
            self.inputCpf.carregar_elemento()
            self.inputCpf.act.click()
            if not self.inputCpf.esta_vazio():
                self.inputCpf.apagar_caracteres(15, delay=0.03, END=True)
            self.inputCpf.enviar_caracteres(self.__dados.cpf, delay=0.02, clear=False)
            sleep(0.2)
            self.inputCpf.press_TAB()
        except StaleElementReferenceException as e:
            print("Falha ao preencher campo, tentando novamente")
            sleep(0.5)
            self.preencherInputCpf()
        except ElementNotInteractableException as e:
            print("Falha ao preencher campo, tentando novamente")
            sleep(0.5)
            self.preencherInputCpf()

    def preencherInputMatricula(self):
        print(f"Preenchendo Matricula: {self.__dados.matricula}")
        self.inputMatricula.carregar_elemento()
        self.inputMatricula.act.click()
        if not self.inputMatricula.esta_vazio():
            self.inputMatricula.apagar_caracteres(15, delay=0.01, END=True)
        self.inputMatricula.act.send_keys(self.__dados.matricula)
        self.inputMatricula.press_TAB()

    def preencherInputDataNascimento(self):
        print(f"Preenchendo Data Nascimento: {self.__dados.dataNascimento}")
        self.inputDataNascimento.carregar_elemento()
        self.inputDataNascimento.act.send_keys(self.__dados.dataNascimento)
        self.inputDataNascimento.press_TAB()

    def resolverCaptcha(self):
        try:
            print("\rResolvendo Captcha...", end="")
            seletor_captcha = "#identificacao-form\\:idCaptcha\\:idImagemCaptcha img"
            idCaptcha, resp = TwoCaptcha(self.__driver).resolver_captcha(seletor_captcha, "2.jpg")
            self.dados_captcha["id"], self.dados_captcha["resp"] = idCaptcha, resp
            print("Resultado:", self.dados_captcha)
        except FalhaScreenShotCaptcha:
            return 0

    def preencherCaptcha(self):
        print(f"Preenchendo Captcha: {self.dados_captcha}")
        self.inputCaptcha.carregar_elemento()
        self.inputCaptcha.act.click()
        if not self.inputCaptcha.esta_vazio():
            self.inputCaptcha.apagar_caracteres(15, delay=0.01, END=True)
        self.inputCaptcha.act.send_keys(self.dados_captcha["resp"])
        self.inputCaptcha.press_TAB()

    def clicarConfirmar(self):
        print("Clicando Confirmar")
        self.btnConfirmar.carregar_elemento()
        self.btnConfirmar.act.click()

    def verificarDivErro(self) -> str:
        print("Verificando <div> de erro")
        try:
            erro = self.divErro.driver.execute_script(
                "return $('.error_message\\:visible').text()")
            return erro
        except WebDriverException:
            print("Preenchido sem erros")
            return ""

    def clicarSerguirInsercao(self):
        try:
            self.btnPropostaAndamento.carregar_elemento()
        except TimeoutException:
            return
        self.btnPropostaAndamento.act.click()
