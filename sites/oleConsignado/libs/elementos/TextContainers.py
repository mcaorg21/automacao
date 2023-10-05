from typing import Union

from selenium.common.exceptions import TimeoutException

from sites.elementos.ContainerElements.TextContainer import TextContainer
from selenium.webdriver import Chrome


def div_mensagem_erro1(driver: Chrome, time_out=5) -> Union[TextContainer, None]:
    sel = '//*[@id="divMensagemErro"]/ul/li'
    label = "<Div>MensagemErro1</Div>"
    ctn = TextContainer(driver, seletor=sel, label=label, time_out=time_out)
    try:
        ctn.carregar_elemento()
    except TimeoutException:
        return None
    return ctn


def div_mensagem_erro2(driver: Chrome, time_out=5) -> Union[TextContainer, None]:
    sel = '//*[@id="divErro"]/ul/li'
    label = "<Div>MensagemErro2</Div>"
    ctn = TextContainer(driver, seletor=sel, label=label, time_out=time_out)
    try:
        ctn.carregar_elemento()
    except TimeoutException:
        return None
    return ctn
