
import os,time,pdb,re,requests,json,sys,os,platform
#winsound

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

from sites.baseRobos.core.data_helpers import formatar_moeda,formatar_cpf_sem_caracteres,formatar_data_banco_dados,buscar_documentos_contrato,download
from sites.baseRobos.core.helpers import deleta_todos_arquivos
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from sites.crefisa.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from PIL import Image

HORARIO_COMERCIAL = 8, 20


class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "insercao": "https://app1.gerencialcredito.com.br/CREFISA/simuladorCrefisa.asp",
            "consulta_status": "https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp"
        }

        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.atualiza = Uconecte()
        self.request_get = APIDataSource()

        self.path_documentos = sys.path[0]+'/documentos/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+'/sites/crefisa/documentos/'

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome):

        run = InserirContrato(driver)
        try:
            run.inserir_contrato()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def inserir_contrato(self):     

        self.verificar_loading()       
        print('Iniciando inserção de contrato...')

        contratos = self.dados.get_contratos_inserir()  

        #testes
        #contratos['contratos'] = [{'codigo_con' : '644147'}] 

        if contratos['tipo'] == 'alert':
            print('Sem contratos para inserir...')
            return False

        for contrato in contratos['contratos']:

            dados_atualizacao = {}
            dados_atualizacao['mensagem'] = 'Inserir contrato'
            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)


            informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con']) 
            self.chrome_driver.get(self.urls["insercao"]) 
            
            #verifica se cpf está habilitado para realizar
            url = f'https://app1.gerencialcredito.com.br/CREFISA/ajax_crefisa.asp?combo=getOperacaoCliente&cpfCliente={informacoes["contrato"]["cpf"]}'
            cookies_name = ""
            cookies_value = ""

            #for i in self.driver.get_cookies():
            #    if 'SESSION' in i['name']:
            #        cookies_name = i['name']
            #        cookies_value = i['value']
            #        break

            #headers = {'Cookie': f'{cookies_name}={cookies_value};'}
            #response = requests.request("GET", url, headers=headers)

            #winsound.Beep(6000, 750)
            #if 'page cannot be displayed' in response.text: 
            #    return False

            #print(response.text)
           
            self.act.enviar_texto('//*[@id="txtCpfSimulacao"]', informacoes["contrato"]["cpf"], By.XPATH)
            self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div[2]/div[2]/div/button', By.XPATH)
            self.verificar_loading()

            retorno_mensagem = ""
            try:
                retorno_mensagem = self.act.obter_texto('/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/span', By.XPATH)
            except:
                retorno_mensagem = ""
                pass

            if retorno_mensagem != "":
                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                #if('System.Exception' in retorno_mensagem):
                #    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                dados_atualizacao['erro'] = retorno_mensagem
                dados_atualizacao['observacao'] = retorno_mensagem
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                continue

            """for i in self.driver.get_cookies(): 
                if 'SESSION' in i['name']:
                    cookies_name = i['name']
                    cookies_value = i['value']

                    try:
                        headers = {'Cookie': f'{cookies_name}={cookies_value};'}
                        response = requests.request("GET", url, headers=headers)

                        if 'Message' in json.loads(response.text):
                            if 'Authorization has been denied for this request.' in json.loads(response.text)['Message']:
                                self.driver.quit()
                    
                        retorno = json.loads(response.text)
                        break

                        if 'page cannot be displayed' in response.text: 
                            return False

                    except:
                        print('XXXXXXXXXXXXXXXXXXXXX Erro na consulta do JSON XXXXXXXXXXXXXXXXXXXXX')

                        continue
                else:
                    continue
            
            if 'erro' in retorno and retorno['erro'] == True:
                return False

            if 'objeto' in retorno and retorno['objeto']['permiteCaptura'] == False:
                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                dados_atualizacao['erro'] = retorno['objeto']['mensagem']
                dados_atualizacao['observacao'] = retorno['objeto']['mensagem']
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                continue
            """

            #verifica se tem todos os documentos necessarios
            pontuacao = 0
            documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
            array_docs_necessarios = ['documentoPessoal',
                                        'COMPROVANTE_ENDERECO',
                                        'MEU_NIS',
                                        'COMPROVANTE_DE_CONTA',
                                        'EXTRATO_BANCaRIO_ULTIMOS_30',
                                        'EXTRATO_BANCaRIO_%7CMES1%7C_DA_CONTA_DO_CAIXATEM',
                                        'EXTRATO_BANCaRIO_%7CMES2%7C_DA_CONTA_DO_CAIXATEM',
                                        'EXTRATO_BANCaRIO_%7CMES3%7C_DA_CONTA_DO_CAIXATEM']

            for doc_unico in documentos_pessoais:
                for doc_exigido in array_docs_necessarios:
                    if doc_exigido in doc_unico:
                        pontuacao += 1

            ######################################################################################
            counter = 1
            conta_anexo_cpf = 1
            #array_xpaths = ['//*[@id="ddlarquivosRg"]','//*[@id="ddlarquivosCpf"]','//*[@id="ddlarquivosContracheque"]','//*[@id="ddlarquivosComprovanteResidencia"]', '//*[@id="ddlarquivosExtratoBancario"]','//*[@id="ddlarquivosOutros"]']
            
            # for doc in documentos_pessoais: 

            #     arquivo = self.path_documentos + f'{counter}_arquivo.pdf'

            #     extensao = doc.split('?')[0].split('.')[-1]
            #     if 'pdf' in extensao:
            #          download(doc, arquivo)
            #     else:
                    
            #         try:
            #             download(doc, self.path_documentos + f'{counter}_arquivo.jpg')
                       
            #             Image.open(self.path_documentos + f'{counter}_arquivo.jpg').convert('RGB').save(arquivo,optimize=True, quality=25)
            #         except:
            #             arquivo = self.path_documentos + f'{counter}_arquivo.'+extensao
            #             pass
            # ######################################################################################
            #pdb.set_trace()
            if pontuacao < 6:
                print('CPF aprovado, mas documentos estão incompletos...')
                dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                print('----------------------------------------------------------------------------------------')
                continue

            try:
                deleta_todos_arquivos(self.path_documentos)
            except:
                pass   



            """print("Preenchendo primeiro fomulario de aceitacao...")
            self.act.enviar_texto('//*[@id="txtCpfSimulacao"]', informacoes['contrato']['cpf'], By.XPATH)
            self.act.press_enter('//*[@id="appVue"]/div[2]/div[2]/div[2]/div/button', By.XPATH)
            print('----------------------------------------------------------------------------------------')
            """

            self.verificar_loading()

            print("Preenchendo segundo fomulario de simulacao...")
            self.act.enviar_texto("//input[@id='txtNomeCompleto']", informacoes['contrato']['nome'], By.XPATH)
            self.act.enviar_texto("//input[@id='txtEmail']", informacoes['contrato']['email'], By.XPATH)
            self.act.enviar_texto("//input[@id='txtTelefone']", informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'], By.XPATH)
            print('----------------------------------------------------------------------------------------')
            
            print("Preenchendo o convenio")
            self.act.select_drop_down("//select[@id='ddlConvenio']",'38', By.XPATH)
            print('----------------------------------------------------------------------------------------')

            print("Preenchendo o reverso")
            reverso_nis = informacoes['contrato']['matricula'][-1]

            #array_reversos ={"0":"01","1":"10","2":"09","3":"08","4":"07","5":"06","6":"05","7":"04","8":"03","9":"02"}
            #reverso = "567"+array_reversos[reverso_nis]
            #self.act.select_drop_down("/html/body/div[7]/div/div[3]/div/div[4]/div[2]/div/select", reverso, By.XPATH)

            array_reversos_menu = {
                                    "0":"2",
                                    "1":"11",
                                    "2":"10",
                                    "3":"9",
                                    "4":"8",
                                    "5":"7",
                                    "6":"6",
                                    "7":"5",
                                    "8":"4",
                                    "9":"3"
                                    }     

            # try:   
            #     self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[4]/div[2]/div/button', By.XPATH)                          
            #     self.act.clicar_elemento(f'//*[@id="appVue"]/div[3]/div/div[4]/div[2]/div/div/ul/li[{array_reversos_menu[reverso_nis]}]/a/span[1]', By.XPATH)
            #     print('----------------------------------------------------------------------------------------')
            # except:
            #     pass

            print('Preenchendo matricula e digito')
            self.act.press_backspace('//*[@id="txtMatricula"]',30,By.XPATH,0, True)
            self.act.enviar_texto('//*[@id="txtMatricula"]', informacoes['contrato']['matricula'][0:-1], By.XPATH)
            self.act.enviar_texto('//*[@id="txtDigito"]', informacoes['contrato']['matricula'][-1], By.XPATH)
            self.act.press_backspace('//*[@id="txtDigito"]',3,By.XPATH,0, True)
            self.act.enviar_texto_intervalado('//*[@id="txtDigito"]', informacoes['contrato']['matricula'][-1], By.XPATH)

            print('----------------------------------------------------------------------------------------')
            print('Preenchendo renda')
            self.act.enviar_texto('//*[@id="txtValorRendaLiquida"]', informacoes['contrato']['renda'], By.XPATH)
            print('----------------------------------------------------------------------------------------')

            print("Preenchendo o tipo de simulação")
            self.act.select_drop_down("//select[@id='txtTipoSimulacao']",'1', By.XPATH)
            print('----------------------------------------------------------------------------------------')

            print('Preenchendo calculo por parcela e valor da parcela')
            # try:
            #     self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[6]/div[2]/div/div/button', By.XPATH)
            #     self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[6]/div[2]/div/div/div/ul/li[1]/a/span[1]', By.XPATH)
            # except:
            #     pass
            self.act.select_drop_down('//*[@id="txtTipoValorContrato"]','1', By.XPATH)

            self.act.enviar_texto('//*[@id="txtValorSimulacao"]', informacoes['contrato']['valorParcela'], By.XPATH) 
            print('----------------------------------------------------------------------------------------')

            print('Clicando em simular')
            self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[7]/div/button', By.XPATH)    
            retorno = self.verificar_loading()
            
            if retorno['retorno'] == False:
                dados_atualizacao['mensagem'] = 'Pendente Dados'
                dados_atualizacao['textoMensagem'] = retorno['mensagem']
                dados_atualizacao['observacao'] = retorno['mensagem']
                if('System.Exception' in retorno_mensagem):
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['interacaoHumana'] = 0
                    dados_atualizacao['observacao'] = "Erro ao inserir: "+retorno['mensagem']
                    dados_atualizacao['erro'] = retorno['mensagem']
                
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                self.remove_div()
                continue

            print('----------------------------------------------------------------------------------------')

            print('Selecionando o prazo...')
            self.act.select_drop_down('//*[@id="ddlPrazo"]', str(int(informacoes['contrato']['prazo'])-1), By.XPATH)
            str_valor = self.act.obter_texto('//*[@id="appVue"]/div[4]/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/span', By.XPATH)       
            print('----------------------------------------------------------------------------------------')


            print('Clicando em finalizar simulacao')
            self.act.clicar_elemento('//*[@id="appVue"]/div[4]/div[2]/div/div[3]/button', By.XPATH)    
            self.verificar_loading()
            print('----------------------------------------------------------------------------------------')

            print('Preenchendo dados pessoais')
            
            #data_nascimento = informacoes['contrato']['dataNascimento'].split('/')
            #data_nascimento = data_nascimento[2]+'-'+data_nascimento[1]+'-'+data_nascimento[0]
            #self.driver.execute_script(f"""$('#txtDataNascimento').val('{data_nascimento}')""")
            #pdb.set_trace()
            #self.act.clicar_elemento('//*[@id="txtDataNascimento"]', By.XPATH)
            self.act.enviar_texto('//*[@id="txtDataNascimento"]', informacoes['contrato']['dataNascimento'], By.XPATH)

            identidade_numero = re.sub('[^0-9]', '', informacoes['contrato']['identidade'])
            self.act.enviar_texto('//*[@id="txtRg"]', identidade_numero[0:-1], By.XPATH)
            self.act.enviar_texto('//*[@id="txtDigito"]', identidade_numero[-1], By.XPATH)

            #pdb.set_trace()
            time.sleep(2)
            self.act.enviar_texto('//*[@id="txtDataEmissaoRg"]', informacoes['contrato']['dataEmissao'], By.XPATH)
            self.act.select_drop_down('//*[@id="ddlOrgaoEmissorRg"]', 'SESP', By.XPATH) #informacoes['contrato']['orgaoEmissor'],
            self.act.select_drop_down('//*[@id="ddlUfOrgaoEmissor"]', informacoes['contrato']['estadoEmissor'], By.XPATH)        
            self.act.select_drop_down('//*[@id="ddlUfNascimento"]',informacoes['contrato']['estadoNaturalidade'], By.XPATH) 
            self.act.enviar_texto('//*[@id="txtNaturalidade"]',informacoes['contrato']['naturalidade'], By.XPATH) 
            self.act.select_drop_down('//*[@id="txtSexo"]',informacoes['contrato']['sexo'][0], By.XPATH)

            
            if self.remove_div() == True:
                self.act.enviar_texto('//*[@id="txtDataEmissaoRg"]', '10/10/2020', By.XPATH)
                self.act.enviar_texto('//*[@id="txtDataNascimento"]', informacoes['contrato']['dataNascimento'], By.XPATH)

            switch = {'CASADO(A)': '1','SOLTEIRO(A)':'2','DIVORCIADO(A)': '3','VIÚVO(A)': '4'}        
            codigoEstadoCivil = switch.get(informacoes['contrato']['estadoCivil'].replace(" ","").upper(), '2')
            
            self.act.select_drop_down('//*[@id="ddlEstadoCivil"]', codigoEstadoCivil, By.XPATH)
            self.act.select_drop_down('//*[@id="txtEscolaridade"]','2', By.XPATH)
            self.act.enviar_texto('//*[@id="txtNomeMae"]',informacoes['contrato']['nomeMae'], By.XPATH)
            self.act.select_drop_down('//*[@id="txtCanalDivulgacao"]','419', By.XPATH)
            print('----------------------------------------------------------------------------------------')

            print('Preenchendo dados endereço')
            self.act.enviar_texto('//*[@id="txtCep"]',informacoes['contrato']['cep'], By.XPATH)

            self.act.enviar_texto('//*[@id="txtNumeroEndereco"]',informacoes['contrato']['numeroCasa'], By.XPATH)
            self.remove_div()
            self.act.press_TAB('//*[@id="txtNumeroEndereco"]', By.XPATH)
            self.act.enviar_texto('//*[@id="txtComplemento"]',informacoes['contrato']['complemento'], By.XPATH)
            print('----------------------------------------------------------------------------------------')

            print('Preenchendo dados conta bancária')
            self.act.enviar_texto('//*[@id="txtContaCorrente"]',informacoes['contrato']['numeroConta'], By.XPATH)
            self.act.enviar_texto('//*[@id="txtDigitoConta"]',informacoes['contrato']['digitoConta'], By.XPATH)
            print('----------------------------------------------------------------------------------------')    

            retorno = self.verificar_loading()

            if retorno['retorno'] == False:
                dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                dados_atualizacao['observacao_emp'] = retorno['mensagem']
                dados_atualizacao['observacao'] = retorno['mensagem']

                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                self.remove_div()
                continue

            print('Finalizando dados Pessoais do Contrato')

            if(self.driver.find_element(By.CSS_SELECTOR,"#chkAutorizaSms").is_selected() == False):
                self.act.clicar_elemento('//*[@id="chkAutorizaSms"]', By.XPATH)

            if(self.act.obter_texto('//*[@id="txtLogradouro"]', By.XPATH) == ""):
                self.act.enviar_texto('//*[@id="txtLogradouro"]',informacoes['contrato']['logradouro'], By.XPATH)  

            if(self.act.obter_texto('//*[@id="txtBairro"]', By.XPATH) == ""):
                self.act.enviar_texto('//*[@id="txtBairro"]',informacoes['contrato']['bairro'], By.XPATH)

            if(self.act.obter_texto('//*[@id="txtCidade"]', By.XPATH) == ""):
                self.act.enviar_texto('//*[@id="txtCidade"]',informacoes['contrato']['cidade'], By.XPATH)

            self.act.select_drop_down('//*[@id="ddlUfEndereco"]',informacoes['contrato']['uf'], By.XPATH)

            self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[10]/div/button', By.XPATH)  

            #pdb.set_trace()
            retorno = self.verificar_loading()

            if retorno['retorno'] == False:
                dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                dados_atualizacao['observacao_emp'] = retorno['mensagem']
                dados_atualizacao['observacao'] = retorno['mensagem']

                if 'Conta incorreta' in retorno['mensagem']:
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                self.remove_div()
                continue

            print('----------------------------------------------------------------------------------------')
            
            #idPessoa = informacoes['dadosContrato']['idPessoa']
            #idContrato = informacoes['dadosContrato']['idContrato']

            print('Anexando arquivos')        

            counter = 1
            conta_anexo_cpf = 1
            #pdb.set_trace()
            for doc in documentos_pessoais:

                if 'COMPROVANTE_ENDERECO' in doc:
                    continue

                arquivo = self.path_documentos + f'{counter}_arquivo.pdf'

                extensao = doc.split('?')[0].split('.')[-1]
                if 'pdf' in extensao:
                     download(doc, arquivo)
                else:
                    
                    try:
                        download(doc, self.path_documentos + f'{counter}_arquivo.'+extensao)
                        Image.open(self.path_documentos + f'{counter}_arquivo.'+extensao).convert('RGB').save(arquivo,optimize=True, quality=10)
                    except:
                        arquivo = self.path_documentos + f'{counter}_arquivo.'+extensao
                        pass

                if 'documentoPessoal' in doc:                
                    caminho_xpath = '//*[@id="ddlarquivosRg"]'

                    #vai anexar em arquivo de cpf também
                    if(conta_anexo_cpf == 2):
                        caminho_xpath = '//*[@id="ddlarquivosCpf"]'
                        #upload2 = self.driver.find_element(By.XPATH,'//*[@id="ddlarquivosCpf"]')
                        #upload2.send_keys(arquivo)
                        #continue

                    conta_anexo_cpf += 1     

                elif 'COMPROVANTE_DE_CONTA' in doc:
                    caminho_xpath = '//*[@id="ddlarquivosContracheque"]'    

                    #vai anexar em arquivo de extratos também
                    #upload2 = self.driver.find_element(By.XPATH,'//*[@id="ddlarquivosExtratoBancario"]')
                    #upload2.send_keys(arquivo)     

                elif 'COMPROVANTE_ENDERECO' in doc:
                    caminho_xpath = '//*[@id="ddlarquivosComprovanteResidencia"]' 

                elif 'EXTRATO_BANCaRIO' in doc:
                    caminho_xpath = '//*[@id="ddlarquivosExtratoBancario"]' 

                else:
                    caminho_xpath = '//*[@id="ddlarquivosOutros"]'

                counter += 1

                upload = self.driver.find_element(By.XPATH, caminho_xpath)
                upload.send_keys(arquivo)

            print('----------------------------------------------------------------------------------------')

            print('Procurando por ade...')

            #for i in range(1,7): 
            #    self.act.clicar_elemento(f'//*[@id="accordion"]/div[{i}]/div[1]/h4/a', By.XPATH)

            self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[2]/div[3]/div/button[2]', By.XPATH)  
                 
            retorno = self.verificar_loading(30)
            
            if retorno['retorno'] == True  and retorno['ade'] != "":
                deleta_todos_arquivos(self.path_documentos)
                self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown > div > div.swal2-actions > button.swal2-confirm.swal2-styled").click()""")

                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                dados_atualizacao['valorContrato'] = formatar_moeda(str_valor.split(" ")[1])
                dados_atualizacao['ade'] = retorno['ade']
                dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                dados_atualizacao['linkAssinatura'] = r"https://api.whatsapp.com/send?phone=5511988060603&text=Quero%20assinar%20o%20contrato%20meu%20contrato%20%23"+retorno['ade']
                dados_atualizacao['status_con'] = "Em Processo"
                dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                dados_atualizacao['liberarDoc'] = 1

                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                print(f'VVVVV Contrato gerado com sucesso! Ade {retorno["ade"]} VVVVV')
                print('--------------------------------------------------------------')

            else:
                #retorno = self.verificar_loading()
                if retorno['retorno'] == False:
                    print('XXXXXXXXXXXXXXXXXXXXX ERRO XXXXXXXXXXXXXXXXXXXXX')
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = retorno['mensagem']
                    dados_atualizacao['observacao'] = retorno['mensagem']
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    self.remove_div()
                    continue


                # try:
                #     ade = re.findall(r'\d+',self.act.obter_texto('//*[@id="swal2-content"]', By.XPATH))[0]
                #     if(ade):
                #         deleta_todos_arquivos(self.path_documentos)
                #         self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown > div > div.swal2-actions > button.swal2-confirm.swal2-styled").click()""")

                #         dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                #         dados_atualizacao['valorContrato'] = formatar_moeda(str_valor.split(" ")[1])
                #         dados_atualizacao['ade'] = retorno['ade']
                #         dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                #         dados_atualizacao['linkAssinatura'] = r"https://api.whatsapp.com/send?phone=5511988060603&text=Quero%20assinar%20o%20contrato%20meu%20contrato%20%23"+retorno['ade']
                #         dados_atualizacao['status_con'] = "Em Processo"
                #         dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                #         dados_atualizacao['liberarDoc'] = 1
                #         self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                # except:
                #     print("XXXXXXXXXXXXXXXXXXx ERRO PROCURA DA ADE ########################")
                #     pdb.set_trace()
                #     #continue


    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def remove_div(self):
        try:
            if self.act.quantidade_elemento('/html/body/div[9]/div/div[3]/button[1]', By.XPATH) == 1:
                self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
                return True
            else:
                return False                      
        except:
            pass


    def verificar_loading(self, interacoes=300, aguardar = False):
        time.sleep(1)

        while (self.act.quantidade_elemento('/html/body/div[8]', By.XPATH) == 1 or self.act.quantidade_elemento('//*[@id="swal2-content"]', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(0.5)
            interacoes -= 1

            if(self.act.quantidade_elemento('//*[@id="swal2-content"]', By.XPATH) == 1):

                mensagem = self.act.obter_texto('//*[@id="swal2-content"]', By.XPATH)
                
                if 'INCLUIDO COM SUCESSO' in mensagem:
                    ade = re.findall(r'\d+',self.act.obter_texto('//*[@id="swal2-content"]', By.XPATH))[0]
                    return {'retorno': True, 'mensagem': "Ade gerada com sucesso!", 'ade': ade}
                
                elif 'Verificação da matrícula. Dados inválidos' in mensagem:
                    return {'retorno': False, 'mensagem': "Sua matrícula está inválida! Confirme a nova matrícula.", 'ade': ""}
                
                elif 'Verificação de dados bancários' in mensagem:
                    return {'retorno': False, 'mensagem': "Conta incorreta favor confirmar.", 'ade': ""}

                else:
                    return {'retorno': False, 'mensagem': mensagem, 'ade': ""}


            if(interacoes < 0):
                return {'retorno': False, 'mensagem': "Loading eterno", 'ade': ""}
                #self.driver.quit()

        return {'retorno': True, 'mensagem': "", 'ade': ""}
