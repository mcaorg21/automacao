from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.ibConsig.IbConsigInsercao.auto.FormDadosFinais import *
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formDadosBancarios import formDadosBancarios
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formDadosEndereco import formDadosEndereco
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formDadosIniciais import formDadosIniciais
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formDadosPessoais import formDadosPessoais
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formDadosProposta import formDadosProposta
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formPortabilidade import formPortabilidade
from sites.ibConsig.libs.auto.forms.FormDadosBancarios import FormDadosBancarios
from sites.ibConsig.libs.auto.forms.FormDadosEndereço import FormDadosEndereco
from sites.ibConsig.libs.auto.forms.FormDadosIniciais import FormDadosIniciais
from sites.ibConsig.libs.auto.forms.FormsDadosPessoais import FormDadosPessoais
from sites.ibConsig.libs.auxiliares.ErrorHandler import ErrorHandlers, ErrorHandler
from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato
from sites.ibConsig.libs.auto.forms.FormDadosProposta import FormDadosProposta
from sites.ibConsig.libs.auxiliares.ib_auxiliares import *
import PATHS
from sites.ibConsig.IbConsigInsercao.auto.portabilidade.formIdentificacao import formIdentificacao
from sites.baseRobos.manager import Manager

from sites.ibConsig.IbConsigInsercao.data.IbConsigData import (
    IbConsigData
)

from sites.ibConsig.IbConsigInsercao.data.portabilidade.DadosPortabilidade import (
    DadosPortabilidade
)

from sites.baseRobos.core.DebugTools import DebugTools
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig
from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import *
from sites import ID_ROBOS
import time,pdb
from pprint import pprint

debug = DebugTools(debugging=False)
HORARIO_COMERCIAL = 7, 23


