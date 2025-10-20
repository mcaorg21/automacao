#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/crefisa/main.py

| projeto: automacao-python
| data: 2025-05-22
| autor: Marcelo Amancio
"""
import pdb,sys, os

if "linux" in sys.platform:
    sys.path.insert(1, '/home/gustavo/Desktop/automacao-python/')
else:
    sys.path.append('../')


from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo,deleta_todos_arquivos
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.euro17.consulta_status.managers.consultaStatus import ConsultaStatus
from sites.euro17.consulta_status.managers.analisaContrato import AnalisaContrato
from sites.euro17.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo

from time import sleep

import shutil,json, random, logging

import tempfile
import atexit
import threading

import argparse

HORARIO_COMERCIAL = 7, 22

class Main():

    id_banco: int = '170'
    id_robo: int = '282941'

    TITLE = "Euro - Analisa Contrato"
    
    def __init__(self, indice):

        self.base_path = PATHS.project_path()
        # numero_random = random.randint(10, 20)
        # self.final_contrato = str(numero_random)[-1]
        self.final_contrato = str(indice)

        self.chrome_user = PATHS.chrome_user('Euro Analisa Contrato ' + self.final_contrato)

        os.environ["TMPDIR"] = "/home/gustavo/Desktop/automacao-python/tmp"
        os.makedirs(os.environ["TMPDIR"], exist_ok=True)

        try:
            pasta_user = self.chrome_user.replace("--user-data-dir=","")
            shutil.rmtree(pasta_user)

            os.environ["TMPDIR"] = "/home/gustavo/Desktop/automacao-python/tmp"
            os.makedirs(os.environ["TMPDIR"], exist_ok=True)

        except:
            pass
        
        self.path_documentos = sys.path[0]+'/logs/'

        if 'win32' in sys.platform:
            self.path_documentos = sys.path[0]+'/logs/'
        
        # Gera a data de hoje no formato YYYY-MM-DD
        self.data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M")

        # Configuração do log
        logging.basicConfig(
                filename= self.path_documentos + f"contratos_{self.data_atual}.log",  # nome do arquivo de saída
                level=logging.INFO,        # nível de log (INFO já é suficiente)
                format="%(asctime)s - %(levelname)s - %(message)s"  # formato com hora
            )
        
        self.driver_path = PATHS.driver_path()
        self.ordem = 'desc' 
        
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"

        # Antes: options.add_argument(self.chrome_user)  # Causa conflito
        # Agora: perfil efêmero automático
        options, _ = self.make_ephemeral_chrome_options(window_size="1150,1000", incognito=True)
        opts = options.arguments 
        
        self.driver = Manager.driver_factory(*opts)

        self.timer: int = 60
        self.ultima_atualizacao: datetime = datetime.now()

        self.uconecte: Uconecte = Uconecte(id_banco=self.id_banco)
        self.act: SeleniumActions = SeleniumActions(self.driver)
        self.sh: SeleniumHelper = SeleniumHelper(self.driver)
        self.selenium_helper = SeleniumHelper(self.driver)

        self.caminho_base = PATHS.project_path()

        self.cookies_path = self.caminho_base+"\\euro\\cookies\\" + "usuario_euro.pkl"
        self.cookies_path_json = self.caminho_base+"\\euro\\cookies\\" + "usuario_euro.json"
        
        self.driver.set_window_position(1350, 0)

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):

        while self.load_cookies_euro_web_admin() == False:
            print('Cookies vencidos, aguardando atualização...')
            sleep(50)
            self.driver.quit()
        
        #fila de analise
        definir_nome_robo(self.TITLE + ' - ' + self.final_contrato)
        
        try:
            #consulta_ou_analise = input('1- consulta | 2 analise \n\n')
            #consulta_ou_analise = '2'
            # if consulta_ou_analise == '1':
            #     ConsultaStatus.iniciar_horario_comercial(self.driver, forcar_consulta=True) 
            # elif consulta_ou_analise == '2':
            AnalisaContrato.iniciar_horario_comercial(self.driver, self.ordem, self.final_contrato)
                
        except Exception as e:
            print(f"Erro no robô: {e}")
            pass
        

        # print('Aguardando minutos para reiniciar...')
        # sleep(60)
        self.main()
        #self.driver.quit()

    def load_cookies_euro_web_admin(self):

        url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/euro/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://capture.kapmug.com/dashboard')
        self.driver.delete_all_cookies()

        return_cookie = True

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://capture.kapmug.com/dashboard')
        
        area_login = self.act.quantidade_elemento('//*[@id="input_text_user"]', By.XPATH)
        
        if(area_login == 1):
            return_cookie = False

        return return_cookie

    def load_cookies_pasta(self):

        self.driver.get('https://web.kapmug.com/home')
        self.driver.delete_all_cookies()

        file = open(self.cookies_path_json)
        cookies = json.load(file)

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://capture.kapmug.com/dashboard')

    def make_ephemeral_chrome_options(self, window_size="1150,1000", incognito=True, guest=False):
        """
        Cria um perfil temporário por execução, evitando lock e reaproveitamento.
        Retorna (options, temp_profile_path). O path é só para debug se quiser.
        """
        temp_profile = tempfile.mkdtemp(prefix="chrome_sess_")  # perfil efêmero

        options = webdriver.ChromeOptions()
        
        if incognito:
            pass
            #options.add_argument("--incognito")
        else:
            options.add_argument(f'--user-data-dir={temp_profile}')   # pasta única por sessão
        # if guest:
        #     # Guest mode ignora dados e perfis; use sem incognito se preferir.
        #     options.add_argument("--guest")

        # Estabilidade / menos prompts
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        if 'win32' not in sys.platform:
            options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-features=TranslateUI,AutomationControlled")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--window-size=" + window_size)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("w3c", False)

        # Limpa o perfil temporário no encerramento do processo
        def _cleanup():
            try:
                shutil.rmtree(temp_profile, ignore_errors=True)
            except:
                pass
        atexit.register(_cleanup)

        return options, temp_profile
    
if __name__ == '__main__':
    
    # threads = []
    # for i in range(4):
    #     try:
    #         print('Aguardando 10 segundos para iniciar a thread...')
    #         sleep(3)
    #         t = threading.Thread(target=Main(i).main)
    #         t.start()
    #         threads.append(t)
    #     except Exception as e:
    #         print(f"Erro ao iniciar thread {i}: {e}")
    #         pass
    
    # for t in threads:
    #     t.join()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, help='Modo de execução')
    args = parser.parse_args()

    run = Main(args.id)
    run.main()
