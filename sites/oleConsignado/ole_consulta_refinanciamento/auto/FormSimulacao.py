from random import randint
from typing import AnyStr, Match, Iterator

from sites.oleConsignado.libs.elementos.Botoes import btn_especie_beneficio
from sites.oleConsignado.libs.elementos.TextInputs import input_especie_beneficio, \
    input_codigo_orgao
from sites.oleConsignado.libs.tratar_infos_site import verificar_div_erro
from sites.oleConsignado.ole_consulta_refinanciamento.domain.Solicitacao import Solicitacao
from sites.elementos import Button, Chrome
from sites.elementos import TextInput


class FormSimulacao:

    def __init__(self, driver: Chrome, solicitacao: Solicitacao):
        self.sol: Solicitacao = solicitacao
        self.__driver = driver

    def preenchido_automaticamente(self):
        return self.sol.orgao == "79" or self.sol.sigla == "MT"

    def preencher_especie_beneficio(self):
        text_input: TextInput = input_especie_beneficio(self.__driver)

        if not text_input.esta_vazio():
            return

        button: Button = btn_especie_beneficio(self.__driver)
        if not button.disabled():
            button.hover_e_clique(pause=0.1)

        if not text_input.disabled():
            text_input.enviar_caracteres(
                self.sol.especieBeneficio, delay=randint(10, 30)/700)
            text_input.press_ENTER()

    def preencher_codigo_orgao(self):
        text_input: TextInput = input_codigo_orgao(self.__driver)

        if not text_input.esta_vazio():
            return

        text_input.enviar_caracteres(self.sol.orgao, delay=0.1)
        text_input.press_TAB()

    def codigos_orgao_div_erro(self) -> Iterator[Match[AnyStr]]:
        import re
        erro: str = verificar_div_erro(self.__driver)
        if not erro:
            return []

        pattern = r"(\d{4,6})"
        yield re.finditer(pattern, erro, re.MULTILINE)
