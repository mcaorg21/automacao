import sys,pdb
sys.path.append('../')
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dados.APIDataSource import APIDataSource
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_actions import SeleniumActions as SelAct
from sites.baseRobos.core.data_helpers import make_request
from requests.exceptions import SSLError, ConnectionError
import requests
from time import sleep
from json import loads



class Consulta_Receita():
    def __init__(self):
        self.options = Options()
        #self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.key = "6Lc0k1MUAAAAAJgAqPTO0dutvMB_m4ZVuvcvUMhA"
        self.count = 0


    def consulta_site(self):
        while True:
            response = APIDataSource().get_request("consulta-cpf-federal")
            response = response.text
            response = loads(response)
            contratos = response['contratos']
            if contratos == []:
                print('Está sem cpfs para serem consultados')
                sleep(300)
                self.consulta_site()

            self.driver = webdriver.Chrome(options=self.options)
            self.driver.get(
                "https://servicos.receita.fazenda.gov.br/servicos/cpf/consultasituacao/consultapublica.asp")
            self.act = SeleniumActions(self.driver)
            self.actAlter = SelAct(self.driver)

            for dic in contratos:
                info = {}
                info['key'] = 'f689f1e12a0399fba803cb2365fc362f'
                info['codigo_tipo_analise'] = 25
                info['codigo_contrato'] = dic['codigo_contrato']
                cpf = dic['cpf_cliente']

                nascimento = dic['nascimento_cli']
                nascimento = nascimento[8:10] + \
                    nascimento[5:7] + nascimento[:4]

                #self.act.press_enter(
                #    '//*[@id="id_captchasonoro"]', metodo=By.XPATH)
                #sleep(4)

                # try:
                #     img_base64 = self.act.obter_atributo(
                #         '//*[@id="imgCaptcha"]', 'src', metodo=By.XPATH)
                # except TimeoutException:
                #     try:
                #         self.act.obter_texto(
                #             '//*[@id="content"]/div/fieldset/h2', metodo=By.XPATH)
                #         print('\033[;31m500-INTERNAL SERVER ERROR\033[m')

                #     except TimeoutException:
                #         print('Trying get the image again...')
                #         img_base64 = self.act.obter_atributo(
                #             '//*[@id="imgCaptcha"]', 'src', metodo=By.XPATH)

                # try:
                #     captcha_token = self.act.reCaptcha(self, img_base64)
                # except SSLError or ConnectionError:
                #     print('erro com o captcha')
                #     captcha_token = self.act.reCaptcha(self, img_base64)

                # if captcha_token == 'ERRR_CAPTCHA_UNSOLVABLE':
                #     sleep(120)
                #     captcha_token = self.act.reCaptcha(self, img_base64)

                # self.act.enviar_texto(
                #     '//*[@id="txtTexto_captcha_serpro_gov_br"]', captcha_token, metodo=By.XPATH)

                self.act.enviar_texto('//*[@id="txtCPF"]',
                                      cpf, metodo=By.XPATH)
                self.act.enviar_texto(
                    '//*[@id="txtDataNascimento"]', nascimento, metodo=By.XPATH)
                
                try:
                    site_key = self.actAlter.obter_atributo('//*[@id="hcaptcha"]','data-sitekey',By.XPATH)
                except:
                    print('XXXXXXXXXXXXX ERRO AO OBTER SITE KEY XXXXXXXXXXXXXX')
                    site_key = '53be2ee7-5efc-494e-a3ba-c9258649c070'                  
                    pass
                try:                    
                    self.actAlter.hcaptcha(site_key, '')
                except:
                    print("Captcha não precisou ser resolvido.")

                self.act.press_enter('//*[@id="id_submit"]', metodo=By.XPATH)

                sleep(5)
                try:
                    situacao = self.act.obter_texto(
                        '//*[@id="mainComp"]/div[2]/p/span[4]/b', metodo=By.XPATH)
                    if situacao == 'PENDENTE A REGULARIZAÇÂO' or situacao == 'pendente a regularização':
                        print(situacao)
                    info['situacao'] = situacao
                    print(f'\033[32m{info} \033[m')
                    try:
                        post_met = APIDataSource().post_request_v2('enviar-infos-cpf-federal', info)
                        print(f'\033[33mRESPONSE {post_met}\033[m')
                        self.count += 1
                        print(self.count)
                    except ConnectionError:
                        while ConnectionError:
                            post_met = APIDataSource().post_request_v2('enviar-infos-cpf-federal', info)
                            sleep(120)
                        print(f'\033[33mRESPONSE {post_met}\033[m')

                except TimeoutException:
                    try:
                        if 'Data de nascimento' in self.act.obter_texto('//*[@id="content-core"]/div/div/div[1]/span/h4/b', By.XPATH):
                            info['situacao'] = "Data de nascimento informada está divergente"
                            post_met = APIDataSource().post_request_v2('enviar-infos-cpf-federal', info)
                            print(f'\033[33mRESPONSE {post_met}\033[m')
                            self.count += 1
                            print(self.count)
                    except:
                        try:
                            error_msg = self.act.obter_texto(
                                '//*[@id="F_Consultar"]/div/div/div[1]/span/h4/b/a', metodo=By.XPATH)

                            if error_msg == 'página anterior':
                                info['situacao'] = 'pendente'
                                print(info)
                            try:
                                post_met = APIDataSource().post_request_v2('enviar-infos-cpf-federal', info)
                                print(f'\033[33mRESPONSE {post_met}\033[m')
                                self.count += 1
                                print(self.count)
                            except ConnectionError:
                                while ConnectionError:
                                    sleep(120)
                                    post_met = APIDataSource().post_request_v2('enviar-infos-cpf-federal', info)
                                print(f'\033[33mRESPONSE {post_met}\033[m')

                        except TimeoutException:
                            try:
                                self.act.obter_texto(
                                    '//*[@id="idMensagemErro"]/span', metodo=By.XPATH)
                                print('Captcha nao passou!')
                                print('\033[;31mDo cpatcha nn passou\033[m')
                                self.driver.close()
                                self.consulta_site()
                            except TimeoutException:
                                print(TimeoutException)
                                print('\033[;31mcaiu no except do captcha nn passou\033[m')
                
                self.act.clicar_elemento(
                    '//*[@id="idRodape"]/p[4]/a/span', metodo=By.XPATH)

            print('Cpfs acabaram')
            sleep(5)
            self.driver.close()
            sleep(300)


if __name__ == '__main__':
    x = Consulta_Receita().consulta_site()
