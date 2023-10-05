"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_formulários
| data: 2020-02-04
| autor: Gustavo Belleza

    Contém classes que representam formulários (ou partes lógicas desses formularios).
Cada método das classes manipula um, e apenas um,  campo do formulário representado
pela classe no qual está contido.
    Ao fim do módulo, estão contidas funções que são essenciais para execução das
tarefas de automação do processo de inserção.
    Neste módulo estão contidas as classes:
        1. PanFormIdentificacao. 2. PanFormInsercaoDadosProposta.
        3. PanFormInsercaoDadosPessoais. 4. PanFormInsercaoDadosBancarios.
        5. PanFormFinalizarInsercao.
    E as funçoes:
        1. verificar_alertas. 2. tratar_mensagens_sistema.
        3. filtrar_tipo_conta

    Padrões comuns para preenchimento de campos:
    1. Simples:
        loc = 'seletor'
        self.act.ação_a_ser_executada
    2. Clique e preenchimento -> dispara eventos <onfocus>
        loc = 'seletor'
        self.act.clique*
        self.act.preencher_campo
    3. Clique, preenchimento, clique -> dispara eventos <onfocus> e <onchange>
        loc = 'seletor'
        self.act.clique*
        self.act.preencher_campo
        self.act.clique*
    4. try:
            ação
       except InvalidElementStateException:
            ação

        => Evita erros quando o elemento com o qual se tenta interagir
        está 'disabled' ou 'readonly'

    * Cliques usando self.act.forcar_clique_stale_element evitam erros
    do tipo InvalidElementStateException.
