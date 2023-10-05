from selenium.common.exceptions import ElementNotInteractableException

from sites.elementos import TextInput, Select
from sites.ibConsig.libs.dto.Contrato import Contrato

import time,pdb

class FormDadosBancarios:
    def __init__(self, contrato: Contrato, **kwargs):
        self._dados: Contrato = contrato
        self.selFormaCredito: Select = kwargs.get("selFormaCredito")
        self.bancoOp: Select = kwargs.get("bancoOp")
        self.iptCodigoBanco: TextInput = kwargs.get("iptCodigoBanco")
        self.iptNoAgencia: TextInput = kwargs.get("iptNoAgencia")
        self.iptDvAgencia: TextInput = kwargs.get("iptDvAgencia")
        self.selContaCredito: Select = kwargs.get("selContaCredito")
        self.iptNoConta: TextInput = kwargs.get("iptNoConta")
        self.iptDvConta: TextInput = kwargs.get("iptDvConta")

    def selecionarFormaCredito(self):
        print(f"Selecionando Forma Crédito: {self._dados.banco.formaCredito}")

        self.selFormaCredito.carregar_elemento()
        self.selFormaCredito.selecionar_opcao(self._dados.banco.formaCredito)

    def preencherCodigoBanco(self):
        print(f"Preenchendo Codigo Banco: {self._dados.banco.numeroBanco}")
        try:
            if(self._dados.banco.formaCredito == '3'):
                self.bancoOp.carregar_elemento()
                self.bancoOp.selecionar_opcao('4')
            else:
                self.iptCodigoBanco.carregar_elemento()
                #self.iptCodigoBanco.act.click()
                self.iptCodigoBanco.enviar_caracteres(self._dados.banco.numeroBanco,0.2)          
        except ElementNotInteractableException:
            print("Não foi possível preencher o campo. Tentando novamente...")
            self.preencherCodigoBanco()

    def preencherNoAgencia(self):
        print(f"Preenchendo No Agencia: {self._dados.banco.agencia}")

        self.iptNoAgencia.carregar_elemento()
        self.iptNoAgencia.act.click()
        self.iptNoAgencia.enviar_texto(self._dados.banco.agencia)
        self.iptNoAgencia.press_TAB()

    def verificar_erro_agencia(self) -> str:
        try:
            erro_agencia = '[id="erroAgencia"]'
            texto_erro_ag = self.act.obter_texto(erro_agencia)
            print("ERRO", texto_erro_ag)

            return texto_erro_ag
        except TimeoutException:
            print("Agencia preenchida")
            return ""

    def preencherDvAgencia(self):
        print(f"Preenchendo DV Agencia: {self._dados.banco.digitoAgencia}")

        self.iptDvAgencia.carregar_elemento()
        #self.iptDvAgencia.act.click()
        self.iptDvAgencia.enviar_texto(self._dados.banco.digitoAgencia)
        #self.iptDvAgencia.press_TAB()

    def selecionarContaCredito(self):
        if(self._dados.banco.formaCredito == '3'):
            print(f"OP não irá preencher tipo de conta...")   
        else:
            print(f"Selecionando Conta Credito: {self._dados.banco.finalidadeCredito}")

            self.selContaCredito.carregar_elemento()
            self.selContaCredito.selecionar_opcao(self._dados.banco.finalidadeCredito)

    def preencherNoConta(self):
        if(self._dados.banco.formaCredito == '3'):
            print(f"OP não irá preencher conta...")   
        else:
            print(f"Preenchendo No Conta: {self._dados.banco.numeroConta}")

            self.iptNoConta.carregar_elemento()
            #self.iptNoConta.act.click()
            self.iptNoConta.enviar_texto(self._dados.banco.numeroConta)
            self.iptNoConta.press_TAB()

    def preencherDvConta(self):
        if(self._dados.banco.formaCredito == '3'):
            print(f"OP não irá preencher dígito de conta...") 
        else:
            print(f"Preenchendo DV Conta: {self._dados.banco.digitoConta}")

            self.iptDvConta.carregar_elemento()
            #self.iptDvConta.act.click()
            self.iptDvConta.enviar_caracteres(self._dados.banco.digitoConta,0.2)
            #self.iptDvConta.enviar_texto(self._dados.banco.digitoConta)
            #self.iptDvConta.press_TAB()
