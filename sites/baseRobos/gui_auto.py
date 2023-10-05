"""
| projeto: automacao-python
| arquivo: gui_auto.py
| data: 21/11/2019
| autor: Gustavo Belleza

Contém atributos e métodos criados para implementar a automação da interface do navegador.
"""
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper

from sites.baseRobos.core.captcha import TwoCaptcha, FalhaScreenShotCaptcha

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import traceback, os
from sites.baseRobos.core.data_helpers import gen_log
from time import sleep


class AutoGUI(object):
    """
    atributos:
    self.chrome_driver = instância do webdriver.
    self.act = instância do SeleniumActions, classe que implementa funcionalidades do selenium webdriver
        utilizando Wait.until(EC).
    self.sh = instância do SeleniumHelper, classe que implementa funcionalidades do selenium webdriver utilizando
        scripts JS/JQuery.
    self.captcha = instância do TwoCaptcha , classe que implementa a API 2Captcha para a resolução de captchas.
    self.tecla = instância do objeto Keys, contém métodos que simulam as teclas do teclado.
    self.metodo = inatância do objeto By, contém métodos que representam metodos de busca por elementos web
        (e.g., By.XPATH, By.ID, etc)
    """
    def __init__(self, driver, wait_timeout=10):
        self.chrome_driver = driver
        self.driver = driver
        self.act = SeleniumActions(self.chrome_driver, time_out=wait_timeout)
        self.sh = SeleniumHelper(self.chrome_driver)
        self.captcha = TwoCaptcha(self.chrome_driver)
        self.tecla = Keys
        self.metodo = By    # em desuso.
        self.parar_se_exception = True
        self.locs = dict()
        self.by = By  # substituir self.metodo
        self.inferir = SeleniumActions.inferir_metodo_seletor

    def executar_script(self, script, wait=1):
        self.chrome_driver.execute_script(script)
        sleep(wait)

    @staticmethod
    def act_factory(driver):
        return SeleniumActions(driver)

    @staticmethod
    def auto_gui_error_log(message, filename):
        gen_log(message, f'auto_gui_{filename}')
        traceback.print_exc(file=open(f'auto_gui_{filename}.log', 'a'))

    @staticmethod
    def auto_process_log(message, filename, modo='print'):
        if modo == 'print' or modo == 'ambos':
            print(message)
        if modo == 'log' or modo == 'ambos':
            gen_log(message, filename)
