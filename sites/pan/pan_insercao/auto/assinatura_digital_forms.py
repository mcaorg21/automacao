"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: assinatura_digital_forms
| data: 2020-02-10
| autor: Gustavo Belleza

| funcionamento:
"""

# SuperClasse herdada por todas as outras classes que implementam automação da interface.
from sites.baseRobos.gui_auto import AutoGUI

# Exceptions nativas do Selenium
from selenium.common.exceptions import (
    StaleElementReferenceException, NoAlertPresentException,
    UnexpectedAlertPresentException, TimeoutException,
    InvalidElementStateException
)
# Funções auxiliares
from sites.baseRobos.core.data_helpers import similaridade
from sites.baseRobos.core.data_helpers import is_number
from sites.baseRobos.core.uconecte import Uconecte

# Função que retorna todas as mensagens de erro já documentadas no site.
from sites.pan.pan_insercao.data.colections import mensagens_alertas

# stdlib
import re
from time import sleep


class PanFormAssinaturaDigital(AutoGUI):

    url_assinatura = ('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb'
                      '/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 6

    @property
    def url(self):
        return self.url_assinatura

    def input_texto_pesquisar_proposta(self, n_proposta: str):
        print("Buscando proposta:", n_proposta)
        loc_pesquisar = '//*[@id="ctl00_Cph_AprCons_txtPesquisa_CAMPO"]'
        self.act.enviar_texto(loc_pesquisar, n_proposta, self.by.XPATH)

    def botao_pesquisar_proposta(self):
        loc_bt_pesquisar = '//*[@id="btnPesquisar_txt"]'
        self.act.hover_e_clique(loc_bt_pesquisar, self.by.XPATH)

    def selecionar_proposta_assinatura(self):
        print("Selecionando proposta.")
        link_assin = ('//*[@id="ctl00_Cph_AprCons_grdConsulta"]'
                      '/tbody/tr[2]/td[6]/a')
        for i in range(10):
            try:
                sleep(2)
                self.act.clicar_elemento(link_assin, self.by.XPATH)
            except Exception:
                return

    def botao_pular_envio_docs(self):
        print("Pulando tela de envio de documentação.")
        try:
            sleep(5)
            loc_pular_escolha_doc = '//*[@id="Pular_DOC"]/button'
            self.act.hover_e_clique(loc_pular_escolha_doc, self.metodo.XPATH)
        except TimeoutException:
            print("Tela de envio de documentação "
                  "ausente. Seguindo assinatura.")

    def verificar_abertura_assinatura_digital(self):
        loc1 = '//*[@id="Pular_DOC"]/button'
        loc2 = '//*[@id="Sig_Opt_1"]/label/div/p[1]'
        check1 = self.act.esta_presente(loc1, self.by.XPATH)
        check2 = self.act.esta_presente(loc2, self.by.XPATH)

        i = 0

        while not check1 and not check2:
            print(f"[{i}]Aguaradando presença modal de assinatura digital")
            check1 = self.act.esta_presente(loc1, self.by.XPATH)
            check2 = self.act.esta_presente(loc2, self.by.XPATH)
            i += 1

    def selecionar_assinatura_via_link(self):
        print("Selecionando forma de assinatura -> Link")
        selec_link = '//*[@id="Sig_Opt_1"]/label/i'
        self.act.hover_e_clique(selec_link, self.metodo.XPATH)

    def confirmar_assinatura_via_link(self):
        print("Confirmar assinatura por link.")
        loc_confirmar = '//*[@id="Continuar_Sig_Opt"]/button'
        self.act.hover_e_clique(loc_confirmar, self.metodo.XPATH)

    def preencher_nome_vendedor(self):
        print("Preenchendo nome do vendedor.")
        loc_nome_vend = 'input[placeholder="Nome do vendedor"]'
        self.act.hover_e_clique(loc_nome_vend)
        self.act.enviar_texto(loc_nome_vend, 'Marcelo Amâncio Castro')

    def preencher_nome_empresa(self):
        print("Preenchendo nome da empresa.")
        loc_nome_empr = 'input[placeholder="Nome da empresa/loja"]'
        self.act.hover_e_clique(loc_nome_empr)
        self.act.enviar_texto(loc_nome_empr, 'uConecte')

    def obter_link_assinatura_digital(self):
        print("Extraindo link para assinatura")
        loc_link = 'input[placeholder="Link de assinatura"]'
        texto_link: str = self.act.obter_atributo(loc_link, 'value')
        print(texto_link)

        return texto_link

    def confirmar_envio_de_link(self):
        print("Continuar envio...")
        loc_continuar = '//*[@id="Continuar_Envio"]/button'
        self.act.hover_e_clique(loc_continuar, self.metodo.XPATH)

    def concluir_assinatura_digital(self):
        print("Concluir assinatura digital")
        loc_concluir = '//*[@id="Continuar_Overview"]/button'
        self.act.hover_e_clique(loc_concluir, self.metodo.XPATH)

        if self.act.esta_presente(loc_concluir):
            sleep(3)
            self.act.forcar_clique_stale_element(loc_concluir)

    def verificar_erro_tentar_novamente(self) -> bool:
        # Verificar se houve erro na assinatura, se sim, tentar novamente
        loc_btn_tentar_novamanete = '//*[@id="Tentar_Novamente"]/button'
        if self.act.esta_presente(loc_btn_tentar_novamanete, self.metodo.XPATH):
            self.act.forcar_clique_stale_element(loc_btn_tentar_novamanete, self.metodo.XPATH)
            return True

        return False
