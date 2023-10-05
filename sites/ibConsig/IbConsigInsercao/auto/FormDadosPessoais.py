from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
import pdb

class DadosPessoais(AutoGUI):
    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver)
        self.__nome = dados.get('nome', None)
        self.__sexo = dados.get('sexo', None)
        self.__estado_civil = dados.get('estadoCivil', None)
        self.__nome_conjuge = dados.get('nomeConjuge', None)
        self.__nome_mae = dados.get('nomeMae', None)
        self.__nome_pai = dados.get('nomePai', None)
        self.__cidade_nasc = dados.get('cidadeNascimento', None)
        self.__uf_nasc = dados.get('ufNascimento', None)
        self.__nacionalidade = dados.get('nacionalidade', None)
        self.__tipo_identidade = dados.get('tipoIdentidade', None)
        self.__emissor = dados['identidade']['emissor']
        self.__uf_identidade = dados['identidade']['uf']
        self.__n_identidade = dados['identidade']['numero']
        self.__data_emissao = dados['identidade']['dataEmissao']
        self.act.time_out = 0.2

    def preencher_nome(self):
        loc = "#servidor\\\\.nome"        
        if(self.sh.verificar_texto_campo_jquery(loc) == ''):
            self.sh.atribuir_valor_campo_jquery(loc, self.__nome)

    def preencher_sexo(self):
        print("Sexo:", self.__sexo)
        loc = "#servidor\\\\.sexo"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__sexo)

    def preencher_estado_civil(self):
        print("Estado civil:", self.__estado_civil)
        loc = "#servidor\\\\.estadoCivil"
        self.sh.atribuir_valor_campo_jquery(
            loc, self.__estado_civil, change=True)

    def preencher_nome_conjuge(self):
        print("Nome do cônge ou da cônja:", self.__nome_conjuge)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.nomeConjuge", self.__nome_conjuge)

    def preencher_nome_mae(self):
        print("Nomde da mãe:", self.__nome_mae)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.nomeMae", self.__nome_mae)

    def preencher_nome_pai(self):
        print("Nome do pai:", self.__nome_pai)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.nomePai", self.__nome_pai)

    def preencher_cidade_nascimento(self):
        print("Cidade nascimento:", self.__cidade_nasc)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.cidadeNascimento", self.__cidade_nasc)

    def preencher_uf_nascimento(self):
        print("UF Nascimento:", self.__uf_nasc)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.ufNascimento", self.__uf_nasc)

    def preencher_nacionalidade(self):
        print("Nacionalidade", self.__nacionalidade)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.nacionalidade", self.__nacionalidade)

    def preencher_tipo_identidade(self):
        print("Tipo de identidade", self.__tipo_identidade)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.identidade\\\\.tipo", self.__tipo_identidade)

    def preencher_emissor(self):
        print("Emissor:", self.__emissor)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.identidade\\\\.emissor", self.__emissor)

    def preencher_uf_identidade(self):
        print("UF identidade:", self.__uf_identidade)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.identidade\\\\.uf", self.__uf_identidade)

    def preencher_numero_identidade(self):
        print("N Identidade:", self.__n_identidade)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.identidade\\\\.numero", self.__n_identidade)

    def preencher_data_emissao(self):
        print("Data emissao:", self.__data_emissao)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.identidade\\\\.dataEmissao",
            self.__data_emissao
        )
