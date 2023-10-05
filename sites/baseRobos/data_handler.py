"""
| projeto: automacao-python
| arquivo: data_handler.py
| data: 21/11/2019
| autor: Gustavo Belleza

Contém atributos e métodos base para lidar com dados (requests, limpeza, processamento) durante
a automação. Os dados são, geralmente, oriundos de APIs, por meio de requests, e de elementos
web, por meio do scrapping realizado pelo selenium webdriver.

são duas funções
index_post - basicamente vc vai mandar os dados para inicializar o log
e index_put - vc vai chamar quando der um sucesso ou problema
index_post
Parametros
key = f689f1e12a0399fba803cb2365fc362f
idRobo
idSolicitacao ou  idContrato
index_put
Parametros
key = f689f1e12a0399fba803cb2365fc362f
idRoboLog
log - qualquer registro que queira salvar
status - 0 = falha 2 = sucesso
na index_post ela te retorna o idRoboLog, vc vai precisar manter ele pra enviar no index_put

"""

from sites.baseRobos.core import data_helpers
from sites.baseRobos.core.uconecte import Uconecte
from requests import Response
from sites.local_db.AtualizacoesPendentesInsercao import AtualizacoesPendentesInsercao
import traceback
from dados.APIGetSource import APIGetSource


class DataHandler(object):
    """
    atributos:
      self.dh: módulo data_helpers. disponibiliza funções que facilitam a requisição, processamento e
        armazenamento de dados.
      self.uconecte: classe Uconecte. contém métodos que implementam interfaces das APIs uConecte com
        a automação.
      self.api_keys = dict(nome_api = api_key)
      self.api_urls = dict(nome_api = api_url)
      self.parar_se_exception = faz com que clausulas try/except parem a execução do programa
    métodos:
      add_api_keys = adiciona um conjunto de pares key-val à variável self.api_keys
      add_api_urls = adiciona um conjunto de pares key-val à variável self.api_urls
    """
    def __init__(self):
        self.dh = data_helpers
        self.uconecte = Uconecte()
        self.api_keys = None
        self.api_urls = None
        self.parar_se_exception = True
        self.db_ades_pendentes = AtualizacoesPendentesInsercao
        self.idRoboLog = 0
        self.data_source: APIGetSource = APIGetSource()

    def add_api_keys(self, api_labels, api_keys):
        """
        :type api_labels: dict
        :type api_keys: dict
        """
        for label in api_labels:
            self.api_keys[label] = api_keys

    def add_api_(self, api_labels, api_urls):
        """
        :type api_labels: dict
        :type api_urls: dict
        """
        for label in api_labels:
            self.api_keys[label] = api_urls

    def api_iniciar_log_robo(self, **kwargs) -> str:
        """
            <index_post>
            Parametros
            key = f689f1e12a0399fba803cb2365fc362f
            idRobo
            idSolicitacao ou idContrato
        """
        key = 'f689f1e12a0399fba803cb2365fc362f'

        post_data = {
            'key': key,
            'idRobo': kwargs.get('idRobo'),
            'idSolicitacao': kwargs.get('idSolicitacao', None),
            'idContrato': kwargs.get('idContrato', None)
        }
        print(f"\nCriando log com os dados: {post_data} \n")

        resp: Response = self.dh.make_request(
            method='POST',
            url='https://uconecte.me/api/v1/robos/salvar',
            params_data=post_data,
            msg=f"Em <iniciar_log_robo>"
        )

        try:
            print("roboLog", resp.content)
        except Exception:
            print(resp)

        try:
            self.idRoboLog: str = resp.json().get('idRoboLog', None)
        except:
            self.idRoboLog = None
            
        if self.idRoboLog is None:
            self.idRoboLog = 'null'

        return self.idRoboLog

    def api_registrar_log_robo(self, **kwargs):
        """
            <index_put>
            Parametros
            key = f689f1e12a0399fba803cb2365fc362f
            idRoboLog
            log - qualquer registro que queira salvar
            status - 0 = falha 2 = sucesso
            na index_post ela te retorna o idRoboLog, vc vai precisar manter
            ele pra enviar no index_put
        """
        self.idRoboLog = kwargs.get('idRoboLog', self.idRoboLog)

        key = 'f689f1e12a0399fba803cb2365fc362f'
        put_data = {
            'key': key,
            'idRoboLog': self.idRoboLog,
            'log': kwargs.get('log'),
            'status': kwargs.get('status')
        }
        print(f"\nRegistrando log com os dados: {put_data} \n")
        self.dh.make_request(
            method='PUT',
            url='https://uconecte.me/api/v1/robos/atualizar',
            params_data=put_data,
            msg=f"Em <registrar_log_robo>"
        )
        self.idRoboLog = 0

    @staticmethod
    def gerar_log_insercao(filename_path: str, **kwargs):
        from datetime import datetime as dt
        import csv

        data = f"{dt.today().day}/{dt.today().month}/{dt.today().year}"
        tempo = f"{dt.now().hour}:{dt.now().minute}:{dt.now().minute}"
        dados = {
            'codigo_con': kwargs.get('codigo_con'),
            'ade': kwargs.get('ade'),
            'data': data,
            'tempo': tempo
        }

        with open(f"{filename_path}.csv", 'a', newline='') as fObj:
            fieldnames = ['codigo_con', 'ade', 'data', 'tempo']
            writer = csv.DictWriter(fObj, fieldnames=fieldnames)

            sniff = csv.Sniffer()
            if not sniff.has_header(filename_path + 'csv'):
                writer.writeheader()

            print("Salvando os dados no log:", data)

            writer.writeheader()
            writer.writerow(dados)

    def data_handler_error_log(self, message, filename):
        self.dh.gen_log(message, f'manager_{filename}')
        traceback.print_exc(file=open(f'manager_{filename}.log', 'a'))


