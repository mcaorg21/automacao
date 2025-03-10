
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



HORARIO_COMERCIAL = 7, 22


class AnalisaContrato(Manager):

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

        run = AnalisaContrato(driver)
        try:
            run.inserir_contrato()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def inserir_contrato(self):     
        self.driver.execute_script("document.body.style.zoom='80%'")
        self.verificar_loading()       
        print('Iniciando inserção de contrato...')

        #fila = input('Informe: 1- para fila ou 2- para contrato teste \n')

        # if(fila == '1'):

        contratos = self.dados.get_contratos_inserir('asc')  

        if contratos['tipo'] == 'alert':
            print('Sem contratos para inserir...')
            return False

        # else:

        #     contrato = input('Informe número contrato: \n')

        #     while contrato == "":
        #         contrato = input('Informe número contrato: \n')

        #     perfil = input('Baixa Renda? 1- sim 2- nao: \n')

        #     while perfil == "":
        #         perfil = input('Baixa Renda? 1- sim 2- nao: \n')

        #     if(perfil != '1'):
        #         perfil = input('Qual perfil? Copie do Web admin: \n')

        #         while perfil == "":
        #             perfil = input('Qual perfil? Copie do Web admin: \n')
        #     else:
        #         perfil ='Autônomo'

        #     #testes
        #     contratos = {}
        #     contratos['contratos'] = [{'codigo_con' : contrato, 'perfil': perfil, 'observacao_emp' : "teste"}] 

        for contrato in contratos['contratos']:

            self.div_principal = '5'
            self.div_principal_overlay = '7'
            
            dados_atualizacao = {}

            if 'Pre aprovado' in contrato['observacao_emp']:
                print ('VVVVVVVVVVVVVVVVVVVVVVVVVVVV JA ANALISADO PELO ROBO VVVVVVVVVVVVVVVVVVVVVVVVVVVV')
                continue

            if 'Inserir manual o robô já tentou por 5x e não conseguiu' in contrato['observacao_emp'] or '5 tentativas ou mais' in contrato['observacao_emp']:
                dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                dados_atualizacao['observacao_emp'] = "5 tentativas ou mais de inserção"
                dados_atualizacao['observacao'] = "5 tentativas ou mais de inserção"
                dados_atualizacao['status_con'] = "Aguardando Comercial"
                dados_atualizacao['erro'] = "5 tentativas ou mais de inserção"
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                continue

            try:
                
                dados_atualizacao['mensagem'] = 'Inserir contrato'
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                print(f"Inserindo contrato para o perfil ---------{contrato['perfil']}----------")

                informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con']) 
                self.chrome_driver.get(self.urls["insercao"]) 
                #verifica se cpf está habilitado para realizar
                url = f'https://app1.gerencialcredito.com.br/CREFISA/ajax_crefisa.asp?combo=getOperacaoCliente&cpfCliente={informacoes["contrato"]["cpf"]}'
                cookies_name = ""
                cookies_value = ""

                numero_conta_origem = informacoes['contrato']['numeroConta']
                digito_conta_origem = informacoes['contrato']['digitoConta']
               
                self.act.enviar_texto('//*[@id="txtCpfSimulacao"]', informacoes["contrato"]["cpf"], By.XPATH)
                self.act.clicar_elemento('//*[@id="appVue"]/div[2]/div[2]/div[2]/div/button', By.XPATH)
                self.verificar_loading(2)
               
                
                # try:
                #     retorno_mensagem = self.act.obter_texto('/html/body/div[5]/div/div[2]/div[2]/div[2]/div/div/span', By.XPATH)
                # except:
                #     try:
                #         retorno_mensagem = self.act.obter_texto('/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/span', By.XPATH)                        
                #     except:
                #         retorno_mensagem = ""
                #         pass   
                #     pass

                retorno_mensagem = self.verificar_loading()

                try:
                    retorno_mensagem = retorno_mensagem['mensagem']
                except:
                    pass

                if 'convênio baixa renda?' in retorno_mensagem.lower():
                    self.act.press_enter(f'/html/body/div[7]/div/div[3]/button[1]', By.XPATH)
                    retorno_mensagem = ""

                try:
                    print('Tela ofertas')
                    self.act.select_drop_down('//*[@id="ddlDddTelefoneSimulacaoPreAprovada"]', informacoes['contrato']['dddCelular'], By.XPATH)
                    self.act.enviar_texto('/html/body/div[5]/div/div[5]/div/div/div[2]/div[2]/div/div/div[2]/input', informacoes['contrato']['celular'], By.XPATH)
                    self.act.clicar_elemento('/html/body/div[5]/div/div[5]/div/div/div[2]/div[3]/div/div/button[1]', By.XPATH)
                except:
                    pass

                try:
                    retorno_mensagem = self.act.obter_texto(f'/html/body/div[{self.div_principal}]/div/div[2]/div[2]/div[2]/div/div/span', By.XPATH)
                except:
                    retorno_mensagem = ""
                    pass

                if retorno_mensagem != "" and "Informe o dígito da matricula" not in retorno_mensagem:

                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                    dados_atualizacao['erro'] = retorno_mensagem
                    dados_atualizacao['observacao'] = retorno_mensagem

                    if('Exception' in retorno_mensagem or 'erro no processamento' in retorno_mensagem):
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['interacaoHumana'] = 0
                        dados_atualizacao['observacao'] = "Erro ao inserir: "+retorno['mensagem']
                        dados_atualizacao['erro'] = retorno['mensagem']

                    if('Experimente fazer login novamente' in retorno_mensagem or 'Erro interno' in retorno_mensagem or 'Ocorreu um erro ao processar a' in retorno_mensagem):
                        print('XXXXXXXXXXX Sessão deslogada... Aguardando 180s pra logar XXXXXXXXXXX')
                        time.sleep(180)
                        self.driver.delete_all_cookies()
                        self.driver.quit()
                        continue

                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue

                else:
                    retorno_mensagem = self.verificar_loading()
                    self.remove_div()


                #verifica se tem todos os documentos necessarios
                pontuacao = 0
                documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']

                id_perfil = get_id_perfil(contrato['perfil'])
                tipo_produto_crefisa = self.get_produto_crefisa(id_perfil)

                #pdb.set_trace()
                if(id_perfil in [9,10,11]):
                    baixa_renda = True
                    preenche_dia_salario = False
                    pontuacao_documentos = 4
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
                    pontuacao_documentos = 4
                    array_docs_necessarios = ['documentoPessoal',
                                              'COMPROVANTE_ENDERECO',
                                              'CONTRA_CHEQUE',
                                              'EXTRATO_BANCaRIO_ULTIMOS_30',      
                                            ]

                    if(id_perfil in [4,5]):
                        pontuacao_documentos = 5
                        array_docs_necessarios = ['documentoPessoal',
                                                  'COMPROVANTE_ENDERECO',
                                                  'EXTRATO_DE_PAGAMENTO',
                                                  'CARTA_DE_CONCESSaO', 
                                                  'EXTRATO_BANCaRIO'     
                                                ]

                        for doc in documentos_pessoais:
                            if 'EXTRATO_DE_PAGAMENTOS_' in doc:
                                try:
                                    print('----------------- LENDO NUMERO DO BENEFICIO -----------------')
                                    base64Arquivo = base64.b64encode(requests.get(doc).content)
                                    prompt = 'informe somente o numero da especie de beneficio em formato json, no retorno retorne a key especie'
                                    numero_beneficio_retorno = self.request_get.post_request_v2('ia-vertex-arquivo', {'key':'f689f1e12a0399fba803cb2365fc362f' ,'base64' : base64Arquivo, 'prompt': prompt}).json()

                                    numero_beneficio = ""
                                    try:
                                        numero_beneficio = json.loads(numero_beneficio_retorno['retorno'].replace('```','').replace('\n','').replace('json',''))['especie']
                                    except:
                                        pass

                                    # download(doc, self.path_documentos + 'carta.pdf')
                                    # reader = PdfReader(self.path_documentos + 'carta.pdf')
                                    # page = reader.pages[0]
                                    # texto = page.extract_text()

                                    # #pattern = re.compile(r"\((\d+)\)")
                                    # match = re.search(r"Espécie:\s*(\d{2})\s*-", texto)
                                    # numero_beneficio = match.group(1)
                                
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


                if(id_perfil in [9,10,11]):

                    for doc_unico in documentos_pessoais:
                        for doc_exigido in array_docs_necessarios:
                            if doc_exigido in doc_unico:
                                if 'documentoPessoal' in doc_unico:
                                    pontuacao += 0.5
                                elif 'MEU_NIS' in doc_unico or 'COMPROVANTE_DE_CONTA' in doc_unico or 'EXTRATO_BANCaRIO_ULTIMOS_30' in doc_unico:
                                    pontuacao += 1
                                else:
                                    continue

                                # print(pontuacao)
                                # print(doc_exigido)
                                # print('doc_exigido')

                else:

                    for doc_unico in documentos_pessoais:
                        for doc_exigido in array_docs_necessarios:
                            if doc_exigido in doc_unico:
                                if 'documentoPessoal' in doc_unico:
                                    pontuacao += 0.5
                                else:
                                    pontuacao += 1

                                # print(pontuacao)
                                # print(doc_exigido)
                                # print('doc_exigido')

                
                ######################################################################################
                counter = 1
                conta_anexo_cpf = 1

                if pontuacao < pontuacao_documentos:
                    retorno_mensagem = self.verificar_loading()
                    print('CPF aprovado, mas documentos estão incompletos...')
                    dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    print('----------------------------------------------------------------------------------------')
                    continue

                else:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "Pre aprovado automacao CPF e docs"
                    dados_atualizacao['observacao'] = "Pre aprovado automacao CPF e docs"
                    dados_atualizacao['erro'] = ""
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                    print('XXXXXXXXXXXXXXXXXX TUDO OK E DOCUMENTACAO PULANDO... XXXXXXXXXXXXXXXXXX')
                    continue
            except:
                pass

    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def remove_div(self):
        try:
            if self.act.quantidade_elemento(f'/html/body/div[{self.div_principal_overlay}]/div/div[3]/button[1]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[9]/div/div[3]/button[1]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[8]/div/div[3]/button[1]', By.XPATH) == 1:                
                self.driver.execute_script("""document.querySelector("body > div.swal2-container.swal2-center.swal2-fade.swal2-shown").remove()""")
                return True
            else:
                return False                      
        except:
            pass

    def verificar_loading(self, interacoes=300, aguardar = False):
        time.sleep(1)

        while (self.act.quantidade_elemento('/html/body/div[7]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[8]', By.XPATH) == 1 or self.act.quantidade_elemento('//*[@id="swal2-content"]', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(1)
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