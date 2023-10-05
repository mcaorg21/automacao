import sys, pdb, json
#sys.path.append('../../')
from dados.APIGetSource import APIDataSource
from sites.baseRobos.core.helpers import formatar_moeda
from sites.baseRobos.manager import Manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sites.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from time import sleep


class Ole_Portal_Orienta():
    def __init__(self):
        self.login = {"usuario": "bbo\\54397", "senha": "88199455A@"}
        self.driver = webdriver.Chrome()
        self.driver.get("https://orienta.oleconsignado.com.br/Paginas/home.aspx")
        self.act = SeleniumActions(self.driver)
    
    def logar(self):
        # usuario
        self.act.enviar_texto('//*[@id="userNameInput"]', self.login['usuario'], By.XPATH)
        # senha
        self.act.enviar_texto('//*[@id="passwordInput"]', self.login['senha'], By.XPATH)
        # carregando --> Ja espera carregar automatico 
        self.act.clicar_elemento('//*[@id="submitButton"]', By.XPATH)
        self.pegar_dados_get()
        
    
    def pegar_dados_get(self):
        response = APIDataSource().get_request("proposta-recebimento-ole")
        todas_propostas = json.loads(response.text)
        for proposta in todas_propostas[1:]:
            self.driver.get("https://www4.bonsucessoconsignado.com.br/statuscontrato/")
            print(proposta)
            self.enviar_dados_consulta(proposta)
        self.driver.quit()

    def enviar_dados_consulta(self, dados):
        # cpf
        self.act.clicar_elemento('//*[@id="ctl00_Main_RadioButtonListBusca_0"]', By.XPATH)
        # Valor
        self.act.enviar_texto('//*[@id="ctl00_Main_TextBoxBusca"]', dados[1], By.XPATH)
        # Pesquisar
        self.act.clicar_elemento('//*[@id="ctl00_Main_btnPesquisar"]', By.XPATH)
        try:
            # Nenhum registro
            self.act.obter_texto('//*[@id="ctl00_Main_gvProposta_ctl01_Label4"]', By.XPATH)
            pdb.set_trace()
        except:
            pass
        self.pegar_dados(dados)
        
    def mudar_tela(self):
        for pagina in self.driver.window_handles:
                self.driver.switch_to.window(pagina)

    def pegar_dados(self, dados):
        for i in range(2, 20):
            try:
                comparar_ade = self.act.obter_texto(f'/html/body/form/div[4]/div/div[1]/div/table/tbody/tr[{i}]/td[2]/a', By.XPATH)
            except:
                break
            if comparar_ade == dados[0]:
                numero_tr_correto = i
                break
            else:
                continue
        # Valor liberado
        valor_liberado = self.act.obter_texto(f'/html/body/form/div[4]/div/div[1]/div/table/tbody/tr[{numero_tr_correto}]/td[5]/a', By.XPATH)
        # Valor Parcela
        valor_parcela = self.act.obter_texto(f'/html/body/form/div[4]/div/div[1]/div/table/tbody/tr[{numero_tr_correto}]/td[7]/a', By.XPATH)
        # clica na ade
        self.act.clicar_elemento(f'/html/body/form/div[4]/div/div[1]/div/table/tbody/tr[{numero_tr_correto}]/td[2]/a', By.XPATH)
        pagina_principal = self.driver.current_window_handle
        if len(self.driver.window_handles) > 1:
            for pagina in self.driver.window_handles:
                if pagina != pagina_principal:
                    self.driver.switch_to.window(pagina)
        status_detalhado = self.act.obter_texto('//*[@id="lblStatusDetalhado"]', By.XPATH)
        observacao = self.act.obter_texto('//*[@id="dlObservacao_ctl00_OBSERVACAOLabel"]', By.XPATH)
        payload = {
            "codigoCon": dados[2], 
            "ade": dados[0], 
            "statusPropostaBanco": status_detalhado, 
            "observacaoDetalhadaBanco": observacao, 
            "valorContrato": valor_liberado,
            "parcelaContrato": valor_parcela,
            "key": "f689f1e12a0399fba803cb2365fc362f"
            }
        response = APIDataSource().post_request_v2('enviar-dados-recebimento-ole', payload)
        print(response)
        self.driver.close()
        self.mudar_tela()



if __name__ == '__main__':
    while True:
        robo = Ole_Portal_Orienta()
        robo.logar()
        print("------ESPERANDO 2 HORAS------")
        sleep(7200)
    '''
    //*[@id="ctl00_Main_gvProposta"]/tbody/tr[2]
    /html/body/form/div[4]/div/div[1]/div/table/tbody/tr[2]/td[2]/a
    '''

