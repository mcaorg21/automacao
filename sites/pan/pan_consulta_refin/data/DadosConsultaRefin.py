from sites.baseRobos.data_handler import DataHandler
import PATHS
from tinydb import TinyDB, Query
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List
dbg = DebugTools(debugging=False)
import pdb

class DadosConsultaRefin(DataHandler):

    id_banco = 68

    def __init__(self):
        super().__init__()
        self.api_urls = {
            'SOLICITACOES': "http://localhost:5000/routing/solicitacoes-refin/pan",
        }
        self.api_key = 'f689f1e12a0399fba803cb2365fc362f'
        self.uconecte.id_banco = self.id_banco
        self.inverter_ordem = False
        self.limitar_fila: int = 20

    def get_solicitacoes_consultar(self) -> list:
        fila: List[dict] = []
        data = {
            "instance": "main"
        }
        
        resp = self.dh.make_request(
            method='GET',
            url=self.api_urls['SOLICITACOES'],
            params_data=data,
            json=True,
            msg="Em <get_solicitacoes_consultar>"
        )
        if not resp:
            return []

        return [resp]

    def atualizar_consulta_refins(self, solicitacao: dict, refins: List[dict]):
        dbg.debugger()
        if solicitacao.get("idSolicitacao", False):
            dbg.warning(f"Atualizando consulta de refinanciamentos: {refins}")
            self.uconecte.inserir_historico_solicitacao(
                id_solicitacao=solicitacao['idSolicitacao'],
                mensagem="Consulta Refinanciamento Pan"
            )
            self.uconecte.calcular_refinanciamento(refins, solicitacao)
        elif solicitacao.get("idPerfil_pessoa", False):
            dbg.warning(f"Atualizando consulta de refinanciamentos em potencial: {refins}")
            self.uconecte.inserir_ofertas_crm({"refinanciamentos": refins}, solicitacao)
        else:
            raise Exception(
                "<Uconecte.atualizar_refins_indisponiveis> "
                "Campo idSolicitacao e idPerfil_pessoa ausentes no objeto "
                "passado no parâmetro <solicitacao>")

    def atualizar_refins_indisponiveis(self, solicitacao: dict, msg):
        print(f'Não possui contratos. Mensagem Sistema: {msg}')
        dbg.debugger()
        idSolicitacao: str = solicitacao.get("idSolicitacao", None)
        idPerfil_pessoa: str = solicitacao.get("idPerfil_pessoa", None)

        if idSolicitacao is not None:
            dbg.warning(f"Atualizando impossibilidade de consulta: {msg}")
            self.uconecte.inserir_historico_solicitacao(
                id_solicitacao=idSolicitacao,
                mensagem=f"Sistema Pan: {msg}")

            self.uconecte.inserir_historico_solicitacao(
                id_solicitacao=idSolicitacao,
                mensagem="Consulta Refinanciamento Pan")

        elif idPerfil_pessoa is not None:
            dbg.warning(f"Atualizando impossibilidade de consulta de refin potencial: {msg}")
            self.uconecte.finalizar_consulta_crm(solicitacao, 3)
        else:
            raise Exception(
                "<Uconecte.atualizar_refins_indisponiveis> "
                "Campo idSolicitacao e idPerfil_pessoa ausentes no objeto "
                "passado no parâmetro <solicitacao>")

    def atualizar_restricao(self, solicitacao: dict, msg: str):
        dbg.warning("Cadastrando restrição", solicitacao['idPessoa'], msg)

        idSolicitacao: str = solicitacao.get("idSolicitacao", None)
        idPerfil_pessoa: str = solicitacao.get("idPerfil_pessoa", None)

        self.uconecte.inserir_bloqueio_pessoa(
            id_pessoa=solicitacao['idPessoa'],
        )

        if idSolicitacao is not None:
            self.uconecte.inserir_historico_solicitacao(
                id_solicitacao=solicitacao['idSolicitacao'],
                mensagem=f"Sistema Pan: {msg}"
            )
            self.uconecte.inserir_historico_solicitacao(
                id_solicitacao=solicitacao['idSolicitacao'],
                mensagem="Consulta Refinanciamento Pan")

        elif idPerfil_pessoa is not None:
            self.uconecte.finalizar_consulta_crm(solicitacao, 2)
        else:
            raise Exception(
                "<Uconecte.atualizar_refins_indisponiveis> "
                "Campo idSolicitacao e idPessoa ausentes no objeto"
                "passado no parâmetro <solicitacao>")


def query_empregador_orgao(**kwargs) -> dict:
    db_path = PATHS.project_path() + "/pan/database/refinanciamento.json"
    db = TinyDB(db_path).table("TAGS")

    orgao: str = kwargs.get('orgao', None)
    sigla: str = kwargs.get('sigla', None)

    FEDERAL = kwargs.get('federal', False)
    INSS = kwargs.get('inss', False)

    if FEDERAL:
        sigla = "FEDERAL"
        tags = db.get(Query().sigla == sigla)
    elif INSS:
        sigla = "INSS"
        tags = db.get(Query().sigla == sigla)
    else:
        tags = db.get(Query().sigla == sigla)

    query_empregador = tags[orgao].keys()
    query_orgao = tags[orgao].values()

    return {'empregador': list(query_empregador)[0],
            'orgao': list(query_orgao)[0]}
