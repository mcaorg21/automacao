from selenium.webdriver import Chrome,ChromeOptions
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException,StaleElementReferenceException,WebDriverException

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.pyautogui_helper import find_elements_on_screen

from sites.baseRobos.core.helpers import deleta_todos_arquivos,formatar_moeda

#from PIL import Image
import PIL.Image as Image
from array import array

import fitz
import base64
import os,time,pdb,json,io,sys
import PATHS
#import cv2
#import pyautogui

from time import sleep
from datetime import datetime

from sites.cora.consultas_emissoes.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

from pyzbar.pyzbar import decode

HORARIO_COMERCIAL = 8, 20


class ConsultaEmissoes(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "qr_code_cobranca": "https://app.cora.com.br/emitir-cobranca/novo-contato",
            "gestao_pagamentos": "https://app.cora.com.br/gestao-de-boleto",
            "gestao_extrato": "https://app.cora.com.br/extrato",
            "transferencia_pix": "https://app.cora.com.br/transferencia"
        }
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.sl = PATHS.slash() 
        #self.imagem_continuar = cv2.imread(PATHS.project_path()+"\\cora\\continuar.png")

    @classmethod
    def iniciar(self, driver: Chrome, dados):        
        run = ConsultaEmissoes(driver)

        #caso envie teste de qrcode emitiremos um especifico e fixo
        if(dados['teste_qrcode'] == True):
            resultado_qrcode = {'retorno_imagem': True, 'pix_cc' : b'00020101021226960014br.gov.bcb.pix2574api.developer.btgpactual.com/v1/p/v2/cobv/6a1a8422ecca432fa2faa3581a775da95204000053039865802BR5908UCONECTE6014BELO HORIZONTE61083013091762070503***630467BE','imagem_base64': b'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', 'codigo_barras': '00190000090321583700005162579170188490000003000'}
        else:
            resultado_qrcode = run.emitir_qr_code(dados)
            
        return resultado_qrcode

    def emitir_qr_code(self, dados):
        
        valor_qr_code = dados['valor_qrcode']
        self.chrome_driver.get(self.urls['qr_code_cobranca'])

        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/ul/li[1]/div', By.XPATH)
        
        self.act.enviar_texto('//*[@id="contact-document"]', dados['cpf'], By.XPATH)
        self.act.enviar_texto('//*[@id="contact-full-name"]', dados['nome_completo']+'_'+str(dados['idTransacao'])+'_', By.XPATH)
        
        
        try:                           
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/form/button', By.XPATH)
        except:
            self.act.clicar_elemento('//*[@id="single-spa-application:@cora/bankslip"]/div/main/form/button', By.XPATH)   

        try:
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/ul/li[1]', By.XPATH)
        except:
            self.act.clicar_elemento('//*[@id="single-spa-application:@cora/bankslip"]/div/main/div[1]/ul/li[1]/div', By.XPATH) 


        self.act.enviar_texto('//*[@id="bankslip-amount"]', valor_qr_code,By.XPATH)
        self.act.enviar_texto('//*[@id="bankslip-name"]',str(dados['cpf'])+'_'+str(dados['idPessoa'])+'_'+str(dados['idTransacao'])+'_'+valor_qr_code, By.XPATH)
        self.act.enviar_texto('//*[@id="bankslip-description"]','uconecte_acreditar', By.XPATH)

        #confirmando nao enviar email, nao relizar cobranca
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/form/button',By.XPATH)
        #self.act.clicar_elemento('/html/body/div[1]/div/main/form/button', By.XPATH) 
        #self.act.clicar_elemento('/html/body/div[1]/div/main/form/button', By.XPATH)
        
              
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/form/button', By.XPATH)

        sleep(1)
        #finalizando confirmacaoo /html/body/div[1]/div/main/div[1]/div/button        
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/form/button', By.XPATH)

        #escolhendocriar boleto com pix 
        #pdb.set_trace()
        sleep(0.5)
        self.act.clicar_elemento('/html/body/div[1]/div/main/div/section/form/div/div/div[1]/label', By.XPATH)
        #self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/section/form/div/div/div[1]/label', By.XPATH)

        #continuar
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/section/form/button', By.XPATH)

        #confirmacao final
        sleep(0.5)
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/button[1]', By.XPATH)

        rec = 0        
        while self.act.quantidade_elemento('/html/body/div[1]/div/main/div[1]/div/div/button',By.XPATH) == 0:
            print('Aguardando download do contrato...') 
            rec +=1
            if(rec > 50):
                return False
            else:
                print('Tentativa: '+str(rec))
            sleep(1)

        #define pasta para download do pdf
        self.download_path = PATHS.project_path()+f"{self.sl}cora{self.sl}pix_boleto{self.sl}"+str(dados['idPessoa'])

        try:
            os.makedirs(self.download_path,0o777)
        except:
            pass

        self.driver.command_executor._commands['send_command'] = ('POST', '/session/$sessionId/chromium/send_command')
        
        params = {'cmd': 'Page.setDownloadBehavior','params': { 'behavior': 'allow', 'downloadPath': self.download_path}}
        self.driver.execute("send_command", params)

        # #dowload pdf
        self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div/button', By.XPATH)

        rec = 0
        while len(os.listdir(self.download_path)) == 0:
            print('Aguardando download...')
            rec +=1
            if(rec > 50):
                return False
            else:
                print('Tentativa: '+str(rec))
            sleep(0.5)

        self.nome_arquivo = os.listdir(self.download_path)[0]
        self.arquivo = self.download_path + self.sl + self.nome_arquivo
        
        #retorna imagem base64
        retorno_imagem = self.retirar_imagens_pdf()
        
        if(retorno_imagem['retorno_imagem'] == True):
            retorno_imagem['codigo_barras'] = self.act.obter_atributo('/html/body/div[1]/div/main/div[1]/div/div/div[4]','data-clipboard-text', By.XPATH)
        else:
            retorno_imagem['codigo_barras'] = ''

        #remove arquivos e pasta
        deleta_todos_arquivos(self.download_path)
        os.rmdir(self.download_path)

        return retorno_imagem

    def retirar_imagens_pdf(self):
        retorno = {'retorno_imagem': False, 'imagem_base64': ''}

        # open the file
        pdf_file = fitz.open(self.arquivo)

        for page_index in range(len(pdf_file)):
    
            # get the page itself
            page = pdf_file[page_index]
            image_list = page.get_images()
              
            # printing number of images found in this page
            # if not image_list:
            #     print(f"Encontrou {len(image_list)} imagens na página {page_index}")
            # else:
            #     print("Sem imagens", page_index)
            #     return {'retorno_imagem': False, 'imagem_base_64': ''}

            for image_index, img in enumerate(page.get_images(), start=1):
                
                # get the XREF of the image
                xref = img[0]                
                  
                # extrai bytes da imagem
                base_image = pdf_file.extract_image(xref)

                if(base_image['width'] != base_image['height']):
                    continue

                image_bytes = base_image["image"]
                  
                # pega imagem em bytes
                image_ext = base_image["ext"]

                #decodifica imagem base 64
                imagem_base64 = base64.b64encode(image_bytes)

                image = Image.open(io.BytesIO(image_bytes))
                result = decode(image)

                pix_cc = ''
                for i in result:
                    pix_cc = i.data.decode("utf-8")

                retorno = {'retorno_imagem': True, 'imagem_base64': imagem_base64, 'pix_cc' : pix_cc}
                #image.save(self.download_path+"\\"+str(xref)+'.'+base_image["ext"])
                #pdf_base64 = convert_file_base_64(self.path + f[0])

        return retorno

    def emitir_qr_code_fila(self):

        self.verificar_loading()       
        print('Inciando sincronização...')
        status_a_consultar = self.dados.get_ades()[1:]

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print('emitir qr code')

    @classmethod
    def sincronizar(self, driver: Chrome):        
        run = ConsultaEmissoes(driver)

        try:
            run.sincronizar_pagamentos()
            run.agendar_pagamentos()
            return True
        
        except TimeoutException as e:
            print('Entrou no exception Timeout')
            return False

        except StaleElementReferenceException as e:
            print('Erro de elemento não estar na pagina...')
            return False

        except WebDriverException as e:
            print('Erro Web Driver...')
            return False

    def sincronizar_pagamentos(self):     

        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        pagamentos = self.dados.get_pagamentos_acreditar()  

        if(len(pagamentos['consulta']) == 0):
            print('Nenhum pagamento para sincronizar')
            return True 
        
        for pagamento in pagamentos['consulta']: 
            #marca inicio da execucao
            inicio_execucao = time.time()

            id_transacao = pagamento['idTransacao']
            pagamento['dataTransacao'] = datetime.strptime(pagamento['dataTransacao'],'%Y-%m-%d %H:%M:%S').strftime("%d/%m/%Y")

            #########################################TESTE########################################
            # pagamento['idTransacao'] = '1262'
            # pagamento['dataTransacao'] = "20/12/2021"
            # pagamento['qrcode'] = ''
            # pagamento['cpf'] = '06050694680'
            # pagamento['valor'] = '20.00'
            #########################################TESTE########################################

            print('Verificando transacao: ' + str(id_transacao))  

            #iniciando a consulta                 
            self.iniciar_consulta()

            #preenchendo o form 
            retorno = self.preencher_formulario_busca(pagamento, True)  
            
            if retorno == False:
                print('XXXXXXXXXXXXXXX NADA ENCONTRADO XXXXXXXXXXXXXXXXXX')
                #marca fim da execucao
                print('Tempo de execucao: ' + str(int(time.time() - inicio_execucao)))
                continue  

            retorno = self.aguardar_loading_sincronizar(True)  

            if retorno == False:
                print('XXXXXXXXXXXXXXX NADA ENCONTRADO XXXXXXXXXXXXXXXXXX')
                #marca fim da execucao
                print('Tempo de execucao: ' + str(int(time.time() - inicio_execucao)))
                continue  


            
            #verifica transacoes recebidas no cpf informado retira 2 pois tem 2 tr vazios     
            try:       
                numero_transacoes_encontradas = len(self.act.retornar_elementos(f'/html/body/div[1]/div/main/div[1]/div/table/tbody/tr', By.XPATH))
            except:
                numero_transacoes_encontradas = len(self.act.retornar_elementos(f'/html/body/div[1]/div/main/div[1]/table/tbody[1]/tr', By.XPATH))
            
            for indice in range(2,numero_transacoes_encontradas):

                print('Verificando linha de transação...' + str(indice - 1))

                if(indice - 1) > 4:
                    print('Pulando busca de transacao')
                    continue


                try:
                    transacoes = self.act.retornar_elementos(f'/html/body/div[1]/div/main/div[1]/div/table/tbody[1]/tr[{indice}]', By.XPATH)
                except:
                    try:
                        transacoes = self.act.retornar_elementos(f'/html/body/div[1]/div/main/div[1]/table/tbody[1]/tr[{indice}]', By.XPATH)
                    except:
                        continue

                for transacao in transacoes: 

                    print('Encontrando transacao...')
                    
                    encontrar_transacao = self.encontrar_transacao(transacao, pagamento, indice)
                    if encontrar_transacao == 1:
                        break
                    elif encontrar_transacao == 2:
                        continue
                    elif encontrar_transacao == 3:
                        if(indice < numero_transacoes_encontradas - 1):
                            print('Reiniciando a consulta;')
                            self.iniciar_consulta()
                            self.preencher_formulario_busca(pagamento)
                        break

                if(encontrar_transacao == 1):
                    break

                print('Passando para proxima linha...')
            print(f'Finalizada confirmação de transação {id_transacao} para próxima...')

            #marca fim da execucao
            print('Tempo de execucao: ' + str(int(time.time() - inicio_execucao))) 

        return True

    def iniciar_consulta(self):
        #atualiza pagina 
        self.chrome_driver.get(self.urls['gestao_pagamentos'])
        self.aguardar_loading_sincronizar()

        #clicar em recebidos retirado ganha 5 segundos
        #self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[3]/ul/li[4]', By.XPATH)
        #self.aguardar_loading_sincronizar()

    def preencher_formulario_busca(self, pagamento, verificar_resultado = False):     
        self.act.enviar_texto('//*[@id="search-bankslip"]',"_"+str(pagamento['idTransacao'])+"_", By.XPATH)

        if self.aguardar_loading_sincronizar(verificar_resultado) == False:
            return False

        # self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[1]/div/div/button', By.XPATH)
        
        # self.aguardar_janela_filtro_data()
        # sleep(1)
        # self.act.enviar_texto('//*[@id="start-date"]',pagamento['dataTransacao'], By.XPATH)
        # sleep(1)
        # self.act.enviar_texto('//*[@id="end-date"]',datetime.now().strftime("%d/%m/%Y"), By.XPATH)
        # self.act.hover_e_clique('//*[@id="start-date"]', By.XPATH)
        # sleep(1)
        # self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[1]/div/div[2]/div/div/div[5]/button', By.XPATH)      

    def encontrar_transacao(self, transacao, pagamento, indice):
        if('Recebido' in transacao.text):         
            valor_boleto_cora =  str("{:.2f}".format(formatar_moeda(transacao.text.split('R$ ')[-1])))
            valor_pagamento_uconecte = pagamento['valor']           
            if(valor_boleto_cora == valor_pagamento_uconecte):                       
                transacao.click()                        
                self.aguardar_loading_detalhes_boleto()   
                try:                     
                    #"/html/body/div[1]/div/main/div[1]/div[4]/div[1]"
                    try:                                    
                        id_transacao = self.act.obter_texto('//*[@id="root"]/div/main/div[1]/div/div[4]/div[1]',By.XPATH).split('_')[1]
                    except:
                        id_transacao = self.act.obter_texto('//*[@id="root"]/div/main/div[1]/div[4]/div[1]',By.XPATH).split('_')[1]
                except:
                    id_transacao = '0'
                if(str(pagamento['idTransacao']) == id_transacao):
                    print('Transacao encontrada e atualizada... Carregando proximo cliente')
                    print('TODO VVVVVVVVVVVVVVVVVVVVVVV ENCONTRADO VVVVVVVVVVVVVVVVVVVVVVV')
                    
                    self.dados.post_dados_consultados({"idTransacao": id_transacao, "valor":valor_boleto_cora})
                    return 1
                else: 
                    print('Reiniciando a consulta por não achar o id de transacao igual: uConecte: '+ str(pagamento['idTransacao']) + ' - Sistema: ' + id_transacao)
                    return 3
            else:
                print('Não achou valor igual') 
                return 2
        else:
            print('Não achou recebido na tr...')
            return 2

    def aguardar_loading_sincronizar(self, verificar_resultado = False):
        rec = 0
        texto = ''
        sleep(0.2)
        while texto == '':
            try:
                texto = self.act.obter_texto('/html/body/div[1]/div/main/div[1]/div/div[1]/div[3]/ul/li[1]',By.XPATH)
            except:                
                texto = ''

            try:
                if(verificar_resultado == True):
                    print('Verificando resultado da busca automatica do cpf')
                    if('Nenhum resultado encontrado' in self.act.obter_texto('/html/body/div[1]/div/main/div[1]/div/div[2]/h3', By.XPATH)):
                        return False
            except:                
                pass

            print('Aguardando loading...') 
            rec +=1
            if(rec > 7):
                # try:
                #     print('Tentando renovar sessão')
                #     self.act.clicar_elemento('/html/body/div[1]/div/main/div[2]/div/div/div[2]/button[2]', By.XPATH)
                # except:
                #     print('Tentando deslogar')
                #     self.act.clicar_elemento('/html/body/div[1]/div/nav/div/ul[3]/li/a/div', By.XPATH)
                #     pass
                self.driver.quit()
                return False
            else:
                print('Aguardando... '+str(rec))
            sleep(1)
        return True

    def aguardar_loading_detalhes_boleto(self):
        rec = 0
        try:
            self.act.obter_texto('//*[@id="root"]/div/main/div[1]/div/div[4]/div[1]', By.XPATH)
            loc = '//*[@id="root"]/div/main/div[1]/div/div[4]/div[1]'
        except:
            loc = '//*[@id="root"]/div/main/div[1]/div[4]/div[1]'

        while self.act.obter_texto(loc,By.XPATH) == '':
            print('Aguardando loading detalhes...') 
            rec +=1
            if(rec > 7):
                return False
            else:
                print('Aguardando... '+str(rec))
            sleep(1)

    def aguardar_janela_filtro_data(self):
        rec = 0
        while self.act.quantidade_elemento('/html/body/div[1]/div/main/div[1]/div/div[1]/div/div[2]/div/div',By.XPATH) == 0:
            print('Aguardando janela abrir...') 
            rec +=1
            if(rec > 7):
                return False
            else:
                print('Aguardando janela de filtro... '+str(rec))
            sleep(1)

    def agendar_pagamentos(self):  
        saques = {}   

        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        saques = self.dados.get_saques_acreditar()  

        if('consulta' in saques and len(saques['consulta']) == 0):
            print('Nenhum saque para sincronizar')
            return True 


        self.chrome_driver.get(self.urls['transferencia_pix'])
        sleep(1)
        self.chrome_driver.get(self.urls['transferencia_pix'])
        
        self.aguardar_loading_xpath('/html/body/div[1]/div/main/div[1]/section/h1', 'Aguardando área de transferência abrir...')

        for saque in saques['consulta']: 
            #marca inicio da execucao
            inicio_execucao = time.time()
            id_transacao = saque['idTransacao'];

            #agendar transacao
            print('Inciando transação: '+id_transacao)

            if(saque['valor'] == '0.00'):
                saque['valor'] = '0.01'
            
            #atualiza pagina             
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/section/ul/li[1]/div[2]/span', By.XPATH)
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/ul/li/div/div[2]/span', By.XPATH)
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[2]/ul/li[2]/span', By.XPATH)
            
            self.act.enviar_texto('//*[@id="transfer-key"]',saque['cpf'], By.XPATH)
            self.act.enviar_texto('//*[@id="transfer-amount"]',saque['valor'], By.XPATH)
            self.act.enviar_texto('//*[@id="bankslip-description"]','cpf:' + str(saque['cpf']) + ';retirada_numero:'+ str(saque['idTransacao']), By.XPATH) 

            try:
                mensagem_erro_cpf = self.act.obter_texto('/html/body/div[1]/div/main/div[1]/div/div[2]/div[2]/div/div[2]', By.XPATH)
            except:
                mensagem_erro_cpf = ''
                pass 
            
            if('CPF inválido' in mensagem_erro_cpf):
                self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[2]/div[2]/div/div[1]/div/button', By.XPATH)
                self.act.enviar_texto('//*[@id="transfer-key"]',saque['cpf'], By.XPATH)

            
            #x, y = find_elements_on_screen(self.imagem_continuar)
            #pyautogui.click(x, y) 
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/div[2]/button', By.XPATH)             
            self.aguardar_loading_xpath('/html/body/div[1]/div/main/div[1]/div/h2', 'Area revisao tranferencia')  

            sleep(1)

            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/button', By.XPATH)
            
            self.aguardar_loading_xpath('/html/body/div[1]/div/main/div[1]/div/h1', 'Area confirmar transacao pendente')              
            self.act.clicar_elemento('/html/body/div[1]/div/main/div[1]/div/button[1]', By.XPATH)

            self.aguardar_loading_xpath('/html/body/div[1]/div/main/div[1]/section/h1', 'Aguardando área de transferência novamente abrir...')
            self.dados.post_dados_consultados({"idTransacao": id_transacao})
            
            #marca fim da execucao
            print('Tempo de execucao: ' + str(int(time.time() - inicio_execucao))) 
            print('-------------------FIM TRANSACAO-----------------')

        return True

    def aguardar_loading_xpath(self, xpath, texto_area):
        rec = 0
        texto = ''
        while texto == '':
            try:
                texto = self.act.obter_texto(xpath,By.XPATH)
            except:                
                texto = ''

            print('Aguardando loading... ' + texto_area) 
            rec +=1
            if(rec > 7):
                return False
            else:
                print('Aguardando... '+str(rec))
            sleep(0.5)
        return True

