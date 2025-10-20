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

import PATHS

class FormLogin:

    def __init__(self, driver: Chrome, login: str, senha: str):
        self.login_input: TextInput = input_login_fact(driver)
        self.senha_input: TextInput = input_senha_fact(driver)
        self.btn_acessar: Button = btn_acessar_fact(driver)
        self.login: str = login
        self.senha: str = senha
        self.driver: Chrome = driver
        #self.site_key_captcha = '6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN'
        self.act = SeleniumActions(driver)

    @staticmethod
    def realizar_login(driver: Chrome, login: str, senha: str, link = "") -> bool:
        
        login: FormLogin = FormLogin(driver, login, senha)
        
        logado = login.esta_logado()
        
        while logado == False:
            
            logado = login.esta_logado()
            
            if logado == True:
                print('Já está logado')
                break

            login.preencher_login()
            login.preencher_senha()    
            # captcha_presente = SeleniumActions(driver).quantidade_elemento('//*[@id="recaptcha"]', By.XPATH)

            # if(captcha_presente == 1):
            #     print('Resolvendo Captcha')
            #     retorno = SeleniumActions(driver).reCaptcha_v2('6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN')    

            login.clicar_btn_acessar()
            try:
                texto_login = SeleniumActions(driver).obter_texto('//*[@id="divAlertaMsg"]', By.XPATH)
                if('SENHA PRECISA SER ALTERADA' in texto_login):
                    pdb.set_trace()
                    SeleniumActions(driver).clicar_elemento('/html/body/div[6]/div/div/div[3]/button', By.XPATH)
                    SeleniumActions(driver).clicar_elemento('/html/body/div[2]/div/form/div/div[3]/input[2]', By.XPATH)
                    SeleniumActions(driver).enviar_texto('//*[@id="senhaAtual_editar"]', senha, By.XPATH)
                    
                    senha_nova = senha[:-1] + str(int(senha[-1]) + 1)

                    SeleniumActions(driver).enviar_texto('//*[@id="novaSenha_editar"]', senha_nova, By.XPATH)
                    SeleniumActions(driver).enviar_texto('//*[@id="novaSenhaR_editar"]', senha_nova, By.XPATH)

                    with open(PATHS.project_path()+'\\facta\\libs\\'+"code.txt", "w", encoding="utf-8") as f: 
                        f.write(senha_nova)
                        
                    SeleniumActions(driver).clicar_elemento('//*[@id="alterarSenhaBotao"]', By.XPATH)
                    sleep(3)
                    SeleniumActions(driver).clicar_elemento('//*[@id="alterarSenhaBotao"]', By.XPATH)
                    SeleniumActions(driver).clicar_elemento('//button[contains(text(), "Fechar")]', By.XPATH)
                    sleep(1)

                    senha = senha_nova
                    input('A senha precisa ser alterada. Pressione Enter para continuar...')
                    
                    return
            except:
                pass
            
            print('Tentando logar')
            #login.verificar_loading()
            sleep(5)

            

        return True



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

