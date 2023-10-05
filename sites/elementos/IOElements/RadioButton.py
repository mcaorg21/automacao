from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.elementos.BaseElement import BaseElement, Chrome


class RadioButton(BaseElement):
    def __init__(self, driver: Chrome, seletor: str, label: str="CheckBox", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.value: str = ""

    def carregar_elemento(self):
        loc = self.metodo, self.seletor

        self._elemento: WebElement = WebDriverWait(self._driver, self.time_out).until(
            EC.element_to_be_clickable(loc), message=self.msg)


