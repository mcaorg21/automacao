from sites.baseRobos.gui_auto import AutoGUI
from sites.baseRobos.core import data_helpers as dh
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from time import sleep


class FormDadosBuscaMargem(AutoGUI):
    def __init__(self, driver: Chrome, **kwargs):
        super().__init__(driver, 2)
        self.__cpf: str = kwargs.get('cpf', None)
        self.__orgao: str = kwargs.get('con_idOrgao', None)
        self.__cod_op: str = '250'  # campo 'espécie'
        self.__matricula: str = kwargs.get('matricula', None)
        self.__consulta_prov_especifico = False
        self.wait: float = 0.6

    @property
    def provimento_especifico(self):
        return self.__consulta_prov_especifico

    @provimento_especifico.setter
    def provimento_especifico(self, status: bool):
        self.__consulta_prov_especifico = status

    def expandir_menu_consulta_margem(self, rec=0):
        print("Expandindo menu para consulta da margem.")
        loc = '//*[@id="menu"]/div[2]/a'
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except TimeoutException:
            if rec > 4:
                raise TimeoutException
            sleep(1)
            return self.expandir_menu_consulta_margem(rec + 1)

    def clicar_link_consulta_margem(self):
        print("Clicando link consulta margem.")
        loc = '[href="/consignatario/pesquisarMargem"]'

        self.act.hover_e_clique(loc)

    def expandir_menu_consigs_facultativas(self):
        print("Expandindo menu para consigs facultativas.")
        loc = '//*[@id="menu"]/div[3]/a'

        self.act.hover_e_clique(loc, self.by.XPATH)

    def clicar_link_reserva_averbacao(self):
        print("Clicando link reserva averbação.")
        loc = '[href="/consignatario/reserva"]'

        self.act.hover_e_clique(loc)

    def preencher_cpf_consulta_margem(self):
        print("Preenchendo CPF para consultar margem:", self.__cpf)
        loc_cpf_input = 'input#cpfServidor'
        self.act.clicar_elemento(loc_cpf_input)
        self.act.enviar_texto_intervalado(
            loc_cpf_input, self.__cpf,
            clear=False, delay=0.03
        )

    def confirmar_consulta_margem(self):
        print("Clicando em consultar margem.")
        loc_botao_pesquisar = 'input[name="botaoPesquisar"]'
        self.act.clicar_elemento(loc_botao_pesquisar)

    def selecionar_orgao_consulta_averbacao(self):
        print("Selecionando orgao para consulta averbação.")
        loc = '[id="selectOrgaoServidor"]'

        val_select_orgao: str

        if self.__orgao == 67:          # PMESP
            val_select_orgao = '148'

        elif self.__orgao == 80:        # SPPREV
            val_select_orgao = '149'

        else:                           # SEFAZ
            val_select_orgao = '102'

        self.act.select_drop_down(loc, val_select_orgao)

    def selecionar_tipo_operacao_consulta_averbacao(self):
        print("Selecionando o tipo de operação", self.__cod_op)
        loc = '[id="selectEspecie"]'

        self.act.select_drop_down(loc, self.__cod_op)

    def preencher_cpf_consulta_averbacao(self):
        loc = 'input#cpf'
        print("Preenchendo CPF para consultar averbacao:", self.__cpf)

        self.act.clicar_elemento(loc)
        self.act.enviar_texto_intervalado(
            loc, self.__cpf, clear=False, delay=0.1
        )

    def preencher_matricula_consulta_averbacao(self):
        print("Preenchendo matricula para consulta averbação:", self.__matricula)
        loc = 'input#inputIdentificacao'
        self.act.clicar_elemento(loc)
        self.act.enviar_texto_intervalado(
            loc, self.__matricula, clear=False, delay=0.1
        )
        self.act.press_TAB(loc)

    def clicar_continuar_consulta_averbacao(self):
        print("Clicando em continuar consulta.")
        loc = '[value="Continuar"]'
        self.act.hover_e_clique(loc)

    def verificar_erro_consulta(self):
        loc = 'span[class="feedbackerror"]'
        erro: str

        sleep(self.wait)
        try:
            erro = self.act.obter_texto(loc)
            raise FalhaConsultaException(erro)
        except TimeoutException:
            return ''

    def verificar_retorno_incial_consulta(self):
        sleep(3)
        try:
            erro = self.driver.execute_script("""return $('.feedbackPanel').text().trim()""")
            if erro != '':
                raise FalhaConsultaException(erro)
        except TimeoutException:
            return ''


class FalhaConsultaException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message
