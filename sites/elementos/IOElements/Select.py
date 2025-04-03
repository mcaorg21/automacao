try:
    from collections import Callable
except:
    # Python 3
    from collections.abc import Callable

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import select as sel
from selenium.webdriver.support.wait import WebDriverWait
from typing import List

from sites.elementos.BaseElement import BaseElement, Chrome
from selenium.webdriver.support import expected_conditions as EC


class Select(BaseElement):

    seletor: str = ""

    def __init__(self, driver: Chrome, seletor: str, label: str="Select", time_out: float=5):
        super().__init__(driver, seletor, label, time_out)
        self.texto: str = ""
        self._elemento: sel.Select = None
        self.seletor = seletor

    def carregar_elemento(self):
        loc = self.metodo, self.seletor
        self._elemento: sel.Select = sel.Select(WebDriverWait(self._driver, self.time_out).until(
            EC.element_to_be_clickable(loc), message=self.msg))

    def selecionar_opcao(self, value, select_by=""):
        switch: Callable = {
            "text": self._elemento.select_by_visible_text,
            "index": self._elemento.select_by_index,
            "value": self._elemento.select_by_value
        }.get(select_by, self._elemento.select_by_value)

        switch(value)

    def estaSelecionado(self, value: str):
        if self._elemento.first_selected_option == value:
            return True
        return False

    @property
    def listaOpcoes(self) -> List[WebElement]:
        return self._elemento.options

    def esta_presente(self) -> bool:
        try:
            self.carregar_elemento()
            return True
        except:
            return False

