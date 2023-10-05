"""
    Função principal - Realiza o login e disponibiliza os cookies
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sites.oleConsignado.robos.auxiliares import *
from sites.baseRobos.core.selenium_actions import SeleniumActions, SeleniumHelper
from sites.baseRobos.core.decorators import AguardarHorarioComercial
import os

from time import sleep
# CONSTANTES GLOBAIS #
ID_BANCO: int = 123
ID_ROBO: int = 24


def login(act: object, driver: object):
    RECAPTCHA_KEY = "6LepATAUAAAAALJCpk3eDBkBiVZuai3DeOsXBFRv"
    act.reCaptcha_v2(RECAPTCHA_KEY)

    act.press_backspace('#Login')
    driver.execute_script("""$('#Login').val('CCASTROLEWE')""")

    act.press_backspace('#Senha')
    act.enviar_texto("#Senha", "marcelo31")

    act.clicar_elemento("#botaoAcessar")

    if driver.current_url.find("Home") == -1:
        print('Erro no login, tentando novamente...')
        return login(act, driver)
    else:
        print('Login realizado com sucesso!')


@AguardarHorarioComercial(inicio=7, fim=20)
def logar_enquanto_deslogado(driver: object, cookies_path):
    act = SeleniumActions(driver)
    sh = SeleniumHelper(driver)
    URL = 'https://ola.oleconsignado.com.br/Home'
    sleep(5)

    driver.get(URL)
    while driver.current_url.find("ola.oleconsignado.com.br/usuario/index?returnurl") != -1:
        print("Logando usuário...")
        login(act, driver)
        print("Logado com sucesso.")

        print("Salvando os cookies.")

    try:
        sh.save_cookies(cookies_path)
    except Exception as e:
        print(e.args)
    sleep(5)
