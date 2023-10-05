from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.oleConsignado.libs.elementos.Botoes import btn_acessar_fact,btn_voltar
from sites.oleConsignado.libs.elementos.TextInputs import input_senha_fact, input_login_fact

from sites.elementos import Button, BaseElement
from sites.elementos import TextInput, Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.oleConsignado.config.auth import DATA_SITE_KEY, HORARIO_COMERCIAL

from time import sleep

class FormLogin:

    def __init__(self, driver: Chrome, login: str, senha: str):
        self.login_input: TextInput = input_login_fact(driver)
        self.senha_input: TextInput = input_senha_fact(driver)
        self.btn_acessar: Button = btn_acessar_fact(driver)
        self.btn_voltar: Button = btn_voltar(driver)
        self.login: str = login
        self.senha: str = senha
        self.driver: Chrome = driver

    @staticmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def realizar_login(driver: Chrome, login: str, senha: str) -> bool:
        login: FormLogin = FormLogin(driver, login, senha)

        for i in range(1, 11):
            if login.esta_logado():
                return True
            else:
                driver.get('https://ola.oleconsignado.com.br/')

            print(f"Login tentativa {i}")
            try:
                login.resolver_recaptcha()
            except:
                FormLogin(driver, login, senha)
            login.preencher_login()
            login.preencher_senha()
            login.clicar_btn_acessar()
            print('Tentando logar')
            sleep(15)
            driver.refresh()

        return login.esta_logado()

    def esta_logado(self) -> bool:
        seletor: str = '//*[@id="rc-anchor-container"]/div[3]'
        try:
            self.login_input.carregar_elemento()
            print("Usuário não está logado.")
            return False
        except:
            try:
                self.btn_voltar.carregar_elemento()
                print("Usuário não está logado.")
                return False
            except TimeoutException as e:  
                print("Usuário logado.")
                return True

    def preencher_login(self):
        print(f"Preenchendo {self.login_input}:", self.login)
        self.login_input.carregar_elemento()
        self.login_input.apagar_caracteres(12, delay=0.01)
        self.login_input.enviar_caracteres(self.login, delay=0.1)

    def preencher_senha(self):
        print(f"Preenchendo {self.senha_input}:", self.senha)
        self.senha_input.carregar_elemento()
        self.senha_input.apagar_caracteres(12, delay=0.01)
        self.senha_input.enviar_caracteres(self.senha, delay=0.1)

    def clicar_btn_acessar(self):
        print(f"Clicando {self.btn_acessar}")
        self.btn_acessar.carregar_elemento()
        self.btn_acessar.act.click()

    def resolver_recaptcha(self):
        print("Resolver recaptcha")
        SeleniumActions(self.driver).reCaptcha_v2(DATA_SITE_KEY)
