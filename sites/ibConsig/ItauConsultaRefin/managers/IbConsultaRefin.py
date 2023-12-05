import logging,sys
sys.path.append('../')


from sites.ibConsig.IbConsigInsercao.auto.FormDadosProposta import DadosProposta
from sites.ibConsig.IbConsigInsercao.auto.FormDadosIniciais import DadosIniciais
from sites.ibConsig.IbConsigInsercao.auto.FormIdentificacao import DadosIdentificacao
from sites.ibConsig.IbConsigInsercao.auto.TabelaRefinanciamentos import TabelaRefinanciamentos
from sites.ibConsig.ItauConsultaRefin.data.DadosConsultaRefin import DadosConsultaRefin
from sites.ibConsig.ItauConsultaRefin.data.DadosItauRefin import DadosItauRefin

from sites.ibConsig.libs.auxiliares.ib_auxiliares import *
from sites.ibConsig.gerar_contrato.gerar_contrato import cookies_gerar_contrato
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig

from selenium.common.exceptions import (
    JavascriptException
)
from sites import ID_ROBOS

from sites.core.selenium_helper import SeleniumHelper

from sites.baseRobos.core.DebugTools import DebugTools
from typing import List
from sites.baseRobos.manager import Manager

import PATHS
from pathlib import Path
from PATHS import project_path

import time,pdb,os,shutil

from typing import Callable
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.ibConsig.cookies import COOKIES_INSERIR_CONTRATO

debug = DebugTools(debugging=False)

HORARIO_COMERCIAL = 7, 20


URL_INICIAL = 'https://www.ibconsigweb.com.br/Index.do?method=prepare'
URL_LOGADO = 'https://www.ibconsigweb.com.br/principal/fsconsignataria.jsp'


