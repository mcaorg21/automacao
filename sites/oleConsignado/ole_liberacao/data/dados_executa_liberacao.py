from sites.baseRobos.data_handler import DataHandler
import pdb


class DadosConsultaLiberacao(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "POST_LIBERACAO": ("https://emprestimofacil.co/web_admin/api/v1/"
                               "atualiza-status/banco-ole/liberacao-proposta/"
                               "?key=f689f1e12a0399fba803cb2365fc362f")
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f"}
        self.data_source.nome_banco = "ole"

    def get_ades(self):
        return self.data_source.propostas_a_liberar()

    def post_dados_consultados(self, dados):
        print("Atualizando dados.")

        atualizado = self.dh.make_request(
            method='POST',
            url=self.api_urls["POST_LIBERACAO"],
            params_data=dados,
            msg="Em POST DADOS LIBERACAO"
        )

        if not atualizado:
            raise Exception("Não foi possível atualizar os dados da proposta.")
        else:
            print("Dados da proposta atualizados com sucesso.")