"""
# SuperClasse herdada por todas as outras classes que implementam automação da interface.
from sites.baseRobos.gui_auto import AutoGUI

# Exceptions nativas do Selenium
from selenium.common.exceptions import (
    StaleElementReferenceException, NoAlertPresentException,
    UnexpectedAlertPresentException, TimeoutException,
    InvalidElementStateException, ElementClickInterceptedException
)
# Funções auxiliares
from sites.baseRobos.core.data_helpers import similaridade
from sites.baseRobos.core.data_helpers import is_number
from sites.baseRobos.core.uconecte import Uconecte

# Função que retorna todas as mensagens de erro já documentadas no site.
from sites.elementos import Button, WebElement, Select
from sites.pan.pan_insercao.data.colections import mensagens_alertas

# stdlib
import re
from time import sleep


class PanFormIdentificacao(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 2

    def oferta_disponivel(self):
        loc_loading = '//*[@id="ctl00_Image2"]'
        self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=300)
        loc_oferta = '//*[@id="textMargemLivre"]'
        if 'Crivo - Card indisponível.' in self.act.obter_texto(loc_oferta, self.by.XPATH):
            return False
        else:
            return True

    def existeCardPendente(self):
        return self.act.esta_presente(
            '/html/body/div[4]/div[3]/div/button[2]', self.by.XPATH)

    def existeAvisoCardCancelado(self):
        return self.act.esta_presente(
            '/html/body/div[5]', self.by.XPATH)

    def hoverCadastro(self):
        btnCadastro = Button(self.driver, '//*[@id="navbar-collapse-funcao"]/ul/li[1]/a')
        btnCadastro.carregar_elemento()

        btnCardOfertas = Button(self.driver, '//*[@id="navbar-collapse-funcao"]/ul/li[1]/ul/li[1]/a')
        btnCardOfertas.carregar_elemento()

        btnCadastro.hoverClickOther(btnCardOfertas.elemento)

    def clicarCardOfertas(self):
        btn = Button(
            self.driver, '//*[@id="navbar-collapse-funcao"]/ul/li[1]/ul/li[1]/a')
        btn.carregar_elemento()
        btn.hover_e_clique(pause=0.2)

    def selectPromotora(self):
        sleep(1)
        sl = Select(self.driver, '//*[@id="Promotora"]')
        sl.carregar_elemento()
        sl.selecionar_opcao("003987")

    def select_empegador(self):
        sleep(1)

        loc_empregador = '//*[@id="Empregador"]'
        OPCAO_INSS = '007000'
        print("Empregador:", OPCAO_INSS)
        self.act.select_drop_down(loc_empregador, OPCAO_INSS, self.by.XPATH)

    def select_orgao(self, contrato):
        sleep(1)

        loc_orgao = '//*[@id="Orgao"]'
        opcao_orgao = self.__filtrar_tipo_beneficio(contrato["especieBeneficio"])
        print("Órgão:", opcao_orgao)
        self.act.select_drop_down(loc_orgao, opcao_orgao, self.by.XPATH)

    def campo_cpf(self, contrato):
        loc_cpf = '//*[@id="CPF"]'
        print("CPF:", contrato['cpf'])
        self.act.forcar_clique_stale_element(loc_cpf, self.by.XPATH)
        self.act.enviar_texto_intervalado(loc_cpf, contrato['cpf'],
                                          self.by.XPATH, 0.03)
        self.act.press_TAB(loc_cpf, self.by.XPATH)

    def campo_data_nascimento(self, contrato):
        try:
            loc_dt_nascimento = '//*[@id="DataNascimento"]'
            #self.act.forcar_clique_stale_element(loc_dt_nascimento, self.by.XPATH)
            print("Data de Nascimento:", contrato['dataNascimento'])
            self.act.enviar_texto_intervalado(
                loc_dt_nascimento, contrato['dataNascimento'], self.by.XPATH)
        except InvalidElementStateException as e:
            print(e)
        except TimeoutException as e:
            print(e)

    def campos_ddd_telefone(self, contrato):
        print(f"DDD e Telefone: ({contrato['dddCelular']}) - {contrato['celular']}")

        loc_ddd = '//*[@id="DDD"]'
        self.act.forcar_clique_stale_element(loc_ddd, self.by.XPATH)
        self.act.enviar_texto_intervalado(
            loc_ddd, contrato['dddCelular'], self.by.XPATH)

        loc_telefone = '//*[@id="Telefone"]'
        self.act.forcar_clique_stale_element(loc_telefone, self.by.XPATH)
        self.act.enviar_texto_intervalado(
            loc_telefone, contrato['celular'], self.by.XPATH)

    def campo_matricula(self, contrato, rec=0):
        print("Matrícula", contrato['matricula'])
        if rec > 3:
            raise Exception("Não foi possível preencehr matricula")
        try:
            loc_matricula = '//*[@id="Matricula"]'
            self.act.forcar_clique_stale_element(loc_matricula, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_matricula, contrato['matricula'],
                self.by.XPATH, delay=0.005, clear=False
            )
            self.act.press_TAB(loc_matricula, self.by.XPATH)
        except StaleElementReferenceException:
            return self.campo_matricula(contrato, rec + 1)

    def botao_consulta(self, rec=0):
        print("Consultando...")
        sleep(0.5)
        loc_consulta = '//*[@id="btnConsultar"]'
        try:
            self.act.clicar_elemento(loc_consulta, self.by.XPATH)
        except ElementClickInterceptedException as e:
            print(e)
            if rec >= 3:
                return
            return self.botao_consulta(rec + 1)
        except TimeoutException as e:
            print(e)
            return

    def descartarCardPendente(self, rec=0):
        loc = '/html/body/div[4]/div[3]/div/button[2]'
        sleep(0.2)
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except:
            if rec >= 3:
                return
            return self.descartarCardPendente(rec + 1)

    def confirmarDescartarPendencia(self, rec=0):
        loc = "/html/body/div[5]/div[3]/div/button"
        sleep(0.2)
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except ElementClickInterceptedException as e:
            print(e)
            if rec >= 3:
                return
            return self.confirmarDescartarPendencia(rec + 1)
        except TimeoutException as e:
            print(e)

    def descartarCardDataPrev(self, rec=0):
        loc = '/html/body/div[5]/div[3]/div/button'
        sleep(0.2)
        try:
            self.act.hover_e_clique(loc, self.by.XPATH)
        except:
            print('Não há modal Dataprev')
            pass

    def ofertarMargemLivre(self, rec=0):
        sleep(5)
        try:
            loc = '//*[@id="btnOfertarMargemLivre"]'
            self.act.hover_e_clique(loc, self.by.XPATH)
        except TimeoutException as e:
            print(e)
            if rec >= 3:
                return
            return self.ofertarMargemLivre(rec + 1)

    def ofertarRefinanciamento(self):
        loc = '//*[@id="btnOfertarRefinanciamento"]'
        self.act.hover_e_clique(loc, self.by.XPATH)

    @staticmethod
    def __filtrar_tipo_beneficio(especieBeneficio: str) -> str:
        """
        Filtra os diversos tipos de benefícios previdenciários em duas
        grandes categorias aceitas pelo site: Aposentadorias (501) e
        Pensões (502).
        """
        aposentadorias = ['42', '32', '41', '46', '52', '57', '92']
        pensoes = ['01','21', '03', '23', '27', '93']
        print(especieBeneficio)
        # if especieBeneficio in aposentadorias:
        #     return '000501'
        
        if especieBeneficio in pensoes:
            return '000502'
        else:
            return '000501'
        # else:
        #     print("ESPÉCIE DE BENEFÍCIO NÃO CODIFICADA:", especieBeneficio)
        #     sleep(10)
        #     raise Exception("Reiniciando fila de contratos.")

    def modal_selecionar_matricula_cadastro(self, acao="fechar", matricula: str = None) -> bool:
        """
        Verifica se o modal de cadastros do cliente foi aberto.
        Caso tenha sido, clica no link correspondente à matrícula
        constante no contrato.
        """

        loc_frame_modal: str = 'framePopUp'
        self.act.trocar_frame_referencia(loc_frame_modal)

        if acao != "fechar":
            # Utiliza o cabeçalho do modal como elemento de verificação
            loc_modal: str = '//*[@id="ctl00_cph_FIJanela1"]/tbody/tr[1]/td/div[2]/span'
            is_modal_presente: bool = self.act.esta_presente(loc_modal, self.by.XPATH)

            if not is_modal_presente:
                print("\rModal não foi aberto.")
                return False
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
                    self.act.forcar_clique_stale_element(loc_cadastro, self.by.XPATH)

                    return True
            print('Matrícula não encontrada.')

        print("Fechando modal da matrícula")
        loc_btn_fechar: str = '//*[@id="btnFechar"]'
        self.act.forcar_clique_stale_element(loc_btn_fechar, self.by.XPATH)


class PanFormInsercaoDadosProposta(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.tabela_selecionada: str = ""
        self.act.time_out = 2

    def select_operacao(self, contrato: dict, recr=0):
        sleep(0.6)
        if recr > 6:
            raise Exception("Não foi possivel clicar no elemento <select_operacao>")
        value = contrato["tipoOperacao"]
        print("Selecionando operação", value)
        loc_op = '//*[@id="ctl00_Cph_ucP_JN_JpTpOper_cbTpOper_CAMPO"]'
        try:
            self.act.clicar_elemento(loc_op, self.by.XPATH)
            self.act.select_drop_down(loc_op, value, self.by.XPATH)
        except TimeoutException as e:
            print(e)
            return self.select_operacao(contrato, recr + 1)
        except StaleElementReferenceException as e:
            print(e)
            return self.select_operacao(contrato, recr + 1)
        except InvalidElementStateException as e:
            print(e)
            return self.select_operacao(contrato, recr + 1)

    def campo_renda(self, contrato: dict):
        loc_renda = '//*[@id="ctl00_Cph_ucP_JN_JpSim_txtRnd_CAMPO"]'

        if self.act.obter_valor(loc_renda, self.by.XPATH) == '':
            renda = contrato['renda'].replace('.', ',')
            print("Preenchendo renda:", contrato["renda"])
            self.act.forcar_clique_stale_element(loc_renda, self.by.XPATH, pause=0.1)

            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.enviar_texto_intervalado(
                loc_renda, renda, self.by.XPATH, delay=0.08, clear=False)

    def campo_valor_solicitacao(self, contrato):
        loc_valor_solicitado = '//*[@id="ctl00_Cph_ucP_JN_JpSim_txtVlrSol_CAMPO"]'
        self.act.forcar_clique_stale_element(loc_valor_solicitado, self.by.XPATH, pause=0.1)

        verificar_alertas(self.act, contrato)

        valor_solicitado = contrato["valorContrato"].replace('.', ',')

        print("Valor solicitado", valor_solicitado)
        self.act.forcar_clique_stale_element(loc_valor_solicitado, self.by.XPATH, pause=0.1)
        verificar_alertas(self.act, contrato)
        self.act.enviar_texto(loc_valor_solicitado, valor_solicitado,
                              self.by.XPATH, clear=True)

    def campo_valor_parcela(self, contrato):
        loc_valor_parcela = '//*[@id="ctl00_Cph_ucP_JN_JpSim_txtVlrParc_CAMPO"]'
        self.act.forcar_clique_stale_element(loc_valor_parcela, self.by.XPATH, pause=0.1)

        verificar_alertas(self.act, contrato)

        valor_parcela = contrato["valorParcela"].replace('.', ',')

        print("Valor da parcela", valor_parcela)
        self.act.forcar_clique_stale_element(loc_valor_parcela, self.by.XPATH, pause=0.1)
        verificar_alertas(self.act, contrato)
        self.act.enviar_texto(loc_valor_parcela, valor_parcela,
                              self.by.XPATH, clear=True)

    def selecionar_campo_prazo(self, contrato: dict, recr=0):
        value = str(contrato["prazo"])
        print("Selecionando prazo", value)
        loc_prazo = '//*[@id="ctl00_Cph_ucP_JN_JpSim_cbPrz_CAMPO"]'
        self.act.select_drop_down(loc_prazo, value, self.by.XPATH)

    def botao_calcular_financiamento(self):
        print("Calculando financiamento.")
        loc_calcular = '//*[@id="btnCalcular_txt"]'
        self.act.clicar_elemento(loc_calcular, self.by.XPATH)

    def retirar_seguro(self):
        print("Retirando seguro.")
        loc_seguro= '//*[@id="ctl00_Cph_ucP_JN_JpSim_ucDSP_grdDespesas_ctl03_CkbIncluir"]'
        self.act.clicar_elemento(loc_seguro, self.by.XPATH)

    def recalcular(self):
        print("Recalculando...")
        loc_recalcular= '//*[@id="btnRecalc_txt"]'
        self.act.clicar_elemento(loc_recalcular, self.by.XPATH)

    def atualiza_valor(self):
        print("Atualizando novo valor...")
        loc_novo_valor = '//*[@id="ctl00_Cph_ucP_JN_JpSim_ucDSP_grdDespesas_ctl04_Label1"]'
        return self.act.obter_texto(loc_novo_valor, self.by.XPATH)

    def checkbox_tabela_beneficio(self, selec_tabela, contrato):
        print("Selecionar tabela:", selec_tabela)
        print("Selecionando checkbox tabela: ", contrato['tabela'])
        self.verificar_indisponibilidade_tabela(selec_tabela, contrato)
        try:
            print(selec_tabela)
            self.act.forcar_preenchimento_cb(selec_tabela, self.by.XPATH)
            verificar_alertas(self.act, contrato)
        except TimeoutException:
            self.verificar_indisponibilidade_tabela(selec_tabela, contrato)

    def verificar_indisponibilidade_tabela(self, loc_checkbox: str, contrato: dict) -> bool:
        mensagem: str = ""

        if loc_checkbox is None:
            mensagem = "Tipo do Benefício do cliente não foi encontrado na tabela"
            tratar_mensagens_sistema(self.act, mensagem, contrato)

        loc_exclamacao: str = loc_checkbox.replace('ckSel', 'lObs')
        disabled: bool = self.act.verificar_atributo(
            loc_exclamacao, 'disabled', self.by.XPATH)

        if disabled:
            loc_msg: str = loc_exclamacao + '/../.'
            mensagem = self.act.obter_atributo(loc_msg, 'title', self.by.XPATH)
            print(mensagem)
            tratar_mensagens_sistema(self.act, mensagem, contrato)
            return False

        else:
            print('ok')
            return True

    def filtrar_tipo_contrato(self, tabela_contrato: str, tipo_contrato: str, contrato: dict) -> str:
        """
        Realiza a triagem e marca o contrato como Margem Complementar ("Aumento") ou
        Financiamento ("Fin")
        """
        self.act.time_out = 0.02
        print("Tipo de contrato:", tipo_contrato)
        print('Tipo de tabela:', tabela_contrato)
        tipo_con: str = ''
        tipo_tab: str = ''

        if tipo_contrato == "NOVO MARGEM COMPLEMENTAR":
            if tabela_contrato == 'tabelaNormal':
                if(contrato['carenciaTabela'] == '120'):
                    tipo_tab = 'INSS_120_NOV_35_NORMAL_A_'  # 'AUMENTO_NORMAL'
                else:
                    tipo_tab = 'INSS_NOV_35_NORMAL_A_'  # 'AUMENTO_NORMAL'
            elif tabela_contrato == 'tabelaInvalidezPericia':
                if(contrato['carenciaTabela'] == '120'):
                    tipo_tab = 'INSS_120_NOV_35_INVALID_NORMAL'  # 'AUMENTO_PER_INVALID_NORMAL'
                else:
                    tipo_tab = 'INSS_NOV_35_INVALID_NORMAL'  # 'AUMENTO_PER_INVALID_NORMAL'
        else:
            if tabela_contrato == 'tabelaNormal':
                if(contrato['carenciaTabela'] == '120'):
                    tipo_tab = 'INSS_NOV_120_NORMAL_A_'  # 'AUMENTO_NORMAL'
                else:
                    tipo_tab = 'INSS_NOV_NORMAL_A_'  # 'AUMENTO_NORMAL'
            elif tabela_contrato == 'tabelaInvalidezPericia':
                if(contrato['carenciaTabela'] == '120'):
                    tipo_tab = 'INSS_NOV_120_INVALID_NORMAL'  # 'AUMENTO_PER_INVALID_NORMAL'
                else:
                    tipo_tab = 'INSS_NOV_INVALID_NORMAL'  # 'AUMENTO_PER_INVALID_NORMAL'

        loc_base: str = ''
        for i in range(20):
            print(i, end=" ")
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=30)
            if i < 10:
                loc_base = f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl0{i}_ckSel"]'
            else:
                loc_base = f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl{i}_ckSel"]'
            loc_texto: str = loc_base + '/../..'
            try:
                texto_tabela: str = self.act.obter_texto(loc_texto, self.by.XPATH)
            except:
                continue
            if tipo_tab in texto_tabela.upper():
                self.act.time_out = 2
                self.tabela_selecionada = texto_tabela
                return loc_base
        self.act.time_out = 2

    def filtrar_tipo_contrato_forcado(self, tabela_contrato: str, tipo_contrato: str, contrato: dict) -> str:
        """
        Realiza a triagem e marca o contrato como Margem Complementar ("Aumento") ou
        Financiamento ("Fin")
        """
        self.act.time_out = 0.02
        print("Tipo de contrato:", tipo_contrato)
        print('Tipo de tabela:', tabela_contrato)
        tipo_con: str = ''
        tipo_tab: str = ''
            
        if tabela_contrato == 'tabelaNormal':
            tipo_tab = 'INSS_NOV_NORMAL_A_'
        else:
            tipo_tab = 'INSS_NOV_INVALID_NORMAL'

        loc_base: str = ''
        for i in range(20):
            print(i, end=" ")
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=30)
            if i < 10:
                loc_base = f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl0{i}_ckSel"]'
            else:
                loc_base = f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl{i}_ckSel"]'
            loc_texto: str = loc_base + '/../..'
            try:
                texto_tabela: str = self.act.obter_texto(loc_texto, self.by.XPATH)
            except:
                continue
            if tipo_tab in texto_tabela.upper():
                self.act.time_out = 2
                self.tabela_selecionada = texto_tabela
                return loc_base
        self.act.time_out = 2


class PanFormInsercaoDadosPessoais(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 2

    def campo_nome(self, contrato):
        try:
            loc_nome = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNome_CAMPO"]'
            print("Nome:", contrato['nome'])
            self.act.forcar_clique_stale_element(loc_nome, self.by.XPATH, pause=0.1)
            self.act.enviar_texto(loc_nome, contrato['nome'], self.by.XPATH)
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_estado_civil(self):
        try:
            loc_ecivil = '//*[@id="ctl00_Cph_ucP_JN_JpCli_cbECivil_CAMPO"]'
            if self.act.verificar_atributo(loc_ecivil, 'value', self.by.XPATH):
                print("Estado Civil.")
                self.act.forcar_clique_stale_element(loc_ecivil, self.by.XPATH, pause=0.1)
                self.act.select_drop_down(loc_ecivil, 'Outros', self.by.XPATH)
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_rg(self, contrato):
        try:
            loc_rg = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtDoc_CAMPO"]'
            print("Identidade.", contrato['identidade'])
            self.act.forcar_clique_stale_element(loc_rg, self.by.XPATH, pause=0.1)
            self.act.enviar_texto(loc_rg, contrato['identidade'], self.by.XPATH)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_cep(self, contrato, rec=1, max_rec=10):
        try:
            loc_loading = '//*[@id="ctl00_Image2"]'
            loc_cep = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]'
            print("CEP.", contrato['cep'])
            self.act.forcar_clique_stale_element(loc_cep, self.by.XPATH, pause=0.01)
            self.act.enviar_texto_intervalado(
                loc_cep, contrato['cep'], self.by.XPATH, delay=0.01)

            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.press_enter(loc_cep, self.by.XPATH)

            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.press_TAB(loc_cep, self.by.XPATH)

            sleep(1)
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            if not self.act.obter_valor(loc_cep, self.by.XPATH):
                sleep(0.5)
                return self.campo_cep(contrato, rec + 1)

        except StaleElementReferenceException:
            if rec < max_rec:
                return self.campo_cep(contrato, rec + 1)
        except TimeoutException:
            if rec < max_rec:
                return self.campo_cep(contrato, rec + 1)
        except InvalidElementStateException:
            if rec < max_rec:
                return self.campo_cep(contrato, rec + 1)

    def campo_endereco(self, contrato):
        try:
            loc_end = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEnd_CAMPO"]'
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.forcar_clique_stale_element(loc_end, self.by.XPATH, pause=0.1)

            print('Logradouro: ', contrato['logradouro'])

            # rua = self.__separar_rua_endereco(contrato['logradouro'])
            self.act.enviar_texto_intervalado(
                loc_end, contrato['logradouro'], self.by.XPATH, delay=0.1)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_n_casa(self, contrato):
        try:
            loc_n_casa = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNr_CAMPO"]'
            print("Numero da casa:", contrato['numeroCasa'])
            self.act.forcar_clique_stale_element(loc_n_casa, self.by.XPATH, pause=0.1)
            self.act.enviar_texto(loc_n_casa, contrato['numeroCasa'], self.by.XPATH)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_complemento(self, contrato):
        try:
            complemento = contrato['complemento']
            if not complemento:
                complemento = "Casa"

            print("Complemento.", complemento)
            loc_compl = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCompl_CAMPO"]'
            self.act.forcar_clique_stale_element(loc_compl, self.by.XPATH, pause=0.1)
            self.act.press_backspace(loc_compl, 15, self.by.XPATH, end=True)
            self.act.enviar_texto_intervalado(
                loc_compl, complemento, self.by.XPATH, delay=0.001, clear=False)
            self.act.forcar_clique_stale_element(loc_compl, self.by.XPATH, pause=0.1)

        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_bairro(self, contrato):
        try:
            loc_bairro = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtBai_CAMPO"]'
            self.act.forcar_clique_stale_element(loc_bairro, self.by.XPATH, pause=0.1)
            if not self.act.obter_atributo(loc_bairro, 'readonly', self.by.XPATH):
                print("Bairro.", contrato['bairro'])

                self.act.enviar_texto(loc_bairro, contrato['bairro'], self.by.XPATH)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_nome_mae(self, contrato):
        try:
            loc_mae = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtMae_CAMPO"]'
            print('Nome da mãe:', contrato['nomeMae'])
            self.act.forcar_clique_stale_element(loc_mae, self.by.XPATH, pause=0.1)
            self.act.enviar_texto(loc_mae, contrato['nomeMae'], self.by.XPATH)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_email(self, contrato):
        try:
            loc_email = '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEmail_CAMPO"]'

            print("Email", contrato["email"])
            self.act.hover_e_clique(loc_email, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_email, contrato["email"].lower(), self.by.XPATH, delay=0.008
            )
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    def campo_cpf_insercao(self, contrato):
        try:
            loc_cep = '//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtCPF$CAMPO"]'

            print("Preenchendo CPF:", contrato['cpf'])
            self.act.forcar_clique_stale_element(loc_cep, self.by.XPATH, pause=0.1)
            self.act.enviar_texto_intervalado(
                loc_cep, contrato['cpf'], self.by.XPATH, delay=0.04)
        except TimeoutException:
            print('Campo já preenchido')
        except InvalidElementStateException:
            print('Campo já preenchido')

    @staticmethod
    def __separar_rua_endereco(rua):
        for i, char in enumerate(rua):
            if is_number(char):
                rua = rua[0: i]
        return rua.strip()


class PanFormInsercaoDadosBancarios(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 2

    def selecionar_ordem_de_pagto(self, contrato: dict):
        print("Ordem de pagto.")

        loc_cartao = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_cbCartBen_CAMPO"]'
        self.act.select_drop_down(loc_cartao, 'S', self.by.XPATH)

        self.__modal_meio_liberacao(contrato)

    def select_tipo_conta(self, tipo_conta: str):
        loc_tipo_conta = '//*[@id="ctl00_Cph_ucP_JN_JpLib_cbTpCtLib_CAMPO"]'
        print("Selecionando tipo da conta: ", tipo_conta)
        self.act.select_drop_down(loc_tipo_conta, tipo_conta, self.by.XPATH)
        self.act.press_TAB(loc_tipo_conta, self.by.XPATH)

    def campo_beneficio(self, contrato: dict):
        loc_beneficio = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtBen_CAMPO"]'
        if self.act.obter_valor(loc_beneficio, self.by.XPATH) == '':
            self.act.forcar_clique_stale_element(loc_beneficio, self.by.XPATH, pause=0.1)
            print(contrato['especieBeneficio'])
            self.act.enviar_texto_intervalado(
                loc_beneficio, contrato['especieBeneficio'], self.by.XPATH, delay=0.01)
            self.act.forcar_clique_stale_element(loc_beneficio, self.by.XPATH, pause=0.1)

    def select_uf_beneficio(self, contrato: dict):
        loc_uf_ben = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_cbUFBen_CAMPO"]'
        print("Preenchendo UF do Benefício", loc_uf_ben)
        self.act.select_drop_down(loc_uf_ben, contrato['uf'], self.by.XPATH)

    def campo_n_banco(self, contrato: dict):
        loc_n_banco = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtBncAvb_CAMPO"]'

        print("Preenchendo Nº do Banco", contrato['numeroBanco'])
        self.act.forcar_clique_stale_element(loc_n_banco, self.by.XPATH, pause=0.1)
        self.act.press_backspace(loc_n_banco, 10, self.by.XPATH)
        self.act.enviar_texto_intervalado(loc_n_banco, str(contrato['numeroBanco']),
                                          self.by.XPATH, clear=False, delay=0.6)
        loc_loading = '//*[@id="ctl00_Image2"]'
        self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

        self.act.press_enter(loc_n_banco, self.by.XPATH)

    def campo_agencia(self, contrato: dict):
        try:
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            loc_agencia = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtAgAvb_CAMPO"]'

            print("Preenchendo Nº da Agência:", contrato['agencia'])
            self.act.forcar_clique_stale_element(loc_agencia, self.by.XPATH, pause=0.1)

            sleep(0.5)
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.press_backspace(loc_agencia, 10, self.by.XPATH, end=True)
            self.act.enviar_texto_intervalado(loc_agencia, str(contrato['agencia']),
                                              self.by.XPATH, clear=False, delay=0.6)
            sleep(0.2)
            self.act.press_enter(loc_agencia, self.by.XPATH)
        except InvalidElementStateException:
            print("Campo 'dígito' não precisa ser preenchido.")

    def digito_agencia(self, contrato: dict):
        try:
            loc_dv_ag = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtDvAgAvb_CAMPO"]'
            print("Preenchendo Dígito da Agência:", contrato['digitoAgencia'])
            self.act.forcar_clique_stale_element(loc_dv_ag, self.by.XPATH, pause=0.1)

            sleep(0.5)
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.press_backspace(loc_dv_ag, 3, self.by.XPATH)
            self.act.enviar_texto_intervalado(loc_dv_ag, str(contrato['digitoAgencia']),
                                              self.by.XPATH, clear=False, delay=0.5)
        except InvalidElementStateException:
            print("Campo 'dígito' não precisa ser preenchido.")

    def n_conta_corrente(self, contrato: dict):
        loc_cc = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtCtAvb_CAMPO"]'
        print("Preenchendo Nº Conta Corrente:", contrato['numeroConta'])
        self.act.forcar_clique_stale_element(loc_cc, self.by.XPATH, pause=0.1)
        sleep(0.5)
        loc_loading = '//*[@id="ctl00_Image2"]'
        self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

        self.act.press_backspace(loc_cc, 12, self.by.XPATH, delay=0.05, end=True)
        self.act.enviar_texto_intervalado(loc_cc, str(contrato['numeroConta']),
                                          self.by.XPATH, clear=False)
        self.act.forcar_clique_stale_element(loc_cc, self.by.XPATH, pause=0.1)

    def dv_conta_corrente(self, contrato: dict):
        try:
            loc_dv_cc = '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtDvCtAvb_CAMPO"]'
            print("Preenchendo Dígito da Conta:", contrato['digitoConta'])
            self.act.forcar_clique_stale_element(loc_dv_cc, self.by.XPATH, pause=0.1)

            sleep(0.5)
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.press_backspace(loc_dv_cc, 3, self.by.XPATH)
            self.act.enviar_texto_intervalado(
                loc_dv_cc, str(contrato['digitoConta']),
                self.by.XPATH, clear=False, delay=0.5
            )
        except InvalidElementStateException:
            print("Campo 'dígito' não precisa ser preenchido.")

    def __modal_meio_liberacao(self, contrato, t=1):
        """
        Modal aberto no caso de o meio de liberação do empréstimo
        for por meio de Ordem de Pagto.
        :type contrato: dict
        :type t: int
        :return: None
        """
        print(f"Selecionando agência para pagamento. Tentativa={t}")
        loc_liberacao: str = '//*[@id="ctl00_Cph_ucP_JN_JpLib_cbLib_CAMPO"]'

        self.act.hover_e_clique(loc_liberacao, self.by.XPATH)
        self.act.select_drop_down(loc_liberacao, '164', self.by.XPATH)

        id_frame_agencias: str = '//*[@id="ctl00_Cph_ucP_ppBnc_frameAjuda"]'
        self.act.trocar_frame_seletor(id_frame_agencias, self.metodo.XPATH)

        print("Código da agência:", contrato['agencia'])
        loc_input: str = '//*[@id="ctl00_cph_E_TXTPESC_CAMPO"]'
        self.act.enviar_texto(loc_input, contrato['agencia'], self.by.XPATH)

        print("Pesquisando...")
        loc_btn = '//*[@id="BB_Pesq_txt"]'
        self.act.hover_e_clique(loc_btn, self.by.XPATH)
        loc_ausente: str = '//*[@id="ctl00_cph_GR_Resolt"]/tbody/tr/td'
        sleep(4)
        erro = self.act.obter_texto(loc_ausente, self.metodo.XPATH)
        print(erro)
        if similaridade('Nenhum(a) Agência foi encontrado(a)', erro) > 85:
            dados: dict = {'erro': r'O atributo obrigatório Agência não foi informado',
                           'mensagem': 'Conferir dados do contrato',
                           'observacao': 'Sistema Pan não encontra agência para OP'}
            self.uconecte.atualizar_contrato(
                contrato['codigoContrato'], dados
            )
            raise Exception("Agencia não encontrada para ordem de pagto.")

        print("Selecionar agência")
        loc_link_ag: str = '//*[@id="ctl00_cph_GR_Resolt_ctl02_lnkCodigo"]'
        self.act.hover_e_clique(loc_link_ag, self.by.XPATH)


class PanFormFinalizarInsercao(AutoGUI):
    url_assinatura = ('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb'
                      '/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 2

    def campo_cpf_operador(self):
        print("Preenchendo CPF do operador")
        loc_cpf_op = '//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]'

        if self.act.obter_texto(loc_cpf_op, self.by.XPATH) == '':
            #self.act.forcar_clique_stale_element(loc_cpf_op, self.by.XPATH, pause=0.01)
            loc_loading = '//*[@id="ctl00_Image2"]'
            self.act.esta_presente_recursivo(loc_loading, self.by.XPATH, max_rec=20)

            self.act.enviar_texto_intervalado(
                loc_cpf_op, '060.506.946-80', self.by.XPATH, delay=0.3, clear=False)
        else:
            self.act.enviar_texto_intervalado(
                loc_cpf_op, '060.506.946-80', self.by.XPATH, delay=0.3, clear=True)

    def apagar_cpf_operador(self):
        print("Apagando CPF do operador")
        loc_cpf_op = '//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]'
        self.act.press_backspace(loc_cpf_op, 16, self.by.XPATH)

    def botao_salvar_proposta(self, recr=1) -> bool:
        print("Salvando proposta.")
        try:
            loc_salvar = '//*[@id="btnGravar_txt"]'
            self.act.forcar_clique_stale_element(loc_salvar, self.by.XPATH, pause=2)
            return True
        except TimeoutException:
            return False

    def aprovar_proposta(self, recr=1) -> bool:
        print("Aprovando proposta...")
        try:
            loc_salvar = '//*[@id="BBApr_txt"]'
            self.act.forcar_clique_stale_element(loc_salvar, self.by.XPATH, pause=2)
            return True
        except TimeoutException:
            return False

    def confirmar_formalizacao_digital_tela(self):
        loc_formalizar_digital =  '//*[@id="btnConfirmar_txt"]'
        self.act.clicar_elemento(loc_formalizar_digital, self.by.XPATH)

    def concluir_negociacao(self):
        loc_botao_negociacao =  '//*[@id="btnConcluirNegociacao"]'
        self.act.clicar_elemento(loc_botao_negociacao, self.by.XPATH)

    def modal_divergencia(self, contrato):
        """
        Lida com o modal que pode ocorrer logo após o salvar a proposta.
        :type contrato: dict
        """
        loc_divergencia = '//*[contains(text(), "Diverg")]'
        if self.act.esta_presente(loc_divergencia, self.by.XPATH):
            print("Divergência Encontrada.")

            erro = "Dados divergentes entre Digitação e Consulta DataPrev"
            tratar_mensagens_sistema(self.act, erro, contrato)

    def confirmar_modal(self, rec: int = 1):
        try:
            print("Confirmando inserção.")
            loc_botao_confirmar = '//*[@id="btnConfirmar_txt"]'
            self.act.hover_e_clique(loc_botao_confirmar, self.by.XPATH, pause=3)
        except TimeoutException:
            if rec < 3:
                sleep(1)
                print("Tentando clicar novamente")
                return self.confirmar_modal(rec=rec + 1)

    def extrair_ade(self) -> str:
        print("Buscando ADE.")
        numero_ade = ""

        if self.act.verificar_existencia_alerta():
            texto_alerta = self.act.obter_texto_alerta()
            numero_ade = re.search(r'\d+', texto_alerta).group()
            self.act.manusear_alerta()
            print("ADE encontrada: ", numero_ade)

        return numero_ade

    def extrair_ade_tabela(self) -> str:
        print("Buscando ADE.")
        numero_ade = ""
        loc_ade = '//*[@id="gridPropostaEmprestimo"]/tbody/tr/td[2]/a'
        numero_ade = self.act.obter_texto(loc_ade,self.by.XPATH)

        print("ADE encontrada: ", numero_ade)

        return numero_ade

    def extrair_ade_frame(self) -> str:
        print("Buscando ADE no FRAME.")

        loc_frame_modal: str = 'framePopUp'
        self.act.trocar_frame_referencia(loc_frame_modal)

        numero_ade = ""
        loc_ade = '//*[@id="lblPropostas"]'
        numero_ade = self.act.obter_texto(loc_ade,self.by.XPATH).replace(";","").strip()

        print("ADE encontrada no Frame: ", numero_ade)

        return numero_ade

    def confirmar_formalizacao_digital(self):
        # Formalização da inserção - Digital
        print("Selecionando tipo de formalizaçao da proposta - Digital.")
        loc_radio_formalizar_digital = '//*[@id="ctl00_Cph_ctl00_ctl00_rbfDigital"]'
        self.act.forcar_clique_stale_element(loc_radio_formalizar_digital, self.by.XPATH)

        loc_formalizar = '//*[@id="btnConfirmar_txt"]'
        self.act.hover_e_clique(loc_formalizar, self.by.XPATH, pause=2)


def verificar_alertas(act: object, contrato: dict):
    """
    :param act: instância da classe SeleniumtActions
    :param contrato: dados do contrato
    """
    sleep(1)
    if act.verificar_existencia_alerta():
        texto_alerta: str = act.obter_texto_alerta()
        print("Alerta encontrado: ", texto_alerta)
        tratar_mensagens_sistema(act, texto_alerta, contrato)


def tratar_mensagens_sistema(act: object, texto: str, contrato: dict, driver=None) -> bool:
    """
    Utiliza um dict de mensagens, retornado pela função <mensagens_alertas>,
    para decidir qual tratativa dar ao andamento do contrato, com base na comparação
    do texto do alerta e os textos contidos nas mensagens retornadas.
    :param act: instância da classe SeleniumtActions
    :param texto: texto de erro do sistema
    :param contrato: dados do contrato
    :raise: Exception(texto_erro)
    """
    from sites.baseRobos.core.uconecte import Uconecte
    uconecte: Uconecte = Uconecte()

    if not act:  # TODO: REFATORAR GAMBIARRA 28/05
        act = AutoGUI.act_factory(driver)

    print("Comparando textos de erro...")

    # Mensagens pré-definidas e respectivas tratativas
    mensagens: dict = mensagens_alertas()

    try:
        act.manusear_alerta('aceitar')
    except UnexpectedAlertPresentException:
        print("Alerta não foi aberto.")
    except NoAlertPresentException:
        print("Alerta não foi aberto.")

    sleep(1)

    # Comparando a mensagem do alerta com as mensagens pré-definidas
    for infos in mensagens:
        comp_re: bool = bool(re.search(infos['texto'], texto))
        comp_in: bool = texto in infos['texto']
        comp_levs_dist: int = similaridade(texto, infos['texto']) >= 80

        if comp_in or comp_re or comp_levs_dist:

            if 'atualizar' in infos['tratamento']:
                raise AtualizarException(infos)

            if 'aceitar' in infos['tratamento']:
                print("Seguir inserção")
                return True

            if 'pular' in infos['tratamento']:
                print("Pular")
                raise Exception(texto)

            if 'aguardar_novo_login' in infos['tratamento']:
                sleep(600)
                print('Aguardando 10 minutos pois alguém criou nova sessão')
                raise Exception(texto)

            if 'preencher_cpf_operador' in infos['tratamento']:
                print("Preenchendo cpf operador novamente")
                return 'preencher_cpf'


def filtrar_tipo_conta(tipo_conta: str) -> str:
    """
    Recebe o nome por extenso do tipo de conta que consta no contrato
    (para liberação do empréstimo). Retorna o código relativo ao atributo
    <value> do menu select correspondente ao tipo de conta escolhido pelo cliente.
    """
    print("Tipo da conta", tipo_conta)

    if 'corrente' in tipo_conta:
        return '01'
    elif 'poupan' in tipo_conta:
        return '02'
    elif 'salario' in tipo_conta or 'salário' in tipo_conta:
        return '03'
    elif 'ordem' in tipo_conta.lower():
        return ''


class AtualizarException(Exception):
    def __init__(self, message: dict):
        super().__init__(AtualizarException)
        self.message: dict = message

    def __repr__(self):
        return f"{self.message}"
