from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from sites.baseRobos.core.helpers import formatar_moeda
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.DebugTools import DebugTools
debug = DebugTools(debugging=False)


class TabelaConsultaMargem(AutoGUI):
    def __init__(self, driver: Chrome, solicitacao: dict):
        super().__init__(driver, 5)
        self.__nome: str = ''
        self.__orgao: str = ''
        self.__identificacao: str = ''
        self.__mes_ref: str = ''
        self.__cod_op: str = '250'  # campo 'espécie'
        self.__matricula: str = solicitacao.get('matricula', None)
        self.__margem: str = ''
        self.__margem_cartao: str = ''
        self.solicitacao = solicitacao

    @property
    def quantidade_provimentos(self) -> float:
        loc = '//span[contains(text(), "Provimento")]'
        qtd: int = self.act.quantidade_elemento(loc, self.by.XPATH)
        return qtd/2

    def extrair_nome(self):
        print("Extraindo nome: ", end='')
        loc = '//*[text()="Nome - "]'
        nome_bruto: str = self.act.obter_texto(loc, self.by.XPATH)

        self.__nome = nome_bruto.split(' - ')[1]
        print(self.__nome)

    def extrair_orgao(self):
        print("Extraindo orgao: ", end='')
        loc = '//*[text()="Órgão - "]'
        orgao_bruto: str = self.act.obter_texto(loc, self.by.XPATH)

        self.__orgao = orgao_bruto.split(' - ')[1]
        print(self.__orgao)

    def extrair_identificacao(self):
        print("Extraindo identificação:", end=' ')
        loc = '//*[text()="Identificação - "]'

        id_bruto: str = self.act.obter_texto(loc, self.by.XPATH)

        self.__identificacao = id_bruto.split(' - ')[1]
        print(self.__identificacao)

    def extrair_mes_referencia(self):
        print("Extraindo mês de referência: ", end='')
        loc = '//*[text()="Mês de Referência da Margem - "]'

        mes_bruto: str = self.act.obter_texto(loc, self.by.XPATH)

        self.__mes_ref = mes_bruto.split(' - ')[1]
        print(self.__mes_ref)

    def extrair_margem_consignavel(self):
        print("Extraindo margem:", end=' ')
        loc = (
            '//*[@id="painelMargensDisponiveis"]'
            '//div[@class="blocoDados itemVisivel"]'
            '/div/div/span/div/table/tbody/tr[1]/td[2]'
        )
        self.__margem = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__margem)

    def extrair_margem_consignavel_orgao(self):
        print("Extraindo margem:", end=' ')
        loc_1 = 'labelOrgao48'
        self.nome_orgao_primeiro = self.act.obter_texto(loc, self.by.XPATH)
        loc_2 = 'labelOrgao62'
        self.nome_orgao_segundo= self.act.obter_texto(loc, self.by.XPATH)
        
        if(self.__orgao):
            print(self.__margem)

    def switch_demo(id_orgao):
        switcher = {
            63: "SEFAZ",
            67: "PMESP",
            80: "SPPREV"
        }
        return switcher.get(argument, "Invalid month")
        
        

    def extrair_margem_cartao(self):
        print("Extraindo margem cartão:", end=' ')
        loc = (
            '//*[@id="painelMargensDisponiveis"]'
            '//div[@class="blocoDados itemVisivel"]'
            '/div/div/span/div/table/tbody/tr[2]/td[2]'
        )
        self.__margem_cartao = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__margem_cartao)

    def extrair_margem_averbacao(self):
        print("Extraindo margem reservada:", end=' ')
        debug.debugger()
        loc = '//*[@id="divTbMargem"]/table/tbody/tr[2]/td[2]/span'
        try:
            self.__margem = self.act.obter_texto(loc, self.by.XPATH)
        except TimeoutException:
            loc = '//*[@id="divTbMargemSProv"]/table/tbody/tr[2]/td[1]/span'
            self.__margem = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__margem)

    def atualizar_margem_solicitacao(self):
        self.solicitacao['margem'] = formatar_moeda(self.__margem)
