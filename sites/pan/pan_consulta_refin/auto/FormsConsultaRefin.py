# SuperClasse herdada por todas as outras classes que implementam automação da interface.
from sites.baseRobos.gui_auto import AutoGUI

# Exceptions nativas do Selenium
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException,
    InvalidElementStateException
)
# stdlib
from time import sleep
from selenium.webdriver import Chrome
from sites.pan.pan_consulta_refin import query_empregador_orgao
from typing import Union
from sites.pan.pan_consulta_refin.auto.auxiliares import (
    NotFoundResultException
)
from sites.pan.pan_consulta_refin.auto.auxiliares import (
    verificar_alertas
)

from sites.pan.pan_consulta_refin.auto.auxiliares import (
    aguardar_loading
)

from sites.elementos import Button, WebElement, Select

import pdb

class FormIdentificacao(AutoGUI):

    def __init__(self, driver: Chrome, **kwargs):
        super().__init__(driver)
        self.act.time_out = 1
        self.__orgao: str = kwargs.get('orgao', 'null')
        self.__sigla: str = kwargs.get('sigla', 'null')
        self.__cpf: str = kwargs.get('cpf', 'null')
        self.__esp_ben: Union[str, None] = kwargs.get('especieBeneficio')
        self.__ddd_celular: str = '11'
        self.__celular: str = '1448-5836'
        self.__data_nascimento: str = kwargs.get('dataNascimento', 'null')
        self.__matricula: str = str(kwargs.get('matricula', 'null'))
        self.__estadual: bool = kwargs.get('estadual', False)
        self.__federal: bool = kwargs.get('federal', False)
        self.__inss: bool = kwargs.get('inss', False)
        self.__dados = kwargs
        self.__dados_funcionais: dict = {}
        self.qtde_erros_digitos_matricula: int = 0
        self.wait: int = 0.5

    @property
    def qtde_erros_matricula_excedido(self):
        return self.qtde_erros_digitos_matricula >= 4

    def carregar_dados_funcionais(self):
        try:
            print("Query: codigo empregador e código órgão.")
            self.__dados_funcionais = query_empregador_orgao(
                orgao=self.__orgao, sigla=self.__sigla,
                federal=self.__federal, inss=self.__inss
            )
            print(f"Dados encontrados: {self.__dados_funcionais}")
        except KeyError as e:
            raise NotFoundResultException(
                f"Código do órgao {self.__orgao} não consta no banco de dados."
            )

    @property
    def cliente_sem_contato(self):
        loc = '//*[@id="ctl00_Cph_ucP_JN_JpOrg_ckSemContato"]'
        return self.act.check_box_is_checked(loc, self.by.XPATH)

    @property
    def cliente_sem_contato_card_ofertas(self):
        loc = '//*[@id="chkSemContato"]'
        return self.act.check_box_is_checked(loc, self.by.XPATH)

    @property
    def dados_solicitacao(self):
        return self.__dados

    @property
    def empregador(self):
        return self.__dados_funcionais['empregador']

    @empregador.setter
    def empregador(self, valor_novo):
        self.__dados_funcionais['empregador'] = valor_novo

    @property
    def orgao(self):
        return self.__dados_funcionais['orgao']

    @orgao.setter
    def orgao(self, valor_novo):
        self.__dados_funcionais['orgao'] = valor_novo

    def select_empegador(self):
        loc_empregador = '//select[@name="ctl00$Cph$ucP$JN$JpOrg$cbOrg4$CAMPO"]'
        empregador = self.__dados_funcionais['empregador']
        print("Empregador:", self.__dados_funcionais['empregador'])
        self.act.select_drop_down(loc_empregador, empregador, self.by.XPATH)

    def habilitar_contato_cliente(self):
        loc = '//*[@id="ctl00_Cph_ucP_JN_JpOrg_ckSemContato"]'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def select_orgao(self):
        loc = '//select[@name="ctl00$Cph$ucP$JN$JpOrg$cbOrg5$CAMPO"]'
        opcao_orgao = self.__dados_funcionais['orgao']
        print("Órgão:", opcao_orgao)
        try:
            self.act.select_drop_down(loc, opcao_orgao, self.by.XPATH)
        except TimeoutException:
            loc = '//*[@id="ctl00_Cph_ucP_JN_JpOrg_cbOrg5_CAMPO_EDIT"]'
            select_val = self.act.obter_valor(loc, self.by.XPATH)
            print("Campo pré-preenchido pelo sistema com o valor:", select_val)


    def campo_cpf(self):
        loc_cpf = '//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtCPF$CAMPO"]'
        print("CPF:", self.__cpf)
        self.act.forcar_clique_stale_element(loc_cpf, self.by.XPATH)
        self.act.enviar_texto_intervalado(
            loc_cpf, self.__cpf, self.by.XPATH, delay=0.03, clear=False
        )
        self.act.press_TAB(loc_cpf, self.by.XPATH)

    def campos_ddd_telefone(self, rec=0):
        print(f"DDD e Telefone: ({self.__ddd_celular})  {self.__celular}")

        if rec > 4:
            raise InvalidElementStateException(
                "<pan_consulta_refin.auto.FormIdentificacao.campos_ddd_telefone>")
        try:
            loc_ddd = '//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtDdd$CAMPO"]'
            self.act.forcar_clique_stale_element(loc_ddd, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_ddd, self.__ddd_celular, self.by.XPATH)

            loc_telefone = '//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtTel$CAMPO"]'
            self.act.forcar_clique_stale_element(loc_telefone, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_telefone, self.__celular, self.by.XPATH)

        except InvalidElementStateException:
            return self.campos_ddd_telefone(rec+1)

    def campo_matricula(self, contrato, rec=0):
        print("Matrícula", contrato['matricula'])
        if rec > 3:
            raise Exception("Não foi possível preencehr matricula")
        try:
            loc_matricula = ('//input[@name="ctl00$Cph$ucP$'
                             'JN$JpOrg$ucMat$txtMatricula$CAMPO"]')
            self.act.forcar_clique_stale_element(
                loc_matricula, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_matricula, contrato['matricula'],
                self.by.XPATH, delay=0.005, clear=False
            )
        except StaleElementReferenceException:
            return self.campo_matricula(contrato, rec + 1)

    def botao_consulta(self):
        print("Consultando...")
        loc_consulta = '//a[@id="btnConsultar_txt"]'
        self.act.forcar_clique_stale_element(loc_consulta, self.by.XPATH)

    def aguardar_abertura_modal(self):
        loc_modal: str = '//*[@id="ctl00_cph_FIJanela1"]/tbody/tr[1]/td/div[2]/span'
        loc_frame_modal: str = '//*[@id="ctl00_Cph_ucP_ppCli_frameAjuda"]'
        modal: bool = self.act.esta_presente(loc_modal, self.by.XPATH)
        i = 1
        while not modal:
            print(f"\r[{i}] Aguardando abertura do modal...", end="")
            self.act.trocar_frame_seletor(loc_frame_modal, self.by.XPATH)
            modal: bool = self.act.esta_presente(loc_modal, self.by.XPATH)
            sleep(0.7)
            if i > 30:
                break
            i += 1
        print()

    def modal_selecionar_matricula_cadastro(self, rec=0) -> bool:
        """
        Verifica se o modal de cadastros do cliente foi aberto.
        Caso tenha sido, clica no link correspondente à matrícula
        constante no contrato.
        """
        sleep(self.wait)
        matricula: str = self.__matricula
        loc_frame_modal: str = '//*[@id="ctl00_Cph_ucP_ppCli_frameAjuda"]'
        self.act.trocar_frame_seletor(loc_frame_modal, self.by.XPATH)

        # Utiliza o cabeçalho do modal como elemento de verificação
        loc_modal: str = '//*[@id="ctl00_cph_FIJanela1"]/tbody/tr[1]/td/div[2]/span'
        is_modal_presente: bool = self.act.esta_presente(loc_modal, self.by.XPATH)

        if not is_modal_presente:
            print("\rModal não foi aberto.")
            raise NotFoundResultException(f'Modal de busca de matricula não foi aberto')
        else:
            print("\rModal aberto.")

        print("Selecionando matrícula para cadastro.")
        # Retornar linhas da tabela - cada index é uma linha
        loc_tabela: str = '//table[@id="ctl00_cph_FIJanela1_FIJanelaPanel1_grvHomo"]//tr'
        linhas_tabela: list = self.act.retornar_elementos(loc_tabela, self.by.XPATH)

        # Buscar matrícula correta na tabela
        for cnt, linha in enumerate(linhas_tabela, 1):
            texto_matricula: str = linha.text.split(' ')[-1]
            print(matricula, texto_matricula)
            if matricula in texto_matricula or texto_matricula in matricula:
                sleep(1)
                loc_cadastro: str = f'//table/tbody/tr[1]/td/div/table/tbody/tr[{cnt}]//a'
                print(f"Buscada: {matricula}. Encontrada: {texto_matricula}.")
                try:
                    self.act.hover_e_clique(loc_cadastro, self.by.XPATH)
                except StaleElementReferenceException:
                    if rec > 5:
                        raise StaleElementReferenceException
                    return self.modal_selecionar_matricula_cadastro(rec+1)

                return True

        raise NotFoundResultException(f'Matrícula ({matricula}) não encontrada.')

    def select_promotora_card_ofertas(self):
        sleep(1)
        sl = Select(self.driver, '//*[@id="Promotora"]')
        sl.carregar_elemento()
        sl.selecionar_opcao("003987")

    def select_empregador_card_ofertas(self):
        sleep(1)

        loc_empregador = '//*[@id="Empregador"]'
        OPCAO_EMPREGADOR = str(self.__dados_funcionais['empregador'])
        print("Empregador:", OPCAO_EMPREGADOR)
        self.act.select_drop_down(loc_empregador, OPCAO_EMPREGADOR, self.by.XPATH)

    def select_orgao_card_ofertas(self):
        sleep(1)

        loc_empregador = '//*[@id="Orgao"]'
        OPCAO_ORGAO = str(self.__dados_funcionais['orgao'])
        print("Orgao:", OPCAO_ORGAO)
        self.act.select_drop_down(loc_empregador, OPCAO_ORGAO, self.by.XPATH)

    def campo_cpf_card_ofertas(self):
        loc_cpf = '//*[@id="CPF"]'
        print("CPF:", self.__cpf)
        self.act.forcar_clique_stale_element(loc_cpf, self.by.XPATH)
        self.act.enviar_texto_intervalado(loc_cpf, self.__cpf,
                                          self.by.XPATH, 0.01)
        self.act.press_TAB(loc_cpf, self.by.XPATH)

    def campo_data_nascimento_card_ofertas(self):
        loc_dt_nascimento = '//*[@id="DataNascimento"]'
        self.act.forcar_clique_stale_element(loc_dt_nascimento, self.by.XPATH)
        print("Data de Nascimento:" + self.__data_nascimento)
        
        try:
            array_data =  self.__data_nascimento.split('-')
            data_nascimento = array_data[2] + '/' + array_data[1] + '/'  + array_data[0]
        except:
            data_nascimento = '18/01/1983'   

        self.act.enviar_texto_intervalado(
        loc_dt_nascimento, data_nascimento, self.by.XPATH)

    def campos_ddd_telefone_card_ofertas(self):
        print(f"DDD e Telefone: ({self.__ddd_celular}) - {self.__celular}")

        loc_ddd = '//*[@id="DDD"]'
        self.act.forcar_clique_stale_element(loc_ddd, self.by.XPATH)
        self.act.enviar_texto_intervalado(
            loc_ddd, {self.__ddd_celular}, self.by.XPATH)

        loc_telefone = '//*[@id="Telefone"]'
        self.act.forcar_clique_stale_element(loc_telefone, self.by.XPATH)
        self.act.enviar_texto_intervalado(
            loc_telefone, {self.__celular}, self.by.XPATH)

    def habilitar_contato_cliente_card_ofertas(self):
        loc = '//*[@id="chkSemContato"]'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def campo_matricula_card_ofertas(self, rec=0):
        print("Matrícula", self.__matricula)

        if(self.__federal == True and len(self.__matricula) < 8 and str(self.__dados_funcionais['empregador']) == '005000'):
            numero_frente = '0'
            while len(self.__matricula) < 8:
                self.__matricula = numero_frente + self.__matricula      

        if rec > 3:
            raise Exception("Não foi possível preencehr matricula")
        try:
            loc_matricula = '//*[@id="Matricula"]'
            self.act.forcar_clique_stale_element(loc_matricula, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_matricula, self.__matricula,
                self.by.XPATH, delay=0.005, clear=False
            )
            self.act.press_TAB(loc_matricula, self.by.XPATH)

            if(str(self.__dados_funcionais['empregador']) == '005000'):
                loc_matricula_instituidor = '//*[@id="MatriculaInstituidor"]'
                self.act.forcar_clique_stale_element(loc_matricula_instituidor, self.by.XPATH)
                self.act.enviar_texto_intervalado(
                    loc_matricula_instituidor, self.__matricula,
                    self.by.XPATH, delay=0.005, clear=False
                )
                self.act.press_TAB(loc_matricula_instituidor, self.by.XPATH)


        except StaleElementReferenceException:
            return self.campo_matricula(contrato, rec + 1)

    def botao_consulta_card_ofertas(self, rec=0):
        print("Consultando...--------" + str(rec))
        if(rec > 50):
            return False

        loc_consulta = '//*[@id="gpbtnConsultar"]'
        loc_consulta_2 = '//*[@id="btnConsultar"]'
        loc_consulta_novo = '//*[@id="btnNovo"]'  
        try:
            self.act.hover_e_clique(loc_consulta_2, self.by.XPATH)
            #aguardar_loading(self.act, self.by.XPATH)
        except:
            try:
                self.act.hover_e_clique(loc_consulta, self.by.XPATH)
            except:
                try:
                    #pdb.set_trace()
                    self.act.hover_e_clique(loc_consulta_novo, self.by.XPATH)
                except:
                    return self.botao_consulta_card_ofertas(rec + 1)
        #except TimeoutException as e:
            #print(e)

    def descartar_card_ofertas_pendente(self, rec=0):
        loc = '/html/body/div[5]/div[3]/div/button[2]'
        loc_2 = '/html/body/div[4]/div[3]/div/button[1]'  
        
        sleep(0.2)

        try:
            try:
                self.act.hover_e_clique(loc, self.by.XPATH)
            except:
                self.act.hover_e_clique(loc_2, self.by.XPATH) 
        except ElementClickInterceptedException as e:
            if rec >= 3:
                return
            return self.descartar_card_ofertas_pendente(rec + 1)
        except TimeoutException as e:
            print(e)

    def clicar_novo_cliente_ofertas_pendente(self, rec=0):
        sleep(2)
        loc = '//*[@id="btnNovo"]'
        sleep(0.2)
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except ElementClickInterceptedException as e:
            if rec >= 3:
                return
            return self.clicar_novo_cliente_ofertas_pendente(rec + 1)
        except TimeoutException as e:
            print(e)

    def confirmar_descartar_card_ofertas(self, rec=0):
        loc = "/html/body/div[5]/div[3]/div/button"
        sleep(0.2)
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except ElementClickInterceptedException as e:
            print(e)
            if rec >= 3:
                return
            return self.confirmar_descartar_card_ofertas(rec + 1)
        except TimeoutException as e:
            print(e)

    def aguardar_abertura_modal_card_ofertas(self):
        loc_modal: str = '/html/body/div[5]'
        loc_frame_modal: str = '//*[@id="framePopUp"]'
        modal: bool = self.act.esta_presente(loc_modal, self.by.XPATH)
        i = 1
        while not modal:
            print(f"\r[{i}] Aguardando abertura do modal...", end="")
            self.act.trocar_frame_seletor(loc_frame_modal, self.by.XPATH)
            modal: bool = self.act.esta_presente(loc_modal, self.by.XPATH)
            sleep(0)
            if i > 2:
                break
            i += 1

    def modal_selecionar_matricula_cadastro_card_ofertas(self, rec=0) -> bool:
        """
        Verifica se o modal de cadastros do cliente foi aberto.
        Caso tenha sido, clica no link correspondente à matrícula
        constante no contrato.
        """
        sleep(self.wait)

        matricula: str = self.__matricula
        loc_frame_modal: str = '//*[@id="framePopUp"]'
        
        # Utiliza o cabeçalho do modal como elemento de verificação
        #loc_modal: str = '//*[@id="framePopUp"]'
        #is_modal_presente: bool = self.act.esta_presente(loc_modal, self.by.XPATH)

        if not self.act.trocar_frame_seletor(loc_frame_modal, self.by.XPATH):
            print("\rModal não foi aberto.")
            raise NotFoundResultException(f'Modal de busca de matricula não foi aberto')
        else:
            print("\rModal aberto.")

        print("Selecionando matrícula para cadastro.")
        # Retornar linhas da tabela - cada index é uma linha
        loc_tabela: str = '//*[@id="listarCPF"]/div/table/tbody/tr'
        linhas_tabela: list = self.act.retornar_elementos(loc_tabela, self.by.XPATH)

        loc_cadastro: str = f'//*[@id="listarCPF"]/div/table/tbody/tr[1]/td[1]/a'
        if not self.act.retornar_elemento(loc_cadastro, self.by.XPATH):
            print('Esperando elementos da matricula...')
            sleep(5)

        # Buscar matrícula correta na tabela
        for cnt, linha in enumerate(linhas_tabela, 1):
            texto_matricula: str = linha.text.split(' ')[-1]

            print(matricula, texto_matricula)
            if matricula in texto_matricula or texto_matricula in matricula:
                sleep(self.wait)
                #loc_cadastro: str = f'//*[@id="listarCPF"]/div/table/tbody/tr/td[{cnt}]/a'
                loc_cadastro: str = f'//*[@id="listarCPF"]/div/table/tbody/tr[{cnt}]/td[1]/a'
                print(f"Buscada: {matricula}. Encontrada: {texto_matricula}.")
                if(self.__orgao == 2 and len(texto_matricula) > 7):
                    continue
                try:
                    self.act.hover_e_clique(loc_cadastro, self.by.XPATH)
                except StaleElementReferenceException:
                    if rec > 10:
                        raise StaleElementReferenceException
                    return self.modal_selecionar_matricula_cadastro(rec+1)

                return True

        raise NotFoundResultException(f'Matrícula ({matricula}) não encontrada.')

    def ofertarRefinanciamento(self):
        loc = '//*[@id="btnOfertarRefinanciamento"]'
        self.act.hover_e_clique(loc, self.by.XPATH)    

    def verificar_retorno_card_ofertas(self):
        try:
            texto_sem_refin =  self.act.obter_texto('//*[@id="textRefinanciamento"]',self.by.XPATH)

            if r"Cliente não possui outros contratos" in texto_sem_refin:
                print('Sem contrato disponivel para refinanciamento...')
                return True

            if r"Cliente possui 0 ativos com saldo devedor total" in texto_sem_refin:
                print('Sem contrato ativo para refinanciamento...')
                return True
        except:
            return False



