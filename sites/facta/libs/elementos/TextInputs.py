from sites.elementos import TextInput, Chrome

def input_login_fact(driver: Chrome, time_out=5):
    sel = '#login'
    label = "login"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_senha_fact(driver: Chrome, time_out=5):
    sel = '#senha'
    label = "senha"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)
