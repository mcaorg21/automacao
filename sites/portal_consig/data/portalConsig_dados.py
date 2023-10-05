from sites.baseRobos.data_handler import DataHandler
from datetime import date
import json
from sites.baseRobos.core.data_helpers import similaridade


class PortalConsigData(DataHandler):
    def __init__(self):
        super().__init__()
        self.solicitacao = None
        self.api_urls = {
            "get_solicitacoes": 'https://uconecte.me/api/v1/Consultas/consultarMargemServidor'
        }
        self.api_keys = {
            "get_solicitacoes": 'e3594254f00c5ba21854dfe55e20f2f9'
        }
        self.parar_se_exception = False

    def req_solicitacoes(self, convenio):
        """
        Realiza uma 'request' á API da uConecte requisitando os
        dados das solicitações de financiamento dos clientes à plataforma.
        :return: (list) uma list de dicts
        """
        codigo = 0
        codigo_perfil = 1
        try:
            if convenio.lower() == 'sp':
                codigo = 25
            elif convenio.lower() == 'mt':
                codigo = 11
            elif convenio.lower() == 'prefeitura_sp':
                codigo_perfil = 3
                codigo = '3-25-9383'                
            else:
                print("Códigos válidos: 25 = SP ou 11 = MT ou 3-25-9383 Pref. Sao Paulo")

            parametros = {'key': self.api_keys["get_solicitacoes"],
                          'codigoPerfil': codigo_perfil,
                          'codigo': codigo
                          }

            request_solicitacoes = self.dh.make_request(
                'GET', self.api_urls["get_solicitacoes"],
                params_data=parametros,
                msg="Em <buscar solicitações>."
            )

            resultado_consulta = request_solicitacoes.json()['consulta']
            return resultado_consulta

        except Exception as e:
            self.data_handler_error_log("Em login_sistema", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def calculo_fin_refin_uconecte(self, solicitacao, print_solicitacao=False):
        if print_solicitacao:
            print(json.dumps(solicitacao, sort_keys=True, indent=2))

        if solicitacao['fk_idCategoria'] == '1':
            self.uconecte.calcular_financiamento(solicitacao, status_solicit=True)

        elif solicitacao['fk_idCategoria'] == '5':
            self.uconecte.calcular_cartao_consignado(solicitacao, status_solicit=True)

    def verificar_status(self, mensagem):
        """
        Após a consulta ao Portal, retorna um dicionário contendo
        informações sobre a consulta realizada. Essas informações
        são apresentadas na forma de um código e uma mensagem.
        O código representa: 0 = servidor não localizado, 1 = servidor
        não permite a consulta à margem, 2 = consulta realizada com
        sucesso e 99 = evento não previsto. A mensagem descreve o
        significado do código.
        :param mensagem: (str) mensagem extraída do portal ('não localizado',
                        'consulta bloqueada', ...) ou gerada durante a execução
                        da função de consulta à margem ('_localizado').
        :return: (dict) keys = [retorno, mensagem]
        """
        if ":" in mensagem:
            mensagem = mensagem.split(':')[1].strip()
            print(mensagem)

        status_consulta = None

        if mensagem == '_localizado' or mensagem == 'Servidor com valor da Margem Indisponível':
            status_consulta = 1
        elif ('Servidor não localizado' in mensagem or
              "Matrícula não bate com a do portal" in mensagem or
              "Dados de cadastro não localizados." in mensagem):
            status_consulta = 2
        elif mensagem == 'Servidor não permite a Consulta da Margem':
            status_consulta = 3
        elif 'Valor da margem indisponível' in mensagem:
            status_consulta = 4
        else:
            status_consulta = 99
            print(f'Erro não codificado {mensagem}')

        return {'retorno': status_consulta, 'mensagem': mensagem}
