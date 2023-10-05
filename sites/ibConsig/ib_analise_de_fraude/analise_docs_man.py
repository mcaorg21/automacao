import time,os,glob,pdb, json
from datetime import datetime
from typing import Dict
import requests
from dados.APIGetSource import APIDataSource
from sites.baseRobos.manager import Manager
from sites.baseRobos.core.helpers import executar_script_pop_up,deleta_todos_arquivos
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.ibConsig.ib_analise_de_fraude.analise_docs_auto import AnaliseDocsAuto
from sites.ibConsig.ib_analise_de_fraude.analise_docs_data import AnaliseDocsData
from sites.baseRobos.core.helpers import identificar_erro_robo
import PATHS
from pathlib import Path
from dados.database.queries.query_dados_robos import *
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.DebugTools import DebugTools
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.configs.dados_robos import ID_ROBOS
from sites.baseRobos.core.helpers import definir_nome_robo
from selenium.webdriver.common.by import By

import base64,time

dbg = DebugTools(debugging=False)

HORARIO_COMERCIAL = 7, 22


class PortalAnaliseDocsMan(Manager):

    ID = ID_ROBOS['ibConsig']['analiseFraude']

    urls = {"portal_analise": "https://www.analisedocumentos.com.br/",
            "ib_consig": (f"https://www.ibconsigweb.com.br/situacaoContrato.do?"
                          f"method=listar&situacaoContratoFiltroForm.numeroAde=")}

    def __init__(self):
        super().__init__()
        self.caminho_base = PATHS.project_path()
        self.user_path = PATHS.chrome_user("IbConsigFraude")
        self.criar_pasta_usuario_chrome(self.user_path)

        self.set_options(
            '--ignore-ssl-errors', self.user_path,
           )
        self.init_chrome_driver()

        self.auto = AnaliseDocsAuto(self.chrome_driver)
        self.data = AnaliseDocsData()
        self.login = {}
        #self.login: Dict[str, str] = query_login_pass_robo(26, "pmcg.1873")

        #self.login['login'] = 'mca1873'
        #self.login['senha'] = 't909176@'
        
        self.login['login'] = 'pmcg.1873'
        #self.login['login'] = 'arthur.1873'
        self.login['senha'] = '@uconecte28'

        self.ib_login = IbConsig.login_fact(
            usuario=self.login['login'], senha=self.login['senha'], driver=self.driver)

        self.act = SeleniumActions(self.driver)
        self.path = str(Path(PATHS.project_path() + "/ibConsig/anexos/portabilidade"))

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls):
        run = PortalAnaliseDocsMan()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        while True:
            definir_nome_robo("Itau - Análise Documentos")
            try:
                if self.anexar_documentos_contrato_no_portal():
                    print(f">> {str(datetime.now())} <<")
                    print(f"Iniciando análises documentais.")

                if self.anexar_documentos_ib_consig():
                    print(f">> {str(datetime.now())} <<")
                    print(f"Iniciando análises documentais.")

                else:
                    print("Aguardando 5 minutos...")
                    time.sleep(300)
                    self.driver.quit()
                    return
            except Exception as e:
                identificar_erro_robo()
                dbg.exception(e)

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def anexar_documentos_contrato_no_portal(self,fila_contratos = '', portabilidade = False):
        try:
            
            if not fila_contratos:
                fila_contratos: list = self.data.obter_contratos_para_analise_documental()[1:]

            if not fila_contratos:
                return False

            for contrato in fila_contratos:
                print(f"Código do contrato: {contrato[2]}")

                documentos: dict = self.data.get_request_documentos(contrato)

                if not documentos["link_log_final"]:
                    print("Não há documentos associados a este contrato")
                    time.sleep(10)
                    self.data.atualizar_status(contrato,
                                               "ERRO: Não há documentos associados a este contrato.")

                    return self.anexar_documentos_contrato_no_portal()

                # entrar no ib consig web
                self.chrome_driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

                # verificar se usuário está logado, caso não, executar login
                while 'index' in self.chrome_driver.current_url.lower():
                    print("Carregando cookies", self.cookies_path)
                    self.ib_login()
                    self.chrome_driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

                codigo_acesso: str = ""

                # redirecionar para página de contratos do cliente
                if(portabilidade):
                    self.chrome_driver.get(self.urls["ib_consig"] + str(contrato[3]))  # contrato[0]=ADE
                else:
                    self.chrome_driver.get(self.urls["ib_consig"] + str(contrato[0]))  # contrato[0]=ADE
                try:
                    try:
                        # encontrar código de acesso para o portal de análise de docs
                        linhas_ocorrencias, linhas_historico = self.auto.extrair_dados_tabelas()
                    except TimeoutException:
                        raise IndexError

                    data_codigo_historico: dict = self.data.extrair_datas_codigos_tabela(
                        linhas_historico, 3)
                    data_codigo_ocorrencias: dict = self.data.extrair_datas_codigos_tabela(
                        linhas_ocorrencias, 2)

                    datas_codigos: dict = {}

                    if data_codigo_historico:
                        datas_codigos.update(data_codigo_historico)
                    if data_codigo_ocorrencias:
                        datas_codigos.update(data_codigo_ocorrencias)

                    codigo_acesso: str = self.data.filtrar_solicitacao_de_analise_mais_recente(
                        datas_codigos)
                except IndexError:
                    print("Código não foi encontrado. É possível que o site ainda não"
                          "tenha liberado o código para consulta.")
                    self.data.atualizar_status(contrato, 'Aguardando análise do banco')
                    time.sleep(20)
                    continue

                # redirecionar para portal de analise
                self.chrome_driver.get(self.urls["portal_analise"])

                dbg.debugger()

                self.auto.acessar_portal(codigo_acesso)
                erro_acesso = self.auto.verificar_erros_acesso_portal()

                # caso em que os docs já tenham sido inseridos
                if "recebida" in erro_acesso or "finalizado" in erro_acesso.lower():
                    print(erro_acesso)
                    self.data.atualizar_status(contrato, erro_acesso)
                    continue

                # caso em que o código de acesso está incorreto -> aguardar, pular.
                elif 'incorreto' in erro_acesso or 'Favor aguardar a análise da documentação' in erro_acesso :
                    self.data.atualizar_status(contrato, erro_acesso)
                    continue

                elif 'expirado' in erro_acesso or "expirada" in erro_acesso:
                    print(erro_acesso)
                    self.data.atualizar_status(contrato, erro_acesso)

                elif 'aplicação' in erro_acesso:
                    print("Tentando outro código")
                    for codigo in datas_codigos.values():
                        print(codigo)
                        self.auto.acessar_portal(codigo)
                        erro_acesso = self.auto.verificar_erros_acesso_portal()

                        if not erro_acesso:
                            break

                # outros erros nao previstos
                elif erro_acesso:
                    print(f"ERRO: {erro_acesso.upper()}")
                    time.sleep(5)
                    continue
                # documentos anexados e enviados com sucesso
                dbg.debugger()
                print(documentos["link_log_final"])
                numero_protocolo: str = self.auto.anexar_documentos(documentos["link_log_final"][0])
                self.data.atualizar_status(contrato, "Contrato enviado para checagem no banco")
                print(f"Documentos do contrato {contrato[2]} anexados com sucesso.")

            return True

        except Exception as e:
            dbg.exception(e)

    def anexar_documentos_ib_consig_portabilidade(self):

        self.chrome_driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
        while 'principal/fsconsignataria' not in self.chrome_driver.current_url.lower():
            self.ib_login()
            self.chrome_driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')

        try:
            fila_contratos: list = self.data.obter_contratos_para_anexar_ibconsig()

            if not fila_contratos:
                return False

            for contrato in fila_contratos[1:]:
                if(contrato[6] == 'REFINANCIAMENTO DA PORTABILIDADE'):
                    novo_contrato = [contrato[5],contrato[4],contrato[1],contrato[0]]
                    self.anexar_documentos_contrato_no_portal([novo_contrato], True)
                else:
                    print('<<<<<<<<< INCIANDO CONTRATO >>>>>>>>>')
                    print(f"Código do contrato: {contrato[1]}")
                    print('Apagando arquivos na pasta...')
                    deleta_todos_arquivos(self.path)

                    self.chrome_driver.get(self.urls["ib_consig"] + str(contrato[2]))  # contrato[0]=ADE

                    executar_script_pop_up(self.chrome_driver)

                    self.act.clicar_elemento('//*[@id="registro"]/tbody/tr/td[13]/table/tbody/tr/td[10]/a/img', By.XPATH)
                    time.sleep(2)
                    self.act.fechar_janela()
                    self.act.retornar_janela_principal()
                    self.act.clicar_elemento('//*[@id="registro"]/tbody/tr/td[13]/table/tbody/tr/td[10]/a/img', By.XPATH)
                    time.sleep(2)
                    self.act.trocar_janela()
                    self.act.trocar_frame_seletor('#_idFrame')

                    self.loc_select_id = '//*[@id="j_idt35:j_idt36:selectTipoDocumento"]'
                    self.loc_select_id_2 = '//*[@id="j_idt30:j_idt31:selectTipoDocumento"]'

                    quantidade_uploads = self.act.quantidade_elemento('.upload')

                    if(quantidade_uploads == 0):
                        try:
                            mensagem_erro = self.act.obter_texto('.error_message')
                            if(r'Erro inesperado' in mensagem_erro
                                or r'Erro' in mensagem_erro):
                                print('Erro tentando novamente...')

                            elif(r'Documentos sem pendências' in mensagem_erro):
                                print('Documentos já anexados...')                
                                self.act.fechar_janela()
                                time.sleep(2)
                                self.act.retornar_janela_principal()
                                self.data.atualizar_status_portabilidade(contrato, "Documentação da portabilidade anexada no banco.")
                            continue
                        except:
                            self.act.fechar_janela()
                            self.act.retornar_janela_principal()
                            print('Abrindo modal novamente...')
                            self.chrome_driver.execute_script(""" openModalIn100('%s', '*****') """ % contrato[2]) 
                            self.act.trocar_janela()
                            self.act.trocar_frame_seletor('#_idFrame')
                    
                    if(quantidade_uploads > 0):
                        print('Em api de documentos...')
                        documentos: dict = self.data.get_request_documentos_portabilidade(contrato)
                        if(documentos['tipo'] == 'success'):
                            self.anexar_documentos_unicos_portabilidade(documentos)    
                            if(quantidade_uploads > 1):
                                for i in range(quantidade_uploads -1):
                                    print('Abrindo modal para anexar novamente o segundo arquivo...')
                                    self.chrome_driver.execute_script(""" openModalIn100('%s', '*****') """ % contrato[2]) 
                                    time.sleep(2)
                                    self.act.trocar_janela()
                                    self.act.trocar_frame_seletor('#_idFrame')
                                    self.anexar_documentos_unicos_portabilidade(documentos)
                        else:
                            self.act.fechar_janela()
                            time.sleep(2)
                            self.act.retornar_janela_principal()
                            continue
                    # else:
                    #     print('Em api de documentos...')
                    #     documentos: dict = self.data.get_request_documentos_portabilidade(contrato)

                    #     if(documentos['tipo'] == 'success'): 
                    #         #anexa ID           
                    #         tipo_identidade = documentos['tipoDocumento']
                    #         try:
                    #             self.act.select_drop_down(self.loc_select_id, tipo_identidade, By.XPATH)
                    #         except:
                    #             self.act.select_drop_down(self.loc_select_id_2, tipo_identidade, By.XPATH)
                    #         caminho_arquivo_identidade = self.path+'\\identidade.jpg'
                    #         try: 
                    #             self.auto.anexar_documentos_portabilidade(base64.b64decode(documentos['identidade']),caminho_arquivo_identidade, '#j_idt30\\:j_idt31\\:fileUpload')   
                    #         except:
                    #             self.auto.anexar_documentos_portabilidade(base64.b64decode(documentos['identidade']),caminho_arquivo_identidade, '#j_idt35\\:j_idt36\\:fileUpload')

                    #         try:
                    #             self.driver.execute_script("""$('.last').each(function(){this.children[1].click()})""")
                    #         except:
                    #             pass

                    #         self.auto.esperar_mensagem('Arquivo enviado com sucesso.','.info_message',5)
                            
                    #         #anexa TERMO
                    #         caminho_arquivo_aceite = self.path+'\\prints.jpg'
                    #         try:
                    #             self.auto.anexar_documentos_portabilidade(base64.b64decode(documentos['prints']) , caminho_arquivo_aceite, '#j_idt62\\:j_idt36\\:fileUpload')
                    #         except:
                    #             self.auto.anexar_documentos_portabilidade(base64.b64decode(documentos['prints']) , caminho_arquivo_aceite, '#j_idt48\\:j_idt31\\:fileUpload')
                            
                    #         try:
                    #             self.driver.execute_script("""$('.last').each(function(){this.children[0].click()})""")
                    #         except:
                    #             pass

                    #         self.auto.esperar_mensagem('Arquivo enviado com sucesso.','.info_message',5)
                    #     else:
                    #         self.act.fechar_janela()
                    #         self.act.retornar_janela_principal()
                    #         continue         

                    #     self.act.clicar_elemento('#enviarEtapa')

                    print('Apagando arquivos na pasta...')
                    deleta_todos_arquivos(self.path)
                    
                    #self.act.fechar_janela()
                    #self.act.retornar_janela_principal()

                    self.data.atualizar_status_portabilidade(contrato, "Documentação da portabilidade anexada no banco.")
                    print('<<<<<<<<< PROCESSO FINALIZADO >>>>>>>>>')
            return True

        except Exception as e:
            dbg.exception(e)

    def anexar_documentos_unicos_portabilidade(self,documentos):
        tipo_primeiro_upload = self.act.obter_texto('.first')
        if 'Termo de Portabilidade Ativa' in tipo_primeiro_upload:
            nome = 'prints.jpg'
            documento = documentos['prints']
        elif 'Cédula de Crédito Bancário Consignado' in tipo_primeiro_upload:
            nome = 'ccb.pdf'
            documento = documentos['ccb']   
        elif 'Termo de Autorização INSS' in tipo_primeiro_upload:
            nome = 'identidade.jpg'
            documento = documentos['identidade']  
        elif 'Documento de Identificação' in tipo_primeiro_upload:
            tipo_identidade = documentos['tipoDocumento']
            nome = 'identidade.jpg'
            documento = documentos['identidade']
            try:
                self.act.select_drop_down(self.loc_select_id, tipo_identidade, By.XPATH)
            except:
                self.act.select_drop_down(self.loc_select_id_2, tipo_identidade, By.XPATH)
            
        caminho_arquivo = self.path+'\\'+nome

        try:   
            self.auto.anexar_documentos_portabilidade(base64.b64decode(documento),caminho_arquivo, '#j_idt35\\:j_idt36\\:fileUpload') 
        except:
            self.auto.anexar_documentos_portabilidade(base64.b64decode(documento),caminho_arquivo, '#j_idt30\\:j_idt31\\:fileUpload')   
         
        try:                   
            self.driver.execute_script("""$('.last').each(function(){console.log(this.children[1].click())})""")
        except:
            pass
        self.auto.esperar_mensagem('Arquivo enviado com sucesso.','.info_message',5)
        self.act.fechar_janela()
        self.act.retornar_janela_principal()

    ###########
    def verificar_nova_margem_restricao(self):
        self.driver.get("https://www.ibconsigweb.com.br/ajusteRestricoes.do?method=prepare")
        while True:
            try:
                carregou = self.act.obter_texto('//*[@id="Table_02"]/tbody/tr/td/form/table/tbody/tr[1]/td[1]/font/strong', By.XPATH)
                self.ib_login()
            except:
                break

        response = APIDataSource().get_request('propostas_em_pedente_ibconsig')
        todas_propostas = json.loads(response.text)
        for proposta in todas_propostas[1:]:
            print(proposta)
            self.driver.get("https://www.ibconsigweb.com.br/ajusteRestricoes.do?method=prepare")
            #pdb.set_trace()
            # ADE
            self.act.enviar_texto('//*[@id="txt"]', proposta[0], By.XPATH)
            # Pesquisar
            self.act.clicar_elemento('//*[@id="submitButton"]', By.XPATH)
            # Editar
            self.act.clicar_elemento('//*[@id="rs"]/tbody/tr/td[10]/table/tbody/tr/td[1]/a', By.XPATH)
            # pegar dados
            margemDisponivel = float(self.act.obter_texto('//*[@id="formDataPrev"]/table/tbody/tr[9]/td[2]', By.XPATH).replace(',', '.').replace(' ', ''))
            # CPF
            #self.act.enviar_texto('//*[@id="cpf"]', propostas[1], By.XPATH)
            # POST
            payload = {"codigoCon": proposta[2], "margemDisponivel": margemDisponivel}
            response = APIDataSource().post_request_v2("enviar-margem-disponivel-ibconsig", payload)
            print(response)
        print("NÂO TEM !!!")
    ###########


    def clicar_enviar(self):
        for i in range(2, 12, 2): # Enviar
            try:
                self.act.clicar_elemento(f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[5]/a', metodo=By.XPATH)
            except:
                pass
            time.sleep(3)
            try:
                if self.act.obter_atributo(f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/input', 'disabled', By.XPATH) == True:
                    continue
            except:
                pass

    def opcoes_disponiveis(self, arquivos):
        for i in range(2, 12, 2):
            try:
                texto = self.act.obter_texto(f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/span', metodo=By.XPATH)
                print(f'\033[;92m{texto}\033[m')
                if "Cédula" in texto or "Foto" in texto: # Outros
                    self.auto.anexar_documentos_portabilidade(base64.b64decode(arquivos['outros']), "/home/gustavo/Desktop/automacao-python/sites/ibConsig/ib_analise_de_fraude/arquivos/outros.jpg", 
                                    f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/input', tipo='xpath') 
                elif "INSS" in texto: # TermoIn100
                    self.auto.anexar_documentos_portabilidade(base64.b64decode(arquivos['termoIn100']), "//home/gustavo/Desktop/automacao-python/sites/ibConsig/ib_analise_de_fraude/arquivos/termoIn100.jpg", 
                                    f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/input', tipo='xpath')
                elif "Identificação" in texto: # Identidade 
                    self.auto.anexar_documentos_portabilidade(base64.b64decode(arquivos['identidade']), "/home/gustavo/Desktop/automacao-python/sites/ibConsig/ib_analise_de_fraude/arquivos/identidade.jpg", 
                                    f'/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/input', tipo='xpath') 
                time.sleep(1)
            except TimeoutException:
                pass
        self.clicar_enviar()


    def resolver_tela_vazia(self):
        self.act.fechar_janela()
        self.act.retornar_janela_principal()
        self.chrome_driver.execute_script(""" openModalIn100('%s', '*****') """ % self.ade_contrato)
        self.act.trocar_janela()
        self.act.trocar_frame_referencia("_idFrame")
    

    def escolher_tipo_documento(self, arquivos):
        time.sleep(4)
        try:
            self.act.select_drop_down('//*[@id="j_idt35:j_idt36:selectTipoDocumento"]', arquivos['tipoDocumento'], By.XPATH)
        except:
            try:
                self.act.select_drop_down('//*[@id="j_idt30:j_idt31:selectTipoDocumento"]', arquivos['tipoDocumento'], By.XPATH)
            except:
                try:
                    teste_msg_erro = self.act.obter_texto('/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[2]/td[1]/span', metodo=By.XPATH)
                    print('Test msg error -->', teste_msg_erro)
                except:
                    print('vai retornar falso no escolher tipo documento')
                    #pdb.set_trace()
                    return False
                try:
                    self.act.obter_texto('//*[@id="panelGroupBase"]/table[2]/caption', metodo=By.XPATH)
                except TimeoutException:
                    print("Vai resolver tela vazia no escolher tipo documento")
                    self.resolver_tela_vazia()
                    self.escolher_tipo_documento(arquivos)

    def anexar_documentos_fluxo100(self):
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
        # verificar se usuário está logado, caso não, executar login
        while 'index' in self.chrome_driver.current_url.lower():
            print("Carregando cookies", self.cookies_path)
            self.ib_login()
        
        response = APIDataSource().get_request('propostas_In100')
        response = json.loads(response.text)
        if response[0]['mensagem'] == 'Nada a atualizar.':
            print('Não tem nada')
            return
    

        for proposta in response[1:]:
            contrato = []
            contrato.append(proposta[0]) # Ade
            contrato.append(proposta[1]) # Codigo_Con
            #contrato['cpf'] = proposta[2] # Cpf
            self.ade_contrato = contrato[0]

            # Get dos documentos relacionados a proposta
            response = APIDataSource().get_request('arquivos_proposta_in100', cpf=proposta[2], ade=proposta[0])
            arquivos = json.loads(response.text)
            # contrato é o for contrato in propostas:
            # Para ver qual o self.driver atual --> Error eb already close
            
            self.driver.get(f"https://www.ibconsigweb.com.br/situacaoContrato.do?method=listar&situacaoContratoFiltroForm.numeroAde={contrato[0]}")
            # habilitar clicar no botão para anexar arquivos
            executar_script_pop_up(self.chrome_driver)
            # for começa aqui
            self.chrome_driver.execute_script(""" openModalIn100('%s', '*****') """ % self.ade_contrato)
            # Muda foco para próxima pagina
            pagina_principal = self.driver.current_window_handle
            if len(self.driver.window_handles) > 1:
                for pagina in self.driver.window_handles:
                    if pagina != pagina_principal:
                        self.driver.switch_to_window(pagina)
            time.sleep(3)
            self.resolver_tela_vazia()
            try:
                time.sleep(2)
                texto_alerta = self.act.obter_texto('//*[@id="global-msg"]/li', metodo=By.XPATH)
                if "sem pendências" in texto_alerta:
                    self.data.atualizar_status_In100(contrato, 'Documentação da in100 já anexada no banco.')
                    self.driver.close()
                    continue
            except TimeoutException:
                pass

            if(arquivos['tipo'] == "danger"):
                self.data.atualizar_status_In100(contrato, 'Documentação não exite para anexar no banco.')
                pagina_principal = self.driver.current_window_handle
                if len(self.driver.window_handles) > 1:
                    for pagina in self.driver.window_handles:
                        if pagina != pagina_principal:
                            self.driver.switch_to_window(pagina)
                pagina_principal.close()
                continue
            
            print(f"\033[;78{arquivos.keys()}\033[m")
            print(f"\033[;78{arquivos['tipoDocumento']}\033[m")
            time.sleep(5)

            if self.escolher_tipo_documento(arquivos) == False:
                self.data.atualizar_status_In100(contrato, 'Documentação da in100 já anexada no banco.')
                pagina_principal = self.driver.current_window_handle
                if len(self.driver.window_handles) > 1:
                    for pagina in self.driver.window_handles:
                        if pagina != pagina_principal:
                            self.driver.switch_to_window(pagina)
                pagina_principal.close()
                self.driver.close()
                continue
            
            self.opcoes_disponiveis(arquivos)
            time.sleep(2)
            # Confirmar
            self.act.clicar_elemento('//*[@id="enviarEtapa"]/a', metodo=By.XPATH)
            if self.act.obter_texto('//*[@id="global-msg"]/li', metodo=By.XPATH) != 'Processo finalizado com sucesso.':
                print('caiu no if')
                self.resolver_tela_vazia()
                self.escolher_tipo_documento(arquivos)
                self.opcoes_disponiveis(arquivos)
            
            self.data.atualizar_status_In100(contrato, 'Documentação da in100 anexada no banco.')
            self.driver.close()
            for pagina in self.driver.window_handles:
                self.driver.switch_to_window(pagina)
        

if __name__ == "__main__":
    PortalAnaliseDocsMan.iniciar_horario_comercial()