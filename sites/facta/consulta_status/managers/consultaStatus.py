from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.pyautogui_helper import find_elements_on_screen

import cv2
import PATHS

import os,time,pdb,re
from datetime import date, datetime
import pyautogui

from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.facta.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

from sites.crefisa.libs.FormLogin import FormLogin
from dados.database.queries.query_dados_robos import query_login_pass_robo

import pyperclip

HORARIO_COMERCIAL = 8, 22


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "andamento": "https://desenv.facta.com.br/sistemaNovo/andamentoPropostas.php",
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

        desafio = self.act.quantidade_elemento('//*[@id="footer-text"]', By.XPATH) 

        while desafio == 1:
            print('Resolva o desafio')
            self.driver.execute_script("document.body.style.zoom='100%'")
            time.sleep(5)
            #x, y = find_elements_on_screen(cv2.imread(PATHS.project_path()+'/facta/consulta_status/managers/confirmar.jpg'))
            pyautogui.click(141,429)
            print('Tentando clicar no desafio...')
            time.sleep(4)
            desafio = self.act.quantidade_elemento('//*[@id="footer-text"]', By.XPATH) 
            #pyautogui.click(x,y)
            #pdb.set_trace()
            # time.sleep(4)
            # try:
            #     pyautogui.click(141,429)
            #     #pyautogui.click(x,y)
            # except:
            #     pass
                
        
        time.sleep(15)

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        # para testes
        # status_a_consultar = [['508020245425', '75498278268  ', '791535','','','','2025-01-25'],
        #                         # ['508020237553', '01969721243  ', '784907','','','','2025-01-21'],
        #                         # ['508020236554', '26257881862  ', '783404','','','','2025-01-20']
        #                         ]

        # status_a_consultar = [['103485821', '10024666955  ', '860543','','','','2025-06-05']]

        self.chrome_driver.get(self.urls["consulta"])

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")
            self.chrome_driver.get(self.urls["andamento"])

            print("Consultando proposta:", proposta)

            ade = proposta[0]
            cod_con = proposta[2]
            self.dados_consulta = {}
            self.dados_consulta['ade'] = ade
            self.dados_consulta["codigoCon"] = cod_con
            
            print(self.dados_consulta)  
            
            self.driver.execute_script("document.body.style.zoom='50%'")
            self.act.enviar_texto('//*[@id="codigoAf"]', ade, By.XPATH)
            self.act.clicar_elemento('//*[@id="pesquisar"]', By.XPATH)
            self.act.clicar_elemento('//i[contains(@class, "copyLink")]', By.XPATH)
            time.sleep(2)
            link = pyperclip.paste()
            print(">>>> Link copiado:", link.strip())

            self.dados_consulta["linkAssinaturaDigital"] = link.strip()
            
            self.act.manusear_alerta('aceitar')

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