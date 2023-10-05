from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.novosaque.libs.elementos.Botoes import btn_acessar_fact
from sites.novosaque.libs.elementos.TextInputs import input_senha_fact, input_login_fact

from sites.elementos import Button, BaseElement
from sites.elementos import TextInput, Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By

from time import sleep
import pdb

class FormLogin:

    def __init__(self, driver: Chrome, login: str, senha: str):
        self.login_input: TextInput = input_login_fact(driver)
        self.senha_input: TextInput = input_senha_fact(driver)
        self.btn_acessar: Button = btn_acessar_fact(driver)
        self.login: str = login
        self.senha: str = senha
        self.driver: Chrome = driver

    @staticmethod
    def realizar_login(driver: Chrome, login: str, senha: str) -> bool:
        login: FormLogin = FormLogin(driver, login, senha)

        driver.get('https://nsaque.ultragate.com.br/')

        for i in range(1, 11):
            if login.esta_logado():
                return True
            else:
                driver.get('https://nsaque.ultragate.com.br/')

            print(f"Login tentativa {i}")

            login.preencher_login()
            login.preencher_senha()            
            login.clicar_btn_acessar()
            print('Tentando logar')
            login.verificar_loading()
            #sleep(10)

        return login.esta_logado()

    def esta_logado(self) -> bool:
        seletor: str = '//*[@id="email"]'
        try:
            self.login_input.carregar_elemento()
            print("Usuário não está logado.")
            return False
        except:
            return True

    def preencher_login(self):
        print(f"Preenchendo {self.login_input}:", self.login)
        self.login_input.carregar_elemento()
        self.login_input.apagar_caracteres(12, delay=0.01)
        self.login_input.enviar_caracteres(self.login, delay=0.01)

    def preencher_senha(self):
        print(f"Preenchendo {self.senha_input}:", self.senha)
        self.senha_input.carregar_elemento()
        self.senha_input.apagar_caracteres(12, delay=0.01)
        self.senha_input.enviar_caracteres(self.senha, delay=0.01)

    def clicar_btn_acessar(self):
        print(f"Clicando {self.btn_acessar}")
        self.btn_acessar.carregar_elemento()
        self.btn_acessar.act.click()

    def resolver_recaptcha(self):
        print("Resolver recaptcha")
        SeleniumActions(self.driver).reCaptcha_v2(DATA_SITE_KEY)

    def verificar_loading(self, interacoes=35, aguardar = False):
        while (SeleniumActions(self.driver).quantidade_elemento('//*[@id="modal-root"]/div/div', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            sleep(2)
            interacoes -= 1
