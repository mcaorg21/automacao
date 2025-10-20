from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from datetime import date, datetime, timedelta
import requests

from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.facta.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

from sites.crefisa.libs.FormLogin import FormLogin
from dados.database.queries.query_dados_robos import query_login_pass_robo


HORARIO_COMERCIAL = 8, 22


class AnalisaContrato(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "consulta": f"https://desenv.facta.com.br/sistemaNovo/propostaAnalise.php?codigo=ade&corretor=94485"
        }
        
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome):

        run = AnalisaContrato(driver)
        try:
            run.consultar_status_pendente()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_status_pendente(self):     
        
        print('Inciando sincronização...')
        status_pendente = self.dados.get_pendentes()[1:]
        for cnt, proposta in enumerate(status_pendente, 1):
            
            self.dados_consulta = {}
            self.dados_consulta['ade'] = 0
            
            cpf = proposta[0]
            cod_con = proposta[1]
            ultima_atualizacao = proposta[2]
            
            data_ref = datetime.strptime(ultima_atualizacao, "%Y-%m-%d %H:%M:%S")
                    
            if datetime.now() - data_ref <= timedelta(hours=1):
                print(f'>>>> Ultima atualização menor que 1 hora: Contrato {cod_con} - Hora {ultima_atualizacao}')
                continue
                      
            print(f"CPF: {cpf}, Código: {cod_con}")
            url = "https://desenv.facta.com.br/sistemaNovo/ajax/consignado-trabalhador/simulador.php"
            payload = {'cpf': {cpf},'acao': 'consulta_autorizacao'}
            response = requests.request("POST", url, headers="", data=payload)
            
            try:
                retorno = response.json()

                if "consultas_disponiveis" in retorno:
                    print("Consulta disponível")
                    if retorno['consultas_disponiveis'] == 'N':
                        print("XXXXXXXXX Consulta não disponível")
                        
                        self.dados_consulta["codigoCon"] = cod_con
                        self.dados_consulta["statusPropostaBanco"] = 'Autorização ainda não realizada'
                        self.dados_consulta['observacaoDetalhadaBanco'] = ""
                        self.dados.post_dados_consultados(self.dados_consulta)  
                        continue
                    else:
                        print("XXXXXXXXX Verificar retorno")
                        #pdb.set_trace()
                else:
                    if 'error' in retorno:
                        print("XXXXXXXXX Erro no retorno")
                        if retorno['error'] == True:
                            if retorno['message'] == 'CPF não encontrado na base':
                                print("XXXXXXXXX CPF não encontrado na base")
                                self.dados_consulta["codigoCon"] = cod_con
                                self.dados_consulta["statusPropostaBanco"] = 'CPF não encontrado na base'
                                self.dados_consulta['observacaoDetalhadaBanco'] = ""
                                self.dados.post_dados_consultados(self.dados_consulta)  
                                continue

                    if("message" in retorno):
                        if retorno['message'] == 'CPF encontrado':
                            print("VVVVVVVVVV CPF encontrado")
                            self.dados_consulta["codigoCon"] = cod_con
                            self.dados_consulta["statusPropostaBanco"] = 'Autorização realizada'
                            self.dados_consulta['observacaoDetalhadaBanco'] = ""
                            self.dados.post_dados_consultados(self.dados_consulta)  
                            continue
                    else:
                        print("XXXXXXXXX Verificar mensagem nova")
                        
            except:
                print("XXXXXXXXX Erro ao interpretar o retorno")
                #pdb.set_trace()
                
        
        return True