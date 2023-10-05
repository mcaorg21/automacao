"""
    Robô Consulta Status Olé
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sites.oleConsignado.ole_consulta_status.managers.consultaStatus import ConsultaStatusOle
from sites.baseRobos.core.selenium_actions import SeleniumActions

from sites.core.uconecte import Uconecte
from sites.baseRobos.core.selenium_helper import SeleniumHelper

from sites.oleConsignado.robos.auxiliares import *

import os
from datetime import datetime
from time import sleep


# CONSTANTES GLOBAIS #
ID_BANCO: int = 123
ID_ROBO: int = 7
# Caminhos Webdriver
DRIVER_PC: str = ("C:\\Users\\{}\\Documents\\automacao-python\\"
                  "drivers\\chromedriver.exe".format('gustavo'))
DRIVER_SERV: str = os.getcwd().replace("\\", "/") + "/drivers/chromedriver.exe"

# Caminhos usuários chrome
USER_PC: str = ('--user-data-dir=C:\\Users\\{}\\AppData\\'
                'Local\\Google\\Chrome\\OleConsig3'.format("gustavo"))
USER_SERV: str = '--user-data-dir=C:/Users/lucas.s/AppData/Local/Google/Chrome/User Ole 3'

# Caminhos cookies
COOKIES_PC: str = ('C:\\Users\\gustavo\\Documents\\'
                   'automacao-python\\sites\\oleConsignado\\oleCk.pkl')
COOKIES_SERV: str = os.getcwd().replace("\\", "/") + "/sites/oleConsignado/cookies/oleCk.pkl"


def main():
    timer: int = 60
    ultima_atualizacao: datetime = datetime.now()

    # instâncias das classes essenciais à automação da tarefa
    driver: object = init_driver()
    tarefa: object = ConsultaStatusOle(driver)
    tarefa.id_robo = ID_ROBO

    # instâncias das classes de uso em <main>
    uconecte: object = Uconecte(id_banco=ID_BANCO)
    sh: object = SeleniumHelper(driver)
    act: object = SeleniumActions(driver)

    driver.get('https://ola.oleconsignado.com.br/Home')

    sleep(20)

    # loop principal
    while True:
        uconecte.atualizar_status_robo(ID_ROBO)

        try:
            aguardar_load_cookies(driver, sh, act, COOKIES_SERV)

            tarefa.consultar_status_proposta()

            ultima_atualizacao = verificar_tempo_execucao(
                ultima_atualizacao=ultima_atualizacao, timer=timer,
                uconecte=uconecte, id_robo=ID_ROBO
            )
        except Exception as e:
            print(e)
            sleep(5)


def init_driver():
    criar_pasta_usuario_chrome(USER_SERV)
    options: object = Options()
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    options.add_argument(USER_SERV)
    options.add_experimental_option("w3c", False)

    driver = webdriver.Chrome(
        executable_path=DRIVER_SERV,
        chrome_options=options)

    return driver


if __name__ == '__main__':
    main()

