import sys
sys.path.append('../')


from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.helpers import definir_nome_robo
from dados.database.queries.query_dados_robos import query_login_pass_robo
from sites.ibConsig.IbConsigInsercao.auto.FormDadosBancarios import *
from sites.ibConsig.IbConsigInsercao.auto.FormDadosEndereco import *
from sites.ibConsig.IbConsigInsercao.auto.FormDadosFinais import *
from sites.ibConsig.IbConsigInsercao.auto.FormDadosIniciais import *
from sites.ibConsig.IbConsigInsercao.auto.FormDadosPessoais import *
from sites.ibConsig.IbConsigInsercao.auto.FormDadosProposta import *
from sites.ibConsig.libs.auto.forms.FormDadosProposta import FormDadosProposta
from sites.ibConsig.IbConsigInsercao.auto.FormIdentificacao import *
from sites.ibConsig.IbConsigInsercao.auto.TabelaRefinanciamentos import *
from sites.ibConsig.libs.auxiliares.ib_auxiliares import *
import PATHS
from sites.baseRobos.manager import Manager

from sites.ibConsig.IbConsigInsercao.data.IbConsigData import (
    IbConsigData, DadosServidorFederalInvalidos
)
from sites.baseRobos.core.DebugTools import DebugTools
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig
from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites import ID_ROBOS
import time,pdb,json

from sites.ibConsig.IbConsigInsercao.manager.portabilidade.insercao_portabilidade import *

from datetime import datetime

from dados.APIDataSource import APIDataSource

from sites.ibConsig.cookies import COOKIES_INSERIR_CONTRATO

debug = DebugTools(debugging=False)
HORARIO_COMERCIAL = 7, 20

import pdb

