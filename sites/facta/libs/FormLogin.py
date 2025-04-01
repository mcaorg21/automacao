from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.facta.libs.elementos.Botoes import btn_acessar_fact
from sites.facta.libs.elementos.TextInputs import input_senha_fact, input_login_fact

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
        #self.site_key_captcha = '6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN'
        #self.act = 

    @staticmethod
    def realizar_login(driver: Chrome, login: str, senha: str, link = "") -> bool:

        login: FormLogin = FormLogin(driver, login, senha)

        login.preencher_login()
        login.preencher_senha()    
        # captcha_presente = SeleniumActions(driver).quantidade_elemento('//*[@id="recaptcha"]', By.XPATH)

        # if(captcha_presente == 1):
        #     print('Resolvendo Captcha')
        #     retorno = SeleniumActions(driver).reCaptcha_v2('6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN')    

        login.clicar_btn_acessar()
        print('Tentando logar')
        #login.verificar_loading()

        return login.esta_logado()



    def esta_logado(self) -> bool:
        seletor: str = '//*[@id="login"]'
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
        SeleniumActions(self.driver).reCaptcha_v2(self.site_key_captcha)

    def verificar_loading(self, interacoes=300, aguardar = False):
        while (SeleniumActions(self.driver).quantidade_elemento('//*[@id="modal-root"]/div/div', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            sleep(2)
            interacoes -= 1
            if(interacoes < -35):
                self.driver.quit()

