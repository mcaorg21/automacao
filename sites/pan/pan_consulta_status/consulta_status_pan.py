import re,pdb
from time import sleep

import requests
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

from sites.core.captcha import TwoCaptcha
from sites.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By
from sites.core.selenium_helper import SeleniumHelper
from sites.core.uconecte import Uconecte

from sites.pan.pan_consulta_status.ConsultaStatusDados import ConsultaStatusDados
from sites.pan.pan_insercao.auto.pan_inserc_formulários import PanFormIdentificacao
from sites.baseRobos.data_handler import DataHandler
from sites.pan.auxiliares.sessao import verificar_sessao_login, login, HORARIO_COMERCIAL
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver import Chrome
from sites.pan.pan_insercao.auto.pan_inserc_formulários import (tratar_mensagens_sistema)


class Pan:

    id_fila_sinc = 28
    id_fila_refin = 27
    id_banco = 68

    def __init__(self, driver, **kwargs):
        self.tabelas_refinanciamento = None
        self.refinanciamentos = None
        self.driver = driver
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"

        self.uconecte = Uconecte(id_banco=self.id_banco)
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.selenium = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver)
        self.forms = PanFormIdentificacao(self.driver)
        self.forms.act.time_out = 3
        self.n_contratos = 0
        self.n_contratos_maximo = 1000
        self.count = 0
        self.log: DataHandler = DataHandler()
        self.dados = ConsultaStatusDados()
        self.cpf = kwargs.get("login", "")
        self.senha = kwargs.get("senha", "")
        self.parceiro = kwargs.get("parceiro", "")
        self.aguardar_sessao = False

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome, configs: dict):
        run = Pan(driver, **configs)
        try:
            return run.sincroniza_contratos_andamento()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):

        self.sincroniza_contratos_andamento()

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def sincroniza_contratos_andamento(self):
        print("Trabalhando na fila de sincronização...")
        try:
            tratar_mensagens_sistema(self.act,self.act.obter_texto_alerta(),'')
        except:
            pass
        contratos_a_atualizar = self.busca_contratos_em_andamento()
        print(contratos_a_atualizar)
        self.n_contratos = 0

        if len(contratos_a_atualizar) == 1:
            print("Fila de sincronização está vazia, trocando para a fila de geração de contratos...")
            return -1

        try:
            self.menu_aprovacao_consulta(0, tipo = contratos_a_atualizar[1:][0][3])
        except:
            self.menu_aprovacao_consulta()
            pass

        for contrato in contratos_a_atualizar[1:]:
            self.contrato = contrato
            try:
                # if not verificar_sessao_login(driver=self.driver, aguardar=self.aguardar_sessao):
                #     login(cpf_login=self.cpf, senha=self.senha, driver=self.driver)
                #     self.aguardar_sessao = True
                #     self.menu_aprovacao_consulta()

                if self.n_contratos == self.n_contratos_maximo:
                    return 1
                self.n_contratos += 1

                print(f"CONTRATO Nº{self.n_contratos} DE {self.n_contratos_maximo}")

                print(f'Pesquisando contrato {contrato[2]}...')  # contrato[2] = ADE
                dados = self.pesquisa_detalhes_contrato(contrato[0], contrato[1], contrato[2])

                if(dados == False):
                    self.menu_aprovacao_consulta(0,contrato[3])
                    dados = self.pesquisa_detalhes_contrato(contrato[0], contrato[1], contrato[2])
                    #self.menu_aprovacao_consulta()
                    if(dados == False):
                        continue
                # contrato[0] = Número da proposta // contrato[1] = CPF
                print("Atualizações:", dados)
                if dados:
                    self.atualiza_contrato_web_admin(contrato[2], dados)
                    #self.menu_aprovacao_consulta()
                
            except Exception as e:
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0)
                self.menu_aprovacao_consulta()

        # self.dados.data_source.atualizar_sincronizacao()
        # self.log.api_registrar_log_robo(
        #                 log=f"Sincronização realizada com sucesso.",
        #                 status=2
        #             )
        return 0

    def menu_aprovacao_consulta(self, tempo_dias_contrato = 0, tipo = 'consignado'):
        
        if('FGTS' in tipo):   
            #'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAndFGTS.aspx?FISession=3979d572847f'         
            link = 'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAndFGTS.aspx'
            id_link = 'WFP2010_PWCNPROPFGTS'
        elif('CARTÃO' in tipo):  
            #'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAndCart.aspx?FISession=3979d572847f'          
            link = 'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAndCart.aspx'
            id_link = 'WFP2010_PWTCNPROPCART'
        else:
            #'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx?FISession=3979d572847f'
            link = 'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx'
            id_link = 'WFP2010_PWTCNPROP'

        #self.driver.get('https://panconsig.pansolucoes.com.br/FIMenu/M')
        #self.driver.get(link)

        try:
            self.act.clicar_elemento('//*[@id="content"]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/div[2]',By.XPATH)
            sleep(2)
            self.act.clicar_elemento('//*[@id="block"]/a', By.XPATH)
        except:
            #novo except
            self.act.clicar_elemento('//*[@id="btnVoltar_txt"]', By.XPATH)
            pass

        try:
            tratar_mensagens_sistema(self.act,self.act.obter_texto_alerta(),'')
        except:
            pass

        self.act.hover_menu_dropdown('//*[@id="navbar-collapse-funcao"]/ul/li[2]/a',By.XPATH)
        
        if(tempo_dias_contrato > 0):
            self.act.clicar_elemento('//*[@id="WFP2010_PWCNPROPCI"]',By.XPATH)
        else:
            self.act.clicar_elemento(f'//*[@id="{id_link}"]',By.XPATH)

    def busca_contratos_em_andamento(self):
        return self.dados.propostas_consultar()

    def pesquisa_detalhes_contrato(self, ade, cpf, codigo_con):
        try:
            observacao_detalhada_banco = ''
            observacao_completa = ''
            sleep(2)
            self.selenium.atribuir_valor_campo_jquery("#ctl00_Cph_AprCons_txtPesquisa_CAMPO", ade)
            self.aguardar_loading()
            self.selenium.clicar_elemento_driver("#btnPesquisar_txt")
            
            self.aguardar_loading()

            encontrar_proposta = self.selenium.verificar_texto_campo_jquery('#ctl00_Cph_AprCons_grdConsulta').strip()
            #pdb.set_trace()
            if encontrar_proposta == 'Não há dados para a visualização.':
                self.menu_aprovacao_consulta(0,self.contrato[3])
                return self.pesquisa_detalhes_contrato(ade, cpf, codigo_con)
                #print(f'Contrato {codigo_con} é antigo ou não consta em banco de dados deste login')
                #status_proposta_banco = 'PENAnalise Promotora'
                #observacao_detalhada_banco = 'CONTRATO ANTIGO OU ADE INCORRETA'
                #return False
            else:
                status_proposta_banco = ''
                ade_busca = self.selenium.verificar_texto_campo_jquery('#ctl00_Cph_AprCons_grdConsulta > tbody > tr.normal > td:nth-child(1) > a').strip()

                if ade == ade_busca:
                    try:
                        status_proposta_banco = self.driver.execute_script(
                            f"""return $('#ctl00_Cph_AprCons_grdConsulta').text().split('NÃO')[1].split('{cpf}')[0].replace(
                            'DIGITAL','').replace('FÍSICO','')""")
                    except:
                        pass
                    try:
                        #self.driver.execute_script(""" __doPostBack('ctl00$Cph$AprCons$grdConsulta','Situacao$0')""")
                        self.driver.execute_script(""" document.querySelector("#ctl00_Cph_AprCons_grdConsulta > tbody > tr.normal > td:nth-child(3) > a").click()""")
                    except:
                        pass
                    self.aguardar_loading()

                    tentativa = 0
                    while self.selenium.buscar_quantidade_elemento('#ctl00_Cph_AprCons_popSituacao_frameAjuda') == 0:
                        tentativa += 1
                        print('Aguardando janela abrir...')
                        sleep(1)
                        self.aguardar_loading()

                        if(tentativa > 50):
                            self.driver.quit()

                    self.aguardar_loading()

                    self.selenium.selecionar_frame('#ctl00_Cph_AprCons_popSituacao_frameAjuda')
                    observacao_completa = self.selenium.verificar_texto_campo_jquery('#ctl00_cph_UcObs_UcObs_txtObs_CAMPO').replace('"','').replace("'",'')

                    if(observacao_completa):

                        if 'BD - Inclusão Efetuada com Sucesso' in observacao_completa:
                            status_proposta_banco += ' - AVERBADA'
                        if 'foi aprovada com sucesso via Webservice através do método AprovarProposta' in observacao_completa:
                            status_proposta_banco += ' - JA LIBERADA'
                        if 'HW - Margem consign excedida' in observacao_completa:
                            status_proposta_banco += ' - JA REPROVADA POR MARGEM AGUARDANDO NOVA TENTATIVA'

                        observacao_detalhada_banco += "\n\n" + observacao_completa

                    self.selenium.clicar_elemento('#btnFechar_txt')

                    print('Salvando observações detalhadas...')

                    dados = {
                        "key": "f689f1e12a0399fba803cb2365fc362f",
                        "statusPropostaBanco": status_proposta_banco,
                        "observacaoDetalhadaBanco": observacao_detalhada_banco,
                        "codigoCon": codigo_con,
                        "ade": ade,
                        "atualiza_detalhes" : 1
                    }

                    return dados
                else:
                    print('>>>>>>>>>>>>>>>>>> ERRO ADE INCORRETA <<<<<<<<<<<<<<<<<<<<')
                    print('ADE: ' + ade + 'ADE FILA: ' + ade_busca)
                    print('>>>>>>>>>>>>>>>>>> ERRO ADE INCORRETA <<<<<<<<<<<<<<<<<<<<')
                    self.menu_aprovacao_consulta(0,self.contrato[3])

        except UnexpectedAlertPresentException:
            self.tratar_mensagem_alert()

    @staticmethod
    def atualiza_contrato_web_admin(codigo_con, dados):

        print(f'Contrato {codigo_con} atualizado com sucesso!')
        requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-pan/contratos/", data=dados)

    def tratar_mensagem_alert(self, solicitacao=False):
        sleep(0.5)
        try:
            print("Buscando mensagem alert")
            mensagem = self.act.obter_texto_alerta()
            if mensagem is None:
                return
            print(mensagem)

        except NoAlertPresentException:
            return
        except Exception as e:
            print(f"Erro ao buscar a mensagem de alert. {e}")
            return self.tratar_mensagem_alert()

        mensagens_regex = [
            {
                'texto': r"Cliente pré-aprovado",
                'Continue': True
            }, {
                'texto': r"Não foi possível realizar a consulta no momento",
                'Continue': True
            }, {
                'texto': r"Banco ou Agência inválido.",
                'Continue': True
            }, {
                'texto': r"Falha de comunicação com o serviço externo após",
                'Continue': True
            }, {
                'texto': r"Agência \d{4} esta inativa.",
                'Continue': True
            }, {
                'texto': r"Quantidade de dígitos informados deve ser igual a 8.",
                'MatriculaErrorPensionista': True
            }, {
                'texto': r"Quantidade de dígitos informado deve ser no máximo 7.",
                'MatriculaErrorServidor': True
            }, {
                'texto': r"A data informada no campo Dt. Nasc: é inválida",
                'Preenchimento': True
            }, {
                'texto': r"É necessário informar o campo ORGAO",
                'Preenchimento': True
            }, {
                'texto': r"Não existem prazos disponíveis nas condições informadas.",
                'InfoNotFound': True
            }, {
                'texto': r"Nenhuma operação encontrada para o CPF\/CNPJ informado",
                'InfoNotFound': True
            }, {
                'texto': r"Recusa Definitiva",
                'Restricao': True
            }, {
                'texto': r"O conteúdo do campo Dt. Nasc",
                'InfoNotFound': True
            }, {
                'texto': ("Consulta de Margem. O tipo de operação 'Refinanciamento' não está autorizado "
                          "por esse servidor. Margem será calculada pela função."),
                'Restricao': True
            }, {
                'texto': ('Não possui contratos. Mensagem Sistema: Nenhuma '
                          'operação encontrada para o CPF/CNPJ informado.'),
                'InfoNotFound': True
            }, {
                "texto": 'Quantidade de parcelas vencidas superior ao permitido!',
                'Restricao': True
            }, {
                'texto': r"É necessário informar o campo EMPREGADOR",
                'InfoNotFound': True
            },
        ]

        print(f"Mensagem alert: {mensagem}")

        for mensagem_regex in mensagens_regex:
            regex = re.compile(mensagem_regex['texto'].lower())
            mensagem_encontrada = regex.search(mensagem.lower())

            if not mensagem_encontrada:
                continue

            self.act.manusear_alerta('aceitar')

            if 'InfoNotFound' in mensagem_regex:
                raise NotFoundResultException(mensagem)
            elif 'Restricao' in mensagem_regex:
                raise RestricaoException(mensagem)
            elif 'Preenchimento' in mensagem_regex:
                raise PreenchimentoException(mensagem)
            elif 'Continue' in mensagem_regex:
                return

    def aguardar_loading(self):
        sleep(0.5)
        iteracoes = 0
        while self.selenium.buscar_quantidade_elemento('.updateprogress:visible') == 1:
            if iteracoes >= 10:
                raise Exception("Numero de iterações excedido:", iteracoes)
            print('Aguardando o Loading...')
            sleep(2)
            iteracoes += 1


class RestricaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class NotFoundResultException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PularCheckboxException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PreenchimentoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
