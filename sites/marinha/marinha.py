import os
import requests

from time import sleep
from datetime import datetime
from sites.core.uconecte import Uconecte
from sites.core.captcha import TwoCaptcha
from sites.core.selenium_helper import SeleniumHelper
from sites.core.selenium_actions import SeleniumActions

from sites.baseRobos.data_handler import DataHandler
from sites.baseRobos.core.helpers import definir_nome_robo


class Marinha:
    """
    # Retorno = 1  >>>> sucesso
    # Retorno = 2  >>>> erro conhecido
    # Retorno = 99 >>>> erro desconhecido
    """
    id_robo = 16

    def __init__(self, login, senha, driver):
        self.retorno = 0
        self.senha = senha
        self.login = login
        self.driver = driver

        self.uconecte = Uconecte()
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.key_api_consulta = '304b5b69eeb3921790c9e7ed9f4df504'

        self.selenium_helper = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver, time_out=10)
        self.log = DataHandler()

    def login_sistema(self):
        try:
            print('\nRealizando login...')

            # Digitar login

            loc_login = """input[name="username"]"""
            self.act.enviar_texto(loc_login, self.login)

            # Aba para digitar senha e resolver o captcha

            loc_botao = """input[name="Entrar"]"""
            self.act.clicar_elemento(loc_botao)

            # Digitar senha

            loc_senha = """input[name="senha"]"""
            self.act.enviar_texto(loc_senha, self.senha)

            # Resolver Captcha

            loc_captcha_img = """img[name="captcha_img"]"""
            loc_campo_catpcha = 'input#captcha'
            id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)
            self.act.enviar_texto(loc_campo_catpcha, res_captcha)
            self.captcha.mudar_status_captcha(id_captcha, '1')

            self.act.clicar_elemento(loc_botao)

            # Verificação da captcha

            loc_erro = 'font.erro'

            try:
                self.act.retornar_elemento(loc_erro)
                print('\nErro ao resolver captcha...')
                self.login_sistema()  # Tenta fazer o login novamente

            except Exception:
                print('\nLogin realizado com sucesso!')

        except Exception as e:
            print(e)

    def ir_tela_consulta(self):

        frame_botao_operacional = "topFrame"
        loc_botao_operacional = 'a#menu-OPERACIONAL'  # botao do menu popup
        self.act.trocar_frame_referencia(frame_botao_operacional)
        self.act.hover_menu_dropdown(loc_botao_operacional)

        frame_consulta_margem = "mainFrame"
        loc_botao_consulta_margem = "div#HM_Item1_1"
        self.act.trocar_frame_referencia(frame_consulta_margem)
        self.act.clicar_elemento(loc_botao_consulta_margem)

    def pega_margem(self, cpf, matricula, codigo, id_solicitacao):
        """
        Função responsável por utilizar os dados do cliente para realizar a
        busca de margem no portal da marinha. Retorna o valor da margem, caso
        encontrado e uma mensagem que tudo ocorreu bem. Caso não ache a margem,
        retorna uma mensagem do erro e:
                                        - 2 para reprovar a proposta
                                        - 99 para um erro desconhecido

        :param cpf: CPF do cliente (str)
        :param matricula: Matricula do cliente (str)
        :param codigo: Código único do cliente (str)
        :param id_solicitacao: ID da solicitação de emprestimo

        :return mensagem: mensagem de erro ou sucesso (str)
        :return margem: margem do cliente (str)
        :return self.retorno: código de sucesso ou erro (int)
        """
        sleep(0.5)
        try:
            loc_matricula = "input#RSE_MATRICULA"
            self.act.press_backspace(loc_matricula)
            self.act.enviar_texto(loc_matricula, matricula)
            sleep(0.5)

            loc_cpf_cliente = "input#SER_CPF"
            self.act.press_backspace(loc_cpf_cliente)
            self.act.enviar_texto(loc_cpf_cliente, cpf)
            sleep(0.5)

            loc_codigo = "input#senha"
            self.act.press_backspace(loc_codigo)
            self.act.enviar_texto(loc_codigo, codigo)
            sleep(0.5)

            loc_botao_pesquisa = "a#btnEnvia"
            self.act.clicar_elemento(loc_botao_pesquisa)
            sleep(0.5)

        except Exception:
            self.pega_margem(cpf, matricula, codigo, id_solicitacao)

        loc_erro = 'font.erro'

        try:
            self.act.retornar_elemento(loc_erro)
            message = self.act.obter_texto(loc_erro)
            if message == 'Código único do Militar/Pensionista não cadastrado.' or message == 'O código único do Militar/Pensionista não confere.':
                mensagem = 'Código único do Militar/Pensionista inválido!'
                print(f'Erro ao consultar margem da socilitacao {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)  # dorme para não ir muito rápido e bugar a plataforma de consulta, isso se repete...
                # (...) nos demais campos pelo mesmo motivo. Valor de 0.3 arbritário, definido por testes.
                self.retorno = 2
            elif 'Nenhum' in message:
                mensagem = 'Matrícula e/ou CPF não possuem registro no eConsig!'
                print(f'Erro ao consultar margem da solicitação {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 2
            else:
                mensagem = 'Um erro inesperado aconteceu'
                print(f'Erro ao consultar margem da solicitação {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 99

            return mensagem, self.retorno
        except Exception:
            pass

        try:
            if not self.act.verificar_existencia_alerta():
                raise Exception("Alerta de erro não foi aberto.")
            message = self.act.obter_texto_alerta()
            self.act.manusear_alerta()
            sleep(0.3)

            if  r'Informe pelo menos 8 dígitos.' in mensagem:
                mensagem = 'A matrícula informada está incorreta!'
                print(f'Erro ao consultar margem da solicitacao {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 2
            elif message == 'Número de CPF inválido.':
                mensagem = 'O CPF informado é inválido!'
                print(f'Erro ao consultar margem da solicitacao {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 2
            elif message == 'Por favor, verifique o conteúdo dos campos grafados em vermelho.':
                mensagem = 'CPF e/ou matrícula informados estão incompletos'
                print(f'Erro ao consultar margem da solicitacao {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 2
            else:
                mensagem = 'Um erro inesperado aconteceu'
                print(f'Erro ao consultar margem da solicitação {id_solicitacao} >>>> {mensagem}')
                sleep(0.3)
                self.retorno = 99

            return mensagem, self.retorno
        except Exception:
            sleep(0.5)

            print('\nPesquisa feita com sucesso!')
            mensagem = 'Ok!'

            loc_margem = 'td.CEDmeio'
            elementos = self.act.retornar_elementos(loc_margem)
            margem = self.trata_margem(elementos[11].text)

            return mensagem, margem

    def logout_sistema(self):

        try:
            frame_botao_operacional = "topFrame"
            loc_botao_sistema = "a#menu-SISTEMA"
            self.act.trocar_frame_referencia(frame_botao_operacional)
            self.act.hover_menu_dropdown(loc_botao_sistema)

            frame_consulta_margem = "mainFrame"
            loc_botao_sair_sistema = "div#HM_Item2_1"
            self.act.trocar_frame_referencia(frame_consulta_margem)
            self.act.clicar_elemento(loc_botao_sair_sistema)

            loc_botao_confirma = 'a[href="#no-back"]'
            self.act.clicar_elemento(loc_botao_confirma)

            print('\nDeslogado do sistema com sucesso!')
        except Exception as e:
            print(e)

    def processar_filas_uconecte(self):
        """
        Retira os dados dos clientes da lista de solicitações (solicitacoes - list) e os utiliza
        para gerenciar a consulta de margem no portal da marinha e o envio dos dados para
        o método de solicitação de financiamento (solicitacao_financiamento).
        """
        solicitacoes = self.__busca_solitacoes()

        for solicitacao in solicitacoes:

            print(f"\nTrabalhando na solicitação {solicitacao['idSolicitacao']}...")
            self.log.api_iniciar_log_robo(
                idRobo=self.id_robo, idSolicitacao=solicitacao['idSolicitacao']
            )

            try:
                definir_nome_robo('Consulta Margem Marinha')
                cpf_consulta = solicitacao['cpf']
                matricula = solicitacao['matricula']
                codigo = solicitacao['codigo']
                msg, margem_disponivel = self.pega_margem(cpf_consulta, matricula, codigo, solicitacao['idSolicitacao'])

                if self.retorno == 2:  # reprova
                    self.__solicitacao_financiamento(solicitacao, margem_disponivel, self.retorno, msg)
                    self.log.api_registrar_log_robo(
                        log=msg, status=2
                    )
                elif self.retorno == 99:  # erro desconhecido
                    self.__solicitacao_financiamento(solicitacao, margem_disponivel, self.retorno, msg)
                    self.log.api_registrar_log_robo(
                        log=msg, status=2
                    )
                else:  # sucesso
                    self.retorno = 1
                    self.__solicitacao_financiamento(solicitacao, margem_disponivel, self.retorno, msg)
                    self.log.api_registrar_log_robo(
                        log=msg, status=2
                    )
            except TimeoutError:
                print('Cliente não encontrado!')
                pass
            except Exception as e:
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {str(e)}", status=0
                )
                raise Exception(str(e))


    def confirmar_leitura(self):
        frame_consulta_margem = "mainFrame"
        self.act.trocar_frame_referencia(frame_consulta_margem)
        if self.selenium_helper.buscar_quantidade_elemento("#checkboxConfirmarLeitura") > 0:
            self.driver.execute_script("""document.querySelector("#checkboxConfirmarLeitura").checked=true""")
            self.act.clicar_elemento("#main > form > table > tbody > tr:nth-child(2) > td > table > tbody > "
                                     "tr:nth-child(4) > td > a")

    def __busca_solitacoes(self):
        """
        Realiza uma 'request' à API da uConecte requisitando os
        dados das solicitações de financiamento dos clientes à plataforma.
        :return: (list) uma lista de dicts
        """
        ulr_api = 'https://uconecte.me/api/v1/Consultas/consultarMargemMarinha'

        parametros = {'key': self.key_api_consulta}

        requests_solicitacoes = requests.get(
            ulr_api,
            params=parametros
        )

        if requests_solicitacoes.status_code != 200:
            print(requests_solicitacoes)
            input('Não foi possivel buscar as solicitações...')

        resultado_consulta = requests_solicitacoes.json()['consulta']
        return resultado_consulta

    def __solicitacao_financiamento(self, solicitacao, margem, retorno, msg):
        """
        Adiciona a margem (int), idadePessoa (int), fk_Cidade (None) e
        fk_Estado (None) na solicitacao (dict) e solicita o calculo do financiamento
        à API da uConecte

        :param solicitacao: solicitacao a ser alterada
        :param margem: valor da margem a ser inserida
        :param retorno: código do sucesso (1) ou erro (99 - inesperado // 2 - conhecido)
        :param msg: mensagem do erro ou de sucesso
        """

        solicitacao['margem'] = margem
        solicitacao['idadePessoa'] = self.calcula_idade(solicitacao['dataNascimento'])
        solicitacao['fk_idCidade'] = None
        solicitacao['fk_idEstado'] = None
        solicitacao['retorno'] = retorno
        solicitacao['mensagem'] = msg

        self.uconecte.calcular_financiamento(solicitacao, status_solicit=True)

    @staticmethod
    def calcula_idade(data):
        """
        Calcula a idade para o seguinte formato de data
        de nascimento: ANO-MÊS-DIA

        :param data: data no formato XXXX-XX-XX
        :return: idade calculada (int)
        """
        ano = datetime.now()
        ano_nascimento = int(data[0:4])

        if ano.month <= int(data[5:7]) and ano.day <= int(data[8:]):
            idade = ano.year - ano_nascimento - 1
        else:
            idade = ano.year - ano_nascimento

        return idade

    @staticmethod
    def trata_margem(dado):
        """
        Pega o dado da margem (R$ ZZZ,ZZ) e retorna somente seu valor
        númerico, substituindo a ',' por '.'

        :param dado: dado bruto retirado direto do site (str)

        :return: valor numerico da margem (float)
        """
        valor = dado[3:].replace('.', '').replace(',', '.')
        return float(valor)