class FormDadosSimulacao(AutoGUI):
    def __init__(self, driver: Chrome, **kwargs):
        super().__init__(driver)
        self.act.time_out = 2
        self.__operacao: str = "Refinanciamento"
        self.__renda: str = kwargs.get('renda', 'null')
        self.__val_contrato: str = kwargs.get('valorContrato', 'null')

    def select_operacao(self):
        print("Selecionando operação", self.__operacao)
        loc_op = '//*[@id="ctl00_Cph_ucP_JN_JpTpOper_cbTpOper_CAMPO"]'

        self.act.forcar_clique_stale_element(loc_op, self.by.XPATH, pause=0.1)
        self.act.select_drop_down(loc_op, self.__operacao, self.by.XPATH)

    def atualizar_lista_refinanciamentos(self, rec=0):
        try:
            print("Clicando em atualizar lista de refinanciamentos")
            loc = '//*[@id="btAtuListaRefin_txt"]'
            self.act.clicar_elemento(loc, self.by.XPATH)
            verificar_alertas(self.chrome_driver)

        except TimeoutException:
            if rec > 3:
                raise TimeoutException
            return self.atualizar_lista_refinanciamentos(rec+1)


class TabelaRefinanciamentos(AutoGUI):
    """
    Colunas tabela:
    1 -> check box
    10 -> valorParcela
    11 -> saldoDevedor
    6 -> parcelas vencidas
    """
    def __init__(self, driver: Chrome):
        super().__init__(driver)
        self.act.time_out = 1
        self.__saldoDevedor: str = ""
        self.__valorParcela: str = ""
        self.qtd_refins_invalidos: int = 0
        self.n_linhas: list = []
        self.linha_tab = ""
        self.idx_check_box: int = 0
        self.__lista_refins: list = []

    @property
    def dados_refinanciamentos(self):
        return self.__lista_refins

    @property
    def val_percela(self):
        return self.__valorParcela

    def validar_consulta_refin(self):
        keys_refins = ['saldoDevedor', 'valorParcela', 'valorLiberado', 'prazo']
        if not self.__lista_refins:
            raise NotFoundResultException("Não foram encontrados refinanciamentos.")

        for refin in self.__lista_refins:
            for key in keys_refins:
                print("Val:", refin.get(key, False))
                if not refin.get(key, False):
                    raise NotFoundResultException("Não foram encontrados refinanciamentos.")

    def set_linha_tabela_e_checkbox(self, idx):
        self.linha_tab = f'//*[@id="tblRefin"]/tbody/tr[{idx}]'
        self.idx_check_box += 1
        print(self.linha_tab)

    def atualizar_lista_refins(self, dados_simulados: dict):
        dados_tabela_refin = {
            'saldoDevedor': self.__saldoDevedor,
            'valorParcela': self.__valorParcela
        }
        print("Atualizando lista de refinanciamentos:")
        print({**dados_tabela_refin, **dados_simulados})

        self.__lista_refins.append({**dados_tabela_refin, **dados_simulados})

    def verificar_quantidade_refinanciamentos(self):
        loc = '//*[@id="tblRefin"]/tbody/tr'
        n_trs: int = self.act.quantidade_elemento(
            loc, self.by.XPATH)

        self.n_linhas = [n for n in range(2, n_trs, 2)]
        print("Quantidade de refinanciamentos:", (n_trs - 1) / 2)
        print("Linhas refinanciamento:", self.n_linhas)

    def parcelas_vencidas(self):
        loc = self.linha_tab + '/td[6]'
        print(loc)
        n_vencidas = self.act.obter_texto(loc, self.by.XPATH)
        n_vencidas = int(n_vencidas.strip())

        print("Quantidade de parcelas vencidas:", n_vencidas)

        return n_vencidas > 0

    def extrair_valor_parcela(self):
        print("Extrair valor parcela:", end=' ')
        loc = self.linha_tab + '/td[10]'
        self.__valorParcela = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__valorParcela)

    def extrair_saldo_devedor(self):
        print("Extrair saldo devedor:", end=' ')
        loc = self.linha_tab + '/td[11]'
        self.__saldoDevedor = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__saldoDevedor)

    @property
    def checkbox_disabled(self):
        idx = self.idx_check_box
        loc = f'//*[@id="ctl00_Cph_ucP_JN_JpRefin_rptRefin_ctl0{idx}_chkSelOperRefin"]'
        check_box = self.act.retornar_elemento(loc, self.by.XPATH)
        return not check_box.is_enabled()

    def selecionar_check_box(self):
        print("Selecionando checkbox")
        idx = self.idx_check_box

        if(idx > 1):
            print("Desmarcando o checkbox anterior")
            idx_desmarca = self.idx_check_box - 1
            loc = f'//*[@id="ctl00_Cph_ucP_JN_JpRefin_rptRefin_ctl0{idx_desmarca}_chkSelOperRefin"]'
            self.act.hover_e_clique(loc, self.by.XPATH, pause=1)
            sleep(4)

        loc = f'//*[@id="ctl00_Cph_ucP_JN_JpRefin_rptRefin_ctl0{idx}_chkSelOperRefin"]'
        self.act.hover_e_clique(loc, self.by.XPATH, pause=0.1)

    @property
    def validar_dados_refin(self):
        return self.__saldoDevedor and self.__valorParcela

    def validar_lista_refinanciamentos(self):
        if self.__lista_refins:
            return True
        else:
            raise NotFoundResultException(
                "Não foram encontrados refinanciamentos."
            )


