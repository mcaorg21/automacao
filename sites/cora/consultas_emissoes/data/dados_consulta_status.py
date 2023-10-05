from sites.baseRobos.data_handler import DataHandler
import pdb

class DadosConsultaStatus(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "POST": "https://uconecte.me/api/v1/carteira/atualizarTransacaoAberta"
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f"
        }

    def get_pagamentos_acreditar(self):
        return self.data_source.fila_sincroniza_pagamentos_acreditar()

    def get_saques_acreditar(self):
        return self.data_source.fila_sincroniza_saques_acreditar()

    def post_dados_consultados(self, dados):
        print("Atualizando dados consultados.")

        dados_post = {'key': self.api_keys['GERAL'], **dados}

        atualizado = self.dh.make_request(
            method='POST',
            url=self.api_urls["POST"],
            params_data=dados_post,
            msg="Em POST DADOS CONSULTA"
        )

        if not atualizado:
            raise Exception("Não foi possível atualizar os dados da proposta.")
        else:
            print("Dados da proposta atualizados com sucesso.")
