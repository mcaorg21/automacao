from sites.baseRobos.gui_auto import AutoGUI
from sites.baseRobos.core.data_helpers import similaridade
from selenium.webdriver import Chrome

from sites.ibConsig.libs.exceptions.Exceptions import NotFoundResultException, PularCheckboxException
from sites.baseRobos.core.DebugTools import DebugTools
from time import sleep

import re,pdb

dbg = DebugTools(debugging=False)


class TabelaRefinanciamentos(AutoGUI):
    """
    As linhas da tabela contendo dados dos refinanciamentos iniciam
    em tr[3]. Logo, sempre que se utilizar iterações com índices
    iniciando em zero, encontra-se a primeira linha com a operação:

        linha-i = i + 3

    Lembrando que as linhas das tabelas (td[n]) começam sempre com
    n = 1, nao n = 0.
    """
    def __init__(self, driver: Chrome, contrato: dict):
        super().__init__(driver, wait_timeout=2)
        self.__parcela: str = contrato.get('valorParcela')
        self.__parcela_refin_margem: str = contrato.get('valorParcelaRefinMargem')
        self.__matricula: str = contrato.get('matricula')
        self.loc_tab = ""
        self.linha: int = 0
        self.__n_refins: int = 0
        self.refinanciamento_selecionado: bool = False
        self.wait = 0.7

    @property
    def ultima_linha(self):
        return self.__n_refins == (self.linha - 2)

    @property
    def total_refinanciamentos(self):
        return self.__n_refins

    @property
    def esta_presente(self) -> bool:
        loc = '//*[@id="contratosPassiveisDeRefinanciamento"]'
        presente: bool = self.act.esta_presente(loc)
        print("Tabela Refin Presente", presente)
        return presente

    def set_linha_tabela(self, idx: int):
        self.linha = idx + 3
        self.loc_tab = f'//*[@id="contratosPassiveisDeRefinanciamento"]/tbody/tr[{self.linha}]'

    def extrair_quantidade_refins(self):
        loc = '[type=checkbox]'
        self.__n_refins = self.act.quantidade_elemento(loc)
        print("Quantidade de refinanciamentos:", self.__n_refins)

    def encontrar_matricula_refinanciamento(self, modo_simulacao = False):
        dbg.debugger()
        sleep(self.wait)
        loc = self.loc_tab + '/td[2]'  # coluna 2 = matricula
        matricula_tabela = self.act.obter_texto(loc, self.by.XPATH)

        print(f"Matricula Contrato: {self.__matricula}."
              f" Matricula Tabela: {matricula_tabela}")

        nao_encontrada = similaridade(self.__matricula, matricula_tabela) < 50
        
        if nao_encontrada and self.ultima_linha:
            if(modo_simulacao == True):
                return False
            raise NotFoundResultException("Matricula não encontrada")

        if nao_encontrada:
            if(modo_simulacao == True):
                return False
            raise PularCheckboxException("Matricula não encontrada")

        if(modo_simulacao == True):
            return True


    def encontrar_matricula_refinanciamento_somando_margem(self):
        dbg.debugger()
        sleep(self.wait)
        loc = self.loc_tab + '/td[2]'  # coluna 2 = matricula
        matricula_tabela = self.act.obter_texto(loc, self.by.XPATH)

        print(f"Matricula Contrato: {self.__matricula}."
              f" Matricula Tabela: {matricula_tabela}")

        nao_encontrada = similaridade(self.__matricula, matricula_tabela) < 75

        if nao_encontrada and self.ultima_linha:
            return False

        if nao_encontrada:
            return False

        return True

    def extrair_parcela(self) -> str:
        loc = self.loc_tab + '/td[9]'  # coluna 9 = parcela
        print("Extraindo valor da parcela: ", end='')
        val = self.act.obter_texto(loc, self.by.XPATH)
        print(val)
        return val.replace(".", ",")

    def encontrar_parcela_refinanciamento(self, refin_somando_margem = False):
        sleep(self.wait)
        loc = self.loc_tab + '/td[9]'  # coluna 9 = valor da parcela
        parcela_tabela = self.act.obter_texto(loc, self.by.XPATH)

        if(refin_somando_margem):
            parcela_con_formatada = self.__parcela_refin_margem
        else:
            parcela_con_formatada = self.__parcela.replace('.', '')

        parcela_tabela_formatada = parcela_tabela.replace(".", ",")

        print(f"Parcela Contrato: {parcela_con_formatada}."
              f" Parcela Tabela: {parcela_tabela}")

        nao_encontrada = parcela_con_formatada != parcela_tabela_formatada

        if nao_encontrada and self.ultima_linha:
            raise NotFoundResultException("Parcela não encontrada")

        if nao_encontrada:
            raise PularCheckboxException("Parcela não encontrada")

    def retornar_parcela_refinanciamento(self):
        sleep(self.wait)
        loc = self.loc_tab + '/td[9]'  # coluna 9 = valor da parcela
        parcela_tabela = self.act.obter_texto(loc, self.by.XPATH)

        return parcela_tabela

    def selecionar_refinanciamento(self):
        print("Selecionar refinanciamento")
        loc = self.loc_tab + '/td[13]/input'  # coluna 13 = check box

        check_box_habilitado = self.act.check_box_is_enabled(loc, self.by.XPATH)

        if not check_box_habilitado and self.ultima_linha:
            raise NotFoundResultException("Matricula não encontrada")

        if not check_box_habilitado:
            raise PularCheckboxException("Checkbox disabled")

        self.act.hover_e_clique(loc, self.by.XPATH, pause=0.1)
        self.refinanciamento_selecionado = True

    def confirmar_selecao(self):
        print("Confirmando seleção do refinanciamento")
        loc = '#submitButton'
        self.act.hover_e_clique(loc)
