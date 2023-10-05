"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_auto.py
| data: 2019-12-20
| autor: Gustavo Belleza

| funcionamento:
    Implementa os processos de requisição e processamento de
    dados para a automação da inserção do Pan.
"""
from typing import List

from sites.baseRobos.data_handler import DataHandler


class PanInsercaoData(DataHandler):
    def __init__(self):
        super().__init__()
        self.data_source.nome_banco = "pan"

    def get_contratos_insercao(self) -> List[dict]:
        """
        Retorna uma lista com os contratos aguardando inserção.
        """
        request_get = self.dh.make_request(
            "GET",
            "http://localhost:5000/routing/contratos-insercao/pan",
            json=True,
            msg="Em <api_uconecte_inserir_get>"
        )
        if not request_get:
            return []

        return [request_get]

    def get_infos_contrato(self, codigo: str) -> dict:
        self.data_source.codigo_dados = codigo
        return self.data_source.informacoes_contrato()['contrato']

    def atualizar_contrato_ade(self, numero_ade: str, codigo_contrato: str, link_assinatura: str, tabela) -> bool:
        """
        Atualiza o contrato de a ADE número <numero_ade>, adicionando a ele o link para
        assinatua digital e colocando-o no status <Aguardando assinatura digital>.

        """
        print(f"Atualizando Contrato {codigo_contrato}."
              f"ADE: {numero_ade}. Link: {link_assinatura}"
              f"Tabela: {tabela}")

        self.uconecte.atualizar_contrato(
            codigo_contrato,
            dados={
                'mensagem': "Aguardando Gerar Contrato",
                'ade': numero_ade,
                'linkAssinatura': link_assinatura,
                'tabelaBanco': tabela
            })

        return True

    def atualizar_contrato_ade_sem_link(self, numero_ade: str, codigo_contrato: str, tabela, observacao, valorContrato) -> bool:
        """
        Atualiza o contrato de a ADE número <numero_ade>, adicionando a ele o link para
        assinatua digital e colocando-o no status <Aguardando assinatura digital>.

        """
        print(f"Atualizando Contrato {codigo_contrato}."
              f"ADE: {numero_ade}."
              f"Tabela: {tabela}")

        self.uconecte.atualizar_contrato(
            codigo_contrato,
            dados={
                'mensagem': "Aguardando Gerar Contrato",
                'ade': numero_ade,
                'tabelaBanco': tabela,
                'observacao': observacao,
                'valorContrato': valorContrato
            })

        return True
