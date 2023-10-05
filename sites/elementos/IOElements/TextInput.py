from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.elementos.BaseElement import BaseElement, Chrome


class TextInput(BaseElement):
    def __init__(self, driver: Chrome, seletor: str, label: str="Input=text", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.value: str = ""

    def carregar_elemento(self):
        loc = self.metodo, self.seletor

        self._elemento: WebElement = WebDriverWait(self._driver, self.time_out).until(
            EC.element_to_be_clickable(loc), message=self.msg)

        self.value = self.elemento.get_attribute("value")

    def enviar_texto(self, texto: str, clear: bool=True):
        if clear:
            self.elemento.clear()
        self.elemento.send_keys(texto)

    def has_hidden_type(self) -> bool:
        input_type: str = self._elemento.get_attribute("type")
        if input_type is None:
            return False
        print("Input Type", input_type)

        return input_type == "hidden"

    def enviar_caracteres(self, string: str, delay: float=0.5, clear: bool=True):
        if clear:
            self.elemento.clear()
        for char in string:
            sleep(delay)
            self.elemento.send_keys(char)

    def apagar_caracteres(self, n_chars: int, delay=0.5, **kwargs):
        HOME: bool = kwargs.get("HOME", False)
        END: bool = kwargs.get("END", False)

        if HOME:
            self.elemento.send_keys(Keys.HOME)
        elif END:
            self.elemento.send_keys(Keys.END)

        for _ in range(n_chars):
            sleep(delay)
            self.elemento.send_keys(Keys.BACKSPACE)

    def esta_vazio(self) -> bool:
        return not self.elemento.get_attribute("value")
