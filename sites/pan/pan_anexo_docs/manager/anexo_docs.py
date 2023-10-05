"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: anexo_docs
| data: 2020-03-10
| autor: Gustavo Belleza
"""
# Classe herdada por PanInsercaoMan
from sites.baseRobos.manager import Manager

# Classe de requisição e manipulaçao de dados
from sites.pan.pan_anexo_docs.data.pan_anexo_data import PanAnexoDocsData

# Funções que implementam a automação pelo ChromeDriver
from sites.pan.pan_anexo_docs.auto.executar_anexo_docs import (
    pesquisar_proposta, verificar_status_formalizacao,
    download_documentos, anexar_documentos_cliente
)
# Exceção levantada quando existem impedimentos para anexo de documentos
from sites.pan.pan_anexo_docs.auto.auxiliares import (
    StatusPropostaException
)
# Auxiliares
from sites.baseRobos.core.helpers import identificar_erro_robo

# Classes-tipo
from sites.pan.pan_anexo_docs.auto.Anexar_docs_forms import PanDocumentosAnexo
from selenium.webdriver import Chrome

from sites.pan.auxiliares.sessao import verificar_sessao_login, login, HORARIO_COMERCIAL
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError


class PanAnexoDocsMan(Manager):
    main_url = ("https://panconsig.pansolucoes.com.br/" +
                "WebAutorizador/Login/AC.UI.LOGIN.aspx")
    id_robo = 1
    id_banco = 68

    def __init__(self, driver: Chrome=False, **kwargs):
        super().__init__()
        self.set_options(
            '--ignore-ssl-errors', "--start-maximized")
        self.init_chrome_driver(import_driver=driver)
        self.data: PanAnexoDocsData = PanAnexoDocsData()

        # Direcionar para o portal
        self.chrome_driver.get(self.main_url)
        self.cpf = kwargs.get("login", "")
        self.senha = kwargs.get("senha", "")
        self.parceiro = kwargs.get("parceiro", "")

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome, configs):
        run = PanAnexoDocsMan(driver, **configs)
        try:
            return run.executar_anexos()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def executar_anexos(self):
        """
        Responsável pela interface entre os métodos da classe PanAnexoDocsData
        e as funções que utilizam dos dados requisitados por esses métodos.
        Fluxo: requisição da lista de contratos que possuem documentos a
        serem anexados, iteração pela lista de contrato acessando as informa-
        ções de cada contrato, requisição dos documentos de um contrato específico
        utilizando a ADE do contrato, anexar os documentos buscados pelo contrato,
        atualizar o status do processo de anexo.
        """
        # Buscar lista de contratos com docs a anexar
        print("Buscar contratos para anexar documentos.")
        infos_contratos = self.data.get_contratos_anexar()

        try:
            # Caso em que não há documentos
            if infos_contratos['retorno'] == 0:
                print("Não há contratos a inserir...")
                return -1
        except TypeError:
            print("Buscados contratos com documentos a serem anexados.")

        # Iterar pelas informações de cada contrato
        for info_contrato in infos_contratos:
            if not verificar_sessao_login(self.driver, aguardar=True):
                login(self.driver, self.cpf, self.senha)

            print("Iniciando processo de anexo de documentos do contrato:", info_contrato)

            # Buscar urls em que constam os documentos do contrato
            docs_urls: list = self.data.get_documentos_contrato(info_contrato['ade'])

            try:
                # Realizar o anexo do documento de identificação e contra-cheque
                self.anexar_id_contrachque(info_contrato, docs_urls)

                # Atualizar caso em que docs. foram anexados com sucesso.
                self.data.atualizar_contrato_webadmin(
                    ade=info_contrato['ade'],
                    codigoCon=info_contrato['codigoCon'],
                    status='DOCUMENTOS ANEXADOS NO BANCO'
                )

            except StatusPropostaException as exc:
                # Atualizar impedimentos ao anexo de documentos
                print(str(exc))
                self.data.atualizar_contrato_webadmin(
                    ade=info_contrato['ade'], codigoCon=info_contrato['codigoCon'],
                    status=str(exc)
                )
            except Exception as e:
                identificar_erro_robo()
                print("Erro na inserção: ", e)

        return 0

    def anexar_id_contrachque(self, dados, docs_urls):
        """
        Realiza o processo de anexo duas vezes: uma anexando a
        identificação, outra o contracheque. O documento de identificação
        pode ser de dois tipos: CNH e RG.
        """
        tipos: list = ["Identificacao", "Contra_cheque"]
        for tipo in tipos:
            try:
                print("Anexando:", tipo)

                # Pesquisa a proposta específica na tabela de propostas inseridas
                pesquisar_proposta(self.chrome_driver, dados)

                # Verifica se a documentação já está marcada com anexada
                verificar_status_formalizacao(self.chrome_driver)

                # Realiza o download da identificação e contra-cheque
                documentos: PanDocumentosAnexo = download_documentos(
                    self.chrome_driver, docs_urls)

                # Realiza upload dos documentos na plataforma.
                anexar_documentos_cliente(
                    self.chrome_driver, documentos, tipo
                )
            except StatusPropostaException as exc:
                # Atualizar impedimentos ao anexo de documentos
                print(str(exc))
                raise StatusPropostaException(str(exc))
