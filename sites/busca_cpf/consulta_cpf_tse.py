import json,sys,os

cmd = 'tmpreaper 1m /tmp'
os.system(cmd)

sys.path.append('../')

import PATHS

from sites.baseRobos.manager import Manager
from time import sleep
from requests.exceptions import ConnectionError
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dados.APIDataSource import APIDataSource
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.helpers import definir_nome_robo
import pdb,shutil,random
import tkinter as tk

class Consulta_Cpf:
    def __init__(self):
        self.key = "6Ld5n8EUAAAAAJJuJF7h6B7JLjhvFZzoYTQ6jCJ1"
        self.count = 0
        self.user_driver_path: str = PATHS.project_path()+"/chrome_user_dir/MTSE22"
        self.options = Options()
        #self.options.add_argument('--headless')
        #self.options.add_argument('--no-sandbox')
        #self.options.add_argument('--disable-dev-shm-usage')
        self.key = "6Lc0k1MUAAAAAJgAqPTO0dutvMB_m4ZVuvcvUMhA"


    def consultar(self, resetar = False):
        definir_nome_robo("Consulta CPF TSE")

        
        while True:
            print('Pegando nova lista de CPFs...')
            response = APIDataSource().get_request("consulta-cpf-tse")
            response = response.text
            response = json.loads(response)


            
            try:
                contratos = response['contratos']
            except KeyError:
                print('Está sem cpfs para serem consultados')
                sleep(300)
                self.consultar()

            if(resetar == False):
                #root = tk.Tk()
                #screen_width = root.winfo_screenwidth()
                #screen_height = root.winfo_screenheight()

                chrome_user = PATHS.chrome_user("MTSE22")
                try:
                    pasta = chrome_user.split('=')[1]
                    shutil.rmtree(pasta)
                except:
                    pass
                options = Options()
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--window-size=826,800')
                options.add_argument('--no-sandbox')  
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(chrome_user)
                options.add_experimental_option("w3c", False)
                #options.add_argument('--headless')
                #options.add_argument(f'--window-position={int(screen_width-screen_width/3)},0')
                options.add_argument(chrome_user)
                options.add_argument('--profile-directory=Default')
                Manager.criar_pasta_usuario_chrome(chrome_user)
                #self.driver = webdriver.Chrome("C:\\wamp64\\www\\automacao-python\\drivers\\chromedriver.exe",chrome_options=options)
                #self.driver = webdriver.Chrome(options=options)
                self.driver = webdriver.Chrome(options=self.options)
                self.driver.delete_all_cookies()
                self.act = SeleniumActions(self.driver)
                #self.driver.get('https://www.tse.jus.br/servicos-eleitorais/titulo-e-local-de-votacao/copy_of_consulta-por-nome')
                self.driver.get("http://www.tse.jus.br/eleitor/titulo-e-local-de-votacao/copy_of_consulta-por-nome")
                self.driver.delete_all_cookies()
                

            try:
                for dic in contratos:
                    info = {}
                    info['key'] = 'f689f1e12a0399fba803cb2365fc362f'
                    info['codigo_contrato'] = dic['codigo_contrato']
                    cpf = dic['cpf_cliente']

                    try:
                        self.act.clicar_elemento('/html/body/div[9]/div/div/div[2]/button', By.XPATH)
                    except:
                        pass

                    try:
                        self.act.clicar_elemento('//*[@id="content"]/app-root/div/app-atendimento-eleitor/div[1]/app-menu-option[7]/button', By.XPATH)
                    except:
                        pass

                    try:
                        self.act.clicar_elemento('/html/body/main/div/div/div[3]/div/div/app-root/app-modal-auth/div/div/div/div/div[2]/div[2]/div/button', By.XPATH)
                    except:
                        pass 

                    self.act.enviar_texto('//*[@id="modal"]/div/div/div[2]/div[2]/form/div[1]/div/input', cpf, metodo=By.XPATH)        
                    
                    sleep(4)

                    self.act.clicar_elemento('//*[@id="modal"]/div/div/div[2]/div[2]/form/div[2]/button[2]', metodo=By.XPATH)

                    tentativa = 0

                    while self.act.quantidade_elemento('//*[@id="content"]/app-root/app-barra-tempo-token/div/div/mat-icon', By.XPATH) == 0:
                        sleep(1)
                        print('Aguardando abertura de tela...')
                        tentativa += 1
                        if(tentativa >= 50):
                            raise TimeoutException()
                    
                    try:                       
                        biometria = self.act.obter_texto('/html/body/main/div/div/div[3]/div/div/app-root/div/app-consultar-situacao-titulo-eleitor/div[1]/div[2]/div[2]/div/p', metodo=By.XPATH)
                        biometria = biometria.replace('ELEITOR/ELEITORA ', '')

                        try:
                            situacao = self.act.obter_texto("/html/body/main/div/div/div[3]/div/div/app-root/div/app-consultar-situacao-titulo-eleitor/div[1]/div[1]/p/span", metodo=By.XPATH)                        
                        except:
                            print('ERRO DE GET DE xpath')                            

                        if 'REGULAR' not in situacao and 'CANCELADO' not in situacao and 'SUSPENSO' not in situacao:
                            try:
                                alerta = self.act.obter_texto('/html/body/main/div/div/div[3]/div/div/app-root/app-modal-mensagem/div/div/div/div[1]/p', By.XPATH)
                                if('Deslogado por inatividade' in alerta):
                                    sleep(10)
                                    self.driver.quit()
                                    print('Resetando consulta...')
                                    self.consultar()
                            except:
                                pdb.set_trace()

                        info['resultado'] = 'success'
                        info['biometria'] = biometria
                        info['situacao'] = situacao
                        print(cpf)
                        print(f'\033[;32m{info}\033[m')

                        post_met = APIDataSource().post_request_v2('enviar-info-cpfs-tse', info)
                        print(post_met.text)

                        self.count += 1
                        print(self.count)

                        tempo_aleatorio = random.uniform(1,5)
                        sleep(tempo_aleatorio)

                    except TimeoutException:
                        try:
                            alerta = self.act.obter_texto('/html/body/main/div/div/div[3]/div/div/app-root/app-modal-confirmacao/div/div/div/div[1]/p', By.XPATH)
                            if('destinada a eleitores cadastrados' in alerta):

                                info['resultado'] = 'success'
                                info['biometria'] = 'NAO POSSUI CADASTRO'
                                info['situacao'] = 'NAO POSSUI CADASTRO'

                                post_met = APIDataSource().post_request_v2('enviar-info-cpfs-tse', info)
                                print(post_met.text)

                                self.count += 1
                                print(self.count)

                                sleep(3)
                                try:
                                    self.act.clicar_elemento('/html/body/main/div/div/div[3]/div/div/app-root/app-modal-confirmacao/div/div/div/div[2]/button[1]', By.XPATH)
                                except:
                                    pass

                                sleep(10)
                                self.driver.quit()
                                print('Resetando consulta...')
                                self.consultar()
                        except:
                                pdb.set_trace()
                                pass
                        print('ERRO DE XPATH OU Captcha não passou')
                        sleep(302)
                        self.driver.quit()
                        print('Resetando consulta...')
                        self.consultar()
                       
                                
                    self.driver.get("http://www.tse.jus.br/eleitor/titulo-e-local-de-votacao/copy_of_consulta-por-nome")                       
                
                print('Agaurdando mais CPF´s para consulta...')
                sleep(303)
                self.driver.quit()
                

            except:
                #pdb.set_trace()
                self.act.clicar_elemento('//*[@id="modal"]/div/div/div[1]/button', By.XPATH)
                sleep(2)
                self.act.clicar_elemento('//*[@id="content"]/app-root/app-modal-mensagem/div/div/div/div[2]/button', By.XPATH)
                sleep(10)
                self.driver.delete_all_cookies()
                self.driver.quit()
                print('Resetando consulta...')
                self.consultar()



if __name__ == '__main__':
    Consulta_Cpf().consultar()
