
import os,time,pdb,re,requests,json,sys,os,platform,datetime,base64,unidecode
from pprint import pprint
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

from sites.euro17.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from datetime import datetime

HORARIO_COMERCIAL = 7, 22

class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False, ordem: str = 'desc'):
        super().__init__()

        self.urls = {
            "insercao": "https://capture.kapmug.com/dashboard?federalNumber=|CPF|&pointOfSale=67ffc6ba8657e44514ca4794"
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
        self.ordem = ordem
    
        self.path_documentos = sys.path[0]+'/sites/facta/documentos/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+'/sites/facta/documentos/'

        self.xpath = {
            
            "pesquisa_inicial": {
                "cpf": '//*[@id="input_text_federalNumber"]'
            },

            "formulario_inicial": {
                "escolha_produto": "/html/body/div/div/div[2]/div/div/div[1]",
                "alerta": "/html/body/div[3]/section/div",
                "cpf": "//*[@id='input_text_cpf']",
                "nome": "//*[@id='input_text_name']",
                "data_nascimento": "//*[@id='input_datepicker_birthDate']",
                "renda": "//*[@id='input_text_income']",
                "celular": "//*[@id='input_text_phones']",
                "email": "//*[@id='input_text_emails']",
                "botao_avancar": "//button[@type='submit']",
                "mensagem_erro": '/html/body/div/main/div/section/div/div/form/div[3]/div[2]',
            },
            
            "simulacao": {
                "primeiro_vencimento": "/html/body/div/main/div[2]/div/section/div/section/section[1]/div[2]/div/div[4]/div/span",
                'primeiro_vencimento_input': '/html/body/div/main/div[2]/div/section/div/section/section[1]/div[2]/div/div[4]/div/label/div[2]/input',
                "botao_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]",
                "input_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/label/div[2]/input",
                "botao_confirmar_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/label/div[3]/button[2]",
                "botao_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/p[2]",
                "input_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/label/div[2]/input",
                "botao_confirmar_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/label/div[3]/button[2]",
                "valor_contrato" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[1]/p[2]",
                "botao_contratar" : "/html/body/div/main/div[2]/div/section/div/div[4]/div/button",
                "texto_recusa" : '/html/body/div/main/div[2]/div/section/div/span/div/div/div/div/button',
                "ade": '/html/body/div/main/div[1]/div/div[1]/div[1]/strong[1]/span',
            },
            
            "dados_pessoais": {
                "cpf": "//*[@id='input_text_cpf']",
                "nome": "//*[@id='input_text_name']",
                "data_nascimento": "//*[@id='input_datepicker_birthDate']",
                "sexo": "//*[@id='select-input-gender']",
                "celular": "//*[@id='input_text_phones']",
                "email": "//*[@id='input_text_emails']",
                "nome_mae": "//*[@id='input_text_mothersName']",
                "nacionalidade": "//*[@id='select-input-nationality']",
                "naturalidade": "//*[@id='select-input-placeOfBirth']",
                "tipo_documento": "//*[@id='select-input-document.documentSetup']",
                "numero_documento": "//*[@id='input_text_document.number']",
                "data_emissao": "//*[@id='input_datepicker_document.emission']",
                "orgao_emissor": "//*[@id='select-input-issuingAuthority']",
                "uf_emissao": "//*[@id='select-input-rgState']",
                "estado_civil": "//*[@id='select-input-maritalStatus']",
                "pessoa_politicamente_exposta": "//*[@id='politicallyExpose']",
                "botao_avancar": "//button[@type='submit']",
                "cep": "//*[@id='input_text_postalCode']",
                "endereco": "//*[@id='input_text_place']",
                "numero": "//*[@id='input_text_placeNumber']",
                "complemento": "//*[@id='input_text_complement']",
                "bairro": "//*[@id='input_text_neighborhood']",
                "cidade": "//*[@id='input_text_city']",
                "estado": "//*[@id='select-input-federativeUnit']",
                "tipo_residencia": "//*[@id='select-input-residenceType']",
                "tempo_residencia": "//*[@id='input_text_residenceTime']",
                "possui_endereco_comercial": "//*[@id='hasBusinessAddress']",
                "botao_voltar": "//button[normalize-space()='VOLTAR']",
                "botao_avancar": "//button[normalize-space()='AVANÇAR']",
                "ocupacao": "//*[@id='select-input-natureOfOccupation']",
                "botao_voltar": "//button[@aria-label='Voltar']",
                "botao_avancar": "//button[normalize-space()='AVANÇAR']"
            },
            
            "dados_bancarios": {
                "banco": "//input[@id='select-input-checkingAccount.bank']",
                "agencia": "//input[@id='input_text_checkingAccount.agency']",
                "digito_agencia": "//input[@id='input_text_checkingAccount.agencyDigit']",
                "tipo_conta": "//input[@id='select-input-checkingAccount.checkingAccountType']",
                "numero_conta": "//input[@id='input_text_checkingAccount.account']",
                "digito_conta": "//input[@id='input_text_checkingAccount.accountDigit']",
                "pix_tipo": "//input[@id='select-input-pix.type']",
                "pix_chave": "//input[@id='input_text_pix.key']",
                "botao_avancar": "//button[@type='submit' and contains(., 'AVANÇAR')]",
                "texto_modal": '/html/body/section/div[2]/div/header/h2',
                "botao_avancar_modal": "/html/body/section/div[2]/div/footer/button[2]",
                "botao_voltar": "//button[contains(., 'VOLTAR')]"
            },
            
            "tela_referencia": {
                "botao_voltar": "//button[contains(text(), 'Voltar')]",
                "titulo_pagina": "//h2[contains(text(), 'Referências')]",
                "tabela_vazia": "//div[contains(text(), 'Nenhum item encontrado')]",
                "botao_adicionar_referencia": "//button[contains(text(), 'Adicionar nova referência')]",
                "botao_avancar": "//button[contains(text(), 'AVANÇAR')]",
                "modal_titulo_adicionar_referencia": "//h2[contains(text(), 'Adicionar referência')]",
                "input_nome": "//input[@id='input_text_name']",
                "input_celular": "//input[@id='input_text_phones']",
                "input_email": "//input[@id='input_text_emails']",
                "select_tipo_referencia": "//input[@id='select-input-referenceType']",
                "botao_cancelar_modal": "//button[contains(text(), 'Cancelar')]",
                "botao_salvar_modal": "//button[contains(text(), 'Salvar')]"
            },
            
            "finalizacao" : {
                "link_formalizacao_button": "//button[contains(text(), 'Gerar QR Code')]",
                "link_formalizacao": "/html/body/section/div[2]/div/div/div/div",
                "fechar_link_formalizacao": "/html/body/section/div[2]/div/footer/button",
                "enviar_link_formalizacao_remota" : "/html/body/div/div/div[1]/div[2]/div[1]/button[4]",
                "input_email_link" : "/html/body/section/div[2]/div/div/div[2]/button[2]",
                "finalizar_avancar": "/html/body/div/div/div[1]/div[2]/div[2]/button[3]",
            }
        }

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome, ordem):

        run = InserirContrato(driver, ordem)
        try:
            run.inserir_contrato()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def inserir_contrato(self):    

        self.driver.execute_script("document.body.style.zoom='80%'")     
        print(f'Iniciando inserção de contrato... Ordem: {self.ordem}')
        
        fila = '1'
        if 'Windows' in platform.system():
            
            fila = input('Informe: 1- para fila ou 2- para contrato teste \n')
            
            if fila == '1':
                self.ordem = input('Qual ordem da fila? desc ou asc? \n')
            else:
                self.ordem = 'desc'

        if(fila == '1'):
            
            contratos = self.dados.get_contratos_inserir(self.ordem)  

            if not contratos['contratos']:
                print('Sem contratos para inserir...')
                time.sleep(10)
                return False

        else:

            contrato = input('Informe número contrato: \n')

            while contrato == "":
                contrato = input('Informe número contrato: \n')

            #testes
            contratos = {}
            contratos['contratos'] = [{'codigo_con' : contrato, 'observacao_emp' : "Pre aprovado"}] 

        for contrato in contratos['contratos']:
            
            print('----------------- Iniciando inserção do contrato -----------------')
            dados_atualizacao = {}
            
            #REMOVER
            # dados_atualizacao['mensagem'] = 'Inserir contrato'
            # self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
            
            print(f'>>>>> Inserindo contrato: {contrato["codigo_con"]}')
            informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
            pprint(informacoes)
            cpf = informacoes['contrato']['cpf'].replace('-','').replace('.','')
            self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))

            self.verificar_loading()
 
            try:

                if 'Inserir manual o robô já tentou por 5x e não conseguiu' in contrato['observacao_emp'] or '5 tentativas ou mais' in contrato['observacao_emp']:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['observacao'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = "5 tentativas ou mais de inserção"
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
                
                print('----------------- Clicando em emprestimo pessoal -----------------')
                self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto'], By.XPATH)
                
                #REMOVER
                # if self.act.quantidade_elemento(self.xpath['formulario_inicial']['alerta'], By.XPATH) == 1:
                #     texto_alerta = self.act.obter_texto(self.xpath['formulario_inicial']['alerta'], By.XPATH)
                #     if('Não é possível criar uma proposta para este CPF' in texto_alerta):
                #         print('XXXXXXXXXXXXXXXXXXXXX Política interna XXXXXXXXXXXXXXXXXXXXX')
                #         dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                #         dados_atualizacao['observacao_emp'] = 'CPF reprovado por política interna'
                #         dados_atualizacao['observacao'] = 'CPF reprovado por política interna'  
                #         dados_atualizacao['erro'] = 'CPF reprovado por política interna'
                #         dados_atualizacao['status_con'] = "Reprovado a Conferir"
                #         self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                #         continue

                self.verificar_loading()
                print('----------------- Preenchendo dados do formulário inicial -----------------')
                self.act.enviar_texto(self.xpath['formulario_inicial']['nome'], informacoes['contrato']['nome'], By.XPATH)
                if 'Windows' in platform.system():
                    self.act.enviar_texto(self.xpath['formulario_inicial']['data_nascimento'], informacoes['contrato']['dataNascimento'], By.XPATH)
                else:
                    invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
                    self.act.enviar_texto(self.xpath['formulario_inicial']['data_nascimento'], invert_data(informacoes['contrato']['dataNascimento']), By.XPATH)
                
                #REMOVER informacoes['contrato']['renda']
                self.act.enviar_texto(self.xpath['formulario_inicial']['renda'], '3000,00' , By.XPATH)
                self.act.enviar_texto(self.xpath['formulario_inicial']['celular'], '+55'+informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'], By.XPATH)
                self.act.enviar_texto(self.xpath['formulario_inicial']['email'], informacoes['contrato']['email'], By.XPATH)

                self.act.clicar_elemento(self.xpath['formulario_inicial']['botao_avancar'], By.XPATH)
                pdb.set_trace()
                self.verificar_loading()
                print('>>>>> Preenchendo primeiro vencimento do contrato')
                self.act.clicar_elemento(self.xpath['simulacao']['primeiro_vencimento'], By.XPATH)

                # data_hoje_formatada = datetime.now().strftime("%d/%m/%Y")
                # if 'Windows' in platform.system():
                #     self.act.enviar_texto(self.xpath['simulacao']['primeiro_vencimento_input'], data_hoje_formatada, By.XPATH)
                # else:   
                #     invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
                #     self.act.enviar_texto(self.xpath['simulacao']['primeiro_vencimento_input'], invert_data(data_hoje_formatada), By.XPATH)
                
                try:
                    texto_recusa = self.act.obter_texto(self.xpath['simulacao']['mensagem_erro'], By.XPATH)

                    if 'Cliente não elegível' in texto_recusa:
                        print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao = {}
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        #self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    else:
                        print('XXXXXXXXXXXXXXXXXXXXX Classificar recusa XXXXXXXXXXXXXXXXXXXXX')
                        pdb.set_trace()
                except:
                    texto_recusa = ''
                    pass
                
                print('----------------- Preenchendo dados da simulação -----------------')
                
                print('>>>>>> Preenchendo parcela do contrato')
                
                #REMOVER informacoes['contrato']['valorParcela']
                self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
                self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
                time.sleep(0.5)
                self.act.enviar_texto(self.xpath['simulacao']['input_parcela'], '200,00', By.XPATH)
                self.act.clicar_elemento(self.xpath['simulacao']['botao_confirmar_parcela'], By.XPATH)

                print('>>>>>> Preenchendo prazo do contrato')
                self.act.clicar_elemento(self.xpath['simulacao']['botao_prazo'], By.XPATH)
                self.act.clicar_elemento(self.xpath['simulacao']['botao_prazo'], By.XPATH)
                time.sleep(0.5)
                self.act.enviar_texto(self.xpath['simulacao']['input_prazo'], informacoes['contrato']['prazo'], By.XPATH)
                self.act.clicar_elemento(self.xpath['simulacao']['botao_confirmar_prazo'], By.XPATH)

                print('>>>>>> Atualizando o valor do contrato')
                valor_contrato = self.act.obter_texto(self.xpath['simulacao']['valor_contrato'], By.XPATH)
                dados_atualizacao['valorContrato'] = formatar_moeda(valor_contrato)
                pdb.set_trace()
                print('>>>>>> Clicando em contratar')
                self.act.clicar_elemento(self.xpath['simulacao']['botao_contratar'], By.XPATH)
                
                self.verificar_loading()
                
                print('----------------- Verificando se o contrato foi pre-aprovado -----------------')
                try:
                    #REMOVER O COMENTARIO DA ATUALIACAO
                    texto_recusa = self.act.obter_texto(self.xpath['simulacao']['texto_recusa'], By.XPATH)
                    if 'Encerrar' in texto_recusa:
                        print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao = {}
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        #self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                            
                except:
                    texto_recusa = ''
                    pass
                
                print('----------------- Contrato foi pre-aprovado -----------------')
                print('>>>>>>>> Pegando a ADE do contrato')
                dados_atualizacao['ade'] = self.act.obter_texto(self.xpath['simulacao']['ade'], By.XPATH).strip()

                print('---------------- Preenchendo dados pessoais -----------------')
                
                print('>>>>>>>> Preenchendo sexo')
                self.act.enviar_texto(self.xpath['dados_pessoais']['sexo'], informacoes['contrato']['sexo'], By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['sexo'], By.XPATH)
                
                print('>>>>>>>> Preenchendo nome da mae')
                self.act.enviar_texto(self.xpath['dados_pessoais']['nome_mae'], informacoes['contrato']['nomeMae'], By.XPATH)

                print('>>>>>>>> Preenchendo nacionalidade')
                self.act.enviar_texto(self.xpath['dados_pessoais']['nacionalidade'], "Brasileira", By.XPATH)
                self.act.enviar_texto(self.xpath['dados_pessoais']['nacionalidade'], "Brasileira", By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['nacionalidade'], By.XPATH)
                
                print('>>>>>>>> Preenchendo naturalidade')                
                self.act.enviar_texto(self.xpath['dados_pessoais']['naturalidade'], informacoes['contrato']['naturalidade'], By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['naturalidade'], By.XPATH)
                
                print('>>>>>>>> Preenchendo dados do documento')                
                self.act.enviar_texto(self.xpath['dados_pessoais']['tipo_documento'], 'DOCUMENTO DE IDENTIFICAÇÃO', By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['tipo_documento'], By.XPATH)
                
                print('>>>>>>>> Preenchendo número do documento')                
                self.act.enviar_texto(self.xpath['dados_pessoais']['numero_documento'], informacoes['contrato']['identidade'], By.XPATH)                
                
                if 'Windows' in platform.system():
                    self.act.enviar_texto(self.xpath['dados_pessoais']['data_emissao'], informacoes['contrato']['dataEmissao'], By.XPATH)
                else:
                    invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
                    self.act.enviar_texto(self.xpath['dados_pessoais']['data_emissao'], invert_data(informacoes['contrato']['dataEmissao']), By.XPATH)
                
                print('>>>>>>>> Preenchendo orgão emissor')
                informacoes['contrato']['orgaoEmissor'] = 'SSP'
                if 'DETRAN' in informacoes['contrato']['orgaoEmissor']:
                    informacoes['contrato']['orgaoEmissor'] = 'DETRAN'                    
                self.act.enviar_texto(self.xpath['dados_pessoais']['orgao_emissor'], informacoes['contrato']['orgaoEmissor'], By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['orgao_emissor'], By.XPATH)
                
                print('>>>>>>>> Preenchendo UF de emissão')
                self.act.enviar_texto(self.xpath['dados_pessoais']['uf_emissao'], informacoes['contrato']['estadoEmissor'], By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['uf_emissao'], By.XPATH)
                
                print('>>>>>>>> Preenchendo estado civil')                
                self.act.enviar_texto(self.xpath['dados_pessoais']['estado_civil'], informacoes['contrato']['estadoCivil'][0:4], By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['estado_civil'], By.XPATH)

                print('>>>>>>>> Clicando em avancar')
                self.act.clicar_elemento(self.xpath['dados_pessoais']['botao_avancar'], By.XPATH)
                self.verificar_loading()

                print('----------------- Preenchendo CEP -----------------')
                self.act.enviar_texto(self.xpath['dados_pessoais']['cep'], informacoes['contrato']['cep'], By.XPATH)
                self.verificar_loading()
                print('>>>>>>>> Preenchendo endereço')
                self.act.enviar_texto(self.xpath['dados_pessoais']['endereco'], informacoes['contrato']['logradouro'], By.XPATH)
                if(informacoes['contrato']['numeroCasa'] == ''):
                    informacoes['contrato']['numeroCasa'] = '1'
                print('>>>>>>>> Preenchendo número da casa')
                self.act.enviar_texto(self.xpath['dados_pessoais']['numero'], informacoes['contrato']['numeroCasa'], By.XPATH)
                if(informacoes['contrato']['complemento'] == ''):
                    informacoes['contrato']['complemento'] = 'CASA'
                print('>>>>>>>> Preenchendo complemento')
                self.act.enviar_texto(self.xpath['dados_pessoais']['complemento'], informacoes['contrato']['complemento'], By.XPATH)
                print('>>>>>>>> Preenchendo bairro')
                self.act.enviar_texto(self.xpath['dados_pessoais']['bairro'], informacoes['contrato']['bairro'], By.XPATH)
                print('>>>>>>>> Preenchendo cidade')
                self.act.enviar_texto(self.xpath['dados_pessoais']['cidade'], informacoes['contrato']['cidade'], By.XPATH)

                print('>>>>>>>> Clicando em avançar')
                self.act.clicar_elemento("//button[normalize-space()='AVANÇAR']", By.XPATH)
                
                self.verificar_loading()
                
                print('----------------- Preenchendo ocupacao -----------------')
                get_ocupacao = lambda codigo: {
                                '1': "Assalariado Setor Público",
                                '2': "Assalariado Setor Público",
                                '3': "Assalariado Setor Público",
                                '4': "Aposentado",
                                '5': "Pensionista",
                                '6': "Assalariado Setor Público",
                                '7': "Assalariado Setor Público",
                                '8': "Assalariado Setor Público",
                                '9': "Empresário",
                                '10': "Autônomo",
                                '11': "Assalariado Setor Privado"
                            }.get(str(codigo), "Assalariado Setor Privado")

                self.act.enviar_texto(self.xpath['dados_pessoais']['ocupacao'], get_ocupacao(informacoes['contrato']['dadosProfissionais']['perfil']), By.XPATH)
                self.act.press_enter(self.xpath['dados_pessoais']['ocupacao'], By.XPATH)
                
                print('>>>>>>>> Clicando em avançar')
                self.act.clicar_elemento(self.xpath['dados_pessoais']['botao_avancar'], By.XPATH)                
                self.verificar_loading()
                
                print('----------------- Preenchendo dados bancários -----------------')
                print('>>>>>>>> Preenchendo banco') 
                self.act.enviar_texto(self.xpath['dados_bancarios']['banco'], informacoes['contrato']['numeroBanco'], By.XPATH)
                self.act.press_enter(self.xpath['dados_bancarios']['banco'], By.XPATH)
                
                print('>>>>>>>> Preenchendo agencia')   
                self.act.enviar_texto(self.xpath['dados_bancarios']['agencia'], informacoes['contrato']['agencia'], By.XPATH)

                #print('>>>>>>>> Preenchendo digito da agencia')
                #self.act.enviar_texto("//input[@id='input_text_checkingAccount.agencyDigit']", informacoes['contrato']['digitoAgencia'], By.XPATH)
                
                print('>>>>>>>> Preenchendo tipo de conta')
                informacoes['contrato']['tipoConta'] = 'Poupança'
                if informacoes['contrato']['tipoConta'] == 'Conta-corrente':
                    informacoes['contrato']['tipoConta'] = 'Conta Corrente'
                self.act.enviar_texto(self.xpath['dados_bancarios']['tipo_conta'], informacoes['contrato']['tipoConta'], By.XPATH)   
                self.act.press_enter(self.xpath['dados_bancarios']['tipo_conta'], By.XPATH)

                print('>>>>>>>> Preenchendo número da conta')
                self.act.enviar_texto(self.xpath['dados_bancarios']['numero_conta'], informacoes['contrato']['numeroConta'], By.XPATH)

                print('>>>>>>>> Preenchendo digito da conta')
                self.act.enviar_texto(self.xpath['dados_bancarios']['digito_conta'], informacoes['contrato']['digitoConta'], By.XPATH)

                print('>>>>>>>> Preenchendo chave Pix')
                self.act.enviar_texto(self.xpath['dados_bancarios']['pix_tipo'], 'CPF', By.XPATH)

                #TODO: Verificar se a chave Pix é obrigatória
                # if 'chavePix' in informacoes['contrato'] and informacoes['contrato']['chavePix'] != '':
                #     self.act.press_enter(self.xpath['dados_bancarios']['pix_tipo'], By.XPATH)
                #     self.act.enviar_texto(self.xpath['dados_bancarios']['pix_chave'], informacoes['contrato']['chavePix'], By.XPATH)
                #     self.act.press_enter(self.xpath['dados_bancarios']['pix_chave'], By.XPATH)

                # else:
                #     print('>>>>>>>> Chave Pix não informada')
                
                
                print('>>>>>>>> Clicando em avançar')
                self.act.clicar_elemento(self.xpath['dados_bancarios']['botao_avancar'], By.XPATH)
                time.sleep(2)

                print('>>>>>>>> Confirmando modal')
                try:
                    texto_modal = self.act.obter_texto(self.xpath['dados_bancarios']['texto_modal'], By.XPATH)
                    if 'Confirmar chave pix?' in texto_modal:
                        self.act.clicar_elemento(self.xpath['dados_bancarios']['botao_avancar_modal'], By.XPATH)
                    else:
                        print('XXXXXXXXXXXXXXXXXXXXX Modal Classificar Nova Interacao XXXXXXXXXXXXXXXXX')
                        pdb.set_trace()
                except:
                    print('XXXXXXXXXXXXXXXXXXXXX Modal Classificar Nova Situacao XXXXXXXXXXXXXXXXX')
                    pdb.set_trace()
                    pass
                
                self.verificar_loading()
                
                print('----------------- Preenchendo Referencias -----------------')
                self.act.clicar_elemento(self.xpath['tela_referencia']['botao_adicionar_referencia'], By.XPATH)
                
                #REMOVER DADOS FIXOS
                self.act.enviar_texto( self.xpath['tela_referencia']['input_nome'], 'MARCELO AMANCIO', By.XPATH)
                self.act.enviar_texto( self.xpath['tela_referencia']['input_celular'], '+5511993449817', By.XPATH)
                self.act.enviar_texto( self.xpath['tela_referencia']['input_email'], 'teste@referencia.com', By.XPATH)
                self.act.enviar_texto( self.xpath['tela_referencia']['select_tipo_referencia'], 'Pessoal', By.XPATH)
                self.act.press_enter( self.xpath['tela_referencia']['select_tipo_referencia'], By.XPATH)
                self.act.clicar_elemento( self.xpath['tela_referencia']['botao_salvar_modal'], By.XPATH)

                self.act.clicar_elemento(self.xpath['tela_referencia']['botao_avancar'], By.XPATH)

                self.verificar_loading()
                
                self.act.clicar_elemento(self.xpath['finalizacao']['link_formalizacao_button'], By.XPATH)
                time.sleep(0.5)
                dados_atualizacao['linkAssinatura'] = self.act.obter_texto(self.xpath['finalizacao']['link_formalizacao'], By.XPATH).strip()

                self.act.clicar_elemento(self.xpath['finalizacao']['fechar_link_formalizacao'], By.XPATH)

                self.act.clicar_elemento("/html/body/section/div[2]/div/footer/button", By.XPATH)
                print('----------------- Registrando a Ade e Atualizando o Contrato -----------------')
                
                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                dados_atualizacao['status_con'] = "Pendente"
                dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                dados_atualizacao['liberarDoc'] = 1
                dados_atualizacao['pedidoDocumentacao'] = 3                              
                
                pdb.set_trace()
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                print('----------------- Finalizando -----------------')
                
                
                self.act.clicar_elemento(self.xpath['finalizacao']['enviar_link_formalizacao_remota'], By.XPATH)
                time.sleep(0.5)
                self.act.clicar_elemento(self.xpath['finalizacao']['input_email_link'], By.XPATH)
                time.sleep(2)
                self.act.clicar_elemento(self.xpath['finalizacao']['finalizar_avancar'], By.XPATH)

                while self.act.quantidade_elemento(self.xpath['pesquisa_inicial']['cpf'], By.XPATH) == 0:
                    print('Aguardando finalização...')
                    time.sleep(1)
                    
                self.verificar_loading()
                
                print('----------------- Finalizado -----------------')
                
            except Exception as e:

                print(e)
                if(self.act.quantidade_elemento('//*[@id="wrapper"]', By.XPATH) == 1):
                    self.inserir_contrato()

                if 'localhost' in e:
                    self.driver.quit()

                else:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = e
                    dados_atualizacao['observacao'] = e
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = e
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
    
    def verificar_loading(self, interacoes = 60):
        
        print('Verificando loading...')
        retorno = True
        while ('Atualizando' in self.driver.title 
               or 'Carregando' in self.driver.title 
               or self.act.esta_presente("//div[contains(@class, 'Loading__Wrapper')]", By.XPATH)
               or self.act.quantidade_elemento('/html/body/div/main/div[2]/div/section/div/div/div', By.XPATH) == 1):
            print('Aguardando Loading...')

            interacoes -= 1
            time.sleep(1)
            if(interacoes < 1):
                return False

        return retorno
