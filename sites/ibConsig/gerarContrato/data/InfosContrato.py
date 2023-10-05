

class InfosContrato:
    def __init__(self, **kwargs):
        self._dados = kwargs
        self._ade: str = kwargs.get("ade")
        self._codigoCon: str = kwargs.get("codigo_con")
        self._codigoCli: str = kwargs.get("codigo_cli")
        self._tipo: str = kwargs.get("tipo")
        self._valorContrato: str = kwargs.get("valor_con")
        self._prazoContrato: str = kwargs.get("prazo_con")
        self._dataDepCon: str = kwargs.get("data_dep_con")
        self._ade_refin_portabilidade: str = kwargs.get("ade_refin_portabilidade")
        self._orgao: str = kwargs.get("orgao")

    @property
    def novoContrato(self):
        return self._tipo == "NOVO SEM SEGURO"

    @property
    def refinanciamento(self):
        return self._tipo == "REFINANCIAMENTO" or self._tipo == "REFINANCIAMENTO SOMANDO MARGEM" 

    @property
    def portabilidade(self):
        return self._tipo == "PORTABILIDADE"

    @property
    def aumento_margem(self):
        return self._tipo == "NOVO MARGEM COMPLEMENTAR"

    @property
    def refinanciamento_margem(self):
        return self._tipo == "REFINANCIAMENTO SOMANDO MARGEM"

    @property
    def codigo(self):
        return self._codigoCon

    @property
    def ade(self):
        return self._ade

    @property
    def codigoCliente(self):
        return self._codigoCli

    @property
    def ade_refin_portabilidade(self):
        return self._ade_refin_portabilidade

    @property
    def orgao(self):
        return self._orgao
