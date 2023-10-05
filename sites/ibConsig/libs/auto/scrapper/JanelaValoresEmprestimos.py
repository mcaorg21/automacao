from typing import Dict, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from sites.elementos.ContainerElements.Row import CelulaTabela
from sites.ibConsig.libs.exceptions.Exceptions import NotFoundResultException


class JanelaValoresEmprestimos:

    seletor = '//*[@id="tableSimulacaoIdeal"]/tbody/tr[{row}]/td[{col}]'

    def __init__(self, driver: Chrome):
        self.colPrazos = CelulaTabela(driver, seletor=self.seletor, time_out=0.5)
        self.colValor = CelulaTabela(driver, seletor=self.seletor, time_out=0.5)
        self.colStatus = CelulaTabela(driver,  seletor=self.seletor+"/input", time_out=0.5)
        self.tabelaValores: Dict[str, List[str]] = {"prazo": [], "valor": [], "status": []}
        self.janelas: list = []
        self.driver: Chrome = driver

    def irParaJanela(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def voltarJanelaPrincipal(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.switch_to.frame(self.driver.find_element_by_name("rightFrame"))

    def extrairTabela(self):

        for linha in range(2, 60):
            try:
                self.colPrazos.carregarCelula(linha, coluna=1)
                self.colValor.carregarCelula(linha, coluna=2)
                self.colStatus.carregarCelula(linha, coluna=3)

            except TimeoutException:
                return

            self.tabelaValores["prazo"].append(self.colPrazos.extrair_texto())
            self.tabelaValores["valor"].append(self.colValor.extrair_texto())
            self.tabelaValores["status"].append(self.colStatus.act.get_attribute("src"))

    def buscarLinhaPorPrazo(self, prazo) -> Dict[str, str]:
        
        try:
            idx: int = (self.tabelaValores["prazo"].index(prazo))
        except:
            return False    

        if idx == -1:
            raise NotFoundResultException(
                f"Erro encontrado: Valor relativo ao prazo não encontrado na tabela de simulação.")

        return {"prazo": self.tabelaValores["prazo"][idx],
                "valor": self.tabelaValores["valor"][idx],
                "status": self.tabelaValores["status"][idx]}


