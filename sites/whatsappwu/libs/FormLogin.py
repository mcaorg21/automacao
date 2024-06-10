from selenium.common.exceptions import TimeoutException

from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.elementos import Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By

from time import sleep

import pdb

class FormLogin:

    def __init__(self, driver: Chrome):
        self.driver: Chrome = driver

    @staticmethod
    def realizar_login(driver: Chrome, link_home = "https://web.whatsapp.com/") -> bool:
        
        login: FormLogin = FormLogin(driver)

        driver.get(link_home)

        if login.esta_logado():
            print('VVVVVVVVVVVVVVVVVVVVV LOGADO VVVVVVVVVVVVVVVVVVVVV')

        else:
            input('-------------------- Faça o QRCODE --------------------')
        
        return True

    def esta_logado(self) -> bool:
        print(SeleniumActions(self.driver).quantidade_elemento('//*[@id="wa_web_initial_startup"]', By.XPATH))
        if(SeleniumActions(self.driver).quantidade_elemento('//*[@id="wa_web_initial_startup"]', By.XPATH) == 1):
            return False
        else:
            return True

    def verificar_loading(self, interacoes=300, aguardar = False):
        pdb.set_trace()
        while (SeleniumActions(self.driver).quantidade_elemento('//*[@id="wa_web_initial_startup"]', By.XPATH) == 0):
            print('Aguardando Loading...' + str(interacoes))
            sleep(2)
            interacoes -= 1
            if(interacoes < -35):
                self.driver.quit()

