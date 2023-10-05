from typing import Tuple, List

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from sites.elementos.ContainerElements.ElementoTabela import ElementoTabela
from sites.elementos.BaseElement import BaseElement, Chrome
from selenium.webdriver.support import expected_conditions as EC


class Tabela(BaseElement):

    seletor: str = ""

    def __init__(self, driver: Chrome, seletores_colunas: Tuple[str], time_out: float=5):
        super().__init__(driver, "")
        self.seletores_colunas: List[str] = []
        self.__length: int = 0
        self.__tabela: List[List[ElementoTabela]] = []

    def linha(self, idx: int) -> List[ElementoTabela]:
        return self.__tabela[idx]

    def elemento_tabela(self, linha: int, coluna: int) -> ElementoTabela:
        return self.__tabela[linha][coluna]

    def carregar_linhas(self):
        linhas: List[List[ElementoTabela]] = []

        for sel in self.seletores_colunas:
            list_elementos: List[ElementoTabela] = []

            for elemento in self.retornar_lista_elementos((self.metodo, sel)):
                list_elementos.append(ElementoTabela(self._driver, elemento, label=sel))

            linhas.append(list_elementos)
        self.__tabela = zip(*linhas)

    def retornar_lista_elementos(self, loc: Tuple[str, str]) -> List[WebElement]:
        return WebDriverWait(self._driver, self.time_out).until(
            EC.visibility_of_all_elements_located(loc))

    def __repr__(self):
        linha_str = "Tabela:\n"
        for linha in self.__tabela:
            linha_str += f"{linha}\n"
        return linha_str
