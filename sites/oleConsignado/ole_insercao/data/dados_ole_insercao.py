"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: dados_ole_insercao
| data: 2020-01-28
| autor: Gustavo Belleza

| funcionamento:
"""
from sites.baseRobos.data_handler import DataHandler


class DadosInsercaoOle(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "GET_SINC": ("https://emprestimofacil.co/web_admin/api/v1/"
                         "atualiza-status/banco-ole/sincronizacao/"),
            "PUT_ATUALIZACOES": 'https://uconecte.me/api/v1/contratos/{}/'
        }
        self.api_keys = {
            'INSERIR': "f689f1e12a0399fba803cb2365fc362f"}
        self.data_source.nome_banco = "ole"

    def get_lista_contratos(self):
        return self.data_source.fila_contratos_inserir()

    def get_dados_contrato(self, codigo_contrato) -> dict:
        self.data_source.codigo_dados = codigo_contrato
        return self.data_source.informacoes_contrato()['contrato']

    def atualizar_contrato(self, codigo_contrato, dados):
        import requests
        if 'mensagem' not in dados:
            dados['mensagem'] = "Aguardando Gerar Contrato"
        print(dados)
        request_atualizar_contrato = requests.put(
            'https://uconecte.me/api/v1/contratos/%s?key=f689f1e12a0399fba803cb2365fc362f' % (
                codigo_contrato),
            data=dados)

        if request_atualizar_contrato.status_code == 200:
            print('contrato atualizado')
        else:
            print(request_atualizar_contrato.text)
            input("Aguardando interação... %s" % request_atualizar_contrato.status_code)
