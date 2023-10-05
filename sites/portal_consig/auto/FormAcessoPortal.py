from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
import pdb
from time import sleep

class FormAcessoPortal(AutoGUI):
    def __init__(self, driver: Chrome):
        super().__init__(driver, wait_timeout=4)
        self.convenio: str = ""
        self.novo_acesso = True

    def selecionar_convenio_consulta(self):
        print("Selecionando portal: ", self.convenio)

        if not self.convenio:
            raise Exception("Atributo <convenio> não pode estar vazio")

        loc_convenio = ""

        if self.convenio.upper() == "SP":       
            xpath_1 = '/html/body/div/div/form/div[2]/div/div[6]/div[2]/fieldset/div/div[1]/span[2]/input'
            xpath_2 = '/html/body/div/div/form/div[2]/div/div[6]/div[2]/fieldset/div/div[2]/fieldset/span/label/input'
            loc_convenio = '//*[contains(text(), "ESTADO DE SÃO PAULO")]/../input'
        elif self.convenio.upper() == "MT":
            xpath_1 = '/html/body/div/div/form/div[2]/div/div[4]/div[2]/fieldset/div/div[1]/span[2]/input'
            xpath_2 = '/html/body/div/div/form/div[2]/div/div[4]/div[2]/fieldset/div/div[2]/fieldset/span/label[2]/input'
            loc_convenio = '//*[contains(text(), "MATO GROSSO")]/../input'
        elif self.convenio == "prefeitura_sp":
            xpath_1 = '/html/body/div/div/form/div[2]/div/div[5]/div[2]/fieldset/div/div[1]/span[2]/input'
            xpath_2 = '/html/body/div/div/form/div[2]/div/div[5]/div[2]/fieldset/div/div[2]/fieldset/span/label/input'
            loc_convenio = '//*[contains(text(), "PREFEITURA DO MUNICÍPIO DE SÃO PAULO")]/../input'

        self.act.hover_e_clique(xpath_1, self.by.XPATH)
        sleep(1)
        self.act.hover_e_clique(xpath_2, self.by.XPATH)
        sleep(2)
        self.act.hover_e_clique('/html/body/div/div/form/div[2]/div/div[7]/input',self.by.XPATH)
        #self.act.hover_e_clique(loc_convenio, self.by.XPATH)

    def clicar_botao_acessar(self):
        print("Clicando em acessar.")
        loc = '[class="botaoAcessar"]'

        self.act.hover_e_clique(loc)