class InsercaoIbConsigPortabilidade(Manager):

    from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato

    ID_BANCO = 1
    ID_ROBO = ID_ROBOS['ibConsig']['inserir']

    captcha_path: str = str(Path(PATHS.project_path() + "/ibConsig/IbConsigInsercao/static"))

    def __init__(self, **kwargs):
        super().__init__()
        self.user_chrome_path: str = kwargs.get('chrome_user', PATHS.chrome_user("IbConsigInsercao"))
        Manager.criar_pasta_usuario_chrome(self.user_chrome_path)
        self.set_options('--ignore-ssl-errors', 'log-level=3', self.user_chrome_path)
        self.init_chrome_driver(import_driver=kwargs.get("extern_driver", False))

        self.data: IbConsigData = IbConsigData()
        self.dataPortabilidade: DadosPortabilidade = DadosPortabilidade()

        self.act: SeleniumActions = SeleniumActions(self.driver, time_out=0.3)
        self.act.message = "Elemento não encontrado."

        self.selenium_helper: SeleniumHelper = SeleniumHelper(self.driver)

        self.contrato: dict = {}
        self.vals_ideais: dict = {}

        self.wait = 0.2

        self.data.ordem_busca = kwargs.get('ordem', 'asc')
        self.data.contrato_teste = kwargs.get('contrato_teste', '')

        # self.usuario = kwargs.get("usuario", "saulo.1873p")
        # self.senha = kwargs.get("senha", "Marcelo@40")
        self.usuario = "mca1873"
        self.senha = "t909176@"
        dados_login = {'usuario': self.usuario, 'senha': self.senha,
                       'driver': self.driver}
        self.login = IbConsig.login_fact(**dados_login)

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, nome_instancia):

        definir_nome_robo(f'Itau - Inserção {nome_instancia}')

        run = InsercaoIbConsigPortabilidade()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

        while not self.login():
            print('Tentativa de Login')

        while True:
            self.inserir_contratos()
            sleep(5)
            self.driver.refresh()

    def inserir_contratos(self):
        try:
            print(f"\nINÍCIO: {dt.now()}\n")
            self.driver.refresh()

            # Buscar detalhes do contrato
            # self.contrato = self.data.get_contrato_teste()
            # self.contrato = self.data.get_contrato_uconecte(contrato['codigo_con'])
            contratos = self.data.buscar_lista_a_inserir()
            
            for contrato in contratos:
                # Buscar detalhes do contrato
                self.contrato = self.data.get_contrato_uconecte(contrato['codigo_con'])
            
                conObj: Contrato = Contrato(self.contrato)

                if not IbConsig.esta_logado(self.driver):
                    self.login()

                if not IbConsig.tela_inicial(self.driver):
                    debug.warning(
                        "[!] Tela Inicial Não Foi Carregada [!] "
                        "\nAperte qualquer tecla para seguir")
                    input(">>> ")

                print(f"\nIniciando inserção do contrato:",
                      self.contrato['codigo_con'])

                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem='Inserir contrato')

                self.inserir_contrato_financiamento(conObj=conObj)

        except ErroRetornarFila as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.message}",
                status=0
            )
        except RestricaoException as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.message}",
                status=0
            )
            self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem='Reprovado a Conferir',
                    observacao=e.message,
                    )
        except UnexpectedAlertPresentException as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.alert_text}",
                status=0
            )
            self.act.manusear_alerta('aceitar')

        except Exception as e:
            debug.exception(e)
            self.manager_error_log(e)
            fechar_janelas_com_erro(self.driver)
            self.data.api_registrar_log_robo(log=f"ERRO: {e}", status=0)

    def inserir_contrato_financiamento(self, conObj: Contrato):
        print(f"Trabalhando no contrato portabilidade: {self.contrato['codigo_con']}")
        self.contrato['entidade'] = filtrar_entidade(conObj.contrato)
        self.act.retornar_janela_principal()
        preencher_dados = self.preencherFormIdentificacao(contrato=conObj)
        
        if preencher_dados:
            try:
                self.preencher_dados_iniciais(conObj)
                aceitar_pendencia(self.driver, self.selenium_helper)
                self.preencherFormPortabilidade(conObj)
                self.preencher_dados_bancarios(contrato=conObj)
                self.preencher_dados_proposta(contrato=conObj)
                self.preencher_dados_pessoais(contrato=conObj)
                self.preencher_dados_endereco(contrato=conObj)
                aceitar_pendencia(self.driver, self.selenium_helper)
                self.preencher_dados_finais(contrato=conObj)
                self.finalizar_insercao_popup()
                self.buscar_ade(contrato=conObj)
                conObj.validarDadosInsercao()

                self.dataPortabilidade.atualizar_aguardando_gerar_contrato(
                    contrato=conObj.contrato,
                    tabelaBanco=conObj.retornarDadoAdicional("tabelaBanco"),
                    ade=conObj.retornarDadoAdicional("ADE"),
                    ade_refin_portabilidade=conObj.retornarDadoAdicional("ADE_PORTABILIDADE"),
                    valorAtualizado=conObj.retornarDadoAdicional("novoValorLiquido")
                )

                print('Iniciando próximo contrato...')

            except UnexpectedAlertPresentException as e:
                print("Alerta inesperado: ", e.alert_text)
                tratar_erros_formulario_insercao(
                    self.driver, self.contrato['codigo_con'],
                    vals_atualizados=self.vals_ideais,
                )

        else:
            return 0
        time.sleep(self.wait)

    def preencherFormIdentificacao(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+------------- Dados Identificação -------------+")
        print("+-----------------------------------------------+")
        form = formIdentificacao(self.driver, contrato)
        errorHandler: ErrorHandler = ErrorHandlers.formularioIdentificacao(
            codigoCon=contrato.codigo)

        self.driver.switch_to.frame("leftFrame")
        form.clicarBtnMenuExpandir()
        form.clicarBtnMenuExpandido()

        SeleniumHelper(self.driver).trocar_frame("rightFrame")

        form.preencherInputEntidade()
        form.selecionarSelectServico("1")
        form.preencherInputCpf()
        form.preencherInputMatricula()
        form.preencherInputDataNascimento()

        while True:
            errorHandler.flush()
            form.resolverCaptcha()

            if form.erroApiCaptcha:
                print("Erro na requisição do Captcha")
                continue

            form.preencherCaptcha()
            form.clicarConfirmar()
            form.clicarSerguirInsercao()
            aguardar_loading(self.driver)

            errorHandler.msgErro = form.verificarDivErro()
            errorHandler.avaliarTratativasDeErro()
            try:
                resultado = errorHandler.aplicarTratativasDeErro()
                return resultado
            except PreenchimentoException as e:
                print("Captcha não foi preenchido corretamente:", e.message)
                continue

            return True

    def preencher_dados_iniciais(self, contrato: Contrato):
        print("+------------------------------------------+")
        print("+------------- Dados Iniciais -------------+")
        print("+------------------------------------------+")
        form: FormDadosIniciais = formDadosIniciais(contrato, self.driver)
        try:
            form.preencherDataNascimento()

            aguardar_loading(self.chrome_driver)

            form.preencherDataFator()

            aguardar_loading(self.driver)

            form.preencherCodigoLoja()
            form.preencherDataRenda()
            form.preencherValorRenda()

            aguardar_loading(self.chrome_driver)

            try:
                form.selecionarUFBeneficio()
            except:
                pass

            form.preencherTipoBeneficio()
            form.selecionarGrauInstrucao()

        except UnexpectedAlertPresentException:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'])

    def preencherFormPortabilidade(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+------------- Dados Portabilidade -------------+")
        print("+-----------------------------------------------+")
        form = formPortabilidade(self.driver, contrato)
        form.preencherIptSaldoDevedor()
        form.preencherIptValorParcela()
        form.preencherIptQtdParcelas()
        form.preencherIptQtdParcelasPagas()
        tratar_erros_formulario_insercao(self.driver,contrato.codigo)
        aguardar_loading(self.driver)
        form.preencherIptNoContrato()
        form.preencherIptUltimoVencimento()
        form.preencherIitPrimeiroVencimento()
        aguardar_loading(self.driver)
        form.preencherIptCodigoBanco()

    def preencher_dados_bancarios(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+--------------- Dados Bancários ---------------+")
        print("+-----------------------------------------------+")

        form: FormDadosBancarios = formDadosBancarios(self.driver, contrato)
        form.selecionarFormaCredito()

        form.preencherCodigoBanco()

        aguardar_loading(self.driver)

        form.preencherNoAgencia()

        aguardar_loading(self.driver)

        time.sleep(self.wait)

        erro_ag = form.verificar_erro_agencia(self)
        if erro_ag:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                msg_erro='Agência não encontrada')

        form.preencherDvAgencia()

        form.preencherNoConta()
        #form.preencherDvConta()

        loc = "#dadosBancarios\\\\.contaDv"
        self.selenium_helper.atribuir_valor_campo_jquery(loc, contrato.banco.digitoConta)

        form.selecionarContaCredito()

    def preencher_dados_proposta(self, contrato: Contrato):
        print("+------------------------------------------------+")
        print("+---------------- Dados Proposta ----------------+")
        print("+------------------------------------------------+")
        form: FormDadosProposta = formDadosProposta(driver=self.driver, contrato=contrato)
        form.filtroTabelaCarencia = lambda taxa: "DIG" in taxa
        form.verficarTipoTabela()

        if(float(contrato._Contrato__dados['dados_portabilidade']['saldoDevedorFinal']) < 2000):
            form.selecionarTabelaDiretaPortabilidade('7935','DIG Inss/Refin Port-1000-1999Tx1,80-1,70')
        else:
            form.selecionarTabelaPelaTaxa()
            form.anexarTabelaCarenciaNoContrato()

        form.apagarValorSolicitado()
        form.preencherValorParcela()
        form.clicarBtnSimular()

        form.extrairValorJanelaSimulacaoEmprestimo()
        
        retorna_valor = form.atualizarValorSolicitadoPortabilidade()
        if retorna_valor == False: 
            raise ErroRetornarFila('Valor não disponível no prazo original pedido.')
        
        form.preencherValorSolicitado()
        form.preencherValorParcela()
        form.preencherNumeroPrestacoes()

    def preencher_dados_pessoais(self, contrato: Contrato):
        print("+------------------------------------------------+")
        print("+---------------- Dados Pessoais- ---------------+")
        print("+------------------------------------------------+")

        form: FormDadosPessoais = formDadosPessoais(self.driver, contrato)
        #form.preencherNome()
        form.preencherSexo()
        form.selecionarEstadoCivil()

        aguardar_loading(self.driver)

        if(self.contrato['estadoCivil'] != 'V' and self.contrato['estadoCivil'] != 'S' and self.contrato['estadoCivil'] != 'I'):
            form.preencherNomeConjuge()

        form.preencherNomeMae()
        form.preencherNomePai()
        form.preencherCidadeNascimento()
        form.selecionarUFNascimento()

        form.selecionarNacionalidade()
        form.selecionarTipoIdentidade()
        form.selecionarOrgaoEmissor()
        form.selecionarUFIdentidade()
        form.preencherNumeroIdentidade()
        form.preencherDataEmissao()

    def preencher_dados_endereco(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+--------------- Dados Endereço ----------------+")
        print("+-----------------------------------------------+")
        form: FormDadosEndereco = formDadosEndereco(self.driver, contrato)
        self.act.time_out = 0.2

        form.preencherCep()
        aguardar_loading(self.driver)

        try:
            form.preencherLogradouro2()
        except:
            form.preencherLogradouro()
            pass

        if form.logradouroSemNumero:
            form.marcarSemNumero()
        else:
            try:
                form.preencherNumero()
            except:
                pass

        form.preencherBairro()
        form.preencherComplemento()
        form.preencheDddTelefone()
        form.preencheNoTelefone()
        form.preencheDddCelular()
        form.preencheNoCelular()

    def preencher_dados_finais(self, contrato: Contrato):
        print("+------------------------------------------------+")
        print("+----------------- Dados Finais -----------------+")
        print("+------------------------------------------------+")
        form: DadosFinais = DadosFinais(self.driver, self.contrato)
        self.act.time_out = 0.2

        form.selecionar_rogado_nao()
        time.sleep(self.wait)

        form.preencher_nome_vendedor()
        form.preencher_forma_envio()
        time.sleep(self.wait)

        form.selecionar_if_nao()
        form.selecionar_rogado_nao()
        time.sleep(self.wait + 2)
        print('Aguardando confirmação final da inserção...')
        form.clicar_confirmar()
        time.sleep(self.wait + 3)

        tratar_erros_formulario_insercao(
            self.driver, self.contrato['codigo_con'],
            vals_atualizados=self.vals_ideais,
        )

    def finalizar_insercao_popup(self):
        """
        Lida com as janelas de confirmação que são abertas ao fim da inserção
        """
        DadosFinais.executar_script_pop_up(self.driver)
        time.sleep(self.wait + 1)

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

            time.sleep(self.wait + 2)

        except UnexpectedAlertPresentException as e:
            print(e)
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,

            )

    def buscar_ade(self, contrato: Contrato):
        dados_finais: DadosFinais = DadosFinais(self.driver, self.contrato)

        dados_finais.buscar_ade_portabilidade()
        dados_finais.buscar_ade() 

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

        contrato.incluirDadoAdicional("ADE", dados_finais.ade)
        contrato.incluirDadoAdicional("ADE_PORTABILIDADE", dados_finais.ade_refin_portabilidade)

class InsercaoIbConsigPortabilidadeFila(Manager):

    from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato

    from sites.ibConsig.IbConsigInsercao.data.portabilidade.DadosPortabilidade import (
        DadosPortabilidade
    )

    ID_BANCO = 1
    ID_ROBO = ID_ROBOS['ibConsig']['inserir']

    captcha_path: str = str(Path(PATHS.project_path() + "/ibConsig/IbConsigInsercao/static"))

    def __init__(self, **kwargs):
        super().__init__()
        self.user_chrome_path: str = kwargs.get('chrome_user', PATHS.chrome_user("IbConsigInsercao"))
        Manager.criar_pasta_usuario_chrome(self.user_chrome_path)
        self.set_options('--ignore-ssl-errors', 'log-level=3', self.user_chrome_path)
        self.init_chrome_driver(import_driver=kwargs.get("extern_driver", False))

        self.data: IbConsigData = IbConsigData()
        self.dataPortabilidade: DadosPortabilidade = DadosPortabilidade()

        self.act: SeleniumActions = SeleniumActions(self.driver, time_out=0.3)
        self.act.message = "Elemento não encontrado."

        self.selenium_helper: SeleniumHelper = SeleniumHelper(self.driver)

        self.contrato: dict = {}
        self.vals_ideais: dict = {}

        self.wait = 0.2

        self.data.ordem_busca = kwargs.get('ordem', 'asc')
        self.data.contrato_teste = kwargs.get('contrato_teste', '')

        # self.usuario = kwargs.get("usuario", "saulo.1873p")
        # self.senha = kwargs.get("senha", "Marcelo@40")
        self.usuario = "mca1873"
        self.senha = "t909176@"
        dados_login = {'usuario': self.usuario, 'senha': self.senha,
                       'driver': self.driver}
        self.login = IbConsig.login_fact(**dados_login)

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, nome_instancia):

        definir_nome_robo(f'Itau - Inserção {nome_instancia}')

        run = InsercaoIbConsigPortabilidade()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

        while not self.login():
            print('Tentativa de Login')

        while True:
            self.inserir_contratos()
            sleep(5)
            self.driver.refresh()

    def inserir_contratos(self):
        try:
            print(f"\nINÍCIO: {dt.now()}\n")
            self.driver.refresh()

            # Buscar detalhes do contrato
            # self.contrato = self.data.get_contrato_teste()
            # self.contrato = self.data.get_contrato_uconecte(contrato['codigo_con'])
            contratos = self.data.buscar_lista_a_inserir()
            
            for contrato in contratos:
                # Buscar detalhes do contrato
                self.contrato = self.data.get_contrato_uconecte(contrato['codigo_con'])
            
                conObj: Contrato = Contrato(self.contrato)

                if not IbConsig.esta_logado(self.driver):
                    self.login()

                if not IbConsig.tela_inicial(self.driver):
                    debug.warning(
                        "[!] Tela Inicial Não Foi Carregada [!] "
                        "\nAperte qualquer tecla para seguir")
                    input(">>> ")

                print(f"\nIniciando inserção do contrato:",
                      self.contrato['codigo_con'])

                self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem='Inserir contrato')

                self.inserir_contrato_financiamento(conObj=conObj)

        except ErroRetornarFila as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.message}",
                status=0
            )
        except RestricaoException as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.message}",
                status=0
            )
            self.data.atualizar_contrato(
                    self.contrato['codigo_con'],
                    mensagem='Reprovado a Conferir',
                    observacao=e.message,
                    )
        except UnexpectedAlertPresentException as e:
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.alert_text}",
                status=0
            )
            self.act.manusear_alerta('aceitar')

        except NotFoundResultException as e:
            print("Erro encontrado: {}".format(e.message))
            self.data.atualizar_contrato(
                self.contrato['codigo_con'],
                erro=f"Erro encontrado: {e.message}", mensagem='Conferir dados do contrato',
                observacao=e.message,

            )
            self.data.api_registrar_log_robo(
                log=f"ERRO: {e.message}",
                status=0
            )

        except Exception as e:
            debug.exception(e)
            self.manager_error_log(e)
            fechar_janelas_com_erro(self.driver)
            self.data.api_registrar_log_robo(log=f"ERRO: {e}", status=0)

    def inserir_contrato_financiamento(self, conObj: Contrato):
        print(f"Trabalhando no contrato portabilidade: {self.contrato['codigo_con']}")
        self.contrato['entidade'] = filtrar_entidade(conObj.contrato)
        self.act.retornar_janela_principal()
        preencher_dados = InsercaoIbConsigPortabilidadeFila.preencherFormIdentificacao(self,contrato=conObj)
        
        if preencher_dados:
            try:
                InsercaoIbConsigPortabilidadeFila.preencher_dados_iniciais(self,conObj)
                aceitar_pendencia(self.driver, self.selenium_helper)
                InsercaoIbConsigPortabilidadeFila.preencherFormPortabilidade(self,conObj)
                InsercaoIbConsigPortabilidadeFila.preencher_dados_bancarios(self,contrato=conObj)
                InsercaoIbConsigPortabilidadeFila.preencher_dados_proposta(self,contrato=conObj)
                InsercaoIbConsigPortabilidadeFila.preencher_dados_pessoais(self,contrato=conObj)
                InsercaoIbConsigPortabilidadeFila.preencher_dados_endereco(self,contrato=conObj)
                aceitar_pendencia(self.driver, self.selenium_helper)
                InsercaoIbConsigPortabilidadeFila.preencher_dados_finais(self,contrato=conObj)
                InsercaoIbConsigPortabilidadeFila.finalizar_insercao_popup(self)
                InsercaoIbConsigPortabilidadeFila.buscar_ade(self,contrato=conObj)
                conObj.validarDadosInsercao()
                DadosPortabilidade.atualizar_aguardando_gerar_contrato_portabilidade(self,contrato=conObj.contrato,tabelaBanco=conObj.retornarDadoAdicional("tabelaBanco"),ade=conObj.retornarDadoAdicional("ADE"),ade_refin_portabilidade=conObj.retornarDadoAdicional("ADE_PORTABILIDADE"),valorAtualizado=conObj.retornarDadoAdicional("novoValorLiquido"))

                print('Finalizando inserção do contrato...')

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

            except UnexpectedAlertPresentException as e:
                print("Alerta inesperado: ", e.alert_text)
                tratar_erros_formulario_insercao(self.driver, self.contrato['codigo_con'],vals_atualizados=self.vals_ideais, msg_erro = e.alert_text)

        else:
            return 0
        time.sleep(self.wait)

    def inserir_contrato_financiamento_aumento(self, conObj: Contrato):
        print(f"Trabalhando no contrato aumento: {self.contrato['codigo_con']}")
        self.contrato['entidade'] = filtrar_entidade(conObj.contrato)

        try:
            InsercaoIbConsigPortabilidadeFila.preencher_dados_iniciais(self,conObj)
            aceitar_pendencia(self.driver, self.selenium_helper)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_bancarios(self,contrato=conObj)
            #InsercaoIbConsigPortabilidadeFila.preencher_dados_proposta(self,contrato=conObj)
            self.preencher_dados_proposta(conObj)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_pessoais(self,contrato=conObj)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_endereco(self,contrato=conObj)
            aceitar_pendencia(self.driver, self.selenium_helper)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_finais(self,contrato=conObj)
            InsercaoIbConsigPortabilidadeFila.finalizar_insercao_popup(self)
            InsercaoIbConsigPortabilidadeFila.buscar_ade_outros(self,contrato=conObj)
            conObj.validarDadosInsercao()
            DadosPortabilidade.atualizar_aguardando_gerar_contrato(self,contrato=conObj.contrato,tabelaBanco=conObj.retornarDadoAdicional("tabelaBanco"),ade=conObj.retornarDadoAdicional("ADE"),valorAtualizado=conObj.contrato['valorContrato'],parcelaAtualizada=conObj.contrato['valorParcela'])

            print('Finalizando inserção do contrato...')

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
        except UnexpectedAlertPresentException as e:
            print("Alerta inesperado: ", e.alert_text)
            tratar_erros_formulario_insercao(
                    self.driver, self.contrato['codigo_con'],
                    vals_atualizados=self.vals_ideais, msg_erro = e.alert_text
                )

        else:
            return 0
        time.sleep(self.wait)

    def inserir_contrato_financiamento_fgts(self, conObj: Contrato):
        print(f"Trabalhando no contrato FGTS: {self.contrato['codigo_con']}")
        self.contrato['entidade'] = '11-'

        try:

            InsercaoIbConsigPortabilidadeFila.preencher_dados_iniciais_fgts(self,conObj)
              
            retorno = self.prencher_dados_proposta_fgts(conObj)  

            if(retorno[0] == False):
                return retorno  

            valor_contrato = retorno[1] 
            valor_parcela = retorno[2] 
                
            retorno = InsercaoIbConsigPortabilidadeFila.preencher_dados_bancarios(self,contrato=conObj)

            if(retorno[0] == False):
                return retorno   

            InsercaoIbConsigPortabilidadeFila.preencher_dados_pessoais(self,contrato=conObj)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_endereco(self,contrato=conObj)
            InsercaoIbConsigPortabilidadeFila.preencher_dados_finais(self,contrato=conObj)           
            InsercaoIbConsigPortabilidadeFila.finalizar_insercao_popup(self)
            InsercaoIbConsigPortabilidadeFila.buscar_ade_outros(self,contrato=conObj)
            conObj.validarDadosInsercao()
            DadosPortabilidade.atualizar_aguardando_gerar_contrato(self,contrato=conObj.contrato,tabelaBanco=conObj.retornarDadoAdicional("tabelaBanco"),ade=conObj.retornarDadoAdicional("ADE"),valorAtualizado=valor_contrato,parcelaAtualizada=valor_parcela)

            print('Finalizando inserção do contrato...')

            return True, None

        except UnexpectedAlertPresentException as e:
            print("Alerta inesperado: ", e.alert_text)
            self.act.manusear_alerta('aceitar')
            return False,e.alert_text

        else:
            return 0

    def preencherFormIdentificacao(self, contrato: Contrato):

        print("+-----------------------------------------------+")
        print("+------------- Dados Identificação -------------+")
        print("+-----------------------------------------------+")
        form = formIdentificacao(self.driver, contrato)
        errorHandler: ErrorHandler = ErrorHandlers.formularioIdentificacao(
            codigoCon=contrato.codigo)

        self.driver.switch_to.frame("leftFrame")
        form.clicarBtnMenuExpandir()

        try:
            form.clicarBtnMenuExpandido2()
        except:
            form.clicarBtnMenuExpandido()

        SeleniumHelper(self.driver).trocar_frame("rightFrame")

        form.preencherInputEntidade()
        form.selecionarSelectServico("1")
        form.preencherInputCpf()
        form.preencherInputMatricula()
        form.preencherInputDataNascimento()

        while True:
            errorHandler.flush()
            form.resolverCaptcha()

            if form.erroApiCaptcha:
                print("Erro na requisição do Captcha")
                continue

            form.preencherCaptcha()
            form.clicarConfirmar()
            form.clicarSerguirInsercao()
            aguardar_loading(self.driver)

            errorHandler.msgErro = form.verificarDivErro()
            errorHandler.avaliarTratativasDeErro()
            try:
                resultado = errorHandler.aplicarTratativasDeErro()
                return resultado
            except PreenchimentoException as e:
                print("Captcha não foi preenchido corretamente:", e.message)
                continue

            return True

    def preencherFormIdentificacaoAumento(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+------------- Dados Identificação -------------+")
        print("+-----------------------------------------------+")
        form = formIdentificacao(self.driver, contrato)
        errorHandler: ErrorHandler = ErrorHandlers.formularioIdentificacao(
            codigoCon=contrato.codigo)

        self.driver.switch_to.frame("leftFrame")
        form.clicarBtnMenuExpandir()
        form.clicarBtnMenuExpandido()

        SeleniumHelper(self.driver).trocar_frame("rightFrame")

        form.preencherInputEntidade()
        form.selecionarSelectServico("1")
        form.preencherInputCpf()
        form.preencherInputMatricula()
        form.preencherInputDataNascimento()

        while True:
            errorHandler.flush()
            form.resolverCaptcha()

            if form.erroApiCaptcha:
                print("Erro na requisição do Captcha")
                continue

            form.preencherCaptcha()
            form.clicarConfirmar()
            form.clicarSerguirInsercao()
            aguardar_loading(self.driver)

            errorHandler.msgErro = form.verificarDivErro()
            errorHandler.avaliarTratativasDeErro()
            try:
                resultado = errorHandler.aplicarTratativasDeErro()
                return resultado
            except PreenchimentoException as e:
                print("Captcha não foi preenchido corretamente:", e.message)
                continue

            return True

    def preencher_dados_iniciais(self, contrato: Contrato):
        print("+------------------------------------------+")
        print("+------------- Dados Iniciais -------------+")
        print("+------------------------------------------+")
        form: FormDadosIniciais = formDadosIniciais(contrato, self.driver)
        try:
            form.preencherDataNascimento()

            aguardar_loading(self.chrome_driver)

            form.preencherDataFator()

            aguardar_loading(self.driver)

            try:
                form.preencherCodigoLoja()
            except:
                pass
                
            form.preencherDataRenda()
            form.preencherValorRenda()

            aguardar_loading(self.chrome_driver)

            try:
                form.selecionarUFBeneficio()
            except:
                pass
                
            form.preencherTipoBeneficio()
            form.selecionarGrauInstrucao()

        except UnexpectedAlertPresentException:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'])

    def preencher_dados_iniciais_fgts(self, contrato: Contrato):
        print("+------------------------------------------+")
        print("+------------- Dados Iniciais -------------+")
        print("+------------------------------------------+")
        form: FormDadosIniciais = formDadosIniciais(contrato, self.driver)

        try:
            self.act.clicar_elemento('/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr/td[6]/a/img', By.XPATH)
        except:
            pass

        try:
            form.preencherDataNascimento()
            aguardar_loading(self.chrome_driver)
            form.preencherDataFator()
            try:
                form.preencherCodigoLoja()
            except:
                pass
            aguardar_loading(self.driver)
            form.preencherDataRenda()
            form.preencherValorRenda()
            aguardar_loading(self.chrome_driver)
            form.selecionarGrauInstrucao()
            aguardar_loading(self.chrome_driver)

        except UnexpectedAlertPresentException:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'])

    def preencherFormPortabilidade(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+------------- Dados Portabilidade -------------+")
        print("+-----------------------------------------------+")
        form = formPortabilidade(self.driver, contrato)
        form.preencherIptSaldoDevedor()
        form.preencherIptValorParcela()
        form.preencherIptQtdParcelas()
        form.preencherIptQtdParcelasPagas()
        tratar_erros_formulario_insercao(self.driver,contrato.codigo)
        aguardar_loading(self.driver)
        form.preencherIptNoContrato()
        form.preencherIptUltimoVencimento()
        form.preencherIitPrimeiroVencimento()
        aguardar_loading(self.driver)
        form.preencherIptCodigoBanco()

    def preencher_dados_bancarios(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+--------------- Dados Bancários ---------------+")
        print("+-----------------------------------------------+")

        form: FormDadosBancarios = formDadosBancarios(self.driver, contrato)
        form.selecionarFormaCredito()

        texto_erro_banco = ''
        texto_erro_ag = ''

        try:
            form.preencherCodigoBanco()
        except UnexpectedAlertPresentException as e:
            print(e)
            return False,e.alert_text.rstrip("\n")

        try:
            time.sleep(2)
            try:
                texto_erro_banco = self.selenium_helper.verificar_texto_campo_jquery('#erroBanco')
            except UnexpectedAlertPresentException as e:
                print(e)
                return False,e.alert_text.rstrip("\n")

        except TimeoutException:
            print("Banco preenchido")

        if(texto_erro_banco != ''):
            return False, "Conta é digital"

        aguardar_loading(self.driver)

        form.preencherNoAgencia()

        try:
            time.sleep(3)
            texto_erro_ag = self.selenium_helper.verificar_texto_campo_jquery('#erroAgencia')
        except TimeoutException:
            print("Agencia preenchida")

        if(texto_erro_ag != ''):
            return False, "Dados bancários incorretos"

        aguardar_loading(self.driver)

        form.preencherDvAgencia()

        form.preencherNoConta()
        #form.preencherDvConta()

        loc = "#dadosBancarios\\\\.contaDv"
        self.selenium_helper.atribuir_valor_campo_jquery(loc, contrato.banco.digitoConta)

        form.selecionarContaCredito()

        return True, None

    def preencher_dados_proposta(self, contrato: Contrato, rec = 0):
        print("+------------------------------------------------+")
        print("+---------------- Dados Proposta ----------------+")
        print("+------------------------------------------------+")
        form: FormDadosProposta = formDadosProposta(driver=self.driver, contrato=contrato)
        form.filtroTabelaCarencia = lambda taxa: "DIG" in taxa
        form.verficarTipoTabela()
        margem_erro = 0

        if(self.contrato['tipo'] != 'PORTABILIDADE'):
            if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1'):
                form.filtroTabelaCarencia = lambda taxa: "DIG" not in taxa
                if(form.valor_contrato < 1000):
                    form.selecionarTabelaDiretaPortabilidade('7897','Inss/Novo Valor R$ 450 a R$ 999')   
                else:
                    form.selecionarTabelaPelaTaxa(margem_erro,False)
                    time.sleep(2)
                    tratar_erros_formulario_insercao(
                        self.driver, self.contrato['codigo_con'])
                    self.act.manusear_alerta('aceitar')
            else:
                form.selecionarTabelaPelaTaxa()
                form.anexarTabelaCarenciaNoContrato()
        else:
            if(float(contrato._Contrato__dados['dados_portabilidade']['saldoDevedorFinal']) < 4000):
                try:
                    if(rec > 0):
                        print('Saldo devedor menor que 2 mil e nova tentativa em taxa menor')
                        form.selecionarTabelaDiretaPortabilidade('1097','DIG Inss/Refin Port-Min4000-Tx 1,69-1,65')
                    else:
                        print('Saldo devedor menor que 2 mil')
                        form.selecionarTabelaDiretaPortabilidade('1061','DIG Inss/Refin Port-Min4000-Tx 1,81-1,70')
                except:
                    raise NotFoundResultException('Tabela não disponível.')
            else:
                #form.selecionarTabelaDiretaPortabilidade('2487','DIG Inss/Refin Port-Min2000-Tx 2,14-1,70')
                if form.selecionarTabelaPelaTaxa() == False:
                    if(rec == 0):
                        raise NotFoundResultException('Tabela não disponível.')
                    elif(rec > 0):
                        raise NotFoundResultException('Não resultou em valores disponíveis até na tentativa da última tabela.')

                form.anexarTabelaCarenciaNoContrato()

        #pdb.set_trace()
        form.apagarValorSolicitado()
        form.preencherValorParcela()
        form.clicarBtnSimular()

        form.extrairValorJanelaSimulacaoEmprestimo()

        if(self.contrato['tipo'] != 'PORTABILIDADE'):
            retorna_valor = form.atualizarValorSolicitado()
        else:
            retorna_valor = form.atualizarValorSolicitadoPortabilidade()

        if retorna_valor == False: 
            print(rec)
            contrato._Contrato__valorTabela = str(float(contrato._Contrato__valorTabela) - 0.05)  
                      
            if(float(contrato._Contrato__valorTabela) < 1.0):
                raise NotFoundResultException('Valor não disponível até na tentativa de taxa de ' + contrato._Contrato__valorTabela )

            print('Tentando tabela menor com taxa de:' + contrato._Contrato__valorTabela)
            rec = rec + 1
            return InsercaoIbConsigPortabilidadeFila.preencher_dados_proposta(self, contrato , rec)
        
        form.preencherValorSolicitado()
        form.preencherValorParcela()
        form.preencherNumeroPrestacoes()

    def preencher_dados_pessoais(self, contrato: Contrato):
        print("+------------------------------------------------+")
        print("+---------------- Dados Pessoais- ---------------+")
        print("+------------------------------------------------+")

        form: FormDadosPessoais = formDadosPessoais(self.driver, contrato)
        #form.preencherNome()
        form.preencherSexo()
        form.selecionarEstadoCivil()

        aguardar_loading(self.driver)

        if(self.contrato['estadoCivil'] != 'V' and self.contrato['estadoCivil'] != 'S' and self.contrato['estadoCivil'] != 'I'):
            form.preencherNomeConjuge()

        form.preencherNomeMae()
        form.preencherNomePai()
        form.preencherCidadeNascimento()
        form.selecionarUFNascimento()

        form.selecionarNacionalidade()
        form.selecionarTipoIdentidade()
        form.selecionarOrgaoEmissor()
        form.selecionarUFIdentidade()
        form.preencherNumeroIdentidade()
        form.preencherDataEmissao()

    def preencher_dados_endereco(self, contrato: Contrato):
        print("+-----------------------------------------------+")
        print("+--------------- Dados Endereço ----------------+")
        print("+-----------------------------------------------+")
        form: FormDadosEndereco = formDadosEndereco(self.driver, contrato)
        self.act.time_out = 0.2

        form.preencherCep()
        aguardar_loading(self.driver)

        try:
            form.preencherLogradouro2()
        except:
            form.preencherLogradouro()
            pass

        if form.logradouroSemNumero:
            form.marcarSemNumero()
        else:
            try:
                form.preencherNumero()
            except:
                pass

        form.preencherBairro()
        form.preencherComplemento()
        form.preencheDddTelefone()
        form.preencheNoTelefone()
        form.preencheDddCelular()
        form.preencheNoCelular()

    def preencher_dados_finais(self, contrato: Contrato):
        print("+------------------------------------------------+")
        print("+----------------- Dados Finais -----------------+")
        print("+------------------------------------------------+")
        form: DadosFinais = DadosFinais(self.driver, self.contrato)
        self.act.time_out = 0.2

        try:
            form.selecionar_rogado_nao()
        except:
            pass
        time.sleep(self.wait)

        form.preencher_nome_vendedor()
        form.preencher_forma_envio()
        time.sleep(self.wait)

        try:
            form.selecionar_if_nao()
        except:
            pass

        if(form.grau_instrucao_wa == 'ANALFABETO' or form.grau_instrucao_uconecte == '1'):
            try:
                form.selecionar_rogado_sim()
            except:
                pass
        else:
            try:
                form.selecionar_rogado_nao()
            except:
                pass

        try:
            self.driver.execute_script('mesmoAgente(true)');
        except:
            pass
        time.sleep(self.wait + 2)

        print('Aguardando confirmação final da inserção...')
        form.clicar_confirmar()
        time.sleep(self.wait + 3)

        try:
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,
            )
        except DadosBancariosException:
            self.preencher_dados_bancarios()
            form.preencher_prazo_contrato()

            if self.contrato['banco']['tipoConta'] == 'Ordem de Pagamento':
                form: FormDadosBancarios = formDadosBancarios(self.driver, contrato)
                form.preencherNoAgencia()
                
            aguardar_loading(self.driver)

            self.driver.execute_script('$("#confirmar").click()')
            time.sleep(self.wait)

    def finalizar_insercao_popup(self):
        """
        Lida com as janelas de confirmação que são abertas ao fim da inserção
        """
        DadosFinais.executar_script_pop_up(self.driver)
        time.sleep(self.wait + 1)

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

            time.sleep(self.wait + 2)

        except UnexpectedAlertPresentException as e:
            print(e)
            tratar_erros_formulario_insercao(
                self.driver, self.contrato['codigo_con'],
                vals_atualizados=self.vals_ideais,

            )

    def buscar_ade(self, contrato: Contrato):
        dados_finais: DadosFinais = DadosFinais(self.driver, self.contrato)

        dados_finais.buscar_ade_portabilidade()
        dados_finais.buscar_ade() 

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

        contrato.incluirDadoAdicional("ADE", dados_finais.ade)
        contrato.incluirDadoAdicional("ADE_PORTABILIDADE", dados_finais.ade_refin_portabilidade)

    def buscar_ade_outros(self, contrato: Contrato):
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

        contrato.incluirDadoAdicional("ADE", dados_finais.ade)

# if __name__ == '__main__':
#     InsercaoIbConsigPortabilidade.iniciar_horario_comercial(nome_instancia="")
