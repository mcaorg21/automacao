from sites.elementos import TextInput, Chrome


def cpf_input_fact(driver: Chrome, time_out=5):
    sel = '#CPF'
    label = "InputTextCPF"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_login_fact(driver: Chrome, time_out=5):
    sel = '#txtUsuario'
    label = "Usuário"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_senha_fact(driver: Chrome, time_out=5):
    sel = '#txtSenha'
    label = "Senha"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)

def input_tfa_fact(driver: Chrome, time_out=5):
    sel = '#txt2FACode'
    label = "2FA"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)

def input_data_nascimento(driver: Chrome, time_out=5):
    sel = '#DataNascimento'
    label = "InputTextDataNascimento"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)
