#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/crefisa/main.py

| projeto: automacao-python
| data: 2021-11-25
| autor: Marcelo Amancio
"""
import pdb,sys, os
sys.path.append('../')
#sys.path.insert(1, '/home/gustavo/Desktop/automacao-python/')


from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo,deleta_todos_arquivos
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.crefisa.consulta_status.managers.analisaContrato import AnalisaContrato

from sites.crefisa.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo

from time import sleep

import shutil,json

HORARIO_COMERCIAL = 7, 22

class Main():

    id_banco: int = '069'
    id_robo: int = 'x'

    TITLE = "Crefisa - Insercao"

    def __init__(self):

        self.id_robo = '691'
        self.usuario = '50801.06050694680'

        # self.id_robo = '692'
        # self.usuario = '50801.03507179660'

        self.base_path: str = PATHS.project_path()

        self.chrome_user: str = PATHS.chrome_user('Crefisa Analise')
        self.driver_path: str = PATHS.driver_path()

        self.api_key = "f689f1e12a0399fba803cb2365fc362f"

        options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        options.add_argument('--ignore-ssl-errors')
        
        options.add_argument('--window-size=1150,600"')
        options.add_argument(self.chrome_user)
        options.add_experimental_option("w3c", False)
        opts = ('--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,1000","--ignore-autocomplete-off-autofill","disable-infobars")


        try:
            self.driver = Manager.driver_factory(*opts)
        except:
            pasta_user = self.chrome_user.replace("--user-data-dir=","")
            print("Erro de criacao de usuario, deletando a pasta...")
            shutil.rmtree(pasta_user)
            #deleta_todos_arquivos(pasta_user)
            #os.rmdir(pasta_user)
            exit()

        self.timer: int = 60
        self.ultima_atualizacao: datetime = datetime.now()

        self.uconecte: Uconecte = Uconecte(id_banco=self.id_banco)
        self.act: SeleniumActions = SeleniumActions(self.driver)
        self.sh: SeleniumHelper = SeleniumHelper(self.driver)
        self.selenium_helper = SeleniumHelper(self.driver)

        self.caminho_base = PATHS.project_path()

        self.cookies_path = self.caminho_base+"\\crefisa\\cookies\\" + "usuario_crefisa.pkl"
        self.cookies_path_json = self.caminho_base+"\\crefisa\\cookies\\" + "usuario_crefisa.json"


    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo('Crefisa - Analisa Contrato')        

        self.load_cookies_crefisa_web_admin()
        
        #fila de insercao de contrato
        definir_nome_robo(self.TITLE)   
        insercao = AnalisaContrato.iniciar_horario_comercial(self.driver)

        if(insercao == False):
            print('entrou............')
            pdb.set_trace()
            self.main()

        print('Aguardando minutos para reiniciar...')
        #self.driver.delete_all_cookies()
        #self.driver.quit()
        sleep(1)
        #Main().main()
        self.main()

    def load_cookies_crefisa_web_admin(self):
        
        url = "https://emprestimofacil.co/web_admin/api/v1/consulta/cookies/crefisa/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/simuladorCrefisa.asp')
        self.driver.delete_all_cookies()

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/Dashboard.asp')

    def load_cookies_crefisa_web_admin(self):
        
        url = "https://emprestimofacil.co/web_admin/api/v1/consulta/cookies/crefisa/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/simuladorCrefisa.asp')
        self.driver.delete_all_cookies()

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/Dashboard.asp')

    def load_cookies_pasta(self):

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/simuladorCrefisa.asp')
        self.driver.delete_all_cookies()

        file = open(self.cookies_path_json)
        cookies = json.load(file)

        for cookie in cookies:
            try:
                #if('expiry' not in cookie):
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp')

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