class InsercaoIbConsig(Manager):

    ID_BANCO = 1
    ID_ROBO = ID_ROBOS['ibConsig']['inserir']

    captcha_path: str = str(Path(PATHS.project_path() + "/ibConsig/IbConsigInsercao/static"))

    def __init__(self, **kwargs):
        super().__init__()
        self.cookies_path = COOKIES_INSERIR_CONTRATO

        self.user_chrome_path: str = kwargs.get('chrome_user', PATHS.chrome_user("IbConsigInsercao"))
        Manager.criar_pasta_usuario_chrome(self.user_chrome_path)
        self.set_options('--ignore-ssl-errors', 'log-level=3', self.user_chrome_path)
        self.init_chrome_driver(import_driver=kwargs.get("extern_driver", False))

        self.data: IbConsigData = IbConsigData()

        self.act: SeleniumActions = SeleniumActions(self.driver, time_out=0.3)
        self.act.message = "Elemento não encontrado."

        self.selenium_helper: SeleniumHelper = SeleniumHelper(self.driver)

        self.mensagem_cliente: str = ""
        self.contrato: dict = {}
        self.vals_ideais: dict = {}

    
        self.data.ordem_busca = kwargs.get('ordem', 'asc')
        self.data.filtro_contratos = kwargs.get('filtro', '')
        self.data.contrato_teste = kwargs.get('contrato_teste', '')

        hoje = datetime.today().isoweekday()

        if(hoje == 1 or hoje == 3):
            #segunda quarta
            self.usuario = kwargs.get("usuario", "cristiano.1873")  
            #self.usuario = "cristiano.1873"          
        elif(hoje == 2 or hoje == 4):
            #terca quinta
            self.usuario = kwargs.get("usuario", "mca1873")
            #self.usuario = "mca1873" 
        else:
            #sexta
            self.usuario = kwargs.get("usuario", "cristiano.1873")
            #self.usuario = "cristiano.1873" 
        
        self.wait = 0.2
        
        #self.senha = kwargs.get("senha","t909176#")

        dados_login = query_login_pass_robo(1, self.usuario)
        self.senha = dados_login["senha"]

        dados_login = {'usuario': self.usuario, 'senha': self.senha,
                       'driver': self.driver}

        self.login = IbConsig.login_fact(**dados_login)
        self.log_path = f"/ibConsig/log/{self.__class__.__name__}"
        self.data.instancia = "MAIN"

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, nome_instancia):

        definir_nome_robo(f'Itau - Insercao {nome_instancia}')

        run = InsercaoIbConsig()
        
        try:
            run.main()            
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

        tentativa_login = 0
        while not self.login():
            tentativa_login += 1
            if(tentativa_login > 5):
                print('Fora do ar...')
                sleep(60)
                self.driver.quit()
            print('Tentativa de Login')
            sleep(5)
            self.driver.delete_all_cookies()
            self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')


        self.selenium_helper.save_cookies(self.cookies_path)

        print("Adicionando os cookies do primeiro usuário...")
        self.selenium_helper.load_cookies(self.cookies_path, True)

        while True:
            self.inserir_contratos()
            sleep(5)
            self.driver.refresh()

    def inserir_contratos(self) -> int:

        contratos = self.data.buscar_lista_a_inserir()

        for contrato in contratos:

            if contrato['valor_con'] is None:
                print('XXXXXXXXXXXXX ERRO DE DADOS XXXXXXXXXXXXXXX')
                self.data.atualizar_contrato(contrato['codigo_con'],mensagem='Reprovado a Conferir',erro = 'Sem dados para inserir, possivel erro no BD')
                continue

            self.data.verificar_atualizacoes_pendentes()
            try:
                print(f"\nINÍCIO: {dt.now()}\n")
                self.driver.refresh()

                print("Tipo de proposta: ", contrato['tipo'])

                # Buscar detalhes do contrato
                self.contrato = self.data.get_contrato_uconecte(contrato['codigo_con'])
                print("contrato: ", self.contrato)

                # if(self.contrato['informacoesExtras']['carenciaTabela'] == '120' and contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
                #     print('Pulando contrato '+contrato['codigo_con'])
                #     print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<TABELA COM CARENCIA '+self.contrato['informacoesExtras']['carenciaTabela']+' BANCO AJUSTANDO PULANDO PROPOSTA>>>>>>>>>>>>>>>>>>>>>>>>>')
                #     continue
                # else:
                #     print('Inserindo contrato '+contrato['codigo_con'])
                #     print('******************************TABELA SEM CARENCIA*****************************************')

                if not IbConsig.esta_logado(self.driver):
                    self.login()

                if not IbConsig.tela_inicial(self.driver):
                    debug.warning(
                        "[!] Tela Inicial Não Foi Carregada [!] "
                        "\nAperte qualquer tecla para seguir")
                    self.driver.quit()

                print(f"\nIniciando inserção do contrato:",
                      self.contrato['codigo_con'])

                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem='Inserir contrato')

                self.contrato['tipo'] = contrato['tipo']

                self.data.api_iniciar_log_robo(
                    idRobo=self.ID_ROBO, idContrato=contrato['codigo_con'])

                conObj: Contrato = Contrato(self.contrato)

                if contrato['tipo'] == 'REFINANCIAMENTO' or contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM':
                    # if(contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM' and self.contrato['valorParcelaRefinMargem'] == ""):
                    #     self.data.atualizar_contrato(
                    #         self.contrato['codigo_con'],
                    #         erro=f"Erro encontrado: Não foi registrada a parcela de refin + margem", 
                    #         mensagem='Conferir dados do contrato',
                    #         observacao="Favor ajustar no editar a parcela do contrato a ser utilizado no sistema do Itaú, senão tiver a parcela aberta pedir extrato de consignação para verificar em outros bancos que representamos."
                    #     )
                    #     continue
                    self.inserir_contrato_refinanciamento(conObj)
                elif(contrato['tipo'] == 'PORTABILIDADE'):
                    run_portabilidade = InsercaoIbConsigPortabilidadeFila
                    InsercaoIbConsigPortabilidadeFila.inserir_contrato_financiamento(self,conObj)
                else:
                    self.inserir_contrato_financiamento(conObj)

            except ErroRetornarFila as e:
                self.data.api_registrar_log_robo(
                    log=f"ERRO: {e.message}",
                    status=0
                )
                self.act.manusear_alerta('aceitar')
            except UnexpectedAlertPresentException as e:
                self.data.api_registrar_log_robo(
                    log=f"ERRO: {e.alert_text}",
                    status=0
                )
                self.act.manusear_alerta('aceitar')
                continue

            except PreenchimentoException as e:
                print("Erro encontrado: {}".format(e.message))
                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    erro=f"Erro encontrado: {e.message}", mensagem='Conferir dados do contrato',
                    observacao=e.message,

                )
                self.data.api_registrar_log_robo(
                    log=f"NotFoundResultException: {e.message}",
                    status=2
                )

            except PreenchimentoTabelaException as e:

                print("Erro encontrado: {}".format(e.message))
                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    erro=f"Erro encontrado: {e.message}", mensagem='Reprovado a Conferir',
                    observacao=e.message,

                )
                self.data.api_registrar_log_robo(
                    log=f"NotFoundResultException: {e.message}",
                    status=2
                )

            except DadoIndisponivelException as e:
                print("Erro encontrado: {}".format(e.msg))
                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    erro=f"Erro encontrado: {e.msg}", mensagem='Conferir dados do contrato',
                    observacao=e.msg,

                )
                self.data.api_registrar_log_robo(
                    log=f"DadoIndisponivelException: {e.msg}",
                    status=2
                )

            except Exception as e:
                debug.exception(e)
                self.manager_error_log(e)
                fechar_janelas_com_erro(self.driver)
                self.data.api_registrar_log_robo(log=f"ERRO: {e}", status=0)

        return 0

    def inserir_contrato_financiamento(self,conObj):
        print(f"Trabalhando no contrato: {self.contrato['codigo_con']}")

        if(self.contrato['tipo'] == 'ANTECIPAÇÃO FGTS'):
            self.contrato['entidade'] = '11-'
            preencher_dados = self.preencher_formulario_identificacao_fgts()
        else:
            self.contrato['entidade'] = filtrar_entidade(self.contrato, False)
            self.act.retornar_janela_principal()
            preencher_dados = self.preencher_formulario_identificacao()

        if(self.contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
            run_portabilidade = InsercaoIbConsigPortabilidadeFila
            InsercaoIbConsigPortabilidadeFila.inserir_contrato_financiamento_aumento(self,conObj)
        elif(self.contrato['tipo'] == 'ANTECIPAÇÃO FGTS'):
            run_portabilidade = InsercaoIbConsigPortabilidadeFila
            retorno = InsercaoIbConsigPortabilidadeFila.inserir_contrato_financiamento_fgts(self,conObj)

            if(retorno[0] == False):
                payload = {
                    "statusPropostaBanco": retorno[1],
                    "codigoCon": self.contrato['codigo_con'],
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                response = APIDataSource().post_request_v2("enviar-dados-itau-sincronizacao", payload)
                raise ErroRetornarFila('Retornando fila: ' + retorno[1])

        else:
            if preencher_dados:
                try:
                    self.preencher_dados_iniciais()
                    aceitar_pendencia(self.driver, self.selenium_helper)

                    self.preencher_dados_bancarios()

                    dados_proposta: DadosProposta = self.preencher_dados_proposta(conObj)
                    self.preencher_dados_pessoais()
                    self.preencher_dados_endereco()

                    aceitar_pendencia(self.driver, self.selenium_helper)

                    self.preencher_dados_finais()
                    self.finalizar_insercao_popup()

                    n_ade = self.buscar_ade()

                    if n_ade:

                        self.data.atualizar_aguardando_gerar_contrato(
                            contrato=self.contrato,
                            tabelaBanco=dados_proposta.tabela_selecionada,
                            ade=n_ade,
                        )

                    print('Iniciando próximo contrato...')

                except UnexpectedAlertPresentException as e:
                    print("Alerta inesperado: ", e.alert_text)
                    tratar_erros_formulario_insercao(
                        self.driver, self.contrato['codigo_con'],
                        vals_atualizados=self.vals_ideais,
                    )
                except NotFoundResultException as e:
                    print("Erro encontrado: {}".format(e.message))
                    self.data.atualizar_contrato(
                        self.contrato['codigo_con'],
                        erro=f"Erro encontrado: {e.message}", mensagem='Reprovado a Conferir',
                        observacao=e.message,

                    )
                    self.data.api_registrar_log_robo(
                        log=f"NotFoundResultException: {e.message}",
                        status=2
                    )

        time.sleep(self.wait)

    def inserir_contrato_refinanciamento(self,conObj, index_refin = 0):
        print(f"Trabalhando no contrato: {self.contrato['codigo_con']}")

        self.contrato['entidade'] = filtrar_entidade(self.contrato)

        self.act.trocar_janela(idx_janela=0, numero_janelas=1)

        try:
            self.preencher_formulario_identificacao()

            tabela_refin = TabelaRefinanciamentos(self.driver, self.contrato)

            # Quantidade de check_boxes na tabela de refins.
            tabela_refin.extrair_quantidade_refins()
            refins_disponiveis = []

            #seleciona automaticamente a parcela de refinanciamento somando margem mais baixa
            if(self.contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM' and self.contrato['valorParcelaRefinMargem'] == ""):
                for index in range(tabela_refin.total_refinanciamentos):                    
                    self.selenium_helper.trocar_frame('rightFrame')
                    tabela_refin.set_linha_tabela(index)
                    if(tabela_refin.encontrar_matricula_refinanciamento_somando_margem()):
                        refins_disponiveis.append(tabela_refin.retornar_parcela_refinanciamento())

                if(len(refins_disponiveis) > 0):
                    self.contrato['valorParcelaRefinMargem'] = "{:.2f}".format(sorted([float(i.replace(',','.')) for i in refins_disponiveis])[index_refin]);
                    self.contrato['valorParcelaRefinMargem'] = self.contrato['valorParcelaRefinMargem'].replace(',','.')
                    self.contrato['valorParcela'] = valor_parcela_texto = self.contrato['valorParcela'].replace(',','.')
                    self.contrato['valorParcela'] = float(self.contrato['valorParcela']) + float(self.contrato['valorParcelaRefinMargem'])
                    self.contrato['valorParcela'] = "{:.2f}".format(self.contrato['valorParcela']).replace('.',',')
                    self.contrato['valorParcelaRefinMargem'] = self.contrato['valorParcelaRefinMargem'].replace('.',',')
                    tabela_refin = TabelaRefinanciamentos(self.driver, self.contrato)
                    # Quantidade de check_boxes na tabela de refins.
                    tabela_refin.extrair_quantidade_refins()
                    refins_disponiveis = []
                    print('Atualizando a parcela do refinanciamento somando margem')
                    self.data.atualizar_contrato(codigo_contrato=self.contrato['codigo_con'], 
                                                mensagem="Atualizar Parcela", 
                                                valorParcela=self.contrato['valorParcela'],
                                                valorParcelaRefinMargem = self.contrato['valorParcelaRefinMargem'],
                                                textoMensagem = "Como possui 9 empréstimos usamos a sua menor parcela no Itaú de R$"+self.contrato['valorParcelaRefinMargem']+" e somamos a margem atual, totalizando para uma nova parcela de R$"+self.contrato['valorParcela']
                                                )

                else: 
                    raise NotFoundResultException("Não foram encontrados no Itaú refinanciamentos para realizar a operação de refin + margem")

            for index in range(tabela_refin.total_refinanciamentos):
                n_ade: str = ""
                self.selenium_helper.trocar_frame('rightFrame')

                try:
                    # Verificar infos contrato com infos de cada linha da tabela
                    tabela_refin.set_linha_tabela(index)
                    tabela_refin.encontrar_matricula_refinanciamento()
                    if(self.contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM'):
                        self.refin_somando_margem = True
                    else:
                        self.refin_somando_margem = False
                    tabela_refin.encontrar_parcela_refinanciamento(self.refin_somando_margem)

                    # A escolha do refin ocorre quando os dados batem.
                    tabela_refin.selecionar_refinanciamento()
                    tratar_alerts_refinanciamento(self.driver, tabela_refin.act)

                    aguardar_loading(self.driver)

                    if tabela_refin.refinanciamento_selecionado:
                        tabela_refin.confirmar_selecao()
                        break

                except UnexpectedAlertPresentException as e:
                    self.act.manusear_alerta('aceitar')
                except PularCheckboxException:
                    continue
                except IndexError:
                    pass

            if not tabela_refin.refinanciamento_selecionado:
                raise NotFoundResultException("Refinanciamento não encontrado")

            atualizar_portabilidade: bool = verifica_portabilidade_retencao(
                driver=self.driver, sh=self.selenium_helper
            )
            if atualizar_portabilidade:
                self.data.portabilidade_retencao_put(self.contrato['codigo_con'])

            self.preencher_dados_iniciais()
            self.preencher_dados_bancarios()
            dados_proposta: DadosProposta = self.preencher_dados_proposta(conObj)

            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
            )
            self.preencher_dados_pessoais()
            self.preencher_dados_endereco()
            aceitar_pendencia(self.driver, self.selenium_helper)
            self.preencher_dados_finais()

            self.finalizar_insercao_popup()

            n_ade = self.buscar_ade()

            if n_ade:
                self.data.atualizar_aguardando_gerar_contrato(
                    contrato=self.contrato,
                    tabelaBanco=dados_proposta.tabela_selecionada,
                    ade=n_ade,
                )

        except RestricaoException as e:
            print('Cadastrar restrição. Mensagem Sistema: {}'.format(e.message))
            self.data.atualizar_contrato(
                self.contrato['codigo_con'], mensagem=e.message,
            )
            self.data.api_registrar_log_robo(
                log=f'Cadastrar restrição. Mensagem Sistema: {e.message}',
                status=2
            )

        except NotFoundResultException as e:
            print("Erro encontrado: {}".format(e.message))
            self.data.atualizar_contrato(
                self.contrato['codigo_con'],
                erro=f"Erro encontrado: {e.message}", mensagem='Reprovado a Conferir',
                observacao=e.message,

            )
            self.data.api_registrar_log_robo(
                log=f"NotFoundResultException: {e.message}",
                status=2
            )
        except PreenchimentoException as e:
            print("Erro encontrado: {}".format(e.message))
            self.data.atualizar_contrato(
                self.contrato['codigo_con'],
                erro=f"Erro encontrado: {e.message}", mensagem='Conferir dados do contrato',
                observacao=e.message,

            )
            self.data.api_registrar_log_robo(
                log=f"NotFoundResultException: {e.message}",
                status=2
            )
        except UnexpectedAlertPresentException as e:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],

            )

    def preencher_formulario_identificacao(self):
        form: DadosIdentificacao = DadosIdentificacao(self.driver, self.contrato)

        #form.valida_entidade()
        #time.sleep(self.wait)
        try:
            self.act.retornar_janela_principal()
            self.selenium_helper.trocar_frame("leftFrame")
            form.abrir_menu_proposta()

            if form.nova_proposta:
                form.link_nova_proposta()
            elif form.refinanciamento:
                form.link_refinanciamento()
            self.selenium_helper.trocar_frame("rightFrame")
            # Preencher campos específicos à entidade do cliente
            self.padrao_formulario_por_entidade(form)

            form.resolver_captcha()

            if form.resposta_captcha == 'ERROR NO USER':
                form.captcha.mudar_status_captcha(form.id_captcha, '2')
                return self.preencher_formulario_identificacao()

            form.preencher_resposta_captcha()

            form.clicar_confirmar()

            aguardar_loading(self.driver)

            try:
                if('estadual' in self.contrato and self.contrato['estadual'] == True):
                    form.escolher_matricula()
            except:
                pass

            selecionar_opcao_modal_formulario(self.driver)

            aguardar_loading(self.driver)

            tratar_erros_formulario_identificacao(
                msg_erro=form.verificar_erros(), driver=self.driver,
                codigo_con=self.contrato['codigo_con'], id_captcha=form.id_captcha
            )
            try:
                item_formulario = self.driver.execute_script(
                    "return $('#ade\\\\.dataFator').length;")

            except JavascriptException:
                print('Formulário de inserção não foi aberto, pular a inserção!')
                return False

            if item_formulario == 1:
                return True

            aguardar_loading(self.driver)

        except PreenchimentoException:
            return self.preencher_formulario_identificacao()

    def preencher_formulario_identificacao_fgts(self):
        form: DadosIdentificacao = DadosIdentificacao(self.driver, self.contrato)

        try:
            self.act.retornar_janela_principal()
            self.selenium_helper.trocar_frame("leftFrame")
            form.abrir_menu_proposta()
            form.link_nova_proposta()

            self.selenium_helper.trocar_frame("rightFrame")

            # Preencher campos específicos à entidade do cliente
            self.padrao_formulario_por_entidade(form)

            form.resolver_captcha()

            if form.resposta_captcha == 'ERROR NO USER':
                form.captcha.mudar_status_captcha(form.id_captcha, '2')
                return self.preencher_formulario_identificacao_fgts()

            form.preencher_resposta_captcha()

            form.clicar_confirmar()

            aguardar_loading(self.driver)

            selecionar_opcao_modal_formulario(self.driver)
            
            msg_erro = form.verificar_erros()

            if(msg_erro and 'A palavra de verificação expirou, por favor gere outra imagem' not in msg_erro
                and 'Palavra de verificação da imagem está incorreta, por favor tente novamente' not in msg_erro):
                payload = {
                    "statusPropostaBanco": msg_erro,
                    "codigoCon": self.contrato['codigo_con'],
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                response = APIDataSource().post_request_v2("enviar-dados-itau-sincronizacao", payload)
                raise ErroRetornarFila('Retornando fila: ' + msg_erro)

            if(msg_erro and 'Palavra de verificação da imagem está incorreta' in msg_erro):
                return self.preencher_formulario_identificacao_fgts()

            try:
                item_formulario = self.driver.execute_script(
                    "return $('#ade\\\\.dataFator').length;")

            except JavascriptException:
                print('Formulário de inserção não foi aberto, pular a inserção!')
                return False

            if item_formulario == 1:
                return True

            aguardar_loading(self.driver)

        except PreenchimentoException:
            return self.preencher_formulario_identificacao()

    def padrao_formulario_por_entidade(self, form: DadosIdentificacao):
        """
        Verifica o padrao do formulário do cliente: se 1581 (INSS, normal
        ou novo_margem (margem complementar)),
        164 (Servidores federais) e servidores de SP (código existente apenas no IbInserção teste).
        :raises DadosServidorFederalInvalidos:
        """
        if(self.contrato['tipo'] == 'ANTECIPAÇÃO FGTS'):
            time.sleep(self.wait)
            form.preencher_entidade()
            aguardar_loading(self.driver)
            form.preencher_cpf()
        else:

            if form.aposentado_pensionista_inss:
                time.sleep(self.wait)

                form.preencher_entidade()

                while self.selenium_helper.buscar_quantidade_elemento_somente_tela(r'#identificacao-form\\\:orgao\\\:find\\\:loading') == 1:
                    print('Aguardando loading...')
                    time.sleep(self.wait)
                if form.nova_proposta:
                    if(self.contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
                        try:
                            form.selecionar_servico('2')
                        except:
                            form.selecionar_servico('1')  
                        time.sleep(self.wait+1)
                    form.preencher_data_nascimento()
                    time.sleep(self.wait)
                    form.preencher_cpf()
                    form.preencher_matricula()
                    form.verificar_data_nascimento()
                    


                elif form.refinanciamento:
                    #while self.selenium_helper.verificar_texto_campo_jquery(r'#identificacao-form\\\:cpf') == '':
                    form.preencher_cpf()
                    time.sleep(self.wait + 2)
                    if(self.selenium_helper.verificar_texto_campo_jquery(r'#identificacao-form\\\:cpf') == ''):
                        form.preencher_cpf()

                if not form.data_nascimento_preenchida and form.nova_proposta:
                    return self.preencher_formulario_identificacao()

            elif form.servidor_federal:
                print("SERVIDOR FEDERAL")
                if form.nova_proposta:
                    try:
                        form.carregar_dados_servidor_federal()
                        form.clicar_botao_pesquisar_orgao()
                        form.preencher_campo_pesquisa_orgao()
                        form.confirmar_pesquisa_orgao()
                        form.clicar_botao_finalizar_pesquisa()
                        time.sleep(self.wait)
                        form.selecionar_situcao_servidor()
                        time.sleep(self.wait)
                    except:
                        try:
                            form.valida_entidade()
                            form.carregar_dados_orgao_servidor_federal_web_admin()
                            form.preencher_campo_pesquisa_orgao_direto()
                            time.sleep(self.wait)
                            form.selecionar_situcao_servidor(False,'2')
                        except:
                            self.data.atualizar_contrato(
                                codigo_contrato=self.contrato['codigo_con'],
                                observacao_emp='Colocar o orgao manual dentro da proposta e colocar insercao automatica.', mensagem='Conferir dados do contrato')
                            raise DadosServidorFederalInvalidos('Possivelmente cliente é aposentado ou pensionista...')  

                if form.refinanciamento:
                    form.preencher_entidade()

                time.sleep(self.wait+2)
                form.preencher_cpf()
                form.preencher_matricula_federal()
                form.selecionar_situcao_servidor()

            elif form.servidor_mt:
                form.valida_entidade()
                print("SERVIDOR ESTADUAL MT")
                form.carregar_dados_servidor_estadual_mt()
                if form.nova_proposta:
                    form.preencher_campo_pesquisa_orgao_direto()

                if form.refinanciamento:
                    form.preencher_entidade()

                time.sleep(self.wait+2)
                form.preencher_cpf()
                time.sleep(self.wait+2)
                form.preencher_cpf()

            elif form.servidor_sao_paulo:
                form.valida_entidade()
                print("SERVIDOR ESTADUAL SP")
                form.carregar_dados_servidor_estadual_sp()
                if form.nova_proposta:
                    form.preencher_campo_pesquisa_orgao_direto()

                if form.refinanciamento:
                    form.preencher_entidade()

                time.sleep(self.wait+2)
                form.preencher_cpf()
                time.sleep(self.wait+2)
                form.preencher_cpf()
                # form.preencher_matricula()
                # form.preencher_data_nascimento()
                #debug.warning("Robô não configurado para servidores de SP")

    def preencher_dados_iniciais(self, alterar_renda:str = ""):
        form: DadosIniciais = DadosIniciais(driver=self.driver, dados=self.contrato)
        self.act.time_out = 0.1

        print("\n<Dados Iniciais Contrato>\n")
        try:
            tratar_erros_formulario_insercao(
                driver=self.driver, codigo_contrato=self.contrato['codigo_con'],
            )
            form.preencher_data_nascimento()
            #time.sleep(self.wait)
            form.preencher_data_fator()

            aguardar_loading(self.driver)

            try:
                form.preencher_codigo_loja()
            except:
                pass

            if form.estadual:
                try:
                    form.preencher_matricula_proposta_servidor()
                except:
                    pass
                form.preencher_data_renda()
                form.preencher_valor_renda()
                form.preencher_valor_margem()   

                print('Removendo tabela normal')
                self.driver.execute_script("""if(document.getElementsByClassName('selectBMG')[5][0].text == 'Tabela Normal'){document.getElementsByClassName('selectBMG')[5][0].remove()}""")

                self.act.manusear_alerta('aceitar')
                form.preencher_data_admissao()
                self.act.manusear_alerta('aceitar')
                form.preencher_cargo()
                self.act.manusear_alerta('aceitar')
                form.preencher_profissao()
                self.act.manusear_alerta('aceitar')

            else:
                form.preencher_data_renda()

            if alterar_renda:
                form.renda = alterar_renda

            if form.inss:
                if(form.valor_contrato > 15000):
                    valor_renda = '5000'
                else:
                    valor_renda = ''

                form.preencher_valor_renda(valor_renda)
                aguardar_loading(self.chrome_driver)
                form.preencher_uf_beneficio()
                form.preencher_tipo_beneficio()
                form.executar_busca_beneficio()
            elif form.federal:
                form.preencher_valor_renda()
                try:
                    #nao existe mais o campo
                    form.preencher_numero_peculio()
                except:
                    pass   

                try:
                    form.fechar_janela_margem_federal(self.driver)                     
                except:
                    pass    

                self.driver.switch_to.window(self.driver.window_handles[0])
                self.selenium_helper.trocar_frame("rightFrame")     

            if form.federal or form.estadual:
                form.preencher_valor_margem()
                aguardar_loading(self.driver)

            form.preencher_grau_instrucao()

        except UnexpectedAlertPresentException:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],

            )

    def preencher_dados_bancarios(self):
        form: DadosBancarios = DadosBancarios(driver=self.driver, dados=self.contrato)
        self.act.time_out = 0.2

        print("\n<Dados Bancarios>")
        form.preencher_forma_credito()
        aguardar_loading(self.driver)

        if form.is_ordem_pagto:
            try:
                form.selecionar_ordem_pagto()
                aguardar_loading(self.driver)
            except:
                pass

        if not form.is_ordem_pagto:
            form.preencher_numero_banco()

            aguardar_loading(self.driver)

            form.preencher_numero_agencia()

            aguardar_loading(self.driver)

            form.executar_busca_agencia()

            erro_ag = form.verificar_erro_agencia()
            if erro_ag:
                tratar_erros_formulario_insercao(
                    self.driver, self.contrato['codigo_con'],
                    msg_erro='Agência não encontrada')
            try:
                if not form.is_ordem_pagto:
                    form.preencher_numero_conta()
                    form.preencher_digito_conta()

            except NameError as e:
                print("Em preencher numero da conta:", e)

            form.preencher_finalidade_credito()

    def prencher_dados_proposta_fgts(self,conObj):
        print('A atualizar valores de saque')  
        #pdb.set_trace()
        try:
            valor_total_antecipacao = float(self.act.obter_texto('//*[@id="label_ade.valorLiberado"]', By.XPATH))
        except:  
            try:
                valor_total_antecipacao = float(self.act.obter_valor('//*[@id="ade.valorAntecipacaoFgts"]', By.XPATH).replace(',','.'))
                if(valor_total_antecipacao < 200):
                    return False, "Valor liberado minimo de R$200,00 não foi atingido para a operação" 
                else:
                    self.selenium_helper.trocar_frame("topFrame")
            
            except:
                self.selenium_helper.trocar_frame("topFrame")

            try:
                self.act.clicar_elemento('//*[@id="item_barra_funcao"]/span[4]/a[1]', By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="item_barra_funcao"]/span[5]/a[1]', By.XPATH)
                pass

            time.sleep(2)
            self.selenium_helper.trocar_frame("rightFrame")
            self.act.clicar_elemento('//*[@id="buttonLink"]', By.XPATH)
            time.sleep(2)
            self.act.manusear_alerta('aceitar')
            time.sleep(2)
            self.driver.delete_all_cookies()
            time.sleep(2)
            self.driver.refresh()
            raise Exception("Deslogando para atualizar...")      

        valor_original_total_antecipacao = valor_total_antecipacao  
        valor_total_garantia = float(self.act.obter_texto('//*[@id="label_ade.valorEmprestimo"]', By.XPATH))
        valor_contrato = float(self.contrato['valorContrato'])

        if(valor_total_antecipacao < 200):
            return False, "Valor liberado minimo de R$200,00 não foi atingido para a operação"

        elif((valor_contrato >= valor_total_antecipacao) or
             (valor_contrato > 1000 and (valor_contrato / valor_total_antecipacao) > 0.75) or 
             (valor_contrato < 1000 and (valor_contrato / valor_total_antecipacao) > 0.60)):
            self.act.enviar_texto('//*[@id="ade.valorAntecipacaoFgts"]',str(valor_total_garantia).replace('.',','), By.XPATH)
            self.act.clicar_elemento('//*[@id="buttonLink"]', By.XPATH)
            time.sleep(0.5)
        else: 
            self.act.enviar_texto('//*[@id="ade.valorAntecipacaoFgts"]',str(valor_contrato).replace('.',','), By.XPATH)
            self.act.clicar_elemento('//*[@id="buttonLink"]', By.XPATH)
            time.sleep(0.5)
            
            valor_total_antecipacao = float(self.act.obter_texto('//*[@id="label_ade.valorLiberado"]', By.XPATH))

            valor_original = valor_contrato
                      
            while valor_total_antecipacao <= valor_original:
                print('Ajustando valor...')
                valor_contrato += 25
                self.act.enviar_texto('//*[@id="ade.valorAntecipacaoFgts"]',str(valor_contrato).replace('.',','), By.XPATH)
                self.act.clicar_elemento('//*[@id="buttonLink"]', By.XPATH)
                time.sleep(0.5)
                valor_total_antecipacao = float(self.act.obter_texto('//*[@id="label_ade.valorLiberado"]', By.XPATH))

            if(valor_total_antecipacao > valor_original_total_antecipacao):
                self.act.enviar_texto('//*[@id="ade.valorAntecipacaoFgts"]',str(valor_original_total_antecipacao).replace('.',','), By.XPATH)  
                self.act.clicar_elemento('//*[@id="buttonLink"]', By.XPATH)
                time.sleep(0.5)
                valor_total_antecipacao = float(self.act.obter_texto('//*[@id="label_ade.valorLiberado"]', By.XPATH))

        valor_total_antecipacao = float(self.act.obter_texto('//*[@id="label_ade.valorLiberado"]', By.XPATH))
        
        tabela_fgts = self.act.obter_texto('//*[@id="fgtsTable"]', By.XPATH).split('\n') 

        valores_atualizados = {"saque1": {"valor": tabela_fgts[1].split()[4], "data":tabela_fgts[1].split()[2]},
                                "saque2": {"valor":tabela_fgts[2].split()[4], "data":tabela_fgts[2].split()[2]},
                                "saque3": {"valor":tabela_fgts[3].split()[4], "data":tabela_fgts[3].split()[2]},
                                "saque4": {"valor":tabela_fgts[4].split()[4], "data":tabela_fgts[4].split()[2]},
                                "saque5": {"valor":tabela_fgts[5].split()[4], "data":tabela_fgts[5].split()[2]},
                                "saque6": {"valor":tabela_fgts[6].split()[4], "data":tabela_fgts[6].split()[2]},
                                "saque7": {"valor":tabela_fgts[7].split()[4], "data":tabela_fgts[7].split()[2]},
                                }
        
        valor_total = 0
        for i in range(1,8): valor_total += float(valores_atualizados['saque'+str(i)]['valor']) 
        
        payload = {
            "statusPropostaBanco": 'Valores atualizados',
            "codigoCon": conObj._Contrato__dados['codigo_con'],
            "valores_atualizados": json.dumps(valores_atualizados),
            "valor_total": valor_total,
            "valor_total_antecipacao": float(valor_total_antecipacao),
            "key": "f689f1e12a0399fba803cb2365fc362f"
        }

        response = APIDataSource().post_request_v2("enviar-dados-itau-sincronizacao", payload)

        return True, valor_total_antecipacao, valor_total

    def preencher_dados_proposta(self,conObj) -> DadosProposta:
        """
        Preenche os dados da proposta considerando campos e operações
        comuns a novas propostas e a refinanciamentos, bem como específicos
        a cada tipo.
        """
        form: DadosProposta = DadosProposta(self.driver, self.contrato)
        self.act.time_out = 0.0

        print("\n<Dados Proposta>")

        try:
            self.federal = self.contrato['federal']
            self.estadual = self.contrato['estadual']
            self.inss = False
        except:
            self.federal= None
            self.estadual = None
            self.inss = True

        form2: FormDadosProposta = formDadosProposta(driver=self.driver, contrato=conObj)
        form2.verficarTipoTabela()
        margem_erro = 0
        valor_minimo_contrato_carencia = 1500
        
        if form.nova_proposta and form.inss:
            try:
                if(form.possui_carencia and form.valor_contrato >= valor_minimo_contrato_carencia):
                    form.selecionar_carencia_adicional()
                    time.sleep(2)
                    self.act.manusear_alerta('aceitar')

                if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1' or form.tabela_digital == '0' and self.contrato['tipo'] != 'NOVO MARGEM COMPLEMENTAR'):
                    tabela_digital = False
                    # if(form.valor_contrato < valor_minimo_contrato_carencia):
                    #     try:
                    #         # if(form.valor_contrato <= 729):
                    #         #     form2.selecionarTabelaDiretaPortabilidade('7897','Inss/Novo Valor R$ 450 a R$ 729')
                    #         # else:
                    #             form2.selecionarTabelaDiretaPortabilidade('1830','Inss/Novo R$ 730 a R$ 1499')

                    #     except:
                    #         if(self.contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
                    #             if(form.possui_carencia):
                    #                 form2.selecionarTabelaDiretaPortabilidade('1193','Inss/Margem Min 730-Car 120-Tx 1,80')
                    #             else:
                    #                 form2.selecionarTabelaDiretaPortabilidade('1196','Inss/Margem Min 730-Tx 1,80')
                    # else:
                    # if(form.valor_contrato >= 1500):
                    try:
                        form2.selecionarTabelaDiretaPortabilidade('7897','Inss/Novo Valor Min R$1.200-Tx 2,14')
                    except:
                        raise NotFoundResultException('Não encontrou a tabela para ANALFABETO para inserir.')
                    # else:
                    #     form.selecionar_carencia_adicional()
                    #     time.sleep(2)
                    #     self.act.manusear_alerta('aceitar')
                    #     form2.selecionarTabelaDiretaPortabilidade('1829','Inss/Novo R$ 730 a R$ 1499 - Car 120')

                    # tabela = form2.selecionarTabelaPelaTaxa(margem_erro,False,form.possui_carencia)
                    # if not tabela:
                    #     form.selecionar_tabela_carencia(tabela_digital)    
                    time.sleep(2)
                    self.act.manusear_alerta('aceitar')
                else: 
                    if(form.tabela_digital == '0'):
                        tabela_digital = False
                    else:
                        tabela_digital = True
                    nova_formalizazao_ins100 = False
                    # if(self.contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
                    #     nova_formalizazao_ins100 = False
                    # else:
                    #     nova_formalizazao_ins100 = self.data.get_termo_in100(self.contrato['idPessoa'])
                    #remocao da proposta de carencia
                    # if(nova_formalizazao_ins100 and form.valor_contrato >= valor_minimo_contrato_carencia and tabela_digital == True and form.possui_carencia == False):
                    #     print('Atualizou contrato para assinatura digital tipo 1')
                    #     self.data.atualizar_contrato(
                    #             self.contrato['codigo_con'],
                    #             mensagem='Assinatura Digital'
                    #         )
                    form.selecionar_tabela_carencia(tabela_digital, nova_formalizazao_ins100)
            except UnexpectedAlertPresentException as e:
                fechar_janelas_com_erro(self.driver, default_frame="rightFrame")
                tratar_erros_formulario_insercao(
                    self.driver, self.contrato['codigo_con'], msg_erro=str(e.alert_text))

        elif form.refinanciamento and (not form.possui_carencia or self.contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM'):
            
            if(form.possui_carencia and form.valor_contrato):
                form.selecionar_carencia_adicional()
                time.sleep(2)
                self.act.manusear_alerta('aceitar')
            
            if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1' or form.tabela_digital == "0"):
                form.selecionar_taxa_refinanciamento(filtro=lambda taxa: "DIG" not in taxa and "Ret" not in taxa)
            else:
                if(form.possui_carencia):
                    form.selecionar_taxa_refinanciamento(filtro=lambda taxa: "DIG" in taxa and "Car" in taxa) 
                    time.sleep(2)
                    self.act.manusear_alerta('aceitar') 
                else:
                    form.selecionar_taxa_refinanciamento(filtro=lambda taxa: "DIG" in taxa and "Ret" not in taxa)

        elif form.estadual or form.federal:

            if(form.possui_carencia and form.federal):
                form.selecionar_carencia_adicional()
                time.sleep(2)
                self.act.manusear_alerta('aceitar')

            if(form.federal and float(form.taxa_juros) > 1.8):
                if(form.possui_carencia):
                    form2.selecionarTabelaDiretaPortabilidade('1813','DIG Fed.Civil/Novo 1-Car 120-Tx 2,05')
                else:
                    if(form.valor_contrato <= 2000):
                        form2.selecionarTabelaDiretaPortabilidade('7869','DIG Fed.Civil/Novo Valor 500 a 1.999')
                    elif(form.valor_contrato > 2000 and form.valor_contrato < 20000):
                        form2.selecionarTabelaDiretaPortabilidade('2483','DIG Fed.Civil/Novo Valor 2.000 a 20.000')
                    else:
                        form2.selecionarTabelaDiretaPortabilidade('2484','DIG Fed.Civil/Novo Valor Min 20.000')
            else:                
                if(form.estadual):
                    margem_erro = 0.3
                    
                form2.selecionarTabelaPelaTaxa(margem_erro)
                form2.anexarTabelaCarenciaNoContrato()

        time.sleep(3)
        form.apagar_campo_valor_solicitado()
        print("Apagando novamente o campo...")
        form.apagar_campo_valor_solicitado()

        time.sleep(self.wait + 1)
        aguardar_loading(self.driver)

        form.preencher_valor_parcela()
        time.sleep(self.wait)

        aguardar_loading(self.driver)

        # insere termo da IN100
        # if(form.inss):
        #     if(self.data.get_termo_in100(self.contrato['idPessoa'])):
        #         form3: DadosFinais = DadosFinais(self.driver, self.contrato)
        #         form3.anexar_termo_in100()

        # Abre o pop-up de simulção e extrai os valores ideais segundo o prazo
        # do contrato (novo) ou segundo o prazo máximo permitido (refin)
        try:
            form.thread_extrair_valores_pop_up()
        except UnexpectedAlertPresentException as e:
            fechar_janelas_com_erro(self.driver, default_frame="rightFrame")
            tratar_erros_formulario_insercao(self.driver, self.contrato['codigo_con'], msg_erro=str(e.alert_text))

        self.selenium_helper.trocar_frame("rightFrame")
        
        if form.nova_proposta:
            # Armazena os valores ideais para os prazos de 48 e 60x
            #  em vals_ideais
            #pdb.set_trace()
            try:
                self.vals_ideais = form.valores_prazos_ib_consig

                # Atualiza o valor do contrato com o valor ideal segundo o prazo
                self.contrato['valorContrato'] = form.val_contrato_atualizado
                self.mensagem_cliente = "O valor do seu contrato foi alterado para " + self.contrato['valorContrato']

                print("[!] Os seguintes valores do contrato serão alterados: valorContrato => ",
                      self.contrato['valorContrato'])
            except:
                raise NotFoundResultException(' O robô não encontrou condições da tabela disponível, provavelmente a idade do cliente ou tipo de beneficio.')


        time.sleep(self.wait)

        try:
            form.preencher_campo_val_emprestimo()
            tratar_erros_formulario_insercao(self.driver, self.contrato['codigo_con'])
        except:
            if form.refinanciamento or form.portabilidade:
                raise NotFoundResultException(' O robô não encontrou condições da tabela disponível, tente colocoar mais uma vez automático ou tente manual.')

        aguardar_loading(self.driver)

        if form.nova_proposta:
            form.recalcular_valor_liberado()

        aguardar_loading(self.driver)

        form.preencher_valor_parcela()

        if(self.contrato['tipo'] == 'NOVO MARGEM COMPLEMENTAR'):
            self.contrato['valorParcela'] = form.valor_parcela
            if(float(self.contrato['valorContrato'].replace(',','.')) < 680) and 'Valor Min' in form.tabela_selecionada:
                form.apagar_campo_valor_solicitado()
                form.tabela_selecionada = ''
                self.preencher_dados_proposta(conObj)
            elif(float(self.contrato['valorContrato'].replace(',','.')) > 680) and '450 a 679' in form.tabela_selecionada:
                form.apagar_campo_valor_solicitado()
                form.tabela_selecionada = ''
                self.preencher_dados_proposta(conObj)


        if form.refinanciamento:
            form.executar_caculo_valores_refinanciamento()

        aguardar_loading(self.driver)

        form.preencher_prazo_contrato()

        tratar_erros_formulario_insercao(
            driver=self.driver,
            vals_atualizados=self.vals_ideais,
            codigo_contrato=self.contrato['codigo_con'],

        )
        if form.refinanciamento:
            form.extrair_valor_maximo_liberado()
            self.contrato['valorContrato'] = form.valor_liberado_maximo
            print("[!] Valor do contrato alterado:", self.contrato['valorContrato'])
            self.contrato['prazo'] = form.prazo_contrato_atualizado

        aguardar_loading(self.driver)

        if form.nova_proposta:
            form.executar_calculo_comissao()

        return form

    def preencher_dados_pessoais(self):
        form: DadosPessoais = DadosPessoais(self.driver, self.contrato)
        self.act.time_out = 0.2

        print("\n<Dados Pessoais>")

        form.preencher_nome()
        form.preencher_sexo()
        form.preencher_estado_civil()

        aguardar_loading(self.driver)

        form.preencher_nome_conjuge()
        form.preencher_nome_mae()
        form.preencher_nome_pai()
        form.preencher_cidade_nascimento()
        form.preencher_uf_nascimento()
        form.preencher_nacionalidade()
        form.preencher_tipo_identidade()
        form.preencher_emissor()
        form.preencher_uf_identidade()
        form.preencher_numero_identidade()
        form.preencher_data_emissao()

    def preencher_dados_endereco(self):
        form: DadosEndereco = DadosEndereco(self.driver, self.contrato)
        self.act.time_out = 0.2

        print("\n<Dados Endereço>")
        form.preencher_cep()
        form.executar_busca_cep()

        if form.logradouro_sem_numero:
            form.check_sem_numero()
        else:
            form.preencher_numero()

        form.preencher_logradouro()
        form.preencher_bairro()
        form.preencher_complemento()
        form.preencher_ddd_telefone()
        form.preencher_numero_telefone()
        form.preencher_ddd_celular()
        form.preencher_numero_celular()

    def preencher_dados_finais(self):
        form: DadosFinais = DadosFinais(self.driver, self.contrato)
        form2: DadosBancarios = DadosBancarios(driver=self.driver, dados=self.contrato)
        
        self.act.time_out = 0.2

        if form2.is_ordem_pagto:
            form2.selecionar_ordem_pagto()
            aguardar_loading(self.driver)
            form2.preencher_numero_agencia()
            aguardar_loading(self.driver)
            form2.executar_busca_agencia()

        debug.debugger()
        print("\n<Dados Finais>")
        #form.selecionar_rogado_nao()
        time.sleep(self.wait)

        form.preencher_nome_vendedor()
        form.preencher_forma_envio()
        time.sleep(self.wait)

        try:
            if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1' or form.tabela_digital == '0'):
                try:
                    form.selecionar_if_sim()
                except:
                    pass
            else:
                form.selecionar_if_nao()
        except:
            pass

        if form.necessario_anexar_contracheque:
            self.data.get_docs_contratos(self.contrato['codigo_con'])
            if(form.estadual):
                try:
                    if(self.contrato['sigla_orgao'].upper() == 'SP'):
                        form.anexar_contracheque_servidor_sp()
                    else:
                        form.anexar_contracheque_servidor_mt() 
                except:
                    pass
            else:
                form.anexar_contracheque()
                

            aguardar_loading(self.driver)

        #time.sleep(self.wait + 1)
        if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1'):
            try:
                form.selecionar_rogado_sim()
            except:
                pass
        else:
            form.selecionar_rogado_nao()

        
        try:
            self.driver.execute_script('mesmoAgente(true)');
        except:
            pass
            
        time.sleep(self.wait + 2)

        print('Aguardando confirmação final da inserção...')
        form.clicar_confirmar()
        #time.sleep(self.wait + 3)
        try:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,
            )
        except DadosBancariosException:
            self.preencher_dados_bancarios()
            self.preencher_dados_proposta(Contrato(self.contrato))
            self.driver.execute_script('$("#confirmar").click()')
            time.sleep(self.wait)

        except PreenchimentoException:
            DadosPessoais(self.driver, self.contrato).preencher_nome_pai()
            self.driver.execute_script('$("#confirmar").click()')
            time.sleep(self.wait)

        except ErroDadosProposta as e:
            print(e)
            debug.debugger()
            self.preencher_dados_iniciais(alterar_renda="5000.00")
            self.preencher_dados_proposta()
            print('Aguardando confirmação final da inserção...')
            form.clicar_confirmar()

        except TaxaSuperiorException:
            form: DadosProposta = DadosProposta(self.driver, self.contrato)

            valor_float_contrato = float(self.contrato['valorContrato'].replace(',','.'))
            valor_somar = (valor_float_contrato /1000)*7.5
            valor_final_contrato = valor_somar + valor_float_contrato
            preencher_novo_valor = str(valor_final_contrato).replace('.',',')

            form.apagar_campo_valor_solicitado()
            form.preencher_campo_novo_val_emprestimo(preencher_novo_valor)
            form.preencher_valor_parcela()
            form.preencher_prazo_contrato()
            

        try:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,
            )
        except DadosBancariosException:
            print("Não conseguiu preencher os dados bancários")
            self.data.atualizar_contrato(
                self.contrato['codigo_con'],
                mensagem="Conferir dados do contrato",
                erro="Agência não foi encontrada",
                observacao="Não foi possível prosseguir com a proposta, "
                           "pois a agência não foi encontrada no sistema do banco!",
            )

    def finalizar_insercao_popup(self):
        """
        Lida com as janelas de confirmação que são abertas ao fim da inserção
        """
        DadosFinais.executar_script_pop_up(self.driver)
        #time.sleep(self.wait + 1)
        try:
        	form: DadosIniciais = DadosIniciais(driver=self.driver, dados=self.contrato)
        	if form.federal:
	            try:
	                form.fechar_janela_margem_federal(self.driver)                     
	            except:
	                pass    

	            self.driver.switch_to.window(self.driver.window_handles[0])
	            self.selenium_helper.trocar_frame("rightFrame")    
        except:
        	pass

        

        try:
            DadosFinais.abrir_confirmar_janelas_finais(
                driver=self.driver,
                script_abrir_janela="nenhumArquivoAnexoPopUp()",
                script_confirmar="confirmCancel()"
            )
            DadosFinais.abrir_confirmar_janelas_finais(
                driver=self.driver,
                script_confirmar="confirmOk()"
            )
            DadosFinais.janela_confirmar_insercao(
                driver=self.driver,
                act=self.act,
            )

            #time.sleep(self.wait + 2)

        except UnexpectedAlertPresentException as e:
            print(e)
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,

            )

    def buscar_ade(self) -> str:
        dados_finais: DadosFinais = DadosFinais(self.driver, self.contrato)

        dados_finais.buscar_ade_final()
        
        if not dados_finais.ade:
            dados_finais.verificar_erro_ib_consig()
            if dados_finais.erro_aplicacao == 'ConsigExceptionList':
                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem="Conferir dados do contrato",
                    erro='Valores do contrato diferentes do ibConsig',
                    observacao='Conferir o valor da parcela do contrato.',

                )
                raise Exception("Pulando o contrato!")
            elif dados_finais.erro_aplicacao:
                raise Exception(dados_finais.erro_aplicacao)
            else:
                raise Exception("ADE não foi encontrada. Contrato não foi atualizado")

        # if(self.contrato['inss'] == True):
        #     dados_finais.apagar_arquivo_in100()

        return dados_finais.ade

    def atualizar_contrato(self, codigo_contrato, **kwargs):

        print(f"Entrou função final... Atualizando contrato com:\n{kwargs}")

        self.data.atualizar_contrato(
            codigo_contrato=codigo_contrato,
            dados=kwargs,
            raise_erro=True
        )
        if not kwargs.get("idRoboLog", False):
            return

        self.api_registrar_log_robo(
            log=kwargs,
            status=0
        )

if __name__ == '__main__':
    InsercaoIbConsig.iniciar_horario_comercial(nome_instancia="Principal")
