from typing import Union, Callable, List, Dict

from selenium.common.exceptions import TimeoutException

from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement

from sites.elementos import TextInput, Select, Button
from sites.ibConsig.libs.exceptions.Exceptions import TentativaAcessoCampoVazio, NotFoundResultException
from sites.ibConsig.libs.auto.scrapper.JanelaValoresEmprestimos import JanelaValoresEmprestimos
from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato
from sites.ibConsig.libs.auxiliares.ib_auxiliares import comparar_valores_contrato, comparar_taxas_de_origem

import pdb


class FormDadosProposta:
    def __init__(self, driver: Chrome, contrato: Contrato, **kwargs):
        self.__dados: Contrato = contrato
        self.dados_captcha: dict = {}
        self.selectTabela: Select = kwargs.get("selectTabela")
        self.selectTabelaEspecial: Select = kwargs.get("selectTabelaEspecial")
        self.__selectTabelaDisponivel: Union[Select, None] = None
        self.iptValorSolicitado: TextInput = kwargs.get("iptValorSolicitado")
        self.iptValorPrestacao: TextInput = kwargs.get("valorPrestacao")
        self.iptNumPrestacoes: TextInput = kwargs.get("iptNumPrestacoes")
        self.valorLiberadoMaximo: TextInput = kwargs.get("valorLiberadoMaximo")
        self.tabelaSimulacao: TextInput = kwargs.get("tabelaSimulacao")
        self.btnSimular: Button = kwargs.get("btnSimular")
        self.janelaValoresEmprestimos = JanelaValoresEmprestimos(driver)
        self.captchaCorreto = False
        self.captchaDisponivel = False
        self.filtroTabelaCarencia: Callable = lambda x: 1
        self.__tabelaCarencia: str = ""
        self.grau_instrucao_sistema: str  = contrato._Contrato__dados['grauInstrucaoWa']
        self.grau_instrucao_cliente: str = contrato._Contrato__dados['grauInstrucao']
        self.tabela_digital_sistema: str = contrato._Contrato__dados['tabelaDigital']

    @property
    def tabelaDisponivel(self):
        if self.__selectTabelaDisponivel is None:
            raise TentativaAcessoCampoVazio(campo="tabelaDisponivel")
        return self.__selectTabelaDisponivel

    @property
    def grau_instrucao_wa(self):
        return self.grau_instrucao_sistema

    @property
    def grau_instrucao_uconecte(self):
        return self.grau_instrucao_cliente

    @property
    def tabela_digital(self):
        return self.tabela_digital_sistema

    def anexarTabelaCarenciaNoContrato(self):
        if not self.__tabelaCarencia:
            raise TentativaAcessoCampoVazio(campo="<__tabelaCarencia>")
        self.__dados.incluirDadoAdicional(
            "tabelaBanco", self.__tabelaCarencia)

    def extrairValorParcela(self):
        self.iptValorPrestacao.carregar_elemento()
        val = self.iptValorPrestacao.act.get_attribute("value")
        self.__dados.valorPrestacao = val

    def verficarTipoTabela(self):
        try:
            self.selectTabela.carregar_elemento()
            self.__selectTabelaDisponivel = self.selectTabela
            print("Tabela normal")
        except TimeoutException:
            self.selectTabelaEspecial.carregar_elemento()
            self.__selectTabelaDisponivel = self.selectTabelaEspecial
            print("Tabela especial")

    def selecionarTabelaPelaTaxa(self,margem_erro=0,tipo_tabela_digital = True, possui_carencia = False):
        self.margem_erro = margem_erro
        self.tipo_tabela_digital = tipo_tabela_digital
        self.possui_carencia = possui_carencia
        opcaoTaxa = self.__buscarOpcaoTabela(
            optsTabela=self.tabelaDisponivel.listaOpcoes,
            funcComparacao=comparar_taxas_de_origem,
            valor=self.__dados.taxaTabelaFloat)

        if not opcaoTaxa:
            opcaoTaxa = self.__buscarOpcaoTabela(
                optsTabela=self.tabelaDisponivel.listaOpcoes,
                funcComparacao=comparar_taxas_de_origem,
                valor=self.__dados.taxaTabelaContratoFinalFloat)
            
            if not opcaoTaxa:
                return False

        valTaxa = opcaoTaxa.get_attribute("value")
        self.__tabelaCarencia = opcaoTaxa.text
        print("Selecionando Tabela Segundo a Taxa:", valTaxa)
        self.tabelaDisponivel.selecionar_opcao(valTaxa)
        print("Tabela selecionada: ", self.__tabelaCarencia)
        self.__dados.incluirDadoAdicional(
            "tabelaBanco", self.__tabelaCarencia)

    def selecionarTabelaPeloValorContrato(self):
        self.tabelaDisponivel.carregar_elemento()
        opcaoValor = self.__buscarOpcaoTabela(
            self.tabelaDisponivel.listaOpcoes, comparar_valores_contrato, self.__dados.valorContrato)
        self.tabelaDisponivel.selecionar_opcao(opcaoValor)

    def selecionarTabelaDiretaPortabilidade(self,opcaoValor, nome):
        self.tabelaDisponivel.carregar_elemento()
        self.tabelaDisponivel.selecionar_opcao(opcaoValor)
        self.__tabelaCarencia = nome
        self.__dados.incluirDadoAdicional(
            "tabelaBanco", self.__tabelaCarencia)
        

    def preencherValorParcela(self):
        self.iptValorPrestacao.carregar_elemento()
        self.iptValorPrestacao.act.click()
        if(float(self.__dados.valorPrestacao.replace('.','').replace(',','.')) > 1000):
            self.__dados.valorPrestacao = self.__dados.valorPrestacao.replace('.','')
        self.iptValorPrestacao.enviar_texto(self.__dados.valorPrestacao)
        self.iptValorPrestacao.press_TAB()

    def apagarValorSolicitado(self):
        self.iptValorSolicitado.carregar_elemento()
        self.iptValorSolicitado.apagar_caracteres(15, delay=0.01)

    def preencherNumeroPrestacoes(self):

        self.iptNumPrestacoes.carregar_elemento()
        self.iptNumPrestacoes.act.click()
        self.iptNumPrestacoes.enviar_texto(self.__dados.numPrestacoes)
        self.iptNumPrestacoes.press_TAB()

    def clicarBtnSimular(self):
        self.btnSimular.carregar_elemento()
        self.btnSimular.act.click()

    def extrairValorJanelaSimulacaoEmprestimo(self):
        self.janelaValoresEmprestimos.irParaJanela()
        self.janelaValoresEmprestimos.extrairTabela()
        self.janelaValoresEmprestimos.voltarJanelaPrincipal()

    def preencherValorSolicitado(self):
        print("Preenchendo valor solicitado:", self.__dados.valorContrato)
        self.iptValorSolicitado.act.click()
        self.iptValorSolicitado.enviar_texto(self.__dados.valorContrato.replace('.', ','))
        self.iptValorSolicitado.press_TAB()

    def atualizarValorSolicitado(self):
        dictLinha: Dict[str, str] = (self.janelaValoresEmprestimos.
                                     buscarLinhaPorPrazo(self.__dados.numPrestacoes))
        if dictLinha == False:
            return False
            
        print(f"Valor do contrato ({self.__dados.valorContrato}) atualizado para: {dictLinha['valor']}")
        self.__dados.valorContrato = dictLinha["valor"]
        self.__dados.incluirDadoAdicional(
            "novoValorContrato", "%.2f" % self.__dados.valorContrato)

    def atualizarValorSolicitadoPortabilidade(self):
        dictLinha: Dict[str, str] = (self.janelaValoresEmprestimos.
                                         buscarLinhaPorPrazo(self.__dados.numPrestacoes))

        if dictLinha == False:
            return False

        print(f"Valor do contrato ({self.__dados.valorContrato}) atualizado...")
        self.__dados.valorContrato = dictLinha["valor"]

        try:
            novo_valor = float(dictLinha["valor"].replace(',', '.')) - float(self.__dados.portabilidade.saldoDevedor.replace(',', '.'))
        except:
            novo_valor = float(dictLinha["valor"]) - float(self.__dados.portabilidade.saldoDevedor)
        
        self.__dados.incluirDadoAdicional(
            "novoValorLiquido", "%.2f" % novo_valor)
        print('Novo valor....')
        print("%.2f" % novo_valor)

    def __buscarOpcaoTabela(self, optsTabela: List[WebElement], funcComparacao: Callable, valor: str, rec = 0) -> WebElement:

        for option in optsTabela:
            # filtro: expressão lambda a ser aplicada para filtrar o tipo de taxa na tabela
            if not self.filtroTabelaCarencia(option.text):
                continue

            if(self.tipo_tabela_digital == False):
                palavra_exclusa_digital = 'DIG'
            else:
                palavra_exclusa_digital = 'NORMAL'
                    
            if (palavra_exclusa_digital in option.text):
                continue

            if(self.possui_carencia == False):
                palavra_exclusa_carencia= 'Car'
            else:
                palavra_exclusa_carencia = 'NORMAL'
                    
            if (palavra_exclusa_carencia in option.text):
                continue

            if funcComparacao(option.text, valor, self.margem_erro, tipo = 'entre_taxas'):
                print("Valor selecionado:", option.text)
                return option

            if funcComparacao(option.text, float(str(valor)[0:3]), self.margem_erro, tipo = 'entre_taxas'):

                print("Valor selecionado:", option.text)
                return option

        #raise NotFoundResultException(f"Valor ({valor}) não encontrado na tabela.")
        return False

