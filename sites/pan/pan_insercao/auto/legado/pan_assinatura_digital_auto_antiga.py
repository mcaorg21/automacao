"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_auto.py
| data: 2019-12-20
| autor: Gustavo Belleza

| funcionamento:
    Automação da interface do processo de assinatura digital, realizado
    logo após a inserção do contrato. O processo se inicia com a seleção
    (por meio da ADE) da proposta que aguarda assinatura digital. Finaliza
    com o envio de um SMS alertando o cliente quanto à assinatura digital.
"""
from typing import Union
from sites.baseRobos.gui_auto import AutoGUI
from sites.baseRobos.core.uconecte import Uconecte
from time import sleep
from selenium.common.exceptions import TimeoutException
# funções que armazenam e retornam coleções de elementos em list e/ou dict
from sites.pan.pan_insercao.data.colections import localizador


class PanInsercaoAssinaturaAntiga(AutoGUI):
    url_assinatura = ('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb'
                      '/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)

        self.limite_loading = 100
        self.chrome_driver = chrome_driver
        self.by = ""
        self.uconecte = Uconecte()
        self.act.time_out = 10

    def selecionar_proposta(self, n_proposta):
        # EM DESUSO A PARTIR DE 24/01/2020 #
        """
        Seleciona, usando a respectiva ADE, a proposta
        que aguarda assinatura.
        :type n_proposta: str
        """
        print("Iniciando assinatura digital.")

        # Redirecionar Para Assinatura Digital
        self.chrome_driver.get(self.url_assinatura)

        # Buscar Proposta
        print("Buscando proposta:", n_proposta)
        loc_pesquisar, self.by = localizador('input_pesquisar')
        self.act.enviar_texto(loc_pesquisar, n_proposta, self.by)

        loc_bt_pesquisar = localizador('bt_pesquisar')
        self.act.hover_e_clique(loc_bt_pesquisar, self.by)

        self.act.time_out = 10  # carregando

        # Selecionar status
        print("Selecionando proposta.")
        link_assin = localizador('a_status')
        self.act.forcar_clique_stale_element(link_assin, self.by)

    def confirmar_assinatura_digital(self) -> Union[str, bool]:
        """
        Etapas:
        1. Formalização digital: Assinatura Eletrônica -> <a>Assinar</a>.
        2. Como deseja capturar a assinatura?: Enviar link de assinatura -> Continuar.
        3. Enviar link de Assinatura: extrair link, escrever nome e empresa, enviar link
        :return: link da assinatura digital
        :rtype: str
        """
        try:

            self.act.time_out = 10  # carregando
            self.act.trocar_frame_referencia('ctl00_Cph_FrameExterno')

            # FORMALIZAÇÃO DIGITAL
            loc_assinar = '//app-signature-proposals/div/div[3]/app-list-item/div/div[2]/div'
            self.act.hover_e_clique(loc_assinar, self.metodo.XPATH)

            # COMO DESEJA CONTINUAR A ASSINATURA?
            loc_enviar_link_assn = '//pan-radio-option[1]/div'
            self.act.forcar_clique_stale_element(loc_enviar_link_assn, self.metodo.XPATH)

            loc_confirmar = '//pan-button/button'
            self.act.forcar_clique_stale_element(loc_confirmar, self.metodo.XPATH)

            # Obter Link De Assinatura Digital
            print("Extraindo link para assinatura")
            loc_link = '//app-send-link-container/div/div[1]/div[1]/strong'
            texto_link = self.act.obter_texto(loc_link, self.metodo.XPATH)

            # Enviar Link Para Cliente por SMS
            input_link = '//app-send-link-container/div/pan-input/div/input'
            self.act.enviar_texto_intervalado(input_link, 'Marcelo de Castro Amâncio - uConecte', self.metodo.XPATH, delay=0.02)

            sleep(2)

            btn_enviar = '//app-send-link-container/div/div[3]/pan-button/button'
            self.act.hover_e_clique(btn_enviar, self.metodo.XPATH)

            print("Link Assinatura Digital:", texto_link)
            return texto_link

        except:
            return False

    def __verificar_assinaturas_pendentes(self):
        """
        Verfica se há mais de uma assinatura aguardando finalização
        para aquela proposta. Isso implica em uma alteração dos elementos
        web ao longo do processo.
        :return: None
        """
        print("Verificando se há assinaturas pendentes")
        loc_assin = '//app-signature-proposals/div/div[2]/div'

        try:
            assinaturas = self.act.quantidade_elemento(loc_assin, self.by)
            return assinaturas
        except TimeoutException:
            return 1

    def __selecionar_assinaturas_pendentes(self, assinaturas, t=1):
        """
        Caso se verifique a presença de assinaturas pendentes para a
        proposta, serão necessários processos um pouco diferentes
        do que aqueles realizados quando não há pendência, em decorrência
        de diferença nos elementos web.
        :param assinaturas: quantidade de assinaturas pendentes
        :type assinaturas: int
        :param t: limite de recursões
        :type t: int
        :return: None
        """
        try:
            sleep(3)
            print(f"{assinaturas} assinaturas pendentes...")
            print("Selecionando assinatura digital.")

            # Escolher Tipo de Formalização -> Digital
            loc_assinar = '//app-signature-proposals/div/div[3]/app-list-item/div/div[2]'
            self.act.forcar_clique_stale_element(loc_assinar,
                                                 self.by, t_max=8)

            # Determinar se Via Link ou WebCam -> Link
            print("Assinatura via Link")
            loc_radio_assinar = '//pan-radio-option[1]/div/label/div[2]/p[1]'
            self.act.forcar_clique_stale_element(loc_radio_assinar, self.by)

        except TimeoutException:
            print("Erro ao buscar elemento, tentando novamente")
            if t < 5:
                self.__selecionar_assinaturas_pendentes(assinaturas, t+1)
            else:
                raise Exception("Erro ao buscar elemento!")

    def __selecionar_assinatura_digital(self, t=1):
        """
        Automação do início do processo de assinatura digital
        nos casos em que não há pendências de assinaturas.
        :type t: int
        :return: None
        """
        try:
            sleep(3)
            print("Selecionando assinatura digital.")

            # Escolher Tipo de Formalização -> Digital
            loc_assinar = '//app-signature-proposals/div/div[3]/app-list-item/div/div[2]'
            self.act.forcar_clique_stale_element(loc_assinar,
                                                 self.by, t_max=8)

            # Determinar se Via Link ou WebCam -> Link
            print("Assinatura via Link")
            loc_radio_assinar = '//pan-radio-option[1]/div/label/div[2]/p[1]'
            self.act.forcar_clique_stale_element(loc_radio_assinar, self.by)

        except TimeoutException:
            print("Erro ao buscar elemento, tentando novamente")
            if t < 5:
                self.__selecionar_assinatura_digital(t=1)
            else:
                raise Exception("Erro ao buscar elemento!")
