"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: anexar_docs_forms
| data: 2020-03-10
| autor: Gustavo Belleza

| funcionamento:
"""
# SuperClasse herdada por todas as outras classes que implementam automação da interface.
from sites.baseRobos.gui_auto import AutoGUI

# Exceptions nativas do Selenium

# Funções auxiliares
from sites.baseRobos.core.uconecte import Uconecte

# stdlib
from sites.baseRobos.core.data_helpers import download
from time import sleep
from pathlib import Path

import PATHS


class PanFormBuscarProposta(AutoGUI):
    """
    Implementa métodos para coletar do site o STATUS, a SITUAÇÃO e o TIPO DE ASSINATURA da proposta,
    que serão armazenados nas respectivas variáveis de instância. Implementa também métodos para
    pesquisa o número da proposta e abrir o modal de anexos.
    """
    __url_assinatura = ('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb'
                        '/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

    def __init__(self, chrome_driver, **kwargs):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 10
        self.nr_proposta: str = kwargs.get("ade", None)
        self.situacao: str = ''
        self.tipo_assn: str = ''
        self.status: str = ''

    @property
    def url(self):
        return self.__url_assinatura

    def input_texto_pesquisar_proposta(self):
        print("Buscando proposta:", self.nr_proposta)
        loc_pesquisar = '//*[@id="ctl00_Cph_AprCons_txtPesquisa_CAMPO"]'
        self.act.enviar_texto(loc_pesquisar, self.nr_proposta, self.by.XPATH)

    def botao_pesquisar_proposta(self):
        loc_bt_pesquisar = '//*[@id="btnPesquisar_txt"]'
        self.act.hover_e_clique(loc_bt_pesquisar, self.by.XPATH)

    def extrair_situacao(self):
        print("Extraindo situação: ", end="")
        loc = ('//*[@id="ctl00_Cph_AprCons_grdConsulta"]'
               '/tbody/tr[2]/td[3]/a')
        self.situacao = self.act.obter_texto(loc, self.by.XPATH)
        print(self.situacao)

    def extrair_tipo_assin(self):
        print("Extraindo tipo de assinatura: ", end="")
        loc = ('//*[@id="ctl00_Cph_AprCons_grdConsulta"]'
               '/tbody/tr[2]/td[5]')
        self.tipo_assn = self.act.obter_texto(loc, self.by.XPATH)
        print(self.tipo_assn)

    def extrair_status_proposta(self):
        print("Extraindo status da proposta: ", end="")
        loc = ('//*[@id="ctl00_Cph_AprCons_grdConsulta"]'
               '/tbody/tr[2]/td[6]/a')
        self.status = self.act.obter_texto(loc, self.by.XPATH)
        print(self.status)

    def clicar_iniciar_anexos(self):
        print("Iniciando anexo de documentos...")
        loc = ('//*[@id="ctl00_Cph_AprCons_grdConsulta"]'
               '/tbody/tr[2]/td[6]/a')
        self.act.hover_e_clique(loc, self.by.XPATH)


class PanFormStatusFormalizacao(AutoGUI):
    """
    Implementa métodos para coletar o status do anexo de docs.
    da proposta (marcada como anexada ou com anexo pendente). O status
    é armazenado na respectiva variável de instância.
    Implementa um método, também, para clicar no botão de seguir o anexo.
    """

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 10
        self.status: str = ''

    def verificar_status_docs_id(self):
        print("Verificando status da documentação de identificação: ")
        loc = ('//div[2]/div[1]/platform-ui-card/'
               'div/div[1]/div/div/div/img')
        status = self.act.obter_atributo(loc, 'src', self.by.XPATH)
        if 'warning' in status:
            self.status = 'pendente'
        elif 'check-green' in status:
            self.status = 'anexado'
        print(self.status)

    def clicar_botao_enviar(self):
        loc = '//*[@id="Overview_DOC_IDENTITY"]'
        self.act.hover_e_clique(loc, self.by.XPATH)


class PanDocumentosAnexo(AutoGUI):
    """
    Seleciona na lista de URLs dos documentos (param: docs_list:) as urls
    do documento de identificação (f/v) e do contra-cheque. Define também o tipo
    de documento de identificação que está disponível no webadmin.
    REaliza o download dos documentos contidos nas URLs e salva o caminho
    de cada documento na variável de instância  __paths_docs.
    """
    path_anexo = (
            str(Path(PATHS.project_path(), 'pan', 'anexos', 'anexo_docs'))
    )

    def __init__(self, chrome_driver: object, docs_list: list):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 10
        self.docs_list: list = docs_list
        self.__tipo_doc_id: str = ''
        self.urls_docs: dict = {'docIdFrente': '', 'docIdVerso': '',
                                'contraCheque': ''}
        self.__paths_docs: dict = {'docIdFrente': '', 'docIdVerso': '',
                                   'contraCheque': ''}
        self.__definir_tipo_doc_anexo()
        self.__criar_pasta_anexos()

    @property
    def tipo_doc_id(self):
        return self.__tipo_doc_id

    @property
    def paths_docs(self):
        return self.__paths_docs

    def __criar_pasta_anexos(self):
        import os
        try:
            os.makedirs(self.path_anexo)
        except OSError:
            print("Pasta 'anexos' já existe.")

    def __definir_tipo_doc_anexo(self):
        print("Definindo tipo de documento", end='')
        for doc_url in self.docs_list:
            if 'documentoPessoal/CNH/' in doc_url:
                self.__tipo_doc_id = "CNH"
            elif 'documentoPessoal/RG/' in doc_url:
                self.__tipo_doc_id = "RG"
        print(self.tipo_doc_id)

    def selecionar_urls_docs(self):
        for doc_url in self.docs_list:
            if 'contra' in doc_url.lower():
                self.urls_docs['contraCheque'] = doc_url

            if f'documentoPessoal/{self.__tipo_doc_id}/FRENTE' in doc_url:
                self.urls_docs['docIdFrente'] = doc_url

            if f'documentoPessoal/{self.__tipo_doc_id}/VERSO' in doc_url:
                self.urls_docs['docIdVerso'] = doc_url

        print(self.urls_docs)

    def download_doc_id_frente(self):
        print(f"Realizando download do doc '{self.tipo_doc_id}' frente.")
        self.paths_docs['docIdFrente'] = (
                self.path_anexo + self.tipo_doc_id + 'FRENTE.jpeg'
        )

        download(
            self.urls_docs['docIdFrente'],
            self.paths_docs['docIdFrente']
        )

    def download_doc_id_verso(self):
        print(f"Realizando download do doc '{self.tipo_doc_id}' verso.")
        self.paths_docs[f'docIdVerso'] = (
                self.path_anexo + self.tipo_doc_id + 'VERSO.jpeg'
        )
        print(self.paths_docs)
        download(
            self.urls_docs['docIdVerso'],
            self.paths_docs['docIdVerso']
        )

    def download_contra_cheque(self):
        print(f"Realizando download do contracheque.")
        self.paths_docs['contraCheque'] = (
                self.path_anexo + 'contraCheque.jpeg'
        )
        download(
            self.urls_docs['contraCheque'],
            self.paths_docs['contraCheque']
        )


class PanFormsAnexarDocs(AutoGUI):
    """
    Contém métodos que implementam o anexo do documento de identificação,
    com base no seu tipo (entrado como parâmetro) e do contra-cheque.
    """

    def __init__(self, chrome_driver: object, paths_docs: dict, tipo_docs: str):
        super().__init__(chrome_driver)
        self.chrome_driver = chrome_driver
        self.uconecte = Uconecte()
        self.act.time_out = 10
        self.tipo_doc: str = tipo_docs
        self.paths_docs: dict = paths_docs

    def clicar_enviar_docs(self):
        loc = '//*[@id="Overview_DOC_IDENTITY"]'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def selecionar_anexar_id(self):
        """Seleciona o tipo de documento de identificação será anexado."""
        print("Selecionando o tipo de documento para anexar.")
        idx = 0
        for i in range(1, 4):
            loc_tipo = f'//div[{i}]/pan-radio/label/div/p[1]'
            tipo = self.act.obter_texto(loc_tipo, self.by.XPATH)
            if self.tipo_doc in tipo:
                idx = i
                break

        loc_btn = f'//div[{idx}]/pan-radio/label/input'
        self.act.hover_e_clique(loc_btn, self.by.XPATH)

    def selecionar_anexar_contracheque(self):
        loc = '//div[3]/pan-radio/label/input'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def enviar_anexo(self, n_campo: int, tipo: str, add_loc=0):
        """
        :param add_loc:
        :param n_campo: 0 = frente, 1 = verso
        :param tipo: docIdFrente, docIdVerso, contraCheque
        """
        try:
            loc = f'//*[@id="file-upload-{n_campo+add_loc}"]'
            print("Anexando: ", loc)
            self.act.enviar_texto(loc, self.paths_docs[tipo], self.by.XPATH)

            print(self.paths_docs[tipo])

            return 0
        except Exception as e:
            print("Tentando anexar novamente!")
            if n_campo > 10:
                return -1
            sleep(0.6)
            return self.enviar_anexo(n_campo, tipo, add_loc=add_loc+1)

    def validar_anexos(self):
        loc = '//*[@id="Selecionar_Arquivo"]/button'
        botao_anexo = self.act.esta_presente(
            loc, self.by.XPATH
        )
        return not botao_anexo

    def clicar_continuar_anexo_doc(self):
        loc = '//*[@id="Continuar_DOC"]/button'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def clicar_confirmar_anexo_doc(self):
        loc = '//*[@id="Continuar_Preview_DOC"]/button'
        self.act.hover_e_clique(loc, self.by.XPATH)

    def clicar_continuar(self):
        loc = '//*[@id="Continuar_DOC_Dash"]/button'
        self.act.hover_e_clique(loc, self.by.XPATH)

