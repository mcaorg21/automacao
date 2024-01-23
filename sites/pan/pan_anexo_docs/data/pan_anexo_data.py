"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_auto.py
| data: 2019-12-20
| autor: Gustavo Belleza

| funcionamento:
"""
from sites.baseRobos.data_handler import DataHandler


class PanAnexoDocsData(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            'GET_CONTRATOS': ('https://emprestimofacil.co/web_admin/api/v1/'
                              'contratos/enviar-documentos-banco/banco-pan/'),
            'GET_DOCS': 'https://app.emprestimofacil.com/api/v1/contratos/documentos',
            'POST_WEBADMIN': ("https://emprestimofacil.co/web_admin/api/"
                              "v1/atualiza-status/banco-pan/contratos/")
        }
        self.api_keys = {
            'UCONECTE': 'f689f1e12a0399fba803cb2365fc362f'
        }

    def get_contratos_anexar(self) -> dict:
        try:
            parametros = {
                'key': self.api_keys["UCONECTE"],
            }
            request_get = self.dh.make_request(
                "GET",
                self.api_urls['GET_CONTRATOS'],
                params_data=parametros,
                msg="Em <api_uconecte_inserir_get>",
                json=True
            )

            return request_get

        except Exception as e:
            self.data_handler_error_log("Em <api_uconecte_inserir_get>", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def get_documentos_contrato(self, ade: str) -> list:
        """
        """
        parametros = {
            'key': self.api_keys["UCONECTE"],
            'ade': ade
        }
        data = self.dh.make_request(
            'GET',
            self.api_urls['GET_DOCS'],
            params_data=parametros,
            msg="Em <get_contrato_teste>",
            json=True
        )

        return data['arquivos']

    def atualizar_contrato_webadmin(self, **kwargs) -> bool:
        """
        :param kwargs: {
                'statusPropostaBanco': kwargs.get('status', None),
                'observacaoDetalhadaBanco': kwargs.get('observacao', ''),
                'codigoCon': kwargs.get('codigoCon', None),
                'ade': kwargs.get('ade', None)
        }
        """
        dados = {
            'key': self.api_keys['UCONECTE'],
            'statusPropostaBanco': kwargs.get('status', None),
            'observacaoDetalhadaBanco': kwargs.get('observacao', ''),
            'codigoCon': kwargs.get('codigoCon', None),
            'ade': kwargs.get('ade', None)
        }
        print("Atualizando contrato com os dados:", dados)
        self.dh.make_request(
            'POST',
            self.api_urls['POST_WEBADMIN'],
            params_data=dados
        )

        return True
