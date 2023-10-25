# import sys
# sys.path.append('../')

from selenium import webdriver
from selenium.webdriver.common.by import By
from sites.core.selenium_actions import SeleniumActions
from sites.core.selenium_actions import SeleniumActions
from dados.APIDataSource import APIDataSource
from sites.ibConsig.gerarContrato.GerarContratos import ItauGerarContratos   
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
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
import re
from tkinter import Tk


class Extrair_tags():
    def __init__(self):
        self.counter = 0
        self.options = webdriver.ChromeOptions()
        self.pasta_arquivos_tag = "/home/gustavo/Desktop/automacao-python/sites/ibConsig/gerar_contrato_icdigital/arquivos_tag/"
        #self.pasta_arquivos_tag = 'C:\\wamp64\\www\\automacao-python\\sites\\ibConsig\\gerar_contrato_icdigital\\arquivos_tag\\'

        self.options.add_experimental_option('prefs', {
            "download.default_directory": self.pasta_arquivos_tag, 
            "download.prompt_for_download": False, 
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True 
        })
        self.driver = webdriver.Chrome(options=self.options)   
        self.driver.get('https://portal.icconsig.com.br')
        self.driver.delete_all_cookies()
        self.driver.get('https://portal.icconsig.com.br')
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
        nome_arquivo = str(os.listdir(self.pasta_arquivos_tag)).replace('[', '').replace(']', '').replace("'", "", 2)
        os.remove(self.pasta_arquivos_tag +nome_arquivo)

    def lidar_msg(self, msg):
        if "Erro ao extrair" in msg or "CCB" in msg or "Tipo de documento de identificação inválido" in msg:
            return True
        
        elif "Esta proposta já foi importada" in msg:
            return False   

    def clicar_importar_proposta(self):
        try:
            sleep(5)
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
                        return False
                    except TimeoutException or ElementClickInterceptedException:
                        pass
        except StaleElementReferenceException:
            sleep(10)
            self.loading()
        except TimeoutException:
            pass

    def importar_proposta(self, payload):
        counter = 0
        # daqui para baixo fica no laço
        self.driver.set_window_size(600, 600)
        self.driver.set_window_position(0, 0)
        pagina = self.driver.current_window_handle 
        cont = 0
        while True:
            try:
                self.login()
                self.clicar_importar_proposta()
            except:
                pass
                
            self.driver.switch_to.window(pagina)

            #sleep(2)
            #pyautogui.click(x=472, y=66)
            sleep(10)
            pyautogui.click(x=472, y=66)
            sleep(3)
            pyautogui.click(x=465, y=120)
            sleep(1)
            pyautogui.moveTo(300, 150)
            sleep(1)
            pyautogui.dragTo(300, 400, 2, button='left')
            self.loading()
            
            try:
                msg_error = self.act.obter_texto("/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[3]/div[2]/cc-alert/div/span", metodo=By.XPATH)
                break
            except TimeoutException:
                msg_error = None
                pass
            try:
                msg_anexado_sucesso = self.act.obter_texto('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[2]/div/span', metodo=By.XPATH)
                if msg_anexado_sucesso == 'Importação concluída':
                    break
                break
            except TimeoutException:
                msg_anexado_sucesso = None
                pass
            if cont >= 10:
                break
            cont += 1


        self.apagar_arquivo()
        print('apagou arquivo')
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
                f = open("/home/gustavo/automacao-python/sites/ibConsig/gerar_contrato_icdigital/novas_ades.txt", "a")
                f.write(f'{payload["ade"]}\n')
                f.close()
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div[2]/button/div', metodo=By.XPATH) 
                return True

            elif 'concluída' in msg_anexado_sucesso:
                print("\033[91mconcluida\033[m")
                self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[4]/div[2]/button', metodo=By.XPATH)
                self.enviar_post(True, payload)
                f = open("/home/gustavo/automacao-python/sites/ibConsig/gerar_contrato_icdigital/novas_ades.txt", "a")
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

    def enviar_sms(self, proposta_ic360 = False):
        # Envia o sms   

        if(proposta_ic360 == True):
            self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-detail/div/div/app-dashboard/div[3]/div[1]/app-send-link-button/button', By.XPATH)
        try:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[6]/div[1]/div/div/label/div[1]/div/div/div', By.XPATH)
        except:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/div[1]/div/div/label/div[1]/div/div/div', By.XPATH)
        # Conclui o envio
        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[2]/div/button', By.XPATH)
        
        print("[DEBUG] SMS enviado")

        if(proposta_ic360 == True):
            self.driver.get('https://portal.icconsig.com.br/proposal')        

    def enviar_whatsapp(self):
        # Envia o wa
        try:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/div[2]/div/div/label/div[1]/div/div/div', By.XPATH)
        except:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/div[1]/div/div/label/div[1]/div/div/div', By.XPATH)
        # Conclui o envio
        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[2]/div/button', By.XPATH)
        print("[DEBUG] Link de whatsapp ativado")

    def get_link_assinatura_digital(self,status):
        if(status == 'LINK ENVIADO' or status == 'NOVA'):
            self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/div',metodo=By.XPATH)
            if(status == 'NOVA'):
                try:
                    self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/cc-radio-group/cc-radio-control[2]/div/div/div', By.XPATH)
                    self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[6]/div[1]/div/div/label/div[1]/div/div/div', By.XPATH)
                except:
                    pass
        else:
            self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[2]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button',metodo=By.XPATH)

        try:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/div[3]/div/div/label/div[1]/div/div/div', metodo=By.XPATH)
        except:
            pass

        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[2]/div/button/div', metodo=By.XPATH)
        sleep(1)
        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-link-generated/div/div/div[4]/button', metodo=By.XPATH)
        link = Tk().clipboard_get()
        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-link-generated/div/div/div[1]/button/div', metodo=By.XPATH)
        Tk().quit()
        print("Link-->" + link)

        return "https"+link.split("https")[-1]

    def passos(self, texto_link, ass_digital_wa = False):
        # atributo
        print('passos')
        contador_erros = 0

        if(texto_link == 'LINK ENVIADO' or texto_link == 'NOVA'):
            proposta_ic360 = False
            try:
                try:
                    self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/div',metodo=By.XPATH)
                except:
                    self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[1]/div/div[2]/span',metodo=By.XPATH)
                    proposta_ic360 = True

                if(ass_digital_wa):
                    self.enviar_whatsapp()
                else:
                    # Manda SMS
                    self.enviar_sms(proposta_ic360)
            except:
                pass
            if(texto_link == 'NOVA'):
                try:
                    texto = self.act.obter_texto("/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/div/span", By.XPATH)
                    if "Existem mais" in texto:
                        # Clica em formalizar em lote
                        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-sent-link/form/div/div[1]/div/div[3]/cc-radio-group/cc-radio-control[2]/div/div/div', By.XPATH)
                        self.enviar_sms()
                        sleep(2)
                except:
                    pass
            return True

        if(texto_link == 'CLIENTE ATUANDO' or texto_link == 'PENDÊNCIA'):
            try:
                # Manda SMS
                self.act.clicar_elemento('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[2]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/div', metodo=By.XPATH)
                self.enviar_sms()
            except:
                pass
            return True

        return False

    def inserir_contrato(self, payload, codigo_cli):
        try:
            self.clicar_importar_proposta()
        except:
            self.login()
            self.clicar_importar_proposta()
            
        url = APIDataSource().get('arquivo_pdf_ade_iccdigital').replace('{ade}', payload['ade']).replace('{codigo_cli}', codigo_cli)
        print(url)
        # começa o get
        response = requests.get(url=url)
        if response.text == '':
            payload['status_assinatura'] = "CCB VAZIA WEB ADMIN"
            x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
            print(x)
            return
        resultado = json.loads(response.text)
        dados = resultado['contratos']
        # baixa o arquivo pdf
        self.driver.get(dados[0]['arquivoPdf'])
        # importar proposta
        self.importar_proposta(payload)
        print('saiu importar proposta')
        # sai da tela de anexar
        self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[1]/div/button', metodo=By.XPATH)
        #self.act.clicar_elemento(, metodo=By.XPATH)

    def pesquisar_id(self):
        sleep(5)
        try:
            self.act.trocar_frame_seletor('/html/body/cc-lib-dialog[2]/div/div[1]/div[2]/div/app-auth-dialog/div/iframe', metodo=By.XPATH)
            self.act.obter_texto('//*[@id="reset-pwd"]', metodo=By.XPATH)
            self.login()
        except:
            pass
        try:
            self.act.clicar_elemento('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-proposal-import/div/div/div/div[1]/div/button', metodo=By.XPATH)
        except TimeoutException:
            pass
        self.driver.set_window_size(1004, 787)

        response = APIDataSource().get_request('propostas_icconsig_itau')
        response_dict = json.loads(response.text)
        try:
            self.propostas = response_dict['contratos']
        except:
            print('Está sem propostas')
            sleep(500)
        for i in self.propostas:
            print(i)
            self.ade = i['ade']
            self.ass_digital = i['assDigital']
            payload = {}
            payload['key'] = "f689f1e12a0399fba803cb2365fc362f"
            payload['ade'] = i['ade']
            payload['codigo_contrato'] = i['codigo_contrato']
            print(payload)
            self.act.enviar_texto('//*[@id="my-label-id"]/input', i['ade'], metodo=By.XPATH)
            self.act.press_enter('//*[@id="my-label-id"]/input', metodo=By.XPATH)

            payload['status_assinatura'] = self.pegar_tag()

            try:
                button_send = self.driver.find_element(By.XPATH,'//*[@id="swiper-wrapper-57380db2a84a69ba"]/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button')
                button_send_sms = button_send.is_enabled()
            except:
                button_send_sms = True
                pass
            pdb.set_trace()
            if(payload['status_assinatura'] == 'pular consulta' or (button_send_sms == False and payload['status_assinatura'] != 'FORMALIZADA')):
                print('Pulando reenvio de SMS')
                continue


            if self.ass_digital != '3' and (payload['status_assinatura'] == 'NOVA' or payload['status_assinatura'] == 'LINK ENVIADO' or payload['status_assinatura'] == 'PENDÊNCIA' or payload['status_assinatura'] == 'CLIENTE ATUANDO'):
                #if(payload['status_assinatura'] == 'NOVA' or payload['status_assinatura'] == 'LINK ENVIADO'):
                try:
                    #payload['link_assinatura_digital'] = self.get_link_assinatura_digital(payload['status_assinatura'])
                    payload['link_assinatura_digital'] = "";
                    sleep(1)
                    y = self.passos(payload['status_assinatura'])

                except:
                    continue

            if(self.ass_digital == '3' and payload['status_assinatura'] == 'LINK ENVIADO'):
                if 'cancelar link via whatsapp' not in self.act.obter_texto('/html/body/app-root/app-content-layout/cc-drawer/div/div/main/app-kanban/div[1]/div[3]/div/div/div[1]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div/app-card/div/div/div[2]/div[3]/div/app-send-link-button/button/span', metodo=By.XPATH):
                    print("Assinatura digital por whatsapp...")
                    y = self.passos(payload['status_assinatura'], True)
                else:
                    print("Link por whatsapp ja ativado...")

            
            if payload['status_assinatura'] is False:
                a = self.inserir_contrato(payload, i['codigo_cliente'])
                self.driver.set_window_size(1004, 787)
                if a is False:
                    x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
                continue
            
            #post entra aqui
            try:
                x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
                print(x.text)
            except:
                x = APIDataSource().post_request_v2('enviar-dados-propostas-iccdigital', payload)
                print(x.text)
        
        self.driver.refresh()  

    def pegar_tag(self, recr = 0):

        sleep(3)

        texto_link = False
        textos = self.driver.execute_script(""" return document.getElementsByClassName('kanban'); """)

        array_palavras = [];
        array_status = ['NOVA','LINK ENVIADO','CLIENTE ATUANDO','PENDÊNCIA','FORMALIZADA','EM ANÁLISE','EM PROCESSAMENTO','CANCELADA']
        
        for texto in textos: 
            texto_legenda = texto.text.strip()   
            array_palavras.append(texto_legenda)  

            for status in array_status:
                if status in texto_legenda:
                    texto_link = status
                    self.counter += 1

        try:
            ade = int(re.findall(r'\d{7,10}', str(array_palavras))[0])
        except:
            ade = 0
        
        if(len(str(array_palavras))) > 550:
            print('Não achou ADE...')
            return 'pular consulta'
        else:
            if(len(str(array_palavras))) < 250:
                recr += 1
                if(recr <= 5):
                    self.act.enviar_texto('//*[@id="my-label-id"]/input', self.ade, metodo=By.XPATH)
                    self.act.press_enter('//*[@id="my-label-id"]/input', metodo=By.XPATH)
                    return self.pegar_tag(recr)


        if self.ade not in str(array_palavras) and 'Formalização em lote' not in str(array_palavras) and int(self.ade) >= int(ade) + 10:
            print('Ade diferente ou proposta de portabilidade##############################')            
            return False

        if(texto_link):
            print('>>>>>>>>>>>Texto encontrato: ' + texto_link)
            return texto_link
        else:
            print('XXXXXXXXXXX Texto não encontrato')
            self.counter += 1
            print(f'\033[93mNão apareceu nenhum...{self.counter}\033[m')
            return False
    
    #def login(self, login='06050694680@1873', senha='Tim223754@'):
    def login(self, login='07488396669@1873', senha='Tim223754@'):
        self.act.trocar_frame_seletor('/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-auth-dialog/div/iframe', metodo=By.XPATH)
        self.act.enviar_texto('/html/body/div/div/div/div/div/div/form/div[1]/input', login, metodo=By.XPATH)
        self.act.enviar_texto("/html/body/div/div/div/div/div/div/form/div[2]/input", senha, metodo=By.XPATH)
        self.act.clicar_elemento('//*[@id="kc-login"]', metodo=By.XPATH) 
        while self.driver.current_url == 'https://portal.icconsig.com.br/':
            sleep(1)
              

    def iniciar(self):
        self.login()
        arquivos_sobrando = glob.glob(self.pasta_arquivos_tag + '*')
        for f in arquivos_sobrando:
            os.remove(f)

        while True:
            self.pesquisar_id()
            
            
    
