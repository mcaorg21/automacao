from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.elementos import Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By

from selenium.webdriver.common.alert import Alert

from time import sleep

import pdb

class FormLogin:

    def __init__(self, driver: Chrome):
        self.driver: Chrome = driver

    @staticmethod
    def realizar_login(driver: Chrome, link_home = "https://web.whatsapp.com/") -> bool:
        
        login: FormLogin = FormLogin(driver)

        driver.get(link_home)

        sleep(3)

        if login.esta_logado():
            print('VVVVVVVVVVVVVVVVVVVVV LOGADO VVVVVVVVVVVVVVVVVVVVV')
            login.verificar_loading()

        else:
            input('-------------------- Faça o QRCODE --------------------')
        
        return True

    def esta_logado(self) -> bool:
        try:
            Alert(self.driver).dismiss()
        except:
            pass

        logado = True
        try:
            botao = SeleniumActions(self.driver).obter_texto('/html/body/div[1]/div/div/div[2]/div[3]/div[1]/aside/div/div[3]/button/div/div', By.XPATH) 
            if 'Baixar o app' in botao:
                logado = False
        except:
            pass
            
        return logado

        # if(SeleniumActions(self.driver).quantidade_elemento('//*[@id="wa_web_initial_startup"]', By.XPATH) == 1):
        #     return False
        # else:
        #     return True

    def verificar_loading(self, interacoes=300, aguardar = False):
        while (SeleniumActions(self.driver).quantidade_elemento("/html/body/div[1]/div/div/div[2]/div[4]/div/div/div[2]/div[1]/h1", By.XPATH) == 0):
            if(SeleniumActions(self.driver).obter_texto("/html/body/div[1]/div/div/div[2]/div[4]/div/div/div[2]/div[1]/h1", By.XPATH) != 'WhatsApp Web'):
                print('Aguardando Loading...' + str(interacoes))
                sleep(1)
                interacoes -= 1
                if(interacoes < -35):
                    self.driver.quit()

