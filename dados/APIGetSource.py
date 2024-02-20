from dados.APIDataSource import APIDataSource
from dados.APIDataSource import ApiResponseException
from typing import List, Dict, Union
from requests import Response
from dados.dados_apis.registros_bancos import filtrar_bancos_id, filtrar_bancos_nome


class APIGetSource:

    def __init__(self, nome_banco=""):
        self.data_source: APIDataSource = APIDataSource()
        self.__id_banco: int = filtrar_bancos_id(nome_banco)
        self.__nome_banco: str = filtrar_bancos_nome(nome_banco)
        self.__nome_banco_param: str = nome_banco
        self.codigo_teste: str = ""

        # codigoCon, idSolicitacao, ADE
        self.codigo_dados: str = ""

    @property
    def nome_banco(self):
        return self.__nome_banco

    @nome_banco.setter
    def nome_banco(self, nome):
        self.__id_banco: int = filtrar_bancos_id(nome)
        self.__nome_banco: str = filtrar_bancos_nome(nome)
        self.__nome_banco_param: str = nome

    @property
    def nome_banco_param(self):
        return self.__nome_banco_param

    def fila_sincroniza_pagamentos_acreditar(self) -> dict:

        resp = self.data_source.get_request(
            nome_endpoint="fila-pagamentos-acreditar")

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def fila_sincroniza_saques_acreditar(self) -> dict:

        resp = self.data_source.get_request(
            nome_endpoint="fila-saques-acreditar")

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def fila_contratos_inserir(self, ordem="desc") -> dict:
        param_teste = {}
        if self.codigo_teste:
            param_teste = {"codigoContratoTeste": self.codigo_teste}

        resp = self.data_source.get_request(
            nome_endpoint="fila-insercao",
            consulta="insercao",
            banco=self.__nome_banco_param,
            ordem=ordem,
            **param_teste)

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def informacoes_contrato(self) -> dict:
        resp = self.data_source.get_request(
            nome_endpoint="informacoes-contrato",
            edit=("{codigo-contrato}", self.codigo_dados))

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)
        print(resp)
        print(resp.content)
        return resp.json()

    def propostas_a_liberar(self) -> List[dict]:
        resp = self.data_source.get_request(
            nome_endpoint="liberar-propostas",
            edit=("{nome-banco}", self.nome_banco))

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def consulta_status(self) -> List[dict]:
        resp = self.data_source.get_request(
            nome_endpoint="consulta-status",
            edit=("{nome-banco}", self.nome_banco))

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def consulta_status_parceiro(self) -> List[dict]:
        resp = self.data_source.get_request(
            nome_endpoint="consulta-status-parceiro",
            edit=("{nome-banco}", self.nome_banco))

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def atualizar_sincronizacao(self) -> Response:
        resp = self.data_source.get_request(
            nome_endpoint="atualiza-sincronizacao",
            edit=("{nome-banco}", self.__nome_banco))
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp

    def contratos_a_gerar(self) -> Dict[str, List[dict]]:
        resp = self.data_source.get_request(
            nome_endpoint="gerar-contrato",
            consulta="gerar",
            banco=self.__nome_banco_param
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def contratos_documentos_a_enviar(self) -> List[dict]:
        resp = self.data_source.get_request(
            nome_endpoint="enviar-docs",
            edit=("{nome-banco}", self.nome_banco))
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def contratos_documentos_a_enviar_ibconsig(self) -> List[dict]:
        resp = self.data_source.get_request(
            nome_endpoint="enviar-docs-portabilidade",
            edit=("{nome-banco}", self.nome_banco))
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def documentos_contrato(self, cpf: str) -> dict:
        resp = self.data_source.get_request(
            nome_endpoint="download-documentos-contrato",
            ade=self.codigo_dados,
            cpf=cpf
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def download_documentos_contrato(self, idPessoa: int, idContrato: int) -> dict:
        resp = self.data_source.get_request(
            nome_endpoint="download-documentos-contrato",
            pessoa=idPessoa,
            contrato=idContrato,
            analise=True,
            enviarFotos=False,
            area=""

        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def docs_log_contrato(self, cpf: str) -> dict:
        resp = self.data_source.get_request(
            nome_endpoint="docs-assinaturas-log",
            ade=self.codigo_dados,
            cpf=cpf
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def docs_contrato_portabilidade(self, cpf: str) -> dict:
        resp = self.data_source.get_request(
            nome_endpoint="docs-portabilidade",
            ade=self.codigo_dados,
            cpf=cpf
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def solicitacoes_consulta_refinanciamento(self) -> Dict[str, List[dict]]:
        resp = self.data_source.get_request(
            nome_endpoint="refinanciamento",
            banco=self.__id_banco
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def solicitacoes_consulta_crm(self):
        resp = self.data_source.get_request(
            nome_endpoint="crm",
            banco=self.__id_banco
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def perfis_consulta_meu_inss(self):
        from dados.dados_apis.keys import KEY_MEU_INSS
        self.data_source.key = KEY_MEU_INSS
        resp = self.data_source.get_request(
            nome_endpoint="consulta-meu-inss",
            perfil="4,5"
        )
        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def perfis_reenvio_sms(self):
        resp = self.data_source.get_request(
            nome_endpoint="reenvio-sms",
            edit=("{nome-banco}", self.__nome_banco))

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.json()

    def perfis_consulta_portal_consignado(self, estado:str):
        from dados.dados_apis.keys import KEY_PORTAL_CONSIG
        self.data_source.key = KEY_PORTAL_CONSIG
        resp = self.data_source.get_request(
            nome_endpoint="portal-consignado",
            codigoPerfil="1",
            codigoEstado=estado)

        if resp.status_code != 200:
            raise ApiResponseException(
                resp.status_code, resp.content)

        return resp.content


if __name__ == "__main__":
    print(APIGetSource("pan").fila_contratos_inserir())