class IbConsultaRefin(Manager):
    ID_BANCO = 1
    ID_ROBO = ID_ROBOS['ibConsig']['consultaRefin']

    def __init__(self, id_instancia: int = 0, **kwargs):
        super().__init__()
        self.id_instacia: int = id_instancia

        self.user_chrome: str = PATHS.chrome_user(kwargs.get("user_dir", "ItauRefin"))
        try:
            pasta = self.user_chrome.split('=')[1]
            shutil.rmtree(pasta)
        except:
            pass

        Manager.criar_pasta_usuario_chrome(self.user_chrome)
        self.set_options('--ignore-ssl-errors', 'log-level=3', self.user_chrome,)

        self.init_chrome_driver()

        self.data: DadosItauRefin = DadosItauRefin()

        self.selenium_helper: SeleniumHelper = SeleniumHelper(self.driver)
        self.act: SeleniumActions = SeleniumActions(self.driver, time_out=0.3)

        self.cookies_path = cookies_gerar_contrato()
        #self.cookies_path = COOKIES_INSERIR_CONTRATO
        self.wait = 0.2
        self.log_path = f"/ibConsig/log/{self.__class__.__name__}"
        self.login: Callable = lambda: None
        self.loja: str = ""

        self.path_captcha = str(Path(project_path() + "/core/captchas/2.jpg"))

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls,  nome_instancia: str, id_instancia=1):
        definir_nome_robo(f"Itau - Consulta Refinanciamento {nome_instancia}")
        run = IbConsultaRefin()
        run.id_instacia = id_instancia
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.driver.delete_all_cookies()

        while True:
            # TODO: TESTE
            # self.driver.get(URL_INICIAL)
            logging.warning("GET!!!")

            self.driver.get("https://www.ibconsigweb.com.br/consignacao/identificacao.jsf?codigoServico=040")
            self.aguardar_login()
            self.executar_consulta_refinanciamentos()


    @staticmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def retornar_instancia_login(**kwargs):
        import re
        """
        :param kwargs: usuario, senha, id_instancia, ordem_reversa, user_dir.
        :return: retorna uma instancia de IbConsultaRefin configurada
            para realizar login.
        :rtype: IbConsultaRefin
        """
        # configurações da instâncioa
        id_instancia: int = kwargs.get("id_instancia", 0)         # constructor
        user_dir: str = kwargs.get("user_dir", "default")         # constructor
        ordem_reversa: bool = kwargs.get("ordem_reversa", False)  # setter

        consulta: IbConsultaRefin = IbConsultaRefin(
            id_instancia=id_instancia, user_dir=user_dir)

        nome_usuario = kwargs.get("usuario", "")
        loja = re.search(r"\d{4}", nome_usuario)
        print(loja)
        if loja is not None:
            consulta.loja = loja.group()

        consulta.data.ordem_reversa = ordem_reversa

        # atribui o método <IbConsig.login_sistema> ao atributo <IbConsultaRefin.login>
        consulta.login = IbConsig.login_fact(driver=consulta.driver, **kwargs)

        return consulta

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def aguardar_login(self):
        i = 1
        while not self.act.esta_presente("[name='bottomFrame']"):
            print(f"\r[{i}] Aguardando login.", end="")
            self.driver.get(URL_INICIAL)
            if self.login() is None:
                try:
                    self.selenium_helper.load_cookies(self.cookies_path, True)
                except Exception as e:
                    print("Cookies não encontrados:", e)
            sleep(5)
            self.driver.get(URL_LOGADO)
            i += 1

    def buscar_refinanciamentos(self, fila="refinanciamento") -> list:
        solicitacoes: List[dict] = []

        if fila == "refinanciamento":
            solicitacoes = self.data.get_solicitacoes_consulta()
        elif fila == "potenciais":
            solicitacoes = self.data.uconecte.buscar_pessoas_potenciais()

        return solicitacoes

    def executar_consulta_refinanciamentos(self, fila="refinanciamento"):

        solicitacoes: List[dict] = self.buscar_refinanciamentos(fila)
        # solicitacoes = [{"idSolicitacao": "1209305",
        #                 "idPessoa": "249782",
        #                 "fk_idPerfil": "4",
        #                 "orgao": "79",
        #                 "cpf": "01319305830",
        #                 "matricula": "1763668883",
        #                 "sigla": "",
        #                 "cidade": "",
        #                 "inss": True}]

        if not solicitacoes:
            return False

        for solicitacao in solicitacoes:

            # tempo_ultimo_captcha = os.path.getmtime(self.path_captcha)
            # tempo_agora = time.time()
            # minutos_passados = (tempo_agora - tempo_ultimo_captcha) / 60

            # if(minutos_passados <= 1):
            #     print("XXXXXXXXXXXXX Aguardando o robo insercao resolver o captcha....")
            #     time.sleep(100 - minutos_passados * 60)

            # TODO: TESTE
            self.driver.get(
                "https://www.ibconsigweb.com.br/consignacao/identificacao.jsf?codigoServico=040")
            sleep(0.6)
           
            if solicitacao.get('idSolicitacao', False):
                print(f"\nIniciando consulta proposta:", solicitacao)
                self.data.api_iniciar_log_robo(
                    idRobo=self.ID_ROBO,
                    idSolicitacao=solicitacao['idSolicitacao'])
            else:
                print(f"\nIniciando consulta refin potencial:", solicitacao['idPerfil_pessoa'])
            try:
                solicitacao['entidade'] = filtrar_entidade(solicitacao)

                dados_consulta: DadosConsultaRefin = DadosConsultaRefin(solicitacao)

                self.consultar_refinanciamentos(dados_consulta)

                dados_consulta.validar_dados_consultados()

                self.data.atualizar_dados_consulta(
                    solicitacao, dados_consulta.refinanciamentos_consultados)

                self.data.api_registrar_log_robo(
                    log='Consulta realizada com sucesso.', status=2)

            except RestricaoException as e:
                print('Cadastrar restrição. Mensagem Sistema: {}'.format(e.message))

                self.data.atualizar_impossibilidade_consulta(
                    solicitacao, e.message, restricao=True)

                # Registrar log com sucesso
                self.data.api_registrar_log_robo(
                    log='Cadastrar restrição. Mensagem Sistema: {}'.format(e.message),
                    status=2)

            except NotFoundResultException as e:
                # Atualizar a indisponibilidade de dados no sistema para o cliente
                print('Não possui contratos. Mensagem Sistema: {}'.format(e.message))

                self.data.atualizar_impossibilidade_consulta(solicitacao, e.message)

                # Registrar log com sucesso
                self.data.api_registrar_log_robo(
                    log="Sistema itaú: {}".format(e.message),
                    status=2)

            except Exception as e:
                self.data.api_registrar_log_robo(log=f"ERRO: {e}", status=0)
                fechar_janelas_com_erro(self.driver)
                deb.exception(e)

        return True

    def consultar_refinanciamentos(self, dados_consulta: DadosConsultaRefin):

        form_id: DadosIdentificacao = DadosIdentificacao(
            self.driver, dados_consulta.dados_solicitacao)
        form_id.consulta_refin = True

        form_dados_refin: DadosProposta = DadosProposta(
            self.driver, dados_consulta.dados_solicitacao, dados_consulta)

        self.preencher_formulario_identificacao(form_id)

        tabela_refin = TabelaRefinanciamentos(
            self.driver, dados_consulta.dados_solicitacao)

        # Quantidade de check_boxes na tabela de refins.
        tabela_refin.extrair_quantidade_refins()

        for index in range(tabela_refin.total_refinanciamentos):
            
            try:
                # Verificar infos contrato com infos de cada linha da tabela
                tabela_refin.set_linha_tabela(index)
                matricula = tabela_refin.encontrar_matricula_refinanciamento(True)

                if not matricula:
                    print('Pulando matrícula...')
                    continue

                form_dados_refin.valor_parcela = tabela_refin.extrair_parcela()
                # A escolha do refin ocorre quando os dados batem.
                tabela_refin.selecionar_refinanciamento()
                tratar_alerts_refinanciamento(self.driver, tabela_refin.act)

                aguardar_loading(self.driver)

                tabela_refin.confirmar_selecao()
                sleep(1)  # necessário.
                tratar_alerts_refinanciamento(self.driver, tabela_refin.act)
                aceitar_pendencia(self.driver, self.selenium_helper)
                try:
                    self.extrair_dados_refinanciamento(form_dados_refin, dados_consulta)
                except UnexpectedAlertPresentException as e:
                    tratar_alerts_refinanciamento(
                        self.driver, tabela_refin.act, texto_alerta=e.alert_text)

                dados_consulta.atualizar_lista_refins(form_dados_refin)

                self.driver.back()
                sleep(2)
                try:
                    self.driver.execute_script("""$('#iFrameOverlay').remove();$('#waitDiv').remove();$('#bodyOverlay').remove()""")
                except:
                    pass


            except PularCheckboxException as e:
                print(e.message)
            except DadoIndisponivelException as e:
                print(e.msg)
                if not tabela_refin.esta_presente:
                    self.driver.back()
                    sleep(2)
                    try:
                        self.driver.execute_script("""$('#iFrameOverlay').remove();$('#waitDiv').remove();$('#bodyOverlay').remove()""")
                    except:
                        pass

    def preencher_formulario_identificacao(self, form: DadosIdentificacao):
        time.sleep(self.wait)
        try:
            aguardar_loading(self.driver)

            if not form.campo_entidade_preenchido:
                form.preencher_entidade()
                situacao = form.verificar_convenio_ativo()
                if not situacao:
                    print('XXXXXXXXXXXXXXXXConvênio inativoXXXXXXXXXXXXXXXX')
                    return False
                form.aguardar_carregar_entidade()

            try:
                form.clicar_modal()
            except:
                pass

            form.preencher_cpf()

            if form.servidor_federal:
                form.preencher_matricula()
                try:
                    form.selecionar_situcao_servidor(consulta_refin=True)
                except:
                    pass

            form.resolver_captcha()

            if form.resposta_captcha == 'ERROR NO USER':
                form.captcha.mudar_status_captcha(form.id_captcha, '2')
                return self.preencher_formulario_identificacao(form)

            form.preencher_resposta_captcha()

            form.clicar_confirmar()

            aguardar_loading(self.driver)
            time.sleep(self.wait)

            selecionar_opcao_modal_formulario(self.driver)

            aguardar_loading(self.driver)

            tratar_erros_formulario_refinanciamento(
                form.act, form.captcha, form.id_captcha)
            try:
                item_formulario = self.driver.execute_script(
                    "return $('#ade\\\\.dataFator').length;")

            except JavascriptException:
                print('Formulário de inserção não foi aberto, pular a inserção!')
                return False

            if item_formulario == 1:
                return True

        except CaptchaRecusadoException:
            return self.preencher_formulario_identificacao(form)

    def extrair_dados_refinanciamento(self, form: DadosProposta, consulta: DadosConsultaRefin):
        """
        Extrai os dados: saldoDevedor, valorLiberado, prazo, valorParcela,
        do respectivo refinanciamento
        """
        form.consulta_refinanciamento = True
        form.act.time_out = 0.2
        aguardar_loading(self.driver)

        consulta.iniciada = True

        #ime.sleep(self.wait+1)
        if self.loja == "1875":
            try:
                DadosIniciais.preencher_campo_loja(form.chrome_driver, "1873")
            except:
                pass

        #time.sleep(self.wait+1)

        DadosIniciais(self.driver, {"renda": "15000,00"}).preencher_valor_renda("15000,00")
        #time.sleep(self.wait+1)
        
        form.preencher_margem_se_vazia()

        time.sleep(2)
        tratar_alerts_refinanciamento(self.driver, form.act)
        
        form.selecionar_taxa_refinanciamento(
            filtro=lambda taxa: ("DIG" in taxa.upper()))

        time.sleep(self.wait+1)

        tratar_alerts_refinanciamento(self.driver, form.act)
        aguardar_loading(self.driver)

        if consulta.estatutario:
            try:
                preencher_simulacao_sem_valor_parcela(form)
            except ParcelaNaoEncontradaException as e:
                print(e.msg)
                form.simular = True

        if consulta.rgps or form.simular:
            preencher_simulacao_usando_valor_parcela(form)

        if consulta.rgps or form.simular:
            # Extrair prazo
            try:
                sleep(2)  # necessário!
                form.extrair_valores_emprestimo()
            except UnexpectedAlertPresentException as e:
                fechar_janelas_com_erro(self.driver, default_frame="rightFrame")
                tratar_alerts_refinanciamento(self.driver, self.act, e.alert_text)

            # self.selenium_helper.trocar_frame("rightFrame")

            time.sleep(self.wait)
            form.preencher_campo_val_emprestimo()

            aguardar_loading(self.driver)

            form.preencher_valor_parcela()

        form.executar_caculo_valores_refinanciamento()
        aguardar_loading(self.driver)

        form.preencher_prazo_contrato()

        tratar_alerts_refinanciamento(self.driver, form.act)

        # Extrair valorLiberado
        form.extrair_valor_liberado()
        # Extrair saldoDevedor
        form.extrair_saldo_devedor()


def preencher_simulacao_sem_valor_parcela(form: DadosProposta):
    try:
        form.preencher_campo_val_emprestimo()
        form.extrair_valor_parcela()
        form.extrair_prazo_formulario()
    except KeyError:
        raise ParcelaNaoEncontradaException


def preencher_simulacao_usando_valor_parcela(form: DadosProposta):
    form.apagar_campo_valor_solicitado()
    tratar_alerts_refinanciamento(form.chrome_driver, form.act)
    time.sleep(0.2)
    aguardar_loading(form.chrome_driver)
    form.preencher_valor_parcela()
    time.sleep(0.2)
    tratar_alerts_refinanciamento(form.chrome_driver, form.act)
    aguardar_loading(form.chrome_driver)


if __name__ == '__main__':
    IbConsultaRefin.iniciar_horario_comercial(nome_instancia="Cookies")
