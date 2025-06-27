from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from datetime import date, datetime


from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.phtech.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

from sites.phtech.libs.FormLogin import FormLogin
from dados.database.queries.query_dados_robos import query_login_pass_robo


HORARIO_COMERCIAL = 8, 22


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "consulta": f"https://phtech.uy3.com.br/ccb/operacoes"
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

        # if not status_a_consultar:
        #     print('Sem atualizações para realizar...')
        #     return False

        # para testes
        # status_a_consultar = [['508020245425', '75498278268  ', '791535','','','','2025-01-25'],
        #                         # ['508020237553', '01969721243  ', '784907','','','','2025-01-21'],
        #                         # ['508020236554', '26257881862  ', '783404','','','','2025-01-20']
        #                         ]

        #status_a_consultar = [['508020238728', '12032318652  ', '777114','','','','2024-01-14']]

        

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")
            
            self.chrome_driver.get(self.urls["consulta"])

            print("Consultando proposta:", proposta)

            ade = proposta[0]
            cod_con = proposta[2]
            self.dados_consulta = {}
            self.dados_consulta['ade'] = ade
            self.dados_consulta["codigoCon"] = cod_con
            
            print(self.dados_consulta)  

            print('>>> Procurando proposta no banco...')
            self.act.enviar_texto('//*[@id="searchString"]', ade, By.XPATH)
            self.act.press_enter('//*[@id="searchString"]', By.XPATH)   

            print('>>> Pegando status no banco...')
            self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto(f'/html/body/div/div/div[7]/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[8]', By.XPATH).strip()
            
            while self.act.quantidade_elemento("MuiDataGrid-virtualScroller", By.CLASS_NAME) == 0:
                print('>>> Aguardando carregamento da proposta...')
                time.sleep(1)
                
            scroll = self.act.retornar_elemento("MuiDataGrid-virtualScroller", By.CLASS_NAME)
            self.driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollLeft + 100000;", scroll)

            print('>>> Pegando dados historico no banco...')
            self.driver.get(self.act.obter_atributo(f"//div[contains(@class,'MuiDataGrid-cell')]//a", 'href', By.XPATH))

            while self.act.quantidade_elemento("//h4[contains(text(), 'Operação')]", By.XPATH) == 0:
                print('>>> Aguardando carregamento da operação...')
                time.sleep(1)
            
            self.driver.execute_script("document.body.style.zoom='70%'")            
            self.act.clicar_elemento("//a[contains(text(), 'Histórico')]", By.XPATH)
            
            historico = self.act.retornar_elemento("//ul[contains(@class,'MuiTimeline-root')]", By.XPATH)
            self.dados_consulta['observacaoDetalhadaBanco'] = historico.text
            
            pdb.set_trace()

            self.dados.post_dados_consultados(self.dados_consulta)    

    def verificar_loading(self, interacoes = 60):
        
        print('Verificando loading...')

        while (self.sh.buscar_quantidade_elemento('#loadGiraGira\\:visible') == 1):
            print('Aguardando Loading...')

            interacoes -= 1
            self.aguardar_consulta(1)
            if(interacoes < 1):
                return