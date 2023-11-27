import sys
sys.path.append('../')

import re, os, pdb
import requests
import datetime

from time import sleep
from selenium import webdriver
from selenium.webdriver import Chrome
from sites.baseRobos.core.uconecte import Uconecte
from sites.core.captcha import TwoCaptcha
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from sites.core.selenium_helper import SeleniumHelper
from selenium.webdriver.chrome.options import Options
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.helpers import definir_nome_robo
from selenium.webdriver.common.action_chains import ActionChains
from sites.baseRobos.core.helpers import (
    formatar_cpf, formatar_porcentagem,
    identificar_erro_robo, countdown
)
from selenium.common.exceptions import (
    NoAlertPresentException, TimeoutException,
    UnexpectedAlertPresentException, ElementClickInterceptedException
)
from selenium.webdriver.common.by import By
from sites.baseRobos.manager import Manager
from sites.baseRobos.data_handler import DataHandler
import PATHS
from sites.bradesco.BradescoConsultaRefinDados import BradescoConsultaRefinDados
from typing import List
from sites.baseRobos.core.DebugTools import DebugTools
from sites.bradesco.auxiliares import identificar_erros_sessao, ErroSessaoException
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from dados.database.queries.query_dados_robos import query_login_pass_robo

import shutil

dbg: DebugTools = DebugTools(debugging=False)
HORARIO_COMERCIAL = 7, 21


