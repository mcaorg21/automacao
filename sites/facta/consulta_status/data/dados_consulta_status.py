from sites.baseRobos.data_handler import DataHandler
import pdb

class DadosConsultaStatus(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "GET_ADES": ("https://emprestimofacil.co/web_admin/api/v1/"
                         "contratos/em-analise/facta"),
            "POST_CONSULTA": ("https://emprestimofacil.co/web_admin/api/v1/"
                              "atualiza-status/facta/contratos/"),
            "GET_SINC": ("https://emprestimofacil.co/web_admin/api/v1/"
                         "atualiza-status/facta/sincronizacao/")
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f"
        }
        self.data_source.nome_banco = "facta"

    def get_ades(self):
        return self.data_source.consulta_status_parceiro()

    def get_contratos_inserir(self, ordem):
        return self.data_source.fila_contratos_inserir(ordem)

    def get_informacoes_contrato(self, codigo_contrato):
        self.data_source.codigo_dados = codigo_contrato
        return self.data_source.informacoes_contrato()

    def post_dados_consultados(self, dados):
        print("Atualizando dados consultados.")

        dados_post = {'key': self.api_keys['GERAL'], **dados}

        atualizado = self.dh.make_request(method='POST',url=self.api_urls["POST_CONSULTA"], params_data=dados_post, msg="Em POST DADOS CONSULTA")

        if not atualizado:
            raise Exception("Não foi possível atualizar os dados da proposta.")
        else:
            print("Dados da proposta atualizados com sucesso.")
