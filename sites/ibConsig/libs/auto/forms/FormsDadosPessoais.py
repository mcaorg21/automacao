from selenium.webdriver import Chrome

from selenium.webdriver import Chrome

from sites.elementos import TextInput, Select
from sites.ibConsig.libs.dto.Contrato import Contrato


class FormDadosPessoais:
    def __init__(self, contrato: Contrato, **kwargs):
        self.__dados: Contrato = contrato
        self.dados_captcha: dict = {}
        self.iptNome: TextInput = kwargs.get("iptNome")
        self.selSexo: Select = kwargs.get("selSexo")
        self.selEstadoCivil: Select = kwargs.get("selEstadoCivil")
        self.iptNomeConjuge: TextInput = kwargs.get("iptNomeConjuge")
        self.iptNomeMae: TextInput = kwargs.get("iptNomeMae")
        self.iptNomePai: TextInput = kwargs.get("iptNomePai")
        self.iptCidadeNascimento: TextInput = kwargs.get("iptCidadeNascimento")
        self.selUFNascimento: Select = kwargs.get("selUFNascimento")
        self.selNacionalidade: Select = kwargs.get("selNacionalidade")
        self.selTipoIdentidade: Select = kwargs.get("selTipoIdentidade")
        self.iptNoIdentidade: TextInput = kwargs.get("iptNoIdentidade")
        self.selOrgaoEmissor: Select = kwargs.get("selOrgaoEmissor")
        self.selUFIdentidade: Select = kwargs.get("selUFIdentidade")
        self.iptDataEmissao: TextInput = kwargs.get("iptDataEmissao")

    def preencherNome(self):
        print(f"Preenchendo Nome: {self.__dados.pessoais.nome}")
        self.iptNome.carregar_elemento()
        #self.iptNome.act.click()
        self.iptNome.enviar_texto(self.__dados.pessoais.nome)
        self.iptNome.press_TAB()

    def preencherSexo(self):
        print(f"Selecionando Sexo: {self.__dados.pessoais.sexo}")
        self.selSexo.carregar_elemento()
        self.selSexo.selecionar_opcao(self.__dados.pessoais.sexo)

    def selecionarEstadoCivil(self):
        print(f"Selecionando EstadoCivil: {self.__dados.pessoais.estadoCivil}")
        self.selEstadoCivil.carregar_elemento()
        self.selEstadoCivil.selecionar_opcao(
            self.__dados.pessoais.estadoCivil)

    def preencherNomeConjuge(self):
        print(f"Preenchendo NomeConjuge: {self.__dados.pessoais.nomeConjuge}")
        self.iptNomeConjuge.carregar_elemento()
        self.iptNomeConjuge.act.click()
        nome_conjuge = self.__dados.pessoais.nomeConjuge
        if(nome_conjuge == ''):
            nome_conjuge = 'NÃO INFORMADO'
        self.iptNomeConjuge.enviar_texto(
            nome_conjuge)
        self.iptNomeConjuge.press_TAB()

    def preencherNomeMae(self):
        print(f"Preenchendo NomeMae: {self.__dados.pessoais.nomeMae}")
        self.iptNomeMae.carregar_elemento()
        #self.iptNomeMae.act.click()
        self.iptNomeMae.enviar_texto(
            self.__dados.pessoais.nomeMae)
        self.iptNomeMae.press_TAB()

    def preencherNomePai(self):
        print(f"Preenchendo NomePai: {self.__dados.pessoais.nomePai}")
        self.iptNomePai.carregar_elemento()
        #self.iptNomePai.act.click()
        self.iptNomePai.enviar_texto(
            self.__dados.pessoais.nomePai)
        self.iptNomePai.press_TAB()

    def preencherCidadeNascimento(self):
        print(f"Preenchendo Cidade Nascimento: {self.__dados.pessoais.cidadeNascimento}")
        self.iptCidadeNascimento.carregar_elemento()
        #self.iptCidadeNascimento.act.click()
        self.iptCidadeNascimento.enviar_texto(
            self.__dados.pessoais.cidadeNascimento)
        self.iptCidadeNascimento.press_TAB()

    def selecionarUFNascimento(self):
        print(f"Preenchendo UF Nascimento: {self.__dados.pessoais.ufNascimento}")
        self.selUFNascimento.carregar_elemento()
        self.selUFNascimento.selecionar_opcao(
            self.__dados.pessoais.ufNascimento)

    def selecionarNacionalidade(self):
        print(f"Preenchendo Nacionalidade: {self.__dados.pessoais.nacionalidade}")
        self.selNacionalidade.carregar_elemento()
        self.selNacionalidade.selecionar_opcao(
            self.__dados.pessoais.nacionalidade)

    def selecionarTipoIdentidade(self):
        print(f"Preenchendo Tipo Identidade: {self.__dados.pessoais.tipoIdentidade}")
        self.selTipoIdentidade.carregar_elemento()
        val: str = self.__dados.pessoais.tipoIdentidade
        if self.selTipoIdentidade.estaSelecionado(val):
            self.selTipoIdentidade.selecionar_opcao(
                self.__dados.pessoais.tipoIdentidade)

    def selecionarOrgaoEmissor(self):
        print(f"Preenchendo Orgao Emissor: {self.__dados.pessoais.tipoIdentidade}")
        self.selOrgaoEmissor.carregar_elemento()
        self.selOrgaoEmissor.selecionar_opcao(
            self.__dados.pessoais.orgaoEmissor)

    def selecionarUFIdentidade(self):
        print(f"Preenchendo UF Identidade: {self.__dados.pessoais.ufIdentidade}")
        self.selUFIdentidade.carregar_elemento()
        self.selUFIdentidade.selecionar_opcao(
            self.__dados.pessoais.ufIdentidade)

    def preencherNumeroIdentidade(self):
        print(f"Preenchendo No Identidade: {self.__dados.pessoais.numeroIdentidade}")
        self.iptNoIdentidade.carregar_elemento()
        self.iptNoIdentidade.act.click()
        self.iptNoIdentidade.enviar_texto(
            self.__dados.pessoais.numeroIdentidade)
        self.iptNoIdentidade.press_TAB()

    def preencherDataEmissao(self):
        print(f"Preenchendo Data Emissao: {self.__dados.pessoais.dataEmissao}")
        self.iptDataEmissao.carregar_elemento()
        self.iptDataEmissao.act.click()
        self.iptDataEmissao.enviar_texto(
            self.__dados.pessoais.dataEmissao)
        self.iptDataEmissao.press_TAB()
