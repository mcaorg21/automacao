import sys, pdb, json
from unidecode import unidecode
#sys.path.append('../../')
from dados.APIGetSource import APIDataSource
from sites.baseRobos.core.data_helpers import formatar_moeda2
from sites.baseRobos.manager import Manager
from sites.baseRobos.core.helpers import definir_nome_robo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sites.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from time import sleep


class Daycoval_Simulacao():
    def __init__(self):
        self.login = {'usuario' : 'DCE-UCONECTE0001', 'senha' : 'Tim909mca@'}
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/")
        sleep(2)
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/")
        self.act = SeleniumActions(self.driver)
        definir_nome_robo("Daycoval Simulacao")

    def logar(self):
        self.act.enviar_texto('//*[@id="FORMULARIO"]/table[1]/tbody/tr[1]/td[3]/input', self.login['usuario'], By.XPATH)
        self.act.enviar_texto('//*[@id="FORMULARIO"]/table[1]/tbody/tr[3]/td[3]/input', self.login['senha'], By.XPATH)
        sleep(1)
        self.act.clicar_elemento('//*[@id="FORMULARIO"]/table[1]/tbody/tr[5]/td[3]/input[2]', By.XPATH)


    def visitar_link_simulacao(self):
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/view/CJT05415.do?pmtr=xllZoBKWzRbga4GzzDEirSmGgeHTUzE0PwNqAN"
                        + "JMBXCUgOHXyTjCS7j0%2BjA7u%2F48bNL8N7so6BcPfFCNrHLR%2FHzjsGkhQHS2u94cDQQYO3FErSzx%2BQXAEDRutuhCH%2F4zNRoWhvGxJeMh7%2FYG3NUK%2Fk1IbQEK1FGjAavztBdJdOI%3D")
        


    def pegar_dados_cgi(self, contador_cgi):
        preencher_json = []

        for i in contador_cgi:        
            resultado = {}
            resultado["nome_tabela"] = str(unidecode(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[3]', By.XPATH)))
            resultado["valor_primeira_parcela"] = str(formatar_moeda2(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[4]', By.XPATH)))
            resultado["valor_ultima_parcela"] = str(formatar_moeda2(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[5]', By.XPATH)))
            resultado["renda_bruta"] = str(formatar_moeda2(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[6]', By.XPATH)))
            resultado["iof"] = str(formatar_moeda2(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[7]', By.XPATH)))
            resultado["taxa_total_mes"] = str(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[8]', By.XPATH))
            resultado["taxa_nominal_ano"] = str(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[9]', By.XPATH))
            resultado["cet"] = str(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[10]', By.XPATH))
            resultado["mensagem"] = str(self.act.obter_texto(f'//*[@id="to"]/tbody/tr[{i}]/td[11]', By.XPATH))
            preencher_json.append(resultado)
         
        return preencher_json


    def ver_quantas_cgi(self):
        lista_cgi = []
        quantidade_propostas = len(self.act.retornar_elementos('//*[@id="tg_conop"]',By.XPATH))

        if(quantidade_propostas > 0):
            for i in range(1, quantidade_propostas):
                produto = self.act.obter_texto(
                            f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[3]', By.XPATH)
                print(produto)
                if 'CGI' not in produto:
                    continue
                else:
                    lista_cgi.append(i)
            return self.pegar_dados_cgi(lista_cgi)
        else:
            print('Pulando consulta...')
            return
            
        
    def tipo_imovel(self, imovel):
        switcher = {
            "Residencial - Casa": 1,
            "Residencial - Apartamento" : 2,
            "Comercial - Loja" : 3,
            "Comercial - Sala Comercial" : 4,
            "Misto - Comercial / Residencial" : 5,
            "Imovel - Veraneio" : 6,
            "Terreno - Construcao Concluida" : 7,
        }

        opcao = switcher.get(imovel, "Erro imovel invalido")
        return opcao
    
    def apagar_campo(self, xpath):
        self.act.clicar_elemento(xpath, By.XPATH)
        self.driver.find_element_by_xpath(xpath).send_keys(Keys.DELETE)
   
   
    def realizar_simulacao(self):
        response = APIDataSource().get_request("daycoval_proposta_imoveis_simulacao")
        todas_propostas = json.loads(response.text)
        print(todas_propostas['tipo'])
        self.visitar_link_simulacao()
        for proposta in todas_propostas['consulta']:
            print('entrou no for')
            dados_consulta = {}
            # Tipo Imovel
            self.act.clicar_elemento('//*[@id="cd_tusobem_chzn"]/a/div/b', By.XPATH)
            self.act.enviar_texto('//*[@id="cd_tusobem_chzn"]/div/div/input', self.tipo_imovel(proposta['tipoImovel']), By.XPATH)
            self.act.press_enter('//*[@id="cd_tusobem_chzn"]/div/div/input', By.XPATH)
            # Valor do Imóvel
            self.apagar_campo('//*[@id="vl_totabem"]')
            try:
                self.act.enviar_texto('//*[@id="vl_totabem"]', proposta['valorImovel'], By.XPATH)
            except:
                continue
            # Valor Credito Pretendido
            self.apagar_campo('//*[@id="vl_princip"]')
            try:
                self.act.enviar_texto('//*[@id="vl_princip"]', proposta['valorCredito'], By.XPATH)
            except:
                continue
            # Data de nascimento
            # Convertendo o padrão americano ao brasileiro
            array_data = proposta['dataNascimento'].split('-')
            data_nascimento = array_data[2] + '-' + array_data[1] + '-' + array_data[0]
            self.act.enviar_texto('//*[@id="dt_nascipr"]', data_nascimento, By.XPATH)
            # bem quitado
            self.act.clicar_elemento('//*[@id="lg_bemquit"]', By.XPATH)
            self.act.clicar_elemento('//*[@id="lg_bemquit"]', By.XPATH)
            # Prazo
            self.apagar_campo('//*[@id="qt_mesesop"]')
            self.act.enviar_texto('//*[@id="qt_mesesop"]', proposta['parcelaSelecionada'], By.XPATH, clear=True)
            # Clicar em calcular
            self.act.clicar_elemento("CAL", By.ID)
            try:
                self.act.clicar_elemento("CAL", By.ID)
            except:
                pass
            carregou = False
            while carregou is False:
                try:
                    self.driver.find_element_by_xpath('/html/body/div[9]/h5/img')
                except NoSuchElementException:
                    carregou = True
            dados_consulta["idSolicitacao"] = proposta['idSolicitacao']
            dados_consulta["proposta"] = self.ver_quantas_cgi()

            if(dados_consulta["proposta"]):
                response_post = APIDataSource().post_request_v3('enviar-proposa-imobiliaria-daycoval', dados_consulta)
                print(response_post)
                print(response_post.text)
            else:
                print('Sem propostas... Pulando a consulta...')
                continue
            
        print("ACABOU !!!")
        while True:
            self.driver.refresh()
            sleep(5)
            print('esta na espera')
            response = APIDataSource().get_request("daycoval_proposta_imoveis_simulacao")
            todas_propostas = json.loads(response.text)
            if todas_propostas['tipo'] == 'success':
                self.realizar_simulacao()

    def main(self):
        self.logar()
        self.realizar_simulacao()

if __name__ == '__main__':
    robo = Daycoval_Simulacao()
    while True:
        robo.main()

'''
232 --> error
232 --> Correta
'''