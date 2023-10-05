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


class PanInsercaoAssinaturaAuto(AutoGUI):
    url_assinatura = ('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb'
                      '/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)

        self.limite_loading = 100
        self.chrome_driver = chrome_driver
        self.by = ""
        self.uconecte = Uconecte()
        self.act.time_out = 5

    def selecionar_proposta(self, n_proposta: str):
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

    def confirmar_assinatura_digital(self, recr: int = 1) -> Union[str, bool]:
        """
        Formaliza o processo de assinatura por via digital
        utilizando o link que será extraído ao fim do processo.
        Termina com o envio do link de assinatura para o cliente.
        :return: link da assinatura digital
        """

        sleep(4)
        self.act.trocar_frame_referencia('ctl00_Cph_FrameExterno')
        try:
            loc_pular_escolha_doc = '//*[@id="Pular_DOC"]/button'
            self.act.nao_esta_presente_recursivo(loc_pular_escolha_doc, self.metodo.XPATH)
            # ENVIE UM DOCUMENTO COM FOTO
            self.act.hover_e_clique(loc_pular_escolha_doc, self.metodo.XPATH)
        except TimeoutException:
            print("Pulando para modo de assinatura")
        loc_assinaturas = '//platform-ui-card/div/div[1]/div[2]/div'
        if self.act.quantidade_elemento(loc_assinaturas, self.metodo.XPATH) > 1:
            loc_continuar = '//*[@id="Continuar_Overview"]/button'
            self.act.hover_e_clique(loc_continuar, self.metodo.XPATH)

        # COMO DESEJA CAPTURAR A ASSINATURA
        print("Selecionando forma de assinatura -> Link")
        selec_link = '//*[@id="Sig_Opt_1"]/label/i'
        self.act.hover_e_clique(selec_link, self.metodo.XPATH)

        print("Confirmar assinatura por link.")
        loc_confirmar = '//*[@id="Continuar_Sig_Opt"]/button'
        self.act.hover_e_clique(loc_confirmar, self.metodo.XPATH)

        # ENVIAR LINK ASSINATURA DIGITAL
        print("Preenchendo nome do vendedor.")
        loc_nome_vend = 'input[placeholder="Nome do vendedor"]'
        self.act.hover_e_clique(loc_nome_vend)
        self.act.enviar_texto(loc_nome_vend, 'Marcelo Amâncio Castro')

        print("Preenchendo nome da empresa.")
        loc_nome_empr = 'input[placeholder="Nome da empresa/loja"]'
        self.act.hover_e_clique(loc_nome_empr)
        self.act.enviar_texto(loc_nome_empr, 'uConecte')

        # Obter Link De Assinatura Digital
        print("Extraindo link para assinatura")
        loc_link = 'input[placeholder="Link de assinatura"]'
        texto_link = self.act.obter_atributo(loc_link, 'value')

        print(texto_link)

        print("Continuar envio...")
        loc_continuar = '//*[@id="Continuar_Envio"]/button'
        self.act.hover_e_clique(loc_continuar, self.metodo.XPATH)

        print("Concluir assinatura digital")
        loc_concluir = '//*[@id="Continuar_Overview"]/button'
        self.act.hover_e_clique(loc_concluir, self.metodo.XPATH)

        if self.act.esta_presente(loc_concluir):
            sleep(3)
            self.act.forcar_clique_stale_element(loc_concluir)

        sleep(3)

        print("Link Assinatura Digital:", texto_link)

        # Verificar se houve erro na assinatura, se sim, tentar novamente
        loc_btn_tentar_novamanete = '//*[@id="Tentar_Novamente"]/button'
        if self.act.esta_presente(loc_btn_tentar_novamanete, self.metodo.XPATH) and recr < 2:
            self.act.forcar_clique_stale_element(loc_btn_tentar_novamanete, self.metodo.XPATH)
            return self.confirmar_assinatura_digital(recr+1)
        elif recr >= 2:
            raise Exception("Problema na aplicação.")

        return texto_link


    def __verificar_assinaturas_pendentes(self):
        """
        Verfica se há mais de uma assinatura aguardando finalização
        para aquela proposta. Isso implica em uma alteração dos elementos
        web ao longo do processo.
        :return: None
        """
        print("Verificando se há assinaturas pendentes")
        loc_assin = localizador('divs_multi_ass')

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
            loc_assinar = localizador('div_assinar')
            self.act.forcar_clique_stale_element(loc_assinar,
                                                 self.by, t_max=8)
            sleep(3)
            # Determinar se Via Link ou WebCam -> Link
            print("Assinatura via Link")
            loc_radio_assinar = localizador('radio_assin_multi_assin')
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

            loc_assin_elet = localizador('div_form')
            self.act.hover_e_clique(loc_assin_elet, self.by)

            sleep(3)
            print("Assinatura via Link")
            # Determinar se Via Link ou WebCam -> Link
            radio_assinatura = localizador('radio_assinatura')
            self.act.hover_e_clique(radio_assinatura, self.by)

        except TimeoutException:
            print("Erro ao buscar elemento, tentando novamente")
            if t < 5:
                self.__selecionar_assinatura_digital(t=1)
            else:
                raise Exception("Erro ao buscar elemento!")
