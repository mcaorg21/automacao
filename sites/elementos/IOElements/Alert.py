from selenium.webdriver.common import alert
from selenium.webdriver.support.wait import WebDriverWait

from sites.elementos.BaseElement import BaseElement, Chrome
from selenium.webdriver.support import expected_conditions as EC


class Alert(BaseElement):

    seletor: str = ""

    def __init__(self, driver: Chrome, seletor: str, label: str="Alert", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.texto: str = ""
        self._elemento: alert.Alert = None

    def carregar_elemento(self, raise_timeout=True):
        WebDriverWait(self._driver, self.time_out).until(EC.alert_is_present())
        self._elemento: alert.Alert = alert.Alert(self._driver)

        self.texto = self.elemento.text

    def enviar_texto(self, texto: str, clear: bool=True):
        if clear:
            self.elemento.clear()
        self.elemento.send_keys(texto)

    def esta_presente(self) -> bool:
        try:
            WebDriverWait(self._driver, self.time_out).until(
                EC.alert_is_present())
            return True
        except:
            return False

    def esta_vazio(self) -> bool:
        return not self.elemento.text
