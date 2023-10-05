from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.elementos.BaseElement import BaseElement, Chrome


class Button(BaseElement):

    def __init__(self, driver: Chrome, seletor: str="", label: str="", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.value: str = ""
        self.text: str = ""
        self.is_enabled: bool = True

    def carregar_elemento(self):
        loc = self.metodo, self.seletor
        self._elemento: WebElement = WebDriverWait(self._driver, self.time_out).until(
            EC.element_to_be_clickable(loc), message=self.msg)

    def hover_e_clique(self, pause: float=0.5):
        self.action_chain.move_to_element(self.elemento)
        self.action_chain.pause(pause).click().perform()
