from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from time import sleep
from selenium.common.exceptions import (
    TimeoutException, ElementNotInteractableException,
)

import pdb


class DadosBancarios(AutoGUI):
    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver=driver)
        self.__forma_credito = dados.get('formaCredito', None)
        self.__n_banco = dados['banco']['numeroBanco']
        self.__n_agencia = dados['banco']['agencia']
        self.__prazo_contrato = dados['prazoContrato']
        self.__numero_conta = dados['banco']['numeroConta']
        self.__dv_conta = dados['banco']['digitoConta']
        self.__finalidade_credito = dados['finalidadeCredito']
        self.act.time_out = 0.2
        self.wait = 0.4

    @property
    def is_ordem_pagto(self):
        return self.__forma_credito == '3'

    def preencher_forma_credito(self):
        print("Forma de crédito:", self.__forma_credito)
        self.sh.atribuir_valor_campo_jquery(
            seletor="#dadosBancarios\\\\.formaCredito",
            valor=str(self.__forma_credito), change=True
        )

    def selecionar_ordem_pagto(self):
        print("Ordem de pagto.")
        loc_banco = '[id="dadosBancarios.numeroOrdemPagamento"]'
        try:
            self.act.select_drop_down(loc_banco, '4')
        except:
            pass
            self.act.select_drop_down(loc_banco, '3')



    def preencher_numero_banco(self):
        print("Numero do banco", self.__n_banco)
        loc_bnc = '[id="dadosBancarios.numeroBanco"]'
        try:
            self.act.enviar_caracteres(
                seletor=loc_bnc, texto=self.__n_banco,
                clear=False, delay=0.05
            )
        except ElementNotInteractableException as e:
            print(f"{self.__class__.__name__}.preencher_numero_banco: {e.msg}")
            sleep(0.5)
            self.preencher_numero_banco()

    def executar_busca_banco(self, wait=1):
        print("Executando busca por tipo do benefício...")
        script = "buscaBancoAjax()"
        #sleep(wait)
        self.chrome_driver.execute_script(script)
        #sleep(wait)

    def preencher_numero_agencia(self):
        print("Numero agencia:", self.__n_agencia)
        loc_ag = '[id="dadosBancarios.agencia"]'
        self.act.forcar_clique_stale_element(loc_ag, pause=0)
        #sleep(self.wait)
        self.act.enviar_caracteres(
            seletor=loc_ag, texto=self.__n_agencia,
            clear=False, delay=0.05
        )

    def executar_busca_agencia(self, wait=1):
        print("Executando busca por tipo do benefício...")
        script = "buscaAgenciaAjax()"

        #sleep(wait)
        self.chrome_driver.execute_script(script)
        #sleep(wait)

    def verificar_erro_agencia(self) -> str:
        try:
            erro_agencia = '[id="erroAgencia"]'
            texto_erro_ag = self.act.obter_texto(erro_agencia)
            print("ERRO", texto_erro_ag)

            return texto_erro_ag
        except TimeoutException:
            print("Agencia preenchida")
            return ""

    def preencher_prazo_contrato(self):
        print("Prazo do contrato:", self.__prazo_contrato)
        loc = "#ade\\\\.quantidadePrestacoes"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__prazo_contrato, change=True
        )

    def preencher_numero_conta(self):
        print("Preenchendo numero da conta:", self.__numero_conta)
        loc = "#dadosBancarios\\\\.conta"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__numero_conta
        )

    def preencher_digito_conta(self):
        print("Preenchendo digito da conta:", self.__dv_conta)
        loc = "#dadosBancarios\\\\.contaDv"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__dv_conta
        )

    def preencher_finalidade_credito(self):
        print("Finalidade de crédito", self.__finalidade_credito)
        loc = "#dadosBancarios\\\\.finalidadeCredito"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__finalidade_credito
        )
