from sites.baseRobos.data_handler import DataHandler
import json
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List
dbg = DebugTools(debugging=False)


class DadosConsultaINSS(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "GET_PERFIS": ("https://app.emprestimofacil.com/index.php/api"
                           "/v1/consultas/consultarMeuInss"),
            "POST_STATUS": "https://app.emprestimofacil.com/index.php/api/v1/consultas/inss",
            "POST_FALHA": "https://app.emprestimofacil.com/index.php/api/v1"
                          "/consultas/atualizaSituacaoContrato"
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f",
            'CONSULTA': '304b5b69eeb3921790c9e7ed9f4df504'
        }

    def get_perfis(self):
        params = {
            'perfil': '4,5',
            'key': self.api_keys['CONSULTA']
        }

        resp = self.dh.make_request(
            method="GET",
            url=self.api_urls["GET_PERFIS"],
            params_data=params,
            msg="Em GET PERFIS CONSULTA MARGEM INSS",
            json=True
        )
        return resp['perfil']

    def post_dados_consultados(self, dados, perfil):
        """
        Parâmetros atualização:
            'codigoCon': codigo_do_contrato,
            'retorno': 0=falha 1=sucesso,
        """
        print("Atualizando dados consultados.")
        dbg.debugger()
        dados_json = json.dumps(dados, indent=4)

        dados_post = {
            'key': self.api_keys['CONSULTA'],
            "consultaBeneficio": dados_json,
            "robo": True,
            "idContrato": perfil['idContrato'],
        }

        atualizado = self.dh.make_request(
            method='POST',
            url=self.api_urls["POST_STATUS"],
            params_data=dados_post,
            msg="Em POST DADOS MARGEM INSS"
        )
        if not atualizado:
            raise Exception(
                "Não foi possível atualizar os dados da proposta."
            )
        else:
            print("Dados da proposta atualizados com sucesso.")

    def atualiza_perfil_web_admin(self, **kwargs):
        perfil: dict = kwargs.get("perfil", "")
        dados_consulta: dict = kwargs.get("dados_consulta", {None: None})
        observacao: str = kwargs.get("observacao", "")
        retorno: int = kwargs.get("retorno", None)

        margem: str = ""
        # Definir se será utilizada margem do cartão ou margem consignável.
        if perfil['tipoContrato'] == "Empréstimo":
            margem = dados_consulta.get('margemDisponivel', "")
            dbg.warning("Utilizando margem consignável " + margem)

        elif perfil['tipoContrato'] == "Cartão":
            margem = dados_consulta.get("margemDisponivelCartao", "")
            dbg.warning("Utilizando margem do cartão " + margem)
        else:
            raise Exception("Tipo do contrato não reconhecido.")

        dados = {
            "retorno": retorno,
            "codigoCon": perfil['codigoContrato'],
            "margemDisponivel": margem,
            # 'arrayParcelasRefin': dados_consulta.get('arrayParcelasRefin', ''),
            "observacao": observacao
        }
        dbg.warning("Atualizando dados no web admin", dados)
        print('***************************************************************************')
        print(dados)
        print('***************************************************************************')

        request_dados_perfil = self.dh.make_request(method="POST",url="https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-margem/portal-meu-inss/?key=f689f1e12a0399fba803cb2365fc362f",params_data=dados, msg="Em ATUALIZA PERFIL WEBADMIN")

        #dbg.warning("Atualizado com sucesso: " + request_dados_perfil.content)

    def post_consulta_info_falha(self, perfil: dict, dados_erro: dict):
        dbg.warning(f"Atualizando dados: {dados_erro}")

        dados = {
            "retorno": dados_erro['retorno'],
            "key": self.api_keys['CONSULTA'],
            "idContrato": perfil['idContrato'],
            "mensagem": dados_erro['erro'] + " Funcao 8",
        }
        post = self.dh.make_request(
            method="POST",
            url=self.api_urls['POST_FALHA'],
            params_data=dados
        )
        if post.status_code != 200:
            input("Problema em reportar a falha da consulta para a API da Uconete!")
