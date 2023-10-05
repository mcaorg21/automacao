from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from time import sleep
from sites.baseRobos.core.data_helpers import strip_zero_left


class DadosEndereco(AutoGUI):
    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver)
        self.endereco: dict = dados.get('endereco', None)
        self.__cep = self.endereco.get('cep', None)
        self.__numero = self.endereco.get('numero', None)
        self.__sn = self.__numero == "0"
        self.__logradouro = self.endereco.get('logradouro', None)
        self.__bairro = self.endereco.get('bairro', None)
        self.__complemento = self.endereco.get('complemento', None)
        self.__tel: dict = dados.get('telefone', None)
        self.__ddd_telefone = self.__tel.get('ddd', None)
        self.__num_telefone = self.__tel.get('numero', None)
        self.__cel: dict = dados.get('celular1', None)
        self.__ddd_celular = self.__cel.get('ddd', None)
        self.__num_celular = self.__cel.get('numero', None)
        self.act.time_out = 0.2

    @property
    def logradouro_sem_numero(self):
        return self.__sn

    def preencher_cep(self):
        print("CEP:", self.__cep)
        self.sh.atribuir_valor_campo_jquery(
            "#endereco\\\\.cep", self.__cep)

    def executar_busca_cep(self, wait=5):
        script = "buscaCepAjax()"
        self.chrome_driver.execute_script(script)
        sleep(wait)

    def preencher_numero(self):
        print("Numero:", self.__numero)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.numero', self.__numero)

    def check_sem_numero(self):
        print("Logradouro sem número.")
        loc = '#logradouroSemNumeroCheck'
        if not self.act.check_box_is_checked(loc):
            self.act.clicar_elemento(loc)

    def preencher_logradouro(self):
        self.__logradouro = self.excluir_reticencias_end(self.__logradouro)
        print("Logradouro:", self.__logradouro)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.logradouro2', self.__logradouro)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.logradouro', self.__logradouro)

    def preencher_bairro(self):
        self.__bairro = self.excluir_reticencias_end(self.__bairro)
        print("Bairro:", self.__bairro)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.bairro2', self.__bairro)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.bairro', self.__bairro)

    def preencher_complemento(self):
        print("Complemento:", self.__complemento)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.complemento', self.__complemento)

    def preencher_ddd_telefone(self):
        print("DDD:", self.__ddd_telefone)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.telefone\\\\.ddd', self.__ddd_telefone)

    def preencher_numero_telefone(self):
        print("Telefone:", self.__num_telefone)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.telefone\\\\.numero', self.__num_telefone)

    def preencher_ddd_celular(self):
        print("Celular DDD:", self.__ddd_celular)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.telefoneCelular1\\\\.ddd', self.__ddd_celular)

    def preencher_numero_celular(self):
        print("Celular:", self.__num_celular)
        self.sh.atribuir_valor_campo_jquery(
            '#endereco\\\\.telefoneCelular1\\\\.numero', self.__num_celular)

    @staticmethod
    def excluir_reticencias_end(endereco: str) -> str:
        aux = endereco.replace(".", "", 3)
        return aux
