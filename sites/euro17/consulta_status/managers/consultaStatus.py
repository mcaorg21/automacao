from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from datetime import date, datetime


from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.euro17.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By
from dados.database.queries.query_dados_robos import query_login_pass_robo


HORARIO_COMERCIAL = 8, 22


class ConsultaStatus(Manager):

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
        pdb.set_trace()
        # if not status_a_consultar:
        #     print('Sem atualizações para realizar...')
        #     return False

        # para testes
        # status_a_consultar = [['508020245425', '75498278268  ', '791535','','','','2025-01-25'],
        #                         # ['508020237553', '01969721243  ', '784907','','','','2025-01-21'],
        #                         # ['508020236554', '26257881862  ', '783404','','','','2025-01-20']
        #                         ]

        #status_a_consultar = [['508020238728', '12032318652  ', '777114','','','','2024-01-14']]

        self.chrome_driver.get(self.urls["consulta"])

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")

            print("Consultando proposta:", proposta)

            ade = proposta[0]
            cod_con = proposta[2]
            self.dados_consulta = {}
            self.dados_consulta['ade'] = ade
            self.dados_consulta["codigoCon"] = cod_con

            print(self.dados_consulta)  

            self.driver.get(self.urls["consulta"].replace('ade', ade))  
            self.verificar_loading()
            
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[1]/section/div/div/div/div/div/form/div[7]/div/div/div/div/div/div[2]/table/tbody/tr/td[4]', By.XPATH).strip()
            
            if('AGUARDANDO ASSINATURA DIGITAL' in self.dados_consulta["statusPropostaBanco"]):
                self.dados_consulta["statusPropostaBanco"] = 'AGUARDANDO ASSINATURA DIGITAL'
                self.dados_consulta['observacaoDetalhadaBanco'] = "Aguardando"
            else:
                
                self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div[1]/section/div/div/div/div/div/form/div[7]/div/div/div/div/div/div[2]/table/tbody/tr[1]/td[4]', By.XPATH).strip()
                self.dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto(f'/html/body/div[1]/section/div/div/div/div/div/form/div[7]/div/div/div/div/div/div[2]/table/tbody/tr[1]/td[5]', By.XPATH).replace('-',"").strip()

            self.dados.post_dados_consultados(self.dados_consulta)    

    def verificar_loading(self, interacoes = 60):
        
        print('Verificando loading...')

        while (self.sh.buscar_quantidade_elemento('#loadGiraGira\\:visible') == 1):
            print('Aguardando Loading...')

            interacoes -= 1
            self.aguardar_consulta(1)
            if(interacoes < 1):
                return