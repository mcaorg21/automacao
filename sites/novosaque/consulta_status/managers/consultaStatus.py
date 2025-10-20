from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.novosaque.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

import pyperclip

HORARIO_COMERCIAL = 7, 20


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "consulta": "https://sistema.novosaque.com.br/admin/contracts"
        }
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome):

        run = ConsultaStatus(driver)
        try:
            run.consultar_status_proposta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_status_proposta(self):     

        self.verificar_loading()       
        print('Inciando sincronização...')
        status_a_consultar = self.dados.get_ades()[1:]

        #self.chrome_driver.get(self.urls["consulta"])

        #print("Atualizando status do robô.")
        #self.dados.uconecte.atualizar_status_robo(7)

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")
            
            proposta = ['713499', '01868620085', '934492', 90, 'Link Enviado', 'http://sistema.novosaque.com.br/payment/5e341fe00685fe3ef05a6f58287c84da61561a9d', 'Cecilia Aquino Micheli']

            try:
                
                print("Consultando proposta:", proposta)

                ade, cpf_bd = proposta[0], proposta[1]
                cod_con = proposta[2]
                tempo_atualizacao = int(proposta[3]) 
                observacao = proposta[4]
                linkAssinaturaDigital = proposta[5] 
                nome_cliente = proposta[6] 
                busca_reiniciada = False
                dados_consulta = {}
                
                if((ade is None or ade == 0 or ade == '0')):
                    dados_consulta['ade'] = ade
                    dados_consulta["codigoCon"] = cod_con
                    dados_consulta['statusPropostaBanco'] = "ERRO SINCRONIZACAO"
                    dados_consulta['observacaoDetalhadaBanco']  = "PROPOSTA NAO POSSUI ADE"
                    self.dados.post_dados_consultados(dados_consulta)   
                    continue 
                
                #ade="9842"
                #cpf="04763519603"
                #cod_con = "521329"

                #self.act.press_backspace('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]/input', 13, By.XPATH, 0,True)
                #self.act.enviar_texto('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]/input', cpf, By.XPATH, clear = True)
                #self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[2]/button', By.XPATH)

                #cpf_formatado = formatar_cpf_sem_caracteres(cpf_bd)                
                #self.driver.get(f'https://nsaque.ultragate.com.br/admin/contracts?cpf={cpf_formatado}')
            
                self.driver.get(f'https://sistema.novosaque.com.br/admin/contracts')
                self.verificar_loading()

                #self.act.enviar_texto('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]/input',ade, By.XPATH)
                
                #self.act.enviar_texto('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]/input',cpf_bd, By.XPATH)
                #self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[2]/button', By.XPATH)
                #self.verificar_loading(2)

                # while self.act.quantidade_elemento('//*[@id="table-responsive-custom"]/tbody/tr', By.XPATH) == 1 and busca_reiniciada == False:
                    
                #     try:
                #         ade_primeira = self.act.obter_texto(f'//*[@id="table-responsive-custom"]/tbody/tr[1]/th/div/div/span', By.XPATH)
                #     except:
                #         print('Procurando ade pelo link')
                #         self.act.clicar_elemento('//*[@id="table-responsive-custom"]/tbody/tr[1]/td[1]/div/a', By.XPATH)

                #         link_ade = self.act.obter_atributo('/html/body/div[1]/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[1]/div/div/a','href',By.XPATH)
                #         ade_primeira = re.findall('\\d+',link_ade)[0]

                #     if(ade_primeira == ade):
                #         busca_reiniciada = True
                #     else:
                #         busca_reiniciada = False
                #         print('Busca ANTERIOR ainda não reinciada. Aguardando...')
                #         self.aguardar_consulta(10)
                #         self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div[2]/button', By.XPATH)  

                #quantidade_propostas = self.act.quantidade_elemento('//*[@id="table-responsive-custom"]/tbody/tr', By.XPATH)
                try:
                    quantidade_propostas = 0
                    if(quantidade_propostas == 0):                    
                        #self.driver.get('https://sistema.novosaque.com.br/admin/contracts')
                        self.act.clicar_elemento('/html/body/div/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/button[3]', By.XPATH)
                        #self.act.enviar_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div/div/div[3]/input', nome_cliente.split(' ')[0], By.XPATH)
                        self.act.enviar_texto('//*[@id="id"]', ade, By.XPATH)
                        self.act.clicar_elemento('/html/body/div[2]/div/div[1]/div/div/div[3]/button[3]', By.XPATH)
                        self.verificar_loading()

                        self.act.clicar_elemento('//*[@id="table-responsive-custom"]/tbody/tr[1]/td[1]/div/a', By.XPATH)

                        link_ade = self.act.obter_atributo('/html/body/div[1]/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[1]/div/div/a','href',By.XPATH)
                        ade_primeira = re.findall('\\d+',link_ade)[0]

                        quantidade_propostas = self.act.quantidade_elemento('//*[@id="table-responsive-custom"]/tbody/tr', By.XPATH)

                    #ajuste 
                    for i in range(1,quantidade_propostas+1):
                        
                        try:
                            
                            print('Procurando ade pelo link')   
                            try:               
                                link_ade = self.act.obter_atributo(f'/html/body/div[1]/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[{i}]/td[1]/div/div/a','href',By.XPATH)
                            except:
                                self.act.clicar_elemento(f'/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[{i}]/td[1]/div/a', By.XPATH)
                                link_ade = self.act.obter_atributo(f'/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[{i}]/td[1]/div/div/a','href',By.XPATH)
                                pass
                            ade_sistema = re.findall('\\d+',link_ade)[0]
    
                        except:                        
                            ade_sistema = self.act.obter_texto(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/th/div/div/span', By.XPATH)

                        if(ade_sistema == ade):
                            self.act.clicar_elemento(f'/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[3]', By.XPATH)
                            print('Consultando ade:' + ade)
                            self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/a', By.XPATH)
                            try:
                                id = self.act.obter_texto(f'//*[@id="table-responsive-custom"]/tbody/tr/td[2]', By.XPATH)
                            except:
                                id = ""
                                pass
                            
                            try:
                                if(id == "-" or id == ""):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/div/button[3]', By.XPATH)
                                else:
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[4]', By.XPATH) 
                            except:
                                self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/div/button[2]', By.XPATH)
                                pass
    
                            self.aguardar_consulta(2)
                            
                            try:
                                try:
                                    dados_consulta['statusPropostaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[2]', By.XPATH).replace('\n',' ')
                                    dados_consulta['observacaoDetalhadaBanco']  = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                    
                                except:
                                    dados_consulta['statusPropostaBanco'] = self.act.obter_texto('/html/body/div[3]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[2]', By.XPATH).replace('\n',' ')
                                    dados_consulta['observacaoDetalhadaBanco']  = self.act.obter_texto('/html/body/div[3]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[4]', By.XPATH)
                                    pass
                            except:
                                dados_consulta['statusPropostaBanco'] = 'Status não encontrado'
                                dados_consulta['observacaoDetalhadaBanco']  = 'Sem status no sistema'
                                pass

                            
                            try:
                                self.act.clicar_elemento('/html/body/div[2]/div/div[1]/div/div/div[1]/button/span', By.XPATH)      
                            except:
                                self.act.clicar_elemento('/html/body/div[3]/div/div[1]/div/div/div[3]/button', By.XPATH)
                                pass

                            #adicao de condicao para retornar pago
                            if(id != "-" or id != ""):
                                try:
                                    dados_consulta['statusPropostaBanco'] = self.act.obter_texto('/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr/td[7]/div/div', By.XPATH).replace('\n',' ')
                                    if('Comissão Paga' in dados_consulta['statusPropostaBanco']):
                                        dados_consulta['statusPropostaBanco'] = 'Pago'
                                        dados_consulta['observacaoDetalhadaBanco']  = 'Comissão Paga'
                                except:
                                    pass

                            #dados_consulta['observacaoDetalhadaBanco'] = ''
                            dados_consulta['linkAssinaturaDigital'] = linkAssinaturaDigital

                            if not linkAssinaturaDigital:
                                while dados_consulta['linkAssinaturaDigital'] is None:
                                    dados_consulta['linkAssinaturaDigital'] = self.copia_link(i) 
                                    print('Tentando encontrar o link de assinatura...')   
                                    self.aguardar_consulta(2)

                            
                            while dados_consulta['observacaoDetalhadaBanco'] == '':
                                #abre menu 
                                if(quantidade_propostas > 1):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/a', By.XPATH)

                                    if(tempo_atualizacao >=  2 and dados_consulta['statusPropostaBanco'] == 'Link Enviado' or dados_consulta['statusPropostaBanco'] == '' or 'Reenvie o SMS por favor para o número' in observacao and dados_consulta['statusPropostaBanco'] == 'Link Enviado'):
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/div/button[1]', By.XPATH)
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/a', By.XPATH)                              

                                else:  
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/a', By.XPATH)

                                    if(tempo_atualizacao >= 3 and dados_consulta['statusPropostaBanco'] == 'Link Enviado' or 'Reenvie o SMS por favor para o número' in observacao and dados_consulta['statusPropostaBanco'] == 'Link Enviado'):
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[1]', By.XPATH)
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/a', By.XPATH)     
                                    
                                self.aguardar_consulta()      

                                if(dados_consulta['statusPropostaBanco'] == 'Negado' or dados_consulta['statusPropostaBanco'] == 'Cancelado'):
                                        
                                    if(quantidade_propostas > 1):
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[{i}]/div/div/button[2]/span', By.XPATH) 
                                        
                                    else:
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[2]/span', By.XPATH) 
                                    
                                    #busca pelas informacoes no modal
                                    #pega dados secundarios     
                                    if(dados_consulta['statusPropostaBanco'] == 'Cancelado'):
                                        try:
                                            dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                        except:                                                 
                                            dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[5]', By.XPATH)
                                    else:                                    
                                        dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[8]', By.XPATH)
                                        dados_consulta['observacaoDetalhadaBanco'] += ' - ' + self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[9]',By.XPATH)

                                elif(dados_consulta['statusPropostaBanco'] == 'Link Enviado' or dados_consulta['statusPropostaBanco'] == ''):
                                    
                                    if(quantidade_propostas > 1):                                    
                                        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/div/button[1]', By.XPATH)                                     
                                    else:
                                        try:
                                            self.act.clicar_elemento('//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[1]', By.XPATH)
                                        except:
                                            pass                                   
                                    try:
                                        dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[4]', By.XPATH)       
                                    except:
                                        dados_consulta['observacaoDetalhadaBanco'] = 'Aguardando assinatura do contrato'
                                        pass

                                elif(dados_consulta['statusPropostaBanco'] == 'Aguardando Assinatura'): 

                                    #busca pelas informacoes no modal  
                                    #pega dados secundarios
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[3]', By.XPATH)
                                    #dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[7]', By.XPATH) 
                                    #dados_consulta['observacaoDetalhadaBanco'] += ' - ' + self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr/td[8]',By.XPATH)                 
                                    self.aguardar_consulta()
                                elif(dados_consulta['statusPropostaBanco'] == 'Contratos Assinados - Aguardando Pagamento'):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[4]', By.XPATH)
                                    dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                elif(dados_consulta['statusPropostaBanco'] == 'Contratos Pagos'):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[4]', By.XPATH)
                                    dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                elif(dados_consulta['statusPropostaBanco'] == 'Pendente de Documentos'):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[4]', By.XPATH)
                                    try:
                                        dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                    except:
                                        dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[3]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                elif('Aguardando Pagamento' in dados_consulta['statusPropostaBanco']):
                                    self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr/td[1]/div/div/button[4]', By.XPATH)
                                    dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[4]', By.XPATH)
                                else:
                                    print('Classificar acao...')
                                    dados_consulta['observacaoDetalhadaBanco'] = 'Classificar Status: ' + dados_consulta['statusPropostaBanco']
                                
                                #fecha menu
                                try:
                                    self.act.clicar_elemento('/html/body/div[2]/div/div[1]/div/div/div[1]/button/span', By.XPATH)                                                              
                                except:
                                    pass 

                                try:
                                    self.act.clicar_elemento('/html/body/div[3]/div/div[1]/div/div/div[3]/button', By.XPATH) 
                                except:
                                    pass
                                    
                                    

                                print('Fechando a consulta...')
                                break
                        
                        if(ade_sistema != ade):
                            self.act.clicar_elemento(f'/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[3]', By.XPATH)
                            continue

                        if(ade_sistema == ade):
                            break
                    
                    if(ade_sistema == ade and 'statusPropostaBanco' in dados_consulta):
                        dados_consulta['ade'] = ade
                        dados_consulta["codigoCon"] = cod_con

                        print(dados_consulta)       
                        self.dados.post_dados_consultados(dados_consulta)    

                    else:
                        print('Pulando consulta...')                            

                except:
                    
                    dados_consulta['ade'] = ade
                    dados_consulta["codigoCon"] = cod_con
                    dados_consulta['statusPropostaBanco'] = "ERRO SINCRONIZACAO"
                    dados_consulta['observacaoDetalhadaBanco']  = "PROPOSTA NAO ENCONTRADA"
                    self.dados.post_dados_consultados(dados_consulta)   
                    continue 
                        
            except Exception as e:
                print(e)

                # self.dados.api_registrar_log_robo(
                #     log=f"ERRO: {e}",
                #     status=0
                # )

                dados_consulta['ade'] = ade
                dados_consulta["codigoCon"] = cod_con
                dados_consulta["statusPropostaBanco"] = 'novo_status_classificar_' + dados_consulta['statusPropostaBanco']
                dados_consulta['observacaoDetalhadaBanco'] = ''

                print(dados_consulta)         
                self.dados.post_dados_consultados(dados_consulta)  
                
                continue

        #self.dados.data_source.atualizar_sincronizacao()
        #self.dados.api_registrar_log_robo(log="Sincronizado com sucesso.",status=2)


    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def copia_link(self, i = 1):

        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/a', By.XPATH)

        self.act.clicar_elemento(f'//*[@id="table-responsive-custom"]/tbody/tr[{i}]/td[1]/div/div/button[2]', By.XPATH)
        link = pyperclip.paste()

        return link


    def verificar_loading(self, interacoes=300, aguardar = False):
        while (self.act.quantidade_elemento('//*[@id="modal-root"]/div/div', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(2)
            interacoes -= 1
            if(interacoes < -35):

                raise Exception('Tempo excedido...')