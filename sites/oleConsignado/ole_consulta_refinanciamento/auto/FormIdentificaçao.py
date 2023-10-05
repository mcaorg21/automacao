from sites.oleConsignado.elementos import btn_iniciar_fact
from sites.oleConsignado.elementos import cpf_input_fact
from sites.elementos import Button
from sites.elementos import TextInput, Chrome


class FormIdentificacao:

    def __init__(self, driver: Chrome, **kwargs):
        self.cpf_input: TextInput = cpf_input_fact(driver)
        self.btn_iniciar: Button = btn_iniciar_fact(driver)
        self._cpf = kwargs.get("cpf")

    def preencher_cpf(self):
        self.cpf_input.carregar_elemento()
        self.cpf_input.enviar_caracteres(self._cpf)

    def clicar_botao_iniciar(self):
        self.btn_iniciar.carregar_elemento()
        self.btn_iniciar.elemento.click()
