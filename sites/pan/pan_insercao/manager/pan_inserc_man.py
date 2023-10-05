"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_auto.py
| data: 2019-12-20
| autor: Gustavo Belleza

| finalidade
    Classe responsável por gerenciar as interfaces entre
    as funções que realizam a automação do navegador
    (módulo <executar_insercao>), (PanInsercaoAssinaturaAuto) bem como
    com a classe responsável pela requisição e processamento
    de dados (PanInsercaoData).

    O processo de automação conta com dois subprocessos:
        1. Inserção do Contrato de Financiamento.
        2. Formalização da Assinatura Digital.
Message: Cannot locate option with value: MargemLivre
"""
# Classe herdada por PanInsercaoMan
from typing import List

from sites.baseRobos.manager import Manager

# Classe de requisição e manipulaçao de dados
from sites.pan.pan_insercao.data.pan_inserc_data import PanInsercaoData

# Funções que executam a automação do processo de inserção
from sites.pan.pan_insercao.auto.executar_insercao import (
    preencher_formulario_identificacao, preencher_dados_proposta_insercao,
    preencher_dados_pessoais, preencher_dados_bancarios, finalizar_insercao,
    realizar_assinatura_digital, ApplicationErrorException
)
from sites.pan.pan_insercao.auto.pan_inserc_formulários import AtualizarException
from selenium.webdriver import Chrome
from requests import Request
from sites.baseRobos.core.DebugTools import DebugTools
from sites.pan.auxiliares.sessao import verificar_sessao_login, login, HORARIO_COMERCIAL
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
dbg = DebugTools(debugging=False)


class PanInsercaoMan(Manager):
    """
    Métodos = [realizar_login_pancred, executar_insercao,
               insercao, assinatura_digital]
    """

    main_url = ("https://panconsig.pansolucoes.com.br/" +
                "WebAutorizador/Login/AC.UI.LOGIN.aspx")
    id_robo: int = 13
    id_banco: int = 68

    def __init__(self, driver: Chrome=False, **kwargs):
        super().__init__()
        self.set_options(
            '--ignore-ssl-errors', "--start-maximized",)
        self.urls: dict = {
            'consig': ('https://panconsig.pansolucoes.com.br/WebAutorizador' +
                       '/Cadastro/CardOferta')
        }
        self.init_chrome_driver(import_driver=driver)
        self.data: PanInsercaoData = PanInsercaoData()

        # Direcionar para o portal
        #self.chrome_driver.get(self.main_url)
        self.atualizar_tabela: str = ""
        self.n_insercoes = 0
        self.n_maximo_insercoes = 10
        self.cpf = kwargs.get("login", "")
        self.senha = kwargs.get("senha", "")
        self.parceiro = kwargs.get("parceiro", "")
        self.aguardar_sessao = kwargs.get("aguardar_sessao", False)

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome, configs: dict):
        run = PanInsercaoMan(driver, **configs)
        try:
            return run.executar_insercao()
        except:
            return -1

        return run

    def executar_insercao(self):
        """
        Método principal na implementação da automação do processo
        de inserção. Gerencia a fila de contratos, sua inserção e
        assinatura digital.
        """
        self.n_insercoes = 0
        infos_contratos: Request  # resposta da request GET
        info_contrato: dict      # informações básicos do contato a inserir
        contrato: dict           # informaçoes detalhadas do contrato
        numero_ade: str          # número da proposta gerada

        print("Buscar contratos para inserção.")
        infos_contratos: List[dict] = self.data.get_contratos_insercao()
        if not infos_contratos:
            print("Não há contratos a inserir...")
            return -1

        for info_contrato in infos_contratos:
            if not verificar_sessao_login(self.driver, aguardar=self.aguardar_sessao):
                login(self.driver, self.cpf, self.senha)
                self.aguardar_sessao = True

            self.data.api_iniciar_log_robo(
                idContrato=info_contrato['codigo_con'],
                idRobo=self.id_robo
            )
            contrato: dict = self.data.get_infos_contrato(info_contrato['codigo_con'])
            print(f"INSERÇÃO Nº{self.n_insercoes} DE {self.n_maximo_insercoes}")
            print("\nInserindo contrato: ", contrato['codigoContrato'])
            print("Contrato tipo: ", info_contrato['tipo'])

            try:
                self.__verificar_erros_contrato(contrato)
                self.driver.get(self.urls['consig'])
                numero_ade: str = self.insercao(contrato, info_contrato['tipo'])

                if(numero_ade == 'Nenhuma oferta disponível' or numero_ade == 'Ade não encontrada' or numero_ade == 'Inseriu mas ade não foi encontrada'):
                    continue

                # Atualizar o contrato com o link da assinatura digital.
                self.data.atualizar_contrato_ade_sem_link(numero_ade, contrato['codigoContrato'], self.atualizar_tabela, 'Contrato inserido, falta salvar Link e Pdf contrato.', self.novo_valor)

                self.data.api_registrar_log_robo(
                    log=f"Contrato inserido com ADE: {numero_ade}",
                    status=2
                )
                #self.assinatura_digital(numero_ade, contrato)

            except AtualizarException as e:
                print("Atualizando o contrato com os dados:", e)
                self.data.uconecte.atualizar_contrato(
                    contrato["codigoContrato"], e.message
                )

            except Exception as e:
                dbg.exception(e)
                self.data.api_registrar_log_robo(
                    log=f"ERRO: {e}", status=0)

        return 0

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def insercao(self, contrato: dict, tipo_contrato: str) -> str:
        """
        Implementa a automação do preenchimento dos formulários
        de inserção dos contratos.
        :return: ADE/NºdaProposta
        """
        # Direcionar para página de inserção
        self.contrato = preencher_formulario_identificacao(self.chrome_driver, contrato)

        if self.contrato == 'Nenhuma oferta disponível':
            print(f"Atualizando o contrato {contrato['codigoContrato']} por não apresentar ofertas disponíveis")
            self.data.uconecte.atualizar_contrato(contrato['codigoContrato'], {
            'mensagem': "Reprovada a Oferta"})
            return 'Nenhuma oferta disponível'

        print(f"Atualizando o contrato {contrato['codigoContrato']}")
        self.data.uconecte.atualizar_contrato(contrato['codigoContrato'], {
            'mensagem': "Inserir contrato"})

        self.data.uconecte.atualizar_status_robo(self.id_robo)

        self.atualizar_tabela, self.novo_valor = preencher_dados_proposta_insercao(
            self.chrome_driver, contrato, tipo_contrato)

        preencher_dados_pessoais(self.chrome_driver, contrato)

        preencher_dados_bancarios(self.chrome_driver, contrato)

        numero_ade: str = finalizar_insercao(self.chrome_driver, contrato)

        if numero_ade == 'Insercao falha':
            print(f"Atualizando o contrato {contrato['codigoContrato']} mas nao achou ade")
            self.data.uconecte.atualizar_contrato(contrato['codigoContrato'], {
            'mensagem': "Conferir dados do contrato", 'observacao': "Verificar a falha na inserção"})
            return 'Ade não encontrada'

        self.data.uconecte.atualizar_status_robo(self.id_robo)

        return numero_ade

    def assinatura_digital(self, numero_ade: str, contrato: dict):
        """
        Implementa a automação da seleção das opções de assinatura.
        Seleciona a assinatura digital, por meio do envio de link via SMS
        ao cliente. Atualiza o contrato da uConecte com o link obtido.
        """
        link_assinatura: str = ""
        try:
            link_assinatura = realizar_assinatura_digital(
                driver=self.chrome_driver, n_ade=numero_ade
            )    # raises ApplicationErrorException
        except ApplicationErrorException as e:
            print(e)

            db = self.data.db_ades_pendentes.criar_instancia(
                id_banco=self.id_banco, ade=numero_ade,
                codigo_con=contrato['codigoContrato'], mensagem=e)
            db.insert_dados_insercao()

        self.data.uconecte.atualizar_status_robo(self.id_robo)

        if not link_assinatura:
            raise Exception("Link da assinatura digital não encontrado.")

        # Atualizar o contrato com o link da assinatura digital.
        self.data.atualizar_contrato_ade(
            numero_ade, contrato['codigoContrato'], link_assinatura, self.atualizar_tabela)

        self.data.api_registrar_log_robo(
            log=f"Contrato inserido com ADE: {numero_ade}",
            status=2
        )

    def __verificar_erros_contrato(self, contrato):
        if contrato['agencia'] == "0"*4:
            print("Dado 'Complemento' vazio.")

            self.data.uconecte.atualizar_contrato(
                contrato['codigoContrato'],
                {'texto': 'número da agência igual a zero.',
                 'erro': 'Erro encontrado: número da agência igual a zero.',
                 'mensagem': "Conferir dados do contrato",
                 'tratamento': ['atualizar']})
            raise Exception('Erro encontrado: dado "complemento" vazio.')

