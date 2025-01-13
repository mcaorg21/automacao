from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from datetime import date, datetime


from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.crefisa.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

from sites.crefisa.libs.FormLogin import FormLogin
from dados.database.queries.query_dados_robos import query_login_pass_robo


HORARIO_COMERCIAL = 8, 20


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "consulta": "https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp"
        }
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.id_robo = '691'
        self.usuario = '50801.06050694680'

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

        #self.verificar_loading()       
        print('Inciando sincronização...')
        status_a_consultar = self.dados.get_ades()[1:]

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        #para testes
        #status_a_consultar = [['508020158898', '02829094271  ', '719774','','','','2024-11-25']]

        self.chrome_driver.get(self.urls["consulta"])

        try:
            self.act.clicar_elemento('/html/body/div[2]/div/a', By.XPATH)
        except:
            pass
        
        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")

            try:
            
                print("Consultando proposta:", proposta)

                ade, cpf_bd = proposta[0], proposta[1]
                cod_con = proposta[2]
                self.data_proposta = proposta[6]
                self.dados_consulta = {}

                self.dados_consulta['ade'] = ade
                self.dados_consulta["codigoCon"] = cod_con

                print(self.dados_consulta)        

                self.limpar_busca()

                self.div = div = '5'
                self.div_segunda = div_segunda = '7'

                while(self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody', By.XPATH) == 0):
                    div = int(div)
                    div += 1

                    if div > 100:
                        print('Erro ao encontrar div correta...')
                        input()

                    self.div = div = str(div)


                self.buscar_contrato(cpf_bd, "cpf", False)

                self.dados_consulta['novaAde'] = ""

                self.aguardar_consulta()
                
                linhas_tr = self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/table/tbody/tr', By.XPATH)
                
                if(linhas_tr > 2):
                    linhas_tr += 2

                #ajuste de linhas
                if(linhas_tr == 0):
                    linhas_tr = 3

                
                contrato_aprovado = False
                self.contrato_aprovado = False

                if(linhas_tr > 4):
                    self.driver.execute_script("document.body.style.zoom='60%'")

                if self.act.quantidade_elemento('//*[@id="divMsgErro"]', By.XPATH) == 1:

                    mensagem = self.act.obter_texto('//*[@id="divMsgErro"]', By.XPATH)

                    if('Nenhum resultado encontrado' in mensagem):
                        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX NENHUM CONTRATO ENCONTRATO XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                        self.dados_consulta["statusPropostaBanco"] = "PROVAVEL EXPIRADA"
                        self.dados_consulta['observacaoDetalhadaBanco'] = ""
                        self.dados_consulta['statusSecundario'] = "Expirada"
                        self.dados.post_dados_consultados(self.dados_consulta) 
                        continue

                print('Verificando se possui contrato aprovado...')
                atualiza_ade = False

                # for i in range(1,linhas_tr,2):  

                i = self.verificar_tr_ade(ade, True)

                if(self.retornar_consulta_aprovado == True):
                    i = self.verificar_tr_ade(ade, True)

                    if(self.retornar_consulta_aprovado == True):
                        print('Atualizando pela segunda vez...')
                        i = self.verificar_tr_ade(ade, True)

                texto_aprovada = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]/span', By.XPATH)
                numero_contrato = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[2]', By.XPATH).strip()

                texto_nova_proposta = ""
                try:
                    texto_nova_proposta = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[2]/span', By.XPATH)
                except:
                    pass

                if(self.contrato_aprovado == True):

                    try:
                        self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div//table/tbody/tr[{i}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                        self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()

                    except:
                        self.dados_consulta["statusPropostaBanco"] = None
                    pass

                    if self.dados_consulta["statusPropostaBanco"] == 'PAGO' or self.dados_consulta['observacaoDetalhadaBanco'] == 'PENDENTE TRANSF. PIX' or ('Aprovada(Nova Proposta' not in texto_nova_proposta and self.dados_consulta["statusPropostaBanco"] == 'APROVADO'):

                        try:
                            data_proposta = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[3]/span', By.XPATH).split(' ')[1]
                                
                            data_proposta_sistema = datetime.strptime(data_proposta, '%d/%m/%Y')
                            data_proposta_crm = datetime.strptime(self.data_proposta, '%Y-%m-%d')

                            if data_proposta_sistema >= data_proposta_crm:
                                atualiza_ade = True
                                contrato_aprovado = True
                                extrair_valor = lambda texto: float(re.search(r'Liberado: R\$ ([\d.,]+)', texto).group(1).replace('.', '').replace(',', '.')) 
                                self.dados_consulta['valorContrato'] = extrair_valor(self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div', By.XPATH))
                                self.dados_consulta['novaAde'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[1]', By.XPATH)
                                self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                                self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                                self.dados_consulta['statusSecundario'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH).strip()
                                indice = i

                        except:
                            pass

                
                elif self.contrato_aprovado == False:

                    i = self.verificar_tr_ade(ade)

                    if 'Aprovada(Nova Proposta' in texto_nova_proposta:
                        self.dados_consulta['novaAde'] = re.findall(r'\d+', texto_nova_proposta)[0]
                        extrair_valor = lambda texto: float(re.search(r'Liberado: R\$ ([\d.,]+)', texto).group(1).replace('.', '').replace(',', '.')) 
                        self.dados_consulta['valorContrato'] = extrair_valor(self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div', By.XPATH))
                        atualiza_ade = True
                    
                if(atualiza_ade == False): 
                    
                    if contrato_aprovado == False:

                        i = self.verificar_tr_ade(ade)

                        #for i in range(1,linhas_tr,2):
                        print('Contrato ainda em andamento...')
                        # linha_tr_ade = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[2]', By.XPATH).strip()

                        # if(linha_tr_ade == ""):
                        #     linha_tr_ade = self.act.obter_texto(f'/html/body/div[8]/div[2]/div[7]/div/div/table/tbody/tr[7]/td[4]/div/a[1]', By.XPATH).strip()

                        
                        if self.ade_encontrada == True:
                                print('Achou Contrato de ade igual do sistema...')

                                self.atualizar_contrato(div,i)

                                self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                                self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                                self.dados_consulta['observacaoDetalhadaBanco'] += "\n\n"+self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[2]/span', By.XPATH).strip()
                                self.dados_consulta['statusSecundario'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH).strip()
                                indice = i
                                 
                                if 'CANCELADO' in self.dados_consulta["statusPropostaBanco"] or 'PENDENTE' in self.dados_consulta["statusPropostaBanco"] and 'AGUARDANDO FORMALIZAÇÃO CLIENTE' not in self.dados_consulta["statusSecundario"]:
                                    
                                    #elemento = str(int((i - 1) / 2))
                                    #self.driver.execute_script(f""" document.querySelector("#linkSubStatus_{elemento}").click() """)
                                    
                                    try:
                                        self.act.clicar_elemento(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH)
                                    except:
                                        nova_div = str(int(div) - 1)
                                        self.act.clicar_elemento(f'/html/body/div[{nova_div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH)
                                        pass
                                    
                                    self.verificar_loading_pendente('modal_historico')
                                    self.act.trocar_frame_referencia("iframeHistorico")
                                    self.verificar_loading_pendente('tabela_historico')

                                    historico_atuacao = "\n\n"+self.act.obter_texto('/html/body/div[3]/div/div[2]/div[2]/table/tbody', By.XPATH)

                                    if('PENDENTE' in self.dados_consulta["statusPropostaBanco"]):  

                                        regex = r"(\d{2}/\d{2}/\d{4} às \d{2}:\d{2}:\d{2} PENDENTE)" 
                                        for observacao in historico_atuacao.split('Pendente |'):

                                            obs_sanit = observacao.replace('SUPORTE 2 TECH',"").strip()
                                            array_obs_split = list(filter(lambda x: x != '',re.split(regex, obs_sanit)))

                                            if len(array_obs_split) == 1:
                                                continue

                                            self.dados_consulta['statusSecundario'] += "\n\n"+ obs_sanit 
                                   
                                    else:
                                        self.dados_consulta['statusSecundario'] += "\n\n"+historico_atuacao


                                    #self.dados_consulta['statusSecundario'] += "\n\n"+self.act.obter_texto('//*[@id="modalSubStatus"]/div/div/div[2]/div/div[2]/table/tbody/tr[1]', By.XPATH)
                                    try:
                                        self.act.trocar_frame_referencia("default")
                                        self.act.clicar_elemento(f'/html/body/div[{div}]/div[2]/div[9]/div/div/div[1]/button/span', By.XPATH)

                                    except:
                                        try:
                                            #self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[9]/div/div/div[1]/button/span', By.XPATH)
                                            self.act.clicar_elemento(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/div[1]/button/span', By.XPATH)
                                        except:
                                            pass
                                        pass           

                    if ('PAGO' in self.dados_consulta["statusPropostaBanco"] or 'APROVADO' in self.dados_consulta["statusPropostaBanco"]) and 'EM ANDAMENTO' in self.dados_consulta["statusSecundario"]:
                        self.dados_consulta['statusSecundario'] += " "+self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/table/tbody/tr[{indice}]/td[4]', By.XPATH).replace('\n',"").split("Liberado")[1]

                    if numero_contrato == "" and 'CANCELADO' not in self.dados_consulta["statusPropostaBanco"]:
                        self.atualizar_contrato(div,i)

                        contrato_aprovado = True
                        self.dados_consulta['novaAde'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[1]', By.XPATH)
                        self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                        self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                        self.dados_consulta['statusSecundario'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH).strip()
                        indice = i

                    if numero_contrato == "" and 'CANCELADO' in self.dados_consulta["statusPropostaBanco"]:

                        contrato_aprovado = True
                        self.dados_consulta['novaAde'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[1]', By.XPATH)
                        self.dados_consulta["statusPropostaBanco"] = "VERIFICAR NOVA PROPOSTA"
                        self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                        self.dados_consulta['statusSecundario'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[6]/a', By.XPATH).strip()
                        indice = i
                    
                self.driver.execute_script("document.body.style.zoom='100%'")      


                self.dados.post_dados_consultados(self.dados_consulta)    

                try:       
                    try:   
                        self.act.clicar_elemento('//*[@id="btnExibirFiltro"]', By.XPATH)
                    except:
                        self.act.trocar_frame_referencia("default")
                        self.act.clicar_elemento(f'/html/body', By.XPATH)
                        self.act.clicar_elemento('//*[@id="btnExibirFiltro"]', By.XPATH)
                        
                    self.act.enviar_texto('//*[@id="txtNumeroAde"]', "", By.XPATH)
                    self.act.enviar_texto('//*[@id="txtCpf"]', "", By.XPATH)

                except:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ERRO DE FILTRO XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    time.sleep(30)
                    pass
                
            except Exception as e:
                print(e)

                if self.act.quantidade_elemento('//*[@id="txtUsuario"]', By.XPATH) == 1:
                    print("XX DESLOGADO XX")
                    dados_login = query_login_pass_robo(self.id_robo, self.usuario)
                    login = FormLogin.realizar_login(self.driver,dados_login['login'], dados_login['senha'], dados_login['link'])
                    self.chrome_driver.get(self.urls["consulta"])
                    self.limpar_busca()

                else:

                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ERRO DE SINCRONIZACAO XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

                    # self.dados.api_registrar_log_robo(
                    #     log=f"ERRO: {e}",
                    #     status=0
                    # )

                    self.dados_consulta["statusPropostaBanco"] = "ERRO NA SINCRONIZACAO"
                    self.dados_consulta['observacaoDetalhadaBanco'] = ""
                    self.dados_consulta['statusSecundario'] = e
                    self.dados.post_dados_consultados(self.dados_consulta) 

                    try:          

                        self.act.clicar_elemento('//*[@id="btnExibirFiltro"]', By.XPATH)
                        self.act.enviar_texto('//*[@id="txtNumeroAde"]', "", By.XPATH)
                        self.act.enviar_texto('//*[@id="txtCpf"]', "", By.XPATH)

                    except:
                        try:
                            texto = self.act.obter_texto('//*[@id="swal2-content"]', By.XPATH)
                        except:
                            texto = ""
                            pass

                        if('Erro interno. Experimente fazer login novamente.' in texto):
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX DESLOGANDO XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            self.driver.delete_all_cookies()
                            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/FinalizaSecao.asp')
                            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
                            return
                        
                        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ERRO DE FILTRO XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                        time.sleep(30)
                        return
                        pass

                    #self.chrome_driver.delete_all_cookies()
                    #self.driver.quit()
                    #return

                continue

        #self.dados.data_source.atualizar_sincronizacao()
        #self.dados.api_registrar_log_robo(log="Sincronizado com sucesso.",status=2)

    def verificar_tr_ade(self, ade, procura_aprovado = False):
        i = 1
        linha_tr_ade = 0

        self.contrato_aprovado = False
        self.ade_encontrada = False
        self.retornar_consulta_aprovado = False

        while ade != linha_tr_ade:

            if(procura_aprovado == True):
                linha_tr_ade = '0'
            else:
                linha_tr_ade = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[1]', By.XPATH).strip()
            
            print(ade + " --> " + linha_tr_ade)

            try:
                data_proposta = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[3]/span', By.XPATH).split(' ')[1]
            except:
                i -= 2
                return i


            data_proposta_sistema = datetime.strptime(data_proposta, '%d/%m/%Y')
            data_proposta_crm = datetime.strptime(self.data_proposta, '%Y-%m-%d')
            
            if(data_proposta_sistema >= data_proposta_crm):
                
                statusPropostaBanco = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div//table/tbody/tr[{i}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                observacaoDetalhadaBanco = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{i}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                #se aprovado
                if statusPropostaBanco == 'PAGO' or observacaoDetalhadaBanco == 'PENDENTE TRANSF. PIX' or (statusPropostaBanco == 'APROVADO' and observacaoDetalhadaBanco == 'PAGAMENTO PENDENTE') or (statusPropostaBanco == 'APROVADO' and observacaoDetalhadaBanco == 'APROVADA'):
                    self.contrato_aprovado = True

                    if((statusPropostaBanco == 'APROVADO' and observacaoDetalhadaBanco == 'APROVADA') and 'PAGO' in self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table', By.XPATH)):
                        i += 2
                        continue

                    print('VVVVVVVVVVVVVVVVV CONTRATO APROVADO VVVVVVVVVVVVVVVVV')                
                    if(observacaoDetalhadaBanco == 'PAGAMENTO PENDENTE'):
                        self.atualizar_contrato(self.div,i)
                        self.retornar_consulta_aprovado = True
                        return i

                    i += 0
                    if(procura_aprovado == True and 'PAGAMENTO PENDENTE' not in self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table', By.XPATH)):
                        #linha_tr_ade = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{i}]/td[4]/div/a[1]', By.XPATH).strip()
                        #if(ade == linha_tr_ade):
                        return i
                    #break 

            if(ade != linha_tr_ade):                
                i += 2

            elif(ade == linha_tr_ade):
                print(F'VVVVVVVVVVVV ADE IGUAL ENCONTRADA {ade} VVVVVVVVVVVV')
                self.ade_encontrada = True

                if(procura_aprovado == False):
                    return i

            

        return i

    def limpar_busca(self):
        self.act.clicar_elemento('//*[@id="btnLimparFiltro"]', By.XPATH)

        if(self.driver.find_element(By.CSS_SELECTOR,"#chkNaoExibeCancelado").is_selected() == True):
            self.act.clicar_elemento('//*[@id="chkNaoExibeCancelado"]', By.XPATH)
        
        if(self.driver.find_element(By.CSS_SELECTOR,"#chkNaoExibeRecebido").is_selected() == True):
            self.act.clicar_elemento('//*[@id="chkNaoExibeRecebido"]', By.XPATH)

    def buscar_contrato(self, var, tipo = "ade", clicar_voltar = True):

        if clicar_voltar == True:
            self.act.clicar_elemento('//*[@id="btnExibirFiltro"]', By.XPATH)

        if tipo == "ade":
            self.aguardar_consulta(2)
            self.act.enviar_texto('//*[@id="txtCpf"]', "", By.XPATH)
            self.act.enviar_texto('//*[@id="txtNumeroAde"]', var, By.XPATH)
            

        if tipo == "cpf":
            self.act.enviar_texto('//*[@id="txtNumeroAde"]', "", By.XPATH)
            self.act.enviar_texto('//*[@id="txtCpf"]', var, By.XPATH)


        #self.act.enviar_texto('//*[@id="txtDataInicial"]', self.data_proposta, By.XPATH)
        #self.act.enviar_texto('//*[@id="txtDataFinal"]',  date.today().strftime("%m/%d/%Y"), By.XPATH)
        self.act.clicar_elemento('//*[@id="btnBuscaContratos"]', By.XPATH)

        self.verificar_loading(2)

    def atualizar_contrato(self, div, linha):

                                             
        try:                          
            self.act.clicar_elemento(f'/html/body/div[{div}]/div[2]/div[{div_segunda}]/div/div/table/tbody/tr[{linha}]/td[6]/ul/li[2]/div/span[2]/button', By.XPATH)
        except:
            self.driver.execute_script("""$('#btnAtualizarStatus').click()""")
            pass

        self.verificar_loading()

        self.aguardar_consulta(5)

        try:
            self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
        except:
            print("Aguardando o ok aparecer...")
            self.aguardar_consulta(5)
            self.verificar_loading()
            try: 
                self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
            except:
                pass

        self.driver.execute_script("""$('#btnAtualizarResultado').click()""")
        self.aguardar_consulta(1)

        try:
            self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
        except:
            print("Aguardando o ok aparecer...")
            self.aguardar_consulta(5)
            self.verificar_loading()
            try: 
                self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
            except:
                pass

    def buscar_status(self, indice = "1", div = "6"):
        try:
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
            self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[2]/span', By.XPATH).strip()
            self.dados_consulta['statusSecundario'] = self.dados_consulta['observacaoDetalhadaBanco'].split('|')[0].replace("|","").strip()
                        
        except:
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[6]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
            self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[6]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[2]/span', By.XPATH).strip()
            self.dados_consulta['statusSecundario'] = self.dados_consulta['observacaoDetalhadaBanco'].split('-')[0].replace("|","").strip()

    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def verificar_loading(self, interacoes=300, aguardar = False):
        self.aguardar_consulta(0.8)

        while (self.act.quantidade_elemento(f'/html/body/div[{self.div}]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[10]', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(1)
            interacoes -= 1

            if self.act.quantidade_elemento(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[1]/td[6]/ul/li[5]/span[1]', By.XPATH) == 1:
                return

            if self.act.quantidade_elemento(f'/html/body/div[{self.div}]/div[2]/div[{self.div_segunda}]/div/div/table/tbody/tr[1]/td[6]/ul/li[2]/div/span[1]/b', By.XPATH) == 1:
                return

            if(interacoes < 1):
                return

            if(interacoes < -35):
                self.driver.quit()

    def verificar_loading_pendente(self, tipo_modal, interacoes=30):

        print('Verificando loading...')
        self.aguardar_consulta(0.8)

        if(tipo_modal == "modal_historico"):

            while (self.sh.buscar_quantidade_elemento('#ModalHistoricoAnaliseContrato\\:visible') == 0):
                print('Aguardando Loading modal...')

        else:
            self.act.trocar_frame_referencia("iframeHistorico")

            while (self.sh.buscar_quantidade_elemento('#tableHistoricoAnalise\\:visible') == 0):
                print('Aguardando Loading...' + str(interacoes))
                time.sleep(1)
                interacoes -= 1

                if(interacoes < 1):
                    return

    def get_indice_cancelado(self, indice):
        
        switcher = {
            1 : "0",
            3 : "1",
            5 : "2",
            7 : "3",
            9 : "4",
            11 : "5",
            13 : "6",
            15 : "7",
            17 : "8",
            19 : "9",
            21 : "10"
        }
        return switcher.get(indice, 'Opção inválida')