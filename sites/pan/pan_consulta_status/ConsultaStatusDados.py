
from typing import List

from sites.baseRobos.data_handler import DataHandler


class ConsultaStatusDados(DataHandler):
    def __init__(self):
        super().__init__()
        self.data_source.nome_banco = "pan"

    def propostas_consultar(self) -> List[dict]:
        return self.data_source.consulta_status()
