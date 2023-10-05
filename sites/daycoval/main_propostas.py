import sys, pdb, json, re, unidecode, os, shutil
#sys.path.append('../../')
from selenium.webdriver.common.keys import Keys
from sites.baseRobos.core.helpers import definir_nome_robo
from datetime import datetime
from dados.APIGetSource import APIDataSource
from sites.baseRobos.core.helpers import formatar_moeda, convert_file_base_64
from sites.baseRobos.manager import Manager
from selenium import webdriver
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sites.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from time import sleep, strftime
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.helpers import deleta_todos_arquivos,apagar_arquivos_pasta,apagar_um_arquivo
from sites.baseRobos.core.data_helpers import buscar_documentos_contrato, download      

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Proposta_Daycoval():
    def __init__(self):
        self.path_pdf = '/home/gustavo/Desktop/automacao-python/sites/daycoval/pdfs/'
        self.path_documentos = '/home/gustavo/Desktop/automacao-python/sites/daycoval/documentos/'
        self.path_arquivo_zip = '/home/gustavo/Desktop/automacao-python/sites/daycoval/fotos.zip'
        #self.path_pdf = 'C:\\wamp64\\www\\automacao-python\\sites\\daycoval\\pdfs\\'
        #self.path_documentos = 'C:\\wamp64\\www\\automacao-python\\sites\\daycoval\\documentos\\'
        #self.path_arquivo_zip = 'C:\\wamp64\\www\\automacao-python\\sites\\daycoval\\fotos.zip'
        self.login = {'usuario' : 'DCM-UCONECTE', 'senha' : 'Tim909mca@'}
        definir_nome_robo("Proposta Daycoval")

    def main(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('prefs', {
            "selectfile.last_directory": self.path_documentos, 
        })
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/")
        sleep(2)
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/")
        self.act = SeleniumActions(self.driver)
        self.act.enviar_texto('//*[@id="FORMULARIO"]/table[1]/tbody/tr[1]/td[3]/input', self.login['usuario'], By.XPATH)
        self.act.enviar_texto('//*[@id="FORMULARIO"]/table[1]/tbody/tr[3]/td[3]/input', self.login['senha'], By.XPATH)
        sleep(1)
        self.act.clicar_elemento('//*[@id="FORMULARIO"]/table[1]/tbody/tr[5]/td[3]/input[2]', By.XPATH)
        self.mudar_link_consulta()


    def mudar_link_consulta(self):
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/view/CJT05415.do?pmtr=xllZoBKWzRbga4GzzDEirSmGgeHTUzE0PwNqAN"
                        + "JMBXCUgOHXyTjCS7j0%2BjA7u%2F48bNL8N7so6BcPfFCNrHLR%2FHzjsGkhQHS2u94cDQQYO3FErSzx%2BQXAEDRutuhCH%2F4zNRoWhvGxJeMh7%2FYG3NUK%2Fk1IbQEK1FGjAavztBdJdOI%3D")
        self.realizar_busca()
        #self.anexar_documentos()
        #self.realizar_sincronizacao()
        sleep(600)
        print('Aguardando 10 minutos...')
        self.driver.quit()       
        

    def mudar_link_sincronizacao(self):
        self.driver.get("https://daycovalimovel.com.br:8443/daycoval/view/CJT05596.do?pmtr=xllZoBKWzRbga4GzzDEirSQ4oh90RPANS"
                        + "kG3O%2FFkE3%2Bgb9Y%2Fjy5oWXYAbVW2X%2F2351J7AfhclRSrNXp8l074%2FBbhEnUOSgSGZX9gaI98NL6cd95trWzLw2TAP3jF5yZUxRG7EfJbKlEhOPS7hKgyVYffgibUq16EdRFM4Nnzx1M%3D")

    def tipo_imovel(self, imovel):
        switcher = {
            "Residencial - Casa": 1,
            "Residencial - Apartamento" : 2,
            "Comercial - Loja" : 3,
            "Comercial - Sala Comercial" : 4,
            "Misto - Comercial / Residencia" : 5,
            "Imovel Veraneio" : 6,
            "Terreno + Construcao Concluida" : 7,
        }
        opcao = switcher.get(imovel, "Erro imovel invalido")
        return opcao
    
    def apagar_campo(self, xpath):
        self.act.clicar_elemento(xpath, By.XPATH)
        self.driver.find_element_by_xpath(xpath).send_keys(Keys.DELETE)
   
    def loading(self):
        carregou = False
        while carregou is False:
            try:
                self.act.manusear_alerta('aceitar')
            except:
                pass

            try:
                self.driver.find_element_by_xpath('/html/body/div[9]/h5/img')                
            except NoSuchElementException:
                carregou = True

    
    def redundancia_insercao(self, proposta):
        print(">>>>>>>>>>>>>>>TENTATIVA DE EXTRAIR O NUM DA SIMULACAO<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        ade_extraida_site = self.extrair_dados(proposta)
        if(ade_extraida_site):
            print(ade_extraida_site)
            self.completar_dados_pdf(proposta)
            pdf_base64 = convert_file_base_64(self.path_pdf + 'MergedFiles.pdf')
            payload = {
                "codigoContrato" : proposta['codigoContrato'], 
                "codigoCliente":  proposta['codigoCliente'],
                "base64" : pdf_base64, 
                "banco" : "daycoval", 
                "key" : "f689f1e12a0399fba803cb2365fc362f",
                "ade": ade_extraida_site
            }
            #POST VEM AQUI --> PDF E ADE EXTRAIDA
            response = APIDataSource().post_request_v2('enviar-pdf-ade-daycoval', payload)
            print(response)
        else:
            if(ade_extraida_site != 'renda_insuficiente'):
                self.redundancia_insercao(proposta)
                sleep(60)

    def anexar_documentos(self):        

        response = APIDataSource().get_request('daycoval_anexar_documentos').text
        dados = json.loads(response)

        if dados[0]['retorno'] == 0:
            print('Nenhum documento para enviar...')
            return
        for i in dados[1:]:
            #apagando arquivos
            print('Removendo arquivos das pastas')
            try:
                deleta_todos_arquivos(self.path_documentos)
                deleta_todos_arquivos(self.path_documentos+'fotos')
                apagar_um_arquivo('/home/gustavo/Desktop/automacao-python/sites/daycoval/identidade.zip')
                apagar_um_arquivo(self.path_arquivo_zip)
            except Exception as e:
                print(e)
            # Fluxo de Documentos
            self.driver.get('https://daycovalimovel.com.br:8443/daycoval/view/CJT05596.do?pmtr=xllZoBKWzRbga4GzzDEirSQ4oh90RPANSkG3O%2FFkE3%2Bgb9Y%2Fjy5oWXYAbVW2X%2F2351J7AfhclRSrNXp8l074%2FBbhEnUOSgSGZX9gaI98NL6cd95trWzLw2TAP3jF5yZUxRG7EfJbKlEhOPS7hKgyVYffgibUq16EdRFM4Nnzx1M%3D')
            # Procurar pelo cpf
            self.act.enviar_texto_intervalado('//*[@id="nm_cgcecpf"]', i['cpf'], By.XPATH, delay=0.4)
            # Clicar em procurar
            self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
            # Pegar status de todas as propostas
            #dado_limpo = re.findall("[0-9]", dado_bruto)
            #numero_simulacao = ''.join([str(i) for i in dado_limpo])
            qtd_propostas = self.act.quantidade_elemento('//*[@id="to"]/tbody/tr', By.XPATH)
            for j in range(1, qtd_propostas + 1):
                # Status
                if self.act.obter_texto(f'//*[@id="to"]/tbody/tr[{j}]/td[5]', By.XPATH) == 'Aguardando Documentação - Fase de Crédito':
                    # Clica nela 
                    self.act.clicar_elemento(f'//*[@id="to"]/tbody/tr[{j}]/td[1]/table/tbody/tr/td/input[22]', By.XPATH)
                    break
            # Clica no botão Documentos
            self.act.clicar_elemento('//*[@id="ENT"]', By.XPATH)
            # Pega url do documento
            url = buscar_documentos_contrato(i['codigoCon'])
            # Baixa o Documento
            
            switch_documentos = {
                1: "Documento de Identificação (RG / RNE / HABILITAÇÃO)",
                2: None,
                3: "Comprovante de Residência",
                4: "Comprovante de Renda",
                5: 'Proposta de Financiamento - BANCO DAYCOVAL',
                6: "Aviso Recibo do IPTU e/ou Documento onde conste Área do Terreno / Construída (capa do carnê)",
                7: "FORMULÁRIO - DPS - Declaração Pessoal de Saúde",
                8: None,
                9: None,   
                10:None,
                11:None
            }
            comprimiu = 0
            counter = 1
            for j in url['arquivos']:
                # Muda o nome do arquivo para baixar
                # Anexar
                extensao = '.pdf'
                if('.jpg?' in j or '.jpeg?' in j):
                    extensao = '.jpg'

                qtd_elementos = self.act.quantidade_elemento('//*[@id="to"]/tbody/tr', By.XPATH)
                # Se for foto imovel o arquivo juntar tudo em um .zip 
                if "FOTO" in j.upper() and "IMOVEL" in j.upper() and not counter == 5:
                    download(j, self.path_documentos + 'fotos/'f'Documento_{counter}{extensao}')
                    print(f'comprimiu {counter}')
                    comprimiu_foto = 1
                elif "RG" and "FRENTE" in j.upper() or "RG" and "VERSO" in j.upper()  or 'CoNJUGE' in j.upper() or 'CASAMENTO' in j.upper():
                    print(j)
                    download(j, self.path_documentos + 'zip_identidade/'f'Documento_{counter}{extensao}')
                    comprimiu = 2
                else:
                    # Faz o Download do Arquivo
                    download(j, self.path_documentos + f'Documento_{counter}{extensao}')
                counter += 1
            # Data para preencher no site
            data = strftime('%d%m%Y')
            
            # Qtd de arquivos
            for j in range(1, len(url['arquivos'])+1):                
                extensao = '.pdf'
                if('.jpg?' in url['arquivos'][j-1] or '.jpeg?' in url['arquivos'][j-1]):
                    extensao = '.jpg'
                for k in range(1, qtd_elementos + 1):
                    # Verifica o nome do arquivo no site para anexar o arquivo correspondente
                    if switch_documentos[j] == self.act.obter_texto(f'//*[@id="to"]/tbody/tr[{k}]/td[3]', By.XPATH):
                        if comprimiu == 2 and switch_documentos[j] == 'Documento de Identificação (RG / RNE / HABILITAÇÃO)':
                            shutil.make_archive("identidade", 'zip', self.path_documentos + 'zip_identidade/')
                            # seleciona o rg
                            self.act.clicar_elemento(f'//*[@id="to"]/tbody/tr[13]/td[1]', By.XPATH)
                            # Data
                            sleep(1)
                            self.act.enviar_texto('//*[@id="dt_recorig"]', data, By.XPATH)
                            # Clica para carregar
                            self.act.clicar_elemento('//*[@id="control_fl_arquivo"]/input', By.XPATH)
                            sleep(2)
                            # Manda o path do arquivo + nome arquivo
                            # Acha o id to input de arquivos
                            upload = self.driver.find_element_by_id("fl_arquivoFormFile")
                            upload.send_keys('/home/gustavo/Desktop/automacao-python/sites/daycoval/identidade.zip')
                            sleep(1)
                            # Clica em Alterar para salvar o upload do arquivo
                            self.act.clicar_elemento('//*[@id="ALT"]', By.XPATH)
                            continue
                        # Anexa o arquivo correto
                        print(j, self.act.obter_texto(f'//*[@id="to"]/tbody/tr[{k}]/td[3]', By.XPATH))
                        # Seleciona ele
                        self.act.clicar_elemento(f'//*[@id="to"]/tbody/tr[{k}]/td[1]', By.XPATH)
                        # Coloca a data
                        sleep(1)
                        self.act.enviar_texto('//*[@id="dt_recorig"]', data, By.XPATH)
                        # Clica para carregar
                        self.act.clicar_elemento('//*[@id="control_fl_arquivo"]/input', By.XPATH)
                        sleep(2)
                        # Manda o path do arquivo + nome arquivo
                        # Acha o id to input de arquivos
                        upload = self.driver.find_element_by_id("fl_arquivoFormFile")
                        upload.send_keys(self.path_documentos + f'Documento_{j}{extensao}')
                        sleep(1)
                        # Clica em Alterar para salvar o upload do arquivo
                        self.act.clicar_elemento('//*[@id="ALT"]', By.XPATH)

            # Anexar o zip das fotos no campo correto
            if comprimiu_foto == 1:
                shutil.make_archive("fotos", 'zip', self.path_documentos + 'fotos/')
                self.act.clicar_elemento('//*[@id="to"]/tbody/tr[6]/td[1]', By.XPATH)
                self.act.enviar_texto('//*[@id="dt_recorig"]', data, By.XPATH)
                self.act.clicar_elemento('//*[@id="control_fl_arquivo"]/input', By.XPATH)
                # Manda o path do arquivo + nome arquivo
                upload = self.driver.find_element_by_id("fl_arquivoFormFile")
                upload.send_keys('/home/gustavo/Desktop/automacao-python/sites/daycoval/fotos.zip')
                # Clica em Alterar para salvar o upload do arquivo
                self.act.clicar_elemento('//*[@id="ALT"]', By.XPATH)
                comprimiu_foto = 0

            num_proposta = self.act.obter_atributo('//*[@id="dg_nm_solcred"]', 'value', By.XPATH)
            payload = {
                "statusPropostaBanco": "DOCUMENTOS ANEXADOS NO BANCO",
                "observacaoDetalhadaBanco": "",
                'numero_proposta': num_proposta,
                "codigoCon": i['codigoCon'],
                "ade": i['ade'],
                "key": "f689f1e12a0399fba803cb2365fc362f"
            }
            response = APIDataSource().post_request_v2('enviar-dados-sincronizacao-daycoval', payload)


            

    # INSERÇÂO
    def realizar_busca(self):
        print('INSERCAO')
        response = APIDataSource().get_request("todas-propostas-daycoval-proposta")
        todas_propostas = json.loads(response.text)
        for contrato in todas_propostas['contratos']:
            codigo_con = ['codigo', contrato['codigo_con']]
            response = APIDataSource().get_request("daycoval_propostas_imoveis_real", edit=codigo_con) 
            dados_proposta = json.loads(response.text)
            if dados_proposta['tipo'] != 'success':
                return             
            
            proposta = dados_proposta['contrato'] 
            print(proposta)
            #Testa para ver se a proposta foi inserida
            self.driver.get("https://daycovalimovel.com.br:8443/daycoval/view/CJT05596.do?pmtr=xllZoBKWzRbga4GzzDEirSQ4oh90RPANSkG3O%2FFkE3%2Bgb9Y%2Fjy5oWXYAbVW2X%2F2351J7AfhclRSrNXp8l074%2FBbhEnUOSgSGZX9gaI98NL6cd95trWzLw2TAP3jF5yZUxRG7EfJbKlEhOPS7hKgyVYffgibUq16EdRFM4Nnzx1M%3D")
            # procura pelo cpf
            self.act.enviar_texto('//*[@id="nm_cgcecpf"]', proposta['cpf'], By.XPATH)
            # Registro não Encontrado
            try:
                self.act.clicar_elemento('/html/div[2]/div/div[2]/input', By.XPATH)
            except:
                pass
            self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)    
            try:
                texto = self.act.obter_texto('//*[@id="bloco2"]', By.XPATH)
                
                if texto.split("\n")[-1] != 'Nenhum item encontrado.' and 'Propostas Recusadas' not in texto.split("\n")[-1]:
                    
                    ade_extraida_site = self.extrair_dados(proposta)
                    self.completar_dados_pdf(proposta)
                    pdf_base64 = convert_file_base_64(self.path_pdf + 'MergedFiles.pdf')
                    payload = {
                        "codigoContrato" : proposta['codigoContrato'], 
                        "codigoCliente":  proposta['codigoCliente'],
                        "base64" : pdf_base64, 
                        "banco" : "daycoval", 
                        "key" : "f689f1e12a0399fba803cb2365fc362f",
                        "ade": ade_extraida_site
                    }

                    #POST VEM AQUI --> PDF E ADE EXTRAIDA
                    response = APIDataSource().post_request_v2('enviar-pdf-ade-daycoval', payload)
                    print(response)
                    continue
            except:
                pass
            try:
                self.driver.get("https://daycovalimovel.com.br:8443/daycoval/view/CJT05415.do?pmtr=xllZoBKWzRbga4GzzDEirSmGgeHTUzE0PwNqAN"
                        + "JMBXCUgOHXyTjCS7j0%2BjA7u%2F48bNL8N7so6BcPfFCNrHLR%2FHzjsGkhQHS2u94cDQQYO3FErSzx%2BQXAEDRutuhCH%2F4zNRoWhvGxJeMh7%2FYG3NUK%2Fk1IbQEK1FGjAavztBdJdOI%3D")
                self.act.clicar_elemento('//*[@id="cd_tusobem_chzn"]/a/div/b', By.XPATH)
            except:
                self.driver.quit()
                self.main()
            self.act.enviar_texto('//*[@id="cd_tusobem_chzn"]/div/div/input', proposta['dadosImovelGarantia']['tipoImovel'], By.XPATH)
            self.act.press_enter('//*[@id="cd_tusobem_chzn"]/div/div/input', By.XPATH)
            self.apagar_campo('//*[@id="vl_totabem"]')
            self.act.enviar_texto('//*[@id="vl_totabem"]', proposta['dadosImovelGarantia']['valorImovel'], By.XPATH)
            self.apagar_campo('//*[@id="vl_princip"]')
            self.act.enviar_texto('//*[@id="vl_princip"]', proposta['valorContrato'], By.XPATH)
            self.act.enviar_texto('//*[@id="dt_nascipr"]', proposta['dataNascimento'], By.XPATH)
            sleep(1)
            self.act.clicar_elemento('//*[@id="lg_bemquit"]', By.XPATH)
            sleep(1)
            self.act.clicar_elemento('//*[@id="lg_bemquit"]', By.XPATH)
            sleep(1)
            # Prazo
            self.apagar_campo('//*[@id="qt_mesesop"]')
            self.act.enviar_texto('//*[@id="qt_mesesop"]', proposta['prazo'], By.XPATH, clear=True)
            try:
                self.act.hover_e_clique('//*[@id="CAL"]', By.XPATH)
                self.act.clicar_elemento("CAL", By.ID)
            except:
                pass
            self.loading()
            # Pegar nome produto
            quantidade_propostas = len(self.act.retornar_elementos('//*[@id="tg_conop"]',By.XPATH))

            print(proposta['outrosDadosOperacao']['tabela'])
            for i in range(1, quantidade_propostas):
                try:
                    produto = unidecode.unidecode(self.act.obter_texto(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[3]', By.XPATH))
                except:
                    break
                print(produto)
                if produto == proposta['outrosDadosOperacao']['tabela']:
                    numero_tr = i
                    break
            self.act.clicar_elemento(f'/html/body/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/form/div/div[8]/table/tbody/tr/td[4]/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[{numero_tr}]/td[3]', By.XPATH)
            self.act.clicar_elemento('//*[@id="GRV"]', By.XPATH) # PROSSEGUIOR COM A PROPOSTA
            ade_extraida_site = self.preencher_dados_imovel(proposta)

            if(ade_extraida_site):

                print(ade_extraida_site)

                self.completar_dados_pdf(proposta)
                pdf_base64 = convert_file_base_64(self.path_pdf + 'MergedFiles.pdf')
                payload = {
                    "codigoContrato" : proposta['codigoContrato'], 
                    "codigoCliente":  proposta['codigoCliente'],
                    "base64" : pdf_base64, 
                    "banco" : "daycoval", 
                    "key" : "f689f1e12a0399fba803cb2365fc362f",
                    "ade": ade_extraida_site
                }

                #POST VEM AQUI --> PDF E ADE EXTRAIDA
                response = APIDataSource().post_request_v2('enviar-pdf-ade-daycoval', payload)
                print(response)
            else:
                self.redundancia_insercao(proposta)
        
        print("----------ACABOU----------")
        return


    def mudar_link_sincronizacao_proposta(self):
        self.driver.get('https://daycovalimovel.com.br:8443/daycoval/view/CJT04602.do?pmtr=xllZoBKWzRbga4GzzDEirW6YcTn88Vt9Q9d9%2BU4XCAJ2AG1Vtl%2F9t9J882uncR1Kbm%2FDQMWv83yxGA8ZEW%2But3Au8gWx%2FWj615NlnbuCUOyjfGJ%2FUmqRlA%3D%3D')

    # SINCRONIZAÇÂO
    def realizar_sincronizacao(self):
        response = APIDataSource().get_request("pegar-dados-sincronizacao-daycoval")
        todas_propostas = json.loads(response.text)
        if todas_propostas[0]['mensagem'] == "Nada a atualizar.":
            print('Não tem na fiila de sincronização...')
            return
        
        for i in range(1, len(todas_propostas)):
            dados = todas_propostas[i]
            # Tente consultar pelo cpf
            try:
                self.mudar_link_sincronizacao_proposta()
                self.act.enviar_texto('//*[@id="nm_cgcecpf"]', dados[1], By.XPATH)
                sleep(1.5)
                self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
                self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
                sleep(1.5)
                try:
                    atividade = self.act.obter_texto('//*[@id="to"]/tbody/tr[1]/td[10]', By.XPATH)
                except:
                    atividade = 'Aguardando Análise do Banco'
                ade =  self.act.obter_texto('//*[@id="to"]/tbody/tr[1]/td[8]', By.XPATH)
                num_id = dados[-1]
                payload = {
                        'statusPropostaBanco': atividade,
                        'observacaoDetalhadaBanco': '',
                        'numero_proposta': ade,
                        'codigoCon': dados[2],
                        'ade': ade,
                        'key': 'f689f1e12a0399fba803cb2365fc362f'
                    }
            except:
                # Tente consultar pela ade
                self.mudar_link_sincronizacao()
                self.act.enviar_texto('//*[@id="ds_identif"]', dados[0], By.XPATH)
                self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
                try:
                    atividade = self.act.obter_texto('//*[@id="to"]/tbody/tr[1]/td[5]', By.XPATH)
                except:
                    self.act.enviar_texto('//*[@id="nm_cgcecpf"]', dados[1], By.XPATH)
                    self.driver.find_element_by_xpath('//*[@id="ds_identif"]').clear()
                    self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
                    atividade = self.act.obter_texto('//*[@id="to"]/tbody/tr[1]/td[5]', By.XPATH)
                dado_bruto = self.act.obter_texto('//*[@id="to"]/tbody/tr[1]/td[6]', By.XPATH)
                num_id_arr = re.findall("[0-9]", dado_bruto)

                if('Simulação' in atividade):
                    num_id = ''.join(num_id_arr)
                payload = {
                    "statusPropostaBanco": atividade,
                    "observacaoDetalhadaBanco": '',
                    "numero_proposta": num_id,
                    "codigoCon": dados[2],
                    "ade": num_id,
                    "key": "f689f1e12a0399fba803cb2365fc362f"
                }
            
            print(payload)
            response = APIDataSource().post_request_v2('enviar-dados-sincronizacao-daycoval', payload)
            print(response)
        return None


    def extrair_dados(self, proposta):
        print('Verificando erros...')
        try:
            texto_erro = self.act.obter_texto('//*[@id="control_message_error"]/td[3]', By.XPATH)
            if('Renda insuficiente para o valor' in texto_erro):
                print('Renda insuficiente....')
                Uconecte().atualizar_contrato(proposta['codigoContrato'], {
                'observacao': 'Renda insuficiente para o valor /prazo pretendido. Ajustar as condições ou complementar com mais um proponente com renda.',
                'mensagem': 'Reprovado a Conferir'
                })
                return 'renda_insuficiente'
        except:
            pass
        self.driver.get('https://daycovalimovel.com.br:8443/daycoval/view/CJT05596.do?pmtr=xllZoBKWzRbga4GzzDEirSQ4oh90RPANSkG3O%2FFkE3%2Bgb9Y%2Fjy5oWXYAbVW2X'
                            + '%2F2351J7AfhclRSrNXp8l074%2FBbhEnUOSgSGZX9gaI98NL6cd95trWzLw2TAP3jF5yZUxRG7EfJbKlEhOPS7hKgyVYffgibUq16EdRFM4Nnzx1M%3D')
        self.loading()
        sleep(2)
        self.act.enviar_texto_intervalado('//*[@id="nm_cgcecpf"]', proposta['cpf'], By.XPATH, delay=0.4)
        self.loading()
        self.act.clicar_elemento('//*[@id="BUS"]', By.XPATH)
        self.act.clicar_elemento('//*[@id="to"]/tbody/tr[1]/td[1]/table/tbody/tr/td/input[22]', By.XPATH)
        dado_bruto = self.act.obter_valor('//*[@id="ds_identif"]', By.XPATH)
        dado_limpo = re.findall("[0-9]", dado_bruto)
        numero_simulacao = ''.join([str(i) for i in dado_limpo])
        return numero_simulacao


    def preencher_dados_proponente(self, proposta):
        # CEP
        self.act.enviar_texto('//*[@id="cd_ceposof"]', proposta['cep'], By.XPATH)
        # Tipo Logradouro
        if 'Rua' in proposta['logradouro']:
            # DROP-DOWN
            self.act.select_drop_down('//*[@id="cd_lograof"]', '32', By.XPATH)
        else:
            self.act.select_drop_down('//*[@id="cd_lograof"]', '4', By.XPATH)
        # Nome
        self.act.enviar_texto('//*[@id="no_nomprop"]', proposta['nome'], By.XPATH)
        # CPF
        sleep(1.5)
        self.act.enviar_texto_intervalado('//*[@id="nm_cpfprop"]', proposta['cpf'], By.XPATH, delay=0.4)
        # RG
        self.act.enviar_texto('//*[@id="nm_reggera"]', proposta['identidade'], By.XPATH)
        self.loading()
        self.act.enviar_texto('//*[@id="nm_reggera"]', proposta['identidade'], By.XPATH)
        try:
            self.act.enviar_texto('//*[@id="no_nomprop"]', proposta['nome'], By.XPATH)
        except:
            pass
        # MAIL
        self.act.enviar_texto('//*[@id="ds_emailcl"]', proposta['email'], By.XPATH)
        # DD
        self.act.enviar_texto('//*[@id="dd_telefof"]', proposta['dddCelular'], By.XPATH)
        # Telefone
        self.act.enviar_texto('//*[@id="nm_telefof"]', proposta['celular'], By.XPATH)
        # Celular
        self.act.enviar_texto('//*[@id="dd_celular"]', proposta['dddCelular'], By.XPATH)
        self.act.enviar_texto('//*[@id="nm_celular"]', proposta['celular'], By.XPATH)
        # profissao
        self.act.enviar_texto('//*[@id="no_profiss"]', proposta['outrosDadosPessoais']['profissao'], By.XPATH)
        # Renda
        self.act.enviar_texto('//*[@id="vl_rmsalar"]', proposta['outrosDadosPessoais']['renda'], By.XPATH)
        # Logradouro
        self.act.enviar_texto('//*[@id="ds_enderof"]', proposta['logradouro'], By.XPATH)
        self.act.enviar_texto('//*[@id="nm_numerof"]', proposta['numeroCasa'], By.XPATH)
        self.act.enviar_texto('//*[@id="ds_complof"]', proposta['complemento'], By.XPATH)
        self.act.enviar_texto('//*[@id="no_bairrof"]', proposta['bairro'], By.XPATH)
        self.act.enviar_texto('//*[@id="no_cidadof"]', proposta['cidade'], By.XPATH)
        self.act.select_drop_down('//*[@id="no_estadof"]', proposta['uf'], By.XPATH)
        sleep(2)
        self.act.clicar_elemento('//*[@id="ENV"]', By.XPATH)
        self.act.manusear_alerta('rejeitar')
        self.loading()
        return self.extrair_dados(proposta)
        

    def switch_estado(self, sigla_estado):
        estados = {
            "AC" : "Acre",
            "AL" : "Alagoas",
            "AP" : "Amapá",
            "AM" : "Amazonas",
            "BA" : "Bahia",
            "CE" : "Ceará",
            "DF" : "Distrito Federal",
            "ES" : "Espírito Santo",
            "GO" : "Goiás",
            "MA" : "Maranhão",
            "MT" : "Mato Grosso",
            "MS" : "Mato Grosso do Sul",
            "MG" : "Minas Gerais",
            "PA" : "Pará",
            "PB" : "Paraíba",
            "PR" : "Paraná",
            "PE" : "Pernambuco",
            "PI" : "Piauí",
            "RJ" : "Rio de Janeiro",
            "RN" : "Rio Grande do Norte",
            "RS" : "Rio Grande do Sul",
            "RO" : "Rondônia",
            "RR" : "Roraima",
            "SC" : "Santa Catarina",
            "SP" : "São Paulo",
            "SE" : "Sergipe",
            "TO" : "Tocantins"
        }
        if sigla_estado in estados:
            return estados[sigla_estado]


    def preencher_dados_imovel(self, proposta):
        ### Imovel ### 
        # cep
        self.act.enviar_texto('//*[@id="cd_ceposof_garan"]', proposta['dadosImovelGarantia']['cepImovel'], By.XPATH)
        if 'Rua' in proposta['dadosImovelGarantia']['logradouro']:
            # logradouro --> drop down
            try:
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.enviar_texto('//*[@id="cd_lograof_garan_chzn"]/div/div/input', 'RUA', By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.enviar_texto('//*[@id="cd_lograof_garan_chzn"]/div/div/input', 'RUA', By.XPATH)
        else:
            # logradouro --> drop down
            try:
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.enviar_texto('//*[@id="cd_lograof_garan_chzn"]/div/div/input', 'AVENIDA', By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="cd_lograof_garan_chzn"]/a', By.XPATH)
                self.act.enviar_texto('//*[@id="cd_lograof_garan_chzn"]/div/div/input', 'AVENIDA', By.XPATH)


        self.act.press_enter('//*[@id="cd_lograof_garan_chzn"]/div/div/input', By.XPATH)
            
        # texto logradouro 
        self.act.enviar_texto('//*[@id="ds_enderof_garan"]', proposta['dadosImovelGarantia']['logradouro'], By.XPATH)
        # numero
        self.act.enviar_texto('//*[@id="nm_numerof_garan"]',  proposta['dadosImovelGarantia']['numero'], By.XPATH)
        # complemento
        self.act.enviar_texto('//*[@id="ds_complof_garan"]',  proposta['dadosImovelGarantia']['complemento'], By.XPATH)
        # bairro
        self.act.enviar_texto('//*[@id="no_bairrof_garan"]',  proposta['dadosImovelGarantia']['bairro'], By.XPATH)
        # cidade
        self.act.enviar_texto('//*[@id="no_cidadof_garan"]', proposta['dadosImovelGarantia']['cidade'], By.XPATH)
        # Estado
        self.act.clicar_elemento('//*[@id="no_estadof_garan_chzn"]/a', By.XPATH)
        estado = self.switch_estado(proposta['dadosImovelGarantia']['estado'])
        self.act.enviar_texto('//*[@id="no_estadof_garan_chzn"]/div/div/input', estado.upper(), By.XPATH)
        self.act.press_enter('//*[@id="no_estadof_garan_chzn"]/div/div/input', By.XPATH)

        return self.preencher_dados_proponente(proposta)

    def switch_mes(self, mes_input):
        mes = {
            '01' : "Janeiro",
            '02' : "Fevereiro",
            '03' : "Março",
            '04' : "Abril",
            '05' : "Maio",
            '06' : "Junho",
            '07' : "Julho",
            '08' : "Agosto",
            '09' : "Setembro",
            '10' : "Outubro",
            '11' : "Novembro",
            '12' : "Dezembro"  
        }
        if mes_input in mes:
            return mes[mes_input] 
    
    def completar_dados_pdf(self, dados):
        packet = io.BytesIO()
        # Cria um Novo Objeto PDF
        can = canvas.Canvas(packet, pagesize=A4)
        # Proponente
        can.drawString(x=45, y=688, text=dados['nome'])
        # CPF
        can.drawString(x=310, y=688, text=dados['cpf'])
        # Endereço Residencial
        endereco = dados['logradouro'] + ', ' + dados['numeroCasa'] + ' ' + dados['complemento'] + ' ' + dados['cidade'] + '/' + dados['uf']
        can.drawString(x=45, y=589, text=endereco.upper())
        # Endereço da Garantia
        endereco = dados['dadosImovelGarantia']['logradouro'] + ', ' + dados['dadosImovelGarantia']['numero'] + ' ' + dados['dadosImovelGarantia']['complemento'] + ' ' + dados['dadosImovelGarantia']['cidade'] + '/' + dados['dadosImovelGarantia']['estado']
        can.drawString(x=45, y=540, text=endereco.upper())
        # Dia
        data_hoje = datetime.now()
        can.drawString(x=115, y=155, text=data_hoje.strftime("%d"))
        # Més
        mes = self.switch_mes(data_hoje.strftime("%m"))
        can.drawString(x=187, y=155, text=mes)
        # Ano
        can.drawString(x=325, y=155, text=data_hoje.strftime("%Y"))
        can.save()
        # Inicio do Buffer do STRING IO
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        # Le o Pdf
        existing_pdf = PdfFileReader(open(self.path_pdf + "documento.pdf", "rb"))
        output = PdfFileWriter()
        # Junta os dois pdfs 
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        # Escreve o Output para o novo pdf
        outputStream = open(self.path_pdf + "documento_preenchido.pdf", "wb")
        output.write(outputStream)
        outputStream.close()
        # Junta o novo pdf preenchido junto com o DPS
        pdf1 = open(self.path_pdf + "documento_preenchido.pdf", "rb")
        pdf2 = open(self.path_pdf + "documento_saude.pdf", "rb")

        pdf1_read = PdfFileReader(pdf1)
        pdf2_read = PdfFileReader(pdf2)

        pdfWriter = PdfFileWriter()
        for page in range(pdf1_read.numPages):
            pageObj = pdf1_read.getPage(page)
            pdfWriter.addPage(pageObj)

        for page in range(pdf2_read.numPages):
            pageObj = pdf2_read.getPage(page)
            pdfWriter.addPage(pageObj)
        pdfOutputFile = open(self.path_pdf + 'MergedFiles.pdf', 'wb')
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()
        pdf1.close()
        pdf2.close()


if __name__ == '__main__':
    robo = Proposta_Daycoval()
    while True:
        robo.main()
        sleep(600)
        
