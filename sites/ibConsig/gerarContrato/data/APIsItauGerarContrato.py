from dados.RequestHandler import RequestHandler
from dados.helpers.fileHandlers.FileHandler import FileHandler
from sites.baseRobos.data_handler import DataHandler
from typing import List, Dict
from sites.baseRobos.core.DebugTools import DebugTools
from dados.APIGetSource import APIGetSource
from sites import ID_ROBOS
from sites.ibConsig.gerarContrato.data.InfosContrato import InfosContrato
from dados.dados_apis.keys import DEFAULT_KEY
from sites.ibConsig.gerarContrato.data import ENDPOINT_GERAR_CONTRATO
dbg = DebugTools(debugging=False)


class APIsItauGerarContrato(DataHandler):

    def __init__(self):
        super().__init__()
        self.uconecte.id_banco = 2
        self.data_source = APIGetSource("itau")

    def buscar_contratos_gerar(self) -> List[dict]:
        resp: Dict[str, List[dict]] = self.data_source.contratos_a_gerar()
        print(resp)
        contratos = resp['contratos']

        if len(contratos) == 0:
            print("Nenhum contrato para geração, trocando de fila...")
            return []

        return contratos

    def iniciarLogGerarContrato(self, codigoCon: str):
        self.api_iniciar_log_robo(
            idRobo=ID_ROBOS["ibConsig"]["gerarContrato"],
            idContrato=codigoCon)

    def registrarLogSucesso(self, msg: str):
        self.api_registrar_log_robo(
            log=msg, status=2)

    def registrarLogErro(self, msg: str):
        self.api_registrar_log_robo(
            log=f"ERRO: {msg}", status=0)

    def enviarPdfContrato(self, infosContrato: InfosContrato, pdfUnificado: FileHandler):
        reqHandler = RequestHandler(method="POST", url=ENDPOINT_GERAR_CONTRATO)
        reqHandler.data = {
            'key': DEFAULT_KEY,
            'ade': infosContrato.ade,
            'codigoCliente': infosContrato.codigoCliente,
            'codigoContrato': infosContrato.codigo,
            'base64': pdfUnificado.encodeToBase64(),
            'banco': 'itau'
        }
        reqHandler.send()
        reqHandler.checkForErrors()
