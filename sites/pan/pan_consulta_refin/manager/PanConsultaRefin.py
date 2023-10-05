# Classe herdada por PanInsercaoMan
from sites.baseRobos.manager import Manager

# Classe de requisição e manipulaçao de dados
from sites.pan.pan_consulta_refin import DadosConsultaRefin

# Funções que executam a automação do processo de inserção
from sites.pan.pan_consulta_refin import (
    FormDadosSimulacao, FormIdentificacao,
    TabelaRefinanciamentos, TabelaSimulacao,
)
from selenium.webdriver import Chrome
from sites.pan.pan_consulta_refin.auto.auxiliares import (
    aguardar_loading_consultar,aguardar_loading,aguardar_loading_card_ofertas, verificar_alertas,
    DadosIdentificacaoIncorretosException
)
from sites.pan.pan_consulta_refin import (
    NotFoundResultException, RestricaoException
)
from selenium.common.exceptions import UnexpectedAlertPresentException
from time import sleep
from sites.pan.auxiliares.sessao import verificar_sessao_login, login, HORARIO_COMERCIAL

from sites.baseRobos.core.helpers import definir_nome_robo, identificar_erro_robo
from sites.baseRobos.core.DebugTools import DebugTools
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
dbg = DebugTools(debugging=False)

import pdb

