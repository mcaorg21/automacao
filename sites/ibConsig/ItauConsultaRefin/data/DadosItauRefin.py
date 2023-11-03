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
import pdb
from sites.baseRobos.data_handler import DataHandler
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List
dbg = DebugTools(debugging=False)


class DadosItauRefin(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            'GET_SOLICITACOES': 'http://localhost:5000/routing/solicitacoes-refin/itau',
            'GET_SOLICITACOES_DEV': 'https://uconecte.me/dev/api/v1/solicitacoes/refinanciamento?key=f689f1e12a0399fba803cb2365fc362f&banco=1&solicitacao=1035600'
        }
        self.api_keys = {
            'UCONECTE': 'f689f1e12a0399fba803cb2365fc362f'
        }
        self.uconecte.id_banco = 1
        self.uconecte.consulta_refin_banco = "Itaú"
        self.ordem_reversa: bool = False
        self.instancia: str = ''

    def get_solicitacoes_consulta(self) -> List[dict]:
        params = {
            'key': self.api_keys['UCONECTE'],
            'banco': 1,
            'instancia': self.instancia
        }
        dados: dict = self.dh.make_request(
            method='GET',
            url=self.api_urls['GET_SOLICITACOES'],
            params_data=params,
            json=True
        )
        if not dados:
            return []

        return [dados]

    def atualizar_dados_consulta(self, solicitacao: dict, dados: List[dict]):
        dbg.warning(f"[API] Calculando Refinanciamento: {dados}")

        if solicitacao.get("idSolicitacao", False):  # refinanciamentos
            self.uconecte.atualizar_consulta_refin(
                solicitacao=solicitacao, calcular_refin=dados)

        elif solicitacao.get("idPerfil_pessoa", False):  # refinanciamentos em potencial
            self.uconecte.inserir_ofertas_crm(
                {"refinanciamentos": dados}, solicitacao)

    def atualizar_impossibilidade_consulta(self, solicitacao, msg, restricao=False):
        dbg.warning(f"[API] Inserindo Histórico Solicitação: {msg}")

        if solicitacao.get("idSolicitacao", False):  # refinanciamentos
            self.uconecte.atualizar_consulta_refin(
                solicitacao=solicitacao, msg_erro=msg)
            if restricao:
                dbg.warning("[API] Inserindo Bloqueio Pessoa.")
                self.uconecte.inserir_bloqueio_pessoa(solicitacao['idPessoa'])

        elif solicitacao.get("idPerfil_pessoa", False):  # refinanciamentos em potencial
            if restricao:
                dbg.warning("[API] Inserindo Bloqueio Pessoa.")
                self.uconecte.finalizar_consulta_crm(solicitacao, 2)
            else:
                self.uconecte.finalizar_consulta_crm(solicitacao, 3)
