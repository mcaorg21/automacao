"""
Modelo da tabela:

    +----------------+----------------+-------------------+
    +  id_instancia  + n_solicitacao  +  datetime_inicio  +
    +----------------+----------------+-------------------+
    +      int       +      str       +       str         +
    +----------------+----------------+-------------------+

"""
from tinydb import Query
from tinydb.database import TinyDB, Table
from PATHS import project_path
from pathlib import Path
from datetime import datetime as dt
from sites.local_db.instance_manager.Exceptions import ValidationError
from typing import Union, List


class InstanceManager(TinyDB):

    db_name = Path(project_path() + "/local_db/instance_manager/managements.json")

    def __init__(self, id_banco, id_instancia):
        super().__init__(str(self.db_name))
        self.id_banco: int = id_banco
        self.id_instancia: str = id_instancia
        self.n_solicitacao: Union[str, None] = None

        self.tabela: Table = self.table(f"banco-{self.id_banco}")

    def set_solicitacao(self, solicitacao: dict):
        self.n_solicitacao = solicitacao.get(
            'idSolicitacao', solicitacao.get('idPerfil_pessoa'))

    def iniciar_tabela_instancia(self):
        Instancia = Query()
        row = self.tabela.search(Instancia.id_instancia == self.id_instancia)
        if not row and self.id_instancia:
            print("Criando tabela instancia:", self.id_instancia)
            a = self.tabela.insert({
                "id_instancia": self.id_instancia,
                "n_solicitacao": None,
                "datetime_inicio": None,
            })
            print(a)

    def registrar_inicio_consulta(self):

        if not self.n_solicitacao:
            return
        self.__validar_dados()
        timestamp = dt.now().strftime("%m/%d/%Y, %H:%M:%S")

        dados = {
            "n_solicitacao": self.n_solicitacao,
            "datetime_inicio": timestamp,
        }
        print("Registrando consulta:", dados)
        Instancia = Query()
        self.tabela.update(dados, Instancia.id_instancia == self.id_instancia)

    def registrar_fim_consulta(self):
        if not self.n_solicitacao:
            return
        Instancia = Query()

        dados: dict = {
            "n_solicitacao": None,
            "datetime_inicio": None
        }
        self.tabela.update(
            dados, Instancia.id_instancia == self.id_instancia)

    def verificar_solicitacoes_consultadas(self):
        if not self.n_solicitacao:
            return
        Instancia = Query()

        consultas: List[dict] = self.tabela.search(Instancia.n_solicitacao == self.n_solicitacao)
        if not consultas:
            return True

        for consulta in consultas:
            if segundos_decorridos(consulta["datetime_inicio"]) < 240:
                return False

        return True

    def __validar_dados(self):  # raises ValidationError
        validate: dict = {
            "id_banco": self.id_banco,
            "id_instancia": self.id_instancia,
            "n_solicitacao": self.n_solicitacao,
        }
        if None in validate.values():
            raise ValidationError(validate)


def segundos_decorridos(date_time: str) -> int:
    data, horario = date_time.split(" ")
    mes, dia, ano = data.split("/")
    hora, mins, segs = horario.split(":")

    if int(dia) < dt.now().day:
        return (1440 * (dt.now().day - int(dia))) * 60

    t1 = (((dt.now().hour * 3600) + dt.now().minute * 60) + dt.now().second)
    t0 = (((int(hora) * 3600) + int(mins) * 60) + int(segs))
    return t1 - t0
