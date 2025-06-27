from sites.elementos import TextInput, Chrome

def input_login_fact(driver: Chrome, time_out=5):
    sel = '#email'
    label = "email"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)


def input_senha_fact(driver: Chrome, time_out=5):
    sel = '#password'
    label = "password"
    return TextInput(driver, seletor=sel, label=label, time_out=time_out)
