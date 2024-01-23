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

from dados.RequestHandler import RequestHandler, NullRequestResponseException
from sites.baseRobos.data_handler import DataHandler
from datetime import datetime as dt
from requests import Response
from sites.baseRobos.core.uconecte import FalhaAPIException
from sites.local_db.AtualizacoesPendentesInsercao import AtualizacoesPendentesInsercao

from PATHS import *

class IbConsigData(DataHandler):

    idBanco = 1

    def __init__(self):
        super().__init__()
        self.api_urls = {
            '164': 'http://api.portaldatransparencia.gov.br/api-de-dados/servidores/remuneracao',
            'port_retencao': 'https://emprestimofacil.co/web_admin/api/v1/atualiza-status'
                             '/banco-itau-consignado/retencao-portabilidade',
            'docs_contrato': 'https://app.emprestimofacil.com/api/v1/contratos/documentos',
            'termo_in100':'https://app.emprestimofacil.com/api/v1/contratos/termo_in100/'
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
        request = RequestHandler(
            url=self.api_urls["164"],
            method="GET",
            params=params,
            headers={"chave-api-dados": "9f337bf4b940d7246008d72705ddf0c9"},
        )
        request.send()
        try:
            dados_servidor = request.receiveAsJson[0]["servidor"]
        except NullRequestResponseException as e:
            print(e.msg)
            raise DadosServidorFederalInvalidos(
                "Erro encontrado: Dados do servidor federal indisponíveis no portal transparência."
            )
        codigo_orgao = dados_servidor["orgaoServidorLotacao"]['codigo']
        codigo_situacao = dados_servidor["situacao"]
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
            url="http://localhost:5000/routing/contratos-insercao/itau",
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
            anexo_path = str(Path(project_path()+'/ibConsig/anexos/contracheque.pdf'))
            if 'contra' in url_arquivo.lower() or 'cheque' in url_arquivo.lower():
                self.dh.download(url_arquivo, anexo_path)

    def get_termo_in100(self, idPessoa: str):
        data = {
            'key': self.api_keys['uconecte_inserir'],
            'idPessoa': idPessoa
        }
        
        termo_in100 = self.dh.make_request(
            method="GET",
            url=self.api_urls['termo_in100'],
            params_data=data,
            json=True
        )

        if(termo_in100['tipo'] == 'success'):
            anexo_path_in100 = str(Path(project_path()+'/ibConsig/anexos/termo_in100/termo_in100_'+ idPessoa +'.jpg'))
            self.dh.download(termo_in100['arquivo'], anexo_path_in100)
            return True
        else:
            return False


    def get_contrato_teste(self):
        contrato = self.uconecte.buscar_informacoes_contrato("412311", return_contrato=True)
        print("CONTRATO TESTE:", contrato)
        return contrato

    def get_contrato_uconecte(self, codigo_con: str) -> dict:
        self.data_source.codigo_dados = codigo_con
        return self.data_source.informacoes_contrato()['dadosContrato']

    def atualizar_contrato(self, codigo_contrato, **kwargs):

        print(f"Atualizando contrato com:\n{kwargs}")

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

    def atualizar_aguardando_gerar_contrato(self, **kwargs):
        contrato: dict = kwargs.get('contrato')
        tabela: str = kwargs.get('tabelaBanco')
        ade: str = kwargs.get('ade')
        valor_atualizado: str

        try:
            valor_atualizado = str(
                round(float(contrato['valorContrato']), 2)).replace('.', ',')
        except ValueError:
            valor_atualizado = contrato['valorContrato']

        try:
            prazo = contrato['prazoContrato'] 
            if(contrato['prazoContrato'] != contrato['prazo']):
                prazo = contrato['prazo']
        except:
            pass

        # Encontrada a ADE, atualiza-se o contrato.
        try:
            self.atualizar_contrato(
                contrato['codigo_con'],
                mensagem="Aguardando Gerar Contrato",
                ade=ade,
                valorContrato=valor_atualizado,
                prazo=prazo,
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
                prazo=prazo,
                textoMensagem="O valor de seu contrato foi alterado.",
                tabelaBanco=tabela
            )
            contrato_pendente.insert_dados_insercao()

        print(f"\n>>> Contrato atualizado. ADE: {ade} <<<\n")

        self.api_registrar_log_robo(
            log=f"Aguardando Gerar Contrato. ADE:{ade}",
            status=2
        )
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
