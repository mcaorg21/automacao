import datetime as dt
from typing import List

from dados.database.dao.RoboLogDAO import RoboLogDao
from dados.database.db_conf.connection import conect_db
import pygal

class RoboLogDataSource:
    def __init__(self, id_robo):
        self.__id_robo = id_robo
        self.__db = conect_db(database="mcaorg1_uconecte")
        self.__cur = self.__db.cursor()

    def consultar_log(self, limite: int=10) -> List[RoboLogDao]:
        query = (f"SELECT * FROM robo_log "
                 f"WHERE fk_idRobo = {self.__id_robo} "
                 f"order by dataConsulta desc limit {limite};")

        self.__cur.execute(query)

        logs: List[dict] = self.__cur.fetchall()
        if logs is None:
            raise ResultadoNaoEncontrado(query)

        self.__cur.close()

        return [RoboLogDao(**log) for log in logs]

    def consultar_status(self, status_log, start, end, limite=500) -> List[int]:
        query = (f"SELECT count(status) FROM robo_log "
                 f"WHERE fk_idRobo = {self.__id_robo} AND "
                 f"status = {status_log} AND "
                 f"DATE(dataConsulta) BETWEEN '{start}' AND '{end}' "
                 "GROUP BY DATE(dataConsulta);"
                 )
        print(query)
        self.__cur.execute(query)

        logs: List[dict] = self.__cur.fetchall()
        if logs is None:
            raise ResultadoNaoEncontrado(query)
        self.__cur.close()

        return [status.get('count(status)') for status in logs]


class ResultadoNaoEncontrado(Exception):
    def __init__(self, query: str):
        super().__init__(query)
        self.query = query

    def __repr__(self):
        return "A query não retornou resultados."
