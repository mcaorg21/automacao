#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/facta/main.py

| projeto: automacao-python
| data: 2025-05-25
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
from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo,deleta_todos_arquivos
from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.euro17.consulta_status.managers.consultaStatus import ConsultaStatus
from sites.euro17.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo
from sites.core.selenium_helper import SeleniumHelper

from time import sleep
import time

import shutil
import pickle, json, requests

HORARIO_COMERCIAL = 8, 22

class Main:

    id_banco: int = '069'
    id_robo: int = 'x'

    TITLE = "Euro17 - Login e Sincronizacao"

    def __init__(self):

        self.id_robo = '282941'
        self.usuario = '060.506.946-80'

        self.base_path: str = PATHS.project_path()

        self.chrome_user: str = PATHS.chrome_user('euro')
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
            exit()

        self.timer: int = 60
        self.ultima_atualizacao: datetime = datetime.now()

        self.uconecte: Uconecte = Uconecte(id_banco=self.id_banco)
        self.act: SeleniumActions = SeleniumActions(self.driver)
        self.sh: SeleniumHelper = SeleniumHelper(self.driver)

        self.caminho_base = PATHS.project_path()

        self.cookies_path = self.caminho_base+"\\euro17\\cookies\\" + "usuario_euro.pkl"
        self.cookies_path_json = self.caminho_base+"\\euro17\\cookies\\" + "usuario_euro.json"

        self.selenium_helper = SeleniumHelper(self.driver)

        self.driver.get('https://web.kapmug.com/home')


    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)

        self.load_cookies_euro_web_admin()

        usuario = "060.506.946-80"
        senha = "@123mudar"        
        login = FormLogin.realizar_login(self.driver, usuario, senha)
        
        if login == False:
            print("Login falhou, verificar o robô.")
            pdb.set_trace()
            return False

        self.selenium_helper.save_cookies(self.cookies_path)
        self.escreve_json()

        #fila de sincronizacao
        definir_nome_robo(self.TITLE)
        #ConsultaStatus.iniciar_horario_comercial(self.driver)
        
        print('Aguardando minutos para reiniciar...')
        sleep(600)
        self.main()

    def load_cookies_euro_web_admin(self):
        
        url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/euro/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://web.kapmug.com/')
        self.driver.delete_all_cookies()

        return_cookie = True

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://web.kapmug.com/home')

        return True

    def escreve_json(self):
        with open(self.cookies_path, 'rb') as fpkl, open(self.cookies_path_json, 'w') as fjson:
            data = pickle.load(fpkl)
            json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)
            
        
        file = open(self.cookies_path_json)

        cookies = json.load(file)
        dados = {
                    'id_robo' : self.id_robo,
                    'cookies_json': json.dumps(cookies)
                }

        req = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/euro/?key={}".format(self.api_key), data=dados)

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
