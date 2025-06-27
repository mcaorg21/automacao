#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/crefisa/main.py

| projeto: automacao-python
| data: 2021-11-25
| autor: Marcelo Amancio
"""
import pdb,sys, os
#sys.path.append('../')
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

from sites.crefisa.consulta_status.managers.consultaStatus import ConsultaStatus
from sites.crefisa.consulta_status.managers.insereContrato import InserirContrato
from sites.crefisa.libs.FormLogin import FormLogin

from dados.database.queries.query_dados_robos import query_login_pass_robo
from sites.core.selenium_helper import SeleniumHelper

from time import sleep
import time

import shutil
import pickle, json, requests

HORARIO_COMERCIAL = 7, 22

class Main:

    id_banco: int = '069'
    id_robo: int = 'x'

    TITLE = "Crefisa - Sincronizacao"

    def __init__(self):

        self.id_robo = '691'
        self.usuario = '50801.06050694680'

        # self.id_robo = '692'
        # self.usuario = '50801.03507179660'

        self.base_path: str = PATHS.project_path()

        self.chrome_user: str = PATHS.chrome_user('Crefisa')
        self.driver_path: str = PATHS.driver_path()

        self.api_key = "f689f1e12a0399fba803cb2365fc362f"

        #options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        #options.add_argument('--ignore-ssl-errors')
        
        #options.add_argument('--window-size=1150,600"')
        #options.add_argument(self.chrome_user)
        #options.add_experimental_option("w3c", False)
        #options.add_experimental_option("prefs", {"intl.accept_languages": "pt-BR"})
        opts = ( "--lang=pt-BR", '--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,1000","--ignore-autocomplete-off-autofill","disable-infobars")
        #kwargs = {"intl.accept_languages": "pt-BR"}

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

        self.cookies_path = self.caminho_base+"\\crefisa\\cookies\\" + "usuario_crefisa.pkl"
        self.cookies_path_json = self.caminho_base+"\\crefisa\\cookies\\" + "usuario_crefisa.json"

        self.selenium_helper = SeleniumHelper(self.driver)

        self.driver.set_window_position(1250, 0)

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')

        self.driver.delete_all_cookies()

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)

        try:
            cookies_vencido = self.load_cookies_crefisa_web_admin()
        except: 
            cookies_vencido = False
            pass

        area_login = self.act.quantidade_elemento('//*[@id="logo"]', By.XPATH)     
        area_logada = self.act.quantidade_elemento('//*[@id="imgLogoEmpresa"]', By.XPATH)

        try:
            popup_login = self.act.obter_texto('/html/body/div[2]/div', By.XPATH)
            self.act.clicar_elemento('/html/body/div[2]/div/div[3]/button[1]', By.XPATH)
            popup_login = True
        except:
            popup_login = False
            pass

        if(popup_login == True):
            self.driver.delete_all_cookies()
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
            area_login = 1

        if(area_logada == 0 or area_login == 1 or cookies_vencido == False):
            try:
                self.driver.delete_all_cookies()
                #dados_login = query_login_pass_robo(self.id_robo, self.usuario)
                dados_login = {}
                dados_login['login'] = '50801.06050694680'
                dados_login['senha'] = '@123Mudar983'
                dados_login['link'] = 'https://app1.gerencialcredito.com.br/CREFISA/'
                login = FormLogin.realizar_login(self.driver,dados_login['login'], dados_login['senha'], dados_login['link'], popup_login)
            except:
                #self.driver.delete_all_cookies()
                self.main()
        try:
            texto = self.act.obter_texto('//h4[contains(text(),"Atualização de senha")]', By.XPATH)
            if texto == 'Atualização de senha':
                input('>>>>>> Troque a senha no arquivo...')
        except:
            pass

        self.selenium_helper.save_cookies(self.cookies_path)
        self.escreve_json()

        #fila de sincronizacao
        definir_nome_robo(self.TITLE)
        ConsultaStatus.iniciar_horario_comercial(self.driver)

        print('Aguardando minutos para reiniciar...')
        
        #self.driver.quit()
        sleep(15)
        self.driver.delete_all_cookies()
        self.main()
        #self.driver.quit()

    def load_cookies_crefisa_web_admin(self):
        
        url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/crefisa/?key={}".format(self.api_key)
        cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
        self.driver.delete_all_cookies()

        return_cookie = True

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                pass


        self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp')

        if self.act.quantidade_elemento('//*[@id="swal2-content"]', By.XPATH) == 1:
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
            return False

        if self.act.quantidade_elemento('/html/body/div[9]/div/div[3]/button[1]', By.XPATH) == 1:
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
            return False

        elif self.act.quantidade_elemento('/html/body/div[10]/div/div[3]/button[1]', By.XPATH) == 1:
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
            return False

        elif self.act.quantidade_elemento('/html/body/div[11]/div/div[3]/button[1]', By.XPATH) == 1:
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/')
            return False

        else:
            self.driver.get('https://app1.gerencialcredito.com.br/CREFISA/Dashboard.asp')

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
        
        req = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/crefisa/?key={}".format(self.api_key), data=dados)

        # for cookie in cookies:
        #     try:
        #         if('expiry' not in cookie):
        #             self.driver.add_cookie(cookie)
        #     except Exception as e:
        #         pass


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
