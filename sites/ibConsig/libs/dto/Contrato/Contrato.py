from typing import Dict

from sites.ibConsig.libs.dto.Contrato.DadosBancarios import DadosBancarios
from sites.ibConsig.libs.dto.Contrato.DadosEndereco import DadosEndereco
from sites.ibConsig.libs.dto.Contrato.DadosPessoais import DadosPessoais
from sites.ibConsig.libs.exceptions.Exceptions import TentativaAcessoCampoVazio, ValidacaoInsercaoException
from sites.ibConsig.libs.dto.Contrato.Portabilidade import Portabilidade


class Contrato:
    def __init__(self, contrato: Dict[str, str]):
        self.__dados: Dict[str] = contrato
        self.__portabilidade: Portabilidade = Portabilidade(contrato)
        self.__dadosBancarios: DadosBancarios = DadosBancarios(contrato)
        self.__dadosPessoais: DadosPessoais = DadosPessoais(contrato)
        self.__dadosEndereco: DadosEndereco = DadosEndereco(contrato)
        self.__valorContratoAlterado: bool = False
        self.__valorTabela = contrato.get("taxaJurosTabela", False)
        if 'dados_portabilidade' in contrato:
            self.__valorTabelaContratoFinal = contrato['dados_portabilidade'].get('taxaJurosContratoFinal',False)
        self.__dadosAdicionais: dict = {}

    def validarDadosInsercao(self):
        print("+---------------------------------------------+")
        print("+----------- Validando Dados Inserção --------+")
        print("+---------------------------------------------+")
        print(">>> ADE...")
        if not self.retornarDadoAdicional("ADE"):
            raise ValidacaoInsercaoException(
                campo="ADE", dado=self.retornarDadoAdicional("ADE"))
        # print(">>> tabelaBanco...")
        # if not self.retornarDadoAdicional("tabelaBanco"):
        #     raise ValidacaoInsercaoException(
        #         campo="tabelaBanco", dado=self.retornarDadoAdicional("tabelaBanco"))
        # print(">>> valorContratoAlterado")
        # if not self.__valorContratoAlterado:
        #     raise ValidacaoInsercaoException(
        #         campo="valorContratoAlterado", dado=self.__valorContratoAlterado)

        print("Atualizando contrato.")

    def incluirDadoAdicional(self, key, val):
        self.__dadosAdicionais[key] = val

    def retornarDadoAdicional(self, key): 
        return self.__dadosAdicionais.get(key, None)

    @property
    def pessoais(self):
        return self.__dadosPessoais

    @property
    def banco(self):
        return self.__dadosBancarios

    @property
    def portabilidade(self):
        return self.__portabilidade

    @property
    def endereco(self):
        return self.__dadosEndereco

    @property
    def valorContrato(self):
        return self.__dados["valorContrato"]

    @valorContrato.setter
    def valorContrato(self, valor):
        self.__dados["valorContrato"] = valor
        self.__valorContratoAlterado = True

    @property
    def contrato(self):
        return self.__dados

    @property
    def codigo(self):
        return self.__dados["codigo_con"]

    @property
    def entidade(self) -> str:
        return self.__dados["codigoEntidade"]

    @property
    def cpf(self) -> str:
        return self.__dados["cpf"]

    @property
    def matricula(self) -> str:
        return self.__dados["matricula"]

    @property
    def dataNascimento(self) -> str:
        return self.__dados["dataNascimento"].replace("/", "")

    @property
    def taxaTabela(self):
        if not self.__valorTabela:
            raise TentativaAcessoCampoVazio(campo="self.__valorTabela")
        return self.__valorTabela

    @property
    def taxaTabelaFloat(self):
        if not self.__valorTabela:
            raise TentativaAcessoCampoVazio(campo="self.__valorTabela")
        return float(self.__valorTabela)

    @property
    def taxaTabelaContratoFinalFloat(self):
        if not self.__valorTabelaContratoFinal:
            raise TentativaAcessoCampoVazio(campo="self.__valorTabelaContratoFinal")
        return float(self.__valorTabelaContratoFinal)

    @taxaTabela.setter
    def taxaTabela(self, taxa):
        self.__valorTabela = taxa

    @property
    def numPrestacoes(self):
        return self.__dados["prazoContrato"]

    @property
    def valorPrestacao(self):
        return self.__dados["valorParcela"]

    @valorPrestacao.setter
    def valorPrestacao(self, val):
        self.__dados["valorParcela"] = val

    @property
    def codigoLoja(self):
        return self.__dados["codigoLoja"]

    @property
    def dataRenda(self):
        return self.__dados["dataRenda"]

    @property
    def valorRenda(self):
        return self.__dados["renda"]

    @property
    def ufBeneficio(self):
        return self.__dados["ufContaBeneficio"]

    @property
    def tipoBeneficio(self):
        return self.__dados["tipoBeneficio"]

    @property
    def grauInstrucao(self):
        return self.__dados["grauInstrucao"]
