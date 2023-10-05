from typing import Union

from selenium.common.exceptions import TimeoutException

from sites.elementos import Button, Chrome


def btn_iniciar_fact(driver: Chrome, time_out=1):
    sel = "#btnIniciarOperacao"
    label = "BotaoIniciarOperacao"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_acessar_fact(driver: Chrome, time_out=1):
    sel = "#botaoAcessar"
    label = "BotaoAcessar"
    return Button(driver, seletor=sel, label=label, time_out=time_out)

def btn_voltar(driver: Chrome, time_out=1):
    sel = "#erro > div > div > div > button"
    label = "BotaoVoltar"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_codigo_convenio(driver: Chrome, time_out=1):
    sel = 'button[data-id="CodigoConvenio"]'
    label = "BotaoCodigoConvenio"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_codigo_operacao(driver: Chrome, time_out=1):
    sel = 'button[data-id="CodigoOperacao"]'
    label = "BotaoCodigoOperacao"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_codigo_tipo_operacao(driver: Chrome, time_out=1):
    sel = 'button[data-id="CodigoTipoOperacao"]'
    label = "BotaoCodigoTipoOperacao"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_selecionar_matricula(driver: Chrome, time_out=1):
    sel = 'button[data-id="CbxMatricula"]'
    label = "BotaoSelecionarMatricula"
    return Button(driver, seletor=sel, label=label, time_out=time_out)


def btn_especie_beneficio(driver: Chrome, time_out=1) -> Button:
    sel = 'button[data-id="CodigoEspecieBeneficio"]'
    label = "BotaoEspecieBeneficio"
    btn: Button = Button(driver, seletor=sel, label=label, time_out=time_out)
    return btn


def btn_ok_modal_sucesso(driver: Chrome, time_out=1) -> Union[Button, None]:
    sel = 'input#btnOKMensagemSucesso'
    label = "<Button>OKMensagemSucesso</Button>"
    ctn = Button(driver, seletor=sel, label=label, time_out=time_out)
    try:
        ctn.carregar_elemento()
    except TimeoutException:
        return None
    return ctn


def btn_ok_modal_dataprev(driver: Chrome, time_out=1) -> Union[Button, None]:
    sel = '//*[@id="btnRetornoDataprev"]'
    label = "<Button>RetornoDataprev</Button>"
    ctn = Button(driver, seletor=sel, label=label, time_out=time_out)
    try:
        ctn.carregar_elemento()
    except TimeoutException:
        return None
    return ctn


def btn_ok_modal_aguardar_dados(driver: Chrome, time_out=1) -> Union[Button, None]:
    sel = "#btnAguardarFinalizar"
    label = "<Button>AguardarFinalizar</Button>"
    ctn = Button(driver, seletor=sel, label=label, time_out=time_out)
    try:
        ctn.carregar_elemento()
    except TimeoutException:
        return None
    return ctn