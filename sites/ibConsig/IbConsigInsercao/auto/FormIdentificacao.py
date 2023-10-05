from sites.baseRobos.core.data_helpers import get_select_options_values, strip_zero_left
from sites.ibConsig.IbConsigInsercao.data.IbConsigData import IbConsigData
from sites.baseRobos.gui_auto import AutoGUI
from sites.baseRobos.core.captcha import FalhaScreenShotCaptcha
from selenium.webdriver import Chrome
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException,
    InvalidElementStateException
)
from time import sleep
from sites.baseRobos.core.DebugTools import DebugTools
dbg = DebugTools(debugging=False)

from sites.ibConsig.libs.exceptions.Exceptions import PreenchimentoException

from sites.baseRobos.core.data_helpers import similaridade

import pdb


class DadosIdentificacao(AutoGUI):

    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver, wait_timeout=2)
        self.__codigo_con = dados.get('codigo_con')
        self.__entidade = dados.get('entidade', None)
        self.__codigo_entidade = dados.get('codigoEntidade', None)
        self.__cpf = dados.get('cpf', None)
        self.__data_nasc = dados.get('dataNascimento', None)
        self.__matricula = dados.get('matricula')
        self.campo_data_nasc: str = ""
        self.id_captcha: int = 0
        self.resposta_captcha: str = ""
        self.__codigo_orgao: str = ""
        self.__codigo_situacao: str = "1"
        self.__tipo: str = dados.get('tipo', "")
        self.consulta_refin: bool = False

    @property
    def nova_proposta(self):
        return "novo" in self.__tipo.lower()
    
    @property
    def refinanciamento(self):
        return ("refinanciamento" in self.__tipo.lower() or
                self.consulta_refin)
    @property
    def nova_proposta_margem(self):
        return "complementar" in self.__tipo.lower()

    @property
    def aposentado_pensionista_inss(self):
        return '1581' in self.__entidade

    @property
    def servidor_federal(self):
        return '164' in self.__entidade

    @property
    def servidor_sao_paulo(self):
        pmesp = '4193' in self.__entidade
        spprev = '4194' in self.__entidade
        sefaz = '4195' in self.__entidade

        return pmesp or spprev or sefaz

    @property
    def servidor_mt(self):
        print(self.__entidade)
        return '243' in self.__entidade

    @property
    def data_nascimento_preenchida(self):
        return self.campo_data_nasc

    @property
    def campo_entidade_preenchido(self) -> bool:
        loc = '//*[@id="identificacao-form:estabelecimento:find:txt-value"]'
        val = self.act.obter_valor(loc, self.by.XPATH)
        if val:
            return True
        else:
            return False

    def abrir_menu_proposta(self):
        loc_link = '//*[@id="slidingMenu"]/div/div[1]/a[2]'
        if self.act.esta_presente(loc_link, self.by.XPATH):
            return
        loc = '#top'
        self.act.clicar_elemento(loc)

    def link_nova_proposta(self, rec=0):
        print("Selecionando Nova Proposta")
        loc = '//*[@id="slidingMenu"]/div/div[1]/a[1]'
        try:
            self.act.clicar_elemento(loc, self.by.XPATH)
        except TimeoutException:
            if rec >= 5:
                raise TimeoutException
            sleep(1)
            return self.link_nova_proposta(rec+1)

    def link_refinanciamento(self):
        print("Selecionando Refinanciamento")
        loc = '//*[@id="slidingMenu"]/div/div[1]/a[2]'
        self.act.clicar_elemento(loc, self.by.XPATH)

    def selecionar_servico(self, valor):
        print("Selecionando Servico")
        loc = '//*[@id="identificacao-form:servico"]'
        self.act.select_drop_down(loc, valor, self.by.XPATH)

    def preencher_entidade(self, rec=0) -> int:
        loc: str = ""
        if self.nova_proposta or self.__tipo == 'ANTECIPAÇÃO FGTS':
            loc = '//*[@id="identificacao-form:orgao:find:txt-value"]'
        if self.refinanciamento:
            loc = '//*[@id="identificacao-form:estabelecimento:find:txt-value"]'

        print("Entidade", self.__entidade)
        if rec >= 5:
            return 0
        try:
            self.act.clicar_elemento(loc, self.by.XPATH)
            self.act.enviar_texto(loc, self.__entidade, metodo=self.by.XPATH, clear=False)
            self.act.press_TAB(loc, self.by.XPATH)
            return 1
        except StaleElementReferenceException as e:
            print(e.msg)
            sleep(1)
            return self.preencher_entidade(rec+1)
        except InvalidElementStateException as e:
            print(e.msg)
            sleep(1)
            return self.preencher_entidade(rec+1)

    def aguardar_carregar_entidade(self) -> bool:
        """//*[@id="identificacao-form:estabelecimento:find:message"]/span
        Entidade não relacionada para a loja."""
        print("Aguardando carregar nome entidade")

        loc = ('//*[@id="identificacao-form:'
               'estabelecimento:find:txt-label"]')

        for i in range(30):
            entidade = False
            try:
                entidade = self.act.obter_valor(loc, self.by.XPATH)
            except StaleElementReferenceException:
                print("StaleElement")
            if entidade:
                print("\nCarregado.")
                return True

            print("\rAguardando...", end="")
            sleep(1.5)

        raise Exception("Erro ao carregar entidade")

    def verificar_convenio_ativo(self) -> bool:
        print("Verificando se convênio está ativo")
        situacao = True
        loc_entidade = '//*[@id="identificacao-form:estabelecimento:find:txt-value"]'
        entidade = self.act.obter_valor(loc_entidade, self.by.XPATH)
        try:
            texto = self.act.obter_texto('//*[@id="identificacao-form:estabelecimento:find:message"]', self.by.XPATH)
        except:
            texto = ''
            pass
        if('Entidade não relacionada para a loja' in texto):
            situacao = False

        return situacao
        

    def carregar_dados_servidor_federal(self):
        """
        :raises DadosServidorFederalInvalidos:
        """
        dados_servidor: dict = IbConsigData().api_transparencia_serv_federais_get(
            self.__cpf.replace('.', '').replace('-', ''),
            codigo_con=self.__codigo_con
        )

        self.__codigo_orgao = dados_servidor['codigo_orgao']
        self.__codigo_situacao = dados_servidor['codigo_situacao']
        print(
            f"Dados codigo_orgao ({self.__codigo_orgao}) e "
            f"codigo_situacao({self.__codigo_situacao}) carregados com sucesso."
        )

        if len(self.__matricula) > 7:
            matricula_remover = len(self.__matricula) - 7
            self.__matricula = self.__matricula[matricula_remover:]

    def carregar_dados_orgao_servidor_federal_web_admin(self):
        self.__codigo_orgao = self.__codigo_entidade
        print(
            f"Dados codigo_orgao ({self.__codigo_orgao})"
        )

    def carregar_dados_servidor_estadual_mt(self):
        self.__codigo_orgao = self.__codigo_entidade
        print(
            f"Dados codigo_orgao ({self.__codigo_orgao})"
        )

    def carregar_dados_servidor_estadual_sp(self):

        if(self.__entidade in ['4193','4194','4195','4195-1']):
            print('Entrou')
            self.__codigo_orgao = self.__entidade
        else:
            self.__codigo_orgao = self.__codigo_entidade
        print(
            f"Dados codigo_orgao ({self.__codigo_orgao})"
        )

    def valida_entidade(self):
        if(self.__codigo_entidade == '0' and self.__entidade == ''):
            raise PreenchimentoException('Favor aprovar o contracheque e registrar o codigo de entidade de acordo com o IbConsig')


    def clicar_botao_pesquisar_orgao(self):
        print("Clicando lupa buscar orgao do servidor")
        loc_pesquisa = '//*[@id="identificacao-form:orgao:find:lnk"]'
        self.act.clicar_elemento(loc_pesquisa, self.by.XPATH)

    def preencher_campo_pesquisa_orgao_direto(self):
        print("Preenchendo campo de pesquisa do orgao:", self.__codigo_orgao)
        loc = '//*[@id="identificacao-form:orgao:find:txt-value"]'
        self.act.clicar_elemento(loc, self.by.XPATH)
        self.act.enviar_caracteres(loc, self.__codigo_orgao,metodo=self.by.XPATH, delay=0.1, clear=False)
        sleep(2)
        self.act.press_TAB(loc, self.by.XPATH)

    def preencher_campo_pesquisa_orgao(self):
        print("Preenchendo campo orgao:", self.__codigo_orgao)
        loc = ('//*[@id="identificacao-form:orgao:find:'
               'filter-group"]/tbody/tr[1]/td[2]/input')
        self.act.enviar_caracteres(
            loc, self.__codigo_orgao,
            metodo=self.by.XPATH, delay=0.1, clear=False
        )

    def confirmar_pesquisa_orgao(self):
        print("Pesquisando pelo orgao:", self.__codigo_orgao)
        loc_botao_pesquisa = '//a[@id="identificacao-form:orgao:find:btPesq"]'
        self.act.clicar_elemento(loc_botao_pesquisa, self.by.XPATH)

    def clicar_botao_finalizar_pesquisa(self):
        print("Finalizando pesquisa...")
        loc_botao_ok = 'img[src="/img/icones/ok.gif"]'
        self.act.clicar_elemento(loc_botao_ok)

    def selecionar_situcao_servidor(self, consulta_refin=False, situacao = '1'):
        print("Selecionando situaçao servidor")
        loc= '//*[@id="identificacao-form:situacaoDoServidor"]'

        if consulta_refin:
            self.act.select_drop_down(loc, situacao, metodo=self.by.XPATH)
            return

        if situacao != '1':
            self.act.select_drop_down(loc, situacao, metodo=self.by.XPATH)
            return

        print("Situação do servidor:", self.__codigo_situacao)

        select_key_values = get_select_options_values(loc, self.act, method=self.by.XPATH)
        codigo_situacao_strip = strip_zero_left(self.__codigo_situacao)

        for key, val in select_key_values.items():
            if key == 'Selecione':
                continue
            key_code = key.split('-')[0].strip()
            key_nome = key.split('-')[1].strip()

            if ((codigo_situacao_strip in key_nome and
                 len(codigo_situacao_strip) == len(key_code)) or
                    (codigo_situacao_strip.upper() in key_code) or
                    (codigo_situacao_strip.upper() in key_nome)):
                self.act.select_drop_down(loc, val, metodo=self.by.XPATH)
                return

    def preencher_data_nascimento(self):
        self.sh.atribuir_valor_campo_jquery(
            "#identificacao-form\\\\:dataDeNascimento",
            self.__data_nasc
        )

    def verificar_data_nascimento(self):
        self.campo_data_nasc = self.sh.verificar_valor_campo_jquery(
            "#identificacao-form\\\\:dataDeNascimento")

    def preencher_cpf(self, rec=0):
        print("Preenchendo CPF", self.__cpf)
        loc = 'input[name="identificacao-form:cpf"]'
        if rec >= 5:
            return 0
        try:
            self.act.clicar_elemento(loc)
            self.act.enviar_texto(
                loc, self.__cpf, clear=False)
            self.act.press_TAB(loc)
            return 1
        except StaleElementReferenceException as e:
            print(e.msg)
            sleep(1)
            return self.preencher_cpf(rec+1)
        except InvalidElementStateException as e:
            print(e.msg)
            sleep(1)
            return self.preencher_cpf(rec+1)

    def preencher_matricula(self):
        try:                    
            loc_matricula_input = 'input[name="identificacao-form:matricula"]'
            self.act.clicar_elemento(loc_matricula_input)
            self.act.enviar_texto(loc_matricula_input, self.__matricula)
        except TimeoutException as e:
            dbg.warning(e.msg)

    def preencher_matricula_federal(self):
        try:                    
            loc_matricula_input = 'input[name="identificacao-form:matricula"]'
            self.act.clicar_elemento(loc_matricula_input)
            tamanho_matricula = len(self.__matricula)
            if(tamanho_matricula > 7):
                i = 0
                while tamanho_matricula > 7:
                    i += 1
                    self.__matricula = str(self.__matricula[i:]) 
                    print('Matricula sendo preparada...' + self.__matricula + ' Tamanho:' + str(i)) 
                    tamanho_matricula = len(self.__matricula)  

            self.act.enviar_texto(loc_matricula_input, self.__matricula)
        except TimeoutException as e:
            dbg.warning(e.msg)

    def resolver_captcha(self, rec=0):
        try:
            seletor_captcha = "#identificacao-form\\:idCaptcha\\:idImagemCaptcha img"

            self.id_captcha, self.resposta_captcha = self.captcha.resolver_captcha(
                seletor_captcha, "2.jpg")

            print("Resposta CAPTCHA:", self.resposta_captcha)
        except FalhaScreenShotCaptcha:
            return 0

    def preencher_resposta_captcha(self):
        self.sh.atribuir_valor_campo_jquery(
            "#identificacao-form\\\\:idCaptcha\\\\:txt-value",
            self.resposta_captcha)

    def clicar_confirmar(self):
        seletor_confirmar = "#identificacao-form\\:idCommandLink"
        self.sh.clicar_elemento_driver(seletor_confirmar)

    def escolher_matricula(self, similar = 70):
        loc_quantidade_matriculas = '/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr'
        quantidade_matriculas = self.act.quantidade_elemento(loc_quantidade_matriculas, self.by.XPATH)
        for i in range(1,quantidade_matriculas+1):
            loc_matricula_sistema = f'/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[3]' 
            matricula_sistema = self.act.obter_texto(loc_matricula_sistema, self.by.XPATH)
            if(similaridade(matricula_sistema, self.__matricula) >= similar):
                loc_escolha_matricula = f'/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[6]/a/img' 
                self.act.clicar_elemento(loc_escolha_matricula, self.by.XPATH)

    def verificar_erros(self):
        loc1 = '//*[@id="global-msg"]/li'
        msg_erro: str
        try:
            msg_erro = self.act.obter_texto(loc1, self.by.XPATH)
            print("Erro encontrado:", msg_erro)
            return msg_erro
        except TimeoutException:
            return False
