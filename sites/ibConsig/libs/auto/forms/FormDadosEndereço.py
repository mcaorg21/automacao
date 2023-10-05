from selenium.common.exceptions import ElementNotInteractableException, InvalidElementStateException

from sites.baseRobos.core.data_helpers import similaridade
from sites.elementos import TextInput, Select, CheckBox, sleep
from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato


class FormDadosEndereco:
    def __init__(self, contrato: Contrato, **kwargs):
        self.dados: Contrato = contrato
        self.iptCep: TextInput = kwargs.get("iptCep")
        self.cBoxSemNumero: CheckBox = kwargs.get("cBoxSemNumero")
        self.iptNumero: TextInput = kwargs.get("iptNumero")
        self.iptLogradouro: TextInput = kwargs.get("iptLogradouro")
        self.iptLogradouro2: TextInput = kwargs.get("iptLogradouro2")
        self.iptBairro: TextInput = kwargs.get("iptBairro")
        self.iptBairro2: TextInput = kwargs.get("iptBairro2")
        self.iptComplemento: TextInput = kwargs.get("iptComplemento")
        self.iptDddTel: TextInput = kwargs.get("iptDddTel")
        self.iptNoTel: TextInput = kwargs.get("iptNoTel")
        self.iptDddCel: TextInput = kwargs.get("iptDddCel")
        self.iptNoCel: TextInput = kwargs.get("iptNoCel")

    @property
    def logradouroSemNumero(self):
        return str(self.dados.endereco.numero) == ""

    def preencherCep(self, carregarElemento=True):
        print(f"Preenchendo CEP: {self.dados.endereco.cep}")
        try:
            if carregarElemento:
                self.iptCep.carregar_elemento()
            self.iptCep.act.click()
            self.iptCep.enviar_texto(self.dados.endereco.cep)
        except ElementNotInteractableException:
            print("Não foi possível preencher o campo. Tentando novamente.")
            sleep(0.5)
            self.preencherCep(carregarElemento=False)

    def marcarSemNumero(self):
        print(f"Marcando logradouro sem número")
        self.cBoxSemNumero.carregar_elemento()
        if self.cBoxSemNumero.estaMarcado:
            self.cBoxSemNumero.marcar()

    def preencherNumero(self):
        print(f"Preenchendo Número: {self.dados.endereco.numero}")
        self.iptNumero.carregar_elemento()
        #self.iptNumero.act.click()
        self.iptNumero.enviar_texto(self.dados.endereco.numero)
        #self.iptNumero.press_TAB()

    def preencherLogradouro(self):
        try:
            print(f"Preenchendo Logradouro: {self.dados.endereco.logradouro}")
            self.iptLogradouro.carregar_elemento()
            texto: str = self.iptLogradouro.act.get_attribute("value")
            print(texto, self.dados.endereco.logradouro)
            if similaridade(texto, self.dados.endereco.logradouro) >= 85:
                return
            self.iptLogradouro.act.click()
            self.iptLogradouro.apagar_caracteres(20, delay=0.01)
            self.iptLogradouro.enviar_texto(self.dados.endereco.logradouro, clear=False)
        except InvalidElementStateException:
            print("Não foi possível preencher o campo. Tentando novamente.")
            sleep(0.5)
            self.preencherLogradouro()

    def preencherLogradouro2(self):
        print(f"Preenchendo Logradouro2: {self.dados.endereco.logradouro}")
        self.iptLogradouro2.carregar_elemento()
        self.iptLogradouro2.act.click()
        self.iptLogradouro2.enviar_texto(self.dados.endereco.logradouro)
        self.iptLogradouro2.press_TAB()

    def preencherBairro(self):
        print(f"Preenchendo Bairro: {self.dados.endereco.bairro}")
        
        try:
            bairro = self.iptBairro
            bairro.carregar_elemento()
        except:
            bairro = self.iptBairro2
            bairro.carregar_elemento()
        
        texto: str = bairro.act.get_attribute("value")

        print(texto, self.dados.endereco.bairro)
        if similaridade(texto, self.dados.endereco.bairro) >= 85:
            return
        bairro.act.click()
        bairro.apagar_caracteres(20, delay=0.01)
        bairro.enviar_texto(self.dados.endereco.bairro, clear=False)

    def preencherBairro2(self):
        print(f"Preenchendo Bairro2: {self.dados.endereco.bairro}")
        self.iptLogradouro2.carregar_elemento()
        self.iptLogradouro2.act.click()
        self.iptLogradouro2.enviar_texto(self.dados.endereco.bairro)
        self.iptLogradouro2.press_TAB()

    def preencherComplemento(self):
        print(f"Preenchendo Complemento: {self.dados.endereco.complemento}")
        self.iptComplemento.carregar_elemento()
        #self.iptComplemento.act.click()
        self.iptComplemento.enviar_texto(self.dados.endereco.complemento)
        #self.iptComplemento.press_TAB()

    def preencheDddTelefone(self):
        print(f"Preenchendo DDD Telefone: {self.dados.endereco.dddTelefone}")
        self.iptDddTel.carregar_elemento()
        #self.iptDddTel.act.click()
        self.iptDddTel.enviar_texto(self.dados.endereco.dddTelefone)
        #self.iptDddTel.press_TAB()

    def preencheNoTelefone(self):
        print(f"Preenchendo Numero Telefone: {self.dados.endereco.numeroTelefone}")
        self.iptNoTel.carregar_elemento()
        #self.iptNoTel.act.click()
        self.iptNoTel.enviar_texto(self.dados.endereco.numeroTelefone)
        #self.iptNoTel.press_TAB()

    def preencheDddCelular(self):
        print(f"Preenchendo DDD Celular: {self.dados.endereco.dddCelular}")
        self.iptDddCel.carregar_elemento()
        #self.iptDddCel.act.click()
        self.iptDddCel.enviar_texto(self.dados.endereco.dddCelular)
        #self.iptDddCel.press_TAB()

    def preencheNoCelular(self):
        print(f"Preenchendo Numero Celular: {self.dados.endereco.numeroCelular}")
        self.iptNoCel.carregar_elemento()
        #self.iptNoCel.act.click()
        self.iptNoCel.enviar_texto(self.dados.endereco.numeroCelular)
        #self.iptNoCel.press_TAB()
