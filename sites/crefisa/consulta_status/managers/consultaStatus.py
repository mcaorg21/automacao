from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
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

        self.verificar_loading()       
        print('Inciando sincronização...')
        status_a_consultar = self.dados.get_ades()[1:]

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        #para testes
        #status_a_consultar = [['508020005927', '31522563881', '634296']]

        self.chrome_driver.get(self.urls["consulta"])

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")

            try:
                
                print("Consultando proposta:", proposta)

                ade, cpf_bd = proposta[0], proposta[1]
                cod_con = proposta[2]
                self.dados_consulta = {}

                self.dados_consulta['ade'] = ade
                self.dados_consulta["codigoCon"] = cod_con

                print(self.dados_consulta)        

                self.limpar_busca()

                self.buscar_contrato(cpf_bd, "cpf", False)

                self.dados_consulta['novaAde'] = ""

                self.div = div = '7'
                if(self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody', By.XPATH) == 0):
                    self.div = div = '6'
                #pdb.set_trace()
                if(self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr', By.XPATH) >= 4):

                    indice = str(int(self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr', By.XPATH))-1) 
                    
                    if self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr', By.XPATH) == 4:
                        novo_contrato = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[1]/td[4]/div/a[2]', By.XPATH).strip()
                        if novo_contrato == "":
                            indice = 1

                    if(self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[4]/div/a[2]', By.XPATH).strip() == ""):

                        self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[2]/div/span[1]', By.XPATH).strip()
                        self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
                        self.dados_consulta['statusSecundario'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[6]/a', By.XPATH).strip()
                        self.dados_consulta['novaAde'] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[4]/div/a[1]', By.XPATH)

                    else:
                        
                        self.buscar_contrato(ade)
                        self.buscar_status()

                else:
                    print('Buscando proposta unica...')
                    self.buscar_status()

                
               

                if ('PAGO' in self.dados_consulta["statusPropostaBanco"] or 'APROVADO' in self.dados_consulta["statusPropostaBanco"]) and 'EM ANDAMENTO' in self.dados_consulta["statusSecundario"]:
                    self.dados_consulta['statusSecundario'] += " "+self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[4]', By.XPATH).replace('\n',"").split("Liberado")[1]

                self.dados.post_dados_consultados(self.dados_consulta)    

                try:          

                    self.act.clicar_elemento('//*[@id="btnExibirFiltro"]', By.XPATH)
                    self.act.enviar_texto('//*[@id="txtNumeroAde"]', "", By.XPATH)
                    self.act.enviar_texto('//*[@id="txtCpf"]', "", By.XPATH)

                except:
                    pdb.set_trace()
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

                    self.dados.api_registrar_log_robo(
                        log=f"ERRO: {e}",
                        status=0
                    )

                continue

        #self.dados.data_source.atualizar_sincronizacao()
        self.dados.api_registrar_log_robo(log="Sincronizado com sucesso.",status=2)


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

        self.act.clicar_elemento('//*[@id="btnBuscaContratos"]', By.XPATH)

        self.verificar_loading()

    def buscar_status(self, indice = "1", div = "6"):
        try:
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
            self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[{self.div}]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[2]/span', By.XPATH).strip()
            self.dados_consulta['statusSecundario'] = self.dados_consulta['observacaoDetalhadaBanco'].split('|')[0].replace("|","").strip()
                        
        except:
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[6]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[1]', By.XPATH).strip()
            self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[6]/div[2]/div[6]/div/div/table/tbody/tr[{indice}]/td[6]/ul/li[5]/span[2]/span', By.XPATH).strip()
            self.dados_consulta['statusSecundario'] = self.dados_consulta['observacaoDetalhadaBanco'].split('-')[0].replace("|","").strip()

    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)


    def verificar_loading(self, interacoes=300, aguardar = False):
        self.aguardar_consulta(0.8)
        while (self.act.quantidade_elemento('/html/body/div[9]', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(0.5)
            interacoes -= 1
            if self.act.quantidade_elemento('/html/body/div[7]/div[2]/div[6]/div/div/table/tbody/tr[1]/td[6]/ul/li[5]/span[1]', By.XPATH) == 1:
                return
            if(interacoes < -35):
                self.driver.quit()