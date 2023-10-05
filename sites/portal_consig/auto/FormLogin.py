from sites.baseRobos.gui_auto import AutoGUI
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome


class FormLogin(AutoGUI):
    def __init__(self, driver: Chrome, **kwargs):
        super().__init__(driver)
        self.cpf_login = kwargs.get('cpf_login')
        self.senha = kwargs.get('senha')
        self.login_status = False

    @property
    def status_login(self):
        if "consignatario" in self.chrome_driver.current_url or "selecaoPerfil" in self.chrome_driver.current_url:
            return True
        else:
            return False

    @property
    def status_login_pagina(self):
        if "selecaoPerfil" in self.chrome_driver.current_url:
            return 0
        elif "autenticado" in self.chrome_driver.current_url:
            return 0
        elif "pesquisarMargem" in self.chrome_driver.current_url:
            return 2

    def clicar_aba_admnistrativo(self):
        # Aba log admin
        loc = '//span[text()="Login Administrativo"]/..'  # XPATH
        self.act.clicar_elemento(loc, metodo=self.metodo.XPATH)

    def resolver_preencher_captcha(self):
        loc_captcha_img = 'img'
        loc_captcha_campo = 'input#captcha'
        id_captcha, captcha_resp = self.captcha.resolver_captcha(loc_captcha_img)
        self.act.enviar_texto(loc_captcha_campo, captcha_resp)
        self.captcha.mudar_status_captcha(id_captcha, '1')

        self.act.press_enter(loc_captcha_campo)

    def preencher_senha(self):
        loc_senha_input = 'input#password'
        self.act.hover_e_clique(loc_senha_input)
        self.act.enviar_texto(loc_senha_input, self.senha)

    def preencher_cpf(self):
        loc_cpf_input = 'input[title="CPF"]'
        self.act.hover_e_clique(loc_cpf_input)
        self.act.press_backspace(loc_cpf_input, loop=11, delay=0.05)
        self.act.enviar_texto(loc_cpf_input, self.cpf_login, clear=False)

    def verificar_erro_captcha(self):
        loc = 'div#divEtapaError2'
        try:
            erro = self.act.obter_texto(loc)
            print(erro)
            raise CaptchaIncorretoException(erro)
        except TimeoutException:
            return False


class CaptchaIncorretoException(Exception):
    def __init__(self, msg):
        self.msg = msg