class Bradesco:

    id_fila_sincronizar = 31
    id_fila_refin = 12
    driver: Chrome

    def __init__(self):
        self.iniciar_chrome()
        self.convenios_gov = {"PR": ("0510-GOVERNO PARANA - PR", 1), "PB": ("N427-GOVERNO PARAÍBA - PB", 4),
                              "BA": ("N436-GOVERNO BAHIA - BA", 7)}
        self.id_banco = 2
        self.id_robo = 12
        self.usuario = 'MARCELO@MCA'

        self.refinanciamentos = None
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"
        self.url = "https://www.bradescopromotoranet.com.br/{}"

        self.uconecte = Uconecte(self.id_banco)
        self.uconecte.consulta_refin_banco = "Bradesco"
        self.selenium = SeleniumHelper(self.driver)
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.act = SeleniumActions(self.driver)
        self.act.time_out = 2
        self.fk_idPerfil_anterior = ''
        self.captcha_invalido = False
        self.erro_convenio = False
        self.completou = False
        self.count_captcha = 0
        self.log = DataHandler()
        self.dados: BradescoConsultaRefinDados = BradescoConsultaRefinDados()

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls):
        run = Bradesco()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.login_sistema()
        while True:
            self.consultar_refinanciamentos(fila="refinanciamentos")
            self.consultar_refinanciamentos(fila="potenciais")
            self.sincroniza_contratos_andamento()
            sleep(10)

    def iniciar_chrome(self):
        """
        Configura as opções do webdriver para ignorar erros ssl e para
        utilizar um perfil personalizado. Inicializa um objeto webdriver.Chrome
        com o caminho do chromedriver.exe e com as opções configuradas e o atribui a
        :var self.driver.
        :return: void.
        """
        chrome_user = PATHS.chrome_user("Bradesco")
        options = Options()
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('log-level=3')
        options.add_argument(chrome_user)

        try:
            #pdb.set_trace()
            pasta = chrome_user.split('=')[1]
            shutil.rmtree(pasta)
        except:
            pass

        Manager.criar_pasta_usuario_chrome(chrome_user)

        self.driver = webdriver.Chrome(
            #executable_path=PATHS.driver_path(),
            options=options)

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def login_sistema(self):
        """
        Direciona o ChromeWebDriver para a URL do banco Bradesco. Caso o usuário
        não esteja logado, esc
        """
        
        self.driver.get('https://www.bradescopromotoranet.com.br/')

        if self.selenium.buscar_quantidade_elemento("#cphBodyMain_cphBody_txtLogin") == 0:
            print("Usuário já está logado, pulando etapa de login...")
            return

        dados_login = query_login_pass_robo(self.id_robo, self.usuario)

        self.selenium.atribuir_valor_campo_driver('#cphBodyMain_cphBody_txtLogin', self.usuario)
        sleep(1)
        self.selenium.atribuir_valor_campo_driver('#cphBodyMain_cphBody_txtSenha', dados_login['senha'])

        self.selenium.clicar_elemento_driver('#cphBodyMain_cphBody_btnEntrar')
        sleep(1)

        try:
            os.remove("/home/gustavo/Desktop/automacao-python/sites/core/captchas/TESTE.jpg")
        except:
            pass
            
    def verifica_horario_comercial(self):
        data_hora = datetime.datetime.now()
        if data_hora.hour > 20:
            print('Fora do horário comercial... Inciando o processo para próxima manhã (7:00)...')
            self.driver.close()
            countdown(36000, 3600, 'Aguardando...')
            self.__init__()
            self.main()

    def sincroniza_contratos_andamento(self):

        self.menu_relatorio_consulta()
        contratos_a_atualizar = self.busca_contratos_em_andamento()
        for contrato in contratos_a_atualizar[1:]:
            try:
                self.log.api_iniciar_log_robo(
                    idRobo=self.id_fila_sincronizar,
                    idSolicitacao=contrato[2]
                )
                print(f'Pesquisando contrato {contrato[2]}...')  # CONTRATO[2] É O CÓDIGO DO CONTRATO
                self.aguardar_loading(tipo='sincronizacao')
                dados = self.pesquisa_detalhes_contrato(contrato[0], contrato[1], contrato[2])
                # CONTRATO [0] É A ADE // CONTRATO[1] É O CPF
                if dados:
                    self.atualiza_contrato_web_admin(contrato[2], dados)
                    self.menu_relatorio_consulta()
                    self.log.api_registrar_log_robo(
                        log=f"Contrato {contrato[2]} sincronizado",
                        status=2
                    )
            except Exception as e:
                dbg.exception(e)
                if identificar_erros_sessao(str(e)):
                    self.login_sistema()
                self.log.api_registrar_log_robo(log=f"ERRO: {str(e)}",status=0)
        self.dados.atualizar_sincronizazao()
        self.completou = True

    # self.driver.close()
    # countdown(3600,10,'Sincronização ok, horário de término atualizado... Aguardando 2 horas...')
    # self.__init__()
    # self.main()

    def menu_relatorio_consulta(self):
        self.driver.get("https://www.bradescopromotoranet.com.br/forms/admin/Esteira/Esteira.aspx")

    def busca_contratos_em_andamento(self):
        request_contratos_a_consultar = requests.get('https://emprestimofacil.co/web_admin/api/v1/contratos/em'
                                                     '-analise/banco-bradesco-promotora/?key'
                                                     '=f689f1e12a0399fba803cb2365fc362f')

        if request_contratos_a_consultar.status_code != 200:
            input('Banco Bradesco Promotora Error - Não foi possível buscar os contratos')
        self.uconecte.atualizar_status_robo(self.id_robo)
        return request_contratos_a_consultar.json()

    def pesquisa_detalhes_contrato(self, ade, cpf, codigo_con):

        self.selenium.clicar_elemento_driver(
            "#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_lblCountBackOffice")
        self.selenium.atribuir_valor_campo_jquery("#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1"
                                                  "_ucConsPendCorrespNetCerto_ddlEtapas", "0")

        self.selenium.atribuir_valor_campo_jquery(
            "#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_ucConsPendCorrespNetCerto_txtContrato", ade)
        self.selenium.clicar_elemento_driver(
            "#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_ucConsPendCorrespNetCerto_btnPesquisar")
        sleep(5)
        status_proposta_banco = self.selenium.verificar_texto_campo_jquery(
            '#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_ucConsPendCorrespNetCerto'
            '_gvPentendeCorresp_lblStNetcerto_0').strip()
        self.selenium.clicar_elemento_driver("#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1"
                                             "_ucConsPendCorrespNetCerto_gvPentendeCorresp_btnHistorico_0")
        sleep(5)

        proposta_encontrada = self.driver.execute_script("""var resultado = $('#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_ucConsPendCorrespNetCerto_gvPentendeCorresp')
        																				.children('tbody').children('tr')
        																				.children('td')
        																				.prevObject[0].innerText; 
        															return resultado""")

        if proposta_encontrada != 'NÃO EXISTEM DADOS PARA ESSA CONSULTA.':

            observacao_completa = self.driver.execute_script("""var resultado = [];	
        																var anchor = $('#cphBodyMain_cphBody_cphBody_ucPendenteCorrespondente1_ucConsPendCorrespNetCerto_ucHistoricoProposta1_gvHistorico')
        																				.children('tbody')
        																				.children('tr')
        																				.children('td');
        																				for(i=0;i<3;i++){resultado.push(anchor[i].innerHTML)} 
        																return resultado""")

            if 'PENDENTE DE DOCUMENTAÇÃO' in observacao_completa:
                status_proposta_banco += ' - PENDENTE DE ENVIO DE DOCUMENTACAO'
            if 'ENVIADO' in observacao_completa:
                status_proposta_banco += ' - AGUARDANDO APROVACAO'
            if 'ENVIAR SENHA' in observacao_completa:
                status_proposta_banco += ' - PEDIDO DE NOVA SENHA'

            observacao_detalhada_banco = "\n\n" + observacao_completa[1] + ' ' + observacao_completa[2]

            print('Salvando observações detalhadas...')

            dados = {
                "key": "f689f1e12a0399fba803cb2365fc362f",
                "statusPropostaBanco": status_proposta_banco,
                "observacaoDetalhadaBanco": observacao_detalhada_banco,
                "codigoCon": codigo_con,
                "ade": ade
            }
        else:
            dados = False

        return dados

    def menu_refinanciamento_fed(self):
        self.driver.get(r"https://www.bradescopromotoranet.com.br/Forms/Proposta/CadastroProposta.aspx?prop=uqnWIp"
                        r"%2fhlKc%3d&prod=QPTSe18vz14%3d")
        self.aguardar_loading()
        self.tratar_erros_modal_consulta()

    def menu_refinanciamento_siape(self):
        self.driver.get(r"https://www.bradescopromotoranet.com.br/Forms/Proposta/CadastroProposta.aspx?prop"
                        r"=1AK8KM4L4X8%3d&prod=QPTSe18vz14%3d")
        self.aguardar_loading()
        self.tratar_erros_modal_consulta()

    def menu_refinanciamento_gov(self):
        self.driver.get(r"https://www.bradescopromotoranet.com.br/Forms/Proposta/CadastroProposta.aspx?prop"
                        r"=tlhjQ2vON6Y%3d&prod=QPTSe18vz14%3d")
        self.aguardar_loading()
        self.tratar_erros_modal_consulta()

    def menu_refinanciamento_inss(self):
        self.driver.get(
            r"https://www.bradescopromotoranet.com.br/Forms/Proposta/CadastroProposta.aspx?prop=VPUjo2IpaA0%3d&prod"
            r"=QPTSe18vz14%3d")
        self.aguardar_loading()
        self.tratar_erros_modal_consulta()

    def buscar_solicitacoes(self):
        solicitacoes: List[dict] = self.dados.buscar_solicatacoes_refinanciamento()

        if not solicitacoes:
            print("Aguardando fila solicitações...")
            sleep(120)

        return solicitacoes

    def consultar_refinanciamentos(self, fila="refinanciamentos"):
        solicitacoes: List[dict] = []

        if fila == "refinanciamentos":
            solicitacoes = self.buscar_solicitacoes()

        elif fila == "potenciais":
            solicitacoes = self.dados.uconecte.buscar_pessoas_potenciais()

        for solicitacao in solicitacoes:
            if solicitacao["sigla"] == "RJ":
                print("Sigla RJ, pulando...")
                continue
            if fila == "refinanciamentos":
                self.log.api_iniciar_log_robo(
                    idRobo=self.id_fila_refin,
                    idSolicitacao=solicitacao['idSolicitacao']
                )
            definir_nome_robo('Bradesco - Consulta Refinanciamento')
            self.refinanciamentos = []

            try:
                print(f"Trabalhando na solicitação {solicitacao}")
                definir_nome_robo('Bradesco - Consulta Refinanciamento')

                if solicitacao['fk_idPerfil'] == '1':
                    if self.fk_idPerfil_anterior != '1' or self.erro_convenio or self.completou:
                        self.completou = False
                        self.erro_convenio = False
                        self.menu_refinanciamento_gov()
                    self.consultar_refinanciamento(solicitacao)
                elif solicitacao['fk_idPerfil'] == '2':
                    if self.fk_idPerfil_anterior != '2' or self.erro_convenio or self.completou:
                        self.completou = False
                        self.erro_convenio = False
                        self.menu_refinanciamento_siape()
                    self.consultar_refinanciamento(solicitacao)
                elif solicitacao['fk_idPerfil'] == '8':
                    if self.fk_idPerfil_anterior != '8' or self.erro_convenio or self.completou:
                        self.completou = False
                        self.erro_convenio = False
                        self.menu_refinanciamento_fed()
                    self.consultar_refinanciamento(solicitacao)
                elif solicitacao['fk_idPerfil'] == '5':
                    if self.fk_idPerfil_anterior != '4' or self.erro_convenio or self.completou:
                        if self.fk_idPerfil_anterior != '5' or self.erro_convenio or self.completou:
                            self.completou = False
                            self.erro_convenio = False
                            self.menu_refinanciamento_inss()
                    self.consultar_refinanciamento(solicitacao, True)
                elif solicitacao['fk_idPerfil'] == '4':
                    if self.fk_idPerfil_anterior != '5' or self.erro_convenio or self.completou:
                        if self.fk_idPerfil_anterior != '4' or self.erro_convenio  or self.completou:
                            self.completou = False
                            self.erro_convenio = False
                            self.menu_refinanciamento_inss()
                    self.consultar_refinanciamento(solicitacao, True)
                else:
                    print(f'O robô não está configurado para calcular o refinanciamento do fk_idPerfil'
                          f' {solicitacao["fk_idPerfil"]}, pulando solicitação...')
                    self.log.api_registrar_log_robo(
                        log=(f'O robô não está configurado para calcular o refinanciamento '
                             f'do fk_idPerfil {solicitacao["fk_idPerfil"]}'),
                        status=2
                    )
                    continue

                print(self.refinanciamentos)
                print("Calculando Refinanciamentos encontrados!")
                print(f"Finalizando consulta.")

                ## Atualizar histórico com consulta realizada com SUCESSO
                self.dados.atualizar_dados_consulta(solicitacao, self.refinanciamentos)
                self.log.api_registrar_log_robo(  # log: consulta finalizada. status sucesso
                    log=f'Consulta realizada com sucesso.',
                    status=2
                )
            except NotFoundResultException as e:
                ## Atualizar histórico com NÃO POSSUI DADOS NO SISTEMA
                print(f'Não possui contratos. Mensagem Sistema: {e.message}')
                self.dados.atualizar_impossibilidade_consulta(solicitacao, e.message)
                self.log.api_registrar_log_robo(  # log: sem dados no sistema. status sucesso
                    log=f'Não possui contratos. Mensagem Sistema: {e.message}',
                    status=2
                )
            except ErroSessaoException as e:
                print(e)
                self.login_sistema()
            except PularSolicitacaoException:
                continue
            except UnexpectedAlertPresentException:
                self.tratar_erros_alerta()
                continue
            except Exception as e:
                self.tratar_erros_alerta()
                dbg.exception(e)
                identificar_erro_robo()
                self.log.api_registrar_log_robo(log=f'ERRO: {e}', status=0) # log: erros críticos. status falha
                continue

    def consultar_refinanciamento(self, solicitacao, selector=False):

        self.preencher_dados_formulario_validacao(solicitacao, selector)
        self.preencher_dados_cliente(solicitacao)
        self.preencher_captcha(solicitacao)

        if solicitacao['fk_idPerfil'] == '5' or solicitacao['fk_idPerfil'] == '4':
            self.escolher_matricula(solicitacao)
            self.calcular_refinanciamentos_inss(solicitacao)
        else:
            self.calcular_refinanciamentos_gov(solicitacao)

    def preencher_dados_formulario_validacao(self, solicitacao, selector=False):

        item = "{} > span.ui-combobox > a > span.ui-button-icon.ui-icon.ui-icon-triangle-1-s"
        print('Verificando css.')

        if self.selenium.verificar_propriedade_css("#cphBodyMain_cphBody_cphBody_ucDadosValidacao_drpEmpresa > option",
                                                   "selected"):
            if selector:
                seletor_beneficio_escolhido = '#cphBodyMain_cphBody_cphBody_ucDadosValidacao_drpTipoBeneficio'
                if self.selenium.verificar_valor_campo_driver(seletor_beneficio_escolhido) == "0":
                    return

                sleep(2)
                seletor_select_empresa = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upEmpresa"
                self.selecionar_dados_validacao(item.format(seletor_select_empresa), 1)
                self.aguardar_loading()

                seletor_select_produto = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upProduto"
                self.selecionar_dados_validacao(item.format(seletor_select_produto), 3)
                self.aguardar_loading()

                #tentando fechar janela
                try:
                    sleep(2)
                    self.act.clicar_elemento('/html/body/div[16]/div[1]/button/span[1]', By.XPATH)
                except:
                    pass

                seletor_select_loja = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upLojas"
                self.selecionar_dados_validacao(item.format(seletor_select_loja), 1)
                self.aguardar_loading()

                seletor_select_filial = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upFilial"
                self.selecionar_dados_validacao(item.format(seletor_select_filial), 1)
                self.aguardar_loading()

                seletor_select_tipo_beneficio = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_pnlTipoBeneficio"
                self.selecionar_dados_validacao(item.format(seletor_select_tipo_beneficio), 1)
                self.aguardar_loading()
            else:
                if solicitacao['fk_idPerfil'] == "1":
                    selecionar = self.selecao_orgao(solicitacao)
                    seletor_select_convenio = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_pnlConvenio"
                    self.selecionar_dados_validacao(item.format(seletor_select_convenio), selecionar)
                    self.aguardar_loading()
                elif solicitacao['fk_idPerfil'] == "8":
                    seletor_select_convenio = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_pnlConvenio"
                    self.selecionar_dados_validacao(item.format(seletor_select_convenio), 2)
                    self.aguardar_loading()
                else:
                    seletor_select_convenio = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_pnlConvenio"
                    self.selecionar_dados_validacao(item.format(seletor_select_convenio), 1)
                    self.aguardar_loading()

                seletor_select_empresa = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upEmpresa"
                self.selecionar_dados_validacao(item.format(seletor_select_empresa), 1)
                self.aguardar_loading()

                seletor_select_produto = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upProduto"
                self.selecionar_dados_validacao(item.format(seletor_select_produto), 1)
                self.aguardar_loading()

                seletor_select_loja = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upLojas"
                self.selecionar_dados_validacao(item.format(seletor_select_loja), 1)
                self.aguardar_loading()

                seletor_select_filial = "#cphBodyMain_cphBody_cphBody_ucDadosValidacao_upFilial"
                self.selecionar_dados_validacao(item.format(seletor_select_filial), 1)
                self.aguardar_loading()

    def selecao_orgao(self, solicitacao):
        for sigla, conjunto in self.convenios_gov.items():
            if solicitacao['sigla'] == sigla:
                return conjunto[1]

    def preencher_dados_cliente(self, solicitacao):
        if solicitacao['fk_idPerfil'] == '1':
            seletor_cpf = '#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_txtCpf'
            self.selenium.atribuir_valor_campo_jquery(seletor_cpf, formatar_cpf(solicitacao['cpf']))
            self.aguardar_loading()

        elif solicitacao['fk_idPerfil'] == '8':
            seletor_cpf = '#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_txtCpf'
            self.selenium.atribuir_valor_campo_jquery(seletor_cpf, formatar_cpf(solicitacao['cpf']))
            self.aguardar_loading()

        elif solicitacao['fk_idPerfil'] == '2':
            seletor_cpf = "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtCpf"
            self.selenium.atribuir_valor_campo_driver(seletor_cpf, solicitacao['cpf'])
            self.aguardar_loading()

            texto_cpf = self.act.obter_valor(seletor_cpf)

            if texto_cpf == '':
                seletor_cpf = "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtCpf"
                self.selenium.atribuir_valor_campo_driver(seletor_cpf, solicitacao['cpf'])
                self.aguardar_loading()

            self.tratar_erros_alerta()

        elif solicitacao['fk_idPerfil'] == '5' or solicitacao['fk_idPerfil'] == '4':
            seletor_cpf = "#cphBodyMain_cphBody_cphBody_ucConsultaMargem_ucConsultaMargemRefin_txtCpf"
            self.selenium.atribuir_valor_campo_jquery(seletor_cpf, formatar_cpf(solicitacao['cpf']))
            self.aguardar_loading()

    def preencher_captcha(self, solicitacao):
        id_captcha = ''

        if solicitacao['fk_idPerfil'] == '4' and ((self.fk_idPerfil_anterior != '4'
                                                   and self.fk_idPerfil_anterior != '5') or self.captcha_invalido):
            self.act.clicar_elemento("#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha")
            sleep(1.5)
            loc_captcha_img = "#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha"
            loc_campo_catpcha = "#cphBodyMain_cphBody_cphBody_ucCaptcha_txtCaptcha"
            id_captcha, res_captcha = self.captcha.resolver_captcha_inss_bradesco(loc_captcha_img)
            self.selenium.atribuir_valor_campo_jquery(loc_campo_catpcha, res_captcha)
            self.aguardar_loading()
        elif solicitacao['fk_idPerfil'] == '5' and ((self.fk_idPerfil_anterior != '5' and
                                                     self.fk_idPerfil_anterior != '4') or self.captcha_invalido):
            self.act.clicar_elemento("#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha")
            sleep(1.5)
            loc_captcha_img = "#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha"
            loc_campo_catpcha = "#cphBodyMain_cphBody_cphBody_ucCaptcha_txtCaptcha"
            id_captcha, res_captcha = self.captcha.resolver_captcha_inss_bradesco(loc_captcha_img)
            self.selenium.atribuir_valor_campo_jquery(loc_campo_catpcha, res_captcha)
            self.aguardar_loading()
        elif solicitacao['fk_idPerfil'] != '4' and solicitacao['fk_idPerfil'] != '5':
            self.act.clicar_elemento("#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha")
            sleep(1.5)
            loc_captcha_img = "#cphBodyMain_cphBody_cphBody_ucCaptcha_captcha"
            loc_campo_catpcha = "#cphBodyMain_cphBody_cphBody_ucCaptcha_txtCaptcha"
            id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)
            self.selenium.atribuir_valor_campo_driver(loc_campo_catpcha, res_captcha)
            self.aguardar_loading()

        if solicitacao['fk_idPerfil'] == '2':
            self.driver.execute_script(
                f"""$('#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtDataNascimento').val('{solicitacao['dataNascimento']}')""")
            seletor_botao = "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_btnPesquisarMargemProposta"
            self.selenium.clicar_elemento_driver(seletor_botao)
            self.aguardar_loading()

        elif solicitacao['fk_idPerfil'] == '5' or solicitacao['fk_idPerfil'] == '4':

            seletor_botao = "#cphBodyMain_cphBody_cphBody_ucConsultaMargem_ucConsultaMargemRefin_btnPesquisarCpf"
            self.act.clicar_elemento(seletor_botao)

            if self.selenium.verificar_valor_campo_jquery("#cphBodyMain_cphBody_cphBody_ucConsultaMargem_ucConsultaMargemRefin_txtDataNascimento") == "":
                self.selenium.clicar_elemento_driver(seletor_botao)
            self.aguardar_loading()
        else:
            seletor_botao = "#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_btnPesquisarCpf"
            self.selenium.clicar_elemento_driver(seletor_botao)
            self.aguardar_loading()

        erro = ""
        try:
            erro = self.act.obter_texto('//*[@id="errorPageContent"]/div[2]/h1', By.XPATH)
        except:
            pass

        if('AVISO DE SISTEMA' in erro):
            self.act.clicar_elemento('//*[@id="errorPageContent"]/div[2]/p[2]/input', By.XPATH)
            pdb.set_trace()
            return


        try:
            self.fk_idPerfil_anterior = solicitacao['fk_idPerfil']
            self.captcha_invalido = False
            self.tratar_erros_modal_consulta()
            self.tratar_erros_alerta()
            self.count_captcha = 0
            print("Captcha Aprovado!")

            if 'id_catpcha' in vars():
                self.captcha.mudar_status_captcha(id_captcha, status='1')
        except CaptchaException:
            print('Captcha Reprovado!')
            self.captcha_invalido = True
            self.count_captcha += 1

            if self.count_captcha > 10:
                self.loga_again()

            if 'id_catpcha' in vars():
                self.captcha.mudar_status_captcha(id_captcha, status='2')
            return self.preencher_captcha(solicitacao)

    def tratar_erros_alerta(self):
        try:
            mensagem_erro = Alert(self.driver).text
        except NoAlertPresentException:
            return
        except Exception as e:
            dbg.exception(e)
            print(f"Erro ao buscar a mensagem de alert. {e}")
            return self.tratar_erros_alerta()

        print(f"Mensagem de erro: {mensagem_erro}")

        alert_regex = [
            {
                'erro': r"Favor verificar o preenchimento correto dos campos.",
                'Preenchimento': True
            }
        ]

        for mensagem_regex in alert_regex:
            regex = re.compile(mensagem_regex['erro'].lower())
            mensagem_encontrada = regex.search(mensagem_erro.lower())

            if not mensagem_encontrada:
                return

            Alert(self.driver).accept()

            if 'Preenchimento' in alert_regex:
                self.consultar_refinanciamentos()

            identificar_erros_sessao(mensagem_erro, throw=True)

    def tratar_erros_modal_consulta(self):
        try:
            from sites.baseRobos.core.data_helpers import similaridade
            if self.selenium.buscar_quantidade_elemento('.ui-dialog-content:visible') > 0:
                mensagem_erro = self.selenium.verificar_texto_campo_jquery('.ui-dialog-content:visible').strip()
            elif self.selenium.buscar_quantidade_elemento('#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_pnlModalPopUP > div.modalContainer > div') > 0:
                mensagem_erro = self.selenium.verificar_texto_campo_jquery('#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_lblMensagemBloqueio')
            else:
                return
        except TimeoutException:
            return

        print(f"Mensagem de erro: {mensagem_erro}")

        if mensagem_erro == "":
            return

        identificar_erros_sessao(mensagem_erro, throw=True)

        erros_regex = [
            {
                'erro': r"Não existem contratos deste cliente no convênio selecionado",
                'InfoNotFound': True
            }, {
                'erro': r"Não foram localizados dados para o CPF informado.",
                'InfoNotFound': True
            }, {
                'erro': r"Código de segurança inválido",
                'Captcha': True
            }, {
                'erro': r"Taxa não permitida por ser superior a taxa de referência ponderada",
                'PularCheckBox': True
            }, {
                'erro': r"Valor Solicitado não pode ser menor que o valor a refinanciar.",
                'PularCheckBox': True
            }, {
                'erro': r"Valor da parcela não pode ser inferior a",
                'PularCheckBox': True
            }, {
                'erro': r"- Valor da parcela não pode ser superior a",
                'PularCheckBox': True
            }, {
                'erro': r"Serviço para cálculo da simulação financeira indisponível",
                'aguardar': True,
                'PularCheckBox': True
            }, {
                'erro': r"Sessão Expirada",
                'Finalizar': True
            }, {
                'erro': r"Usuário não possui acesso à este convênio.",
                'ErrorConvenio': True
            }, {
                'erro': r"Favor verificar o preenchimento correto dos campos.",
                'InfoNotFound': True
            }, {
                'erro': r"CPF não localizado.",
                'InfoNotFound': True
            }, {
                'erro': r"CPF não cadastrado no SIAPE",
                'InfoNotFound': True
            }, {
                'erro': r"Indisponibilidade parcial ao acesso dos contratos. Tente novamente.",
                'PularSolicitacao': True
            }, {
                'erro': r"Não é possível efetuar a consulta ao PDC com os parâmetros informados. Dados do contrato "
                        r"não encontrados",
                'PularCheckBox': True
            }, {
                'erro': r'PORTABILIDADE OU REFINANCIAMENTO DE PORTABILIDADE COM MENOS DE 360 DIAS',
                'PortabilidadeError': True
            }, {
                'erro': r'Serviço indisponível.',
                'PularSolicitacao': True
            }, 
            # {
            #     'erro': r'Não foi possível exibir o simulador.',
            #     'PularSolicitacao': True
            # }, 
            {
                "erro": r"O prazo desta operação de REFIN deve ser de no mínimo",
                'PularCheckBox': True
            } , {
                "erro": r"não atende a politica do Banco",
                'PularCheckBox': True
            }, {
                "erro": r"Valor Solicitado não pode ser menor que o valor a refinanciar",
                'PularCheckBox': True
            }, {
                "erro": r"Valor liquido não atende a politica do banco",
                'PularCheckBox': True
            }
            , {
                "erro": r"não permitida por ser superior a taxa de referência ponderada",
                'PularCheckBox': True
            }, {
                "erro": r"Não foi possível exibir o simulador",
                'PularCheckBox': True
            }, {
                "erro": r"Não é possível efetuar a consulta ao PDC com os parâmetros informado",
                'PularCheckBox': True
            },
            {
                "erro" : r"vencimento do seu certificado",
                "Fechar" : True

            }

        ]

        
        for erro_regex in erros_regex:
            regex = re.compile(erro_regex['erro'])
            erro_encontrado = regex.search(mensagem_erro)

            similar = similaridade(erro_regex['erro'], mensagem_erro) > 90
            if not erro_encontrado and not similar:
                continue

            try:
                self.selenium.clicar_elemento('.ui-dialog-titlebar-close:visible')
            except ElementClickInterceptedException:
                self.selenium.clicar_elemento('.ui-dialog-titlebar-close:visible')

            if 'aguardar' in erro_regex:
                print('Aguardando 2 minutos...')
                sleep(120)

            if 'InfoNotFound' in erro_regex:
                try:
                    loc = '//*[@id="cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCancelar"]'
                    self.act.clicar_elemento(loc, By.XPATH)
                except TimeoutException:
                    print("Modal não precisou ser fechado")
                raise NotFoundResultException(message=mensagem_erro)
            elif 'Captcha' in erro_regex:
                raise CaptchaException(message=mensagem_erro)
            elif 'PularCheckBox' in erro_regex:
                raise PularCheckboxException(message=mensagem_erro)
            elif 'Finalizar' in erro_regex:
                raise Exception(mensagem_erro)
            elif 'ErrorConvenio' in erro_regex:
                self.erro_convenio = True
                print('Erro de Convenio, logando novamente...')
                self.loga_again()
            elif 'PularSolicitacao' in erro_regex:
                return
            elif 'SessaoExpirada' in erro_regex:
                self.main()
            elif 'PortabilidadeError' in erro_regex:
                print('Cancelando operação...')
                self.selenium.clicar_elemento('#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_btnDialogNo')
                self.aguardar_loading()
                raise PularCheckboxException(message=mensagem_erro)
            elif 'Fechar' in erro_regex:
                try: 
                    self.act.clicar_elemento('/html/body/div[1]/div[1]/button/span[1]', By.XPATH)
                except:
                    pass
                return

        raise Exception("Mensagem não encontrada...")

    def loga_again(self):
        self.selenium.clicar_elemento_driver("#cphBodyMain_ucMenu_rptMenu_upMenu_4")
        self.act.manusear_alerta(acao='aceitar')
        self.main()

    def escolher_matricula(self, solicitacao):
        seletor_matricula = "#cphBodyMain_cphBody_cphBody_ucConsultaMargem_ucConsultaMargemRefin_drpBeneficio"
        if self.selenium.buscar_quantidade_elemento(seletor_matricula) == 0:
            return
        matricula_selecionada = self.selenium.verificar_valor_campo_driver(seletor_matricula)
        if(str(solicitacao['matricula']) in matricula_selecionada):
            options_matricula = self.driver.find_element(By.CSS_SELECTOR,seletor_matricula + " option")
            if(self.selenium.buscar_quantidade_elemento(seletor_matricula) >= 1):
                for option in [options_matricula]:
                    if str(solicitacao['matricula']) in matricula_selecionada:
                        self.selenium.atribuir_valor_campo_jquery(seletor_matricula, option.text, change=True)
                        self.aguardar_loading()
                        return
        else:
            print("Matricula não foi encontrada, mude o valor selecionado!")
            raise NotFoundResultException(message="Matricula não encontrada!")                     

    def calcular_refinanciamentos_gov(self, solicitacao):
        if solicitacao['fk_idPerfil'] == '2' and self.selenium.verificar_propriedade_css(
                "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtValorMargemSIAPE", 'disabled'):
            #seletor_checkboxes = "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_gvMargens input"
            #checkboxes_refinanciamento = self.driver.find_element(By.CSS_SELECTOR,seletor_checkboxes)
            #checkboxes = list(map(lambda refin: f"#{refin.get_attribute('id')}", checkboxes_refinanciamento))

            seletor_checkboxes = "cphBodyMain_cphBody_cphBody_ucMargemSIAPE_gvMargens"

            try:
                checkboxes_refinanciamento = checkboxes = self.driver.find_element(By.ID,seletor_checkboxes).find_elements(By.TAG_NAME, "tr")
            except:
                checkboxes_refinanciamento = checkboxes = ""
                pass

            for checkbox in checkboxes:
                self.selenium.clicar_elemento_driver(checkbox)
                self.aguardar_loading()

                try:
                    self.tratar_erros_modal_consulta()
                    self.tratar_erros_alerta()
                except PularCheckboxException:
                    self.fechar_modal_simulador()
                    continue


                #seletor_checkboxes2 = "#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos input"
                seletor_checkboxes2 = "cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos"

                try:
                    checkboxes_refinanciamento2 = checkboxes2 = self.driver.find_element(By.ID,seletor_checkboxes2).find_elements(By.TAG_NAME, "tr")
                except:
                    checkboxes_refinanciamento2 = checkboxes2 = ""
                    pass

                if not checkboxes_refinanciamento2 :
                    print('XXXXXXXXXXXNão há matriculas vinculadas ao CPFXXXXXXXXXXXXX')
                    continue

                #checkboxes2 = list(map(lambda refin: f"#{refin.get_attribute('id')}", checkboxes_refinanciamento2))
                index_checkbox = 2
                count = 0

                for checkbox2 in checkboxes2:
                    if solicitacao['fk_idPerfil'] == '2':
                        motivo = self.selenium.verificar_texto_campo_jquery(
                            f'#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos_lblMotivo_{count}')
                        if motivo.find('Este contrato não possui') != -1 or motivo.find('margem negativa') != -1 or \
                                motivo.find("refinanciamento") != -1:
                            count += 1
                            continue

                    self.selenium.clicar_elemento_driver(checkbox2)
                    valor_parcela = self.selenium.verificar_texto_campo_jquery(
                        f"#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos > tbody > "
                        f"tr:nth-child({str(index_checkbox)}) > td:nth-child(5)")
                    index_checkbox += 1
                    self.selenium.clicar_elemento_driver(
                        "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_btnSimulador")
                    self.aguardar_loading()

                    try:
                        self.tratar_erros_modal_consulta()
                    except PularCheckboxException:
                        self.fechar_modal_simulador()
                        count += 1
                        continue

                    self.selenium.atribuir_valor_campo_driver(
                        "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_txtValorParcela", valor_parcela)
                    self.selenium.clicar_elemento_driver(
                        "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular")

                    if self.selenium.buscar_quantidade_elemento(
                            "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_txtDataPrimVct") == 0:
                        self.selenium.clicar_elemento(
                            "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular")

                    self.aguardar_loading()

                    try:
                        self.tratar_erros_modal_consulta()
                        self.tratar_erros_alerta()
                    except PularCheckboxException:
                        self.fechar_modal_simulador()
                        count += 1
                        continue

                    seletor_linhas_taxas = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_gvSimulacao" \
                                           " tr"
                    linhas_taxa = self.driver.find_element(By.CSS_SELECTOR,seletor_linhas_taxas)

                    if linhas_taxa[1].get_attribute('style').find('red') != -1 or not self.validar_taxa(linhas_taxa[1], solicitacao):
                        print("Refinanciamento foi calculado, mas não está disponível.")
                        self.fechar_modal_simulador()
                        count += 1
                        continue

                    seletor_prazo = '#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_drpPrazo'
                    prazo = self.selenium.verificar_valor_campo_driver(seletor_prazo)

                    valores = linhas_taxa[1].text.split(' ')

                    saldo_devedor = valores[2].split('\n')[1]
                    valor_liberado = valores[3]

                    if int(self.formatar_valor(valor_liberado)) <= int(self.formatar_valor(valor_parcela)):
                        print('Refinanciamento não pôde ser calculado pois o valor liberado é inferior ao valor da '
                              'parcela!')
                        self.fechar_modal_simulador()
                        count += 1
                        continue

                    self.refinanciamentos.append({
                        'saldoDevedor': saldo_devedor,
                        'valorLiberado': valor_liberado,
                        'prazo': prazo,
                        'valorParcela': valor_parcela
                    })

                    self.fechar_modal_simulador()
                    count += 1
        else:
            if solicitacao['fk_idPerfil'] == '2' and not self.selenium.verificar_propriedade_css(
                    "#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtValorMargemSIAPE", 'disabled'):
                self.selenium.atribuir_valor_campo_driver('#cphBodyMain_cphBody_cphBody_ucMargemSIAPE_txtValorMargem'
                                                          'SIAPE', '1')

            #seletor_checkboxes = "#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos input"
            
            seletor_checkboxes = "cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos"
            
            try:
                checkboxes_refinanciamento = checkboxes = self.driver.find_element(By.ID,seletor_checkboxes).find_elements(By.TAG_NAME, "tr")
            except:
                checkboxes_refinanciamento = checkboxes = ""
                pass

            if not checkboxes_refinanciamento :
                print('XXXXXXXXXXXNão há matriculas cinculadas ao CPFXXXXXXXXXXXXX')
                return

            # checkboxes_refinanciamento = self.driver.find_element(By.CSS_SELECTOR,seletor_checkboxes)
            # checkboxes = list(map(lambda refin: f"#{refin.get_attribute('id')}", checkboxes_refinanciamento))
            index_checkbox = 2
            count = 0

            for checkbox in checkboxes:
                if solicitacao['fk_idPerfil'] == '2':
                    motivo = self.selenium.verificar_texto_campo_jquery(
                        f'#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos_lblMotivo_{count}')
                    if motivo.find('Este contrato não possui') != -1 or motivo.find('margem negativa') != -1 or \
                            motivo.find("refinanciamento") != -1:
                        count += 1
                        continue

                self.selenium.clicar_elemento_driver(checkbox)
                valor_parcela = self.selenium.verificar_texto_campo_jquery(
                    f"#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos > tbody > "
                    f"tr:nth-child({str(index_checkbox)}) > td:nth-child(5)")
                index_checkbox += 1
                self.selenium.clicar_elemento_driver("#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_btnSimulador")
                self.aguardar_loading()
                try:
                    self.tratar_erros_modal_consulta()
                except PularCheckboxException:
                    self.fechar_modal_simulador()
                    count += 1
                    continue

                self.selenium.atribuir_valor_campo_driver(
                    "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_txtValorParcela", valor_parcela)
                self.selenium.clicar_elemento_driver(
                    "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular")

                if self.selenium.buscar_quantidade_elemento(
                        "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_txtDataPrimVct") == 0:
                    self.selenium.clicar_elemento(
                        "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular")

                self.aguardar_loading()

                try:
                    self.tratar_erros_modal_consulta()
                    self.tratar_erros_alerta()
                except PularCheckboxException:
                    self.fechar_modal_simulador()
                    count += 1
                    continue

                seletor_linhas_taxas = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_gvSimulacao tr"
                linhas_taxa = self.driver.find_element(By.CSS_SELECTOR,seletor_linhas_taxas)

                if linhas_taxa[1].get_attribute('style').find('red') != -1 or not self.validar_taxa(linhas_taxa[1],solicitacao):
                    print("Refinanciamento foi calculado, mas não está disponível.")
                    self.fechar_modal_simulador()
                    count += 1
                    continue

                seletor_prazo = '#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_drpPrazo'
                prazo = self.selenium.verificar_valor_campo_driver(seletor_prazo)

                valores = linhas_taxa[1].text.split(' ')

                saldo_devedor = valores[2].split('\n')[1]
                valor_liberado = valores[3]

                if int(self.formatar_valor(valor_liberado)) <= int(self.formatar_valor(valor_parcela)):
                    print('Refinanciamento não pôde ser calculado pois o valor liberado é '
                          'inferior ao valor da parcela!')
                    self.fechar_modal_simulador()
                    count += 1
                    continue

                self.refinanciamentos.append({
                    'saldoDevedor': saldo_devedor,
                    'valorLiberado': valor_liberado,
                    'prazo': prazo,
                    'valorParcela': valor_parcela
                })

                self.fechar_modal_simulador()

    @staticmethod
    def formatar_valor(valor):
        valor = valor.replace('.', '').replace(',', '')
        return valor

    @staticmethod
    def validar_taxa(linha, solicitacao):

        return True
        
        #raw_taxa = linha.find_element(By.TAG_NAME,'td')[1].text
        raw_taxa = linha.text.split('\n')[0]
        if not raw_taxa:
            return False

        tabela = raw_taxa[0:3]
        taxa = float(raw_taxa[6:].replace(',','.').replace('%',''))

        # if solicitacao['fk_idPerfil'] == '4' or solicitacao['fk_idPerfil'] == '5':
        #     if tabela != 'IN1':
        #         print("Tabela não disponível!")
        #         return False
        #else:
        # if formatar_porcentagem(taxa) < 1.4:
        #     print(f"Taxa encontrada: {taxa}")
        #     return False

        return True

    def calcular_refinanciamentos_inss(self, solicitacao):
        #seletor_checkboxes = "#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos"
        seletor_checkboxes = "cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos"
        try:
            checkboxes_refinanciamento = checkboxes = self.driver.find_element(By.ID,seletor_checkboxes).find_elements(By.TAG_NAME, "tr")
        except:
            checkboxes_refinanciamento = checkboxes = ""
            pass

        if not checkboxes_refinanciamento :
            print('XXXXXXXXXXXNão há matriculas cinculadas ao CPFXXXXXXXXXXXXX')
            return

        indice = -1;
        for checkbox in checkboxes:
            

            try:
                if('CONTRATOS A REFINANCIAR DATA VALOR SOLICITADO' in checkbox.text):
                    continue
            except:
                pass

            indice += 1;

            try:
                if checkbox.is_enabled() == False :
                    continue
            except:
                continue
            #pdb.set_trace()
            if len(checkboxes) -1 > 1:
                #self.desmarcar_todos_checkbox(checkboxes, seletor_checkboxes+"_chkSelecionar_"+str(indice), indice) 
                
                #desmarca todos
                for i in range(indice, len(checkboxes) -1):
                    selector_futuro = seletor_checkboxes+"_chkSelecionar_"+str(i)  
                    if(self.driver.find_element(By.ID, selector_futuro).is_selected()):
                        self.driver.find_element(By.ID, selector_futuro).click()

                selector_atual = seletor_checkboxes+"_chkSelecionar_"+str(indice)   
                self.driver.find_element(By.ID, selector_atual).click()
                
                sleep(2)

            seletor_salario = "#cphBodyMain_cphBody_cphBody_ucConsultaMargem_ucConsultaMargemRefin_txtValorBeneficio"
            self.selenium.atribuir_valor_campo_jquery(seletor_salario, "1.500,00", change=True)
            self.aguardar_loading()

            seletor_simular = "#cphBodyMain_cphBody_cphBody_ucDadosRefinanciamento_gvContratos_rbSelecionar_"+str(indice)
            #seletor_simular = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_btnSimulador"
            self.selenium.clicar_elemento_driver(seletor_simular)
            self.aguardar_loading()

            seletor_calcular = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_btnSimulador"
            #seletor_calcular = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular"
            self.selenium.clicar_elemento_driver(seletor_calcular)
            self.aguardar_loading()

            try:
                self.tratar_erros_modal_consulta()
                self.tratar_erros_alerta()
            except PularCheckboxException:
                self.fechar_modal_simulador()
                continue

            seletor_calcular = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCalcular"
            self.selenium.clicar_elemento_driver(seletor_calcular)
            self.aguardar_loading()

            try:
                self.tratar_erros_modal_consulta()
                self.tratar_erros_alerta()
            except PularCheckboxException:
                self.fechar_modal_simulador()
                continue

            #seletor_linhas_taxas = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_gvSimulacao tr"
            linhas_taxa = self.driver.find_element(By.ID,'cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_gvSimulacao').find_elements(By.TAG_NAME, "tr")

            if linhas_taxa[1].get_attribute('style').find('red') != -1 or not self.validar_taxa(linhas_taxa[1],solicitacao):
                print("Refinanciamento foi calculado, mas não está disponível.")
                self.fechar_modal_simulador()
                continue

            seletor_prazo = '#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_drpPrazo'
            prazo = self.selenium.verificar_valor_campo_driver(seletor_prazo)

            seletor_parcela = '#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_txtValorParcela'
            valor_parcela = self.selenium.verificar_valor_campo_driver(seletor_parcela)

            valores = linhas_taxa[1].text.split(' ')

            saldo_devedor = valores[2].split('\n')[1]
            valor_liberado = valores[3]

            if int(self.formatar_valor(valor_liberado)) <= int(self.formatar_valor(valor_parcela)):
                print("Refinanciamento foi calculado, mas não está disponível.")
                self.fechar_modal_simulador()
                continue

            self.refinanciamentos.append({
                'saldoDevedor': saldo_devedor,
                'valorLiberado': valor_liberado,
                'prazo': prazo,
                'valorParcela': valor_parcela
            })

            self.fechar_modal_simulador()

    def fechar_modal_simulador(self):
        seletor_cancelar = "#cphBodyMain_cphBody_cphBody_ucDadosFinanciamento_ucSimulador_btnCancelar"
        self.selenium.clicar_elemento_driver(seletor_cancelar)
        self.aguardar_loading()

    def desmarcar_todos_checkbox(self, checkboxes):
        for checkbox in checkboxes:
            if checkbox.is_enabled():
                self.selenium.clicar_elemento_driver(checkbox)
                self.aguardar_loading()

    def selecionar_dados_validacao(self, seletor, opcao=1):
        select = self.driver.find_element(By.CSS_SELECTOR,seletor)
        action = ActionChains(self.driver)
        action.click(select)

        for _ in range(opcao):
            action.send_keys(Keys.DOWN)
            action.pause(1)

        action.send_keys(Keys.ENTER)
        action.perform()
        self.aguardar_loading()

    def aguardar_loading(self, tipo = 'consulta_refinanciamento'):
        sleep(2)
        contador = 0
        while self.selenium.buscar_quantidade_elemento('#UpdateProgress1:visible') == 1:
            print('Aguardando o loading...')
            contador += 1
            sleep(2)
            if contador == 50:
                if(tipo == 'consulta_refinanciamento'):
                    self.sincroniza_contratos_andamento()
                else:
                    self.consultar_refinanciamentos()
                

    @staticmethod
    def atualiza_contrato_web_admin(codigo_con, dados):
        print(f'Contrato {codigo_con} atualizado com sucesso!')
        request_dados_contrato = requests.post(
            "https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-bradesco-promotora/contratos/",
            data=dados)

        if request_dados_contrato.status_code == 200:
            print('Contrato atualizado no webadmin com sucesso!')
        else:
            print(request_dados_contrato.text)
            input(f"Aguardando interação... {request_dados_contrato.status_code}")


class RestricaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class NotFoundResultException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class CaptchaException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PularCheckboxException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PularSolicitacaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


if __name__ == '__main__':
    Bradesco.iniciar_horario_comercial()

