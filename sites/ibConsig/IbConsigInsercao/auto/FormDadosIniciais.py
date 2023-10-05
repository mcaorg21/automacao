from datetime import datetime as dt
from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from time import sleep

from sites.elementos import TextInput, Select
from selenium.webdriver.common.by import By

class DadosIniciais(AutoGUI):

    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver)
        self.__data_nasc = dados.get('dataNascimento', None)
        self.__data_con = dados.get('dataContrato', None)
        self.data_fator = dt.now().strftime("%d/%m/%Y")
        self.__codigo_loja = dados.get('codigoLoja', None)
        self.__data_renda = dados.get('dataRenda', None)
        self.renda = dados.get('renda', None)
        self.__entidade = dados.get('entidade', None)
        self.__uf_beneficio = dados.get('ufContaBeneficio', None)
        self.__tipo_beneficio = dados.get('tipoBeneficio', None)
        self.n_peculio = '10'
        self.codigo_profissao = '106'
        self.__val_margem = dados.get('valorParcela', None)
        self.__grau_instrucao = dados.get('grauInstrucao')
        self.estadual = dados.get('estadual', False)
        self.inss = dados.get('inss', False)
        self.federal = dados.get('federal', False)
        self.__dados = dados
        self.act.time_out = 0.2
        self.wait = 0.05
        self.__matricula = dados.get('matricula')
        self.__val_contrato = float(dados.get('valorContrato', 0.0))

    @property
    def dados_inciais(self):
        return self.__dados

    @property
    def entidade(self):
        if(self.__entidade == '0' and (self.estadual or self.federal)):
            raise PreenchimentoException('Favor editar propostam aprovar o contracheque + registrar o codigo de entidade de acordo com o IbConsig e pedir inserção automática')
        else:   
            return self.__entidade

    @property
    def valor_contrato(self):
        return self.__val_contrato

    @staticmethod
    def preencher_campo_loja(driver: Chrome, campo_loja: str):
        print("Preenchendo campo loja:", campo_loja)
        txt_ipt: TextInput = TextInput(driver, '[id="ade.loja"]')
        txt_ipt.carregar_elemento()
        txt_ipt.enviar_caracteres(campo_loja, delay=0.05)
        txt_ipt.press_TAB()

    def preencher_matricula_proposta_servidor(self):
        txt_input: TextInput = TextInput(
             driver=self.chrome_driver, seletor="input[id='input_registro_matricula_MatriculaDefault']")
        txt_input.carregar_elemento()

        if(self.__matricula[0:3] == '000'):
            self.__matricula = self.__matricula[3:]

        print("Preenchendo a matricula:", self.__matricula)
        #txt_input.act.click()
        txt_input.enviar_caracteres(self.__matricula, delay=0.05, clear=True)
        #txt_input.enviar_texto("input[id='input_registro_matricula_MatriculaDefault']", self.__matricula, By.XPATH)
        #txt_input.press_TAB()


        del txt_input

    def preencher_data_nascimento(self):
        print("Data de nacimento", self.__data_nasc)
        loc = 'input[id="servidor.dataNascimento"]'
        self.act.forcar_clique_stale_element(loc, pause=0.1)
        self.act.enviar_caracteres(
            seletor=loc, texto=self.__data_nasc,
            clear=False, delay=0.1
        )
        #sleep(self.wait)
        self.act.press_TAB(loc)

    def preencher_data_admissao(self):
        print("Data de admissao, sendo preenchida...")
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor="input[id='registro.dataAdmissao']")
        txt_input.carregar_elemento()

        print("Preenchendo data admissao:", '01/01/2000')
        txt_input.act.click()
        txt_input.enviar_caracteres(self.data_fator, delay=0.02, clear=False)
        txt_input.press_TAB()

        del txt_input

    def preencher_data_fator(self):
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor="input[id='ade.dataFator']")
        txt_input.carregar_elemento()

        print("Preenchendo data fator:", self.data_fator)
        txt_input.act.click()
        #txt_input.apagar_caracteres(10, delay=0.01)
        txt_input.enviar_caracteres(self.data_fator, delay=0.02, clear=False)
        txt_input.press_TAB()

        del txt_input

    def preencher_codigo_loja(self):
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor="input[id='ade.loja']")
        txt_input.carregar_elemento()

        print("Preenchendo codigo loja:", self.__codigo_loja)
        txt_input.act.click()
        txt_input.enviar_caracteres(self.__codigo_loja, delay=0.02)
        txt_input.press_TAB()

        del txt_input

    def preencher_data_renda(self):
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor="input[id='registro.dataRenda']")
        txt_input.carregar_elemento()

        print("Preenchendo data renda:", self.__data_renda)
        txt_input.act.click()
        txt_input.enviar_caracteres(self.__data_renda, delay=0.05)
        txt_input.press_TAB()

        del txt_input

    def preencher_valor_renda(self,valor_renda = '15000'):
        if self.renda is None:
            self.renda = valor_renda

        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor='input[id="registro.renda"]')
        txt_input.carregar_elemento()

        print("Preenchendo renda:", self.renda)
        #txt_input.act.click()
        txt_input.enviar_caracteres(self.renda, delay=0.02)
        txt_input.press_TAB()

        del txt_input

    def preencher_uf_beneficio(self):
        select: Select = Select(
            driver=self.chrome_driver, seletor='[id="ade.ufContaBeneficio"]')
        select.carregar_elemento()

        print("Preenchendo UF do Benefício:", self.__uf_beneficio)
        select.selecionar_opcao(self.__uf_beneficio, select_by="value")

        del select

    def preencher_tipo_beneficio(self):
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor='input[id="registro.codTipoBeneficio"]')
        txt_input.carregar_elemento()

        print("Preenchendo Tipo do Benefício:", self.__tipo_beneficio)
        txt_input.act.click()
        txt_input.enviar_caracteres(self.__tipo_beneficio, delay=0.02)
        txt_input.press_TAB()

        del txt_input

    def executar_busca_beneficio(self, wait=0.2):
        print("Executando busca por tipo do benefício...")
        script = "buscaTipoBeneficio()"

        sleep(wait)
        self.chrome_driver.execute_script(script)
        sleep(wait)

    def preencher_numero_peculio(self):
        print("Preenchendo número peculio:")
        loc_peculio = 'input[id="ade.numeroPeculio"]'
        self.act.enviar_texto(loc_peculio, self.n_peculio)

    @staticmethod
    def fechar_janela_margem_federal(driver: Chrome, rec = 0):
        print('Verificando se existe a janela de margem')
        if(len(driver.window_handles) > 1):
            print('Fechando a janela de margem...')
            driver.switch_to.window(driver.window_handles[1])
            print('Janela fechada...')
            driver.close()
            driver.switch_to.default_content()

        else:
            rec += 1
            if(rec >= 30):
                print('Janela de margem não aberta...')
                return
            else:
                sleep(1)
                print('Janela nao aberta... Nova tentativa...' + str(rec))
                self.fechar_janela_margem_federal(driver,rec)

        

    def preencher_cargo(self):
        print("Preenchendo cargo do servidor.")
        #self.act.select_drop_down(loc_profissao, '106')
        txt_input: TextInput = TextInput(
            driver=self.chrome_driver, seletor='input[id="registro.cargo"]')
        txt_input.carregar_elemento()

        print("Preenchendo renda:", 'EFETIVO')
        #txt_input.act.click()
        txt_input.enviar_caracteres('EFETIVO', delay=0.05)
        txt_input.press_TAB()

        del txt_input

    def preencher_valor_margem(self):
        print("Preenchendo valor da margem")

        format_val = str(float(
            self.__val_margem.replace(',', '.')
        ) + 1).replace('.', ',')

        loc_margem = 'input[id="margem.valor"]'
        try:
            margem_sistema = float(self.act.obter_valor(loc_margem).replace('.', '').replace(',', '.'))
        except:
            margem_sistema = 0
            pass
        if(margem_sistema != float(self.__val_margem.replace('.', '').replace(',', '.'))):
            try:
                self.act.enviar_texto(loc_margem, format_val)
            except:
                print('Preenchendo novamente a margem')
                self.preencher_valor_margem()

    def preencher_grau_instrucao(self):
        print("Grau de instrução:", self.__grau_instrucao)
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.grauInstrucao", self.__grau_instrucao)

    def preencher_profissao(self):
        print("Preenchendo profissão do servidor.")
        self.sh.atribuir_valor_campo_jquery(
            "#servidor\\\\.profissao", '106')


