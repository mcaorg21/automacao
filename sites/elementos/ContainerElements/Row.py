from selenium.webdriver.common import alert
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.elementos.BaseElement import BaseElement, Chrome


class CelulaTabela(BaseElement):
    seletor: str = ""

    def __init__(self, driver: Chrome, seletor: str,  time_out: float = 5):
        super().__init__(driver=driver, seletor=seletor, label="", time_out=time_out)
        self.texto: str = ""
        self._elemento: alert.Alert = None
        self.linha: int = 0
        self.coluna: int = 0
        self.seletorLinha = ""
        self.seletor = seletor

    def carregar_elemento(self):
        loc = self.metodo, self.seletorLinha
        self._elemento: WebElement = WebDriverWait(self._driver, self.time_out).until(
            EC.presence_of_element_located(loc), message=self.msg)

    def extrair_texto(self) -> str:
        self.texto = self._elemento.text
        return self.texto

    def carregarCelula(self, linha, coluna):
        self.seletorLinha = (self.seletor
                             .replace("{row}", str(linha))
                             .replace("{col}", str(coluna)))
        self.carregar_elemento()
