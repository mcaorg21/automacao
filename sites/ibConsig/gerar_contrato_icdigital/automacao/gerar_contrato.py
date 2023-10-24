#import sys
#sys.path.append('../')

from selenium import webdriver
from selenium.webdriver.common.by import By
from sites.core.selenium_actions import SeleniumActions
from sites.core.selenium_actions import SeleniumActions
from dados.APIDataSource import APIDataSource
from sites.ibConsig.gerarContrato.GerarContratos import ItauGerarContratos   
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, InvalidSessionIdException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime
import os
import requests
from requests.exceptions import ConnectionError 
import json
import glob
import pdb
import pyautogui


class IbConsig_gerar():
    def __init__(self):
        self.counter = 0
        self.caminho_servidor = '/home/gustavo/Desktop/automacao-python/sites/ibConsig/gerar_contrato_icdigital/arquivos/'
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('prefs', {
            "download.default_directory": self.caminho_servidor, 
            "download.prompt_for_download": False, 
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True 
        })
        self.google_aberto = True
        self.driver = webdriver.Chrome(options=self.options)   
        self.driver.get('https://portal.icconsig.com.br')
        self.driver.set_window_size(600, 600)
        self.driver.set_window_position(0, 0)
        self.gerenciar_contratos = ItauGerarContratos(self.driver)
        self.act = SeleniumActions(self.driver)
        

    def enviar_post(self, good, payload):
        print(good)
        if good is False:
            payload['status_assinatura'] = "ERRO SUBIR CCB"
            x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
        else:
            payload['status_assinatura'] = "NOVA"
            x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
        print(x.text)


    def apagar_arquivo(self):
        nome_arquivo = str(os.listdir(self.caminho_servidor)).replace('[', '').replace(']', '').replace("'", "", 2)
        os.remove(self.caminho_servidor + nome_arquivo)


    def lidar_msg(self, msg):
        if "Erro ao extrair" in msg or "CCB" in msg:
            return True
        
        elif "Esta proposta já foi importada" in msg:
            return False
        

    def enviar_link(self):
        f = open('/home/gustavo/Desktop/automacao-python/sites/ibConsig/gerar_contrato_icdigital/novas_ades.txt', 'r+')
        for line in f:
            sleep(2)
            self.act.enviar_texto('//*[@id="my-label-id"]/input', line, metodo=By.XPATH)
            sleep(3)
            self.act.press_enter('//*[@id="my-label-id"]/input', metodo=By.XPATH)
            self.passos()
        f.truncate(0)

    def arquivos_para_contrato(self):
        # get dos contratos
        try:
            response = APIDataSource().get_request('arquivos_icdigital')
        except ConnectionError:
            self.driver.quit()
            self.google_aberto = False
            print("Erro conexão, espere 30s..")
            sleep(30)
            self.arquivos_para_contrato() 
        try:
            response_dict = json.loads(response.text)
            contratos = response_dict['contratos']
        except:
            print('Ta sem...')
            print(">>>>>> ESPERA 60 SEGUNDOS <<<<<<")
            sleep(60)
            self.arquivos_para_contrato()
            
        # Importar proposta
        return contratos

    def clicar_importar_proposta(self):
        try:                        
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[1]/div/button', By.XPATH)
        except:
            pass
        try:
            sleep(3)
            self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[2]/button', metodo=By.XPATH)
        except:
            pyautogui.click(x=458, y=520)
            pass

    def loading(self):
        try:
            counter = 0
            while 'pdf' in self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[2]/cc-dropzone/div/div[1]/div/div/div', metodo=By.XPATH):
                sleep(0.5)
                counter += 1
                if counter > 35:
                    try:
                        self.act.trocar_frame_seletor('/html/body/cc-lib-dialog[2]/div/div[1]/div[2]/div/app-auth-dialog/div/iframe', metodo=By.XPATH)
                        self.act.obter_texto('//*[@id="reset-pwd"]', metodo=By.XPATH)
                        self.login()
                        break
                        
                    except TimeoutException or ElementClickInterceptedException:
                        pass
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            sleep(10)
            self.loading()
        

    def importar_proposta(self, payload):
        counter = 0
        # daqui para baixo fica no laço
        self.driver.set_window_size(600, 600)
        self.driver.set_window_position(0, 0)
        pagina = self.driver.current_window_handle 
        while True:
            self.driver.switch_to.window(pagina)

            #sleep(2)
            #pyautogui.click(x=472, y=66)
            sleep(1)
            pyautogui.click(x=472, y=66)
            sleep(1)
            pyautogui.click(x=465, y=120)
            sleep(1)
            pyautogui.moveTo(300, 150)
            sleep(1)
            pyautogui.dragTo(300, 400, 2, button='left')
            self.loading()
            
            try:
                msg_error = self.act.obter_texto("/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[2]/cc-alert/div/span", metodo=By.XPATH)
                print(msg_error)
                break
            except TimeoutException:
                msg_error = None
                print('Entrou None')
                pass
            try:
                msg_anexado_sucesso = self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[2]/div/span', metodo=By.XPATH)
                print(msg_anexado_sucesso)
                if msg_anexado_sucesso == 'Importação concluída':
                    break
                break
            except TimeoutException:
                print('Entrou Ultimo NoNe')
                msg_anexado_sucesso = None
                pass
        
        try:
            self.apagar_arquivo()
        except:
            arquivos_sobrando = glob.glob(self.caminho_servidor + '*')
            for f in arquivos_sobrando:
                os.remove(f)
            
        if msg_error != None:
            print(f'\033[93m{msg_error}\033[m')
            if self.lidar_msg(msg_error) is True:
                payload['status_assinatura'] = "ERRO SUBIR CCB"
                self.enviar_post(False, payload)
                return False
            
            elif self.lidar_msg(msg_error) is False:
                    counter += 1
                    payload['status_assinatura'] = 'LINK ENVIADO'
                    APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
                    return False
            else:
                return False
       
        if msg_anexado_sucesso != None:
            print(msg_anexado_sucesso)
            if 'formalização' in msg_anexado_sucesso:
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[2]/cc-radio-group/cc-radio-control[2]/div/div/div', metodo=By.XPATH)
                sleep(2)
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div/button/div', metodo=By.XPATH)
                sleep(2)
                self.enviar_post(True, payload)
                f = open("/home/gustavo/Desktop/automacao-python/sites/ibConsig/gerar_contrato_icdigital/novas_ades.txt", "a")
                f.write(f'{payload["ade"]}\n')
                f.close()
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div[2]/button/div', metodo=By.XPATH) 
                return True

            elif 'concluída' in msg_anexado_sucesso:
                print("\033[91mconcluida\033[m")
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div[2]/button', metodo=By.XPATH)
                self.enviar_post(True, payload)
                f = open("/home/gustavo/Desktop/automacao-python/sites/ibConsig/gerar_contrato_icdigital/novas_ades.txt", "a")
                f.write(f'{payload["ade"]}\n')
                f.close()
                return True

            elif 'Atenção!' in msg_anexado_sucesso:
                self.enviar_post(False, payload)
                # processo anti-fraude
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[2]/cc-checkbox/div/div/div', metodo=By.XPATH)
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[4]/button', metodo=By.XPATH)

            try:
                z = self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[2]/div/span', metodo=By.XPATH)
                if z == 'Importação concluída':
                    self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div[2]/button', metodo=By.XPATH)
            except TimeoutException:
                pass
        
        sleep(10) 

    def passar_img(self):
        contratos = self.arquivos_para_contrato()
        qtd_novos = 0
        counter = 0
       
        for i in contratos:    
            print(counter)
            print(i)
            payload = {}
            payload['key'] = "f689f1e12a0399fba803cb2365fc362f"
            payload['ade'] = i['ade']
            payload['codigo_contrato'] = i['codigo_contrato']
            if self.google_aberto is not True:
                self.driver = webdriver.Chrome(options=self.options)   
                self.gerenciar_contratos = ItauGerarContratos(self.driver)
                self.act = SeleniumActions(self.driver)
                self.driver.get('https://portal.icconsig.com.br')
                self.login()

            self.clicar_importar_proposta()
            try:
                self.driver.get(i['arquivoPdf'])
            except:
                payload['status_assinatura'] = "ERRO SUBIR CCB"
                self.enviar_post(False, payload)
                continue

            test = self.importar_proposta(payload)
            if test is False or None:
                print('test é false ou None')
                continue     
            elif test is True:
                qtd_novos += 1
            counter += 1
            
        print('\033[92mACABOU...\033[m' + ' Quantidade de novos:' + str(qtd_novos))
        if qtd_novos == 0:
            try:
                try:
                    self.driver.close()
                except:
                    pass
                self.google_aberto = False
                print('Esperando 30 segundos...')
                sleep(30)
            except InvalidSessionIdException:
                pass 
            return
        self.driver.refresh()
        self.enviar_link()
        

    def ___antiga___deprecated_passos(self):
        # atributo
        print('passos')
        contador_erros = 0
        
        try:
            # enviar link
            self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/button', metodo=By.XPATH)
        except TimeoutException or ElementClickInterceptedException or StaleElementReferenceException:
            contador_erros += 1
            try:
                # enviar link EM ANDAMENTO
                self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[2]/div/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/button', metodo=By.XPATH)
            except TimeoutException or ElementClickInterceptedException:
                return False

        sleep(1)
        try:
            
            #'/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/div/div[1]/div[1]/div[1]/span'
            texto = self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[1]/div[1]/div[1]/span', metodo=By.XPATH)
            if "Existem mais" in texto:
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[1]/div[2]/div[2]/cc-radio-group/cc-radio-control[2]/div/div/div', metodo=By.XPATH)
        except TimeoutException or StaleElementReferenceException:
            pass
        
        sleep(3)
        try:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[2]/div[1]/div/button', metodo=By.XPATH)
        except TimeoutException or ElementClickInterceptedException:
            while self.act.obter_texto("/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[1]/div/div[1]/span", metodo=By.XPATH) != "Como deseja enviar o link?":
                sleep(2)
            print("Acabou")

    def passos(self, texto_link):
        # atributo
        print('passos')
        contador_erros = 0

        if(texto_link == 'LINK ENVIADO' or texto_link == 'NOVA'):
            try:
                self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/div',metodo=By.XPATH)
            except:
                pass
            if(texto_link == 'NOVA'):
                try:
                    texto = self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[1]/div[1]/div[1]/span', metodo=By.XPATH)
                    if "Existem mais" in texto:
                        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[1]/div[2]/div[2]/cc-radio-group/cc-radio-control[2]/div/div/div', metodo=By.XPATH)
                        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div/div/app-sent-link/div/div[2]/div[1]/div/button', metodo=By.XPATH)
                        sleep(2)
                except:
                    pass
            return True

        if(texto_link == 'CLIENTE ATUANDO' or texto_link == 'PENDÊNCIA'):
            try:
                self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[2]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/div', metodo=By.XPATH)
            except:
                pass
            return True

        return False

    def login(self, login='07488396669@1873', senha='Tim223754@'):
        self.act.trocar_frame_seletor('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-auth-dialog/div/iframe', metodo=By.XPATH)
        self.act.enviar_texto('/html/body/div/div/div/div/div/div/form/div[1]/input', login, metodo=By.XPATH)
        self.act.enviar_texto("/html/body/div/div/div/div/div/div/form/div[2]/input", senha, metodo=By.XPATH)
        self.act.clicar_elemento('//*[@id="kc-login"]', metodo=By.XPATH) 
        while self.driver.current_url == 'https://portal.icconsig.com.br/':
            sleep(1)

    def iniciar(self):
        arquivos_sobrando = glob.glob(self.caminho_servidor + '*')
        for f in arquivos_sobrando:
            os.remove(f)
        while True:
            self.passar_img()