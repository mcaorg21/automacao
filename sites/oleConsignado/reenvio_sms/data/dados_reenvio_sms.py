from sites.baseRobos.data_handler import DataHandler


class DadosReenviarSMS(DataHandler):
    def __init__(self):
        super().__init__()
        self.api_urls = {
            "GET_ADES": ("http://emprestimofacil.co/web_admin/api/"
                         "v1/contratos/a-reenviar-sms/banco-ole/"),
            "POST_STATUS": ("http://emprestimofacil.co/web_admin/api/v1/atualiza-status/"
                            "banco-ole/sms-envio/?key=f689f1e12a0399fba803cb2365fc362f"),
        }
        self.api_keys = {
            'GERAL': "f689f1e12a0399fba803cb2365fc362f"
        }

    def get_ades(self):
        return self.dh.make_request(
            method="GET",
            url=self.api_urls["GET_ADES"],
            params_data={"key": self.api_keys['GERAL']},
            msg="Em GET DADOS REENVIO SMS",
            json=True
        )

    def post_dados_consultados(self, dados):
        """
        Parâmetros atualização:
            'codigoCon': codigo_do_contrato,
            'retorno': 0=falha 1=sucesso,
        """
        print("Atualizando dados consultados.")

        atualizado = self.dh.make_request(
            method='POST',
            url=self.api_urls["POST_STATUS"],
            params_data=dados,
            msg="Em POST DADOS REENVIO"
        )
        if not atualizado:
            raise Exception(
                "Não foi possível atualizar os dados da proposta."
            )
        else:
            print("Dados da proposta atualizados com sucesso.")

    def get_sinc(self):
        self.dh.make_request(
            method="GET",
            url=self.api_urls["GET_SINC"],
            params_data={'key': self.api_keys["GERAL"]}
        )


