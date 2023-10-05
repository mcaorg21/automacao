from sites.oleConsignado.libs.elementos.Botoes import btn_ok_modal_sucesso, btn_ok_modal_dataprev, \
    btn_ok_modal_aguardar_dados
from sites.oleConsignado.libs.elementos.TextContainers import (
    div_mensagem_erro1, div_mensagem_erro2)
from selenium.webdriver import Chrome

from sites.elementos import TextContainer
from sites.elementos import Button


def verificar_div_erro(driver: Chrome) -> str:
    div1: TextContainer = div_mensagem_erro1(driver)
    div2: TextContainer = div_mensagem_erro2(driver)

    if div1 is not None:
        div1.extrair_texto()
        return div1.texto

    if div2 is not None:
        div2.extrair_texto()
        return div2.texto

    return ""


def dispensar_modais(driver: Chrome):
    btn_sucesso: Button = btn_ok_modal_sucesso(driver)
    btn_dataprev: Button = btn_ok_modal_dataprev(driver)
    btn_aguardar: Button = btn_ok_modal_aguardar_dados(driver)

    if btn_sucesso is not None:
        print("Dispensando:", btn_sucesso)
        btn_sucesso.hover_e_clique()

    elif btn_dataprev is not None:
        print("Dispensando:", btn_dataprev)
        btn_dataprev.hover_e_clique()

    elif btn_aguardar is not None:
        print("Dispensando:", btn_aguardar)
        btn_aguardar.hover_e_clique()
