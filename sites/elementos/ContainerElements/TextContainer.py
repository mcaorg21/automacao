from selenium.webdriver.common import alert
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.elementos.BaseElement import BaseElement, Chrome


class TextContainer(BaseElement):

    seletor: str = ""

    def __init__(self, driver: Chrome, seletor: str, label: str="TextDisplay", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.texto: str = ""
        self._elemento: alert.Alert = None

    def carregar_elemento(self):
        loc = self.metodo, self.seletor
        self._elemento: WebElement = WebDriverWait(self._driver, self.time_out).until(
            EC.presence_of_element_located(loc), message=self.msg)

    def extrair_texto(self):
        self.texto = self._elemento.text
