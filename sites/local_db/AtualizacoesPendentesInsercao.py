from tinydb import Query
from tinydb.database import TinyDB, Table
from PATHS import project_path
from pathlib import Path
from datetime import datetime as dt


class AtualizacoesPendentesInsercao(TinyDB):

    db_name = Path(project_path() + "/local_db/contratos_inseridos.json")
    print(db_name)

    def __init__(self, idBanco, **kwargs):
        super().__init__(self.db_name)
        self.idBanco = idBanco
        self.mensagem = kwargs.get('mensagem', "Aguardando Gerar Contrato")
        self.ade = kwargs.get('ade', None)
        self.codigoCon = kwargs.get('codigo_con', None)
        self.valorContrato = kwargs.get('valorContrato', None)
        self.textoMensagem = kwargs.get('textoMensagem', None)
        self.tabelaBanco = kwargs.get('tabelaBanco', None)
        self.obs = kwargs.get("obs", None)
        self.contratos_consultados: list = []
        self.timestamp = None

        self.registro_contratos: Table = self.table(f"banco-{self.idBanco}")

    @classmethod
    def criar_instancia(cls, id_banco,  **kwargs):
        mensagem = kwargs.get('mensagem', "Aguardando Gerar Contrato")
        ade = kwargs.get('ade', None)
        codigoCon = kwargs.get('codigo_con', None)
        valorContrato = kwargs.get('valorContrato', None)
        textoMensagem = kwargs.get('textoMensagem', None)
        tabelaBanco = kwargs.get('tabelaBanco', None)
        obs = kwargs.get("obs", None)
        timestamp = kwargs.get("timestamp", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))

        return AtualizacoesPendentesInsercao(
            idBanco=id_banco, mensagem=mensagem, ade=ade,
            codigo_con=codigoCon, valorContrato=valorContrato,
            tabelaBanco=tabelaBanco, textoMensagem=textoMensagem,
            obs=obs, timestamp=timestamp)

    def insert_dados_insercao(self):
        if self.ade is None or self.codigoCon is None:
            raise DadosEssenciaisNaoEncontrados

        dados: dict = {
            'idBanco': self.idBanco,
            'codigo_con': self.codigoCon,
            'ade': self.ade,
            'mensagem': self.mensagem,
            'valorContrato': self.valorContrato,
            'textoMensagem': self.textoMensagem,
            'tabelaBanco': self.tabelaBanco,
            'obs': self.obs,
            'timestamp': self.timestamp
        }

        print("Salvando atualizacoes no banco de dados: ",
              dados)
        self.registro_contratos.insert(dados)

    def select_contratos_a_atualizar(self) -> list:
        self.contratos_consultados = []
        contratos = self.registro_contratos.all()
        contrato: dict

        for contrato in contratos:
            self.contratos_consultados.append(contrato['codigo_con'])

        print("Contratos consultados:", self.contratos_consultados)

        return contratos

    def delete_dados_consultados(self):
        Dados = Query()
        for i in self.contratos_consultados:
            print("Excluindo registro dos contratos:", i)
            a = self.registro_contratos.remove(Dados.codigo_con == i)
            print(a)


class DadosEssenciaisNaoEncontrados(Exception):
    def __init__(self):
        self.msg: str = "ADE e/ou codigoCon não inseridos"

    def __repr__(self):
        return self.msg


if __name__ == "__main__":
    a = AtualizacoesPendentesInsercao(1)
    print(a.select_contratos_a_atualizar())
    a.delete_dados_consultados()
