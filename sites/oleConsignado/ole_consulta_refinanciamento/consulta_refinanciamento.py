"""
# TODO Se for adicionar mais algum estado para consultar, faz-se necessário atualizar o
#   refinanciamento.json com os códigos do orgão tanto da uConecte quanto da plataforma do
#   Olé, seguindo o pradão já estabelecido.
"""

#PARA RODAR NO WINDOWS
# import sys
# sys.path.append('../../../')

import random
import re
import time
import requests,pdb,shutil
from typing import List

from selenium.webdriver import Chrome
from selenium import webdriver
from tinydb import TinyDB, Query
from selenium.common.exceptions import NoSuchElementException,JavascriptException
from sites.core.helpers import formatar_porcentagem, formatar_moeda
from sites.oleConsignado.gerar_refin.ole_consignado import OleConsignado, ErrorOleException
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.data_helpers import similaridade
from sites.core.selenium_helper import SeleniumHelper
import PATHS
from sites.baseRobos.data_handler import DataHandler
from sites.oleConsignado.ole_consulta_refinanciamento.OleConsultaRefinDados import OleConsultaRefinDados
from sites.oleConsignado.config.paths_ole import PATH_ID_REFIN,PATH_COOKIES_JSON,PATH_ID_4_2
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.oleConsignado.robos.auxiliares import ErroSessaoOle
from sites.oleConsignado.libs.FormLogin import FormLogin
from dados.database.LoginDBDataSource import LoginDBDataSource

from selenium.webdriver.common.by import By

from sites.oleConsignado.gerar_refin.ole_consignado import OleConsignado

HORARIO_COMERCIAL = 8, 20


