from selenium.webdriver.remote.webelement import WebElement

from sites.elementos.BaseElement import BaseElement, Chrome

class ElementoTabela(BaseElement):

    seletor: str = ""

    def __init__(self, driver: Chrome, elemento: WebElement, label: str="LinhaTabela", time_out: float=5):
        super().__init__(driver, "", label, time_out)
        self.texto: str = ""
        self._elemento: WebElement = elemento

    def extrair_texto(self):
        self.texto = self._elemento.text
