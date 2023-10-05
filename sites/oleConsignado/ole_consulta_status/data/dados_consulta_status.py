from sites.baseRobos.data_handler import DataHandler


class DadosConsultaStatus(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "GET_ADES": ("http://emprestimofacil.co/web_admin/api/v1/"
                         "contratos/em-analise/banco-ole"),
            "POST_CONSULTA": ("https://emprestimofacil.co/web_admin/api/v1/"
                              "atualiza-status/banco-ole/contratos/"),
            "GET_SINC": ("https://emprestimofacil.co/web_admin/api/v1/"
                         "atualiza-status/banco-ole/sincronizacao/")
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f"
        }
        self.data_source.nome_banco = "ole"

    def get_ades(self):
        return self.data_source.consulta_status()

    def post_dados_consultados(self, dados):
        print("Atualizando dados consultados.")

        dados_post = {'key': self.api_keys['GERAL'], **dados}

        atualizado = self.dh.make_request(
            method='POST',
            url=self.api_urls["POST_CONSULTA"],
            params_data=dados_post,
            msg="Em POST DADOS CONSULTA"
        )

        if not atualizado:
            raise Exception("Não foi possível atualizar os dados da proposta.")
        else:
            print("Dados da proposta atualizados com sucesso.")