class ConsultaRefin(Manager):

    id_fila_refin = 27
    id_banco: int = 68

    urls: dict = {
        'login': ("https://panconsig.pansolucoes.com.br"),
        'consulta': ('https://panconsig.pansolucoes.com.br/WebAutorizador/Cadastro/CardOferta')
    }
    #antiga url /MenuWeb/Cadastro/Proposta/UI.PropostaSimplificada.aspx
    def __init__(self, driver: Chrome = False, **kwargs):
        super().__init__()
        self.set_options(
            '--ignore-ssl-errors', 'log-level=3'
            "--start-maximized", kwargs.get("headless", ""))
        self.init_chrome_driver(import_driver=driver)

        self.data: DadosConsultaRefin = DadosConsultaRefin()
        self.data.inverter_ordem = kwargs.get("ordem_inversa", False)
        self.filtro = kwargs.get("filtro", lambda x: False)
        self.verificar_sessao = kwargs.get("verificar_sessao", False)
        self.senha = kwargs.get("senha", "Marcelo@39")
        self.cpf_login = kwargs.get("login", "085.746.096-09")
        self.parceiros = kwargs.get("parceiros", "003987")
        self.data.limitar_fila = kwargs.get("min_len", 0)
        self.nome_robo = kwargs.get("nome_robo")
        self.aguardar_sessao = False

    @staticmethod
    def get_standalone_instance(**kwargs):

        pan_refin: ConsultaRefin = ConsultaRefin(
            driver=kwargs.get("driver", None), headless=kwargs.get("headless", ""))

        pan_refin.nome_robo = kwargs.get("nome_robo")
        pan_refin.cpf_login = kwargs.get("login", None)
        pan_refin.senha = kwargs.get("senha", None)
        pan_refin.filtro = kwargs.get("filtro", lambda x: False)
        pan_refin.verificar_sessao = kwargs.get("verificar_sessao", None)
        pan_refin.parceiros = kwargs.get("parceiros", "003987")
        pan_refin.data.inverter_ordem = kwargs.get("ordem_inversa")

        return pan_refin

    def run(self):


        login(self.driver, self.cpf_login, self.senha, self.parceiros)
        try:
            while True:
                print("Iniciando consulta de Refinanciamentos")
                self.consultar_refinanciamentos(fila="refinanciamento")

                print("Iniciando consulta de Refinanciamentos Potenciais")
                self.consultar_refinanciamentos(fila="potenciais")

                print("Filas de Consulta de Refinanciamento Finalizadas.")

                #sleep(120)
        except:
            return
            # print(e.msg)
            # self.driver.quit()

    def consultar_refins_e_potenciais(self):
        self.consultar_refinanciamentos("refinanciamento")
        self.consultar_refinanciamentos("potenciais")

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_refinanciamentos(self, fila="refinanciamento"):
        print("Buscando solicitaçoes de refinanciamento")

        dados_consulta = self.data.get_solicitacoes_consultar()

        if not dados_consulta:
            return -1

        print(dados_consulta)
        
        dbg.debugger()

        for cnt, solicitacao in enumerate(dados_consulta[0]):

            definir_nome_robo(self.nome_robo)
            try:
                verificar_alertas(self.chrome_driver)

                if not verificar_sessao_login(self.chrome_driver, self.verificar_sessao):
                    login(self.driver, self.cpf_login, self.senha, self.parceiros)

                # if solicitacao["sigla"] == "RJ":
                #     print(f"Sigla: {solicitacao['sigla']}. Pulando...")
                #     continue

                if self.filtro(solicitacao):
                    continue

                if solicitacao.get('idSolicitacao', False):
                    self.data.api_iniciar_log_robo(
                        idRobo=self.id_fila_refin, idSolicitacao=solicitacao['idSolicitacao'])
                    print(f"[{cnt}] Consultando solicitação: {solicitacao['idSolicitacao']}")
                else:
                    print(f"[{cnt}] Consultando pessoa: {solicitacao['idPessoa']}")

                if cnt > 20:
                    print("Seguindo para a próxima fila...")
                    return

                form_id: FormIdentificacao = FormIdentificacao(
                    self.chrome_driver, **solicitacao)
                form_sim: FormDadosSimulacao = FormDadosSimulacao(
                    self.chrome_driver, **solicitacao)
                tab_refin: TabelaRefinanciamentos = TabelaRefinanciamentos(
                    self.chrome_driver)
                tab_sim: TabelaSimulacao = TabelaSimulacao(
                    self.chrome_driver, **solicitacao)

                self.preencher_form_identificacao(form_id)
                self.preencher_form_simulacao(form_sim)
                self.extrair_dados_refin(tab_refin, tab_sim)

                tab_refin.validar_lista_refinanciamentos()

                self.data.atualizar_consulta_refins(
                    solicitacao, tab_refin.dados_refinanciamentos
                )
                self.data.api_registrar_log_robo(
                    log="Consulta realizada com sucesso", status=2)

            except NotFoundResultException as e:
                self.data.atualizar_refins_indisponiveis(  # raises Exception
                    solicitacao=solicitacao, msg=e.message)
                self.data.api_registrar_log_robo(log=e.message, status=2)

            except RestricaoException as e:
                self.data.atualizar_restricao(
                    solicitacao, e.message)
                self.data.api_registrar_log_robo(log=e.message, status=2)

            except UnexpectedAlertPresentException:
                verificar_alertas(self.chrome_driver)
                
            except Exception as e:
                dbg.exception(e)
                self.data.api_registrar_log_robo(log=f"ERRO: {e}", status=0)
                identificar_erro_robo()
                sleep(5)

        return 0

    def preencher_form_identificacao(self, form: FormIdentificacao):
        print("Preenchendo formulário de identificação")
        form.chrome_driver.get(self.urls['consulta'])

        #form.select_promotora_card_ofertas()
        form.carregar_dados_funcionais()
        try:
            aguardar_loading_card_ofertas(form.act, form.by)
            form.select_empregador_card_ofertas()
            aguardar_loading_card_ofertas(form.act, form.by)

            verificar_alertas(self.chrome_driver)

            form.select_orgao_card_ofertas()
            aguardar_loading_card_ofertas(form.act, form.by)

            form.campo_cpf_card_ofertas()
            aguardar_loading_card_ofertas(form.act, form.by)

            form.aguardar_abertura_modal_card_ofertas()
            aguardar_loading_card_ofertas(form.act, form.by)
            verificar_alertas(self.chrome_driver)

            try:
                form.modal_selecionar_matricula_cadastro_card_ofertas()
                verificar_alertas(self.chrome_driver)
                try:
                    form.descartar_card_ofertas_pendente()
                    form.confirmar_descartar_card_ofertas()
                except:
                    pass

            except DadosIdentificacaoIncorretosException as e:
                form.clicar_novo_cliente_ofertas_pendente()
                aguardar_loading_card_ofertas(form.act, form.by)
                form.campo_data_nascimento_card_ofertas()
                aguardar_loading_card_ofertas(form.act, form.by)
                form.campo_matricula_card_ofertas()
                try:
                    aguardar_loading_card_ofertas(form.act, form.by)
                    form.descartar_card_ofertas_pendente()
                    aguardar_loading_card_ofertas(form.act, form.by)
                    form.confirmar_descartar_card_ofertas()
                    aguardar_loading_card_ofertas(form.act, form.by)
                except:
                    pass
                pass
                #if form.qtde_erros_matricula_excedido:
                #     raise Exception("Erro quantidade de digitos matricula")
                # form.empregador = e.empregador_corrigido
                # form.orgao = e.orgao_corrigido
                # form.qtde_erros_digitos_matricula += 1
                # return self.preencher_form_identificacao(form)

            try:
                form.descartar_card_ofertas_pendente()
                form.confirmar_descartar_card_ofertas()
            except:
                pass

            aguardar_loading_card_ofertas(form.act, form.by)
            #if form.cliente_sem_contato_card_ofertas:
            try:
                form.habilitar_contato_cliente_card_ofertas()
            except:
                pass

            #form.campos_ddd_telefone_card_ofertas()

            try:
                form.descartar_card_ofertas_pendente()
                form.confirmar_descartar_card_ofertas()
            except:
                pass

            consulta_botao = form.botao_consulta_card_ofertas()

            aguardar_loading_consultar(form.act, form.by)
            
            if(consulta_botao == False):
                raise Exception("Demora na consulta... Resetando consulta...")

            aguardar_loading_card_ofertas(form.act, form.by)

            verificar_alertas(self.chrome_driver)
            
            resultado_incial = form.verificar_retorno_card_ofertas()
            if(resultado_incial == True):
                print('Sem contrato disponivel para refinanciamento...')
                aguardar_loading_card_ofertas(form.act, form.by)
                raise(NotFoundResultException("Refinanciamento indisponivel"))
            
            aguardar_loading_card_ofertas(form.act, form.by)    
            verificar_alertas(self.chrome_driver)   

            form.ofertarRefinanciamento()
            aguardar_loading_card_ofertas(form.act, form.by)  

        except UnexpectedAlertPresentException as e:
            print(e.alert_text)
            verificar_alertas(self.chrome_driver)
            form.act.manusear_alerta()

    def preencher_form_simulacao(self, form: FormDadosSimulacao):
        print("Preenchendo dados da simulação.")
        verificar_alertas(self.chrome_driver,'','formulario_simulacao')
        form.select_operacao()

        verificar_alertas(self.chrome_driver)
        aguardar_loading(form.act, form.by)

        form.atualizar_lista_refinanciamentos()

        aguardar_loading(form.act, form.by)
        verificar_alertas(self.chrome_driver)
        aguardar_loading(form.act, form.by)

    def extrair_dados_refin(self, tab_refin: TabelaRefinanciamentos, tab_sim: TabelaSimulacao):
        print("Extraindo dados da tabela de refinanciamento")
        tab_refin.verificar_quantidade_refinanciamentos()
        for i in tab_refin.n_linhas:
            try:
                verificar_alertas(self.chrome_driver)

                tab_refin.set_linha_tabela_e_checkbox(i)

                aguardar_loading(tab_refin.act, tab_refin.by)
                tab_refin.selecionar_check_box()
                aguardar_loading(tab_refin.act, tab_refin.by)

                if tab_refin.parcelas_vencidas():
                    continue
                tab_refin.extrair_valor_parcela()
                tab_refin.extrair_saldo_devedor()

                if tab_refin.checkbox_disabled:
                    continue

                verificar_alertas(self.chrome_driver)
                aguardar_loading(tab_refin.act, tab_refin.by)

                tab_sim.preencher_campo_parcela(tab_refin.val_percela)
                aguardar_loading(tab_sim.act, tab_sim.by)

                tab_sim.botao_calcular_financiamento()

                verificar_alertas(self.chrome_driver)
                aguardar_loading(tab_sim.act, tab_sim.by)

                if tab_sim.refinanciamento_indisponivel():
                    continue

                tab_sim.extrair_prazo()
                

                verificar_alertas(self.chrome_driver)
                #!import code; code.interact(local=vars())
                loc = '//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond"]'
                item = self.driver.find_element_by_xpath(loc).text.split('\n')
                for tabela in item: 
                    if r'_90_RFN_NORMAL' not in tabela and r'RFN_NORMAL' in tabela:
                        valor = tabela.split(" ")[-1].strip()
                        try:
                            valor_float = float(valor.replace(".","").replace(",","."))
                        except:
                            valor_float = 0
                        nome_tabela = tabela.split(" ")[1].strip()
                        print('Nome tabela: ' + str(nome_tabela))
                        break

                if valor_float == 0:
                    for index,tabela in enumerate(item): 
                        if r'FLEX' in tabela:
                            valor = tabela.split(" ")[-1].strip()
                            try:
                                valor_float = float(valor.replace(".","").replace(",","."))
                            except:
                                valor_float = 0
                            nome_tabela = tabela.split(" ")[1].strip()
                            
                            if(index >= len(item) - 1 and valor_float == 0):
                                print('Nome tabela: ' + str(nome_tabela))
                                print('Valor achado: ' + str(valor_float))
                                break
                            if(valor_float > 0):
                                print('Nome tabela: ' + str(nome_tabela))
                                print('Valor achado: ' + str(valor_float))
                                break


                if(valor_float < 1):
                    continue

                if tab_sim.tabela_invalida:
                    continue

                tab_sim.extrair_val_liberado(valor)
                tab_sim.extrair_nome_tabela(nome_tabela)

                # if tab_sim.valor_disponivel_invalido:
                #     continue

                if tab_refin.validar_dados_refin and tab_sim.validar_dados_simulacao:
                    tab_refin.atualizar_lista_refins(
                        tab_sim.dados_simulados
                    )
            # except NotFoundResultException:
            #     print("Refinanciamento indisponivel")
            except UnexpectedAlertPresentException as e:
                verificar_alertas(self.chrome_driver)
                raise Exception(e.alert_text)

        tab_refin.validar_consulta_refin()


if __name__ == "__main__":
    ConsultaRefin.main()