class ConsultaRefinanciamento(OleConsignado):
    id_fila_refin = 20
    url_login = "ola.oleconsignado.com.br/usuario/index?returnurl"

    def __init__(self, driver: Chrome):
        super().__init__(driver)
        self.base_path = PATHS.project_path()
        self.path_db = self.base_path + "/oleConsignado/database/refinanciamento.json"
        self.solicitacao = None
        self.refinanciamentos = None
        self.driver: Chrome = driver
        #self.driver = webdriver.Chrome()
        self.selenium = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver)
        self.db_info = TinyDB(self.path_db).table("identificador_orgao")
        self.auth: LoginDBDataSource = LoginDBDataSource(self.id_fila_refin, "alexandre18733")
        self.cookies_path = PATH_ID_4_2
        self.cookies_json_path = PATH_COOKIES_JSON
        self.selenium_helper = SeleniumHelper(self.driver)
        self.log = DataHandler()
        self.dados: OleConsultaRefinDados = OleConsultaRefinDados()
        self.tipo_fila = "refinanciamento"

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = ConsultaRefinanciamento(driver)
        try:
            run.consultar_refins_e_potenciais()

        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        except ErroSessaoOle:
            self.aguardar_cookies()

        return run


    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def aguardar_cookies(self):
        cnt = 0
        while self.driver.current_url.find("Home") == -1 and cnt < 50:
            try:
                self.selenium_helper.load_cookies(self.cookies_path, delete=True)
            except Exception as e:
                print(e)
            print("Aguardando cookies do Olé Refin...")
            self.driver.refresh()
            time.sleep(20)
            cnt += 1

        self.uconecte.atualizar_status_robo(self.id_robo)

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_refins_e_potenciais(self):
        # self.driver.get('https://ola.oleconsignado.com.br/Identificacao')
        # self.selenium_helper.load_cookies(self.cookies_path, False)
        self.driver.get('https://ola.oleconsignado.com.br/Identificacao')
        # self.driver.refresh()
        #self.driver.delete_all_cookies()

        # try:
        #     self.selenium_helper.load_cookies_json('https://ola.oleconsignado.com.br/Identificacao', 
        #                                         'https://ola.oleconsignado.com.br/Identificacao', 
        #                                         self.cookies_path_json, True, False)
        # except:
        #     pass

        # self.auth.load_dados_login()

        # if FormLogin.realizar_login(self.driver, self.auth.login(), self.auth.senha()):
        #     self.selenium_helper.save_cookies(self.cookies_path)
        #     self.selenium_helper.save_cookies_json(self.cookies_path, self.cookies_json_path)

        self.driver.get('https://ola.oleconsignado.com.br/Home')

        self.aguardar_cookies()


        print('Gerando contratos...')
        OleConsignado.iniciar_horario_comercial(self.driver)

        print("Consultando refinanciamentos...")
        self.executar_consulta_refinanciamentos(fila='refinanciamento')
        self.executar_consulta_refinanciamentos(fila='potenciais')


    def executar_consulta_refinanciamentos(self, fila="refinanciamento"):
        pular_consulta = 0
        self.tipo_fila = fila
        # try:
        #     self.selenium_helper.load_cookies(self.cookies_path, delete=True)
        #     self.driver.refresh()
        #     time.sleep(3)
        # except Exception as e:
        #     self.selenium_helper.save_cookies(self.cookies_path)
        #     print(e)

        
        # if FormLogin.realizar_login(self.driver, self.auth.login, self.auth.senha):
        #     SeleniumHelper(self.driver).save_cookies(self.cookies_path)

        # time.sleep(2)
        # self.selenium_helper.save_cookies(self.cookies_path)
        # time.sleep(2)

        self.selenium_helper.save_cookies(self.cookies_path)

        solicitacoes: List[dict] = []
        if fila == "refinanciamento":
            solicitacoes = self.buscar_solicitacoes_refinanciamento()
        elif fila == "potenciais":
            solicitacoes = self.uconecte.buscar_pessoas_potenciais()

        for cnt, self.solicitacao in enumerate(solicitacoes, 1):
            print(f"[{cnt}]Fila Consulta ", fila.title())
            self.solicitacao['matricula'] = str(self.solicitacao['matricula'])
            # if self.solicitacao['sigla'] == "RJ":
            #     continue
            if fila == "refinanciamento":
                self.log.api_iniciar_log_robo(
                    idSolicitacao=self.solicitacao['idSolicitacao'],
                    idRobo=self.id_fila_refin)
            # try:
            #     self.selenium_helper.load_cookies(self.cookies_path, delete=True)
            #     self.driver.refresh()
            #     time.sleep(3)
            # except Exception as e:
            #     continue

            print(f"Trabalhando na solicitação: {self.solicitacao}")

            self.refinanciamentos = []

            try:
                if not self.consultar_refinanciamento():
                    print(f"Finalizando consulta solicitação: {self.solicitacao}")
                    if (self.driver.current_url.find("Simulacao") == -1 and
                            (self.driver.current_url.find("unauthorized") > -1 or
                             self.driver.current_url.find("SessionUnauthorized") > -1)):
                        print('Reiniciando a consulta')
                        # self.log.api_registrar_log_robo(
                        #     log="SessionUnauthorized", status=0)
                        self.executar_consulta_refinanciamentos(fila=self.tipo_fila)
                    else:
                        # ATUALIZAÇÃO DE CONSULTA REALIZADA COM SUCESSO
                        self.dados.atualizar_dados_consulta(self.solicitacao, self.refinanciamentos)
                        self.log.api_registrar_log_robo(
                            log=f"Consulta realizada com sucesso. Refinanciamentos: {self.refinanciamentos}", status=2)
                        continue
                else:
                    print("Calculando Refinanciamentos encontrados!")

            except NotFoundResultException as e:
                print(f'Não possui contratos. Mensagem Sistema: {e.message}')
                if self.driver.current_url.find("Simulacao") == -1 and self.driver.current_url.find("Identificacao") != 33: 
                    print('trace para login')
                    self.log.api_registrar_log_robo(
                        log="SessionUnauthorized", status=0)
                    continue

                self.dados.atualizar_impossibilidade_consulta(self.solicitacao, e.message)
                self.log.api_registrar_log_robo(log=e.message, status=2)

            except RestricaoException as e:
                print("Restrição:", e.message)
                self.dados.atualizar_impossibilidade_consulta(
                    self.solicitacao, e.message, restricao=True)

            except ErrorOleException as e:
                print('Erro inesperado reiniciando consulta...')
                self.log.api_registrar_log_robo(
                    log=f'Erro inesperado reiniciando consulta. {e.message}', status=0)
                continue
                print('Pulando consulta...')
                pular_consulta = 1

            except PularCheckboxException as e:
                print('Erro na procura do orgao...')
                self.log.api_registrar_log_robo(
                    log=f'Erro na procura do orgao. {e.message}', status=0)
                continue

            except RefinanciamentosInexistente as e:
                print('Refinanciamento inexistentes...')
                self.dados.atualizar_dados_consulta(self.solicitacao, self.refinanciamentos)
                self.log.api_registrar_log_robo(
                            log=f"Consulta realizada com sucesso. Refinanciamentos inexistente.", status=2)
                continue

            if self.driver.current_url.find("Simulacao") == -1 and self.driver.current_url.find("Identificacao") != 33:
                print('trace para login 2')
                
                if(self.driver.current_url.find("Home") == 33):
                    continue
                if(self.driver.current_url.find("SessionUnauthorizedReCaptcha")>0):
                    continue

            else:
                print(f"Finalizando consulta solicitação: {self.solicitacao}")
                if(pular_consulta == 0):
                    self.dados.atualizar_dados_consulta(self.solicitacao, self.refinanciamentos)

        if self.driver.current_url.find("Simulacao") == -1 and (self.driver.current_url.find("unauthorized") > -1 or self.driver.current_url.find("SessionUnauthorized") > -1) :
            print('Deslogado... Logando...')
            try:
                self.selenium_helper.load_cookies(self.cookies_path)
            except Exception as e:
                print(e)
            time.sleep(1)
            self.driver.get('https://ola.oleconsignado.com.br/Identificacao')
            #self.driver.get('https://ola.oleconsignado.com.br/Simulacao/Index/?&24809594653&1378868568&011398')
            # if(self.driver.current_url.find("SessionUnauthorized") > -1 or self.driver.current_url.find("unauthorized") > -1):

        self.log.api_registrar_log_robo(
                            log=f"Consulta realizada com sucesso. Refinanciamentos: {self.refinanciamentos}", status=2)

    def buscar_solicitacoes_refinanciamento(self):
        request_solicitacoes = requests.get(
            f"https://uconecte.me/api/v1/solicitacoes/refinanciamento?key={self.api_key}&banco={self.id_banco}")

        if request_solicitacoes.status_code != 200:
            print(request_solicitacoes.text)
            input("Não foi possível buscar as solicitações. Verifique o que aconteceu!")

        solicitacoes = request_solicitacoes.json()['solicitacoes']

        if len(solicitacoes) == 0:
            print('Nenhum refinanciamento para consultar!')
            #self.driver.quit()
            return []

        return solicitacoes

    def aba_identificacao_refin(self):
        self.driver.get('https://ola.oleconsignado.com.br/Simulacao/Index/')
        
        #ALTERNATIVA PARA O SISTEMA
        #self.act.hover_e_clique('//*[@id="nav"]/div/ul/li[1]/a/span',By.XPATH)
        #time.sleep(1)
        #self.act.hover_e_clique('//*[@id="nav"]/div/ul/li[1]/ul/li/a', By.XPATH)

        # if self.solicitacao['fk_idPerfil'] in ["4","5"]:
        #     #inss
        #     #https://ola.oleconsignado.com.br/Simulacao/Index/?&cpf&matricula&011398
        #     #siape sistema veio sem o 0
        #     #https://ola.oleconsignado.com.br/Simulacao/Index/?&04456588780&01776135&013579
            
        #     if(len(self.solicitacao['matricula'])<10):
        #         self.solicitacao['matricula'] = self.prepara_matricula_zeros_frente(self.solicitacao['matricula'],10)
        #     self.driver.get('https://ola.oleconsignado.com.br/Simulacao/Index/?&%s&%s&011398' % (self.solicitacao['cpf'],self.solicitacao['matricula']))
        #     #time.sleep(1)
        #     if(self.driver.current_url.find("error") != -1):
        #         print('Não existem refinanciamentos disponíveis!!\n')
        #         #self.forma_indireta_consulta()
                
        # elif self.solicitacao['fk_idPerfil'] in ["1"] and self.solicitacao['sigla'] in ["SP"] and self.solicitacao['orgao'] in ["63"]:
            #estado sp
            #https://ola.oleconsignado.com.br/Simulacao/Index/?&09618590836&0000007835310&014583
        #     self.solicitacao['matricula'] = self.prepara_matricula_zeros_frente(self.solicitacao['matricula'],13)
        #     self.driver.get('https://ola.oleconsignado.com.br/Simulacao/Index/?&%s&%s&014583' % (self.solicitacao['cpf'],self.solicitacao['matricula']))
        #     time.sleep(1)
        #     if(self.driver.current_url.find("error") != -1):
        #         self.forma_indireta_consulta()

        # else:
        print('Consultando...')
        self.forma_indireta_consulta()
    
    def forma_indireta_consulta(self,time_sleep = 1):
        self.driver.get('https://ola.oleconsignado.com.br/Identificacao')
        time.sleep(time_sleep)
        try:
            self.selenium.atribuir_valor_campo_jquery('#CPF', self.solicitacao['cpf'])
            #self.act.hover_e_clique('//*[@id="CPF"]', By.XPATH)
            #self.act.enviar_texto('//*[@id="CPF"]', self.solicitacao['cpf'], By.XPATH)
        except JavascriptException as e:
            self.executar_consulta_refinanciamentos(fila="refinanciamento")
        time.sleep(time_sleep)
        self.act.hover_e_clique('//*[@id="btnIniciarOperacao"]', By.XPATH)
        #self.selenium.clicar_elemento("#btnIniciarOperacao")
        time.sleep(time_sleep)
        self.selecionar_matricula() 

    def human_type(self,element, text):
        for char in text:
            time.sleep(random.randint(1,10)) #fixed a . instead of a ,
            element.send_keys(char)

    def prepara_matricula_zeros_frente(self,matricula,maximo_digitos):
        count = 0
        nova_matricula = matricula
        while count < maximo_digitos:
            nova_matricula = '0' + nova_matricula 
            if(len(nova_matricula) == maximo_digitos):
                return nova_matricula
            count += 1

    def consultar_refinanciamento(self):
        self.aba_identificacao_refin()
        if not self.buscar_lista_refinanciamentos():
            return False
        else:
            return True

    def selecionar_matricula(self):
        #try:
            #time.sleep(3)
        print('Entrou para selecionar')

        mensagem_nao_pertube = ""
        try:
            mensagem_nao_pertube = self.act.obter_texto('//*[@id="divMensagemErro"]/ul/li',By.XPATH)  
        except:
            pass  

        mensagem_contrato_portabilidade = ""
        try:
            mensagem_contrato_portabilidade = self.act.obter_texto('//*[@id="compPortabilidadeContainer"]/div/h5',By.XPATH)  
        except:
            pass   
        
        if('restrições definidas em Política Interna' in mensagem_nao_pertube or 'Não perturbe' in mensagem_nao_pertube or 'Não Me Perturbe' in mensagem_nao_pertube or 'Não é possível seguir com essa proposta devido a restrições definidas pela Autorregulação' in mensagem_nao_pertube):
            raise NotFoundResultException(message='Pulando solicitação pois não existem refinanciamentos disponíveis!!\n')

        if (self.driver.current_url.find("unauthorized") > -1 or self.driver.current_url.find("SessionUnauthorized") > -1):
            print('Sistema deslogou... Novo login sendo realizado...')
            self.consultar_refins_e_potenciais()

        try:
            self.selenium.clicar_elemento("a:contains(Operações Disponíveis - Empréstimo)")
            self.verificar_loading()
        except JavascriptException as e:
            self.executar_consulta_refinanciamentos(fila="refinanciamento")

        time.sleep(2)

        try:
            table_id = self.driver.find_element(By.ID,'tbRefin')
            linhas = table_id.find_elements(By.TAG_NAME, "tr")
            #linhas = self.driver.find_element(By.CSS_SELECTOR,'#tbRefin tbody tr')
        except:
            raise RefinanciamentosInexistente(message='Pulando solicitação pois não existem refinanciamentos disponíveis!!\n')    

        if not linhas:
            #linhas = self.driver.find_element(By.CSS_SELECTOR,'#tbCompPortab tbody tr')
            table_id = self.driver.find_element(By.ID,'tbCompPortab')
            linhas = table_id.find_elements(By.TAG_NAME, "tr")
            if('COMPLEMENTO DE PORTABILIDADE' in mensagem_contrato_portabilidade):
                raise NotFoundResultException(message='Pulando solicitação pois não existem refinanciamentos disponíveis!!\n')        

        for linha in linhas:
            colunas = linha.text.split(' ')
                # if colunas[0].text.find(self.solicitacao['matricula']) != -1:
                #     colunas[1].find_element(By.CSS_SELECTOR,'a').click()
                #     self.verificar_loading()
                #     return

            if self.solicitacao['matricula'] in colunas[0] or similaridade(self.solicitacao['matricula'],colunas[0]) > 55:
                print('Selecionando a matrícula...')
                linha.find_element(By.CSS_SELECTOR,'a').click()
                self.verificar_loading(120,True)
                return


            #raise NotFoundResultException(message='Pulando solicitação pois não existem refinanciamentos disponíveis!!\n')
        #except:
            #print ('Não há refinanciamentos disponíveis - trace selecionar matricula')
            #pass
            # pdb.set_trace()
            
    def buscar_lista_refinanciamentos(self):
        try:
            while self.selenium.buscar_quantidade_elemento_somente_tela('#divMensagemSucesso') == 1:
                self.selenium.clicar_elemento('#btnOKMensagemSucesso')
                time.sleep(3)
        except:
            pass
        
        try:
            try:
                self.selenium.clicar_elemento('#idCheckBox-1')
            except:
                self.selenium.clicar_elemento("#radioDigital")
            time.sleep(3)
        except:
            print('nao clicou no radio')
            self.executar_consulta_refinanciamentos(fila=self.tipo_fila)


        self.contratos_portabilidade = False 
        try:
            if 'Portabilidade' in self.selenium.verificar_texto_campo_driver('#GridContratos'):
                self.contratos_portabilidade = True 

                try:
                    msg_erro = self.selenium.verificar_texto_campo_driver('#divMensagemErro')
                except:
                    msg_erro = ""
                    pass

                if('Não existe(m) produto(s) para as condições informadas' in msg_erro):
                    print('Pulando consulta por não ter contrato para refinanciar na portabilidade...')
                    return False

        except:                
            pass

        if not self.preencher_complementos(self.contratos_portabilidade):
            print('Pulando solicitação pois o órgão não foi encontrado!\n')
            return False

        else:

            self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)            

            linhas_refinanciamento = self.tratar_linhas_refinanciamento()
            self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)   
            checkbox_selecionado = None

            i = 0
            for linha in linhas_refinanciamento:
                #pdb.set_trace()
                i += 1

                if(i > 1):
                    if checkbox_selecionado is not None:
                        self.selenium.clicar_elemento(checkbox_selecionado)
                        time.sleep(2)

                    self.selenium.clicar_elemento(linha['checkbox'])
                else:
                    mycheckbox = self.driver.find_element(By.ID, linha['checkbox'].replace('#',''))
                    if not mycheckbox.is_selected():
                        self.selenium.clicar_elemento(linha['checkbox'])

                checkbox_selecionado = linha['checkbox']
                time.sleep(1)
                
                try:
                    if(self.contratos_portabilidade):
                        self.act.hover_e_clique('//*[@id="divRefin"]/div[2]/div[4]/div/div/button', By.XPATH)
                        time.sleep(0.5)

                        try:
                            loc_tabela_portabilidade = '//*[@id="divRefin"]/div[2]/div[4]/div/div/div/div/input'
                            self.act.enviar_texto_intervalado(loc_tabela_portabilidade, '012397', By.XPATH)
                            self.act.press_enter(loc_tabela_portabilidade, By.XPATH)
                        except:
                            pass

                    self.selenium.clicar_elemento('#btnCalcularRefin')

                    self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)  
                    
                    if self.contratos_portabilidade and self.selenium.buscar_quantidade_elemento('.alert-dismissible\\:visible'):
                        if 'Valor da taxa está fora dos limites do parâmetro' in self.selenium.verificar_texto_campo_jquery('#divMensagemErro'):
                            raise PularCheckboxException(message="Não há refinanciamento disponível para essa proposta.")
                        if 'Selecione um Produto para realizar o cálculo' in self.selenium.verificar_texto_campo_jquery('#divMensagemErro'):
                            raise PularCheckboxException(message="Não há refinanciamento disponível para essa proposta.")
                        #if 'Ocorreu um erro interno. Tente novamente' in self.selenium.verificar_texto_campo_jquery('#divMensagemErro'):
                        #    raise PularCheckboxException(message="Não há refinanciamento disponível para essa proposta.")

                    self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)   

                    try:
                        codigo = self.act.retornar_elemento('#idNomeProduto-1').text
                    except:
                        codigo = ''
                        self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)   

                    selector = True
                    
                    if self.solicitacao['sigla'] == 'SP':
                        selector = self.produto_sp(codigo, self.db_info)
                    if selector:
                        self.selenium.atribuir_valor_campo_jquery('#SelectProdutoRefin', codigo[0:6], change=True)
                        self.verificar_loading(pular_erro_portabilidade = self.contratos_portabilidade)
                        try:
                            valor_liberado = self.driver.find_element(By.CSS_SELECTOR,'#idValorLiberado-1').text
                            self.validar_condicoes_refinanciamento(valor_liberado)
                        except:
                            raise PularCheckboxException(message="Não há refinanciamento disponível para essa proposta.")
                    else:
                        raise PularCheckboxException(message="Não foi possível fazer o refinanciamento com as tabelas "
                                                             "pré-definidas para essa proposta!")

                except PularCheckboxException as e:
                    print(e.message)
                    self.dados.atualizar_impossibilidade_consulta(self.solicitacao, e.message)
                    continue

                prazo = self.driver.find_element(By.CSS_SELECTOR,'#idQteParcela-1').text
                
                if(linha['saldoDevedor'] and valor_liberado and prazo and linha['valorParcela']):
                    self.refinanciamentos.append({
                        'saldoDevedor': linha['saldoDevedor'],
                        'valorLiberado': valor_liberado,
                        'prazo': prazo,
                        'valorParcela': linha['valorParcela']
                    })
                else:
                    raise ErrorOleException(message="Erro de configurações de valores de refinanciamento linha 408!")

            return True

    def produto_sp(self, codigo, db):
        tabelas = db.get(Query().idOrgaoUconecte == self.solicitacao['orgao'])

        for tabela in tabelas['tabela']:
            if tabela['nome'] == codigo:  # tabela calculada já está dentro das normas
                return True

        for tabela in tabelas['tabela']:
            try:
                self.selenium.atribuir_valor_campo_jquery('#SelectProdutoRefin', tabela['codigo'], change=True)
                self.verificar_loading()
                self.selenium.clicar_elemento('#btnCalcularRefin')
                self.verificar_loading()
                return True
            except PularCheckboxException:
                continue

        return False

    def preencher_complementos(self, pular_erro_portabilidade = False):
        codigo_orgao = ''
        if self.solicitacao['orgao'] == '79' or self.solicitacao['sigla'] == 'MT':
            if self.selenium.verificar_valor_campo_jquery('#CodigoEspecieBeneficio') == '':
                self.selenium.atribuir_valor_campo_jquery("#CodigoEspecieBeneficio", self.solicitacao['especieBeneficio'], change=True)
            #  Se for INSS ou MT pula pois o orgão já é preenchido automaticamente pelo sistema do Olé
            return True

        

        if self.selenium.verificar_valor_campo_jquery('#CodigoOrgao') == '':
            if self.solicitacao['fk_idPerfil'] == '2':
                self.verificar_loading(pular_erro_portabilidade = pular_erro_portabilidade)
                #regex = r"(\d{4,6})"
                try:
                    self.selenium.atribuir_valor_campo_jquery('#CodigoOrgao', '000783', change=True)
                    time.sleep(3)
                    codigo_orgao = self.selenium.verificar_texto_campo_driver('#divMensagemErro').split('\n')[2][0:6]
                    self.selenium.atribuir_valor_campo_jquery('#CodigoOrgao', codigo_orgao, change=True)
                    # matches = re.finditer(regex, self.selenium.verificar_texto_campo_driver('#divMensagemErro'), re.MULTILINE)
                    # import pdb
                    # pdb.set_trace()
                    # for matchNum, match in enumerate(matches, start=1):
                    #     self.selenium.atribuir_valor_campo_jquery('#CodigoOrgao', match.group(0), change=True)
                    #     break
                except:
                    pass

                return True
            else:
                cd_orgao = self.ajusta_db(self.db_info)
                if not cd_orgao:
                    print(
                        f"\nNão foi possível encontrar o Órgão da solicitação: {self.solicitacao}...")
                    return False
                else:
                    self.selenium.atribuir_valor_campo_jquery('#CodigoOrgao', cd_orgao, change=True)
                    return True

    def tratar_linhas_refinanciamento(self):
        linhas_tratadas = []

        #linhas_refinanciamento = self.driver.find_element(By.CSS_SELECTOR,'#tblContratosAptoRefin tbody tr')
        table_id = self.driver.find_element(By.ID,'tblContratosAptoRefin')
        linhas_refinanciamento = table_id.find_elements(By.TAG_NAME, "tr")  
        
        for linha in linhas_refinanciamento:
            if(self.contratos_portabilidade == True):
                try:
                    checkbox = f"#{linha.find_element(By.CSS_SELECTOR,'input[type=radio]').get_attribute('id')}"
                except NoSuchElementException:
                    continue   
            else:
                try:
                    checkbox = f"#{linha.find_element(By.CSS_SELECTOR,'input[type=checkbox]').get_attribute('id')}"
                except NoSuchElementException:
                    continue

            #colunas = linha.find_element(By.CSS_SELECTOR,'td')
            colunas = linha.text.split(' ')

            linhas_tratadas.append({
                'checkbox': checkbox,
                'valorParcela': colunas[4],
                'saldoDevedor': colunas[5]
            })

        return linhas_tratadas

    def tratar_mensagens_erro(self, erros):
        erros = self.limpar_mensagem_erro(erros)

        erros_identificados = [
            {
                'erro': r"CPF com suspeita de óbito.",
                'mensagem': 'Reprovado a Conferir',
                'Restricao': True
            }, {  # TODO: codigo duplicado para teste
                'erro': r'Pagina fora do ar.',
                'PularRefin': True
            }
        ]

        erros_regex = [
            {
                'erro': r"Valor liberado inferior ao mínimo permitido.",
                'Pular': True
            }, {
                'erro': r"Não existe produto para as condições informadas.",
                'Pular': True
            }, {
                'erro': r"VALOR LIBERADO INFERIOR AO MÍNIMO PERMITIDO",
                'Pular': True
            }, {
                'erro': r"A combinação dos valores informados não possibilitam o cálculo da simulação",
                'Pular': True
            }, {
                'erro': r"Valor da simulação não pode ser menor ou igual ao valor total do refinanciamento.",
                'Pular': True
            }, {
                'erro': r"A taxa informada não pode ser maior que a taxa ponderada",
                'Pular': True
            }, {
                'erro': r"Não existem propostas de contratos aptos a refinanciamento",
                'Pular': True
            },{
                'erro': r"risco por CPF ou limite de valores",
                'Pular': True
            }, {
                'erro': r"O valor solicitado, somando outras operações existentes, excede o RISCO MÁXIMO.",
                'Pular': True
            }, {
                'erro': r"Parcela de número:",
                'Error': True
            }, {
                'erro': r"Ocorreu um erro interno. Tente novamente.",
                'Error': True
            }, {
                'erro': r"Ocorreu um erro inesperado, tente novamente mais tarde.",
                'Error': True
            }, {
                'erro': r"Benefício é obrigatório",
                'PreencheBeneficio': True
            }, {
                'erro': r"Cliente possui contrato com inadimplência.",
                'Restricao': True
            }, {
                'erro': r"CPF possui restrição.",
                'Restricao': True
            }, {
                'erro': r"Não existem contratos aptos para refinanciamento.",
                'NotFound': True
            },{
                'erro': r"Não existem simulações de refinanciamento disponíveis",
                'Pular': True
            },{
                'erro': r"Cliente possui número máximo de operações em aberto (CPF e MATRÍCULA) para o convênio 013579",
                'NotFound': True
            }, {
                'erro': r"Este convenio não poderá ser utilizado, pois o cliente possui \d{2} anos e não existem planos à serem aplicados para cadastro da proposta devido o limite de idade ser de \d{2} anos na data base da Operação.Favor utilizar outro convenio.",
                'Restricao': True
            }, {
                'erro': r"Este convenio não poderá ser utilizado, pois o cliente possuirá \d{2} anos no vencimento da operação e não existem planos à serem aplicados para cadastro da proposta devido o limite de idade ser de 74 anos no vencimento da Operação. Favor utilizar outro convenio.",
                'Restricao': True
            }, {
                'erro': r"Cliente não atende à regra interna deste benefício.",
                'Restricao': True
            }, {
                'erro': r"Valor solicitado é maior do que o permitido para a Idade do Financiado.",
                'Restricao': True
            }, {
                'erro': r"Falha na solicitação. Para mais informações, entre em contato com a Olé!",
                'PularRefin': True
            }, {
                'erro': r"Saldo devedor mais valor solicitado excede o valor de RISCO MÁXIMO.",
                'Pular': True
            }, {
                'erro': r"object reference not set to an instance of an object.",
                'PularRefin': True
            }, {
                'erro': r'Pagina fora do ar.',
                'PularRefin': True
            },{
                'erro': r'Nenhuma proposta encontrada para o intervalo de 1 mês. Período: \d{2}\/\d{2}\/\d{4} à \d{2}\/\d{2}\/\d{4}.',
                'NotFound': True
            },{
                'erro': r'One or more errors occurred. (An error occurred while sending the request.)',
                'PularRefin': True
            },{         
                'erro': r'O valor da parcela deverá ser maior que o valor da parcela',
                'Pular': True
            },{           
                'erro': r'Não existe produto para as condições informadas. Taxa mínima necessária: \d{1}\,\d{2}\%',
                'Pular': True    
            },{
                'erro': r'O produto selecionado possui uma taxa que está fora do intervalo aceito para esta operação (\d{1}\,\d{2}\% a \d{1}\,\d{2}\% a.m.). Refaça a sua simulação utilizando um produto válido.',
                'Pular': True
            },{
                'erro': r'O produto selecionado possui uma taxa que está fora do intervalo aceito para esta operação.',
                'Pular': True
            },{
                'erro': r'Selecione um ou mais contratos para Refinanciamento.', 
                'Pular': True 
            },{
                'erro': r'Valor solicitado ou valor da parcela é de preenchimento obrigatório.', 
                'Pular': True 
            },{
                'erro': r'Órgão é obrigatório.',
                'ErroOrgao': True
            },{
                'erro': (r'Cliente possui número máximo de operações em aberto'
                         r' (CPF e MATRÍCULA) para o convênio \d.'),
                'PularRefin': True
            },{
                'erro': 'Não foi possivel recuperar os dados de todos os contratos informados',
                'NotFound': True,
            },{
                'erro': r"O órgão informado não está vinculado à matrícula. Favor alterar para um "
                        "dos órgãos listados abaixo e consultar a margem novamente.",
                'Pular': True
            },{
                "erro": "'Codigo Correspondente' não pode ser nulo.",
                "Pular": True
            },{
                "erro": "'Código correspondente é obrigatório'",
                "Pular": True
            },{
                "erro": r"Percentual mínimo de quitação não atingido",
                "Pular": True
            },{
                "erro": r"ORIGEM2 INVÁLIDA",
                'Error': True
            },{
                "erro": r"O órgão informado não está vinculado à matrícula. Favor alterar para um dos órgãos listados abaixo e consultar a margem novamente.",
                'Pular': True
            },{
                "erro": r"Não há operações disponíveis para contratos de empréstimo",
                "SemRefin": True
            },{
                "erro": r"Este convênio não possui venda padrão",
                "ContinuarConsulta": True
            }, {
                'erro': r"Benefício inativado pelo órgão. Em caso de dúvidas, gentileza verificar junto ao INSS",
                'Restricao': True
            }, {
                'erro': r"A taxa informada não pode ser maior que a taxa encarteirada",
                'Pular': True
            }
        ]

        if erros == 'Pagina fora do ar.':
            print("ErrorOleException. Aguardando atualizar página...")
            time.sleep(2)
            raise ErrorOleException

        for erro_identificado in erros_identificados:
            try:
                erros.index(erro_identificado['erro'])
                if erro_identificado['mensagem'] == "Reprovado a Conferir":
                    print("Atualizando contrato:", erro_identificado['mensagem'])
                    self.atualizar_contrato(self.codigo_contrato, erro_identificado)
                    raise RestricaoException("Refinanciamento não disponível!")
                elif erro_identificado['mensagem'] == 'PularRefin':
                    self.executar_consulta_refinanciamentos(fila=self.tipo_fila)
            except ValueError:
                pass

        for erro_regex in erros_regex:
            regex = re.compile(erro_regex['erro'], re.IGNORECASE)
            erro_encontrado = [erro for erro in erros for match in [
                regex.search(erro)] if match]
            
            if not erro_encontrado:
                continue

            if 'Restricao' in erro_regex:
                raise RestricaoException("Refinanciamento não disponível!")
            elif 'Pular' in erro_regex:
                raise PularCheckboxException("Refinanciamento não disponível para essa proposta!")
            elif 'SemRefin' in erro_regex:
                raise RefinanciamentosInexistente("Refinanciamento não disponível para essa proposta!")
            elif 'Error' in erro_regex:
                raise ErrorOleException("Erro ao calcular refinanciamento!")
            elif 'ErrorParcela' in erro_regex:
                raise ErrorOleException(
                    "Encontrada erro em uma das parcelas da proposta ao calcular o refinanciamento!")
            elif 'NotFound' in erro_regex:
                raise NotFoundResultException("Não tem todas as informações para consulta")
            elif 'ErroOrgao' in erro_regex:
                raise ErrorOleException("Erro de orgao.")
            elif 'ContinuarConsulta' in erro_regex:
                print('Continuando a consulta... E fechando o alerta...')   
                self.selenium.clicar_elemento('#closeDivMensagemAlerta') 
                return
            elif 'PreencheBeneficio' in erro_regex:
                self.selenium.atribuir_valor_campo_jquery("#CodigoEspecieBeneficio", self.solicitacao['especieBeneficio'], change=True)   
                self.selenium.clicar_elemento('#idCheckBox-1')
                self.selenium.clicar_elemento('#btnCalcularRefin')      
                time.sleep(5)  
            elif 'PularRefin' in erro_regex:
                continue
                #self.main()

        self.mensagem_erro_nao_encontrada(erros)

    def mensagem_erro_nao_encontrada(self, erros):
        raise ErrorOleException(erros)

    def validar_condicoes_refinanciamento(self, valor_liberado):
        taxa = formatar_porcentagem(self.driver.find_element(By.CSS_SELECTOR,'#idTaxa-1').text)

        if formatar_moeda(valor_liberado) < 250.00:
            raise PularCheckboxException(message='Não atingiu o valor mínimo')
        # elif taxa < 1.7:
        #     raise PularCheckboxException(message='Taxa indisponível para cálculo de refinanciamento!')

    def ajusta_db(self, db):
        """
        Função responsável por pegar o ID do órgão referente ao sistema da OLÉ a partir do id do Órgão referente à
        uConecte
        :param db: variável no formato TinyDB
        :return: valor da ID do órgão referente ao sistema da OLÉ ou False caso não encontre o órgão no .json
        """
        if self.solicitacao["sigla"] == "SP":
            tabelas = db.get(Query().idOrgaoUconecte == self.solicitacao['orgao'])
            return tabelas['idOrgaoOle']

        else:
            cd_orgaos = db.get(Query().sigla == self.solicitacao['sigla'])
            aux = cd_orgaos['tabela'][0]
            aux2 = list(aux.items())

            for key, value in aux2:
                if value == self.solicitacao['orgao']:
                    return aux2[(aux2.index((key, value))) + 1][1]

            return False


