from sites.baseRobos.data_handler import DataHandler
from typing import List, Dict, Union
from sites.baseRobos.core.DebugTools import DebugTools
from dados.APIGetSource import APIGetSource
dbg = DebugTools(debugging=False)


class BMGDados(DataHandler):

    def __init__(self):
        super().__init__()
        self.uconecte.id_banco = 2
        self.data_source = APIGetSource("bmg")

    def buscar_propostas_liberar(self) -> List[dict]:
        propostas: List[dict] = self.data_source.propostas_a_liberar()

        if len(propostas) == 1:
            print("Nenhuma proposta com ADE para liberação!")
            return []

        return propostas
