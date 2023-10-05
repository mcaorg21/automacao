

class Solicitacao:
    def __init__(self, **kwargs):
        self.__idSolicitacao = kwargs.get("idSolicitacao")
        self.__idPessoa = kwargs.get("idPessoa")
        self.__fk_idPerfil = kwargs.get("fk_idPerfil")
        self.__cpf = kwargs.get("cpf")
        self.__matricula = kwargs.get("matricula")
        self.__especieBeneficio = kwargs.get("especieBeneficio")
        self.__sigla = kwargs.get("sigla")
        self.__orgao = kwargs.get("orgao")
        self.__estadual = kwargs.get("estadual")
        self.__inss = kwargs.get("inss")
        self.__federal = kwargs.get("federal")

    @property
    def orgao(self):
        return self.__orgao

    @orgao.setter
    def orgao(self, val: str):
        self.__orgao = val

    @property
    def idSolicitacao(self):
        return self.__idSolicitacao

    @property
    def idPessoa(self):
        return self.__idPessoa

    @property
    def fk_idPerfil(self):
        return self.__fk_idPerfil

    @property
    def cpf(self):
        return self.__cpf

    @property
    def matricula(self):
        return self.__matricula

    @property
    def especieBeneficio(self):
        return self.__especieBeneficio

    @property
    def sigla(self):
        return self.__sigla

    @property
    def estadual(self):
        return self.__estadual

    @property
    def inss(self):
        return self.__inss
    
    @property
    def federal(self):
        return self.__federal
