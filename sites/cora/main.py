#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/novosaque/main.py

| projeto: automacao-python
| data: 2021-12-27
| autor: Marcelo Amancio
"""
import pdb,sys

import qrcode
#sys.path.append('../../')

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options

from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
import random

from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper

from sites.cora.consultas_emissoes.managers.consultaEmissoes import ConsultaEmissoes

from sites.cora.libs.FormLogin import FormLogin

from time import sleep
import time
from distutils.dir_util import copy_tree

import tkinter as tk

class IniciarEmissaoConsulta():

    def __init__(self):  

        self.base_path: str = PATHS.project_path()        
        self.driver_path: str = PATHS.driver_path()
        self.path_arquivo = PATHS.project_path()+"\\cora\\pix_boleto\\"
        self.inicio_execucao = time.time()        

    def main(self, dados_post):         

        self.driver = self.inciar_chrome(Chrome)  

        resultado = {}
        
        login = FormLogin.realizar_login(self.driver)

        if login == False:
            resultado['retorno_imagem'] = False
            resultado['codigo_barras'] = ''
            resultado['imagem_base64'] = ''
            resultado['tempo_execucao'] = ''
            self.driver.quit()
            self.main(dados_post)        

        resultado = ConsultaEmissoes.iniciar(self.driver, dados_post)
        resultado['tempo_execucao'] = int(time.time() - self.inicio_execucao)

        self.driver.quit()

        return resultado

    def sincronizacao(self):  

        definir_nome_robo("Cora - Sincronizacao")

        self.driver = self.inciar_chrome(Chrome)  

        resultado = {}
        
        login = FormLogin.realizar_login(self.driver)

        while ConsultaEmissoes.sincronizar(self.driver) == True:        
            self.driver.refresh()
            print('Sincronização finalizada aguardando 3 minutos...') 
            sleep(60)           
            self.driver.quit()            
            run = IniciarEmissaoConsulta()
            run.sincronizacao()

        self.driver.quit()
        run = IniciarEmissaoConsulta()
        run.sincronizacao()

    def inciar_chrome(self, Chrome, tipo = "solo", chrome_users = range(4,12)):

        if(tipo == "multiplo"):

            chrome_user = 'CoraEmissoes_'+str(chrome_users)
            options = self.iniciar_chrome_opcoes(chrome_user)
            self.driver: Chrome = webdriver.Chrome(executable_path=self.driver_path,chrome_options=options)

        else:
            for user in chrome_users:
                try:
                    chrome_user = 'CoraEmissoes_'+str(user)
                    options = self.iniciar_chrome_opcoes(chrome_user)
                    self.driver: Chrome = webdriver.Chrome(executable_path=self.driver_path,chrome_options=options)
                    break
                except:
                    print('XXXXXXXXXXXXXXX TENTANDO OUTRO USUARIO xxxxxxxxxxxxxxx')
                    continue

        print('>>>>>>>>>>>>>>>>>>>>>>>> Usando usuario: ' +chrome_user) 
        return self.driver   
        
    def iniciar_chrome_opcoes(self, chrome_user = 'CoraEmissoes_1'):
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        self.chrome_user: str = PATHS.chrome_user(chrome_user)
        options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)

        options.add_argument('--ignore-ssl-errors')
        options.add_argument('log-level=3')
        options.add_argument('--window-size=826,900')

        options.add_argument(f'--window-position={int(screen_width-screen_width/3)},0')
        
        #options.add_argument('--headless')
        options.add_argument(self.chrome_user)
        options.add_experimental_option("w3c", False)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        prefs = {'download.default_directory' : self.path_arquivo}
        options.add_experimental_option('prefs', prefs)

        return options


if __name__ == '__main__':
    run = IniciarEmissaoConsulta()
    run.sincronizacao()
