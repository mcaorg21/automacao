
import os,time,pdb,re,requests,json,sys,os,platform,datetime, random
#winsound

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

from sites.baseRobos.core.helpers import deleta_todos_arquivos
from sites.baseRobos.core.data_helpers import similaridade

from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from dados.APIDataSource import APIDataSource

from time import sleep


HORARIO_COMERCIAL = 8, 20


class Tarefas(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.xpath_menu = {
            "chat": {
                "icone": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div/span/div/div[1]/div[1]",
                "criar" : "/html/body/div[1]/div/div/div[2]/div[3]/header/header/div/span/div/span/div[1]/div",
                "pesquisar" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/button",
                "input_pesquisa" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p",
                "telefone_encontrado" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[2]/div/div/span",
                "loading_pesquisa" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/span/div/span/svg/circle",
                "clique_telefone_resultado" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[2]/div/div/span",
                "clique_input_texto_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p",
                "input_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p",
                "enviar_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span"
            },            
            "status": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div/span/div/div[1]/div[2]",
            "canais": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div/span/div/div[1]/div[4]",
        }

        self.init_chrome_driver(import_driver=driver)
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.request_post = APIDataSource()

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome):

        run = Tarefas(driver)
        try:
            run.iniciar_rotina()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    #@ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_rotina(self):    

        self.iniciar_conversa(random.randint(2,15))
        #continuar_conversa()
        #postar_status()
        #participar_comunidade()
        #retirar_participacao_comunidade()

    def iniciar_conversa(self, limite_envios = 2):

        for i in range(1, limite_envios):

            #pegar lista pre definida em csv
            telefone = ['31993448917','31993448824']

            telefone = telefone[random.randint(0,len(telefone) -1)]

            self.act.clicar_elemento(self.xpath_menu['chat']['icone'], By.XPATH)
            self.act.clicar_elemento(self.xpath_menu['chat']['criar'], By.XPATH)
            self.act.clicar_elemento(self.xpath_menu['chat']['pesquisar'], By.XPATH)
            self.act.enviar_texto(self.xpath_menu['chat']['input_pesquisa'], telefone, By.XPATH)

            self.verificar_loading(self.xpath_menu['chat']['loading_pesquisa'], "Pesquisa Telefone")

            
            if(self.act.quantidade_elemento(self.xpath_menu['chat']['telefone_encontrado'], By.XPATH) == 1):
                telefone_encontrado = self.act.obter_atributo(self.xpath_menu['chat']['telefone_encontrado'], 'title', By.XPATH).replace(" ","")

                if(similaridade(telefone_encontrado,telefone) > 70):
                    print('VVVVVVVVVVVVVVVVVVVVV TELEFONE ENCONTRADO VVVVVVVVVVVVVVVVVVVVV')
                    self.act.clicar_elemento(self.xpath_menu['chat']['clique_telefone_resultado'], By.XPATH)
                    sleep(random.randint(2,5))

                    print("Enviando mensagem...")
                    random_mensagem = self.get_assunto_aleatorio_ia(random.randint(1,11))

                    self.enviar_mensagem(True, random_mensagem)

                    sleep(random.randint(1,3))

                else:
                    print('XXXXXXXXXXXXXXXXXX TELEFONE NÃO ENCONTRADO XXXXXXXXXXXXXXXXXX')
                    continue

            #sleep(random.randint(9,240))

        sleep(random.randint(2,5))
    

    def enviar_mensagem(self, ia = False, mensagem_contexto = "oi tudo bem?"):

        if(ia == True):

            request = self.request_post.post_request_v3("ia-vertex-texto", {
                "key": "f689f1e12a0399fba803cb2365fc362f",
                "texto": mensagem_contexto,
                "tokens": random.randint(30,60)
            })
            
            retorno = request.json()

            if(retorno['tipo'] == "alert"):
                print("XXXXXXXXXXXXXX ERRO JSON XXXXXXXXXXXXXX")
                mensagem_contexto =[ "Houve um erro ao buscar a IA mas ssegue a vida!"]
            else:
                mensagem_contexto = retorno['resposta'].split("\n")

        sleep(random.randint(1,3))    

        self.act.clicar_elemento(self.xpath_menu['chat']['clique_input_texto_chat'], By.XPATH)

        self.apagar_input(self.xpath_menu['chat']['input_chat'])
        
        try:
            for paragrafo in mensagem_contexto:
                self.act.enviar_texto_intervalado_uma_vez(self.xpath_menu['chat']['input_chat'], paragrafo, By.XPATH, False, random.random() / 6)
                self.act.press_shift_enter(self.xpath_menu['chat']['input_chat'], By.XPATH)

        except Exception as e:
            #self.apagar_input(self.xpath_menu['chat']['input_chat'])
            #self.act.enviar_texto(self.xpath_menu['chat']['input_chat'], mensagem_contexto, By.XPATH)
            pass

        self.act.press_enter(self.xpath_menu['chat']['input_chat'], By.XPATH)
        #self.act.clicar_elemento(self.xpath_menu['chat']['enviar_chat'], By.XPATH)

    def verificar_loading(self, xpath, tipo, interacoes = 300):
        while (self.act.quantidade_elemento(xpath, By.XPATH) == 1):
            print('Aguardando Loading...' + ' ' + tipo + ' ' + str(interacoes))
            sleep(1)
            interacoes -= 1
            if(interacoes < -35):
                self.driver.quit()

    def get_assunto_aleatorio_ia(self, id_assunto):

        switcher = {
            1: "crie uma frase aleatoria motivacional",
            2: "fale uma citacao da biblia",
            3: "cite qualquer cidade do mundo e seu principal ponto turistica",
            4: "cite uma passagem historica da humanidade",
            5: "comente sobre uma receita",
            6: "cite uma tecnologia atual e comente",
            7: "cante um refrao de musica",
            8: "conte sobre um episodio da historia do Brasil",
            9: "cite um mitologia grega e sua historia",
            10: "fale sobre um ator de hollywood e uma curiosidade sobre ele"
        }
 
        return switcher.get(id_assunto, "fale qualquer coisa engraçada")



    def apagar_input(self, xpath):

        self.act.press_ctrl_A(xpath, By.XPATH)
        self.act.press_backspace(xpath, 1, By.XPATH, 0)