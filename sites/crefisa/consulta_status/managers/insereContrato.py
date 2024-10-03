
import os,time,pdb,re,requests,json,sys,os,platform,datetime,base64
#winsound

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

from sites.baseRobos.core.data_helpers import formatar_moeda,formatar_cpf_sem_caracteres,formatar_data_banco_dados,buscar_documentos_contrato,download
from sites.baseRobos.core.helpers import deleta_todos_arquivos,get_id_perfil
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from sites.crefisa.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from unidecode import unidecode

from PIL import Image

try:
    from pypdf import PdfReader
except:
    from PyPDF2 import PdfReader



HORARIO_COMERCIAL = 8, 20


class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "insercao": "https://app1.gerencialcredito.com.br/CREFISA/simuladorCrefisa.asp",
            "consulta_status": "https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp"
        }

        #self.set_options('--ignore-ssl-errors',"--lang=pt_BR")
        #self.set_experimental_opts({'intl.accept_languages': 'pt,pt_BR'})
        #pdb.set_trace()
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.atualiza = Uconecte()
        self.request_get = APIDataSource()

        self.path_documentos = sys.path[0]+'/sites/crefisa/documentos/'

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

        if contratos['tipo'] == 'alert':
            print('Sem contratos para inserir...')
            return False

        #testes
        #contratos = {}
        #contratos['contratos'] = [{'codigo_con' : '658259', 'perfil' : 'CLT(Empresa Privada)'}] 

        

        for contrato in contratos['contratos']:
            try:
                dados_atualizacao = {}
                dados_atualizacao['mensagem'] = 'Inserir contrato'
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                print(f"Inserindo contrato para o perfil ---------{contrato['perfil']}----------")

                informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con']) 
                self.chrome_driver.get(self.urls["insercao"]) 
                #pdb.set_trace()
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
                self.verificar_loading(2)
               
                retorno_mensagem = ""
                try:
                    retorno_mensagem = self.act.obter_texto('/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/span', By.XPATH)
                except:
                    try:
                        retorno_mensagem = self.act.obter_texto('/html/body/div[8]/div/div[2]/div[1]', By.XPATH)
                    except:
                        retorno_mensagem = ""
                        pass   
                    pass

                if retorno_mensagem != "":

                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                    dados_atualizacao['erro'] = retorno_mensagem
                    dados_atualizacao['observacao'] = retorno_mensagem

                    if('Exception' in retorno_mensagem or 'erro no processamento' in retorno_mensagem):
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['interacaoHumana'] = 0
                        dados_atualizacao['observacao'] = "Erro ao inserir: "+retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']

                    if('Experimente fazer login novamente' in retorno_mensagem or 'Erro interno' in retorno_mensagem):
                        print('XXXXXXXXXXX Sessão deslogada... Aguardando 5 minutos pra logar XXXXXXXXXXX')
                        time.sleep(300)
                        self.driver.delete_all_cookies()
                        self.driver.quit()
                        continue

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
                #pdb.set_trace()
                id_perfil = get_id_perfil(contrato['perfil'])
                tipo_produto_crefisa = self.get_produto_crefisa(id_perfil)

                if(id_perfil in [9,10,11]):
                    baixa_renda = True
                    preenche_dia_salario = False
                    pontuacao_documentos = 6
                    array_docs_necessarios = ['documentoPessoal',
                                            'COMPROVANTE_ENDERECO',
                                            'MEU_NIS',
                                            'COMPROVANTE_DE_CONTA',
                                            'EXTRATO_BANCaRIO_ULTIMOS_30',
                                            'EXTRATO_BANCaRIO_%7CMES1%7C_DA_CONTA_DO_CAIXATEM',
                                            'EXTRATO_BANCaRIO_%7CMES2%7C_DA_CONTA_DO_CAIXATEM',
                                            'EXTRATO_BANCaRIO_%7CMES3%7C_DA_CONTA_DO_CAIXATEM']

                else:
                    baixa_renda = False
                    preenche_dia_salario = True
                    pontuacao_documentos = 5
                    array_docs_necessarios = ['documentoPessoal',
                                              'COMPROVANTE_ENDERECO',
                                              'CONTRA_CHEQUE',
                                              'EXTRATO_BANCaRIO_ULTIMOS_30',      
                                            ]

                    if(id_perfil in [4,5]):
                        pontuacao_documentos = 6
                        array_docs_necessarios = ['documentoPessoal',
                                                  'COMPROVANTE_ENDERECO',
                                                  'EXTRATO_DE_PAGAMENTO',
                                                  'CARTA_DE_CONCESSaO', 
                                                  'EXTRATO_BANCaRIO'     
                                                ]

                        for doc in documentos_pessoais:
                            if 'CARTA_DE_CONCESSaO_DO_BENEFiCIO' in doc:
                                try:
                                    download(doc, self.path_documentos + 'carta.pdf')
                                    reader = PdfReader(self.path_documentos + 'carta.pdf')
                                    page = reader.pages[0]
                                    texto = page.extract_text()
                                    pattern = re.compile(r"\((\d+)\)")
                                    numero_beneficio = pattern.findall(texto)[0]
                                
                                except:
                                    if 'numeroBeneficio' in informacoes['contrato']['dadosProfissionais']:
                                        numero_beneficio = informacoes['contrato']['dadosProfissionais']['numeroBeneficio']

                                    else:
                                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                                        dados_atualizacao['observacao_emp'] = "Número do benefício não encontrato no documento carta concessão"
                                        dados_atualizacao['observacao'] = "Número do benefício  não encontrato no documento carta concessão"
                                        dados_atualizacao['status_con'] = "Aguardando Comercial"

                                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                        self.remove_div()
                                        continue

                

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
                if pontuacao < pontuacao_documentos:
                    print('CPF aprovado, mas documentos estão incompletos...')
                    dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    print('----------------------------------------------------------------------------------------')
                    continue

                try:
                    deleta_todos_arquivos(self.path_documentos)
                except:
                    self.path_documentos = sys.path[0]+'/documentos/'
                    deleta_todos_arquivos(self.path_documentos)
                    pass  


                erro_leitura_ia = False

                if(id_perfil in [9,10,11]):
                    mensagem_erro_leitura = "Não reconheceu nenhum arquivo anexado."

                    for doc_unico in documentos_pessoais:
                        for doc_exigido in array_docs_necessarios:
                            if doc_exigido in doc_unico:
                                if('COMPROVANTE_DE_CONTA_DO_CAIXATEM' in doc_unico):
                                    base64Arquivo = base64.b64encode(requests.get(doc_unico).content)
                                    # prompt1 = """
                                    #             You are a document entity extraction specialist. Given a document, your task is to extract the text value of the following entities:
                                    #               {
                                    #                "banco": "",
                                    #                "agencia": "",
                                    #                "conta": "",
                                    #                "digito_conta": ""
                                    #               }


                                    #             - The JSON schema must be followed during the extraction.
                                    #             - The values must only include text strings found in the document.
                                    #             - Generate null for missing entities.
                                    #             """
                                    #prompt = 'quais os dados da imagem. JSON schema, {"banco":"","agencia":"","conta":"","digito_conta":""}'
                                    #prompt = 'informe em formato JSON usando as keys banco, agencia, conta, digito_conta com os dados do arquivo'
                                    prompt = 'informe o retorno dos dados da imagem em formato json'
                                    retorno_conta = self.request_get.post_request_v2('ia-vertex-arquivo', {'key':'f689f1e12a0399fba803cb2365fc362f' ,'base64' : base64Arquivo, 'prompt': prompt}).json()
                                    
                                    print('.... Lendo o comprovante de conta')

                                    if 'tipo' in retorno_conta and retorno_conta['tipo'] == 'alert':
                                        erro_leitura_ia = True
                                        break;

                                    retorno_conta_json = json.loads(retorno_conta['retorno'].replace('```','').replace('\n','').replace('json',''))
                                    
                                    key_conta = 'Conta'
                                    if 'conta' in retorno_conta_json:
                                        key_conta = 'conta'

                                    try:
                                        informacoes['contrato']['numeroConta'] = retorno_conta_json[key_conta].split("-")[0]
                                        informacoes['contrato']['digitoConta'] = retorno_conta_json[key_conta].split("-")[-1]
                                    except:
                                        erro_leitura_ia = True
                                        mensagem_erro_leitura = "COMPROVANTE DE CONTA"
                                        break
                                        pass

                                    continue

                                elif('MEU_NIS' in doc_unico):
                                    matricula_origem = informacoes['contrato']['matricula']
                                    base64Arquivo = base64.b64encode(requests.get(doc_unico).content)

                                    prompt = 'a imagem é um comprovante de matricula meu nis nela contem a matricula que é formada por 11 numeros retorne essa informacao em formato json usando a key com nome matricula com os dados contidos no arquivo e com o regex \\d{11}'
                                    retorno_matricula = self.request_get.post_request_v2('ia-vertex-arquivo', {'key':'f689f1e12a0399fba803cb2365fc362f' ,'base64' : base64Arquivo, 'prompt': prompt}).json()
                                    
                                    print('.... Lendo dados da matricula')
                                    
                                    if 'tipo' in retorno_matricula and retorno_matricula['tipo'] == 'alert':
                                        erro_leitura_ia = True
                                        mensagem_erro_leitura = "MEU NIS"                                        
                                        break;

                                    retorno_matricula_json = json.loads(retorno_matricula['retorno'].replace('```','').replace('\n','').replace('json',''))
                                    matricula_json = retorno_matricula_json['matricula']
                                    continue

                    if erro_leitura_ia == True and 'inserir' not in contrato['observacao_emp']:
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = "IA não reconheceu o documento na leitura: "+mensagem_erro_leitura
                        dados_atualizacao['observacao'] = "IA não reconheceu o documento na leitura: "+mensagem_erro_leitura
                        dados_atualizacao['status_con'] = "Aguardando Comercial"
                        dados_atualizacao['erro'] = "IA não reconheceu o documento na leitura"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        self.remove_div()
                        continue

                    #troca matricula

                    if 'inserir' in contrato['observacao_emp']:
                        informacoes['contrato']['matricula'] = matricula_origem
                    else:
                        informacoes['contrato']['matricula'] = matricula_json


                print(f"Continuando inserção contrato para o perfil ---------{contrato['perfil']}----------")
                """print("Preenchendo primeiro fomulario de aceitacao...")
                self.act.enviar_texto('//*[@id="txtCpfSimulacao"]', informacoes['contrato']['cpf'], By.XPATH)
                self.act.press_enter('//*[@id="appVue"]/div[2]/div[2]/div[2]/div/button', By.XPATH)
                print('----------------------------------------------------------------------------------------')
                """

                retorno = self.verificar_loading()

                print("Preenchendo segundo fomulario de simulacao...")

                try:
                    self.act.enviar_texto("//input[@id='txtNomeCompleto']", informacoes['contrato']['nome'], By.XPATH)
                    self.act.enviar_texto("//input[@id='txtEmail']", informacoes['contrato']['email'], By.XPATH)

                    self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[2]/div[2]/div/div[1]/div/button', By.XPATH)
                    elementos_ddd = '/html/body/div[6]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/ul/li'
                    ddd_lista = self.act.retornar_elementos(elementos_ddd, By.XPATH)

                    for i in ddd_lista:
                        if i.text == informacoes['contrato']['dddCelular']:
                            print('Achou o DDD...')
                            i.click()
                            
                    self.act.enviar_texto("//input[@id='txtTelefone']", informacoes['contrato']['celular'], By.XPATH)
                    print('----------------------------------------------------------------------------------------')
                except:
                    self.driver.delete_all_cookies()

                print("Preenchendo o convenio")
                self.act.select_drop_down("//select[@id='ddlConvenio']",tipo_produto_crefisa, By.XPATH)
                print('----------------------------------------------------------------------------------------')

                print("Preenchendo o reverso")

                try:
                    reverso_nis = informacoes['contrato']['matricula'][-1]
                except:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "Matrícula incorreta"
                    dados_atualizacao['observacao'] = "Matrícula incorreta"
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = "Matrícula incorreta"
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    self.remove_div()
                    continue

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

                if(baixa_renda == False):

                    self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[5]/div[1]/div/button', By.XPATH)
                    select_dia_salario = str(int(informacoes['contrato']['diaSalario']) + 1)

                    try:
                        self.act.clicar_elemento(f'/html/body/div[6]/div/div[3]/div/div[5]/div[1]/div/div/ul/li[{select_dia_salario}]', By.XPATH)
                    except:
                        self.act.clicar_elemento(f'/html/body/div[6]/div/div[3]/div/div[5]/div[1]/div/div/ul/li[2]', By.XPATH)
                        pass

                    if id_perfil in [4,5]:

                        try:
                            self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[5]/div[2]/div/button', By.XPATH)  
                            self.act.enviar_texto('/html/body/div[6]/div/div[3]/div/div[5]/div[2]/div/div/div/input', numero_beneficio, By.XPATH)
                            self.act.press_enter('/html/body/div[6]/div/div[3]/div/div[5]/div[2]/div/div/div/input', By.XPATH)

                        except:

                            if 'numeroBeneficio' in informacoes['contrato']['dadosProfissionais']:
                                numero_beneficio = informacoes['contrato']['dadosProfissionais']['numeroBeneficio']

                            else:

                                dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                                dados_atualizacao['observacao_emp'] = "Contrato teste de inss para colocar o beneficio"
                                dados_atualizacao['observacao'] = "Contrato teste de inss para colocar o beneficio"
                                dados_atualizacao['status_con'] = "Aguardando Comercial"
                                dados_atualizacao['erro'] = "Contrato teste de inss para colocar o beneficio"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                self.remove_div()
                                continue
                            pass

                print('----------------------------------------------------------------------------------------')
                print('Preenchendo renda')
                self.act.enviar_texto('//*[@id="txtValorRendaLiquida"]', informacoes['contrato']['renda'], By.XPATH)

                print('----------------------------------------------------------------------------------------')

                print("Preenchendo o tipo de simulação")

                try:
                    self.act.select_drop_down("//select[@id='txtTipoSimulacao']",'1', By.XPATH)
                    novo_contrato = True
                except:
                    self.act.select_drop_down("//select[@id='txtTipoSimulacao']",'2', By.XPATH)
                    novo_contrato = False
                    pass

                mensagem_refin = ""
                try:
                    mensagem_refin = self.act.obter_texto('//*[@id="appVue"]/div[3]/div/div[7]/div[1]/div/div/span', By.XPATH)
                    if 'apto à contratação de refin recorrente' in mensagem_refin:
                        novo_contrato = False
                        self.act.select_drop_down("//select[@id='txtTipoSimulacao']",'2', By.XPATH)
                        self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[7]/div[2]/div/label', By.XPATH)
                        self.act.clicar_elemento('/html/body/div[6]/div/div[3]/div/div[8]/div/button[1]', By.XPATH)    
                        retorno = self.verificar_loading()

                        if(retorno['retorno'] == False):
                            if 'Não há contratos para refinanciar' in retorno['mensagem']:
                                novo_contrato = True
                                time.sleep(2)
                                self.remove_div()
                                self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[7]/div[2]/div/label', By.XPATH)
                                
                except:
                    pass

                print('----------------------------------------------------------------------------------------')

                print('Preenchendo calculo por parcela e valor da parcela')

                if(novo_contrato == True):
                    try:
                        self.act.select_drop_down('//*[@id="txtTipoValorContrato"]','1', By.XPATH)
                    except:
                        self.act.select_drop_down("//select[@id='txtTipoSimulacao']",'1', By.XPATH)
                        self.act.select_drop_down('//*[@id="txtTipoValorContrato"]', '1', By.XPATH)
                        pass

                    self.act.enviar_texto('//*[@id="txtValorSimulacao"]', informacoes['contrato']['valorParcela'], By.XPATH) 
                    print('----------------------------------------------------------------------------------------')
                    
                    print('Clicando em simular')
                    try:
                        self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[7]/div/button', By.XPATH)
                    except:
                        self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[8]/div/button[1]', By.XPATH)
                        pass

                    retorno = self.verificar_loading()
                
                if retorno['retorno'] == False:
                    dados_atualizacao['mensagem'] = 'Pendente Dados'
                    dados_atualizacao['textoMensagem'] = retorno['mensagem']
                    dados_atualizacao['observacao'] = retorno['mensagem']
                    dados_atualizacao['erro'] = retorno['mensagem']

                    if('Exception' in retorno_mensagem):
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['interacaoHumana'] = 0
                        dados_atualizacao['observacao'] = "Erro ao inserir: "+retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']

                    if('matrícula' in retorno['mensagem']):
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = "Matrícula incorreta"
                        dados_atualizacao['observacao'] = "Matrícula incorreta"
                        dados_atualizacao['erro'] = retorno['mensagem']
                        dados_atualizacao['status_con'] = "Aguardando Comercial"

                    if('Selecione Espécie do Benefício' in retorno['mensagem']):
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = "Informe número do benefício"
                        dados_atualizacao['observacao'] = "Informe número do benefício"
                        dados_atualizacao['erro'] = retorno['mensagem']
                        dados_atualizacao['status_con'] = "Aguardando Comercial"

                    if('o cliente já possui contrato em andamento com a parcela' in retorno['mensagem'] or 'possui contrato em andamento com a parcela' in retorno['mensagem']):
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = retorno['mensagem']
                        dados_atualizacao['observacao'] = retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"

                    
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    self.remove_div()
                    continue

                print('----------------------------------------------------------------------------------------')

                print('Selecionando o prazo...')

                if novo_contrato == False:

                    self.act.select_drop_down('//*[@id="txtTipoValorContratoNovaSimulacao"]', "1", By.XPATH)
                    self.act.enviar_texto('//*[@id="txtValorSimulacaoNovaSimulacao"]', informacoes['contrato']['valorParcela'], By.XPATH)
                    self.act.clicar_elemento('/html/body/div[6]/div/div[4]/div[2]/div/div[2]/div/div/button', By.XPATH)

                    retorno = self.verificar_loading()

                    if retorno['retorno'] == False:

                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = retorno['mensagem']
                        dados_atualizacao['observacao'] = retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']

                        if('Nenhuma simulação encontrada' in retorno['mensagem']):

                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = retorno['mensagem']
                            dados_atualizacao['observacao'] = retorno['mensagem']
                            dados_atualizacao['erro'] = retorno['mensagem']
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"

                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        self.remove_div()
                        continue

                    else:

                        self.dados_consulta ={}
                        self.dados_consulta["atualizaTipoProposta"] = "REFINANCIAMENTO"
                        self.dados_consulta["codigoCon"] = contrato['codigo_con']

                        texto_refin = self.act.obter_texto('//*[@id="appVue"]/div[4]/div[2]/div[1]/div[1]/div', By.XPATH)
                        texto_novo = self.act.obter_texto('//*[@id="appVue"]/div[4]/div[2]/div[2]/div[2]/div/div/div', By.XPATH)

                        str_valor = self.act.obter_texto('//*[@id="appVue"]/div[4]/div[2]/div[2]/div[2]/div/div/div/div[2]/div[4]/div/span', By.XPATH)
                        novo_valor_contrato = formatar_moeda(str_valor.split(" ")[1])

                        self.dados_consulta["mensagemDadosRefin"] = f" Dados do refinamento: {texto_refin} - {texto_novo}"
                        self.dados_consulta["valor_con"] = novo_valor_contrato

                        self.dados.post_dados_consultados(self.dados_consulta)
                        # dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        # dados_atualizacao['observacao_emp'] = "Esse contrato e de refinanciamento e precisa tratar no codigo para quando resultado"
                        # dados_atualizacao['observacao'] = "Esse contrato e de refinanciamento e precisa tratar no codigo para quando resultado"
                        # dados_atualizacao['erro'] = retorno['mensagem']
                        # dados_atualizacao['status_con'] = "Aguardando Comercial"
                        # self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        

                else:
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
                #self.act.select_drop_down('//*[@id="ddlUfOrgaoEmissor"]', informacoes['contrato']['estadoEmissor'], By.XPATH)     
                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[2]/div[6]/div/button', By.XPATH)  
                self.act.enviar_texto('/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div[6]/div/div/div/input', informacoes['contrato']['estadoEmissor'], By.XPATH)

                if informacoes['contrato']['estadoEmissor'] == 'SE':
                    self.act.press_DOWN('/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div[6]/div/div/ul/li[1]/a',By.XPATH)
                self.act.press_enter('/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div[6]/div/div/div/input', By.XPATH)

                
                #self.act.select_drop_down('//*[@id="ddlUfNascimento"]',informacoes['contrato']['estadoNaturalidade'], By.XPATH) 
                #pdb.set_trace()
                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[3]/div[2]/div/button', By.XPATH)  
                self.act.enviar_texto('/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/input', informacoes['contrato']['estadoNaturalidade'], By.XPATH)
                
                if informacoes['contrato']['estadoNaturalidade'] == 'SE':
                    self.act.press_DOWN('/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div[2]/div/div/ul/li[1]/a',By.XPATH)

                self.act.press_enter('/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/input', By.XPATH)
                time.sleep(5)
                #self.act.enviar_texto('//*[@id="txtNaturalidade"]',informacoes['contrato']['naturalidade'], By.XPATH) 
                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[3]/div[3]/div/button', By.XPATH)  
                self.act.enviar_texto('/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div[3]/div/div/div/input', unidecode(informacoes['contrato']['naturalidade']), By.XPATH)
                self.act.press_enter('/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div[3]/div/div/div/input', By.XPATH)

                self.act.select_drop_down('//*[@id="txtSexo"]',informacoes['contrato']['sexo'][0], By.XPATH)
                
                if self.remove_div() == True:
                    self.act.enviar_texto('//*[@id="txtDataEmissaoRg"]', '10/10/2020', By.XPATH)
                    #self.act.enviar_texto('//*[@id="txtDataNascimento"]', informacoes['contrato']['dataNascimento'], By.XPATH)

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
                
                try:
                    self.act.enviar_texto('//*[@id="txtComplemento"]',informacoes['contrato']['complemento'], By.XPATH)
                except:
                    self.act.enviar_texto('//*[@id="txtComplemento"]','Casa', By.XPATH)
                    pass

                print('----------------------------------------------------------------------------------------')

                print('Preenchendo dados conta bancária')
                if(baixa_renda == False):
                    if informacoes['contrato']['numeroBanco'] == '955':
                        informacoes['contrato']['numeroBanco'] = '033'
                    self.act.select_drop_down('//*[@id="ddlBanco"]', informacoes['contrato']['numeroBanco'], By.XPATH)
                    self.act.enviar_texto('//*[@id="txtAgencia"]',informacoes['contrato']['agencia'], By.XPATH)


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
                    self.act.enviar_texto('//*[@id="txtLogradouro"]',informacoes['contrato']['logradouro'].replace('...',''), By.XPATH)  

                if(self.act.obter_texto('//*[@id="txtBairro"]', By.XPATH) == ""):
                    self.act.enviar_texto('//*[@id="txtBairro"]',informacoes['contrato']['bairro'].replace('...',''), By.XPATH)

                #if(self.act.obter_texto('//*[@id="ddlUfEndereco"]', By.XPATH) == ""):
                #    self.act.enviar_texto('//*[@id="txtBairro"]',informacoes['contrato']['uf'], By.XPATH)

                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[8]/div[2]/div/button', By.XPATH)  
                self.act.enviar_texto('/html/body/div[6]/div/div[2]/div/div[2]/div[8]/div[2]/div/div/div/input', informacoes['contrato']['uf'], By.XPATH)
                if informacoes['contrato']['uf'] == 'SE':
                    self.act.press_DOWN('/html/body/div[6]/div/div[2]/div/div[2]/div[8]/div[2]/div/div/ul/li[1]/a',By.XPATH)
                self.act.press_enter('/html/body/div[6]/div/div[2]/div/div[2]/div[8]/div[2]/div/div/div/input', By.XPATH)

                texto_cidade = self.act.obter_texto('//*[@id="appVue"]/div[2]/div/div[2]/div[8]/div[3]/div/button', By.XPATH)
                if( texto_cidade == "" or texto_cidade == "Selecione"):
                    #self.act.enviar_texto('//*[@id="txtCidade"]',informacoes['contrato']['cidade'], By.XPATH)
                    time.sleep(5)
                    self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[8]/div[3]/div/button', By.XPATH)  
                    self.act.enviar_texto('/html/body/div[6]/div/div[2]/div/div[2]/div[8]/div[3]/div/div/div/input', informacoes['contrato']['cidade'], By.XPATH)
                    self.act.press_enter('/html/body/div[6]/div/div[2]/div/div[2]/div[8]/div[3]/div/div/div/input', By.XPATH)

                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[10]/div/button', By.XPATH)  


                retorno = self.verificar_loading()
                
                if 'Data' in retorno['mensagem']:
                    
                    if 'Nascimento' in retorno['mensagem']: 
                        self.registra_data_nascimento(informacoes)
                        retorno = self.verificar_loading()

                        if 'data de nascimento deve ser maior ou igual' in retorno['mensagem']:
                            self.registra_data_rg(informacoes, True)
                            self.registra_data_nascimento(informacoes)
                            retorno['retorno'] == True
                            retorno['mensagem'] == ""

                    if 'RG' in retorno['mensagem']:
                        self.registra_data_rg(informacoes)
                        retorno = self.verificar_loading()

                        #print(erro)

                        """dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = erro
                        dados_atualizacao['observacao'] = erro
                        dados_atualizacao['status_con'] = "Aguardando Comercial"

                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                        continue"""

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
                self.driver.execute_script("document.body.style.zoom='50%'")
                for doc in documentos_pessoais:

                    if 'COMPROVANTE_ENDERECO' in doc and baixa_renda == True:
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

                    if(baixa_renda == True):

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

                    else:

                        if 'documentoPessoal' in doc:                
                            caminho_xpath = '//*[@id="ddlarquivosRg"]'

                            #vai anexar em arquivo de cpf também
                            if(conta_anexo_cpf == 2):
                                caminho_xpath = '//*[@id="ddlarquivosCpf"]'
                                #upload2 = self.driver.find_element(By.XPATH,'//*[@id="ddlarquivosCpf"]')
                                #upload2.send_keys(arquivo)
                                #continue

                            conta_anexo_cpf += 1     

                        elif 'CONTRA_CHEQUE' in doc or 'EXTRATO_DE_PAGAMENTOS' in doc:
                            caminho_xpath = '//*[@id="ddlarquivosContracheque"]'    

                            #vai anexar em arquivo de extratos também
                            #upload2 = self.driver.find_element(By.XPATH,'//*[@id="ddlarquivosExtratoBancario"]')
                            #upload2.send_keys(arquivo)     

                        elif 'COMPROVANTE_ENDERECO' in doc:
                            caminho_xpath = '//*[@id="ddlarquivosComprovanteResidencia"]' 

                        elif 'EXTRATO_BANCaRIO' in doc or 'CARTA_DE_CONCESSaO' in doc:
                            caminho_xpath = '//*[@id="ddlarquivosExtratoBancario"]' 

                        else:
                            caminho_xpath = '//*[@id="ddlarquivosOutros"]'


                    counter += 1

                    try:
                        upload = self.driver.find_element(By.XPATH, caminho_xpath)
                    except:
                        upload = self.driver.find_element(By.XPATH, '//*[@id="ddlarquivosOutros"]')
                        pass

                    upload.send_keys(arquivo)

                        
                #pdb.set_trace()
                print('----------------------------------------------------------------------------------------')

                print('Procurando por ade...')
                
                #for i in range(1,7): 
                #    self.act.clicar_elemento(f'//*[@id="accordion"]/div[{i}]/div[1]/h4/a', By.XPATH)

                try:
                    self.act.clicar_elemento('//*[@id="appVue"]/div[3]/div/div[2]/div[3]/div/button[2]', By.XPATH)  
                except:
                    self.driver.execute_script("""$('#appVue > div:nth-child(3) > div > div.card-body > div.row.mt-4 > div > button.btn.btn-primary').click()""")
                     
                retorno = self.verificar_loading(30)
                self.driver.execute_script("document.body.style.zoom='100%'")
                
                if retorno['retorno'] == True  and retorno['ade'] != "":
                    deleta_todos_arquivos(self.path_documentos)
                    self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown > div > div.swal2-actions > button.swal2-confirm.swal2-styled").click()""")

                    dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                    #pdb.set_trace()
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
            except Exception as e:
                print(e)
                continue


    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def remove_div(self):
        try:
            if self.act.quantidade_elemento('/html/body/div[9]/div/div[3]/button[1]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[8]/div/div[3]/button[1]', By.XPATH) == 1:                
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
                    return {'retorno': False, 'mensagem': "Sua matrícula está inválida! Confirme a nova matrícula." + mensagem, 'ade': ""}
                
                elif 'Verificação de dados bancários' in mensagem:
                    return {'retorno': False, 'mensagem': "Conta incorreta favor confirmar. " + mensagem, 'ade': ""}

                else:
                    return {'retorno': False, 'mensagem': mensagem, 'ade': ""}


            if(interacoes < 0):
                return {'retorno': False, 'mensagem': "Loading eterno", 'ade': ""}
                #self.driver.quit()

        return {'retorno': True, 'mensagem': "", 'ade': ""}

    def get_produto_crefisa(self, perfil):
        switcher = {
            1 : "43",
            2 : "42",
            3 : "44",
            4 : "1",
            5 : "1",
            6 : "42",
            7 : "42",
            8 : "42",
            9 : "38",
            10 : "38",
            11 : "38"
        }
        return switcher.get(perfil, 'Opção inválida')


    def registra_data_rg(self,informacoes, forjar_data = False):
        self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
                
        print("XXXXXXXXXXXXXXXX ERRO NA DATA DE RG XXXXXXXXXXXXXXXXXXX")

        if(forjar_data == True):
            data_nova = "10/10/" + str(int(informacoes['contrato']['dataNascimento'].split('/')[2]) - 1)
        else:
            data_nova = "10/10/2020"

        self.act.enviar_texto('//*[@id="txtDataEmissaoRg"]', data_nova, By.XPATH)
        self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[10]/div/button', By.XPATH)

    def registra_data_nascimento(self, informacoes):
        self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")

        print("XXXXXXXXXXXXXXXX ERRO NA DATA DE NASCIMENTO XXXXXXXXXXXXXXXXXXX")

        nova_data_nascimento = datetime.datetime.strptime(informacoes['contrato']['dataNascimento'], "%d/%m/%Y").strftime("%m-%d-%Y")
        self.act.enviar_texto('//*[@id="txtDataNascimento"]', nova_data_nascimento, By.XPATH)
        self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div/div[2]/div[10]/div/button', By.XPATH)  