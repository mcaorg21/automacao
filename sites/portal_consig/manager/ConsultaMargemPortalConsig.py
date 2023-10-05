from sites.baseRobos.manager import Manager
from sites.portal_consig.data.portalConsig_dados import PortalConsigData
from sites.portal_consig.auto.FormAcessoPortal import FormAcessoPortal
from sites.portal_consig.auto.FormLogin import FormLogin, CaptchaIncorretoException
from sites.portal_consig.auto.FormDadosBuscaMargem import (
    FormDadosBuscaMargem, FalhaConsultaException
)
from sites.portal_consig.auto.TabelaConsultaMargem import (
    TabelaConsultaMargem
)
from sites.baseRobos.core.helpers import *

from datetime import date
from selenium.common.exceptions import TimeoutException
from sites.core.selenium_helper import SeleniumHelper
import traceback as tb
from typing import List

import pdb,pickle,json,requests
import PATHS

from time import sleep


class PortalConsigMan(Manager):
    main_url = "https://www.portaldoconsignado.com.br/"
    main_url_logado = "https://www.portaldoconsignado.com.br/selecaoPerfil?551"
    id_robo = 15

    def __init__(self):
        super().__init__()
        self.chrome_user = self.PATHS.chrome_user("PortalConsig")
        self.criar_pasta_usuario_chrome(self.chrome_user)

        self.set_options(
            '--ignore-ssl-errors', '--no-sandbox',
            'log-level=3', self.chrome_driver)
        self.data = PortalConsigData()

        self.cpf_login = '05906929681'
        #self.cpf_login = '06445557694'
        self.senha_admin = 'Banco@21'
        #self.senha_admin = 'Banco@1609'
        self.login_status = False

        self.caminho_base = PATHS.project_path()
        self.cookies_path = self.caminho_base+"\\portal_consig\\cookies\\" + "usuario_portal_consig.pkl"
        self.cookies_path_json = self.caminho_base+"\\portal_consig\\cookies\\" + "usuario_portal_consig.json"

    @staticmethod
    def main():
        portal_sp = PortalConsigMan()
        portal_sp.init_chrome_driver()
        while True:
            portal_sp.executar_busca_margem()


    def executar_busca_margem(self, solicitacao: dict=None):
        # Classe com métodos e atributos para gerenciar o estado da sessão.
        login: FormLogin = FormLogin(
                driver=self.chrome_driver,
                senha=self.senha_admin,
                cpf_login=self.cpf_login
        )

        acesso: FormAcessoPortal = FormAcessoPortal(driver=self.chrome_driver)

        # Classe com métodos e atributos para gerenciar a
        # troca de perfis segundo o Estado a ser consultado
        if(login.status_login == False):
                self.chrome_driver.get(self.main_url)
                # Método que implementa FormLogin
                self.realizar_login(login)  
                if(self.cpf_login != '06445557694'): 
                    self.acessar_portal_consulta(acesso, 'sp')    
                    self.salva_cookies_escreve_json() 
                    self.driver.execute_script("window.history.go(-1)")   

        else:
            range_back = login.status_login_pagina
            if(self.cpf_login == '06445557694'):
                range_back = 0
            for i in range(range_back):
                self.driver.execute_script("window.history.go(-1)")
                sleep(5)

            if(range_back == 0):
                self.driver.refresh()

        conta = 1

        array_convenios = ['prefeitura_sp','sp','mt']
        if(self.cpf_login == '06445557694'):
            array_convenios = ['sp']

        for idx,convenio in enumerate(array_convenios):

            print('Iniciando consulta convênio de: ' + convenio.upper())

            solicitacoes: List[dict] = []

            # if solicitacao is None:
            try:
                solicitacoes: list = self.data.req_solicitacoes(convenio)
            except:
                solicitacoes = None
            # else:
            #     solicitacoes.append(solicitacao)  

            if solicitacoes:
                for num, solicitacao in enumerate(solicitacoes):
                    self.data.api_iniciar_log_robo(
                        idRobo=self.id_robo,
                        idSolicitacao=solicitacao['idSolicitacao']
                    )
                    try:

                        # Método que implementa FormAcessoPortal
                        if(self.cpf_login != '06445557694'):
                            #self.driver.execute_script("window.history.go(-1)")
                            self.acessar_portal_consulta(acesso, convenio)

                        # Classe responsável por armazenar e utilizar dados do cliente
                        # para acessar as tabelas que contém os dados da margem
                        busca: FormDadosBuscaMargem = FormDadosBuscaMargem(
                            driver=self.chrome_driver, **solicitacao
                        )

                        # Classe com atributos que armazenam as informações da tabela
                        # de dados do servidor e métodos para extrair infos da tabela.
                        tabela: TabelaConsultaMargem = TabelaConsultaMargem(
                            driver=self.chrome_driver, solicitacao=solicitacao
                        )

                        # salva cookies para adm
                        self.salva_cookies_escreve_json()

                        try:
                            # Implementa as classes FormDadosBuscaMargem e TabelaConsultaMargem
                            self.extrair_dados_servidor(busca, tabela)
                        except FalhaConsultaException as e:
                            self.data.api_registrar_log_robo(
                                log=e.message,
                                status=2
                            )
                            self.__atualizar_erro_consulta(solicitacao, e.message)
                            continue

                        tabela.atualizar_margem_solicitacao()
                        print(solicitacao['margem'])
                        
                        self.__atualizar_bem_sucedido(solicitacao)
                        self.data.api_registrar_log_robo(
                            log=f"Margem consultada com sucesso: {solicitacao['margem']}",
                            status=2)
                    except Exception as e:
                        tb.print_exc()
                        self.data.api_registrar_log_robo(
                            log=f"ERRO: {e}",
                            status=0
                        )
            else:
                conta += 1
                print('Não há solicitações para o convenio' + convenio.upper() + ' no momento.')
            
        if(conta >= 3):
            self.acessar_portal_consulta(acesso, 'sp')
            print('Aguardando 60 segundos para reiniciar busca...')
            self.driver.execute_script("window.history.go(-1)")
            sleep(60)
            
                

    def realizar_login(self, form: FormLogin):
        if form.status_login:
            return False

        form.clicar_aba_admnistrativo()
        form.preencher_cpf()
        form.preencher_senha()
        form.resolver_preencher_captcha()
        try:
            form.verificar_erro_captcha()
        except CaptchaIncorretoException:
            return self.realizar_login(form)

        return True

    def acessar_portal_consulta(self, form: FormAcessoPortal, convenio: str):
        try:
            form.convenio = convenio
            form.selecionar_convenio_consulta()
            form.clicar_botao_acessar()
        except TimeoutException:
            print("Usuário atual consulta apenas servidores de SP.")

    def extrair_dados_servidor(self, form: FormDadosBuscaMargem, tabela: TabelaConsultaMargem):

        if tabela.quantidade_provimentos <= 1:
            form.expandir_menu_consulta_margem()
            form.clicar_link_consulta_margem()
            form.preencher_cpf_consulta_margem()
            form.confirmar_consulta_margem()
            form.verificar_retorno_incial_consulta()  # raises FalhaConsultaException
            form.verificar_erro_consulta()  # raises FalhaConsultaException

            # if tabela.quantidade_provimentos > 1:
            #     print(tabela.quantidade_provimentos)
            #     form.provimento_especifico = True
            #     print("Cliente possui mais de um provimento.")

            #     return self.extrair_dados_servidor(form, tabela)

            tabela.extrair_margem_consignavel()
            tabela.extrair_margem_cartao()
        else:
            import pdb
            pdb.set_trace()
            form.expandir_menu_consigs_facultativas()
            form.clicar_link_reserva_averbacao()
            form.selecionar_orgao_consulta_averbacao()
            form.selecionar_tipo_operacao_consulta_averbacao()
            form.preencher_cpf_consulta_averbacao()
            form.preencher_matricula_consulta_averbacao()
            form.clicar_continuar_consulta_averbacao()
            form.verificar_erro_consulta()  # raises FalhaConsultaException

            tabela.extrair_margem_averbacao()

    def __atualizar_bem_sucedido(self, solicitacao):
        print("Calculando financiamento.")
        solicitacao['retorno'] = 1
        solicitacao['mensagem'] = '_localizado'

        atualizar_idade_solicitacao(solicitacao)

        self.data.calculo_fin_refin_uconecte(solicitacao, True)

    def __atualizar_erro_consulta(self, solicitacao, erro):
        print("Atualizando erro")

        status_consulta = self.data.verificar_status(erro)

        solicitacao['retorno'] = status_consulta['retorno']
        solicitacao['mensagem'] = status_consulta['mensagem']
        solicitacao['margem'] = ''

        atualizar_idade_solicitacao(solicitacao)

        self.data.calculo_fin_refin_uconecte(solicitacao, True)

    def salva_cookies_escreve_json(self):
        self.selenium_helper = SeleniumHelper(self.chrome_driver)
        self.selenium_helper.save_cookies(self.cookies_path)

        with open(self.cookies_path, 'rb') as fpkl, open(self.cookies_path_json, 'w') as fjson:
            data = pickle.load(fpkl)
            json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)
            
            
        file = open(self.cookies_path_json)
        cookies = json.load(file)
        dados = {
                    'id_robo' : self.id_robo,
                    'cookies_json': json.dumps(cookies)
                }

        req = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/promobank/?key=f689f1e12a0399fba803cb2365fc362f", data=dados)
        if(req.status_code == 200):
            print('Cookies salvos com sucesso!')

def atualizar_idade_solicitacao(solicitacao):
    anoNasc, mesNasc, diaNasc = solicitacao['dataNascimento'].split('-')
    anoAt, mesAt, diaAt = str(date.today()).split('-')
    idade = int(anoAt) - int(anoNasc)
    if int(mesAt) == int(mesNasc) and diaAt > diaNasc:
        idade -= 1
    elif int(mesAt) > int(mesNasc):
        idade -= 1

    solicitacao['idadePessoa'] = idade


if __name__ == "__main__":

    while True:
        PortalConsigMan.main()


