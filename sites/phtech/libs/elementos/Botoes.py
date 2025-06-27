from typing import Union

from selenium.common.exceptions import TimeoutException

from sites.elementos import Button, Chrome

import pdb


def btn_acessar_fact(driver: Chrome, time_out=1):
    sel = "//button[contains(text(), 'Acessar')] | //button[@type='submit']"
    label = "Acessar"
    return Button(driver, seletor=sel, label=label, time_out=time_out)
