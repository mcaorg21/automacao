
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
                "criar" : "/html/body/div[1]/div/div/div[2]/div[3]/header/header/div/span/div/span/div[1]/div/span",
                "pesquisar" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/button",
                "input_pesquisa" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p",
                "telefone_encontrado" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[2]/div/div/span",
                "loading_pesquisa" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/span/div/span/svg/circle",
                "clique_telefone_resultado" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[2]/div/div/span",
                "clique_input_texto_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p",
                "input_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p",
                "enviar_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span",
                "mensagem_nao_Lida" : "/html/body/div[1]/div/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div[2]/div[2]/div[2]/span[1]/div/span",
                "filtro" : "/html/body/div[1]/div/div/div[2]/div[3]/div/div[1]/div/button/div",
                "filtro_mensagem_nao_lida": "/html/body/div[1]/div/div/span[5]/div/ul/div/li[1]/div/div[1]",
                "responder_primeiro_contato" :"/html/body/div[1]/div/div/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div[2]",
                "ultima_mensagem_chat" : "/html/body/div[1]/div/div/div[2]/div[4]/div/div[3]/div/div[2]/div[3]/div[3]"

            },            
            "status": {
                "icone": "/html/body/div[1]/div/div/div[2]/div[3]/header/div[2]/div/span/div[3]/div/span",
                "icone_adicionar": "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/header/div/span/div/span/div[1]/div/span",
                "adicionar_texto": "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/header/div/span/div/span/div[1]/span/div/ul/li[2]/div",
                "input_status" : "/html/body/div[1]/div/div/span[3]/div/div/div[2]/div/div[1]",
                "enviar_status": "/html/body/div[1]/div/div/span[3]/div/div/div[3]/div/div[2]/div/div"
            },
            "canais": {
                "icone": "/html/body/div[1]/div/div/div[2]/div[3]/header/div[2]/div/span/div[4]/div/span",
                "icone_mais": "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/header/div/div[3]/div/div/span",
                "icone_encontrar_canais": "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/header/div/div[3]/div/span/div/ul/li[2]/div",
                "concordar_continuar": "/html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[2]/div/button[2]/div/div",
                "input_pesquisa" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/span/div/div/div[1]/div/div/div/div[2]/div[1]/p",
                "seguir": f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/span/div/div/div[2]/div/div/div/div[{random.randint(1,5)}]/div/div/div/div/div[3]/button",
                "cancelar_seguir": "/html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[2]/div/button[1]/div/div",
                "botao_encontrar_mais": "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/span/div/div/header/div/div[1]/div",
                "voltar" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/span/div/div/header/div/div[1]/div/span",
                "ler_canal" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/div/div[2]/div[1]/div/div",
                "voltar_principal" : "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/span/div/span/div/div/header/div/div[1]/div/span"
            },            
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

        if(self.verifica_mensagem_nao_lida() == True):
            print('Respondendo mensagem...')
            self.responder_mensagem()

        print('Atuando...') 
        self.iniciar_conversa(random.randint(2,5))
        sleep(random.randint(1,3)) 

        #self.postar_status()
        self.participar_comunidade()
        

    def iniciar_conversa(self, limite_envios = 2):

        

        for i in range(1, limite_envios):
            print(f"---------- Mensagem {i} de {limite_envios-1} ----------")
            #pegar lista pre definida em csv
            telefone = ['31993448917','31993448824']

            telefone = telefone[random.randint(0,len(telefone) -1)]

            #self.act.clicar_elemento(self.xpath_menu['chat']['icone'], By.XPATH)    

            self.act.clicar_elemento(self.xpath_menu['chat']['criar'], By.XPATH)
            self.act.clicar_elemento(self.xpath_menu['chat']['pesquisar'], By.XPATH)
            self.act.enviar_texto(self.xpath_menu['chat']['input_pesquisa'], telefone, By.XPATH)

            self.verificar_loading(self.xpath_menu['chat']['telefone_encontrado'], "Pesquisa Telefone", 0)
            
            if(self.act.quantidade_elemento(self.xpath_menu['chat']['telefone_encontrado'], By.XPATH) >= 1):
                telefone_encontrado = self.act.obter_atributo(self.xpath_menu['chat']['telefone_encontrado'], 'title', By.XPATH).replace(" ","")

                if(similaridade(telefone_encontrado,telefone) > 70):
                    print('VVVVVVVVVVVVVVVVVVVVV TELEFONE ENCONTRADO VVVVVVVVVVVVVVVVVVVVV')
                    self.act.clicar_elemento(self.xpath_menu['chat']['clique_telefone_resultado'], By.XPATH)
                    sleep(random.randint(2,5))

                    print("Enviando mensagem...")
                    random_mensagem = self.get_assunto_aleatorio_ia(random.randint(1,12))

                    self.enviar_mensagem(True, random_mensagem)

                    sleep(random.randint(1,3))

                else:
                    print('XXXXXXXXXXXXXXXXXX TELEFONE NÃO ENCONTRADO XXXXXXXXXXXXXXXXXX')
                    continue

            sleep(random.randint(9,60))

        sleep(random.randint(2,5))

    def postar_status(self):
        print("---------- POSTANDO STATUS ----------")

        self.act.clicar_elemento(self.xpath_menu['status']['icone'], By.XPATH)
        self.act.clicar_elemento(self.xpath_menu['status']['icone_adicionar'], By.XPATH)
        self.act.clicar_elemento(self.xpath_menu['status']['adicionar_texto'], By.XPATH)
        self.apagar_input(self.xpath_menu['status']['input_status'])

        texto_status = "escreva uma mensagem aleatoria ou engracada para o status do whatsapp sem formatacao"
        mensagem_status = self.define_mensagem_ia(texto_status, 25, False)

        self.act.enviar_texto(self.xpath_menu['status']['input_status'], mensagem_status, By.XPATH)
        self.act.clicar_elemento(self.xpath_menu['status']['enviar_status'], By.XPATH)

    def participar_comunidade(self):
        print("---------- ENTRANDO EM COMUNIDADES  ----------")

        self.act.clicar_elemento(self.xpath_menu['canais']['icone'], By.XPATH)
        self.verificar_loading(self.xpath_menu['canais']['icone_mais'], 0, "Aguardando Canais")

        self.act.clicar_elemento(self.xpath_menu['canais']['icone_mais'], By.XPATH)
        self.act.clicar_elemento(self.xpath_menu['canais']['icone_encontrar_canais'], By.XPATH)
        try:
            self.act.clicar_elemento(self.xpath_menu['canais']['concordar_continuar'], By.XPATH)
        except:
            pass

        assunto = self.define_mensagem_ia("escolha um assunto de canal de comunidades com 1 palavra", 10, False)

        self.apagar_input(self.xpath_menu['canais']['input_pesquisa'])
        self.act.enviar_texto_intervalado_uma_vez(self.xpath_menu['canais']['input_pesquisa'], assunto, By.XPATH)

        try:
            self.act.clicar_elemento(self.xpath_menu['canais']['seguir'], By.XPATH)
        except:
            pass

        try:
            self.act.clicar_elemento(self.xpath_menu['canais']['cancelar_seguir'], By.XPATH)
        except:
            pass

        self.apagar_input(self.xpath_menu['canais']['input_pesquisa'])
        self.act.clicar_elemento(self.xpath_menu['canais']['voltar'], By.XPATH)

        try:
            self.act.clicar_elemento(self.xpath_menu['canais']['ler_canal']+f'[{random.randint(1,30)}]', By.XPATH)
            sleep(random.randint(5,9))
        except:
            pass

        self.act.clicar_elemento(self.xpath_menu['canais']['voltar_principal'], By.XPATH)

        #self.act.clicar_elemento(self.xpath_menu['canais']['botao_encontrar_mais'], By.XPATH)

    def verifica_mensagem_nao_lida(self):
        print("---------- VERFICANDO SE POSSUI MENSAGEM NAO LIDA  ----------")
        try:
            self.act.clicar_elemento(self.xpath_menu['chat']['filtro'], By.XPATH)
            self.act.clicar_elemento(self.xpath_menu['chat']['filtro_mensagem_nao_lida'], By.XPATH)
            mensagem_nao_lida = self.act.obter_texto(self.xpath_menu['chat']['mensagem_nao_Lida'], By.XPATH)
            return True
        except:
            return False

    def responder_mensagem(self):
        print("---------- RESPONDENDO  ----------")
        self.act.clicar_elemento(self.xpath_menu['chat']['responder_primeiro_contato'], By.XPATH)

        self.verificar_loading(self.xpath_menu['chat']['clique_input_texto_chat'], 0)
        self.apagar_input(self.xpath_menu['chat']['input_chat'])
        self.act.clicar_elemento(self.xpath_menu['chat']['input_chat'], By.XPATH)
        #ultima_mensagem = self.act.obter_texto('/html/body/div[1]/div/div/div[2]/div[4]/div/div[3]/div/div[2]/div[3]', By.XPATH).split('\n')[-2]
        self.enviar_mensagem(False, ["🚨 Nosso whatsapp de atendimento é o 1150392812, conforme informamos no contato ai em cima!"])
      
    def enviar_mensagem(self, ia = False, mensagem_contexto = "oi tudo bem?"):

        if(ia == True):
            mensagem_contexto = self.define_mensagem_ia(mensagem_contexto, random.randint(45,70))

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

    def define_mensagem_ia(self, mensagem_contexto, random_tokens = random.randint(30,60), com_formatacao = True):

        print(f"------------ Enviando mensagem de {random_tokens} tokens sobre {mensagem_contexto} ------------")

        request = self.request_post.post_request_v3("ia-vertex-texto", {
                "key": "f689f1e12a0399fba803cb2365fc362f",
                "texto": mensagem_contexto,
                "tokens": random_tokens
            })
            
        retorno = request.json()

        if(retorno['tipo'] == "alert"):
            print("XXXXXXXXXXXXXX ERRO JSON XXXXXXXXXXXXXX")
            mensagem_contexto =[ "Houve um erro ao buscar a IA mas segue a vida!"]
        else:
            if(com_formatacao == True):
                mensagem_contexto = retorno['resposta'].split("\n")
            else:
                mensagem_contexto = retorno['resposta']
        
        return mensagem_contexto

    def verificar_loading(self, xpath, _existente = 1, tipo = "", interacoes = 300):
        while (self.act.quantidade_elemento(xpath, By.XPATH) == _existente):
            print('Aguardando Loading...' + ' ' + tipo + ' ' + str(interacoes))
            sleep(1)
            interacoes -= 1
            if(interacoes < -35):
                self.driver.quit()

    def get_assunto_aleatorio_ia(self, id_assunto):

        switcher = {
            1: "crie uma frase aleatoria motivacional",
            2: "fale uma citacao da biblia",
            3: "cite dicas de saude e bem estar",
            4: "cite uma passagem historica da humanidade",
            5: "cite uma comida e comente",
            6: "cite uma tecnologia atual e comente",
            7: "cante um refrao de musica",
            8: "conte um episodio da segunda guerra mundial",
            9: "cite um mitologia grega e sua historia",
            10: "fale sobre um ator de hollywood e uma curiosidade sobre ele",
            11: "fale sobre curiosidades matematicas"
        }
 
        return switcher.get(id_assunto, "fale qualquer coisa engraçada")

    def get_assunto_aleatorio_canais(self, id_assunto):

        switcher = {
            1: "crie uma frase aleatoria motivacional",
            2: "fale uma citacao da biblia",
            3: "cite dicas de saude e bem estar",
            4: "cite uma passagem historica da humanidade",
            5: "cite uma comida e comente",
            6: "cite uma tecnologia atual e comente",
            7: "cante um refrao de musica",
            8: "conte um episodio da segunda guerra mundial",
            9: "cite um mitologia grega e sua historia",
            10: "fale sobre um ator de hollywood e uma curiosidade sobre ele"
        }
 
        return switcher.get(id_assunto, "fale qualquer coisa engraçada")

    def apagar_input(self, xpath):

        self.act.press_ctrl_A(xpath, By.XPATH)
        self.act.press_backspace(xpath, 1, By.XPATH, 0)