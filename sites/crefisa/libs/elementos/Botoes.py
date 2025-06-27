from typing import Union

from selenium.common.exceptions import TimeoutException

from sites.elementos import Button, Chrome

import pdb


def btn_acessar_fact(driver: Chrome, time_out=1):
    sel = '//*[@id="btnLogin"]'
    label = "Entrar"
    return Button(driver, seletor=sel, label=label, time_out=time_out)

def btn_tfa_fact(driver: Chrome, time_out=1):
    sel = '//*[@id="btn2faCode"]'
    label = "Validar"
    return Button(driver, seletor=sel, label=label, time_out=time_out)