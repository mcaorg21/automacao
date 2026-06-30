from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.crefisa.libs.elementos.Botoes import btn_acessar_fact,btn_tfa_fact
from sites.crefisa.libs.elementos.TextInputs import input_senha_fact, input_login_fact, input_tfa_fact

from sites.elementos import Button, BaseElement
from sites.elementos import TextInput, Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By

from time import sleep
import pdb, sys, requests

import pyotp

class FormLogin:

    def __init__(self, driver: Chrome, login: str, senha: str):
        self.login_input: TextInput = input_login_fact(driver)
        self.senha_input: TextInput = input_senha_fact(driver)
        self.tfa_input: TextInput = input_tfa_fact(driver)
        
        self.btn_acessar: Button = btn_acessar_fact(driver)        
        self.btn_tfa: Button = btn_tfa_fact(driver)
        
        self.login: str = login
        self.senha: str = senha
        self.driver: Chrome = driver
        #self.site_key_captcha = '6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN'
        #self.act = 
        
    @staticmethod
    def realizar_login(driver: Chrome, login: str, senha: str, link = "https://app1.gerencialcredito.com.br/CREFISA/Dashboard.asp", popup_login = False) -> bool:
        
        login: FormLogin = FormLogin(driver, login, senha)
        
        if(popup_login == False):

            #driver.get(link_home)

            if login.esta_logado():
                driver.refresh()
                return True

            #driver.get(link)

            for i in range(1, 20):
                if login.esta_logado():
                    return True
                else:
                    driver.get(link)

                print(f"Login tentativa {i}")

                login.preencher_login()
                login.preencher_senha()    
                captcha_presente = SeleniumActions(driver).quantidade_elemento('//*[@id="recaptcha"]', By.XPATH)

                if(captcha_presente == 1):
                    print('Resolvendo Captcha')
                    retorno = SeleniumActions(driver).reCaptcha_v2('6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN')    
                
                login.clicar_btn_acessar()

                botao_validar = SeleniumActions(driver).quantidade_elemento('//*[@id="btn2faCode"]', By.XPATH)
                
                while (botao_validar > 0):
                    #secret = "IRCDQQJVGUYDERRVGMYDIRBQGFAUKMKBGY2EKNRYHBBEEN2EGFDA===="
                    #secret = "IJDECNRQGZAUIOKGIMYDIMJYGBBDONRVGUZDGMJZGJBEMMBVGM4A===="
                    secret = "II4EGMSGIVBDQOBUGZCDIQ2FIRATGRBXGQ4TOMRYIVBUIRBTHFBQ===="
                    
                    codigo_tfa = pyotp.TOTP(secret).now()
                    #codigo_tfa = login.ler_codigo()
    
                    print('>>>>>>>>>>>>>> Aguardando o codigo 2FA')
                    if(codigo_tfa == "000000" or codigo_tfa == ""):
                        print('Codigo 2FA 000000 ou vazio, inválido ou ainda não atualizado') 
                        driver.quit()
                        sleep(3)
                        
                    elif(codigo_tfa == "111111" or codigo_tfa == ""):
                        print('Codigo vencido...') 
                        sleep(3)
                        return False
                        
                    else:
                        login.preencher_2fa(codigo_tfa)
                        login.clicar_btn_tfa()
                                
                        sleep(3)
                        botao_validar = SeleniumActions(driver).quantidade_elemento('//*[@id="btn2faCode"]', By.XPATH)
                        if botao_validar > 0:
                            with open(login.path_arquivo, "w") as f:
                                f.write("000000")
                                print('Aguardando novo POST para atualizar o codigo 2FA')
                            
                sleep(2)

                print('Tentando logar')
                login.verificar_loading()
                #sleep(10)

            

        else:

            login.preencher_login()
            login.preencher_senha()    
            captcha_presente = SeleniumActions(driver).quantidade_elemento('//*[@id="recaptcha"]', By.XPATH)

            if(captcha_presente == 1):
                print('Resolvendo Captcha')
                retorno = SeleniumActions(driver).reCaptcha_v2('6Lf-1q0pAAAAAJCrjBOtEvZLrrFlL50mkWpwvSTN')    

            login.clicar_btn_acessar()

            botao_validar = SeleniumActions(driver).quantidade_elemento('//*[@id="btn2faCode"]', By.XPATH)
            
            while (botao_validar > 0):
                
                codigo_tfa = login.ler_codigo()
                        
                print('>>>>>>>>>>>>>> Aguardando o codigo 2FA')
                if(codigo_tfa == "000000" or codigo_tfa == ""):
                    print('Codigo 2FA 000000 ou vazio, inválido ou ainda não atualizado') 
                    raise Exception('Codigo 2FA 000000 ou vazio, inválido ou ainda não atualizado')
                    driver.quit()
                    sleep(3)
                    
                elif(codigo_tfa == "111111" or codigo_tfa == ""):
                    print('Codigo vencido...') 
                    sleep(3)
                    return False
                    
                else:
                    login.preencher_2fa(codigo_tfa)
                    login.clicar_btn_tfa()
                            
                    sleep(3)
                    botao_validar = SeleniumActions(driver).quantidade_elemento('//*[@id="btn2faCode"]', By.XPATH)
                    if botao_validar > 0:
                        with open(login.path_arquivo, "w") as f:
                            f.write("000000")
                            print('Aguardando novo POST para atualizar o codigo 2FA')                    
                            
                    
            print('Tentando logar')
            login.verificar_loading()

        return login.esta_logado()

    
    def ler_codigo(self):
        try:
            if "linux" in sys.platform:
                self.path_arquivo = sys.path[0]+"/libs/codigo.txt"
            else:
                self.path_arquivo = sys.path[0]+"\\sites\\crefisa\\libs\\codigo.txt"
                
            with open(self.path_arquivo, "r") as f:
                codigo = f.read().strip()
            
            return codigo
        
        except FileNotFoundError:
            return "Arquivo codigo.txt não encontrado."
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    def esta_logado(self) -> bool:
        seletor: str = '//*[@id="txtUsuario"]'
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
        
    def preencher_2fa(self, codigo):
        print(f"Preenchendo 2FA: ", codigo)
        self.tfa_input.carregar_elemento()
        self.tfa_input.apagar_caracteres(12, delay=0.01)
        self.tfa_input.enviar_caracteres(codigo, delay=0.01)

    def clicar_btn_acessar(self):
        print(f"Clicando {self.btn_acessar}")
        self.btn_acessar.carregar_elemento()
        self.btn_acessar.act.click()
    
    def clicar_btn_tfa(self):
        print(f"Clicando {self.btn_tfa}")
        self.btn_tfa.carregar_elemento()
        self.btn_tfa.act.click()

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

