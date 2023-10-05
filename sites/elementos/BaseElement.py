from typing import Union, Callable, List
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from sites.baseRobos.core.data_helpers import make_request
from selenium.webdriver.remote.webelement import WebElement
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from logging import warning


class BaseElement:
    def __init__(self, driver: Chrome, seletor: str, label: str="", time_out: float=10.0):
        self._driver: Chrome = driver
        self._seletor: str = seletor
        self.time_out = time_out
        self._elemento: Union[WebElement, None] = None
        self.metodo: str = self.inferir_metodo_seletor(self._seletor)
        self.action_chain = ActionChains(driver)
        self.label = label
        self.msg: str = f"Não foi possível encontrar o elemento: {self.seletor}"

    @property
    def driver(self):
        return self._driver

    @property
    def elemento(self):
        return self._elemento

    @property
    def act(self):
        if not self._elemento:
            warning("Elemento nulo")
            return None
        return self._elemento

    @property
    def seletor(self):
        return self._seletor

    @seletor.setter
    def seletor(self, val: str):
        self._seletor = val

    def press_ENTER(self):
        self._elemento.send_keys(Keys.ENTER)

    def press_TAB(self):
        self._elemento.send_keys(Keys.TAB)

    def ctrl_c(self):
        self._elemento.key_down(Keys.CONTROL).send_keys('C').key_up(Keys.CONTROL).perform()

    def ctrl_v(self):
        self._elemento.key_down(Keys.CONTROL).send_keys('V').key_up(Keys.CONTROL).perform()

    def executar_cadeia(self, cadeia:List[Callable], delay=0):
        for acao in cadeia:
            if delay:
                sleep(delay)
            acao()

    def disabled(self) -> bool:
        if self._elemento.get_attribute("disabled") is not None:
            return True
        if self._elemento.get_attribute("aria-disabled") is not None:
            return True
        if not self._elemento.is_enabled():
            return True

        return False

    @staticmethod
    def elemento_esta_presente(driver:Chrome, seletor: str, timeout:float=4.0) -> bool:
        loc = BaseElement.inferir_metodo_seletor(seletor), seletor
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(loc), message="Elemento não encontrado")
            print(f"Elemento {seletor} encontrado")
            return True
        except TimeoutException as e:
            print(e)
            return False

    @staticmethod
    def inferir_metodo_seletor(seletor: str) -> str:
        import re

        if re.match(r"/{2}\w+|/{2}\*", seletor):
            return By.XPATH
        elif re.match(r"\**\w*\[\w*=[\'|\"]\w+.*|\w*[#|.]\w+\.*\w*", seletor):
            return By.CSS_SELECTOR

    def __repr__(self):
        return f"WebElement[{self.label}]"

