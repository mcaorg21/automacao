import pdb, sys, json, base64, pickle, ssl, smtplib

from os import walk
from datetime import datetime
sys.path.append('../../')
#sys.path.append('../')
from sites.baseRobos.core.helpers import definir_nome_robo,enviar_email_gmail_uconecte
from sites.baseRobos.core.helpers import formatar_moeda, convert_file_base_64, deleta_todos_arquivos
from dados.APIDataSource import APIDataSource
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.safra.sincroniza_aprova_cookies import Consulta_Safra_Sinc
from time import sleep
from requests.exceptions import ConnectionError  
from dados.database.queries.query_dados_robos import query_login_pass_robo

HORARIO_COMERCIAL = 8, 22
counter_login = 0
class Consulta_Safra():

    def __init__(self):
        # self.login = {'usuario': "CBSU148834", 'senha': 'Marcelo_909'}
        # self.agente = '07823888688'

        self.path = '/home/gustavo/Desktop/automacao-python/sites/safra/pdfs/'
        self.path_cookies = '/home/gustavo/Desktop/automacao-python/sites/safra/'
        # desnecessaro para nao ficar logando -> open(self.path_cookies+'cookies_insercao.pkl', 'w').close()

        #self.path = 'C:\\wamp64\\www\\automacao-python\\sites\\safra\\pdfs\\'
        #self.path_cookies = 'C:\\wamp64\\www\\automacao-python\\sites\\safra\\'
        # desnecessaro para nao ficar logando -> open(self.path_cookies+'cookies_insercao.pkl', 'w').close()

        self.chrome_options = ChromeOptions()
        prefs = {'download.default_directory' : self.path}
        self.chrome_options.add_experimental_option('prefs', prefs)
        #chrome_options.add_argument("--headless")
        self.driver = Chrome(chrome_options=self.chrome_options)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(973, 900)

        #self.tabela = 'FGTS-NOVO-2,04-1 A 3 ANOS-SUB'
        self.tabela = 'FGTS-NOVO-1,89-1 A 5 SAQUES-SUB'




    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self, url_get=None, title = "Safra - Insercao - A inserir" ): 
        definir_nome_robo(title)   

        if(url_get):
            self.usuario = "CBSU145355"
            self.id_robo = "2"
            nome_usuario = "Saulo"
            self.agente = '06445557694'
            self.nome_cookies = "cookies_insercao_pendente.pkl"
        else:
            self.usuario = "CBSU145337"
            self.id_robo = "1"
            nome_usuario = "Carolina"            
            self.agente = '03507179660'
            self.nome_cookies = "cookies_insercao.pkl" 

            #para testes
            # self.login = {'usuario': "CBS144673", 'senha': '@48Marcelo', 'nome_usuario' : 'Marcelo'}
            # self.agente = '06050694680' 
            # self.nome_cookies = "cookies_insercao.pkl"

        dados_login = query_login_pass_robo(self.id_robo, self.usuario)
        
        self.login = {'usuario': self.usuario, 'senha': dados_login['senha'], 'nome_usuario' : nome_usuario}

        self.driver.get('https://epfweb.safra.com.br/PainelControle')

        try:
            cookies = pickle.load(open(self.path_cookies+self.nome_cookies, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
                sleep(1)
        except:
            print("Unexpected error:", sys.exc_info()[0])       
            pass

        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        
        self.act = SeleniumActions(self.driver)

        logou = False
        try:
            self.act.enviar_texto('//*[@id="txtUsuario"]', self.login['usuario'], By.XPATH)            
        except:
            logou = True

        if not logou: 
            self.driver.delete_all_cookies()
            open(self.path_cookies+self.nome_cookies, 'w').close()
            sleep(2)
            print('Logando...')
            self.act.enviar_texto('//*[@id="txtSenha"]', self.login['senha'], By.XPATH)
            print('Terminando de fazer login...')
            sleep(2)
            self.act.hover_e_clique('//*[@id="btnEntrar"]', By.XPATH)
            sleep(45)
            try:
                self.act.hover_e_clique('//*[@id="btnEntrar"]', By.XPATH)
            except:
                pass
            print('Enviando mensagem...')
            msg = "Subject: ######Login realizado -> Robo Safra Insercao#### \n\n Login realizado -" + self.login['nome_usuario'] + " - " + self.login['usuario']
            #enviar_email_gmail_uconecte("notifica4@uconecte.me", "mcaorg@gmail.com", msg)
            payload = {"telefoneDDD": '31993448917',"mensagem": msg,"key": "f9223937d6a342a75fa449a2e5bbd75b"}
            response = APIDataSource().post_request_v2('enviar-mensagem-whatsapp', payload)
            sleep(30)
        
        self.verificar_loading()

        # mudar para painel de controle
        if not logou:
            with open(self.path_cookies+self.nome_cookies, "wb") as file:
                pickle.dump(self.driver.get_cookies(), file)
                sleep(1)

        self.driver.get('https://epfweb.safra.com.br/PainelControle')

        global counter_login
        try:
            self.act.obter_texto('//*[@id="tblLogin"]/tbody/tr/td/div/label[1]', By.XPATH)
            counter_login += 1
            print('Tentativa de LOGIN: ' + str(counter_login))
            if counter_login == 2:
                msg = "Subject: ######Problema -> Robo Safra Insercao#### \n\nTerceira tentativa de no login (" + self.login['usuario'] + ") feita no insercao. Para corrigir o problema delete os cookies."
                enviar_email_gmail_uconecte("notifica4@uconecte.me", "mcaorg@gmail.com", msg)
                print('XXXXXXXXXXXXXXXXXXXX ERRO NO LOGIN AGUARDANDO 30 MINUTOS XXXXXXXXXXXXXXXXXXXX')
                open(self.path_cookies+self.nome_cookies, 'w').close()
                sleep(1800)                
                self.main(url_get,title)
                counter_login = 0
        except:
            counter_login = 0
            pass

        try:
            if url_get:
                self.insercao(url=url_get)
                #Consulta_Safra_Sinc(self.driver).sincronizador()
                #Consulta_Safra_Sinc(self.driver).aprovador()
            else:
                print('Iniciando insercao de novos contratos...')
                self.insercao()
                print('Ajudando pendentes...')
                self.insercao(url_get, tipo_fila = 'ajuda_pendente_contrario')

            #self.driver.quit()
            print('Aguardando 30 segundos....')
            self.driver.refresh() 
            sleep(30)

        except ErroInicialException as e:
            print(e)
            print('XXXXXXXXXXXXXXX ERRO INICIAL XXXXXXXXXXXXXXX')
            self.driver.set_window_size(973, 900)
            #self.driver.quit()
            self.main(url_get,title)
        
        except ConnectionError:
            print('XXXXXXXXXXXXXXX ERRO REQUISICAO XXXXXXXXXXXXXXX')
            #self.driver.quit()
            self.main(url_get,title)
        
        except:
            print("Erro inesperado:", sys.exc_info()[0])
            definir_nome_robo('####ERRO####' + title)
            texto_erro = ''
            try:
                texto_erro = self.act.obter_texto('//*[@id="msgBloqueioFgts"]',By.XPATH)
                if 'Digite uma nova proposta' in texto_erro:
                    print('Aguardando 1 minuto...')
                    sleep(60)
            except:
                print('Aguardando 3 minutos...')
                sleep(180)

            sleep(300)
            self.main(url_get,title)

        # print('Reiniciando...')
        # self.main(url_get,title)
        
    def verificar_loading(self, interacoes=100, aguardar = False):
        sleep(0.3)
        try:
            while (self.act.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
                print('Aguardando Loading...' + str(interacoes))
                sleep(0.3)
                interacoes -= 1
                if(interacoes == 0):
                    print('XXXXXXXXXXXXXXXXXXXX Loading sem solução... XXXXXXXXXXXXXXXXXXXX')
                    break
        except:
            pass     

    def menu_opcoes(self, xpath_clique, texto, use_down_key = False):
        try:
            self.act.clicar_elemento(xpath_clique, By.XPATH)
            xpath_input = xpath_clique[::-1]
            xpath_input = xpath_input.replace('a', '', 1)
            xpath_input = xpath_input[::-1]
            xpath_input += 'div/div/input'
            self.act.enviar_texto(xpath_input, texto, By.XPATH)
            if use_down_key == True:
                self.driver.find_element_by_xpath(xpath_input).send_keys(Keys.DOWN)
            self.act.press_enter(xpath_input, By.XPATH)
        except:
            pass

    def soma_limites(self, limites):

        for i in limites:
            qtd_ponto = 0
            for j in i:
                if j == '.':
                    qtd_ponto += 1
            if qtd_ponto > 1:
                limites[limites.index(i)] = i.replace(".", "", 1)

        return sum([float(i) for i in limites])

    def post_atualiza_valores(self, limites, proposta, datas, msg_error, saques_iniciais):
        print('post atualizando valores')
        # Post
        for i in limites:
            qtd_ponto = 0
            for j in i:
                if j == '.':
                    qtd_ponto += 1
            if qtd_ponto > 1:
                limites[limites.index(i)] = i.replace(".", "", 1)
        
        valores_antecipacao = []
        for k, v in proposta['valoresSaqueAniversario'].items():
            valores_antecipacao.append(float(v))

        if(self.numero_campos_saques == 1):
            
            # if(saques_iniciais == 'nao' or self.ultimos_saques == True):
            #     valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]}}
            # else:
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]}}

        elif(self.numero_campos_saques == 2):

            # if(saques_iniciais == 'nao' or self.ultimos_saques == True):
            #     valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]},
            #                           "saque7": {"valor":limites[1], "data":datas[1]}}
            # else:
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]}}

        elif(self.numero_campos_saques == 3):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]}}

        elif(self.numero_campos_saques == 4):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]}}

        elif(self.numero_campos_saques == 5):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]}}

        elif(self.numero_campos_saques == 6):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]}}

        elif(self.numero_campos_saques == 7):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]}
                                   }

        elif(self.numero_campos_saques == 8):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]}
                                   }

        elif(self.numero_campos_saques == 9):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]},
                                   "saque9": {"valor":limites[8], "data":datas[8]},
                                   }

        elif(self.numero_campos_saques == 10):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]},
                                   "saque9": {"valor":limites[8], "data":datas[8]},
                                   "saque10": {"valor":limites[9], "data":datas[9]},
                                   }

        
        #if(saques_iniciais == 'sim'):
        self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)
        #else:
            #self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', '1,69')

        self.verificar_loading()
        self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)

        self.verificar_loading()
        msg_error = self.pegar_msg_error()
        
        if(msg_error):
            return False


        valor_total_antecipacao = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]', By.XPATH).replace('.', '').replace(',', '.')

        for i in limites:
            limites[limites.index(i)] = float(i)

        if(saques_iniciais == 'nao' or msg_error is None):
            msg_error = 'Atualizando valores'

        payload = {
            "statusPropostaBanco": msg_error,
            "codigoCon": proposta['codigoContrato'],
            "valores_atualizados": json.dumps(valores_atualizados),
            "valor_total": sum(limites),
            "valor_total_antecipacao": float(valor_total_antecipacao),
            "saques_iniciais": saques_iniciais,
            "key": "f689f1e12a0399fba803cb2365fc362f"
        }

        response = APIDataSource().post_request_v2("enviar-dados-safra", payload)
        print("Em post atualizar valores...")
        print(response)
        return True

    def post_insercao_alert(self, limites, proposta, datas, msg_error, saques_iniciais, retirar_mais_centavos = 0):
        print('post insercao alert')
        # Post
        for i in limites:
            qtd_ponto = 0
            for j in i:
                if j == '.':
                    qtd_ponto += 1
            if qtd_ponto > 1:
                limites[limites.index(i)] = i.replace(".", "", 1)
        
        valores_antecipacao = []
        if(isinstance(proposta['valoresSaqueAniversario'], str) == False):        
            for k, v in proposta['valoresSaqueAniversario'].items():
                valores_antecipacao.append(float(v))

        if(self.numero_campos_saques == 1):

            # if(saques_iniciais == 'nao' or self.ultimos_saques == True):
            #     valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]}}
            # else:
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]}}

        elif(self.numero_campos_saques == 2):

            # if(saques_iniciais == 'nao' or self.ultimos_saques == True):
            #     valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]},
            #                           "saque7": {"valor":limites[1], "data":datas[1]}}
            # else:
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]}}

        elif(self.numero_campos_saques == 3):
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]}}

        elif(self.numero_campos_saques == 4):
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]}}

        elif(self.numero_campos_saques == 5):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]}}

        elif(self.numero_campos_saques == 6):

            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]}}

        elif(self.numero_campos_saques == 7):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]}}

        elif(self.numero_campos_saques == 8):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]}
                                   }

        elif(self.numero_campos_saques == 9):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]},
                                   "saque9": {"valor":limites[8], "data":datas[8]},
                                   }

        elif(self.numero_campos_saques == 10):
           
            valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]},
                                   "saque4": {"valor":limites[3], "data":datas[3]},
                                   "saque5": {"valor":limites[4], "data":datas[4]},
                                   "saque6": {"valor":limites[5], "data":datas[5]},
                                   "saque7": {"valor":limites[6], "data":datas[6]},
                                   "saque8": {"valor":limites[7], "data":datas[7]},
                                   "saque9": {"valor":limites[8], "data":datas[8]},
                                   "saque10": {"valor":limites[9], "data":datas[9]},
                                   }
        
        for i in range(0, self.numero_campos_saques):
            self.act.clicar_elemento(f'//*[@id="valFgtsAntecipacao_{i}"]', By.XPATH)
            #if len(limites[i]) < 6 and len(limites[i]) > 4:
            #    limites[i] += '0'
            #self.act.enviar_texto(f'//*[@id="valFgtsAntecipacao_{i}"]', "{:.2f}".format(float(limites[i]), By.XPATH)
            self.act.enviar_texto(f'//*[@id="valFgtsAntecipacao_{i}"]', "{:.2f}".format(float(limites[i])), By.XPATH)

        #if(saques_iniciais == 'sim'):
        self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)
        #else:
        #self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', '1,69')

        self.verificar_loading()
        self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)

        try:
            msg = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
            print(msg)
            
            if msg == 'Ocorreu um erro no processamento dos dados, favor tentar novamente':   
                print('Com o erro de processamento vamos retirar 2 /3 centavos da primeira e 1 centavo de cada parcela...')  

                if(self.numero_campos_saques == 1):
            
                    #if(saques_iniciais == 'nao' or self.ultimos_saques == True):
                    #    valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]}}
                    #else:
                    valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]}}

                elif(self.numero_campos_saques == 2):

                    #if(saques_iniciais == 'nao' or self.ultimos_saques == True):
                    #    valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]},
                    #                            "saque7": {"valor":limites[1], "data":datas[1]}}
                    #else:
                    valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                           "saque2": {"valor":limites[1], "data":datas[1]}}

                elif(self.numero_campos_saques == 3):
                    valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                   "saque2": {"valor":limites[1], "data":datas[1]},
                                   "saque3": {"valor":limites[2], "data":datas[2]}}

                elif(self.numero_campos_saques == 4):
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]}}

                elif(self.numero_campos_saques == 5):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]}}

                elif(self.numero_campos_saques == 6):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.01 - retirar_mais_centavos), "data":datas[5]}}

                elif(self.numero_campos_saques == 7):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.01 - retirar_mais_centavos), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.01 - retirar_mais_centavos), "data":datas[6]}}

                elif(self.numero_campos_saques == 8):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.01 - retirar_mais_centavos), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.01 - retirar_mais_centavos), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.01 - retirar_mais_centavos), "data":datas[7]}
                                   }

                elif(self.numero_campos_saques == 9):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.01 - retirar_mais_centavos), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.01 - retirar_mais_centavos), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.01 - retirar_mais_centavos), "data":datas[7]},
                                   "saque9": {"valor": str(float(limites[8]) - 0.01 - retirar_mais_centavos), "data":datas[8]}
                                   }

                elif(self.numero_campos_saques == 10):           
                    valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.04 - retirar_mais_centavos), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.03 - retirar_mais_centavos), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.03 - retirar_mais_centavos), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.01 - retirar_mais_centavos), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.01 - retirar_mais_centavos), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.01 - retirar_mais_centavos), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.01 - retirar_mais_centavos), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.01 - retirar_mais_centavos), "data":datas[7]},
                                   "saque9": {"valor": str(float(limites[8]) - 0.01 - retirar_mais_centavos), "data":datas[8]},
                                   "saque10": {"valor": str(float(limites[9]) - 0.01 - retirar_mais_centavos), "data":datas[9]},
                                   }
                
                for i in range(0, self.numero_campos_saques):
                    self.act.clicar_elemento(f'//*[@id="valFgtsAntecipacao_{i}"]', By.XPATH)
                    limites[i] = float(limites[i])
                    retirar_centavos = 0.01 + retirar_mais_centavos
                    if(i == 0):
                        retirar_centavos = 0.04 + retirar_mais_centavos
                    if(i == 1 or i == 2):
                        retirar_centavos = 0.03 + retirar_mais_centavos


                    limites[i] = "{:.2f}".format(limites[i] - retirar_centavos)                                       
                    self.act.enviar_texto(f'//*[@id="valFgtsAntecipacao_{i}"]', limites[i], By.XPATH)

                #if(saques_iniciais == 'sim'):
                self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)
                #else:
                #    self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', '1,69')

                self.verificar_loading()
                self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)

        except:
            pass

        self.verificar_loading()

        try:
            valor_total_antecipacao = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]', By.XPATH).replace('.', '').replace(',', '.')
        except:
            
            if('Valor liberado ao cliente deve ser superior a' in msg):
                for i in limites:
                    limites[limites.index(i)] = float(i)

                payload = {
                    "statusPropostaBanco": 'Proposta menor que o valor minimo permitido',
                    "codigoCon": proposta['codigoContrato'],
                    "valores_atualizados": json.dumps(valores_atualizados),
                    "valor_total": sum(limites),
                     "saques_iniciais" : saques_iniciais,
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                
                response = APIDataSource().post_request_v2("enviar-dados-safra", payload)
                raise ErroInicialException('Valor mínimo... Reiniciando processo...')

            elif('Não foi possível encontrar taxas disponíveis' in msg):
                for i in limites:
                    limites[limites.index(i)] = float(i)

                payload = {
                    "statusPropostaBanco": 'Não foi possível encontrar taxas disponíveis',
                    "codigoCon": proposta['codigoContrato'],
                    "valores_atualizados": json.dumps(valores_atualizados),
                    "valor_total": sum(limites),
                     "saques_iniciais" : saques_iniciais,
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                
                response = APIDataSource().post_request_v2("enviar-dados-safra", payload)
                raise ErroInicialException('Não existe taxa... Reiniciando processo...')

            else:
                print('Será retirado mais 1 centavos para passar...')
                return self.post_insercao_alert(limites, proposta, datas, msg_error, saques_iniciais, 0.01)
 
        for i in limites:
            limites[limites.index(i)] = float(i)

        if(saques_iniciais == 'nao' or msg_error is None):
            msg_error = 'Atualizando valores'

        payload = {
            "statusPropostaBanco": msg_error,
            "codigoCon": proposta['codigoContrato'],
            "valores_atualizados": json.dumps(valores_atualizados),
            "valor_total": sum(limites),
            "valor_total_antecipacao": float(valor_total_antecipacao),
            "saques_iniciais" : saques_iniciais,
            "key": "f689f1e12a0399fba803cb2365fc362f"
        }

        response = APIDataSource().post_request_v2("enviar-dados-safra", payload)
        print(response)
        return True

    def inserir_maximo(self, limites, valor_total_pedido):
        
        print('Somando limite total...')
        # Post
        for i in limites:
            qtd_ponto = 0
            for j in str(i):
                if j == '.':
                    qtd_ponto += 1
            if qtd_ponto > 1:
                limites[limites.index(i)] = i.replace(".", "", 1)

        total_disponivel = sum(map(float,limites))
        
        if(total_disponivel < valor_total_pedido):
            return True
        elif(total_disponivel <= 1.2 * valor_total_pedido):
            return True
        elif(valor_total_pedido > 600 and valor_total_pedido < 1000 and total_disponivel < 1700):
            return True
        elif(total_disponivel <= 650):
            return True
        else:
            return False

    def post_insercao_erro_processamento(self, limites, proposta, datas, msg_error, saques_iniciais):
        
        print('post_insercao_erro_processamento')
        # Post
        for i in limites:
            qtd_ponto = 0
            for j in str(i):
                if j == '.':
                    qtd_ponto += 1
            if qtd_ponto > 1:
                limites[limites.index(i)] = i.replace(".", "", 1)

        valor_total_antecipacao = []

        try:
            print('Com o erro de processamento vamos retirar 2 centavos de cada parcela...')

            if(self.numero_campos_saques == 1):

                #if(saques_iniciais == 'nao' or self.ultimos_saques == True):
                #    valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]}}
                #else:
                valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]}}

            elif(self.numero_campos_saques == 2):

                #if(saques_iniciais == 'nao' or self.ultimos_saques == True):
                #    valores_atualizados = {"saque6": {"valor":limites[0], "data":datas[0]},
                #                          "saque7": {"valor":limites[1], "data":datas[1]}}
                #else:
                valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                        "saque2": {"valor":limites[1], "data":datas[1]}}

            elif(self.numero_campos_saques == 3):
                    valores_atualizados = {"saque1": {"valor":limites[0], "data":datas[0]},
                                       "saque2": {"valor":limites[1], "data":datas[1]},
                                       "saque3": {"valor":limites[2], "data":datas[2]}}

            elif(self.numero_campos_saques == 4):
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]}}

            elif(self.numero_campos_saques == 5):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]}}

            elif(self.numero_campos_saques == 6):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.02), "data":datas[5]}}

            elif(self.numero_campos_saques == 7):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.02), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.02), "data":datas[6]}}

            elif(self.numero_campos_saques == 8):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.02), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.02), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.02), "data":datas[7]}
                                   }

            elif(self.numero_campos_saques == 9):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.02), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.02), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.02), "data":datas[7]},
                                   "saque9": {"valor": str(float(limites[8]) - 0.02), "data":datas[8]}}

            elif(self.numero_campos_saques == 10):            
                valores_atualizados = {
                                   "saque1": {"valor": str(float(limites[0]) - 0.02), "data":datas[0]},
                                   "saque2": {"valor": str(float(limites[1]) - 0.02), "data":datas[1]},
                                   "saque3": {"valor": str(float(limites[2]) - 0.02), "data":datas[2]},
                                   "saque4": {"valor": str(float(limites[3]) - 0.02), "data":datas[3]},
                                   "saque5": {"valor": str(float(limites[4]) - 0.02), "data":datas[4]},
                                   "saque6": {"valor": str(float(limites[5]) - 0.02), "data":datas[5]},
                                   "saque7": {"valor": str(float(limites[6]) - 0.02), "data":datas[6]},
                                   "saque8": {"valor": str(float(limites[7]) - 0.02), "data":datas[7]},
                                   "saque9": {"valor": str(float(limites[8]) - 0.02), "data":datas[8]},
                                   "saque10": {"valor": str(float(limites[9]) - 0.02), "data":datas[9]}}

            i = 0
            for saque,valor in proposta['valoresSaqueAniversario'].items():
                valor = float(valor)
                self.act.clicar_elemento(f'//*[@id="valFgtsAntecipacao_{i}"]', By.XPATH)
                if(valor > 0.0):
                    limites[i] = float(limites[i])
                    limites[i] = "{:.2f}".format(limites[i] - 0.02)                                       
                    self.act.enviar_texto(f'//*[@id="valFgtsAntecipacao_{i}"]', limites[i], By.XPATH)
                    if(self.numero_campos_saques == 1):
                        break
                else:
                    self.act.enviar_texto(f'//*[@id="valFgtsAntecipacao_{i}"]', '0,00', By.XPATH)
                
                i += 1

            #if(saques_iniciais == 'sim'):
            self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)
            #else:
                #self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', '1,69')

            self.verificar_loading()
            self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)

            msg_error = self.pegar_msg_error()

            if 'Prazo da operação inferior ao permitido. É necessário que o prazo da operação seja de no mínimo 12 meses.' in msg_error:
                dados_post = {
                    "statusPropostaBanco": 'Somente tem o primeiro saque e não pode ainda realizar por estar ainda abaixo dos 12 meses.',
                    "codigoCon": proposta['codigoContrato'],
                    "ade": ''
                }
                response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                return False

        except:
            pass

        self.verificar_loading()
        
        valor_total_antecipacao = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]', By.XPATH).replace('.', '').replace(',', '.')
        
        for i in limites:
            limites[limites.index(i)] = float(i)

        if(saques_iniciais == 'nao' or msg_error is None):
            msg_error = 'Atualizando valores'

        payload = {
            "statusPropostaBanco": msg_error,
            "codigoCon": proposta['codigoContrato'],
            "valores_atualizados": json.dumps(valores_atualizados),
            "valor_total": sum(limites),
            "valor_total_antecipacao": float(valor_total_antecipacao),
            "saques_iniciais" : saques_iniciais,
            "key": "f689f1e12a0399fba803cb2365fc362f"
        }
        
        response = APIDataSource().post_request_v2("enviar-dados-safra", payload)
        print(response)
        return True

    def pegar_msg_error(self):
        msg_error = None
        try:
            msg_error = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
        except:
            pass
        
        return msg_error

    def verifica_campos_obrigatorios(self, proposta, rec = 0):
        print('Verificando se algum campos deixou de ser preenchido...')

        try:
            mensagem_obrigatorio = self.act.obter_texto('.padraoNaoPreenchido')
        except:
            mensagem_obrigatorio = ''
            pass

        if(mensagem_obrigatorio == ''):
            print('VVVVVVVVVVVVVVV Campos preenchidos, finalizando proposta VVVVVVVVVV')
            return True

        if('orgão empregador' in mensagem_obrigatorio):
            if proposta['produto'] == 'AUXILIO':
                try:
                    self.menu_opcoes('//*[@id="ddlOrgaosEmpregadores_chzn"]/a', 'SUBSECRETARIA A ADM MINISTERIO CIDADANIA') 
                except:
                    pass

        if('Alfabetizado' in mensagem_obrigatorio):
            # Alfabetizado
            if proposta['grauInstrucao'] != 1:
                self.menu_opcoes('//*[@id="ddlAlfabetizacao_chzn"]/a', 'SIM')
            else:
                self.menu_opcoes('//*[@id="ddlAlfabetizacao_chzn"]/a', 'NÃO')
            self.verificar_loading()

        if('Situação do Empregado' in mensagem_obrigatorio or 'situação do empregado' in mensagem_obrigatorio):
            if proposta['produto'] == 'AUXILIO':
                try:
                    self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'ATIVO')  
                except:
                    pass
            else:
                try:
                    self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'ATIVO')  
                except:
                    pass 

        if('Vínculo Empregatício' in mensagem_obrigatorio or 'vínculo empregatício' in mensagem_obrigatorio):
            if proposta['produto'] == 'AUXILIO':
                try:
                    self.menu_opcoes('//*[@id="ddlVinculoEmpregaticio_chzn"]/a', 'TEMPORÁRIO')  
                except:
                    pass
            else:
                try:
                    self.menu_opcoes('//*[@id="ddlRegimesJuridico_chzn"]/a', 'CLT')
                    self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'ATIVO')
                    self.menu_opcoes('//*[@id="ddlVinculoEmpregaticio_chzn"]/a', 'EFETIVO')     
                except:
                    pass       
                    
        elif('profissão' in mensagem_obrigatorio):
            if proposta['produto'] == 'AUXILIO':
                try:
                    self.menu_opcoes('//*[@id="ddlProfissao_chzn"]/a', 'AUXILIO BRASIL')  
                except:
                    pass
            else:
                try:
                    self.menu_opcoes('//*[@id="ddlProfissao_chzn"]/a', 'ANALISTA')
                except:
                    pass 
                    
        elif('cargo' in mensagem_obrigatorio):
            if proposta['produto'] == 'AUXILIO':
                try:
                    self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'AUXILIO BRASIL')  
                except:
                    pass
            else:
                try:
                    self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'ANALISTA DE OPERACOES COMERCIAIS')
                except:
                    pass 

        elif('contatos' in mensagem_obrigatorio):
            try:
                self.act.hover_e_clique('//*[@id="gview_ContatoGrid"]/div[3]',By.XPATH)
                self.act.hover_e_clique('//*[@id="jqg1"]/td[2]',By.XPATH)
                self.act.enviar_texto_intervalado('//*[@id="jqg1_Telefone"]', ' ' + proposta['celular'], By.XPATH)
            except:
                pass 

        elif('uf rg' in mensagem_obrigatorio):
            try:
                if(proposta['identidade']['uf'] == 'SE'):
                    self.act.hover_e_clique('//*[@id="ddlUFRG_chzn"]',By.XPATH)
                    self.verificar_loading()
                    self.act.hover_e_clique('//*[@id="ddlUFRG_chzn"]',By.XPATH)
                    self.verificar_loading()
                    self.act.enviar_texto('//*[@id="ddlUFRG_chzn"]/div/div/input', proposta['identidade']['uf'], By.XPATH)
                    self.verificar_loading()
                    self.driver.find_element_by_xpath('//*[@id="ddlUFRG_chzn"]/div/div/input').send_keys(Keys.DOWN)
                    self.verificar_loading()
                    self.driver.find_element_by_xpath('//*[@id="ddlUFRG_chzn"]/div/div/input').send_keys(Keys.ENTER)
                else:
                    self.menu_opcoes('//*[@id="ddlUFRG_chzn"]/a', proposta['identidade']['uf'])
            except:
                pass 

        elif('cep' in mensagem_obrigatorio):
            try:
                self.act.enviar_texto('//*[@id="txtCep"]', '01153000', By.XPATH)
                self.act.enviar_texto('//*[@id="txtNumero"]', proposta['endereco']['numero'], By.XPATH)
                self.act.enviar_texto('//*[@id="txtComplemento"]', proposta['endereco']['logradouro'] + proposta['endereco']['numero'] + proposta['endereco']['bairro'] + proposta['endereco']['complemento'], By.XPATH)        
                self.menu_opcoes('//*[@id="ddlUF_chzn"]/a', proposta['endereco']['uf'])
                print('erro de cep')
                self.act.clicar_elemento('//*[@id="btnConsultarEndereco"]', By.XPATH)
                self.act.enviar_texto('//*[@id="txtCep"]', proposta['endereco']['cep'], By.XPATH)
            except:
                pass

        elif('nro' in mensagem_obrigatorio):
            try:
                self.act.enviar_texto('//*[@id="txtNumero"]', '10', By.XPATH)
            except:
                pass

        elif('uf' in mensagem_obrigatorio):
            try:
                if(proposta['endereco']['uf'] == 'SE'):
                    self.act.hover_e_clique('//*[@id="ddlUF_chzn"]',By.XPATH)
                    self.verificar_loading()
                    self.act.hover_e_clique('//*[@id="ddlUF_chzn"]',By.XPATH)
                    self.verificar_loading()
                    self.act.enviar_texto('//*[@id="ddlUF_chzn"]/div/div/input', proposta['identidade']['uf'], By.XPATH)
                    self.verificar_loading()
                    self.driver.find_element_by_xpath('//*[@id="ddlUF_chzn"]/div/div/input').send_keys(Keys.DOWN)
                    self.verificar_loading()
                    self.driver.find_element_by_xpath('//*[@id="ddlUF_chzn"]/div/div/input').send_keys(Keys.ENTER)

                else:
                    self.menu_opcoes('//*[@id="ddlUF_chzn"]/a', proposta['endereco']['uf'])
            except:
                pass

        elif('logradouro' in mensagem_obrigatorio):
            try:
                self.act.clicar_elemento('//*[@id="txtLogradouro"]', By.XPATH)
                self.act.enviar_texto('//*[@id="txtLogradouro"]', proposta['endereco']['logradouro'], By.XPATH)
                self.act.enviar_texto('//*[@id="txtNumero"]', proposta['endereco']['numero'], By.XPATH)
                self.act.enviar_texto('//*[@id="txtComplemento"]', proposta['endereco']['complemento'], By.XPATH)
                self.act.enviar_texto('//*[@id="txtBairro"]', proposta['endereco']['bairro'], By.XPATH) 
                self.act.enviar_texto('//*[@id="txtCidade"]', proposta['endereco']['cidade'], By.XPATH)            
                self.menu_opcoes('//*[@id="ddlUF_chzn"]/a', proposta['endereco']['uf'])
            except:
                pass

        elif('agência' in mensagem_obrigatorio):
            try:
                self.menu_opcoes('//*[@id="ddlBanco_chzn"]/a', proposta['banco']['numeroBanco'])
                self.verificar_loading()
                self.act.enviar_texto_intervalado ('//*[@id="txtAgencia"]', proposta['banco']['agencia'], By.XPATH)
                self.verificar_loading()
                self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.DOWN)
                self.verificar_loading()
                self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.ENTER)
            except:
                pass

        elif('nome cônjuge' in mensagem_obrigatorio):
            try:
                self.act.enviar_texto('//*[@id="txtNomeConjuge"]', proposta['outrosDadosPessoais']['conjuge'], By.XPATH)
            except:
                pass 

        elif('referências do cliente' in mensagem_obrigatorio):
            try:
                self.act.enviar_texto('//*[@id="txtNomeRef"]', proposta['referenciaPessoal']['nome'], By.XPATH)
                self.verificar_loading()
                self.menu_opcoes('//*[@id="ddlAfinidade_chzn"]/a', proposta['referenciaPessoal']['afinidade'].upper())
                self.verificar_loading()            
                # Telefone
                self.act.enviar_texto('//*[@id="txtDigitoTel"]', proposta['referenciaPessoal']['telefone'][0:4], By.XPATH)
                self.verificar_loading()

                if(len(proposta['referenciaPessoal']['telefone'][5:]) < 8):
                    self.act.enviar_texto('//*[@id="txtTelefoneRef"]',  proposta['referenciaPessoal']['telefone'][4:], By.XPATH)
                else:
                    self.act.enviar_texto('//*[@id="txtTelefoneRef"]',  proposta['referenciaPessoal']['telefone'][5:], By.XPATH)
                self.verificar_loading()

                self.menu_opcoes('//*[@id="ddlAfinidade_chzn"]/a', proposta['referenciaPessoal']['afinidade'].upper())
                self.verificar_loading()

                self.act.clicar_elemento('//*[@id="btnAdicionarRef"]', By.XPATH)
                self.verificar_loading()
            except:
                pass               

        else:
            print('Tratar mensagem obrigatoria...')
            #pdb.set_trace()

        self.act.clicar_elemento('//*[@id="btnValidarProposta"]', By.XPATH)
        sleep(1)

        rec += 1

        if(rec == 15):
            print('Nova tratativa de campos obrigatórios não consegue ser tratada...')
            pdb.set_trace()

        self.verifica_campos_obrigatorios(proposta, rec)

    def escolher_ano_saque(self, ano):
        if(ano == '1º ao 7º'):
            ano = '1º'
        else:
            ano = '6º'

        self.act.clicar_elemento('//*[@id="ddlTipoProdutoFGTS_chzn"]/a',By.XPATH)
        self.act.enviar_texto('//*[@id="ddlTipoProdutoFGTS_chzn"]/div/div/input',ano,By.XPATH)
        self.act.press_enter('//*[@id="ddlTipoProdutoFGTS_chzn"]/div/div/input', By.XPATH)

    def insercao_inicial(self, proposta, anos_saque = '1º ao 7º'):
        try:      
            self.verificar_loading()
            ''' Inicio Simulacao '''
            # Convênio
            if proposta['produto'] == 'INSS':
                self.menu_opcoes('//*[@id="ddlConvenio_chzn"]/a', 'INSS')
            elif proposta['produto'] == 'AUXILIO':
                self.menu_opcoes('//*[@id="ddlConvenio_chzn"]/a', 'AUXILIO BRASIL')
            else:
                self.menu_opcoes('//*[@id="ddlConvenio_chzn"]/a', 'FGTS')
            # Produto
            self.verificar_loading()            
            self.menu_opcoes('//*[@id="ddlProduto_chzn"]/a', 'NOVO')

            # CPF
            self.act.enviar_texto('//*[@id="txtCPF"]', proposta['cpf'], By.XPATH)
            self.verificar_loading()

            #clica botao de busca cpf
            self.act.clicar_elemento('//*[@id="btnConsultarCPF"]', By.XPATH)
            self.verificar_loading()

            self.act.clicar_elemento('//*[@id="txtNome"]', By.XPATH)
            self.verificar_loading()
            # Nome
            self.act.enviar_texto('//*[@id="txtNome"]', proposta['nome'], By.XPATH)
            self.verificar_loading()

            # TIpo
            if proposta['produto'] == 'INSS':
                self.menu_opcoes('//*[@id="ddlTipoFormalizacao_chzn"]/a', 'DIGITAL WHATSAPP 2.0')
            elif(proposta['produto'] == 'AUXILIO'):
                self.menu_opcoes('//*[@id="ddlTipoFormalizacao_chzn"]/a', 'DIGITAL WEB 2.0 - AUX BRASIL')    
            else:
                #escolhe do 1 ao 7 ano
                self.escolher_ano_saque(anos_saque)
                self.menu_opcoes('//*[@id="ddlTipoFormalizacao_chzn"]/a', 'DIGITAL FGTS')
                self.menu_opcoes('//*[@id="ddlTipoFormalizacao_chzn"]/a', 'DIGITAL FGTS')

            self.verificar_loading()

            self.act.enviar_texto('//*[@id="txtDddWhatsAppDP"]', proposta['dddCelular'], By.XPATH)
            self.verificar_loading()

            self.act.clicar_elemento('//*[@id="fstDadosPessoais"]/div/p[3]/label', By.XPATH)
            self.verificar_loading()

            self.act.enviar_texto('//*[@id="txtTelWhatsAppDP"]', proposta['celular'], By.XPATH)
            self.verificar_loading()

            # UF
            if(proposta['produto'] == 'AUXILIO'):            
                self.menu_opcoes('//*[@id="ddlUFsCliente_chzn"]/a', proposta['endereco']['uf'], True)
                self.verificar_loading()
                self.act.enviar_texto('//*[@id="txtMatricula"]', proposta['matricula'], By.XPATH)
                self.verificar_loading()

            # <<< PROSSEGUIR >>>
            try:
                self.act.clicar_elemento('//*[@id="btnProsseguirSimulador"]', By.XPATH)
            except:
                self.act.enviar_texto('//*[@id="txtNome"]', proposta['nome'], By.XPATH)
                self.act.clicar_elemento('//*[@id="txtTelWhatsAppDP"]', By.XPATH)
                self.verificar_loading()

                self.act.clicar_elemento('//*[@id="fstDadosPessoais"]/div/p[5]', By.XPATH)
                self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)

            self.verificar_loading()

            msg_error = None

            try:
                msg_error = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
            except:
                pass

            if msg_error == "Preencha todos os campos obrigatórios":
                # Nome
                self.act.enviar_texto('//*[@id="txtNome"]', proposta['nome'], By.XPATH)
                self.act.enviar_texto('//*[@id="txtNome"]', proposta['nome'], By.XPATH)
                self.menu_opcoes('//*[@id="ddlUFsCliente_chzn"]/a', proposta['endereco']['uf'],True)
                self.act.clicar_elemento('//*[@id="btnProsseguirSimulador"]', By.XPATH)
                try:
                    msg_error = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
                except:
                    pass

            return msg_error

        except:
            try:
                msg_error = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
            except:
                pass
            
            if(msg_error):
                print('XXXXXXXXXXXXXXXXXXXXXX Erro na insercao...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                dados_post = {"statusPropostaBanco": msg_error ,"codigoCon": proposta['codigoContrato'], "ade": ''}
                response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                return msg_error

            raise ErroInicialException('Erro na pesquisa inicial... Reiniciando processo...' + msg_error)

    def preparar_insercao(self):
        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        self.act.clicar_elemento('//*[@id="PainelControle_novaProposta"]', By.XPATH)
        '''ORIGIN DA PROPOSTA'''
        # agente
        self.act.enviar_texto_intervalado('//*[@id="txtAgenteCertificado"]', self.agente, By.XPATH)
        self.verificar_loading()
        self.driver.find_element_by_xpath('//*[@id="txtAgenteCertificado"]').send_keys(Keys.DOWN)
        self.verificar_loading()
        self.act.press_enter('//*[@id="txtAgenteCertificado"]', By.XPATH)
        self.verificar_loading()
        self.act.clicar_elemento('//*[@id="btnProsseguir"]', By.XPATH)

    def verifica_insercao(self, proposta):   

        principal = proposta['valorPrincipal']   
        inserida = False
        
        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
        self.act.enviar_texto('//*[@id="PainelControle_cpf"]', proposta['cpf'], By.XPATH)
        self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]/span', By.XPATH)
        self.verificar_loading()

        #nova tratativa para pegar ade de contratos com muitas insercoes  
        indice = 0     
        try:
            quantidade_propostas = self.act.quantidade_elemento('.btnMenuContext')
        except:
            print('Nada inserido... Continuando insercao')
            return False 

        if(quantidade_propostas == 1):
            texto_status1 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[2]', By.XPATH)
            texto_status2 = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[5]/span', By.XPATH)
            if texto_status1 == '' and  texto_status2 == 'Em Análise': 
                if str(proposta['valorPrincipal']) != self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[13]',By.XPATH).replace('.','').replace(',','.'):
                    dados_post = { "statusPropostaBanco": "Verificar duplicidade de proposta", "codigoCon": proposta['codigoContrato']}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    return True
                else:
                    indice = 2
                    ade = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]/a', By.XPATH)

        else: 
            for i in range(0, quantidade_propostas):
                texto_status1 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[2]', By.XPATH)
                texto_status2 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[5]', By.XPATH)
                if texto_status1 == '' and texto_status2 == 'Em Análise': 
                    if(str(proposta['valorPrincipal']) == self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[13]',By.XPATH).replace('.','').replace(',','.')):
                        ade = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[6]/a', By.XPATH)
                        indice = i + 2
                        inserida = True
                        break
                    else:
                        inserida = False
                else:
                    inserida = False


        if not inserida:
            return False

        self.act.clicar_elemento(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{indice}]/td[1]/a', By.XPATH)

        url_bruta = None
        d_textos = {}
        d_textos = ''

        self.verificar_loading()

        # BASE64 
        self.act.clicar_elemento('/html/body/ul/li[4]', By.XPATH)
        sleep(10)

        try:
            f = []
            for (dirpath, dirnames, filenames) in walk(self.path):
                f.extend(filenames)
                break
            pdf_base64 = convert_file_base_64(self.path + f[0])
            deleta_todos_arquivos(self.path)
            pdf_base64 = pdf_base64.decode('utf-8')            
        except:
            self.act.obter_texto('//*[@id="divSiteIndisponivel"]/span', By.XPATH)
            pdf_base64 = None
            self.verificar_loading()
            self.act.clicar_elemento('//*[@id="divSiteIndisponivel"]/span/a', By.XPATH)            

        payload = {
                    "codigoCliente": proposta['codigoCliente'],
                    "codigoContrato": proposta['codigoContrato'],
                    "ade": ade,
                    "base64": pdf_base64,
                    "linkAssinaturaDigital": url_bruta,
                    "banco":"safra-fgts",
                    "valorCon": principal,
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                
        response = APIDataSource().post_request_v2('enviar-dados-safra-insercao', payload)
        print(response.text)

        return True
   
    def insercao(self, url=None, tipo_fila = ''):

        inserir_auxilio = False

        if url:
            response = APIDataSource().get_request('dados-insercao2-safra').text
            dados = json.loads(response)
            tamanho_fila = len(dados['contratos'])

            if(tamanho_fila == 0):
                response = APIDataSource().get_request('dados-insercao-safra').text
                dados = json.loads(response)
                tamanho_fila = len(dados['contratos'])
                if(tamanho_fila < 10):
                    print('Não irá ajudar na fila de A Inserir pois tem menos de 10...')
                    return
                else:
                    response = APIDataSource().get_request('dados-insercao-ajuda-a-inserir-safra').text
                    dados = json.loads(response)
                    print('VVVVVVVVVVVVVV Ajudando na fila A Inserir VVVVVVVVVVVVVVVVVVVV')
                
            
        else:

            if(tipo_fila == 'ajuda_pendente_contrario'):
                response = APIDataSource().get_request('dados-insercao3-safra').text
                dados = json.loads(response)
                tamanho_fila = len(dados['contratos'])
                if(tamanho_fila < 10):
                    print('Não irá ajudar na fila de pendentes pois tem menos de 10...')
                    return
            else:
                response = APIDataSource().get_request('dados-insercao-safra').text
                dados = json.loads(response)
                tamanho_fila = len(dados['contratos'])

                ##################
                #tamanho_fila = 0
                ##################

                if(tamanho_fila == 0):
                    inserir_auxilio = True
                    print('VVVVVVVVVVVVVV Iniciando a fila A Inserir Auxílio VVVVVVVVVVVVVVVVVVVV')
                    response = APIDataSource().get_request('dados-insercao-safra-auxilio').text
                    dados = json.loads(response)

        for i in dados['contratos']:
            try:
                response = APIDataSource().get_request('dados-proposta-insercao-safra', edit=['codigo_con', i['codigo_con']]).text
                proposta = json.loads(response)
                proposta = proposta['contrato']  

                verifica_insercao = self.verifica_insercao(proposta)   
                if verifica_insercao == True:
                    print('Proposta já inserida...Pulando.')
                    continue     
                self.preparar_insercao()
            except:
                raise ErroInicialException('Erro na pesquisa inicial... Reiniciando processo...')
            
            if(proposta['produto'] == 'AUXILIO'):
                inserir_auxilio = True
                print('XXXXXXXXXXXXXXXXXXXXXXAuxilio vai inserir assim que voltar...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                dados_post = {"statusPropostaBanco": 'Auxilio temporariamente nao permitido',"codigoCon": proposta['codigoContrato'],"ade": ''}
                response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                continue

            if(inserir_auxilio == False):
                self.ultimos_saques = proposta['ultimos_saques']

                #if(self.ultimos_saques == True):
                    #self.insercao_inicial(proposta, '6º ao 7º')
                    #saques_iniciais = 'nao'
                #else:
                self.insercao_inicial(proposta, '1º ao 7º')
                saques_iniciais = 'sim'
            elif(inserir_auxilio == True):
                self.insercao_inicial(proposta)
                simulou = True

            msg_error = ''
            try:
                self.verificar_loading()
                msg_error = self.act.obter_texto('//*[@id="toast-container"]/div/div', By.XPATH)
            except:
                pass

            if msg_error != None and msg_error != '':
                if msg_error == 'Por favor, informe um agente certificado válido.':
                    continue

            #DESABILITADO
            # if('Não foi possível encontrar saldos disponíveis.' in msg_error):
            #     saques_iniciais = 'nao'
            #     print('-------------- Tentando do 6º ao 7º saque... ----------------')
            #     self.preparar_insercao()
            #     msg_error = self.insercao_inicial(proposta, '6º ao 7º')
            #     if(msg_error != None and msg_error != ''):
            #         msg_error += ' - Esta na consulta de 6 e 7 ano saque aniversario'

            if msg_error != None and msg_error != '': 
                if msg_error != 'Ocorreu um erro ao tentar consultar o saldo do FGTS' and 'Você precisa selecionar pelo menos uma simulação para continuar!' not in msg_error:
                    dados_post = {
                        "statusPropostaBanco": msg_error,
                        "codigoCon": proposta['codigoContrato'],
                        "ade": ''
                    }
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    print(response)
                    print(response.text)
                    #self.driver.refresh()
                    self.verificar_loading()
                    continue
                elif 'Você precisa selecionar pelo menos uma simulação para continuar!' in msg_error:
                    self.act.clicar_elemento('//*[@id="btnProsseguirSimulador"]', By.XPATH)
                else:
                    # CONTINUE
                    print('CONTINUE')
                    #self.driver.refresh()
                    self.verificar_loading()
                    continue

            # Tabela de Juros
            if proposta['produto'] == 'FGTS':
                msg_error = None
                simulou = False
                oferecer_maximo = False
                limites = []
                datas = []

                try:
                    self.numero_saques = self.act.quantidade_elemento('.valAntecipacao') + 1
                    self.numero_campos_saques = self.act.quantidade_elemento('.valAntecipacao')
                except:
                    raise ErroInicialException('Erro na pesquisa inicial area saques... Reiniciando processo...')
                
                for i in range(1, self.numero_saques):
                    limites.append(self.act.obter_texto(f'//*[@id="gridSaldoFgts"]/tbody/tr[{i}]/td[2]', By.XPATH).replace("R$ ", "").replace(",", "."))
                    datas.append(self.act.obter_texto(f'//*[@id="gridSaldoFgts"]/tbody/tr[{i}]/td[1]', By.XPATH))

                self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_0"]', By.XPATH)

                #if(self.ultimos_saques):
                #    self.act.enviar_texto('//*[@id="valFgtsAntecipacao_0"]', proposta['valoresSaqueAniversario']['sexto'], By.XPATH) 
                #else:

                if(proposta['valoresSaqueAniversario'] != ''):
                    self.act.enviar_texto('//*[@id="valFgtsAntecipacao_0"]', proposta['valoresSaqueAniversario']['primeiro'], By.XPATH)  

                    try:
                        self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_1"]', By.XPATH) 
                    except:
                        self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_0"]', By.XPATH) 

                    self.verificar_loading()
                    msg_error = self.pegar_msg_error()            
                    #pdb.set_trace()
                    if(msg_error):
                        #//*[@id="toast-container"]/div/button
                        print('Erro encontrado...1')

                    else:
                        #if(self.ultimos_saques):
                        #    self.act.enviar_texto('//*[@id="valFgtsAntecipacao_1"]', proposta['valoresSaqueAniversario']['setimo'], By.XPATH) 
                        #else:
                        try:
                            self.act.enviar_texto('//*[@id="valFgtsAntecipacao_1"]', proposta['valoresSaqueAniversario']['segundo'], By.XPATH)
                        except:
                            self.act.enviar_texto('//*[@id="valFgtsAntecipacao_0"]', proposta['valoresSaqueAniversario']['primeiro'], By.XPATH)

                        #pdb.set_trace()
                        if(self.numero_campos_saques > 2):

                            self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_2"]',  By.XPATH)
                            self.verificar_loading()
                            msg_error = self.pegar_msg_error()

                            if(msg_error):
                                print('Erro encontrado...2')
                            else:
                                self.act.enviar_texto('//*[@id="valFgtsAntecipacao_2"]',  proposta['valoresSaqueAniversario']['terceiro'], By.XPATH)
                            
                                if(self.numero_campos_saques > 3):
                                    self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_3"]',  By.XPATH)
                                    self.verificar_loading()
                                    msg_error = self.pegar_msg_error()

                                    if(msg_error):
                                        print('Erro encontrado...3')
                                    else:

                                        self.act.enviar_texto('//*[@id="valFgtsAntecipacao_3"]',  proposta['valoresSaqueAniversario']['quarto'], By.XPATH)    

                                        if(self.numero_campos_saques > 4):
                                            self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_4"]', By.XPATH)
                                            self.verificar_loading()
                                            msg_error = self.pegar_msg_error()  

                                            if(msg_error):
                                                print('Erro encontrado...4')
                                            else:
                                                self.act.enviar_texto('//*[@id="valFgtsAntecipacao_4"]',  proposta['valoresSaqueAniversario']['quinto'], By.XPATH)      

                                                if(self.numero_campos_saques > 5):
                                                    self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_5"]', By.XPATH)
                                                    self.verificar_loading()
                                                    msg_error = self.pegar_msg_error()  

                                                    if(msg_error):
                                                        print('Erro encontrado...5')
                                                    else:
                                                        self.act.enviar_texto('//*[@id="valFgtsAntecipacao_5"]',  proposta['valoresSaqueAniversario']['sexto'], By.XPATH)

                                                        if(self.numero_campos_saques > 6):
                                                            self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_6"]', By.XPATH)
                                                            self.verificar_loading()
                                                            msg_error = self.pegar_msg_error()
                                                            if(msg_error):
                                                                print('Erro encontrado...6')
                                                            else:
                                                                self.act.enviar_texto('//*[@id="valFgtsAntecipacao_6"]',  proposta['valoresSaqueAniversario']['setimo'], By.XPATH)
                                                                self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)                  
                                                                msg_error = self.pegar_msg_error()  

                                                                if(msg_error):
                                                                    print('Erro encontrado...7') 
                                                                else: 
                                                                    if(self.numero_campos_saques > 7):
                                                                        self.act.enviar_texto('//*[@id="valFgtsAntecipacao_7"]',  proposta['valoresSaqueAniversario']['oitavo'], By.XPATH)
                                                                        self.act.clicar_elemento('//*[@id="valFgtsAntecipacao_7"]', By.XPATH)
                                                                        self.verificar_loading()
                                                                        msg_error = self.pegar_msg_error()
                                                                        if(msg_error):
                                                                            print('Erro encontrado...8')
                                                                        else:
                                                                            if(self.numero_campos_saques > 8):
                                                                                self.act.enviar_texto('//*[@id="valFgtsAntecipacao_8"]',  proposta['valoresSaqueAniversario']['nono'], By.XPATH)
                                                                                self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)                
                                                                                msg_error = self.pegar_msg_error()
                                                                                if(msg_error):
                                                                                    print('Erro encontrado...9') 
                                                                                else:
                                                                                    if(self.numero_campos_saques > 9):
                                                                                        self.act.enviar_texto('//*[@id="valFgtsAntecipacao_9"]',  proposta['valoresSaqueAniversario']['decimo'], By.XPATH)
                                                                                        self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', self.tabela)                
                                                                                        msg_error = self.pegar_msg_error()
                                                                                        if(msg_error):
                                                                                            print('Erro encontrado...10')

                if(proposta['valoresSaqueAniversario'] == ''):
                    oferecer_maximo = True
                else:
                    if(limites and not msg_error and '0.00' not in proposta['valoresSaqueAniversario'].values() 
                        or limites and not msg_error and saques_iniciais == 'nao'):
                        oferecer_maximo = self.inserir_maximo(limites,proposta['valorTotalGarantia'])

                valor_resultado = 0
                try:
                    valor_resultado = float(self.act.obter_valor('//*[@id="ValorPrincipal"]',By.XPATH).replace('.','').replace(',','.'))
                except:
                    pass

                if(valor_resultado == 0.0):
                    oferecer_maximo = True

                if msg_error:
                    simulou = self.post_insercao_alert(limites, proposta, datas, msg_error, saques_iniciais)
                else:
                    if(oferecer_maximo == True):
                        simulou = self.post_insercao_alert(limites, proposta, datas, msg_error, saques_iniciais)
                    else:
                        simulou = self.post_atualiza_valores(limites, proposta, datas, msg_error, saques_iniciais)
            
            if simulou is False:
                # Simular
                msg_error = None
                msg_error = self.pegar_msg_error()

                if 'Prazo da operação inferior ao permitido.' in msg_error  or 'Valor liberado ao cliente deve ser superior' in msg_error:
                    dados_post = {
                    "statusPropostaBanco": msg_error,
                    "codigoCon": proposta['codigoContrato'],
                    "ade": ''
                    }
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    continue

                self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)
                msg_error = self.pegar_msg_error()

                valor_limites_somados = self.soma_limites(limites)

                if msg_error == 'Não foi possível encontrar saldos disponíveis.' and valor_limites_somados >= 500:
                    print('Como o saldo é maior do que simulado atualizamos os valores para o número...')
                    simulou = self.post_insercao_alert(limites, proposta, datas, msg_error, saques_iniciais)

                if msg_error == 'Ocorreu um erro no processamento dos dados, favor tentar novamente':
                    simulou = self.post_insercao_erro_processamento(limites, proposta, datas, msg_error, saques_iniciais)
                    if(simulou == False):
                        continue



            if proposta['produto'] == 'FGTS':
                id_parcela = 0
            elif proposta['produto'] == 'AUXILIO':
                try:
                    aviso_sem_tabela = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[2]/div/fieldset/div/div[1]/ul/li',By.XPATH)
                except:
                    aviso_sem_tabela = ""
                    pass

                if("não há tabelas para esta seleção." in aviso_sem_tabela):
                    print('Auxilio vai inserir assim que voltar...')
                    dados_post = {"statusPropostaBanco": 'Auxilio temporariamente nao permitido',"codigoCon": proposta['codigoContrato'],"ade": ''}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    continue

                id_parcela = 1
                self.menu_opcoes('//*[@id="IdTabelaJuros_chzn"]/a', 'AUXILIO BRASIL 4,19 - PRAZO DE 6 A 24')
                self.verificar_loading()
                self.act.enviar_texto('//*[@id="Prazos_chzn"]/ul/li/input', proposta['prazo'], By.XPATH)
                self.verificar_loading()
                self.act.enviar_texto('//*[@id="Prazos_chzn"]/ul/li/input', proposta['prazo'], By.XPATH)
                self.act.press_enter('//*[@id="Prazos_chzn"]/ul/li/input', By.XPATH)
                self.act.enviar_texto('//*[@id="ValorParcela"]',proposta['valorParcela'], By.XPATH)
            else:
                id_parcela = 1

            if(inserir_auxilio):
                self.act.clicar_elemento('//*[@id="divSimuladorConteudo"]/div/fieldset[2]/button[1]', By.XPATH)
                self.verificar_loading()
                principal = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[8]', By.XPATH)
                self.verificar_loading()
                self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[1]/input', By.XPATH)

            else:

                try:
                    self.act.clicar_elemento(f'//*[@id="{id_parcela}"]/td[1]/input', By.XPATH)
                except:
                    self.act.clicar_elemento(f'//*[@id="{id_parcela}"]/td[1]/input', By.XPATH)
                self.verificar_loading()                          

                principal = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]', By.XPATH)

            dados_post = {
                        "statusPropostaBanco": "Valor principal atualizado",
                        "codigoCon": proposta['codigoContrato'],
                        "ade": '',
                        "valorCon": principal.replace('.','').replace(',','.')
                    }

            print('Atualizando o valor para ' + str(principal))
            response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)

            # Gravar e avançar
            self.act.clicar_elemento('//*[@id="btnGravarSimulacao"]', By.XPATH)
            self.verificar_loading()
            
            msg_error = None
            msg_error = self.pegar_msg_error()
            
            if msg_error == 'Ocorreu um erro durante o processamento da solicitação':
                simulou = self.post_insercao_erro_processamento(limites, proposta, datas, msg_error, saques_iniciais)
                self.act.clicar_elemento(f'//*[@id="{id_parcela}"]/td[1]/input', By.XPATH)
                principal = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[5]/div/fieldset[2]/div[4]/div[1]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]', By.XPATH)
                print(principal)
                self.act.clicar_elemento('//*[@id="btnGravarSimulacao"]', By.XPATH)
                self.verificar_loading()
                msg_error = None

                if(float(principal.replace(',','.')) < 300 and saques_iniciais == 'sim'):
                    print('Proposta com valor menor que 300 reais...')
                    dados_post = {"statusPropostaBanco": 'Proposta menor que o valor minimo permitido',"codigoCon": proposta['codigoContrato'],"ade": ''}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    continue

                if(float(principal.replace(',','.')) < 200 and saques_iniciais == 'nao'):
                    print('Proposta com valor de saques finais menor que 200 reais...')
                    dados_post = {"statusPropostaBanco": 'Proposta menor que o valor minimo permitido',"codigoCon": proposta['codigoContrato'],"ade": ''}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    continue

            if msg_error:
                dados_post = {
                "statusPropostaBanco": msg_error,
                "codigoCon": proposta['codigoContrato'],
                "ade": ''
                }
                response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)


            self.verificar_loading()
            '''Dados Pessoais '''
            
            #nome completo
            self.act.enviar_texto('//*[@id="txtNomeCompleto"]', proposta['nome'], By.XPATH)

            if proposta['produto'] == 'AUXILIO':
                # Alfabetizado
                if proposta['grauInstrucao'] != 1:
                    self.menu_opcoes('//*[@id="ddlAlfabetizacao_chzn"]/a', 'SIM')
                else:
                    self.menu_opcoes('//*[@id="ddlAlfabetizacao_chzn"]/a', 'NÃO')
                self.verificar_loading()

                # Sexo
                if proposta['sexo'] == 'Feminino':
                    self.menu_opcoes('//*[@id="ddlSexo_chzn"]', 'FEMININO')
                else:
                    self.menu_opcoes('//*[@id="ddlSexo_chzn"]', 'MASCULINO')
                self.act.enviar_texto('//*[@id="ddlSexo_chzn"]/div/div/input', proposta['sexo'].upper(), By.XPATH)
                self.act.press_enter('//*[@id="ddlSexo_chzn"]/div/div/input', By.XPATH)

                # Nome Mãe
                preenchido = None
                try:
                    preenchido = self.act.obter_atributo('//*[@id="txtNomeMae"]', 'value', By.XPATH)
                except:
                    pass
                if not preenchido:
                    self.act.enviar_texto('//*[@id="txtNomeMae"]', proposta['nomeMae'], By.XPATH)

            # Data de nascimento
            self.act.enviar_texto('//*[@id="txtDtNascimento"]', proposta['dataNascimento'], By.XPATH)

            # Nome do Pai
            # preenchido = None
            # try:
            #     preenchido = self.act.obter_atributo('//*[@id="txtNomePai"]', 'value', By.XPATH)
            # except:
            #     pass
            # if proposta['nomePai'] != '' and preenchido == '':
            #     self.act.enviar_texto('//*[@id="txtNomePai"]', proposta['nomePai'], By.XPATH)
            # # Documento
            # self.act.enviar_texto('//*[@id="txtRG"]', proposta['identidade']['numero'], By.XPATH)
            # # Uf Documento
            # try:
            #     self.menu_opcoes('//*[@id="ddlUFRG_chzn"]/a', proposta['identidade']['uf'])
            # except:
            #     pass
            # self.verificar_loading()
            
            
            
            # Estado civil
            # if proposta['outrosDadosPessoais']['estadoCivil'] == 'Solteiro (a)':
            #     estado_civil = 'SOLTEIRO'
            # elif proposta['outrosDadosPessoais']['estadoCivil'] == 'Casado (a)':    
            #     estado_civil = 'CASADO'
            # else:
            #     estado_civil = 'DIVORCIADO'
            # self.menu_opcoes('//*[@id="ddlEstadoCivil_chzn"]/a', estado_civil)
            self.verificar_loading()
            # Nome Mãe
            # preenchido = None
            # try:
            #     preenchido = self.act.obter_atributo('//*[@id="txtNomeMae"]', 'value', By.XPATH)
            # except:
            #     pass
            # if not preenchido:
            #     self.act.enviar_texto('//*[@id="txtNomeMae"]', proposta['nomeMae'], By.XPATH)

            #self.verificar_loading()
            #email
            self.act.enviar_texto('//*[@id="txtEmail"]', proposta['outrosDadosPessoais']['email'], By.XPATH)
            #self.verificar_loading()
            # try:
            #     if proposta['outrosDadosPessoais']['estadoCivil'] == 'Casado (a)':
            #         self.act.enviar_texto('//*[@id="txtNomeConjuge"]', proposta['outrosDadosPessoais']['conjuge'], By.XPATH)
            # except:
            #     pass

            ''' Contato do Cliente '''
            #self.verificar_loading()            
            # try:                
            #     self.act.clicar_elemento('//*[@id="Add_-1"]', By.XPATH)
            # except:
            #     pass

            #self.verificar_loading()

            # DDD
            # self.act.enviar_texto('//*[@id="jqg1_DDD"]', proposta['dddCelular'], By.XPATH)
            # self.verificar_loading()
            # Telefone
            #self.act.clicar_elemento('//*[@id="jqg1_Telefone"]', By.XPATH)

            # self.act.hover_e_clique('//*[@id="gview_ContatoGrid"]/div[3]',By.XPATH)
            # self.act.hover_e_clique('//*[@id="jqg1"]/td[2]',By.XPATH)
            # self.act.enviar_texto_intervalado('//*[@id="jqg1_Telefone"]', ' ' + proposta['celular'], By.XPATH)
            # self.verificar_loading()

            ### Referencia pessoal ###
            # self.act.enviar_texto('//*[@id="txtNomeRef"]', proposta['referenciaPessoal']['nome'], By.XPATH)
            # self.verificar_loading()
            # Afinidade
            # try:
            #     if proposta['referenciaPessoal']['afinidade'] == 'Amigo(a)':
            #         proposta['referenciaPessoal']['afinidade'] = 'Amigos(as)'
            #     self.menu_opcoes('//*[@id="ddlAfinidade_chzn"]/a', proposta['referenciaPessoal']['afinidade'].upper())
            #     self.verificar_loading()
            # except:
            #     self.verificar_loading()
            
            # Telefone
            # self.act.enviar_texto('//*[@id="txtDigitoTel"]', proposta['referenciaPessoal']['telefone'][0:4], By.XPATH)
            # self.verificar_loading()

            # if(len(proposta['referenciaPessoal']['telefone'][5:]) < 8):
            #     self.act.enviar_texto('//*[@id="txtTelefoneRef"]',  proposta['referenciaPessoal']['telefone'][4:], By.XPATH)
            # else:
            #     self.act.enviar_texto('//*[@id="txtTelefoneRef"]',  proposta['referenciaPessoal']['telefone'][5:], By.XPATH)
            # self.verificar_loading()

            # self.menu_opcoes('//*[@id="ddlAfinidade_chzn"]/a', proposta['referenciaPessoal']['afinidade'].upper())
            # self.verificar_loading()

            # self.act.clicar_elemento('//*[@id="btnAdicionarRef"]', By.XPATH)
            # self.verificar_loading()

            ''' Endereço '''
            
            # Cep
            cep =  self.act.obter_atributo('//*[@id="txtCep"]', 'value', By.XPATH)
            if cep == '':
                self.act.enviar_texto('//*[@id="txtCep"]', proposta['endereco']['cep'], By.XPATH)

            self.verificar_loading()
            self.act.clicar_elemento('//*[@id="txtLogradouro"]', By.XPATH)
            # Logradouro
            logradouro = self.act.obter_atributo('//*[@id="txtLogradouro"]', 'value', By.XPATH)
            if logradouro == '':
                self.act.enviar_texto('//*[@id="txtLogradouro"]', proposta['endereco']['logradouro'], By.XPATH)
            # NRO
            nro = self.act.obter_atributo('//*[@id="txtNumero"]', 'value', By.XPATH)
            if nro == '':
                if proposta['endereco']['numero'] is None: 
                    self.act.enviar_texto('//*[@id="txtNumero"]', '0', By.XPATH)
                else:
                    self.act.enviar_texto('//*[@id="txtNumero"]', proposta['endereco']['numero'], By.XPATH)
            # Compltemento
            complemento = self.act.obter_atributo('//*[@id="txtComplemento"]', 'value', By.XPATH)
            if complemento == '':
                if proposta['endereco']['numero'] is None: 
                    self.act.enviar_texto('//*[@id="txtComplemento"]', '0', By.XPATH)
                else:
                    self.act.enviar_texto('//*[@id="txtComplemento"]', proposta['endereco']['complemento'], By.XPATH)
            # Bairro
            bairro = self.act.obter_atributo('//*[@id="txtBairro"]', 'value', By.XPATH)
            if bairro == '':
                self.act.enviar_texto('//*[@id="txtBairro"]', proposta['endereco']['bairro'], By.XPATH)
            # Cidade
            cidade = self.act.obter_atributo('//*[@id="txtCidade"]', 'value', By.XPATH)
            if cidade == '':
                self.act.enviar_texto('//*[@id="txtCidade"]', proposta['endereco']['cidade'], By.XPATH)
            try:
                self.menu_opcoes('//*[@id="ddlUF_chzn"]/a', proposta['endereco']['uf'])
            except:
                pass
            self.act.clicar_elemento('//*[@id="btnConsultarEndereco"]', By.XPATH)

            ''' Dados da Ocupação '''
            # Uf beneficiop do cliente
            # --> proposta['produto']
            self.verificar_loading()

            # if proposta['produto'] == 'INSS':
            #     # orgao empregador
            #     self.menu_opcoes('//*[@id="ddlOrgaosEmpregadores_chzn"]/a', 'INSS')
            # elif proposta['produto'] == 'FGTS':                
            #     self.menu_opcoes('//*[@id="ddlOrgaosEmpregadores_chzn"]/a', 'FGTS')
            if proposta['produto'] == 'AUXILIO':
                self.verificar_loading()

                #orgao empregador
                self.menu_opcoes('//*[@id="ddlOrgaosEmpregadores_chzn"]/a', 'SUBSECRETARIA A ADM MINISTERIO CIDADANIA')

                #regime juridico
                self.menu_opcoes('//*[@id="ddlRegimesJuridico_chzn"]/a', 'CLT')

                #situacao
                self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'ATIVO')
                self.verificar_loading()

                #vinculo
                self.menu_opcoes('//*[@id="ddlVinculoEmpregaticio_chzn"]/a', 'TEMPORÁRIO')

                #profissao
                self.menu_opcoes('//*[@id="ddlProfissao_chzn"]/a', 'AUXILIO BRASIL')

                #cargo
                self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'AUXILIO BRASIL')

                #renda
                self.act.enviar_texto('//*[@id="txtValorRenda"]', '600.00', By.XPATH)

                # Data de admissao
                self.act.enviar_texto('//*[@id="txtDtAdmissao"]', '01/01/2000', By.XPATH)

            # regime juridico
            # self.menu_opcoes('//*[@id="ddlRegimesJuridico_chzn"]/a', 'CLT')
            # self.menu_opcoes('//*[@id="ddlRegimesJuridico_chzn"]/a', 'CLT')
            # self.verificar_loading()

            # if proposta['produto'] == 'inss':
            #     self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'INATIVO')
            #     self.menu_opcoes('//*[@id="ddlProfissao_chzn"]/a', 'INSS')
            #     #self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'INSS')
            # else:
            #      self.menu_opcoes('//*[@id="ddlSituacaoEmpregado_chzn"]/a', 'ATIVO')
            #      self.verificar_loading()

            #      self.menu_opcoes('//*[@id="ddlVinculoEmpregaticio_chzn"]/a', 'EFETIVO')
            #      self.verificar_loading()

            #      self.menu_opcoes('//*[@id="ddlProfissao_chzn"]/a', 'ANALISTA')
            #      self.verificar_loading()

            #      self.menu_opcoes('//*[@id="ddlOrgaosEmpregadores_chzn"]/a', 'FGTS')
            #      self.verificar_loading()

            # Vinculo Empregaticio
            # if proposta['produto'] == 'FGTS':
            #     self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'ANALISTA DE OPERACOES COMERCIAIS')
            #     self.verificar_loading()
            #     self.menu_opcoes('//*[@id="ddlCargos_chzn"]/a', 'ANALISTA DE OPERACOES COMERCIAIS')

            # Valor Renda
            # if proposta['produto'] == 'FGTS':
            #     renda = '5000.00'

            # self.act.enviar_texto('//*[@id="txtValorRenda"]', renda, By.XPATH)
            # self.verificar_loading()

            # Data de Admissão
            # self.act.enviar_texto('//*[@id="txtDtAdmissao"]', '01012010', By.XPATH)
            # self.verificar_loading()

            try:
                #verifica o aviso A conta bancária que será creditada é a mesma do contrato de Empréstimo FGTS realizado anteriormente. Em caso de dúvidas, oriente o cliente a consultar o seu contrato de Empréstimo FGTS anterior.
                aviso_conta = self.act.obter_texto('//*[@id="fstDadosBancarios"]/div/ul/li',By.XPATH)
                if('A conta bancária que será creditada é a mesma do contrato de Empréstimo FGTS realizado anteriormente' in aviso_conta):
                    print('Pulando...')
                    conta_registrada = True
                else:
                    print('Registrando a conta...')
                    conta_registrada = False
            except:
                conta_registrada = False

            if not conta_registrada:
                # Tipo de Pagamento 
                tipo = proposta['banco']['tipoConta'].replace('-', ' ')
                if tipo.split()[-1] == 'poupança':
                    tipo = 'Poupança'
                #self.menu_opcoes('//*[@id="ddlTipoPagamentoBeneficio_chzn"]/a', tipo)
                # Tipo de COnta
                self.menu_opcoes('//*[@id="ddlTiposContasBanco_chzn"]/a', tipo)
                self.verificar_loading()

                # banco
                try:
                    self.menu_opcoes('//*[@id="ddlBanco_chzn"]/a', proposta['banco']['numeroBanco'])
                except:
                    pass
                
                try:    
                    self.menu_opcoes('//*[@id="ddlBanco_chzn"]/a', proposta['banco']['numeroBanco'])
                except:
                    pass

                # Agencia
                self.verificar_loading()
                
                self.act.enviar_texto_intervalado ('//*[@id="txtAgencia"]', proposta['banco']['agencia'], By.XPATH)
                self.verificar_loading()

                try:
                    opcoes_agencias = int(self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[7]/div/form/fieldset[6]/p[3]/span',By.XPATH).split(' ')[0])
                except:
                    try:
                        opcoes_agencias = int(self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[3]/div[7]/div/form/fieldset[6]/p[3]/span',By.XPATH).split(' ')[0])  
                    except: 
                        opcoes_agencias = 0
                        pass
                    pass            

                if(opcoes_agencias > 1):
                    for i in range(1,opcoes_agencias): self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.DOWN)
                elif (opcoes_agencias == 1):
                    self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.DOWN)
                    self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.DOWN)
                else:
                    print('XXXXXXXXXXXXXXXXXXXXXXAGENCIA INVALIDAXXXXXXXXXXXXXXXXXXXXXX')
                    
                    self.act.clicar_elemento('//*[@id="btnValidarProposta"]', By.XPATH)
                    self.verificar_loading()
                    self.act.clicar_elemento('//*[@id="btnGravarProposta"]', By.XPATH)
                    while True:
                        try:
                            self.act.obter_texto('//*[@id="divLoading"]', By.XPATH)
                        except:
                            break
                    self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
                    self.act.enviar_texto('//*[@id="PainelControle_cpf"]', proposta['cpf'], By.XPATH)
                    self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]/span', By.XPATH)
                    self.verificar_loading()
                    indice = 0                   
                    if(self.act.quantidade_elemento('.btnMenuContext') > 1): 

                        for i in range(0,self.act.quantidade_elemento('.btnMenuContext')):
                            texto_status1 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[2]', By.XPATH)
                            texto_status2 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[5]', By.XPATH)
                            if texto_status1 == '' and texto_status2 == 'Em Digitação': 
                                ade = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[6]/a', By.XPATH)
                                self.act.clicar_elemento(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[4]/a/span', By.XPATH)
                                indice = i + 2
                                break
                    else:

                        ade = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]/a', By.XPATH)
                        self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[4]/a/span', By.XPATH)
                    dados_post = { "statusPropostaBanco": "Erro ao digitar a agencia", "codigoCon": proposta['codigoContrato'], "ade": ade, "valorCon": formatar_moeda(principal)}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    break   

                self.verificar_loading()            

                self.driver.find_element_by_xpath('//*[@id="txtAgencia"]').send_keys(Keys.ENTER)

                # Conta Corrente
                self.act.enviar_texto('//*[@id="txtContaCorrente"]', proposta['banco']['numeroConta'] + proposta['banco']['digitoConta'], By.XPATH)

            # Validar digitação
            # if(conta_registrada):
            #     pdb.set_trace()
            self.act.clicar_elemento('//*[@id="btnValidarProposta"]', By.XPATH)
            self.verificar_loading()

            self.verifica_campos_obrigatorios(proposta)

            try:
                self.verificar_loading()
                self.act.clicar_elemento('//*[@id="btnSubmeterProposta"]', By.XPATH)
                try:
                    msg_error = self.pegar_msg_error()
                except:
                    msg_error = ''
                    pass

                if 'UF do endereço divergente da UF da origem!' in msg_error:
                    print('UF divergente, cadastrando novamente o endereço...')
                    self.act.enviar_texto('//*[@id="txtCep"]', proposta['endereco']['cep'], By.XPATH)
                    self.verificar_loading()
                    self.act.clicar_elemento('//*[@id="btnConsultarEndereco"]', By.XPATH)
                    self.verificar_loading()
                    try:
                        self.act.enviar_texto('//*[@id="txtNumero"]', proposta['endereco']['numero'], By.XPATH)
                    except:
                        pass
                    try:
                        self.act.enviar_texto('//*[@id="txtComplemento"]', proposta['endereco']['complemento'], By.XPATH)
                    except:
                        pass
                    self.verificar_loading()
                    self.act.clicar_elemento('//*[@id="btnSubmeterProposta"]', By.XPATH)

            except:
                print('Erro ao submeter proposta')
                dados_post = { "statusPropostaBanco": "Proposta digitada gerar manual", "codigoCon": proposta['codigoContrato'], "ade": ade, "valorCon": formatar_moeda(principal)}
                response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                print(response)
                continue

            while True:
                try:
                    self.act.obter_texto('//*[@id="divLoading"]', By.XPATH)
                except:
                    break
        
            self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
            self.act.enviar_texto('//*[@id="PainelControle_cpf"]', proposta['cpf'], By.XPATH)
            self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]/span', By.XPATH)
            self.verificar_loading()

            #nova tratativa para pegar ade de contratos com muitas insercoes  
            indice = 0     
            quantidade_propostas = self.act.quantidade_elemento('.btnMenuContext')               
            if(quantidade_propostas> 1): 
                for i in range(0,quantidade_propostas):
                    texto_status1 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[2]', By.XPATH)
                    texto_status2 = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[5]', By.XPATH)
                    produto = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[8]', By.XPATH)

                    if(produto == 'Auxilio Brasil' and proposta['produto'] == 'AUXILIO'):
                        if texto_status1 == '' and texto_status2 == 'Em Análise': 
                            ade = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[6]/a', By.XPATH)
                            #self.act.clicar_elemento(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[4]/a/span', By.XPATH)
                            indice = i + 2
                            break
                    else:
                        if texto_status1 == '' and texto_status2 == 'Em Análise': 
                            ade = self.act.obter_texto(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[6]/a', By.XPATH)
                            #self.act.clicar_elemento(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{i+2}]/td[4]/a/span', By.XPATH)
                            indice = i + 2
                            break
            else:

                ade = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[6]/a', By.XPATH)
                #self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[4]/a/span', By.XPATH)

            self.verificar_loading()
            #titulo_d = self.act.obter_texto('/html/body/div[9]/div[1]/span', By.XPATH)

            url_bruta = None
            d_textos = {}

            # try:
            #     quantidade_td = self.act.quantidade_elemento('/html/body/div[9]/div[2]/fieldset/table/tbody/tr[1]/td', By.XPATH)                
            #     for j in range(1, quantidade_td + 1):
            #         d_textos[self.act.obter_texto(f'html/body/div[9]/div[2]/fieldset/table/tbody/tr[{j}]/td[1]', By.XPATH)] = self.act.obter_texto(f'/html/body/div[9]/div[2]/fieldset/table/tbody/tr[{j}]/td[2]', By.XPATH)
            #     for k in d_textos:
            #         if "Clique" in k:
            #             url_bruta = k.split()
            #             url_bruta = url_bruta[-1]
            # except:
            d_textos = ''
            print('Não existe LINK')

            #clica no X
            #self.act.clicar_elemento('/html/body/div[9]/div[1]/button', By.XPATH)

            if(self.act.quantidade_elemento('.btnMenuContext') > 1):  
                try:               
                    self.act.clicar_elemento(f'/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[{indice}]/td[1]/a', By.XPATH)
                except:
                    print('XXXXXXXXXXXXX Erro de impressão da proposta XXXXXXXXXXXXXXXX')
                    dados_post = { "statusPropostaBanco": "Recusada", "codigoCon": proposta['codigoContrato'], "ade": 0}
                    response = APIDataSource().post_request_v2('enviar-dados-safra', dados_post)
                    print(response)
                    continue
            else:
                self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[1]/a', By.XPATH)

            self.verificar_loading()

            # BASE64 
            if proposta['produto'] == 'AUXILIO':
                self.act.clicar_elemento('/html/body/ul/li[6]', By.XPATH)
            else:
                self.act.clicar_elemento('/html/body/ul/li[4]', By.XPATH)

            try:
                self.act.obter_texto('//*[@id="divSiteIndisponivel"]/span', By.XPATH)
                pdf_base64 = None
                self.verificar_loading()
                self.act.clicar_elemento('//*[@id="divSiteIndisponivel"]/span/a', By.XPATH)
            except:
                f = []
                for (dirpath, dirnames, filenames) in walk(self.path):
                    f.extend(filenames)
                    break
                pdf_base64 = convert_file_base_64(self.path + f[0])
                deleta_todos_arquivos(self.path)
                pdf_base64 = pdf_base64.decode('utf-8')

            print(ade)

            if proposta['produto'] == 'FGTS' or proposta['produto'] == 'AUXILIO':
                payload = {
                    "codigoCliente": proposta['codigoCliente'],
                    "codigoContrato": proposta['codigoContrato'],
                    "ade": ade,
                    "base64": pdf_base64,
                    "linkAssinaturaDigital": url_bruta,
                    "banco":"safra-fgts",
                    "valorCon": formatar_moeda(principal),
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
                
                response = APIDataSource().post_request_v2('enviar-dados-safra-insercao', payload)
                print(response)
        
        print('##########ACABOU##########')

class ErroInicialException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


if __name__ == '__main__':
    robo = Consulta_Safra()
    while True:
        robo.main()
        sleep(60)