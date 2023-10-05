import os
import PyPDF2
import re
import requests
import unidecode
import json

from time import sleep
from selenium import webdriver
from sites.inss.legado.helpers import *
from sites.baseRobos.core.helpers import (
    countdown, definir_nome_robo, identificar_erro_robo
)
from sites.core.uconecte import Uconecte
from selenium.webdriver.chrome.options import Options
from sites.core.selenium_actions import SeleniumActions
from sites.core.selenium_helper import SeleniumHelper
from selenium.common.exceptions import (
    TimeoutException, NoSuchWindowException, JavascriptException,
    ElementClickInterceptedException, WebDriverException
)
from selenium.webdriver.common.by import By


class Inss:
    user = {
        'pc': '--user-data-dir=C:/Users/gustavo/AppData/Local/Google/Chrome/inss',
        'serv': '--user-data-dir=C:/Users/lucas.s/AppData/Local/Google/Chrome/inss'
    }

    caminho_base = os.getcwd().replace('\\', '/')
    path = {
        'pc': "C:\\Users\\gustavo\\Documents\\automacao-python\\drivers\\chromedriver.exe",
        'serv': caminho_base + '/drivers/chromedriver.exe'
    }

    def __init__(self):
        options = Options()
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(self.user['pc'])

        self.pdf_path = self.caminho_base + '/sites/inss'

        prefs = {
            "download.default_directory": self.pdf_path.replace('/', '\\'),
            # 'download.default_directory': "C:\\Users\\arthur.l\\Documents\\automacao-python\\sites\\inss",
            'profile.default_content_setting_values.automatic_downloads': True,
            'download.prompt_for_download': False,
            'plugins.plugins_disabled': 'Chrome PDF Viewer'
        }

        options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(
            executable_path=self.path['pc'],
            options=options
        )
        self.driver.delete_all_cookies()

        self.api_key = '304b5b69eeb3921790c9e7ed9f4df504'
        self.ultima_atualizacao = datetime.now()
        self.timer = 600
        self.uconecte = Uconecte()
        self.act = SeleniumActions(self.driver, time_out=2)
        self.selenium = SeleniumHelper(self.driver)
        self.estava_logado = False
        self.data_site_key = '6LeVYrUUAAAAAM7ZsAaZS5tpZOD6AwG8-1Nm6Iep'
        self.margem_emprestimo = ''
        self.margem_cartao = ''
        self.base_calculo = ''
        self.dados_banco = {}
        self.dados_emprestimo = {}
        self.arrayConsultaRefin = []
        self.arrayParcelasRefin = []
        self.beneficio = ''
        self.id_robo = 17

    def login(self, perfil):
        """
        Função de login no portal Meu INSS. O portal possui um reCaptcha v2 e é às vezes é necessário resolvê-lo para
        que o login seja bem sucedido. A função também verifica se o usuário e/ou senha são inválidos. Caso seja,
        reprova a solicitação. Vale ressaltar, também, que o login ocorre em uma janela pop-up, por isso é necessário
        trocar de janelas durante a execução da função.

        :param perfil: array com as informações do Beneficiário, como CPF e senha.
        """
        print('Realizando login...')

        if not self.estava_logado:
            self.driver.get(" https://sso.acesso.gov.br/login?client_id=meu.inss.gov.br")
            self.aguardar_loading_incial()
            page_state = self.driver.execute_script('return document.readyState;')
            while page_state != 'complete':
                page_state = self.driver.execute_script('return document.readyState;')
                sleep(1)

            try:
                loc_botao_login = '//div/form/button[1]'
                self.act.clicar_elemento(loc_botao_login, By.XPATH)
            except TimeoutException:
                loc_menu_emp = "#area_lista > div > ul > li:nth-child(10) > a > div > span"
                self.act.clicar_elemento(loc_menu_emp)

                loc_botao_login = '#eaps-involucro > section > div > button'
                self.act.clicar_elemento(loc_botao_login)
            except ElementClickInterceptedException:
                loc_menu_emp = "#area_lista > div > ul > li:nth-child(10) > a > div > span"
                self.act.clicar_elemento(loc_menu_emp)

                loc_botao_login = '#eaps-involucro > section > div > button'
                self.act.clicar_elemento(loc_botao_login)

        self.act.trocar_janela(1, 2)  # troca para o pop up de login

        page_state = self.driver.execute_script('return document.readyState;')
        while page_state != 'complete':
            page_state = self.driver.execute_script('return document.readyState;')
            sleep(1)

        loc_cpf = '#j_username'
        self.act.enviar_texto(loc_cpf, perfil['cpf'])

        loc_botao_proxima = '#kc-login'
        self.act.clicar_elemento(loc_botao_proxima)

        self.verificar_erros(perfil)

        loc_senha = '#j_password'
        self.act.enviar_texto(loc_senha, perfil['senhaAcesso'])

        while self.act.obter_valor(loc_senha) == "":
            self.act.enviar_texto(loc_senha, perfil['senhaAcesso'])

        loc_botao_entrar = '#submit-button'
        self.act.clicar_elemento(loc_botao_entrar)

        try:
            self.act.obter_atributo('body > div:nth-child(11)', 'style')
            self.act.reCaptcha_v2(self.data_site_key, 'onSubmit')
        except TimeoutException:
            pass
        except AttributeError:
            pass

        try:
            self.verificar_erros(perfil)
        except NoSuchWindowException:
            pass

        self.act.trocar_janela(0, 1)
        print('Login realizado com sucesso!')

    def main(self):
        self.uconecte.atualizar_status_robo(self.id_robo)

        try:
            os.remove("C:\\Users\\gustavo\\Documents\\automacao-python\\"
                      "sites\\inss\\extrato-emprestimos-consignados.pdf")  # verifica se existe um PDF na pasta quando o programa inicia. Caso sim, o remove.
        except FileNotFoundError:
            pass

        self.driver.get("https://meu.inss.gov.br/central/#/emprestimo-consignado")
        while True:
            try:
                self.verifica_horario_comercial()
                self.buscar_margem()
                self.verificar_tempo_execucao()
            except Exception as e:
                identificar_erro_robo()
                raise Exception(str(e))

    def buscar_margem(self):
        """
        Função responsável por coordenar a busca da margem. Ela tenta fazer o login no portal e, caso já exista uma
        conta logada, faz o logout antes de continuar.
        """
        perfis = self.buscar_perfis()
        for perfil in perfis:
            definir_nome_robo('Consulta Margem INSS')
            if (similaridade(perfil['idContrato'], "794673") > 70 or
                    similaridade(perfil['idContrato'], "794680") > 70 or
                    similaridade(perfil['idContrato'], "794730") > 75 or
                    similaridade(perfil['idContrato'], "794695") > 75):
                continue

            print(f'\nTrabalhando no contrato {perfil["codigoContrato"]}...')

            try:
                self.login(perfil)

                if 'selo' in self.driver.current_url:
                    self.finaliza_consulta_info_falha(perfil,
                                                      "CPF informado não foi localizado no Cadastro Nacional de "
                                                      "Informações Sociais (CNIS). Realize sua inscrição no "
                                                      "Portal do INSS.")
                    continue
            except TimeoutException:
                self.estava_logado = True
                self.logout()
                self.estava_logado = False
                try:
                    self.login(perfil)
                    if 'selo' in self.driver.current_url:
                        self.finaliza_consulta_info_falha(perfil,
                                                          "CPF informado não foi localizado no Cadastro Nacional de "
                                                          "Informações Sociais (CNIS). Realize sua inscrição no "
                                                          "Portal do INSS.")
                        continue
                except RecuperacaoConta:
                    self.margem_cartao = ""
                    self.margem_emprestimo = ""
                    self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                                   "E necessario definir uma nova "
                                                   "senha para o cadastro.")
                    self.finaliza_consulta_info_falha(perfil,
                                                      "E necessario definir uma nova senha para o cadastro.")
                    continue
                except UsuarioErrado:
                    self.margem_cartao = ""
                    self.margem_emprestimo = ""
                    self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                                   "Usuario e/ou senha invalidos.")
                    self.finaliza_consulta_info_falha(perfil, "Usuario e/ou senha invalidos.")
                    continue
                except CPFsemCadastro:
                    self.margem_cartao = ""
                    self.margem_emprestimo = ""
                    self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                                   "CPF sem cadastro no meu INSS.")
                    self.finaliza_consulta_info_falha(perfil, "CPF sem cadastro no meu INSS.")
                    continue
            except RecuperacaoConta:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                               "E necessario definir uma nova "
                                               "senha para o cadastro.")
                self.finaliza_consulta_info_falha(perfil,
                                                  "E necessario definir uma nova senha para o cadastro.")
                continue
            except UsuarioErrado:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                               "Usuario e/ou senha invalidos.")
                self.finaliza_consulta_info_falha(perfil, "Usuario e/ou senha invalidos.")
                continue
            except CPFsemCadastro:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                               "CPF sem cadastro no meu INSS.")
                self.finaliza_consulta_info_falha(perfil, "CPF sem cadastro no meu INSS.")
                continue

            if not self.achar_matricula(perfil):
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 0,
                                               "Matricula nao encontrada.")
                self.finaliza_consulta_info_falha(perfil, "Matricula nao encontrada")
                continue

            try:
                self.verificacoes()
            except BloqueadoError:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 2,
                                               "Bloqueado para emprestimo.")
                continue
            except RepresentanteError:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 3,
                                               "Possui representante legal.")
                continue
            except MargemError:
                self.margem_cartao = ""
                self.margem_emprestimo = ""
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 4,
                                               "Nenhuma informação encontrada ")
                self.finaliza_consulta_info_falha(perfil, 'Não abriu informações para o benefício.')
                continue

            try:
                self.verificar_erros()
            except MargemError:
                continue

            self.pegar_dados_banco()
            self.pegar_dados_emprestimo()

            if not self.pegar_margem_pdf():
                continue

            print(f"Margem Empréstimo: {formatar_valor(self.margem_emprestimo, False)}")
            print(f"Margem Cartão: {formatar_valor(self.margem_cartao, False)}")

            self.finaliza_consulta_info_sucesso(perfil)

            if perfil['tipoContrato'] == "Empréstimo":
                self.atualiza_perfil_web_admin(perfil, self.margem_emprestimo, 1,
                                               "Margem de emprestimo consultada "
                                               "com sucesso!")
            elif perfil['tipoContrato'] == "Cartão":
                self.atualiza_perfil_web_admin(perfil, self.margem_cartao, 1,
                                               "Margem do cartao consultada "
                                               "com sucesso!")
            else:
                input('Status não cadastrado!')

            self.logout()
            print(f'Finalizando contrato {perfil["codigoContrato"]}...')

    def pegar_dados_banco(self):
        print("Colentado informações sobre o banco...")
        self.aguardar_loagind_barra(True)
        banco = self.act.obter_texto("#eaps-involucro > div > section.area-conteudo > div > div > "
                                     "section:nth-child(2) > div.eco-box-inst-pag-campos > "
                                     "div.eco-campo.eco-box-inst-pag-cod-nome > span > span:nth-child(2)")
        cod_banco = self.act.obter_texto(
            "#eaps-involucro > div > section.area-conteudo > div > div > "
            "section:nth-child(2) > div.eco-box-inst-pag-campos > "
            "div.eco-campo.eco-box-inst-pag-cod-nome > span > span:nth-child(1)")

        tipo_conta_over = self.act.obter_texto(
            "#eaps-involucro > div > section.area-conteudo > div > div > "
            "section:nth-child(2) > div.eco-box-inst-pag-campos > "
            "div.eco-box-inst-pag-creditos > div > div:nth-child(2) > span > span")

        agencia = self.act.obter_texto(
            "#eaps-involucro > div > section.area-conteudo > div > div > "
            "section:nth-child(2) > div.eco-box-inst-pag-campos > "
            "div.eco-box-inst-pag-creditos > div > div:nth-child(3) > span")

        if tipo_conta_over == "Conta Corrente":
            conta_over = self.act.obter_texto(
                "#eaps-involucro > div > section.area-conteudo > div > div > "
                "section:nth-child(2) > div.eco-box-inst-pag-campos > "
                "div.eco-box-inst-pag-creditos > div > div:nth-child(4) > span")

            conta = conta_over[:(len(conta_over) - 1)]
            digitoConta = conta_over[len(conta_over) - 1]
        else:
            conta = ''
            digitoConta = ''

        tipo_conta = unidecode.unidecode(tipo_conta_over)

        self.dados_banco = {
            "banco": cod_banco + ' - ' + banco,
            "agencia": agencia,
            "conta": conta,
            "digitoConta": digitoConta,
            "tipoConta": tipo_conta,
        }

    def pegar_dados_emprestimo(self):
        print("Colentando informações sobre os emprestimos...")
        try:
            qtd_linhas = self.driver.execute_script(
                "return document.querySelector('#eaps-involucro > div > "
                "section.area-conteudo > div > div > "
                "section.eco-box-contratos-emprestimos > "
                "div.eco-box-cont-emp-campos "
                " > div > div.eco-box-cont-emp-body').childElementCount")
        except JavascriptException:
            print("Perfil não possui emprestimos ativos!")
            return
        except WebDriverException:
            print("Perfil não possui emprestimos ativos!")
            return

        if qtd_linhas == 1:
            # cod_emp = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
            #                                f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > "
            #                                f"div > div.eco-box-cont-emp-body > div > "
            #                                f"span.box-cont-emp-coluna.cl1")

            situacao = self.act.obter_texto(
                f"#eaps-involucro > div > section.area-conteudo > div > div > "
                f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > "
                f"div > div.eco-box-cont-emp-body > div > span.box-cont-emp-coluna.cl2")

            cod_banco = get_agencia(
                self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo >"
                                     f" div > div > section.eco-box-contratos-emprestimos > "
                                     f"div.eco-box-cont-emp-campos > div > "
                                     f"div.eco-box-cont-emp-body > div > "
                                     f"span.box-cont-emp-coluna.cl4"))

            parcelas = self.act.obter_texto(
                f"#eaps-involucro > div > section.area-conteudo > div > div > "
                f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > "
                f"div > div.eco-box-cont-emp-body > div > span.box-cont-emp-coluna.cl9")

            valor_parcelas = formatar_valor(self.act.obter_texto(f"#eaps-involucro > div > "
                                                                 f"section.area-conteudo "
                                                                 f"> div > div > "
                                                                 f"section.eco-box-contratos-emprestimos "
                                                                 f"> div.eco-box-cont-emp-campos > div > "
                                                                 f"div.eco-box-cont-emp-body > "
                                                                 f"div > "
                                                                 f"span.box-cont-emp-coluna.cl10"),
                                            True)

            data_inicio = self.act.obter_texto(
                f"#eaps-involucro > div > section.area-conteudo > div > div > "
                f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos "
                f"> div > div.eco-box-cont-emp-body > div > "
                f"span.box-cont-emp-coluna.cl6")

            # data_fim = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
            #                                 f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > "
            #                                 f"div > div.eco-box-cont-emp-body > div > "
            #                                 f"span.box-cont-emp-coluna.cl7")
            #
            # inclusao = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
            #                                 f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > "
            #                                 f"div > div.eco-box-cont-emp-body > div > "
            #                                 f"span.box-cont-emp-coluna.cl8")

            valor_emp = formatar_valor(
                self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > "
                                     f"div > div > section.eco-box-contratos-emprestimos "
                                     f"> div.eco-box-cont-emp-campos > div > "
                                     f"div.eco-box-cont-emp-body > div > "
                                     f"span.box-cont-emp-coluna.cl11"), True)
            self.dados_emprestimo = {
                "numeroBanco": cod_banco,
                "valorPresenteInicial": valor_emp,
                "parcela": valor_parcelas,
                "parcelasPagas": str(calcula_parcelas_pagas(data_inicio)),
                "parcelasTotais": parcelas,
                "dataInicioDesconto": data_inicio,
                # "dataFinalDesconto": data_fim,
                # "dataInclusao": inclusao,
                "statusContrato": situacao
                # "codigoEmprestimo": cod_emp
            }

            self.arrayParcelasRefin.append(valor_parcelas)
            self.arrayConsultaRefin.append(self.dados_emprestimo)

        else:
            for index in range(1, qtd_linhas + 1):
                # cod_emp = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
                # f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos > " f"div >
                # div.eco-box-cont-emp-body > div:nth-child({str(index)}) > " f"span.box-cont-emp-coluna.cl1")

                situacao = self.act.obter_texto(
                    f"#eaps-involucro > div > section.area-conteudo > div > div > "
                    f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos >"
                    f" div > div.eco-box-cont-emp-body > div:nth-child({str(index)}) > "
                    f"span.box-cont-emp-coluna.cl2")

                cod_banco = get_agencia(
                    self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo >"
                                         f" div > "
                                         f"div > section.eco-box-contratos-emprestimos > "
                                         f"div.eco-box-cont-emp-campos > div > "
                                         f"div.eco-box-cont-emp-body > div:nth-child("
                                         f"{str(index)}) > span.box-cont-emp-coluna.cl4"))

                parcelas = self.act.obter_texto(
                    f"#eaps-involucro > div > section.area-conteudo > div > div > "
                    f"section.eco-box-contratos-emprestimos > "
                    f"div.eco-box-cont-emp-campos > "
                    f" div > div.eco-box-cont-emp-body > div:nth-child({str(index)}) > "
                    f"span.box-cont-emp-coluna.cl9")

                valor_parcelas = formatar_valor(self.act.obter_texto(f"#eaps-involucro > div > "
                                                                     f"section.area-conteudo "
                                                                     f"> div > div > "
                                                                     f"section.eco-box-contratos-emprestimos "
                                                                     f"> div.eco-box-cont-emp-campos > div > "
                                                                     f"div.eco-box-cont-emp-body > "
                                                                     f"div:nth-child({str(index)}) > "
                                                                     f"span.box-cont-emp-coluna.cl10"),
                                                True)

                data_inicio = self.act.obter_texto(
                    f"#eaps-involucro > div > section.area-conteudo > div > div > "
                    f"section.eco-box-contratos-emprestimos > "
                    f"div.eco-box-cont-emp-campos "
                    f"> div > div.eco-box-cont-emp-body > div:nth-child({str(index)}) > "
                    f"span.box-cont-emp-coluna.cl6")

                # data_fim = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
                # f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos >" f" div >
                # div.eco-box-cont-emp-body > div:nth-child({str(index)}) > " f"span.box-cont-emp-coluna.cl7")
                #
                # inclusao = self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > div > div > "
                # f"section.eco-box-contratos-emprestimos > div.eco-box-cont-emp-campos >" f" div >
                # div.eco-box-cont-emp-body > div:nth-child({str(index)}) > " f"span.box-cont-emp-coluna.cl8")

                valor_emp = formatar_valor(
                    self.act.obter_texto(f"#eaps-involucro > div > section.area-conteudo > "
                                         f"div > div > section.eco-box-contratos"
                                         f"-emprestimos "
                                         f"> div.eco-box-cont-emp-campos > div > "
                                         f"div.eco-box-cont-emp-body > div:nth-child( "
                                         f"{str(index)}) > "
                                         f"span.box-cont-emp-coluna.cl11"), True)

                self.dados_emprestimo = {
                    "numeroBanco": cod_banco,
                    "valorPresenteInicial": valor_emp,
                    "parcela": valor_parcelas,
                    "parcelasPagas": str(calcula_parcelas_pagas(data_inicio)),
                    "parcelasTotais": parcelas,
                    "dataInicioDesconto": data_inicio,
                    # "dataFinalDesconto": data_fim,
                    # "dataInclusao": inclusao,
                    "statusContrato": situacao
                    # "codigoEmprestimo": cod_emp
                }

                self.arrayParcelasRefin.append(valor_parcelas)
                self.arrayConsultaRefin.append(self.dados_emprestimo)

    def error(self, tentativa):
        if tentativa < 2:
            try:
                while self.act.quantidade_elemento(
                        "#eaps-involucro > div > label.no-content-primary-text") > 0:

                    error = self.act.retornar_elemento(
                        "#eaps-involucro > div > label.no-content-primary-text")

                    if "Ocorreu" in error.text:
                        self.act.clicar_elemento("#eaps-involucro > div > button")
                        self.aguardar_loading_body()
            except TimeoutException:
                tentativa += 1
                pass

            try:
                while self.act.quantidade_elemento("#eaps-involucro > div > section > div > "
                                                   "label.no-content-primary-text") > 0:

                    error = self.act.retornar_elemento("#eaps-involucro > div > section > div > "
                                                       "label.no-content-primary-text")

                    if "Ocorreu" in error.text:
                        self.act.clicar_elemento("#eaps-involucro > div > section > div > button")
                        self.aguardar_loading_body()
            except TimeoutException:
                tentativa += 2
                self.error(tentativa)

    def achar_matricula(self, perfil):
        """
        Função que compara a matricula da solicitação com as matriculas existes no portal. Caso encontre a matrícula,
        acessa suas informações, caso contrário, avisa que não encontrou a matrícula e reprova a solicitação.

        :param perfil: Array com as informações do Beneficiário, como a matrícula.
        :return: True se encontrou a matrícula e False caso contrário.
        """
        breakpoint()

        print('Selecionando matricula...')
        # self.aguardar_loading_body()

        sleep(1)
        try:
            text = self.act.obter_texto("#eaps-involucro > div > label.no-content-primary-text")
            if 'Não foram encontrados benefícios para você' in text:
                return False
            else:
                self.error(0)
        except TimeoutException:
            self.error(0)

        linhas = self.driver.find_elements_by_css_selector('.item-texto')

        if not linhas:
            loc_btn_emprestimo = '#area_lista > div > ul > li:nth-child(10) > a'
            self.act.clicar_elemento(loc_btn_emprestimo)
            sleep(1)
            linhas = self.driver.find_elements_by_css_selector('.item-texto')

        count = 1

        for linha in linhas:
            if linhas.index(linha) % 3 == 0:
                count += 1
                if len(perfil['matricula']) == 11:
                    if int(similaridade(linha.text,
                                        formatar_matricula(perfil['matricula'], 2)) > 74):
                        self.act.clicar_elemento(
                            f"#eaps-involucro > div > section > div > a:nth-child({count}) > div")
                        return True
                elif len(perfil['matricula']) == 10:
                    if int(similaridade(linha.text,
                                        formatar_matricula(perfil['matricula'], 1))) > 74:
                        self.act.clicar_elemento(
                            f"#eaps-involucro > div > section > div > a:nth-child({count}) > div")
                        return True
                else:
                    if int(similaridade(linha.text, perfil['matricula'])) > 74:
                        self.act.clicar_elemento(
                            f"#eaps-involucro > div > section > div > a:nth-child({count}) > div")
                        return True

        print('Matricula não encontrada!')
        return False

    def verificacoes(self):
        """
        Função que verifica algumas restrições nas informações da matricula selecionada, são elas:
            - Nenhuma informação existe para aquela matricula;
            - Matrícula possui representante legal e, portanto, não é disponibilizado suas margens.
        Em ambos os casos, a mensagem é exibida na tela e a solicitação reprovada.

        :return: True caso não exista nenhuma restrição e False caso exista.
        """
        self.aguardar_loagind_barra(True)
        try:
            elemento = self.act.retornar_elemento(
                "#eaps-involucro > div > section.app-mensagem > span.texto")
            if 'Nenhuma informação encontrada para o documento' in elemento.text:
                print(elemento.text)
                raise MargemError(message=elemento.text)
        except TimeoutException:
            pass

        try:
            ce = self.act.retornar_elemento(
                "#eaps-involucro > div > section.area-conteudo > div > div > "
                "section.eco-box-beneficio > div.eco-box-benef-campos > "
                "div.eco-box-flex-pensao-benef > div.eco-box-benef-elegivel-emprestimo > "
                "div:nth-child(1) > span")
            if ce.text == 'Sim':
                print('Perfil está bloqueado para emprestimos')
                raise BloqueadoError(message="Perfil está bloqueado para empréstimo")
        except TimeoutException:
            pass

        try:
            rl = self.act.retornar_elemento(
                "#eaps-involucro > div > section.area-conteudo > div > div > section.eco-box-beneficio > "
                "div.eco-box-benef-campos > div.eco-box-flex-pensao-benef > div.eco-box-benef-pensao > div:nth-child("
                "2) > span")

            if rl.text == 'Sim':
                print(
                    'Não foi possível verificar a margem pois essa solicitação possui representante legal.')
                raise RepresentanteError(message="Perfil possui representante legal!")

            return
        except TimeoutException:
            return

    def pegar_margem_pdf(self):
        """
        Função responsável por pegar a Margem de emprestimo e a Margem de cartão do beneficiário do arquivo em PDF. Para
        isso, a função baixa o PDF, abre-o e pega os textos da primeira página do arquivo. Normalmente, esses dados
        estão localizados no faixa de 405-510 do array de texto, então a função varre somente essa faixa. Caso ocorra
        algum problema na busca da margem, é provável que o erro esteja na faixa, podendo ser que ela não esteja abran-
        gendo as informações, então deve-se aumentá-la.

        :return: True se encontra as margens e False caso haja alguma restrição.
        """
        try:
            print('Buscando margens...')
            self.aguardar_loagind_barra(True)

            self.verificar_erros()

            self.margem_emprestimo = ''
            self.margem_cartao = ''
            self.base_calculo = ''

            self.verificar_erros()
            self.download_pdf()

            pdfFile = open('extrato-emprestimos-consignados.pdf', 'rb')
            # pdfFile = open(self.caminho_base+'/sites/inss/extrato-emprestimos-consignados.pdf', 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFile)

            page = pdfReader.getPage(0)
            texto = page.extractText()
            index = texto[405:460].find('$')

            for index in range((405 + index + 2), 480):
                if texto[index] != 'M':
                    self.margem_emprestimo = self.margem_emprestimo + texto[index]
                    last_index = index + 1
                else:
                    break

            for index in range((last_index + 22), 510):
                if texto[index] != 'B':
                    self.margem_cartao = self.margem_cartao + texto[index]
                    last_index = index + 1
                else:
                    break

            for index in range((last_index + 19), 540):
                if texto[index] != 'M':
                    self.base_calculo = self.base_calculo + texto[index]
                else:
                    break

            pdfFile.close()
            # os.remove(self.caminho_base+'/sites/inss/extrato-emprestimos-consignados.pdf')
            os.remove(
                "C:\\Users\\arthur.l\\Documents\\automacao-python\\sites\\inss\\extrato-emprestimos-consignados"
                ".pdf")
            return True
        except MargemError:
            return False

    def download_pdf(self):
        loc_btn_imprimir = '#app-imprimir'
        self.act.clicar_elemento(loc_btn_imprimir)
        self.aguardar_loagind_barra(False)
        sleep(1)

        baixou = os.path.exists(
            "C:\\Users\\arthur.l\\Documents\\automacao-python\\sites\\inss\\extrato-emprestimos"
            "-consignados.pdf")

        # baixou = os.path.exists(self.caminho_base+'/sites/inss/extrato-emprestimos-consignados.pdf')

        if not baixou:
            self.download_pdf()

    def logout(self):
        print("Realizando logout...")
        loc_menu = "#mini-btel"
        self.act.clicar_elemento(loc_menu)
        sleep(1)

        loc_icone = "#icone-filiado"
        self.act.clicar_elemento(loc_icone)
        sleep(1)

        loc_btn_sair = "#bt-limpa-dados-filiado"
        self.act.clicar_elemento(loc_btn_sair)
        sleep(1)

        loc_btn_emprestimo = '#area_lista > div > ul > li:nth-child(10) > a'
        self.act.clicar_elemento(loc_btn_emprestimo)
        sleep(1)

        try:
            while self.act.retornar_elemento('#area_lista > div > ul > li:nth-child(10) > a'):
                self.act.clicar_elemento(loc_btn_emprestimo)
                sleep(1)
        except TimeoutException:
            pass

    def aguardar_loagind_barra(self, selector):
        """
        Aguarda o carregamento das informações da matrícula e também o loading de download do arquivo PDF.

        :param selector: auxiliar que altera a mensagem de aguardando. Caso True, exibe a de 'Aguardando Loading' e caso
        contrário, exibe a de 'Aguardando Download'.
        """
        try:
            sleep(2)
            count = 0
            while self.act.quantidade_elemento("#app-animacao-carregamento") > 0:
                if selector:
                    print('Aguardando loading...')
                else:
                    print('Aguardando download...')

                count += 1
                sleep(2)

                if count > 30:
                    print("Muito tempo aguardando... reiniciando a fila...")
                    self.logout()
                    self.main()
        except TimeoutException:
            pass

    def aguardar_loading_body(self):
        """
        Aguarda o carregamento das matrículas disponíveis para aquele beneficiário.
        """
        try:
            sleep(2)
            while self.act.quantidade_elemento(
                    "#eaps-involucro > div > div.aposaut-aguarde_body") > 0:
                print('Aguardando loading...')
                sleep(2)
        except TimeoutException:
            pass

    def aguardar_loading_incial(self):
        try:
            sleep(2)
            while self.act.quantidade_elemento("#initload > div") > 0:
                print("Aguardando loagind....")
                sleep(2)
        except TimeoutException:
            pass

    def verificar_erros(self, perfil=''):
        try:
            if self.act.verificar_n_janelas(2):
                elemento = self.act.retornar_elemento(
                    "#loginData > div > div.painel-login.text-center > "
                    "div.painel-login-senha > div:nth-child(4) > "
                    "div.col-md-9.text-left.text-danger")
                erro = elemento.text

                try:
                    self.tratar_erros(erro, perfil)
                except NameError:
                    return

        except TimeoutException:
            pass

        try:
            elemento = self.act.retornar_elemento(
                "#eaps-involucro > div > section.app-mensagem > span.texto")
            erro = elemento.text

            try:
                self.tratar_erros(erro, perfil)
            except NameError:
                return

        except TimeoutException:
            pass

        try:
            elemento = self.act.retornar_elemento("#conteudo")
            erro = elemento.text

            try:
                self.tratar_erros(erro, perfil)
            except NameError:
                return
        except TimeoutException:
            pass

        try:
            elemento = self.act.retornar_elemento("#Content > div.container.main > div > div > h2")
            erro = elemento.text

            try:
                self.tratar_erros(erro, perfil)
            except NameError:
                return
        except TimeoutException:
            pass

    def tratar_erros(self, erro, perfil=''):

        erros_regex = [
            {
                "erro": r"Usuário e/ou senha inválidos.",
                "UsuarioErrado": True
            }, {
                "erro": r"Não foi possível encontrar uma conta para o CPF informado. Por favor, crie sua conta.",
                "CPFsemCadastro": True
            }, {
                "erro": r"Não foi possível acessar o Google reCAPTCHA",
                "reCAPTCHAError": True
            }, {
                "erro": r"Ocorreu um erro na tentativa de login.",
                "reCAPTCHAError": True
            }, {
                "erro": r"É necessário definir uma nova senha para o cadastro",
                "novaSenhaError": True
            }, {
                "erro": r"computador",
                "roboError": True
            }, {
                "erro": r"Autorização de uso de dados pessoais",
                "AutorizacaoError": True
            }, {
                "erro": r"Nenhuma informação encontrada para o documento informado \d{10}",
                "margemError": True
            }, {
                "erro": r"Ocorreu um erro na sua requisição. Tente novamente mais tarde.",
                "margemError": True
            }, {
                "erro": r"Recuperação de conta",
                "novaSenhaError": True
            }, {
                "erro": r"Ativação de conta",
                "novaSenhaError": True
            }
        ]

        for erro_regex in erros_regex:
            regex = re.compile(erro_regex['erro'])
            erro_encontrado = [erro for match in [
                regex.search(erro)] if match]

            if not erro_encontrado:
                continue

            if "UsuarioErrado" in erro_regex:
                print(erro_regex['erro'])
                self.act.fechar_janela(1)
                self.act.trocar_janela(0, 1)
                raise UsuarioErrado(message='Usuário e/ou senha inválidos!')
            elif "CPFsemCadastro" in erro_regex:
                print(erro_regex['erro'])
                self.act.fechar_janela(1)
                self.act.trocar_janela(0, 1)
                raise CPFsemCadastro(message='CPF sem cadastro no meu INSS!')
            elif "reCAPTCHAError" in erro_regex:
                print(erro_regex['erro'] + '. Tentando novamente...')
                self.act.fechar_janela(1)
                self.act.trocar_janela(0, 1)
                self.login(perfil)
            elif "novaSenhaError" in erro_regex:
                print('É necessário definir uma nova senha para o cadastro.')
                self.act.fechar_janela(1)
                self.act.trocar_janela(0, 1)
                raise RecuperacaoConta(
                    message='É necessário definir uma nova senha para o cadastro.')
            elif "roboError" in erro_regex:
                print(
                    'Captcha acusou o robô de ser um robô, esperando 2 minutos para enganar o Google e '
                    'inciar as atividades novamente...')
                sleep(120)
                self.login(perfil)
            elif "AutorizacaoError" in erro_regex:
                print('Autorizando uso de dados pessoais...')
                seletor_btn_autorizacao = "#confirmationFormId > div:nth-child(2) > input.btn.btn-primary.btn-large"
                self.act.clicar_elemento(seletor_btn_autorizacao)
            elif "margemError" in erro_regex:
                print(erro_regex['erro'])
                raise MargemError(message=erro_regex['erro'])

    def buscar_perfis(self):
        request_perfis = requests.get(
            f"https://uconecte.me/dev/index.php/api/v1/consultas/consultarMeuInss?perfil"
            f"=4,5&key={self.api_key}")

        if request_perfis.status_code != 200:
            input('INSS Error - Não foi possível buscar os contratos')

        perfis = request_perfis.json()['perfil']

        if len(perfis) == 0:
            print('Nenhum perfil para ser consultado, aguardando 5 minutos...')
            sleep(300)
            return []

        return perfis

    @staticmethod
    def finaliza_consulta_info_falha(perfil, mensagem):

        dados = {
            "retorno": 0,
            "key": "304b5b69eeb3921790c9e7ed9f4df504",
            "idContrato": perfil['idContrato'],
            "mensagem": mensagem + " Funcao 8",
        }

        request_dados_perfil = requests.post("https://uconecte.me/dev/index.php/api/v1/consultas"
                                             "/atualizaSituacaoContrato", data=dados)

        print(request_dados_perfil.text)
        if request_dados_perfil.status_code != 200:
            print(f"Status code: {request_dados_perfil.status_code}")
            input("Problema em reportar a falha da consulta para a API da Uconete!")

    def finaliza_consulta_info_sucesso(self, perfil):
        print("Finalizando consulta das informações...")
        nome = self.act.obter_texto("#eaps-involucro > div > div.app-subtitle.fim-header")
        self.beneficio = tipo_beneficio(
            self.act.obter_texto("#eaps-involucro > div > section.area-conteudo > div > div > "
                                 "section.eco-box-beneficio > div.eco-box-benef-campos > "
                                 "div.eco-campo.eco-box-benef-situacao > span.eco-fonte-escura > span"))
        dados = {
            "retorno": 1,
            "mensagem": "--Consulta realizada com sucesso! Funcao 8",
            "nomeCompleto": nome[33:], # ok
            "cpf": perfil['cpf'],
            "creditoTotal": formatar_valor(self.base_calculo, False), # ok
            "valorEmprestimos": self.soma_parcelas(), #ok
            "margemDisponivel": formatar_valor(self.margem_emprestimo, False), # ok
            "margemDisponivelCartao": formatar_valor(self.margem_cartao, False), # ok
            "arrayParcelasRefin": self.arrayParcelasRefin, # ok
            "especieBeneficio": self.beneficio, # ok
            "numeroEmprestimos": len(self.arrayConsultaRefin), # ok
            "arrayConsultaRefin": self.arrayConsultaRefin, # ok
            "banco": self.dados_banco['banco'], # ok
            "agencia": self.dados_banco['agencia'], #ok
            "conta": self.dados_banco['conta'], #ok
            "digitoConta": self.dados_banco['digitoConta'], #ok
            "tipoConta": self.dados_banco['tipoConta'] # ok
        }

        dados_json = json.dumps(dados, indent=4)

        dados_post = {
            "consultaBeneficio": dados_json,
            "robo": True,
            "idContrato": perfil['idContrato'],
        }

        request_dados_perfil = requests.post(
            "https://uconecte.me/dev/index.php/api/v1/consultas/inss", data=dados_post)
        print(request_dados_perfil.text)
        if request_dados_perfil.status_code != 201:
            print(f"Status code: {request_dados_perfil.status_code}")
            input("Problema em reportar a consulta para a API da Uconecte")

        self.arrayParcelasRefin = []
        self.arrayConsultaRefin = []

    @staticmethod
    def atualiza_perfil_web_admin(perfil, margem, retorno, observacao):
        dados = {
            "retorno": retorno,
            "codigoCon": perfil['codigoContrato'],
            "margemDisponivel": formatar_valor(margem, False),
            "observacao": observacao
        }

        request_dados_perfil = requests.post(
            "https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza"
            "-margem/portal-meu-inss/?key=f689f1e12a0399fba803cb2365fc362f",
            data=dados)

        if request_dados_perfil.status_code != 200:
            print(f"Status code: {request_dados_perfil.status_code}")
            input(
                "Problema ao atualizar a margem do perfil no webadmin, favor verificar o que ocorreu!")

    def soma_parcelas(self):
        somatorio = 0

        for parcela in self.arrayParcelasRefin:
            somatorio = somatorio + float(parcela)

        return str(round(somatorio, 2))

    def verifica_horario_comercial(self):
        data_hora = datetime.now()
        if data_hora.hour > 20:
            print('Fora do horário comercial... Inciando o processo para próxima manhã (7:00)...')
            self.driver.close()
            countdown(36000, 3600, 'Aguardando...')
            self.__init__()
            self.main()

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print(f"\nTempo entre atualizações: {time_between_updates}")
        print(f"Timer: {self.timer} segundos")

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            print(f"Esperando {wait_time} segundos antes de recomeçar a fila!")

            if wait_time > 0:
                sleep(wait_time)

        self.ultima_atualizacao = datetime.now()
        self.uconecte.atualizar_status_robo(self.id_robo)


class UsuarioErrado(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class RecuperacaoConta(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class MargemError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class CPFsemCadastro(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class BloqueadoError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class RepresentanteError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


def criar_pasta_usuario_chrome(user_path):
    import os
    try:
        os.makedirs(user_path)
    except OSError:
        print("Pasta o usuário chrome não precisou ser criada, pois já existe.")


if __name__ == '__main__':
    run = Inss()
    run.main()
