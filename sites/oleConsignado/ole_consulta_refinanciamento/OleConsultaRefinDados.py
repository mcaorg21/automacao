from sites.baseRobos.data_handler import DataHandler
from typing import List
from sites.baseRobos.core.DebugTools import DebugTools
dbg = DebugTools()


class OleConsultaRefinDados(DataHandler):
    def __init__(self):
        super().__init__()
        self.uconecte.id_banco = 123
        self.uconecte.consulta_refin_banco = "Olé"

    def atualizar_dados_consulta(self, solicitacao: dict, consulta: List[dict]):
        """
        Atualiza os dados da consulta por refinanciamentos tanto em casos de
        refinanciamentos, quanto em casos de refinanciamentos em potencial
        """
        if solicitacao.get("idSolicitacao", False):  # refinanciamentos
            dbg.warning(f"Atualizando consulta de refinanciamentos: {consulta}")
            self.uconecte.atualizar_consulta_refin(
                solicitacao=solicitacao, calcular_refin=consulta)

        elif solicitacao.get("idPerfil_pessoa", False):  # refinanciamentos em potencial
            dbg.warning(f"Atualizando consulta de refinanciamentos em potencial: {consulta}")
            self.uconecte.inserir_ofertas_crm({"refinanciamentos": consulta}, solicitacao)

    def atualizar_impossibilidade_consulta(self, solicitacao: dict, msg: str, restricao: bool=False):

        if solicitacao.get("idSolicitacao", False):  # refinanciamentos
            dbg.warning(f"Atualizando impossibilidade de consulta: {msg}")
            self.uconecte.atualizar_consulta_refin(
                solicitacao=solicitacao, msg_erro=msg)
            if restricao:
                dbg.warning(f"Inserindo bloqueio de perfil.: {msg}")
                self.uconecte.inserir_bloqueio_pessoa(solicitacao['idPessoa'])

        elif solicitacao.get("idPerfil_pessoa", False):  # refinanciamentos em potencial
            dbg.warning(f"Atualizando impossibilidade de consulta de refin potencial: {msg}")
            if restricao:
                dbg.warning("Inserindo bloqueio de perfil.")
                self.uconecte.inserir_bloqueio_pessoa(solicitacao['idPessoa'])
                self.uconecte.finalizar_consulta_crm(solicitacao, 2)
            else:
                self.uconecte.finalizar_consulta_crm(solicitacao, 3)


