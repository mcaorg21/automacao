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
import pdb,shutil
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
                sleep(30)
                self.driver.delete_all_cookies()
                

            try:
                for dic in contratos:
                    info = {}
                    info['key'] = 'f689f1e12a0399fba803cb2365fc362f'
                    info['codigo_contrato'] = dic['codigo_contrato']
                    cpf = dic['cpf_cliente']

                    # try:
                    #     self.act.reCaptcha_v2(self.key)
                    # except ConnectionError:
                    #     print('Site do captcha recusou a conexão')
                    #     sleep(10)
                    #     self.consultar(resetar = True)

                    try:
                        self.act.clicar_elemento('//*[@id="consulta-situacao-eleitoral-form-submit"]', By.XPATH)
                    except:
                        pass

                    self.act.enviar_texto(
                        "//input[@name='nomeTituloCPF']", cpf, metodo=By.XPATH)
                    
                    self.act.press_enter("//button[@class='btn btn-amarelo']", metodo=By.XPATH)

                    #self.act.press_enter("//button[@class='btn btn-amarelo']", metodo=By.XPATH)
                    try:
                        self.act.hover_e_clique('//*[@id="consulta-situacao-eleitoral-form-submit"]', By.XPATH)
                        sleep(1)
                        self.act.hover_e_clique('//*[@id="consulta-situacao-eleitoral-form-submit"]', By.XPATH)
                        sleep(1)
                        self.act.hover_e_clique('//*[@id="consulta-situacao-eleitoral-form-submit"]', By.XPATH)
                    except:
                        pass

                    try:
                        loading = self.act.obter_texto('img-loading loading-situacao-eleitoral', metodo=By.CLASS_NAME)
                        while loading:
                            print('carregando')
                            sleep(1)
                    except:
                        pass
                    
                    try:                       
                        biometria = self.act.obter_texto('/html/body/main/div/div/div[3]/div/div/div/section/div[1]', metodo=By.XPATH)
                        biometria = biometria.replace('ELEITOR/ELEITORA ', '')
                        situacao = self.act.obter_texto("/html/body/main/div/div/div[3]/div/div/div/section/div[2]/p[2]", metodo=By.XPATH)                        
                        situacao = situacao.replace('Situação da Inscrição:\n', '')
                        info['resultado'] = 'success'
                        info['biometria'] = biometria
                        info['situacao'] = situacao
                        print(cpf)
                        print(f'\033[;32m{info}\033[m')

                        post_met = APIDataSource().post_request_v2('enviar-info-cpfs-tse', info)
                        print(post_met.text)

                        self.count += 1
                        print(self.count)

                    except TimeoutException:
                        #self.driver.get("http://www.tse.jus.br/eleitor/titulo-e-local-de-votacao/copy_of_consulta-por-nome")
                        #pass
                        try:
                            alerta = self.act.obter_texto("/html/body/main/div/div/div[3]/div/div/div/section/div[1]", metodo=By.XPATH)
                            print(f'\033[;31m{alerta}\033[m')
                            if alerta == 'Serviço temporariamente indisponível':
                                sleep(300)
                                self.consultar(resetar = True)

                            info['resultado'] = 'alert'
                            print(cpf)
                            print(f'\033[;31m{info}\033[m')

                            post_met = APIDataSource().post_request_v2('enviar-info-cpfs-tse', info)
                            print(post_met)

                            self.count += 1
                            print(self.count)
                        except TimeoutException or Exception:                            
                            try:
                                self.act.obter_texto('//*[@id="texto-conteudo"]/p', metodo=By.XPATH)
                            except:
                                print('ERRO DE XPATH OU Captcha não passou')
                                sleep(300)
                                self.driver.quit()
                                print('Resetando consulta...')
                                self.consultar()
                       
                    self.driver.get("http://www.tse.jus.br/eleitor/titulo-e-local-de-votacao/copy_of_consulta-por-nome")    
                    # try:                    
                    #     self.act.clicar_elemento("/html/body/main/div/div/article/div/article/main/section/div[2]/button", metodo=By.XPATH)
                    # except:
                    #     try:
                    #         self.act.obter_texto('//*[@id="texto-conteudo"]/p', By.XPATH)
                    #         print('pegou meu try')
                    #         self.consultar(resetar=True)
                    #     except:
                    #         self.act.clicar_elemento("/html/body/main/div/div/article/div/article/main/section/form/fieldset/button", metodo=By.XPATH)                      
                
                print('Essa leva já acabou, esperando a api pegar mais cpfs...')
                sleep(300)
                self.driver.quit()
                

            except:
                sleep(300)
                self.driver.quit()
                print('Resetando consulta...')
                self.consultar()



if __name__ == '__main__':
    Consulta_Cpf().consultar()
