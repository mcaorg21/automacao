#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/facta/main.py

| projeto: automacao-python
| data: 2021-06-02
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

from sites.phtech.consulta_status.managers.consultaStatus import ConsultaStatus
from sites.phtech.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo
from sites.core.selenium_helper import SeleniumHelper

from time import sleep
import time

import shutil
import pickle, json, requests

HORARIO_COMERCIAL = 8, 22

class Main:

    id_banco: int = '301'
    id_robo: int = '3011'

    TITLE = "Phtech - Sincronizacao"

    def __init__(self):

        self.id_robo = '3011'        
        self.nome_banco = 'phtech'

        self.base_path: str = PATHS.project_path()

        self.chrome_user: str = PATHS.chrome_user(self.nome_banco + "_sincronizacao")
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

        self.caminho_base = PATHS.project_path()

        self.cookies_path = self.caminho_base+f"\\{self.nome_banco}\\cookies\\" + "usuario.pkl"
        self.cookies_path_json = self.caminho_base+f"\\{self.nome_banco}\\cookies\\" + "usuario.json"
        
        self.login = self.caminho_base+"\\phtech\\login\\" + "usuario.json"

        self.selenium_helper = SeleniumHelper(self.driver)


    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)
        
        # try:
            # pdb.set_trace()
            # resposta = requests.post('https://consultadpv.phng.dev/auth/login', data={'usuario': 'consulta.glm', 'senha': '&3cywE@72H2S'})
            # token = resposta.json().get('token')
            # self.driver.get('https://consultadpv.phng.app/consulta')
            # pdb.set_trace()
            # self.driver.refresh()
            # self.act.enviar_texto("//label[contains(., 'Usuario')]/ancestor::div[contains(@class,'field')]//input", 'consulta.glm', By.XPATH)
            # self.act.enviar_texto("//label[contains(., 'Senha')]/ancestor::div[contains(@class,'field')]//input", '&3cywE@72H2S', By.XPATH)
            # self.act.clicar_elemento("//button[span[normalize-space(text())='Entrar']]", By.XPATH)
            # time.sleep(5)
        # except:
        #     pass
        
        try:
            cookies_vencido = self.load_cookies_web_admin()
        except: 
            cookies_vencido = False
            pass
        
        area_login = self.act.quantidade_elemento('//*[@id="password"]', By.XPATH)     

        if(area_login == 1 or cookies_vencido == False):
            self.driver.delete_all_cookies()
            #self.driver.get('https://phtech.uy3.com.br/')

            try:
                self.driver.delete_all_cookies()
                #dados_login = query_login_pass_robo(self.id_robo, self.usuario)
                dados_login = json.load(open(self.login))
                dados_login['link'] = 'https://phtech.uy3.com.br/ccb/login.php'
                FormLogin.realizar_login(self.driver,dados_login['login'], dados_login['senha'], dados_login['link'])

            except:
                self.main()
                
        time.sleep(10)  
              
        self.driver.get('https://phtech.uy3.com.br/ccb/simular/')
        
        self.selenium_helper.save_cookies(self.cookies_path)
        self.escreve_json()

        #fila de sincronizacao
        definir_nome_robo(self.TITLE)
        ConsultaStatus.iniciar_horario_comercial(self.driver)
        
        print('Aguardando minutos para reiniciar...')
        sleep(1500)
        self.main()

    def load_cookies_web_admin(self):

        url = f"http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/{self.nome_banco}/?key={self.api_key}"
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://phtech.uy3.com.br/ccb/operacoes')
        self.driver.delete_all_cookies()

        return_cookie = True

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass

        self.driver.get('https://phtech.uy3.com.br/ccb/simular')

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

        requests.post(f"https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/{self.nome_banco}/?key={self.api_key}", data=dados)


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
