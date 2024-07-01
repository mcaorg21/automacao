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
from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo,deleta_todos_arquivos
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.whatsappwu.consulta_status.managers.tarefas import Tarefas
from sites.whatsappwu.libs.FormLogin import FormLogin

from time import sleep

import shutil, random

HORARIO_COMERCIAL = 8, 20

class Main:

    id_banco: int = 'x'
    id_robo: int = 'x'

    TITLE = "Whatsapp WarmUP"

    def __init__(self):

        self.base_path: str = PATHS.project_path()

        self.chrome_user: str = PATHS.chrome_user('WhatsappWU')
        self.driver_path: str = PATHS.driver_path()

        options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        options.add_argument('--ignore-ssl-errors')
        
        options.add_argument('--window-size=1150,600"')
        options.add_argument(self.chrome_user)
        options.add_experimental_option("w3c", False)
        opts = ('--disable-blink-features=AutomationControlled',
                '--ignore-ssl-errors', 
                self.chrome_user, 
                'log-level=3',
                "--no-sandbox",
                "--window-size=1150,1000",
                "--ignore-autocomplete-off-autofill",
                "disable-infobars")


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

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)
        
        login = FormLogin.realizar_login(self.driver)

        Tarefas.iniciar_horario_comercial(self.driver)

        print('Aguardando minutos para reiniciar...')
        sleep(random. randint(1, 300))
        self.main()


if __name__ == '__main__':
    run = Main()
    run.main()