class NotFoundResultException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PularCheckboxException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class RefinanciamentosInexistente(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class RestricaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.helpers import aguardar_n_segundos, definir_nome_robo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

definir_nome_robo("Ole - Consulta Refin")

chrome_user = PATHS.chrome_user("OleRefin")

try:
    shutil.rmtree(PATHS.project_path()+'/chrome_user_dir/OleRefin')
except:
    pass

options = Options()
options.add_argument('--ignore-ssl-errors')
options.add_argument('log-level=3')
options.add_argument(chrome_user)
Manager.criar_pasta_usuario_chrome(chrome_user)

driver = webdriver.Chrome(
            #executable_path=PATHS.driver_path(),
            options=options)
driver.get('https://ola.oleconsignado.com.br/Home')

for i in range(10):
    ConsultaRefinanciamento.iniciar_horario_comercial(driver=driver)
    aguardar_n_segundos(60)
    
#manager.driver.quit()



#removido

# if __name__ == "__main__":
#     from sites.baseRobos.manager import Manager
#     from sites.baseRobos.core.helpers import aguardar_n_segundos, definir_nome_robo
#     definir_nome_robo("Ole - Consulta Refin")
#     manager = ()
#     manager.init_chrome_driver()
#     manager.driver.get('https://ola.oleconsignado.com.br/Home')
#     manager.set_options(
#         '--ignore-ssl-errors', 'log-level=3',
#         "--headless", "--no-sandbox")

#     for i in range(10):
#         ConsultaRefinanciamento.iniciar_horario_comercial(driver=manager.driver)
#         aguardar_n_segundos(60)
    
#     manager.driver.quit()
    

