from sites.baseRobos.data_handler import DataHandler
from typing import List, Dict, Union
from sites.baseRobos.core.DebugTools import DebugTools
from dados.APIGetSource import APIGetSource
dbg = DebugTools(debugging=False)


class ItauGerarContratoDados(DataHandler):

    def __init__(self):
        super().__init__()
        self.uconecte.id_banco = 2
        self.data_source = APIGetSource("itau")

    def buscar_contratos_gerar(self) -> List[dict]:
        resp: Dict[str, List[dict]]= self.data_source.contratos_a_gerar()
        print(resp)
        contratos = resp['contratos']

        if len(contratos) == 0:
            print("Nenhum contrato para geração, trocando de fila...")
            return []

        return contratos
