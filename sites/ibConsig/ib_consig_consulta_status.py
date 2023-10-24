from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from sites.core.selenium_helper import SeleniumHelper

import os, sys, time, requests,json
import pyautogui
import re
import pdb
import datetime
from datetime import timedelta

from sites.core.captcha import TwoCaptcha
from sites.core.uconecte import Uconecte
from sites.baseRobos.core.helpers import (
    identificar_erro_robo, definir_nome_robo)
from sites.baseRobos.data_handler import DataHandler
from sites.ibConsig.gerar_contrato.gerar_contrato import GerarContratoIbConsig


class IbConsigGetStatus:
    def __init__(self):
        self.id_robo = 5
        self.caminho_base = os.getcwd().replace("\\", "/")
        self.driver = self.iniciar_google_chrome()
        
        self.selenium_helper = SeleniumHelper(self.driver)
        self.cookies_path = GerarContratoIbConsig.cookies_path
        self.logado = False
        self.captcha = TwoCaptcha(self.driver, manual=True)
        self.url_consulta_status = ('https://www.ibconsigweb.com.br/situacaoContrato.do?method'
                                    '=listar&situacaoContratoFiltroForm.numeroAde=')

        self.uconecte = Uconecte()
        self.log = DataHandler()

    def iniciar_google_chrome(self):
        options = Options()
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('log-level=3')

        options.add_argument("--window-size=1200,800")
        #options.add_argument('--user-data-dir=C:/Users/lucas.s/AppData/Local/Google/Chrome/IbConsig4')
        options.add_argument(   '--user-data-dir=C:/Users/marcelo/AppData/Local/Google/Chrome/Robo 2/Profile 5')

        return webdriver.Chrome(
            executable_path=self.caminho_base + "/drivers/chromedriver.exe",
            chrome_options=options)

    def main(self):

        self.verifica_horario_comercial()
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

        input("Adicionando os cookies do primeiro usuário...")
        #self.selenium_helper.load_cookies(self.cookies_path,True)

        contratos_a_atualizar = self.busca_contratos_em_andamento()

        for contrato in contratos_a_atualizar[1:]:
            self.log.api_iniciar_log_robo(
                idRobo=self.id_robo,
                idSolicitacao=contrato[2]
            )
            definir_nome_robo('Atualiza Status Proposta IbConsig')
            try:
                #contrato[0] = '418140'
                #contrato[2] = '47815860'
                print('Pesquisando contrato %s...' % (contrato[2]))
                self.driver.get(self.url_consulta_status + contrato[0])
                dados = self.busca_dados_proposta(contrato[0], contrato[2])
                
                if dados:
                    self.atualiza_contrato_web_admin(contrato[2], dados)
                    self.log.api_registrar_log_robo(
                        log='Sincronização realizada com sucesso.',
                        status=2
                    )
                else:
                    print('Erro ao atualizar a proposta...')
                    self.main()
            except Exception as e:
                self.log.api_registrar_log_robo(
                    log=f'ERRO: {e}',
                    status=0
                )
                identificar_erro_robo()
                print(e)

        self.atualiza_horario_sincronizacao_web_admin()
        self.countdown(180, 10, 'Sincronização ok, horário de término atualizado... Aguardando 10 minutos...')

        self.main()

    def verifica_horario_comercial(self):
        data_hora = datetime.datetime.now()
        if (data_hora.hour > 21):
            print('Fora do horário comercial... Inciando o processo para próxima manhã (8:00)...')
            self.driver.close()
            self.countdown(39600, 3600, 'Aguardando...')
            self.__init__()
            self.main()

    def login_sistema(self):
        try:
            campo_login = self.driver.find_element(By.CSS_SELECTOR,
                "input[name='usuario']")
            campo_login.clear()
            campo_login.send_keys(self.usuario)

            password = self.driver.find_element(By.NAME,"j_password")
            password.clear()
            password.send_keys(self.senha)

            id_captcha, captcha_resposta = self.captcha.resolver_captcha(
                "[name='iCaptcha']")
            captcha_field = self.driver.find_element(By.NAME,"captcha")
            captcha_field.send_keys(captcha_resposta)
            captcha_field.send_keys(Keys.RETURN)
            time.sleep(10)

            # Verifica se esta na tela correta e se o login foi bem sucedido
            campo_senha = self.driver.execute_script(
                "return $('[name=j_password]').length")

            if (campo_senha == 1):
                print('Error -  Problema no login usuário')
                self.captcha.mudar_status_captcha(id_captcha, '2')
                return False

            print('Logado com sucesso')
            self.captcha.mudar_status_captcha(id_captcha, '1')
            return True
        except Exception:
            return False

    def busca_contratos_em_andamento(self):
        request_contratos_a_consultar = requests.get(
            'https://emprestimofacil.co/web_admin/api/v1/contratos/em-analise/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f')

        if (request_contratos_a_consultar.status_code != 200):
            input('Itaú Consignado Consignado Error - Não foi possível buscar os contratos')
        self.uconecte.atualizar_status_robo(self.id_robo)
        return request_contratos_a_consultar.json()

    def busca_dados_proposta(self, ade, codigo_con):
        #self.countdown(1, 1, 'Buscando proposta...')
        erro_consulta = ''
        erro_consulta_pesquisa = ''
        try:
            self.driver.execute_script("""$('[title="Situação do contrato"]').click()""")
        except Exception:
            print('Página ainda não carregou, tentando novamente..')
            self.busca_dados_proposta(ade, codigo_con)

        detalhes_proposta = self.busca_status_contrato_tela()
        
        try:
            erro_consulta = self.driver.execute_script(
                """return $('.erro').text()""")  # 'Ocorreram erros no processamento de sua requisição. Erro: IC_0109'
            erro_consulta_pesquisa = self.driver.execute_script(
                """return $('.TituloTabela').html().trim()""")  # A pesquisa não retornou resultado.
        except:
            pass

        if (erro_consulta or erro_consulta_pesquisa):
            if (erro_consulta_pesquisa):
                self.driver.execute_script("""$('input[name="situacaoContratoFiltroForm.cpf"]').val('');
                                              $('#submitButton').click();""")
            return False
        else:
            if (detalhes_proposta[0] == 'Cancelada' or detalhes_proposta[0] == 'Rejeitada' or detalhes_proposta[0] == 'Solicitada'):
                status_proposta = detalhes_proposta[0]
                observacao_detalhada = '%s - %s -  %s %s %s %s' % (detalhes_proposta[1], detalhes_proposta[2],
                                                                   detalhes_proposta[3], detalhes_proposta[4],
                                                                   detalhes_proposta[5], detalhes_proposta[-1])
            else:
                status_proposta = detalhes_proposta[0] + ' - ' + detalhes_proposta[1]
                observacao_detalhada = '%s %s' % (detalhes_proposta[3], detalhes_proposta[-1])

            dados = {
                "key": "f689f1e12a0399fba803cb2365fc362f",
                "statusPropostaBanco": status_proposta,
                "observacaoDetalhadaBanco": observacao_detalhada,
                "formalizacao": self.consistencia_pre_formalizacao,
                "consistenciasNaoLiberadas": self.array_consistencia,
                "consistenciaAnuenciaAverbacao": self.array_consistencia_183,
                "consistenciaAntiFraude": self.array_consistencia_51_155,
                "codigoCon": codigo_con,
                "ade": ade
            }

            return dados

    def busca_status_contrato_tela(self):
        detalhes_proposta = self.driver.execute_script("""return $('table:contains("Informações do Contrato")').text()
                                                                    .concat($('table:contains("Restrições")').text())
                                                                    .concat($('table:contains("Histórico da ADE")').text())
                                                                    .concat($('table:contains("Consistências/Ocorrências")').text()
                                                                    .concat($('table:contains("Informação de Portabilidade")').text()))
                                                        """) 
        detalhes_observacoes = detalhes_proposta.split('\n')

        #trata o cancelada
        arrayTextosNaoUteis = ["Informações do Contrato","STATUS",
                                "SITUAÇÃO","DATA","DESCRIÇÃO DA PROPOSTA",
                                "DETALHE","Restrições","CÓDIGO DO RETORNO",
                                "DESCRIÇÃO DO RETORNO","DATA RESTRIÇÃO",
                                "Histórico da ADE",
                                "REPONSÁVEL","TIPO","DESCRIÇÃO"]

        array_texto_resultado = []
        array_texto_resultado_detalha_cancelada = []

        for texto in detalhes_observacoes:
            if(texto not in arrayTextosNaoUteis and texto != "" and "\t" not in texto):
                array_texto_resultado.append(texto)
                if("CANCELADA" in texto):
                    if not array_texto_resultado_detalha_cancelada:
                        array_texto_resultado_detalha_cancelada.append(texto)

        #trata a consistencia 112 e 160 automatica
        array_textos_consistencia_112_160_nao_liberada = ["CONSISTÊNCIA 112 NEGADA - RETORNO INSS AM. REGULARIZAR OS DADOS BANCARIOS NO PORTAL OPERACIONAL (AUTOSSERVICO)",
                                                      "CONSISTÊNCIA 112 NEGADA - RETORNO INSS AN. REGULARIZAR A CONTA NO PORTAL OPERACIONAL (AUTOSSERVICO)"]

        texto_aguardando_112 = "CONSISTÊNCIA 112 NEGADA - VALIDAÇÃO DE DADOS INSS \x1a AGUARDANDO RETORNO"
        consistencia_112_liberada = []

        if("CONSISTÊNCIA 112 LIBERADA - #112#LIBERACAO DE CONSISTENCIA 112" in detalhes_observacoes or "#112# Consistência 112 liberada." in detalhes_observacoes):
            consistencia_112_liberada.append("- CONSISTENCIA 112 JA LIBERADA")

        if not consistencia_112_liberada:
            for texto_nao_liberada in array_textos_consistencia_112_160_nao_liberada:
                if(texto_nao_liberada in detalhes_observacoes):
                    if(texto_aguardando_112 not in detalhes_observacoes or detalhes_observacoes.index(texto_nao_liberada) > detalhes_observacoes.index(texto_aguardando_112)):
                        consistencia_112_liberada.append("- CONSISTENCIA REPROVADA POR DADOS BANCARIOS")

        if not consistencia_112_liberada:
            consistencia_112_liberada.append("- CONSISTENCIA AGUARDANDO")

        consistencia_retencao_portabilidade = []
        if("Essa proposta de refinanciamento foi utilizada na retenção de um pedido de portabilidade. É necessário formalizar a operação mesmo com o cancelamento do refinanciamento." in detalhes_observacoes):
            consistencia_retencao_portabilidade.append("- PEDIDO DE PORTABILIDADE")

        consistencia_atraso_refinanciamento = []
        if("REFINANCIAR OU REGULARIZAR O(S) CONTRATO(S) EM ATRASO" in detalhes_observacoes):
            consistencia_atraso_refinanciamento.append("- ATRASO EM CONTRATO")
        
        self.consistencia_pre_formalizacao = 0
        if("Analise do Kit Digital Concluída" in detalhes_observacoes or "ANALISE DO KIT DIGITAL CONCLUÍDA" in detalhes_observacoes or "Pré Formalização - Regularizada" in detalhes_observacoes or "CONSISTÊNCIA 277 LIBERADA - #277##001# - ANALISE DO KIT DIGITAL CONCLUÍDA" in detalhes_observacoes or "CONSISTÊNCIA 276 LIBERADA - #276##001# - ANALISE DO KIT DIGITAL CONCLUÍDA" in detalhes_observacoes):
            self.consistencia_pre_formalizacao = 1

        self.array_consistencia =  self.verifica_consistencia_liberada(['261','262','264','265'],array_texto_resultado,2)
        self.array_consistencia_183 =  self.verifica_consistencia_liberada(['183'],array_texto_resultado,24)
        self.array_consistencia_51_155 =  self.verifica_consistencia_liberada(['51','155'],array_texto_resultado,12)
        
        return array_texto_resultado+consistencia_112_liberada+array_texto_resultado_detalha_cancelada+consistencia_retencao_portabilidade+consistencia_atraso_refinanciamento

    def verifica_consistencia_liberada(self,consistencias,array_texto,horas_atraso):
        horas_limite_atraso = datetime.timedelta(hours=horas_atraso)
        consistencias_nao_liberadas = []

        for consistencia in consistencias: 
            if(consistencia in array_texto):
                try:
                    data_inicial_consistencia = datetime.datetime.strptime(array_texto[array_texto.index(consistencia)+1],'%d/%m/%Y %H:%M')
                    data_agora = datetime.datetime.now()
                    horas_passadas = data_agora - data_inicial_consistencia
            
                    consistencia_liberada_andamento = 0
                    pedido_banco = 0
                    posicao_texto_banco = 0
                    envio_empresa = 0
                    posicao_texto_empresa = 0
                    liberada_consistencia = ''
                    for i in range(6,60,4):
                        try:
                            consistencia_analisar = array_texto[array_texto.index(consistencia)+i-2] 
                        except:
                            continue

                        if(array_texto[array_texto.index(consistencia)+i-2] == consistencia):
                            liberada_consistencia = array_texto[array_texto.index(consistencia)+i]
                            texto_consistencia = array_texto[array_texto.index(consistencia)+i+1]
                            if(r"108-" in texto_consistencia or r"088-" in texto_consistencia or r"089-" in texto_consistencia or r"Documentacao enviada ilegivel" in texto_consistencia):
                                pedido_banco += 1
                                posicao_texto_banco = i
                            if(r"042-" in texto_consistencia or r"109-" in texto_consistencia or r"115-" in texto_consistencia):
                                envio_empresa += 1
                                posicao_texto_empresa = i
                            if(liberada_consistencia == 'Consistência Liberada'):
                                pedido_banco = 0
                                envio_empresa = 0
                                consistencia_liberada_andamento = 1
                                break

                    if(consistencia_liberada_andamento == 0):
                        if(posicao_texto_banco > posicao_texto_empresa):
                            consistencia_liberada_andamento = 0

                        if(posicao_texto_empresa > posicao_texto_banco):
                            consistencia_liberada_andamento = 1

                    if(consistencia_liberada_andamento == 1):
                            consistencias_nao_liberadas.append('')        
                    else:
                        if(horas_passadas > horas_limite_atraso):
                            consistencias_nao_liberadas.append(consistencia)
                        else:
                            consistencias_nao_liberadas.append('')
                except Exception as e:
                    consistencias_nao_liberadas.append(consistencia)

        array_consistencias = [int(x) for x in consistencias_nao_liberadas if x]
        if(array_consistencias):
            return 1
        else:
            return 0       
              
    def atualiza_contrato_web_admin(self,codigo_con,dados):
        request_dados_contrato = requests.post(
            "https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-itau-consignado/contratos/", data=dados)
        
        if (request_dados_contrato.status_code != 200):
            input('Itaú Consignado Error - Não foi possível atualizar o contrato %s no request' % (codigo_con))
        else:
            print('Contrato %s atualizado com sucesso!' % (codigo_con))
        
    def atualiza_horario_sincronizacao_web_admin(self):
        request_atualiza_horario_sincronizacao = requests.get(
            "https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-itau-consignado/sincronizacao/?key=f689f1e12a0399fba803cb2365fc362f")
        
        if (request_atualiza_horario_sincronizacao.status_code != 200):
            input('Itaú Consignado Erro - Não foi possível atualizar o horário de sincronização')
            
    def countdown(self,t,step=1,msg=''): 
        pad_str = ' ' * len('%d' % step)
        for i in range(t, 0, -step):
            print ('%s %d segundo(s) %s\r' % (msg, i, pad_str))
            sys.stdout.flush()
            time.sleep(step)
            
    

