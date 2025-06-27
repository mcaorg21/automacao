#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/crefisa/main.py

| projeto: automacao-python
| data: 2025-03-25
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

from sites.facta.consulta_status.managers.insereContrato import InserirContrato
from sites.facta.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo

from time import sleep

import shutil,json,random

HORARIO_COMERCIAL = 7, 22

class Main():

    id_banco: int = '149'
    id_robo: int = '1491'

    TITLE = "Facta - Insercao"

    def __init__(self):

        nome = f'Facta Insercao {random.randint(1, 1000)}'
        self.base_path: str = PATHS.project_path()
        self.chrome_user: str = PATHS.chrome_user(nome)
        self.driver_path: str = PATHS.driver_path()
        self.ordem = 'desc' 
        
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"

        options = Options()
        try:
            Manager().criar_pasta_usuario_chrome(self.chrome_user)
   
            options.add_argument('--ignore-ssl-errors')
            
            options.add_argument('--window-size=1150,600"')
            options.add_argument(self.chrome_user)
            options.add_experimental_option("w3c", False)
            opts = ('--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,1000","--ignore-autocomplete-off-autofill","disable-infobars")

            # try:
            self.driver = Manager.driver_factory(*opts)
            # except:
            #     pasta_user = self.chrome_user.replace("--user-data-dir=","")
            #     print("Erro de criacao de usuario, deletando a pasta...")
            #     shutil.rmtree(pasta_user)
            #     exit()
            
        except:
            self.ordem = 'asc' 
            self.chrome_user = str = PATHS.chrome_user('Facta Insercao DESC')
            Manager().criar_pasta_usuario_chrome(self.chrome_user)
            
            options.add_argument('--ignore-ssl-errors')
            
            options.add_argument('--window-size=1150,600"')
            options.add_argument(self.chrome_user)
            options.add_experimental_option("w3c", False)
            opts = ('--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,1000","--ignore-autocomplete-off-autofill","disable-infobars")

            self.driver = Manager.driver_factory(*opts)

        self.timer: int = 60
        self.ultima_atualizacao: datetime = datetime.now()

        self.uconecte: Uconecte = Uconecte(id_banco=self.id_banco)
        self.act: SeleniumActions = SeleniumActions(self.driver)
        self.sh: SeleniumHelper = SeleniumHelper(self.driver)
        self.selenium_helper = SeleniumHelper(self.driver)

        self.caminho_base = PATHS.project_path()

        self.cookies_path = self.caminho_base+"\\facta\\cookies\\" + "usuario_facta.pkl"
        self.cookies_path_json = self.caminho_base+"\\facta\\cookies\\" + "usuario_facta.json"

        self.driver.set_window_position(300, 0)

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):

        # try:
        #     cookies_vencido = self.load_cookies_facta_web_admin()
        # except: 
        #     cookies_vencido = False
        #     pass

        while self.load_cookies_facta_web_admin() == False:
            print('Cookies vencidos, aguardando atualização...')
            sleep(5)
        
        #fila de insercao de contrato
        definir_nome_robo(self.TITLE + ' - ' + self.ordem)   
        insercao = InserirContrato.iniciar_horario_comercial(self.driver, self.ordem)

        if(insercao == False):
            print('entrou............')
            self.main()

        print('Aguardando minutos para reiniciar...')
        self.main()


    def load_cookies_facta_web_admin(self):
        
        url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/facta/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://desenv.facta.com.br/sistemaNovo/dashboard.php')
        self.driver.delete_all_cookies()

        return_cookie = True

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://desenv.facta.com.br/sistemaNovo/dashboard.php')
        
        area_login = self.act.quantidade_elemento('//*[@id="login"]', By.XPATH)
        
        if(area_login == 1):
            return_cookie = False

        return return_cookie


    def load_cookies_pasta(self):

        self.driver.get('https://desenv.facta.com.br/sistemaNovo/dashboard.php')
        self.driver.delete_all_cookies()

        file = open(self.cookies_path_json)
        cookies = json.load(file)

        for cookie in cookies:
            try:
                #if('expiry' not in cookie):
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://desenv.facta.com.br/sistemaNovo/propostaSimulador.php')

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print("Tempo entre atualizações: {}".format(time_between_updates))
        print("Timer: {} segundos".format(self.timer))

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            print("Esperando {} segundos antes de recomeçar a fila!".format(wait_time))

            if wait_time > 0:
                sleep(wait_time)

            self.timer += 1
        else:
            self.timer -= 1

        self.ultima_atualizacao = datetime.now()
        self.uconecte.atualizar_status_robo(self.id_robo)


if __name__ == '__main__':
    run = Main()
    run.main()