class TabelaSimulacao(AutoGUI):
    def __init__(self, driver: Chrome, **kwargs):
        super().__init__(driver)
        self.act.time_out = 1
        self.__tipo_ben = kwargs.get('especieBeneficio')
        self.__idade = kwargs.get('idade')
        self.__valorLiberado: str = ""
        self.__prazo: str = ""
        self.nome_tabela: str = ""
        self.dados_solicitacao: dict = kwargs

    @property
    def dados_simulados(self) -> dict:
        return {
            'valorLiberado': self.__valorLiberado,
            'prazo': self.__prazo,
        }

    @property
    def tabela_invalida(self) -> bool:
        inv3 = "INSS_RFN_CIP_INVALID_RET" in self.nome_tabela
        if str(self.__tipo_ben) is None:
            return inv3
        else:
            inv1 = (self.__tipo_ben == "32" and
                    int(self.__idade) < 60 and
                    'INSS_RFN_INVALID_NORMAL' not in self.nome_tabela)
            inv2 = (self.__tipo_ben == "32" and int(self.__idade) >= 60
                    and "INSS_RFN_CIP_INVALID_RET" in self.nome_tabela)

            return inv1 or inv2 or inv3

    @property
    def valor_disponivel_invalido(self):
        return (not self.__valorLiberado) or self.__valorLiberado == "0,00"

    def preencher_campo_parcela(self, val_parcela: str):
        loc_parcela = '//*[@id="ctl00_Cph_ucP_JN_JpSim_txtVlrParc_CAMPO"]'
        
        print("Preenchendo parcela:", val_parcela)
        #self.act.forcar_clique_stale_element(loc_parcela, self.by.XPATH, pause=0.1)

        loc_loading = '//*[@id="ctl00_Image2"]'
        try:
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)
        except:
            pass
        
        self.act.enviar_texto_intervalado(loc_parcela, '', self.by.XPATH, delay=0.5, clear=True)
        
        try:
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)
        except:
            pass
        self.act.enviar_texto_intervalado(loc_parcela, val_parcela, self.by.XPATH, delay=0.5, clear=False)

        try:
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)
        except:
            pass

        #pdb.set_trace()

    def botao_calcular_financiamento(self):
        print("Calculando financiamento.")
        loc_calcular = '//*[@id="btnCalcular_txt"]'
        self.act.clicar_elemento(loc_calcular, self.by.XPATH)

    def refinanciamento_indisponivel(self):
        loc = '//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond"]/tbody/tr[2]/td[7]'
        status = self.act.obter_atributo(loc, "title", self.inferir(loc))
        print("Status refin: ", status)
        return status

    def extrair_prazo(self):
        print("Extraindo prazo de refinanciamento.", end=' ')
        loc = '//*[@id="ctl00_Cph_ucP_JN_JpSim_cbPrz_CAMPO"]'
        self.__prazo = self.act.obter_valor(loc, self.by.XPATH)
        print(self.__prazo)

    def extrair_nome_tabela(self, nome_tabela = 'NORMAL'):
        # print("Extraindo nome da tabela:", end=" ")
        # loc = "//*[@id='ctl00_Cph_ucP_JN_JpSim_gvCond']/tbody/tr[2]/td[3]"
        # self.nome_tabela = self.act.obter_texto(loc, self.by.XPATH)
        self.nome_tabela = nome_tabela
        print(self.nome_tabela)

    def extrair_val_liberado(self, valor = 0):
        print("Extraindo valor liberado", end=' ')
        #loc = "//*[@id='ctl00_Cph_ucP_JN_JpSim_gvCond']/tbody/tr[2]/td[6]"
        #self.__valorLiberado = self.act.obter_texto(loc, self.by.XPATH)
        self.__valorLiberado = valor
        print(self.__valorLiberado)

    @property
    def validar_dados_simulacao(self):
        return self.__valorLiberado and self.__prazo
