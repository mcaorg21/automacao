"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: auxiliares
| data: 2020-03-16
| autor: Gustavo Belleza

| funcionamento:
"""
from sites.baseRobos.core.captcha import TwoCaptcha

from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver import Chrome
from ..data.collections import (
    registro_erros_form_identificacao, registro_erros_forms_refin
)
import re
from time import sleep
from sites.baseRobos.gui_auto import AutoGUI
from sites.ibConsig.libs.exceptions.Exceptions import *


def selecionar_opcao_modal_formulario(driver: Chrome):
    texto_modal = ""
    modal = driver.execute_script(
        """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').find('a:contains("Não")').length""")

    if (modal == 1):
        texto_modal = driver.execute_script(
            """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').text()""")
        driver.execute_script(
            """$('#identificacao-form\\\\:modalDialog').find('a:contains("Sim")').click()""")
        sleep(5)

    return modal, texto_modal


def filtrar_tabela_carencia(tx_origem: float, novo_margem: bool=None):
    select_val = 0
    print("Taxa:", tx_origem)
    # Comparar Taxa de Juros com Taxas da Tabela
    if novo_margem:
        if tx_origem >= 2.03:
            select_val = 1283
        elif tx_origem >= 1.89:
            select_val = 1284
    else:
        if tx_origem > 2.03:
            select_val = 2109
        elif tx_origem >= 1.99:
            select_val = 2122
        elif tx_origem >= 1.84:
            select_val = 2176
        elif tx_origem >= 1.72:
            select_val = 2208
        elif tx_origem >= 1.56:
            select_val = 2286
        elif tx_origem >= 1.40:
            select_val = 7873
    print('Select val:', select_val)
    return str(select_val)


def aguardar_loading(act: SeleniumActions, by: By):
    loc = '//*[@id="waitDiv"]/center/img'
    act.esta_presente_recursivo(loc, by.XPATH)


def fechar_modal_portabilidade(act: SeleniumActions):
    try:
        act.fechar_janela(ordem_janela=1)
        act.trocar_janela(idx_janela=0)
        act.trocar_frame_referencia("rightFrame")
    except Exception:
        pass


def tratar_erros_formulario_refinanciamento(act: SeleniumActions, captcha: TwoCaptcha, id_captcha: int):
    mensagem_erro: str
    try:
        loc_erro = '[id="global-msg"]'
        sleep(2)
        mensagem_erro: str = act.obter_texto(loc_erro)
        mensagem_erro = mensagem_erro.strip()
    except TimeoutException:
        return False

    if not mensagem_erro:
        return

    mensagens = registro_erros_form_identificacao()

    for mensagem in mensagens:
        regex = re.compile(mensagem['texto'])
        erro_encontrado = regex.search(mensagem_erro)

        if not erro_encontrado:
            continue

        if 'aprovar' in mensagem:
            print("Captcha Aprovado")
            captcha.mudar_status_captcha(id_captcha, '1')
        else:
            print("[CR] Catpcha Recusado")
            captcha.mudar_status_captcha(id_captcha, '2')
            raise CaptchaRecusadoException("Captcha recusado")
        if 'preencher' in mensagem:
            raise CaptchaRecusadoException("Captcha Recusado")

        if 'finalizar' in mensagem or 'localizar' in mensagem or 'localizado' in mensagem:
            raise NotFoundResultException(mensagem_erro)


def tratar_alerts_refinanciamento(driver: Chrome, act: SeleniumActions, texto_alerta: str = False):
    import re
    if not texto_alerta:
        try:
            alert = driver.switch_to.alert
            texto_alerta = alert.text

        except Exception:
            return

    print("Mensagem encontrada: {}".format(texto_alerta))

    mensagens = registro_erros_forms_refin()

    for mensagem in mensagens:
        if 'Sistema temporariamente indisponível' in mensagem['texto']:
            driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
            return -1

        regex = re.compile(mensagem['texto'])
        alerta_encontrado = regex.search(texto_alerta)

        if not alerta_encontrado:
            continue
        try:
            act.manusear_alerta('aceitar')
        except UnexpectedAlertPresentException:
            act.manusear_alerta('aceitar')

        act.fechar_alertas_recursivamente()
        print("depois tentar fechar", mensagem)
        if 'selecionar' in mensagem:
            raise RefinIndisponivelException(
                "Não foi possível escolher o refinanciamento")

        if 'restricao' in mensagem:
            print(mensagem)
            act.fechar_alertas_recursivamente()
            raise RestricaoException(mensagem)

        if 'localizar' in mensagem:
            raise NotFoundResultException(mensagem)

        if 'return' in mensagem:
            return

    input('Não identificou a mensagem: {}'.format(texto_alerta))


def filtrar_entidade(dados):

    entidade: str = ''

    if 'estadual' in dados:
        if dados['sigla'] == 'MT':
            entidade = '243'
        elif dados['sigla'] == "SP":
            entidade = "4195-1"
            if dados["orgao"] in ["66", "67"]:
                entidade = "4193"
            elif dados["orgao"] in ["80", "81"]:
                entidade = "4194"
        elif dados['sigla'] == "RJ":
            entidade = "1"

    elif 'federal' in dados:
        entidade = "164"
    elif 'municipal' in dados and dados['cidade'] == "São Paulo":
        entidade = "128"
    elif 'municipal' in dados and dados['cidade'] == "Recife":
        entidade = "2542"
    elif 'municipal' in dados and dados['cidade'] == "Curitiba":
        entidade = "3392"
    elif 'municipal' in dados and dados['cidade'] == "Aracaju":
        entidade = "3267"
    elif 'municipal' in dados and dados['cidade'] == "Santa Cruz do Sul":
        entidade = "4169"
    elif 'inss' in dados:
        entidade = "1581"

    return entidade


class GerenciarSessao(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.estado = 0
        self.cond_login: bool = False

    @property
    def estado_atual(self):
        return self.estado

    def verificar_estado(self):
        if not self.cond_login:
            print("Usuário não está logado.")
            self.estado = 0
        else:
            print("Usuário está logado.")
            self.estado = 1
        self.resolver_estado()

    def resolver_estado(self):
        print("Resolvendo estado...")
        if self.estado == 0:
            print("Interrompendo processos...")
            raise Exception("[SESSION] Necessário carregar novos cookies")
        elif self.estado == 1:
            print("Seguindo execução das tarefas.")

    def aguardar_load_cookies(self, cks_path: str, max_cnt: int=50):
        cnt = 0

        while not self.cond_login and cnt < max_cnt:
            self.sh.load_cookies(cks_path)
            print("Aguardando cookies...")
            self.chrome_driver.refresh()
            sleep(10)
            cnt += 1

        if cnt > max_cnt:
            raise Exception("[SESSION]Tempo para carregar cookies excedido.")
