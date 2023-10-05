from selenium.common.exceptions import TimeoutException

from sites.cora.libs.elementos.Botoes import btn_acessar_fact
from sites.cora.libs.elementos.TextInputs import input_senha_fact, input_login_fact

from sites.elementos import Button, BaseElement
from sites.elementos import TextInput, Chrome

from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from dados.APIDataSource import APIDataSource

from selenium.webdriver.common.by import By

from time import sleep
import time,random

import pdb
import PATHS


class FormLogin:

    def __init__(self, driver: Chrome):
        self.driver: Chrome = driver 
        self.sl = PATHS.slash()  
        self.chrome_user = driver.capabilities['chrome']['userDataDir'].split(self.sl)[6]
        self.final_nome_cookies = driver.capabilities['chrome']['userDataDir'].split(self.sl)[6].split('_')[1] 
        self.sh = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver)
        self.request = APIDataSource()
        self.cookies_path_sincronizador: str = PATHS.project_path()+f'{self.sl}cora{self.sl}cookies{self.sl}cookies_1.pkl'
        self.cookies_path: str = PATHS.project_path()+f'{self.sl}cora{self.sl}cookies{self.sl}cookies_'+self.final_nome_cookies+'.pkl'
        self.base_path: str = PATHS.project_path()  

    @staticmethod
    def realizar_login(driver: Chrome) -> bool:  
        login = FormLogin(driver)
        return login.verificar_login()

    def verificar_login(self):

        self.driver.get('https://app.cora.com.br/dashboard')   
        try:
            try:
                self.sh.load_cookies(self.cookies_path_sincronizador)
            except:
                self.sh.load_cookies(self.cookies_path)
        except:
            try:
                open(self.cookies_path, "x")
            except:
                pass
        
        if(self.verifica_se_logado() == True):
            return True

        if(self.tempo_ultimo_login(15)[0] == False):
            if(self.verifica_se_logado() == True):
                return True
            # aguardar = int(self.final_nome_cookies)*6
            # print('Aguardando '+ str(int(self.final_nome_cookies)*6) +' segundos...')
            # if(aguardar > 36):
            #     self.verificar_login()
            sleep(random.randrange(12, 60, 12))

        #registra tentativa de login para que os outros que forem logar respeitem o tempo de espera
        self.tentativa_ultimo_login()

        rec = 0
        while self.act.quantidade_elemento('/html/body/div[1]/div/nav/div/div/div/svg', By.XPATH) == 0:
            
            if(self.verifica_se_logado() == True):
                return True

            print('Aguardando confirmação de sessão..') 
            #self.driver.get('https://app.cora.com.br/dashboard')
            rec +=1
            if(rec > 3 or self.act.quantidade_elemento('/html/body/div/section/div/div[1]/figure/figcaption', By.XPATH) == 1):
                print('Tentativa: '+str(rec))
                break

            if (self.act.quantidade_elemento('//*[@id="single-spa-application:@cora/dashboard"]/div/header/div/div[1]/h1', By.XPATH) == 1):
                return True
            sleep(1) 

        codigo = ''
        rec = 0
        while self.act.quantidade_elemento('/html/body/div/section/div/div[1]/figure/figcaption', By.XPATH) == 0 or codigo == '':
            print('Aguardando codigo na tela...') 
            try:
                codigo = self.act.obter_texto('/html/body/div/section/div/div[1]/figure/figcaption', By.XPATH)
            except:
                codigo = ''
                rec +=1
                if(rec > 50):
                    return False
                else:
                    print('Tentativa: '+str(rec))
                sleep(1)

        #payload = {"telefoneDDD": '31991399952',"mensagem": codigo+'_codigo_cora',"key": "f9223937d6a342a75fa449a2e5bbd75b"}
        #response = APIDataSource().post_request_v2('enviar-mensagem-sms', payload)  
        #response = APIDataSource().post_request_v2('enviar-mensagem-whatsapp', payload) 
        #SAMSUMG
        #payload = {"idOneSignal": "48740934-b134-11ec-8adc-1e1a79f53678", "titulo": "_codigo_cora", "mensagem": codigo,"key": "f9223937d6a342a75fa449a2e5bbd75b"} 
        #LG
        #NAO É O ID DO ONESIGNAL QUE MANDA E SIM O PLAYER ID
        payload = {"idOneSignal": "9cdabc5a-67c2-4f8f-a02a-aae51344b654", "titulo": "_codigo_cora", "mensagem": codigo,"key": "f9223937d6a342a75fa449a2e5bbd75b"}
        
        response = APIDataSource().post_request_v2('enviar-mensagem-push', payload)  
        
        rec = 0
        while self.act.quantidade_elemento('/html/body/div/section/div/div[1]/figure/figcaption', By.XPATH) == 1:
            print('Codigo encontrado,' + codigo + ' aguardando atualizacao manual e liberacao de login na tela...') 
            rec +=1
            if(rec > 60):
                return False
            else:
                print('Tentativa: '+str(rec))
            sleep(1)

        rec = 0
        while self.act.quantidade_elemento('/html/body/div[2]/div/nav/div/div/div/svg', By.XPATH) == 1:
            print('Aguardando carregar página para emissão da cobrança...') 
            rec +=1
            if(rec > 50):
                return False
            else:
                print('Tentativa: '+str(rec))
            sleep(1)

        
        self.sh.save_cookies(self.cookies_path)      

        self.tentativa_ultimo_login()

        return True

    def tentativa_ultimo_login(self):
        f = open(self.base_path+f"{self.sl}cora{self.sl}ultimo_login.txt", "w")
        f.write(str(time.time()))
        f.close()

    def tempo_ultimo_login(self, tempo_passado_ultimo_login = 20):
        ultimo_login = open(self.base_path+f"{self.sl}cora{self.sl}ultimo_login.txt", "r").read()
        tempo_ultimo_login = time.time()
        try:
            tempo_ultimo_login = float(tempo_ultimo_login) - float(ultimo_login)
        except:
            tempo_ultimo_login = 0
        
        if tempo_ultimo_login > tempo_passado_ultimo_login:
            return True,tempo_ultimo_login
        else:
            return False,tempo_ultimo_login

    def verifica_se_logado(self):
        if (self.act.quantidade_elemento('//*[@id="root"]/div/header/div[1]', By.XPATH) == 1):
            print('Logado...')
            return True
        else:
            return False

