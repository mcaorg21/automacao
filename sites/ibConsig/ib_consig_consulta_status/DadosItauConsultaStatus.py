from sites.baseRobos.data_handler import DataHandler
from typing import List
from sites.baseRobos.core.DebugTools import DebugTools
from dados.APIGetSource import APIGetSource
from sites.baseRobos.core.decorators import ApenasHorarioComercial
dbg = DebugTools(debugging=False)


class DadosItauConsultaStatus(DataHandler):

    def __init__(self):
        super().__init__()
        self.data_source.nome_banco = "itau"

    def atualiza_sincronizacao(self):
        self.data_source.atualizar_sincronizacao()

    @ApenasHorarioComercial(inicio=7, fim=20)
    def buscar_propostas_em_analise(self) -> List[dict]:
        return self.data_source.consulta_status()
