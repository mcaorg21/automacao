from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import (
    UnexpectedAlertPresentException, InvalidElementStateException,
    StaleElementReferenceException, TimeoutException, NoSuchElementException
)
from selenium.webdriver.common.by import By

from selenium.webdriver import Chrome

import os, time, requests
import re

from sites.core.captcha import TwoCaptcha
from sites.core.selenium_helper import SeleniumHelper
from sites.core.uconecte import Uconecte
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.data_helpers import (
    get_select_options_values, strip_zero_left
)
from sites.baseRobos.core.decorators import ApenasHorarioComercial

HORARIO_COMERCIAL = 7, 20


class IbConsig:
    def __init__(self, usuario, senha, driver: Chrome=None, cookies_path=None):
        self.cookies_path = cookies_path
        self.driver = driver

        self.usuario = usuario
        print(self.usuario)
        self.senha = senha
        print(self.senha)

        self.uconecte = Uconecte()
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.selenium_helper = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver)
        self.act.time_out = 5
        self.valor_liberado_maximo: str = "0"

    @classmethod
    def login_fact(cls, **kwargs):
        ib = IbConsig(kwargs.get('usuario'), kwargs.get('senha'), kwargs.get('driver'))
        return ib.login_sistema

    @classmethod
    def esta_logado(cls, driver: Chrome):
        print("URL:", driver.current_url)
        print("TITLE:", driver.title)
        return (not ("index.do" in str(driver.current_url).lower()) and
                not ("consig" in driver.title.lower()))

    @classmethod
    def tela_inicial(cls, driver, time_out=2):
        loc = "//*[contains(text(), 'Avisos')]"
        act = SeleniumActions(driver, time_out)
        sh = SeleniumHelper(driver)
        sh.trocar_frame("rightFrame")
        return act.esta_presente(loc, By.XPATH)

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def login_sistema(self):
        try:
            bottom_frame = self.selenium_helper.buscar_quantidade_elemento('[name=bottomFrame]')
            if bottom_frame == 1:
                print('Pulando etapa de Login, usuário já logado no sistema!')
                return True

            seletor_login = "[name='usuario']"
            self.selenium_helper.atribuir_valor_campo_driver(seletor_login, self.usuario)

            seletor_senha = "[name='j_password']"
            self.selenium_helper.atribuir_valor_campo_driver(seletor_senha, self.senha)

            id_captcha, captcha_resposta = self.captcha.resolver_captcha(
                "[name='iCaptcha']")

            captcha_field = self.driver.find_element(By.NAME,"captcha")
            captcha_field.send_keys(captcha_resposta)
            captcha_field.send_keys(Keys.RETURN)
            time.sleep(10)

            campo_senha = self.driver.execute_script(
                "return $('[name=j_password]').length")

            if campo_senha == 1:
                try:
                    loc_erro_login = '.erro'
                    texto_erro = self.act.obter_texto(loc_erro_login)
                    print("Erro ao logar:", texto_erro.upper())

                    if '12 MINUTO(S)' in texto_erro.upper():
                        print('Aguardando 12.05 minutos...')
                        time.sleep(730)

                except TimeoutException:
                    print('Não há acesso simultâneo...')

                self.captcha.mudar_status_captcha(id_captcha, '2')
                return False

            print('Logado com sucesso!')
            self.captcha.mudar_status_captcha(id_captcha, '1')
            try:
                self.selenium_helper.save_cookies(self.cookies_path)
            except TypeError:
                print("Cookies não foram salvos.")

            return True
        except Exception as e:
            print(e)

    def logout_sistema(self):
        try:
            self.selenium_helper.trocar_frame('topFrame')
            self.selenium_helper.clicar_elemento("a:contains('Sair do Sistema')")

            time.sleep(2)
            self.selenium_helper.trocar_frame('rightFrame')
            self.selenium_helper.clicar_elemento("#buttonLink")

            time.sleep(2)
            Alert(self.driver).accept()
            print('Deslogado com sucesso')
        except Exception as e:
            print(e)

    def menu_nova_proposta(self):
        time.sleep(2)

        try:
            self.selenium_helper.trocar_frame('leftFrame')

            seletor_link = 'a[href="/consignacao/identificacao.jsf"]:visible'
            menu_aberto = self.selenium_helper.buscar_quantidade_elemento(seletor_link)

            if (menu_aberto == 0):
                self.selenium_helper.clicar_elemento_driver('#top')

            self.selenium_helper.clicar_elemento_driver('a[href="/consignacao/identificacao.jsf"]')
            return self.procurar_campos_formulario_identificacao()
        except Exception as e:
            print(e)

    def menu_refinanciamento(self):
        time.sleep(2)

        try:
            self.selenium_helper.trocar_frame('leftFrame')

            seletor_link = 'a[href="/consignacao/identificacao.jsf"]:visible'
            menu_aberto = self.selenium_helper.buscar_quantidade_elemento(seletor_link)

            if (menu_aberto == 0):
                self.selenium_helper.clicar_elemento_driver('#top')

            self.selenium_helper.clicar_elemento_driver(
                'a[href="/consignacao/identificacao.jsf?codigoServico=040"]')
        except Exception as e:
            print(e)

    def procurar_campos_formulario_identificacao(self):
        time.sleep(2)
        self.selenium_helper.trocar_frame('rightFrame')

        tentativas = 0
        while self.driver.execute_script(
                "return $('#identificacao-form\\\\:orgao\\\\:find\\\\:txt-value\\:visible').length") == 0:
            if (tentativas >= 10):
                self.driver.refresh()
                return self.menu_nova_proposta()
            time.sleep(2)
            tentativas += 1
            print('Esperando campos formulário')

    def preencher_formulario_refinanciamento(self, dados_refinanciamento):
        self.selenium_helper.trocar_frame('rightFrame')
        seletor_entidade = '#identificacao-form\\:estabelecimento\\:find\\:txt-value'

        try:
            time.sleep(2)
            if self.selenium_helper.verificar_valor_campo_driver(seletor_entidade) == "":
                self.selenium_helper.atribuir_valor_campo_tab(
                    dados_refinanciamento['entidade'], seletor=seletor_entidade)
                time.sleep(3)
        except NoSuchElementException:
            time.sleep(3)
        if self.selenium_helper.verificar_valor_campo_driver(seletor_entidade) == "":
            self.selenium_helper.atribuir_valor_campo_tab(
                dados_refinanciamento['entidade'], seletor=seletor_entidade)
            time.sleep(3)

        seletor_loading = "#identificacao-form\\\\:estabelecimento\\\\:find\\\\:loading\\:visible"
        while (self.selenium_helper.buscar_quantidade_elemento(seletor_loading) == 1):
            print("Aguardando loading entidade...")
            time.sleep(2)

        seletor_cpf = "#identificacao-form\\:cpf"
        self.selenium_helper.atribuir_valor_campo_driver(
            seletor_cpf, dados_refinanciamento['cpf'])

        if 'federal' in dados_refinanciamento:
            self.preencher_dados_servidor_federal(dados_refinanciamento['matricula'])

        try:
            self.preencher_captcha_formulario_refinanciamento()
        except CaptchaException:
            return self.preencher_formulario_refinanciamento(dados_refinanciamento)

    def preencher_dados_servidor_federal(self, matricula):
        seletor_matricula = "#identificacao-form\\:matricula"
        self.selenium_helper.atribuir_valor_campo_driver(
            seletor_matricula, matricula)

        seletor_situacao = "#identificacao-form\\\\:situacaoDoServidor"
        self.selenium_helper.atribuir_valor_campo_jquery(
            seletor_situacao, 1, change=True)

        time.sleep(2)

    def preencher_captcha_formulario_refinanciamento(self):
        seletor_img_captcha = "#identificacao-form\\:idCaptcha\\:idImagemCaptcha img"
        self.captcha.captcha_path = os.getcwd()
        id_captcha, resposta_captcha = self.captcha.resolver_captcha(
            seletor_img_captcha)

        if (resposta_captcha == 'ERROR NO USER'):
            self.selenium_helper.clicar_elemento_driver(
                "#identificacao-form\\:idCaptcha\\:idCommand")
            raise CaptchaException("Nenhum usuário para responder o captcha!")

        seletor_captcha = "#identificacao-form\\:idCaptcha\\:txt-value"
        self.selenium_helper.atribuir_valor_campo_driver(
            seletor_captcha, resposta_captcha)

        seletor_confirmar = "#identificacao-form\\:idCommandLink"
        self.selenium_helper.clicar_elemento_driver(seletor_confirmar)

        # TODO: testar se está realmente conseguindo evitar erros relativos à abertura de alertas.
        if self.act.verificar_existencia_alerta():
            print(f"Aviso abertura de alerta: {self.act.obter_texto_alerta()}")
            self.act.manusear_alerta(acao='rejeitar')

        self.selecionar_opcao_modal_formulario()
        self.aguardar_loading()

        self.tratar_erros_formulario_refinanciamento(id_captcha)
        self.aguardar_loading()

    def tratar_erros_formulario_refinanciamento(self, id_captcha):
        mensagem_erro = self.driver.execute_script(
            "return $('.error_message\\:visible').text()")
        mensagem_erro = mensagem_erro.strip()

        if mensagem_erro == "":
            return

        mensagens = [
            {
                'texto': r"Não foi encontrado nenhum contrato para o cpf",
                'finalizar': True,
                'aprovar': True
            }, {
                'texto': r"Não foi localizado nenhum contrato com os dados fornecidos.",
                'finalizar': True,
                'aprovar': True
            }, {
                'texto': r"Palavra de verificação da imagem está incorreta, por favor tente novamente.",
                'preencher': True
            }, {
                'texto': r"A palavra de verificação expirou, por favor gere outra imagem.",
                'preencher': True
            }, {
                'texto': r"Não foi possível localizar código do cliente com o CPF.",
                'finalizar': True,
                'aprovar': True
            }, {
                'texto': r"Não foi localizado nenhum contrato com os dados fornecidos.",
                'finalizar': True,
                'aprovar': True
            }
        ]

        for mensagem in mensagens:
            regex = re.compile(mensagem['texto'])
            erro_encontrado = regex.search(mensagem_erro)

            if not erro_encontrado:
                continue

            if 'aprovar' in mensagem:
                print("Captcha Aprovado")
                self.captcha.mudar_status_captcha(id_captcha, '1')
            else:
                print("Catpcha Recusado")
                self.captcha.mudar_status_captcha(id_captcha, '2')

            if 'preencher' in mensagem:
                raise CaptchaException("Captcha recusado!")

            if 'finalizar' in mensagem or 'localizar' in mensagem or 'localizado' in mensagem:
                raise NotFoundResultException(mensagem_erro)

    def selecionar_opcao_modal_formulario(self):
        texto_modal = ""
        modal = self.driver.execute_script(
            """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').find('a:contains("Não")').length""")

        if (modal == 1):
            texto_modal = self.driver.execute_script(
                """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').text()""")
            self.driver.execute_script(
                """$('#identificacao-form\\\\:modalDialog').find('a:contains("Sim")').click()""")
            time.sleep(5)

        return modal, texto_modal

    def fechar_modal_portabilidade(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.selenium_helper.trocar_frame('rightFrame')
        except Exception:
            pass

    def escolher_refinanciamento(self, index, insercao=False):
        time.sleep(1)
        self.selenium_helper.trocar_frame('rightFrame')
        checkbox = self.driver.find_elements_by_css_selector('[type=checkbox]')[index]

        if checkbox.get_property('disabled'):
            raise PularCheckboxException("Checkbox disabled!")

        if not checkbox.get_property('checked'):
            checkbox.click()
            time.sleep(1)
            self.tratar_alerts_refinanciamento()

        self.driver.find_element_by_css_selector('#submitButton').click()
        time.sleep(3)

        try:
            mensagem = self.tratar_alerts_refinanciamento()
            if mensagem == 'restricao':
                raise NotFoundResultException(mensagem)

            if not insercao:
                self.fechar_modal_portabilidade()
            self.aguardar_loading(pre_loading=2, limite=True)

        except EscolherRefinanciamentoException:
            if self.escolher_refinanciamento(index) == 0:
                return 0
        except UnexpectedAlertPresentException:

            mensagem = self.act.obter_texto_alerta()
            print(mensagem)
            if mensagem == 'não eleito':
                raise NotFoundResultException(mensagem)

            return self.escolher_refinanciamento(index)

    def tratar_alerts_refinanciamento(self):
        try:
            alert = self.driver.switch_to.alert
            texto_alerta = alert.text

        except Exception:
            return

        print("Mensagem encontrada: {}".format(texto_alerta))

        if 'não eleito' in texto_alerta:
            raise NotFoundResultException(texto_alerta)


        mensagens = [
            {
                'texto': r"Sistema temporariamente indisponível. Tente mais tarde.",
                'selecionar': True
            }, {
                'texto': r"Favor selecionar pelo menos um contrato para refinanciamento.",
                'selecionar': True
            }, {
                'texto': r"Cliente não eleito a contratação devido a política de crédito.",
                'restricao': True
            }, {
                'texto': r"CPF com status irregular na Receita Federal.",
                'restricao': True
            }, {
                'texto': r"Parametrização de risco operacional não encontrada",
                'restricao': True
            }, {
                'texto': r"O atributo Data Nascimento informado é inválido.",
                'pular': True
            }, {
                'texto': r"Tabela de coeficientes não foi parametrizada corretamente para este produto\/loja",
                'pular': True
            }, {
                'texto': r"Não foi possível localizar código do cliente com o CPF.",
                'selecionar': True
            }, {
                'texto': r"O atributo Valor da Margem informado é inválido. O atributo obrigatório Margem não foi informado.",
                'pular': True
            }, {
                'texto': r"Cliente não elegível a contratação",
                'restricao': True
            }
        ]

        for mensagem in mensagens:
            if 'Sistema temporariamente indisponível' in mensagem['texto']:
                self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
                return -1

            regex = re.compile(mensagem['texto'])
            alerta_encontrado = regex.search(texto_alerta)

            if not alerta_encontrado:
                continue
            try:
                alert.accept()
            except UnexpectedAlertPresentException:
                alert.accept()

            self.fechar_multiplos_alerts(texto_alerta)
            print("depois tentar fechar", mensagem)
            if 'selecionar' in mensagem:
                raise EscolherRefinanciamentoException(
                    "Não foi possível escolher o refinanciamento")

            if 'restricao' in mensagem:
                print(mensagem)
                self.fechar_multiplos_alerts(mensagem)
                raise RestricaoException(mensagem)

            if 'localizar' in mensagem:
                raise NotFoundResultException(texto_alerta)

            if 'return' in mensagem:
                return

        input('Não identificou a mensagem: {}'.format(texto_alerta))

    def fechar_multiplos_alerts(self, texto_base):
        try:
            time.sleep(1)
            texto_alert = Alert(self.driver).text

            if texto_alert == texto_base:
                Alert(self.driver).accept()

            self.fechar_multiplos_alerts(texto_base)
        except Exception:
            return

    def encontrar_matricula_refinanciamento(self, index, matricula):
        linha_completa = self.driver.find_elements_by_css_selector(
            ".contratoDoAmbienteAtual")[index].text
        regex = re.compile("{}".format(matricula))
        matricula_encontrada = regex.search(linha_completa)

        if not matricula_encontrada:
            raise PularCheckboxException("Matricula não encontrada!")

    def encontrar_parcela_refinanciamento(self, index, parcela):
        linha_completa = self.driver.find_elements_by_css_selector(
            ".contratoDoAmbienteAtual")[index].text
        regex = re.compile("{}".format(parcela))

        if not regex.search(linha_completa):
            raise PularCheckboxException("Parcela não encontrada!")

    def calcular_refinanciamento_com_popup(self, valor_parcela, tipo=None):
        print("Selecionando a taxa de juros")
        self.escolher_taxa(tipo)
        self.aguardar_loading()

        print("Apagando campo valor solicitado")
        self.selenium_helper.atribuir_valor_campo_driver(
            '#ade\\.valorEmprestimo', '')
        time.sleep(2)

        print("Preenchendo valor da parcela")
        self.preencher_valor_parcela(valor_parcela)

        print("Simulando refinanciamento")
        self.selenium_helper.clicar_elemento_driver('#simulacao')
        print("Buscando valor soclitado no popup de acordo com maior prazo disponivel")
        self.leitura_popup_simulacao()

        print("Preenchendo valor solicitado:", self.valor_solicitado)
        self.selenium_helper.atribuir_valor_campo_driver(
            '#ade\\.valorEmprestimo', self.valor_solicitado)
        time.sleep(2)

        print("Preenchendo prazo:", self.prazo)
        self.selenium_helper.atribuir_valor_campo_driver(
            '#ade\\.quantidadePrestacoes', self.prazo)
        time.sleep(2)
        print("Preenchendo valor da parcela:", valor_parcela)
        self.preencher_valor_parcela(valor_parcela)
        time.sleep(3)
        self.aguardar_loading()

        print("Recalculando valores do refinanciamento")
        self.recalcular_valores_refinanciamento()
        self.aguardar_loading()

        # loc_max_lib = '//*[@id="label_ade.valorLiberadoComIof"]'
        # valor_max = self.act.obter_texto(loc_max_lib, By.XPATH)
        # if tipo == "INSERCAO" and not valor_max:
        #     loc = '//*[@id="ade.codigoCarencia"]'
        #     self.act.forcar_clique_stale_element(loc, By.XPATH, pause=0)
        #     self.act.select_drop_down(loc, '2208', By.XPATH)
        #
        #     self.aguardar_loading()
        #     time.sleep(1)
        #     self.act.forcar_clique_stale_element(loc, By.XPATH, pause=0)
        #     self.act.select_drop_down(loc, '2176', By.XPATH)
        #
        #     self.aguardar_loading()
        #     time.sleep(1)
        #
        #     self.act.forcar_clique_stale_element(loc, By.XPATH, pause=0)
        #     self.escolher_taxa(tipo)
        #     time.sleep(1)
        #     self.aguardar_loading()

        time.sleep(4)
        self.selenium_helper.atribuir_valor_campo_driver(
            '#ade\\.quantidadePrestacoes', self.prazo)
        time.sleep(3)
        try:
            loc_prazo = '[id="ade.quantidadePrestacoes"]'
            self.act.press_TAB(loc_prazo)
        except TimeoutException:
            print("!!!")
        print("Extraindo valor liberado máximo...", end='')
        loc_val_max = '//*[@id="label_refinanciamento.valorAdicionalComIof"]'
        self.valor_liberado_maximo = self.act.obter_texto(
            seletor=loc_val_max, metodo=By.XPATH
        )
        print(self.valor_liberado_maximo)

    def preencher_valor_parcela(self, valor_parcela, rec=0):
        time.sleep(3)
        try:
            print(f"[{rec}] Preenchendo parcela:", valor_parcela)
            if rec >= 2:
                raise Exception("Não foi possivel preencher parcela")

            if self.selenium_helper.buscar_quantidade_elemento(
                    '#ade\\\\.valorPrestacao\\:visible') == 1:

                self.selenium_helper.atribuir_valor_campo_driver(
                    '#ade\\.valorPrestacao', valor_parcela)
                time.sleep(2)

        except InvalidElementStateException as e:
            print(e)
            self.preencher_valor_parcela(valor_parcela, rec+1)
        except TimeoutException as e:
            print(e)
            self.preencher_valor_parcela(valor_parcela, rec+1)
        except StaleElementReferenceException as e:
            print(e)
            self.preencher_valor_parcela(valor_parcela, rec+1)

    def escolher_taxa(self, tipo=None):
        seletor_taxa = '#label_refinanciamento\\.taxaContratoOrigem'
        taxa_atual = self.selenium_helper.verificar_texto_campo_driver(seletor_taxa)
        # taxa_atual = float(taxa_atual.replace(',', '.'))
        options, seletor_carencia = self.identificar_campo_carencia()
        valor_carencia = self.__filtrar_tabela_carencia(tipo)

        self.selenium_helper.atribuir_valor_campo_jquery(
            seletor_carencia, valor_carencia, change=True)

    def identificar_campo_carencia(self):
        seletores_carencia = [
            {
                'jquery': "#ade\\\\.codigoCarencia{}",
                'driver': "#ade\\.codigoCarencia{}"
            }, {
                'jquery': "#ade\\\\.codigoTabelaEspecial{}",
                'driver': "#ade\\.codigoTabelaEspecial{}"
            }
        ]

        for seletor_carencia in seletores_carencia:
            quantidade = self.selenium_helper.buscar_quantidade_elemento(
                seletor_carencia['jquery'].format(" option")
            )

            if quantidade > 0:
                options = self.driver.find_elements_by_css_selector(
                    seletor_carencia['driver'].format(" option")
                )

                return options, seletor_carencia['jquery'].format("")

    def leitura_popup_simulacao(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        regex = re.compile('icones/ok.gif')

        linhas = self.driver.find_elements_by_css_selector('#tableSimulacaoIdeal tr')
        linhas_encontradas = [linha for linha in linhas for match in [
            regex.search(linha.get_attribute('innerHTML'))] if match]

        self.prazo = False
        self.valor_solicitado = False

        if len(linhas_encontradas) >= 1:
            self.prazo, self.valor_solicitado = linhas_encontradas[-1].text.split(' ')

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.selenium_helper.trocar_frame('rightFrame')

        if self.valor_solicitado is False:
            raise PularCheckboxException(
                "Não foi possível encontrar o valor solicitado!")

    def recalcular_valores_refinanciamento(self):
        self.driver.execute_script("""
            buscaValorCapitalSegurado();
            buscaCoeficienteAndExpansaoIofAjax();
            calculoPercentualComissaoAjax();
        """)

    def filtrar_entidade(self, dados):
        
        entidade: str = ''

        if 'estadual' in dados:
            dados['sigla'] = dados['sigla'].upper()
            if dados['sigla'] == 'MT':
                entidade = '243'
            elif dados['sigla'] == "SP":
                entidade = "4195"
                if dados["orgao"] in ["66", "67"]:
                    entidade = "4193"
                elif dados["orgao"] in ["80", "81"]:
                    entidade = "4194"
            elif dados['sigla'] == "RJ":
                entidade = "1"

        elif 'federal' in dados:
            entidade = "164"
        elif 'municipal' in dados and dados['cidade'] == "São Paulo":
            entidade = "128"
        elif 'municipal' in dados and dados['cidade'] == "Praia Grande":
            entidade = "3710"
        elif 'inss' in dados:
            entidade = "1581"

        return entidade

    def aguardar_loading(self, pre_loading=0, pos_loading=2, limite=False):
        try:
            self.limite_loading = 100
            time.sleep(pre_loading)

            while self.selenium_helper.buscar_quantidade_elemento('.carregando.inivisivel\\:visible') >= 1:
                print('Esperando o loading...')
                time.sleep(3)
                if limite: self.verificar_limite()

            while self.selenium_helper.buscar_quantidade_elemento('.carregando\\:visible') >= 1:
                print('Esperando o loading...')
                time.sleep(3)
                if limite: self.verificar_limite()

            time.sleep(pos_loading)
        except Exception as e:
            print("Loading erro: ", e)

    def verificar_limite(self):
        self.limite_loading -= 1

        if self.limite_loading < 1:
            raise PularCheckboxException("Não foi possível selecionar o contrato")

    def form_servidor_federal(self, cpf, matricula):
        # Requisição dos dados do servidor
        api_url = 'http://www.transparencia.gov.br/api-de-dados/servidores/remuneracao'

        # ano_mes = date_time_to_list()[0:2]
        # ano_mes_str = str(ano_mes[0]) + str(ano_mes[1] - 1)

        params = {
            'cpf': cpf,
            'mesAno': '202001'
        }
        print(params)
        dados = requests.get(
            api_url,
            params=params
        )
        print(dados, dados.text)

        if dados.status_code != 200:
            print(f"Impossível completar requisição. Status: {dados}")
        if not dados.json():
            return 0

        dados_servidor = dados.json()[0]['servidor']
        codigo_orgao = dados_servidor["orgaoServidorExercicio"]['codigo']
        codigo_situacao = dados_servidor["situacao"]['codigo']

        # Localizar órgão do servidor
        loc_pesquisa = 'img[src="/img/icones/pesquisar.gif"]'
        self.act.clicar_elemento(loc_pesquisa)
        time.sleep(2)

        self.act.trocar_frame_referencia("rightFrame")
        loc_campo_pesquisa = '//*[@id="identificacao-form:orgao:find:filter-group"]/tbody/tr[1]/td[2]/input'
        self.act.enviar_texto(loc_campo_pesquisa, codigo_orgao, By.XPATH)

        loc_botao_pesquisa = '//a[@id="identificacao-form:orgao:find:btPesq"]'
        self.act.clicar_elemento(loc_botao_pesquisa, By.XPATH)

        loc_botao_ok = 'img[src="/img/icones/ok.gif"]'
        self.act.clicar_elemento(loc_botao_ok)

        # Selecionar situaçao do cliente
        loc_menu_select = 'select[name="identificacao-form:situacaoDoServidor"]'
        select_key_values = get_select_options_values(loc_menu_select, self.act)
        codigo_situacao_strip = strip_zero_left(codigo_situacao)
        for key, val in select_key_values.items():
            if key == 'Selecione':
                continue
            key_code = key.split('-')[0].strip()
            key_nome = key.split('-')[1].strip()
            if (codigo_situacao_strip in key_code and len(codigo_situacao_strip) == len(key_code)) or \
                    (codigo_situacao_strip in key_nome):
                self.act.select_drop_down(loc_menu_select, val)

        # Inserir CPF
        loc_CPF_input = 'input[name="identificacao-form:cpf"]'
        self.act.clicar_elemento(loc_CPF_input)
        self.act.enviar_texto(loc_CPF_input, cpf)

        # Inserir Matrícula
        if(len(matricula) > 7):
            matricula_remover = len(matricula) - 7
            matricula = matricula[matricula_remover:]

        loc_matricula_input = 'input[name="identificacao-form:matricula"]'
        self.act.clicar_elemento(loc_matricula_input)
        self.act.enviar_texto(loc_matricula_input, matricula)

    def form_servidores_sp(self, contrato):
        print("***teste***")
        print(f"Conulta Servidor de Sp: {contrato['entidade']}")
        # Alterar frame
        self.act.trocar_frame_referencia('rightFrame')

        # Inserir entidade
        loc_entidade_input = '//*[@id="identificacao-form:orgao:find:txt-value"]'
        self.act.enviar_texto(loc_entidade_input, contrato['entidade'], By.XPATH)
        # Inserir CPF
        loc_CPF_input = 'input[name="identificacao-form:cpf"]'
        self.act.clicar_elemento(loc_CPF_input)
        time.sleep(5)
        self.act.enviar_texto(loc_CPF_input, contrato['cpf'], clear=False)

    def __filtrar_tabela_carencia(self, tipo=None):
        print("Obtendo taxa de juros do contrato de origem.")

        # Obter Taxa de Juros do Cotrato de Origem
        loc_tx_origem = '//*[@id="label_refinanciamento.taxaContratoOrigem"]'
        tx_origem = self.act.obter_texto(loc_tx_origem, By.XPATH)
        tx_origem = float(tx_origem.replace(',', '.'))
        select_val = 0
        print("Taxa:", tx_origem)

        # Comparar Taxa de Juros com Taxas da Tabela
        if tipo == "NOVO_MARGEM":
            if tx_origem >= 2.03:
                select_val = 1283
            elif tx_origem >= 1.89:
                select_val = 1284
        else:
            if tx_origem >= 1.8:
                select_val = 2109
            elif tx_origem >= 1.72:
                select_val = 2122
            elif tx_origem >= 1.56:
                select_val = 2176
            elif tx_origem >= 1.40:
                select_val = 2208
        print('Select val:', select_val)
        return str(select_val)


class CaptchaException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


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


class EscolherRefinanciamentoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PreenchimentoTabelaException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class PreenchimentoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message