# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| projeto: automacao-python
| arquivo: ib_consig_data.py
| data: 21/11/2019
| autor: Gustavo Belleza

Esta classe tem o intuito de armazenar e processar dados vindos tanto de
requests realizadas a APIs quanto de elementos da interface web, retornados
pela classe "IbConsigAuto".
"""
from typing import Callable, List

from sites.baseRobos.data_handler import DataHandler
from datetime import datetime as dt
from requests import Response
from sites.baseRobos.core.uconecte import Uconecte,FalhaAPIException
from sites.ibConsig.libs.dto.Contrato import Contrato
from sites.local_db.AtualizacoesPendentesInsercao import AtualizacoesPendentesInsercao


class DadosPortabilidade(DataHandler):

    idBanco = 1

    def __init__(self):
        super().__init__()
        self.api_urls = {
            '164': 'http://www.transparencia.gov.br/api-de-dados/servidores/remuneracao',
            'port_retencao': 'https://emprestimofacil.co/web_admin/api/v1/atualiza-status'
                             '/banco-itau-consignado/retencao-portabilidade',
            'docs_contrato': 'https://app.emprestimofacil.com/api/v1/contratos/documentos'
        }
        self.api_keys = {
            'uconecte_inserir': 'f689f1e12a0399fba803cb2365fc362f'
        }
        self.ordem_busca = 'asc'
        self.filtro_contratos: Callable = lambda x: None
        self.contrato_teste: str = ""
        self.data_source.nome_banco = "itau"
        self.instancia = ""

    def api_transparencia_serv_federais_get(self, cpf: str, codigo_con: str) -> dict:
        """
        Retorna dados dos servidores federais da API do portal transparência.
        :param codigo_con:
        :type cpf: str
        """

        params = {
            'cpf': cpf,
            'mesAno': dt.now().strftime("%Y%m")
        }
        dados: Response = self.dh.make_request(
            "GET", self.api_urls["164"], params_data=params
        )

        if not dados.content or not dados.json():
            raise DadosServidorFederalInvalidos(
                "Erro encontrado: Dados do servidor federal indisponíveis no portal transparência."
            )
        dados_servidor = dados.json()[0]['servidor']
        codigo_orgao = dados_servidor["orgaoServidorExercicio"]['codigoOrgaoVinculado']
        codigo_situacao = dados_servidor["situacao"]['codigo']
        if codigo_orgao.count('0') == len(codigo_orgao):
            print("Código órgão:", codigo_orgao)
            raise DadosServidorFederalInvalidos(
                    f"Erro encontrado: código do "
                    f"órgao no portal transparência = {codigo_orgao}")
        return {
            "codigo_orgao": codigo_orgao,
            "codigo_situacao": codigo_situacao
        }

    def buscar_lista_a_inserir(self) -> list:
        """
        Retorna uma lista com os contratos aguardando inserção.
        """
        resp = self.dh.make_request(
            method="GET",
            url="http://localhost:5050/routing/contratos-insercao/itau",
            params_data={"instancia": self.instancia},
            json=True)

        if not resp:
            return []

        return [resp]

    def portabilidade_retencao_put(self, codigo_con):
        dados = {
            'key': self.api_keys['uconecte_inserir'],
            'codigoCon': codigo_con
        }
        self.dh.make_request(
            'PUT', self.api_urls['port_retencao'],
            params_data=dados
        )

    def get_docs_contratos(self, codigo_con: str):
        data = {
            'key': self.api_keys['uconecte_inserir'],
            'contrato': codigo_con
        }
        contrato_docs = self.dh.make_request(
            method="GET",
            url=self.api_urls['docs_contrato'],
            params_data=data,
            json=True
        )
        for url_arquivo in contrato_docs['arquivos']:
            if 'contra' in url_arquivo.lower() or 'cheque' in url_arquivo.lower():
                self.dh.download(url_arquivo, 'contracheque.pdf')

    def get_contrato_teste(self) -> Contrato:
        contrato = self.uconecte.buscar_informacoes_contrato("409592", return_contrato=True)
        return Contrato(contrato)

    def get_contrato_uconecte(self, codigo_con: str) -> dict:
        self.data_source.codigo_dados = codigo_con
        return self.data_source.informacoes_contrato()['dadosContrato']

    def atualizar_contrato(self, codigo_contrato, **kwargs):

        print(f"Atualizando (2) contrato com:\n{kwargs}")

        self.uconecte.atualizar_contrato(
            codigo_contrato=codigo_contrato,
            dados=kwargs,
            raise_erro=True
        )
        if not kwargs.get("idRoboLog", False):
            return

        self.api_registrar_log_robo(
            log=kwargs,
            status=0
        )

    def atualizar_contrato_fila(self, codigo_contrato, **kwargs):

        print(f"Entrou na funcao classe... Atualizando contrato com:\n{kwargs}")
        
        Uconecte().atualizar_contrato(codigo_contrato=codigo_contrato,dados=kwargs,raise_erro=True)
        if not kwargs.get("idRoboLog", False):
            return

        self.api_registrar_log_robo(
            log=kwargs,
            status=0
        )

    def atualizar_aguardando_gerar_contrato(self, **kwargs):
        print('########################FINAL NOVA FUNCAO#####################')
        contrato: dict = kwargs.get('contrato')
        tabela: str = kwargs.get('tabelaBanco')
        ade: str = kwargs.get('ade')
        #ade_refin_portabilidade: str = kwargs.get('ade_refin_portabilidade')
        valor_atualizado: str = kwargs.get('valorAtualizado') 
        parcela_atualizada: str = kwargs.get('parcelaAtualizada') 

        try:
            valor_atualizado = valor_atualizado.replace('.', ',')
            parcela_atualizada = parcela_atualizada.replace('.', ',')
        except:
            pass

        # Encontrada a ADE, atualiza-se o contrato.
        # ade_refin_portabilidade=ade_refin_portabilidade,

        try:
            self.atualizar_contrato(
                contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=ade,
                valorContrato=valor_atualizado,
                valorParcela = parcela_atualizada,
                textoMensagem="O valor de seu contrato foi alterado.",
                tabelaBanco=tabela
            )
        except FalhaAPIException as e:
            print(e.http_code)
            contrato_pendente: AtualizacoesPendentesInsercao = AtualizacoesPendentesInsercao(
                idBanco=self.idBanco,
                codigo_con=contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=ade,
                valorContrato=valor_atualizado,
                valorParcela = parcela_atualizada,
                textoMensagem="O valor de seu contrato foi alterado.",
                tabelaBanco=tabela
            )
            contrato_pendente.insert_dados_insercao()

        print(f"\n>>> Contrato atualizado. ADE: {ade} <<<\n")

        DataHandler().api_registrar_log_robo(
            log=f"Aguardando Gerar Contrato. ADE:{ade}",
            status=2
        )
        print(f"\nFIM: {dt.now()}\n")

    def atualizar_aguardando_gerar_contrato_portabilidade(self, **kwargs):
        print('########################FINAL PORTABILIDADE#####################')
        contrato: dict = kwargs.get('contrato')
        tabela: str = kwargs.get('tabelaBanco')
        ade: str = kwargs.get('ade')
        ade_refin_portabilidade: str = kwargs.get('ade_refin_portabilidade')
        valor_atualizado: str = kwargs.get('valorAtualizado') 

        valor_atualizado = valor_atualizado.replace('.', ',')
        # Encontrada a ADE, atualiza-se o contrato.
        try:
            DadosPortabilidade.atualizar_contrato_fila(self,
                contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=ade,
                ade_refin_portabilidade=ade_refin_portabilidade,
                valorContrato=valor_atualizado,
                textoMensagem="O valor de seu contrato foi alterado.",
                tabelaBanco=tabela
            )
        except FalhaAPIException as e:
            print(e.http_code)
            contrato_pendente: AtualizacoesPendentesInsercao = AtualizacoesPendentesInsercao(
                idBanco=self.idBanco,
                codigo_con=contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=ade,
                valorContrato=valor_atualizado,
                textoMensagem="O valor de seu contrato foi alterado.",
                tabelaBanco=tabela
            )
            contrato_pendente.insert_dados_insercao()

        print(f"\n>>> Contrato atualizado. ADE: {ade} <<<\n")
        DataHandler().api_registrar_log_robo(log=f"Aguardando Gerar Contrato. ADE:{ade}",status=2)
        print(f"\nFIM: {dt.now()}\n")

    def verificar_atualizacoes_pendentes(self):
        registro_contratos: AtualizacoesPendentesInsercao = AtualizacoesPendentesInsercao(
            idBanco=self.idBanco)
        contratos_pendentes = registro_contratos.select_contratos_a_atualizar()

        for contrato in contratos_pendentes:

            self.atualizar_contrato(
                codigo_contrato=contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=contrato['ade'],
                valorContrato=contrato['valorContrato'],
                textoMensagem=contrato['textoMensagem'],
                tabelaBanco=contrato['tabelaBanco']
            )
        registro_contratos.delete_dados_consultados()


class DadosServidorFederalInvalidos(Exception):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return self.msg
