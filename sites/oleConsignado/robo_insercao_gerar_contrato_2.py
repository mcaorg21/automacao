#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/oleConsignado/robo_sinc_insercao.py

| projeto: automacao-python
| data: 2020-02-17
| autor: Gustavo Belleza
"""
import sys,pdb, shutil
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

from sites.oleConsignado.gerar_refin.ole_consignado import OleConsignado
from sites.oleConsignado.ole_insercao.managers.ole_consig_insercao import OleConsigInsercao
from sites.oleConsignado.robos.auxiliares import ErroSessaoOle

import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from sites.oleConsignado.config.paths_ole import PATH_ID_4_2

HORARIO_COMERCIAL = 8, 20


class Main:

    id_banco: int = 123
    id_robo: int = 20

    TITLE = "Ole - Insercao/Gerar Contrato"

    def __init__(self):
        self.base_path: str = PATHS.project_path()
        try:
            shutil.rmtree(PATHS.project_path()+'/chrome_user_dir/OleInsercao2')
        except:
            pass
        self.chrome_user: str = PATHS.chrome_user('OleInsercao2')

        self.driver_path: str = PATHS.driver_path()
        self.cookies_path = PATH_ID_4_2

        options = Options()
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(self.chrome_user)
        options.add_experimental_option("w3c", False)
        #self.driver: Chrome = webdriver.Chrome()

        #self.driver = webdriver.Chrome(options=options)

        self.driver = webdriver.Chrome()
        
        # self.driver: Chrome = webdriver.Chrome(executable_path=self.driver_path,   chrome_options=options
        # )
        self.timer: int = 60
        self.ultima_atualizacao: datetime = datetime.now()

        self.uconecte: Uconecte = Uconecte(id_banco=self.id_banco)
        self.act: SeleniumActions = SeleniumActions(self.driver)
        self.sh: SeleniumHelper = SeleniumHelper(self.driver)

        self.iter_cnt: int = 0

        self.RECAPTCHA_KEY: str = "6LepATAUAAAAALJCpk3eDBkBiVZuai3DeOsXBFRv"

    def main(self):
        definir_nome_robo(self.TITLE)

        self.driver.get('https://ola.oleconsignado.com.br/Home')

        self.aguardar_cookies()

        while True:
            try:
                definir_nome_robo(self.TITLE)
                #OleConsignado.iniciar_horario_comercial(self.driver)
            except:
                pass

            try:
                definir_nome_robo(self.TITLE)
                OleConsigInsercao.iniciar_horario_comercial(self.driver)

                self.verificar_tempo_execucao()

                self.iter_cnt += 1

                if self.iter_cnt >= 2:
                    #self.driver.quit()
                    sleep(60)
                    raise KeyboardInterrupt

            except ErroSessaoOle:
                self.aguardar_cookies()

            except Exception as e:
                print(e)
                sleep(5)

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

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def aguardar_cookies(self):
        cnt = 0
        while self.driver.current_url.find("Home") == -1 and cnt < 50:
            try:
                self.sh.load_cookies(self.cookies_path, delete=True)
            except Exception as e:
                print(e)
            print("Aguardando cookies do Olé Refin...")
            self.driver.refresh()
            sleep(20)
            cnt += 1

        self.uconecte.atualizar_status_robo(self.id_robo)


if __name__ == '__main__':
    run = Main()
    run.main()
