from sites.elementos import TextInput, Chrome


def cpf_input_fact(driver: Chrome, time_out=5):
    sel = '#CPF'
    label = "InputTextCPF"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_login_fact(driver: Chrome, time_out=5):
    sel = '#Login'
    label = "InputTextLogin"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_senha_fact(driver: Chrome, time_out=5):
    sel = '#Senha'
    label = "InputTextSenha"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_data_nascimento(driver: Chrome, time_out=5):
    sel = '#DataNascimento'
    label = "InputTextDataNascimento"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_convenio(driver: Chrome, time_out=5):
    sel = '//*[@id="divSimulacao"]/div[1]/div[2]/div/div/div/div/input'
    label = "InputTextConvenio"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_codigo_operacao(driver: Chrome, time_out=5):
    sel = '//*[@id="divSimulacao"]/div[1]/div[3]/div/div/div/div/input'
    label = "InputTextCodigoOperacao"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_codigo_tipo_operacao(driver: Chrome, time_out=5):
    sel = '//*[@id="divSimulacao"]/div[1]/div[4]/div/div/div/div/input'
    label = "InputTextCodigoTipoOperacao"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_matricula(driver: Chrome, time_out=5):
    sel = "#Matricula"
    label = "InputTextMatricula"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_div_cbx_matricula(driver: Chrome, time_out=5):
    sel ='//*[@id="divCbxMatricula"]/div/div/div/div/input'
    label = "InputTextDivCbxMatricula"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_valor_parcela(driver: Chrome, time_out=5):
    sel = "#ValorParcela"
    label = "InputTextValorParcela"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_especie_beneficio(driver: Chrome, time_out=5) -> TextInput:
    sel = '//*[@id="divBeneficio"]/div/div/div/div/input'
    label = "InputTextEspecieBeneficio"
    ipt: TextInput = TextInput(driver, seletor=sel, label=label, time_out=time_out)
    ipt.carregar_elemento()
    return ipt


def input_codigo_orgao(driver: Chrome, time_out=5) -> TextInput:
    sel = '#CodigoOrgao'
    label = "InputTextCodigoOrgao"
    ipt: TextInput = TextInput(driver, seletor=sel, label=label, time_out=time_out)
    ipt.carregar_elemento()
    return ipt
