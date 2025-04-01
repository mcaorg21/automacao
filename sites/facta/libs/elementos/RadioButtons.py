from sites.elementos import RadioButton, Chrome


def btn_codigo_tipo_operacao(driver: Chrome, time_out=5):
    sel = "#radioDigital"
    label = "RadioTipoContratação"
    return RadioButton(driver, seletor=sel, label=label, time_out=time_out)
