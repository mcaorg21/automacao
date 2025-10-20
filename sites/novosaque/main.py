#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/novosaque/main.py

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

from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.manager import Manager
from sites.core.uconecte import Uconecte

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo,deleta_todos_arquivos
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.novosaque.consulta_status.managers.consultaStatus import ConsultaStatus
from sites.novosaque.consulta_status.managers.insereContrato import InserirContrato

from sites.novosaque.libs.FormLogin import FormLogin

from time import sleep

import shutil

HORARIO_COMERCIAL = 7, 22

class Main:

    id_banco: int = 285
    id_robo: int = 'x'

    TITLE = "Novo Saque - Insercao e Sincronizacao"

    def __init__(self):
        self.base_path: str = PATHS.project_path()
        self.chrome_user: str = PATHS.chrome_user('NovoSaque')
        self.driver_path: str = PATHS.driver_path()
        
        options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        options.add_argument('--ignore-ssl-errors')
        
        options.add_argument('--window-size=1150,600"')
        options.add_argument(self.chrome_user)
        options.add_experimental_option("w3c", False)
        opts = ('--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,800","--ignore-autocomplete-off-autofill","disable-infobars")


        try:
            self.driver = Manager.driver_factory(*opts)
            # self.driver: Chrome = webdriver.Chrome(
            #     executable_path=self.driver_path,
            #     options=options
            # )
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

        self.driver.set_window_position(1250, 0)

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)

        login = FormLogin.realizar_login(self.driver,'aplicativo@uconecte.me','@123mudar')

        #fila de insercao de contrato
        definir_nome_robo(self.TITLE)
        InserirContrato.iniciar_horario_comercial(self.driver)
          
        #fila de sincronizacao
        definir_nome_robo(self.TITLE)
        ConsultaStatus.iniciar_horario_comercial(self.driver)

        print('Aguardando 10 minutos para reiniciar...')
        #self.driver.quit()
        sleep(600)
        #Main().main()
        self.main()


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
