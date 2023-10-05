from sites.ibConsig.libs.exceptions.Exceptions import NotFoundResultException
from typing import List
import pdb


class DadosConsultaRefin:

    def __init__(self, solicitacao: dict):
        self.id = solicitacao.get('idSolicitacao', None)
        if self.id is None:
            self.id = solicitacao.get('idPessoa')
        self.cpf = solicitacao['cpf']
        self.matricula = solicitacao['matricula']
        self.orgao = solicitacao['orgao']
        self.federal = solicitacao.get('federal', False)
        self.estadual = solicitacao.get('estadual', False)
        self.inss = solicitacao.get('inss', False)
        self.municipal = solicitacao.get('municipal', False)
        self.iniciada = False
        self.__lista_refins: List[dict] = []
        self.__dados:dict = solicitacao

    @property
    def refinanciamentos_consultados(self):
        return self.__lista_refins

    @property
    def rgps(self):
        return self.inss or self.municipal

    @property
    def estatutario(self):
        return self.federal or self.estadual

    @property
    def dados_solicitacao(self):
        return self.__dados

    def atualizar_lista_refins(self, dados_proposta):
        self.__lista_refins.append({
            'saldoDevedor': dados_proposta.saldo_devedor,
            'valorLiberado': dados_proposta.valor_liberado,
            'prazo': dados_proposta.prazo_refin,
            'valorParcela': dados_proposta.valor_parcela
        })
        print("Lista refinanciamentos atualizada:", self.__lista_refins)

    def validar_dados_consultados(self) -> bool:  # raises DadosConsultadosIncompletos
        print("Validando dados consultados...")
        keys_refins: List[str] = ['saldoDevedor', 'valorLiberado', 'prazo', 'valorParcela']
        if not self.__lista_refins and self.iniciada:
            raise NotFoundResultException("Lista de refinanciamentos vazia.")

        for refin in self.__lista_refins:
            for key in keys_refins:
                if not refin.get(key, False):
                    raise NotFoundResultException(
                        f"Dado do refinanciamento não encontrado: {key}")

        return True


class DadosConsultadosIncompletos(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg
