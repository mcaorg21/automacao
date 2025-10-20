
import os,time,pdb,re,requests,json,sys,os,platform,datetime,base64,unidecode
import logging

from pprint import pprint
#winsound

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

from sites.baseRobos.core.data_helpers import formatar_moeda,formatar_cpf_sem_caracteres,formatar_data_banco_dados,buscar_documentos_contrato,download
from sites.baseRobos.core.helpers import deleta_todos_arquivos,get_id_perfil,apagar_arquivo
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from sites.euro17.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from datetime import datetime

from sites.baseRobos.core.helpers import definir_nome_robo

HORARIO_COMERCIAL = 7, 22

class AnalisaContrato(Manager):

    def __init__(self, driver: Chrome = False, ordem: str = 'desc', final_contrato: str = '999'):
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
        self.final_contrato = final_contrato

        self.path_documentos = sys.path[0]+'/logs/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+'/sites/euro17/logs/'

        self.xpath = {
            
            "pesquisa_inicial": {
                "cpf": '//*[@id="input_text_federalNumber"]',
                "botao_iniciar" : "//button[text()='Iniciar']",
            },

            "formulario_inicial": {
                "escolha_produto_ep": '//p[normalize-space(.)="Crédito Pessoal"]',
                "escolha_produto_ep_br": '//p[normalize-space(.)="Credito Pessoal B.R."]',
                "escolha_produto": "/html/body/div/div/div[2]/div/div/div[1]",
                "pendencias": "(//div[contains(@class, 'pendency') and text()='Pendências'])[2]",
                "pendencias_baixa_renda": "(//div[contains(@class, 'pendency') and text()='Pendências'])[1]",
                "continuar" : "//button[text()='Continuar']",
                "alerta": "/html/body/div[3]/section/div",
                "cpf": "//*[@id='input_text_cpf']",
                "nome": "//*[@id='input_text_name']",
                "data_nascimento": "//*[@id='input_datepicker_birthDate']",
                "renda": "//*[@id='input_text_income']",
                "celular": "//*[@id='input_text_phones']",
                "email": "//*[@id='input_text_emails']",
                "botao_avancar": "//button[@type='submit']",
                "mensagem_erro": '/html/body/div/main/div[2]/div/section/div/span/div/div/div/div/button',
            },
            
            "simulacao": {
                "primeiro_vencimento": "/html/body/div/main/div[2]/div/section/div/section/section[1]/div[2]/div/div[4]/div/span",
                'primeiro_vencimento_input': '/html/body/div/main/div[2]/div/section/div/section/section[1]/div[2]/div/div[4]/div/label/div[2]/input',
                "botao_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]",
                "alerta_parcela" : "//div[contains(text(), 'não pode ser maior')]",
                "input_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/label/div[2]/input",
                "botao_confirmar_parcela" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/label/div[3]/button[2]",
                "botao_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/p[2]",
                "input_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/label/div[2]/input",
                "botao_confirmar_prazo" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/label/div[3]/button[2]",
                "valor_contrato" : "/html/body/div/main/div[2]/div/section/div/div[2]/div[1]/p[2]",
                "botao_contratar" : "/html/body/div/main/div[2]/div/section/div/div[4]/div/button",
                "texto_recusa" : '/html/body/div/main/div[2]/div/section/div/span/div/div/div/div/button',
                "texto_recusa_novo" : '//form',
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
                "tipo_regime": '//input[@id="select-input-communionRegime"]',
                "nome_conjuge": '//*[@id="input_text_nameSpouse"]',
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
                "empresa": '//*[@id="input_text_employeeAt"]',
                "ocupacao": "//*[@id='select-input-natureOfOccupation']",
                "profissao": '//*[@id="input_text_jobTitle"]',
                "data_admissao": "//*[@id='input_datepicker_hiringDate']",
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
    def iniciar_horario_comercial(cls, driver: Chrome, ordem, final_contrato):

        run = AnalisaContrato(driver, ordem, final_contrato)
        try:
            run.analisa_contrato()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def analisa_contrato(self):    

        self.driver.execute_script("document.body.style.zoom='80%'")     
        print(f'Iniciando análise de contrato... Ordem: {self.final_contrato}')
        #self.ordem = 'asc'
        fila = '1'
        if sys.platform == 'win32':
            fila = '2'
            #fila = input('Informe: 1- para fila ou 2- para contrato teste \n') 
        
        numero_fila = self.final_contrato
        
        # if 'Windows' in platform.system():
        #     fila = input('Informe: 1- para fila ou 2- para contrato teste \n')
        #     if fila == '1':
        #         self.ordem = input('Qual ordem da fila? desc ou asc? \n')
        #         numero_fila = input('De a 0 a 9 qual numero da fila? 99 para todos \n')
        #     else:
        #         self.ordem = 'desc'
                

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
            perfil = input('Qual perfil? Copie do WEBADMIN')
            while perfil == "":
                #perfil = input('Qual perfil? Copie do WEBADMIN')
                perfil = "CLT(Empresa Privada)"
            contratos['contratos'] = [{'codigo_con' : contrato, 'perfil' : perfil, 'observacao_emp' : ''}] 

        # if(numero_fila == '99'):
            #definir_nome_robo('Euro17 Inserção - Desc - Fila: Todos')
        # else:
            #definir_nome_robo(numero_fila + ' - ' + self.ordem + ' - Fila: ' + numero_fila)

        definir_nome_robo(f'{self.final_contrato} - Euro17 Análise')

        for contrato in contratos['contratos']:
            
            dados_atualizacao = {}
            
            if fila == '2':
                array_contratos = [contrato['codigo_con'][-1]]
            
            else:
                # if self.final_contrato == '0':
                #     array_contratos = ['0','1','2','3',[]]
                # elif self.final_contrato == '1':
                #     array_contratos = ['4','5']
                # elif self.final_contrato == '2':
                #     array_contratos = ['6','7','8','9']
                # else:
                # array_contratos = ['0','1','2','3','4','5','6','7','8','9']
                
                # if self.final_contrato == '0':
                #     array_contratos = ['0','1','2']
                # elif self.final_contrato == '1':
                #     array_contratos = ['3','4','5']
                # elif self.final_contrato == '2':
                #     array_contratos = ['6','7','8']
                # elif self.final_contrato == '3':
                #     array_contratos = ['9','0']
                # else:
                #     array_contratos = ['0','1','2','3','4','5','6','7','8','9']
                # elif self.final_contrato == '4':
                #     array_contratos = ['2','3','4','5']
                # else:
                #     array_contratos = ['0']
                array_contratos = [self.final_contrato]

            if(contrato['codigo_con'][-1] not in array_contratos):
                print(f'>>>>> Contrato {contrato["codigo_con"]} pulando esse contrato... Fila: {self.final_contrato}')
                continue
            
            dados_atualizacao['mensagem'] = 'Analise contrato'
            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
            
            # if(self.final_contrato != contrato['codigo_con'][-1] and numero_fila != '999'):
            #     print(f'>>>>> Contrato {contrato["codigo_con"]} pulando esse contrato... Fila: {self.final_contrato}')
            #     continue

            if 'Pre aprovado' in contrato['observacao_emp']:
                print('>>>>> Contrato pré-aprovado, pulando esse contrato...')
                continue

            print('----------------- Iniciando análise do contrato -----------------')

            dados_atualizacao = {}
            baixa_renda = False
            id_perfil = get_id_perfil(contrato['perfil'])

            print(f'>>>>> Analisando contrato: {contrato["codigo_con"]}')
            logging.info(f"Contrato: {contrato['codigo_con']}")

            informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
            #pprint(informacoes)
            #removido
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
                    logging.info(f"Contrato: {contrato['codigo_con']} - 5T")
                    continue
                
                print('----------------- Clicando em emprestimo pessoal -----------------')
                try:
                    self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep'], By.XPATH)
                    
                    time.sleep(0.5)
                    try:
                        texto_alerta = self.act.obter_texto("//div[contains(@class,'SnackbarAlert__Content')]", By.XPATH)
                    except:
                        texto_alerta = ""
                        pass
                            
                    if 'Não é possível criar uma proposta para este CPF' in texto_alerta:
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias'], By.XPATH)
                        time.sleep(1)
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                        baixa_renda = False
                        
                except:
                    time.sleep(3)
                    baixa_renda = True
                    self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
                    
                    self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                    
                    time.sleep(0.5)
                    try:
                        texto_alerta = self.act.obter_texto("//div[contains(@class,'SnackbarAlert__Content')]", By.XPATH)
                    except:
                        texto_alerta = ""
                        pass
                    
                    if 'Não é possível criar uma proposta para este CPF' in texto_alerta:
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias_baixa_renda'], By.XPATH)
                        time.sleep(1)
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                    
                
                self.verificar_loading()
                try:

                    escolha_produto = self.act.quantidade_elemento(self.xpath['formulario_inicial']['escolha_produto'], By.XPATH)
                    self.act.clicar_elemento('/html/body/div/div/div[2]/div/div[2]/div[1]', By.XPATH)
                
                    if(escolha_produto > 0):
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias'], By.XPATH)
                        
                        if self.act.quantidade_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH) == 1:
                            baixa_renda = False
                            self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                        
                        else:
                            print('>>>>>> Tentando produto Baixa Renda')
                            baixa_renda = True
                            self.act.clicar_elemento(self.xpath['pesquisa_inicial']['botao_iniciar'], By.XPATH)
                            self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                            self.verificar_loading()
                            
                            try:
                                self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias_baixa_renda'], By.XPATH)

                                try:
                                    self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                                except:
                                    print('XXXXXXXXXXXXXXXXXXX Política Interna XXXXXXXXXXXXXXXXXXX')
                                    dados_atualizacao = {}
                                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                    dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                    logging.info(f"Contrato: {contrato['codigo_con']} - PI1")
                                    continue
                                
                            except:
                                pass
     
                except:
                    pass
                
                time.sleep(2)
                if('data-confirmation-personal-address-occupation' not in self.driver.current_url):
                    
                    self.verificar_loading()
                    print('>>>>> Verificando a aprovação')
                    formulario_inicial = False
                    
                    if self.act.quantidade_elemento(self.xpath['formulario_inicial']['nome'], By.XPATH) == 0:

                        print('>>>>> Não abriu formulário inicial, verificando se foi aprovado ou recusado...')
                        pdb.set_trace()
                        
                        if 'simulator-personal-loan' in self.driver.current_url:
                            self.preencher_valores_simulacao(informacoes, baixa_renda, contrato)
                            self.verificar_loading()

                            if self.act.quantidade_elemento('//button[contains(text(),"Continuar")]', By.XPATH):
                                print('----------------- Contrato pré-aprovado -----------------')
                                documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
                    
                                if len(documentos_pessoais) < 6:
                                    print('XXXXXXXX CPF aprovado, mas documentos estão incompletos... XXXXXXXX')
                                    dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                    print('----------------------------------------------------------------------------------------')
                                    logging.info(f"Contrato: {contrato['codigo_con']} - XX")
                                    continue
                                
                                else:
                                    
                                    baixa_renda = "ALTA RENDA"
                                    if baixa_renda:
                                        baixa_renda = "BAIXA RENDA"
                                    
                                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                                    dados_atualizacao['observacao_emp'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                                    dados_atualizacao['observacao'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                                    dados_atualizacao['erro'] = ""
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                                    print('XXXXXXXXXXXXXXXXXX TUDO OK E DOCUMENTACAO PULANDO... XXXXXXXXXXXXXXXXXX')
                                    logging.info(f"Contrato: {contrato['codigo_con']} - VV")
                                    continue
                                               
                        if 'personal-reference' in self.driver.current_url:
                            continue
                            # self.act.clicar_elemento('//span[contains(text(),"Parar")]', By.XPATH)
                            # print('>>>>> Cancelando proposta...')
                            # self.act.enviar_texto('//*[@id="select-input-reason"]', 'Sem', By.XPATH)
                            # tie.sleep(1)
                            # self.act.press_enter('//*[@id="select-input-reason"]', By.XPATH)
                            # time.sleep(1)
                            # self.act.clicar_elemento('//button[contains(text(),"CANCELAR")]', By.XPATH)
                            # self.verificar_loading()
                            
                            # if baixa_renda:
                            #     self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                            # else:
                            #     self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep'], By.XPATH)
                            
                            # self.verificar_loading()
                            
                        
                        try:
                            botao_formalizacao = self.act.quantidade_elemento('//button[contains(text(),"Formalização")]', By.XPATH)
                        except:
                            botao_formalizacao = 0
                            pass
                        
                        if botao_formalizacao == 0:
                            try:
                                botao_continuar = self.act.quantidade_elemento('//button[contains(text(),"Continuar")]', By.XPATH)
                            except:
                                botao_continuar = 0
                                pass
                            
                            if(botao_continuar == 1):
                                self.act.clicar_elemento('//button[contains(text(),"Continuar")]', By.XPATH)
                                
                            else:
                                self.driver.get('https://analysis.kapmug.com/formalization')
                                self.verificar_loading()
                                self.act.enviar_texto('//*[@id="input_text_search"]', cpf, By.XPATH)
                                time.sleep(2)
                                try:
                                    self.act.clicar_elemento('//span[contains(text(), "Cancelada")]', By.XPATH)
                                    time.sleep(2)
                                    self.verificar_loading()
                                    texto_janela = self.act.obter_texto('//*[@id="root"]', By.XPATH)
                                    
                                    if 'Cancelada pelo Cliente' in texto_janela and 'Em Andamento' not in texto_janela:
                                        
                                        print('XXXXXXXXXXXXXXXXXXXXX Cancelada pelo cliente XXXXXXXXXXXXXXXXXXXXX')
                                        
                                        dados_atualizacao = {}
                                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                        dados_atualizacao['observacao_emp'] = 'Cancelada pelo cliente'
                                        dados_atualizacao['observacao'] = 'Pedido cancelado pelo cliente'
                                        dados_atualizacao['erro'] = 'Cancelada pelo cliente'
                                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                        logging.info(f"Contrato: {contrato['codigo_con']} - CANC")
                                        continue
                                    
                                    else:
                                        
                                        print('>>>>> Classificar tela de acompanhamento FILA dossie...')
                                        
                                        dados_atualizacao = {}
                                        dados_atualizacao['mensagem'] = texto_janela
                                        dados_atualizacao['observacao_emp'] = texto_janela
                                        dados_atualizacao['observacao'] = texto_janela
                                        dados_atualizacao['erro'] = texto_janela
                                        dados_atualizacao['status_con'] = "Aguardando Comercial"
                                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                        logging.info(f"Contrato: {contrato['codigo_con']} - CLASSIF")
                                        continue
                                    
                                except:
                                    
                                    texto_janela = self.act.obter_texto('//*[@id="root"]', By.XPATH)
                                    
                                    if 'Nenhum item encontrado' in texto_janela:
                                        
                                        print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                                        dados_atualizacao = {}
                                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                        dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                        logging.info(f"Contrato: {contrato['codigo_con']} - PI5")
                                        continue
                                    
                                    else:
                                        
                                    
                                        print('TRATAR ERRO DE CONTRATO CANCELADO')
                                        pdb.set_trace()
                                        pass

                                print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                                
                                

                        
                        if botao_formalizacao == 1:
                            print('VVVVVV Contrato aprovado VVVVVV')
                            self.act.clicar_elemento('//button[contains(text(),"Formalização")]', By.XPATH)
                            time.sleep(1)
                            dados_atualizacao['linkAssinatura'] = self.act.obter_texto('/html/body/div/main/div/section/div/div[2]/div[1]/span', By.XPATH).strip().replace('http','https')
                            self.act.clicar_elemento('//button[contains(text(),"FINALIZAR")]', By.XPATH)
                            
                            self.act.enviar_texto('//*[@id="input_text_proposalOrFederalNumber"]', cpf, By.XPATH)
                            self.act.clicar_elemento('//button[contains(text(),"Buscar")]', By.XPATH)
                            time.sleep(2)

                            botao_continuar = self.act.quantidade_elemento('//button[contains(text(),"Continuar")]', By.XPATH)

                            if botao_continuar == 1:

                                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                                dados_atualizacao['ade'] = self.act.obter_texto('/html/body/div/div/div[2]/div/div[2]/section/div/div/div[1]/div/div/span[1]/span/span[1]', By.XPATH).strip()
                                dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                                dados_atualizacao['status_con'] = "Pendente"
                                dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                                dados_atualizacao['liberarDoc'] = 1
                                dados_atualizacao['pedidoDocumentacao'] = 3  
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                
                                logging.info(f"Contrato: {contrato['codigo_con']} - AP")
                                
                                continue
                        
                        try:
                            try:
                                self.act.clicar_elemento('//button[contains(text(),"Parar")]', By.XPATH)
                            except:
                                self.act.clicar_elemento('//span[contains(text(),"Parar")]', By.XPATH)
                                pass
                            
                                time.sleep(2)
                                print('>>>>> Cancelando proposta...')
                                self.act.enviar_texto('//*[@id="select-input-reason"]', 'Sem', By.XPATH)
                                time.sleep(1)
                                self.act.press_enter('//*[@id="select-input-reason"]', By.XPATH)
                                time.sleep(1)
                                self.act.clicar_elemento('//button[contains(text(),"CANCELAR")]', By.XPATH)
                                self.verificar_loading()
                                
                                dados_atualizacao['mensagem'] = "Conferir dados do contrato"
                                dados_atualizacao['observacao_emp'] = ""
                                dados_atualizacao['observacao'] = ""
                                dados_atualizacao['erro'] = ""
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                
                                logging.info(f"Contrato: {contrato['codigo_con']} - 22I")
                                
                                continue
                        
                        except:
                            print('XXXXXXXXXXXXXXXXXXXXX Duplicidade de proposta XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao = {}
                            dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                            dados_atualizacao['observacao_emp'] = 'Duplicidade de proposta'
                            dados_atualizacao['observacao'] = 'Duplicidade de proposta'
                            dados_atualizacao['erro'] = 'Duplicidade de proposta'
                            dados_atualizacao['status_con'] = "A Inserir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            logging.info(f"Contrato: {contrato['codigo_con']} - 22C")
                            
                            continue
                    
                    elif self.act.quantidade_elemento(self.xpath['formulario_inicial']['nome'], By.XPATH) == 1:
                        print('----------------- Preenchendo dados do formulário inicial -----------------')
                        self.act.enviar_texto(self.xpath['formulario_inicial']['nome'], informacoes['contrato']['nome'], By.XPATH)
                        
                        if informacoes['contrato']['dataNascimento'] is None or informacoes['contrato']['dataNascimento'] == '':
                            print('>>>>> Data de nascimento vazia, pulando esse contrato...')
                            dados_atualizacao = {}
                            dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                            dados_atualizacao['observacao_emp'] = 'Data de nascimento vazia'
                            dados_atualizacao['observacao'] = 'Data de nascimento vazia'
                            dados_atualizacao['erro'] = 'Data de nascimento vazia'
                            dados_atualizacao['status_con'] = "Aguardando Comercial"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            logging.info(f"Contrato: {contrato['codigo_con']} - DNV")
                            continue
                        
                        if 'Windows' in platform.system():
                            self.act.enviar_texto(self.xpath['formulario_inicial']['data_nascimento'], informacoes['contrato']['dataNascimento'], By.XPATH)
                        else:
                            invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
                            self.act.enviar_texto(self.xpath['formulario_inicial']['data_nascimento'], invert_data(informacoes['contrato']['dataNascimento']), By.XPATH)
                        
                        if informacoes['contrato']['renda'].count(',') == 2 or informacoes['contrato']['renda'].count('.') == 2:
                            print('>>>>> Renda com vírgula/ ponto duplo, formatando...')
                            renda_str = informacoes['contrato']['renda']
                            
                            if renda_str.count('.') == 2:
                                partes = renda_str.split('.')
                            else:
                                partes = renda_str.split(',') 

                            informacoes['contrato']['renda'] = renda_str = partes[0] + partes[1] + ',' + partes[2]
                            
                        formulario_inicial = False
                        if(self.act.quantidade_elemento(self.xpath['formulario_inicial']['renda'], By.XPATH) == 1):
                            formulario_inicial = True
                            self.act.enviar_texto(self.xpath['formulario_inicial']['renda'], "{:.2f}".format(formatar_moeda(informacoes['contrato']['renda'])), By.XPATH)

                        self.act.enviar_texto(self.xpath['formulario_inicial']['celular'], informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'], By.XPATH)
                        self.act.enviar_texto(self.xpath['formulario_inicial']['email'], informacoes['contrato']['email'], By.XPATH)

                        if formulario_inicial:
                            print('>>>>> Preenchendo Dados iniciais')
                            self.act.clicar_elemento(self.xpath['formulario_inicial']['botao_avancar'], By.XPATH)
                            self.verificar_loading()

                            try:
                                self.preencher_valores_simulacao(informacoes, baixa_renda, contrato)
                            except:
                                print('XXXXXXXXXXXXXXXXXXX ERRO EXCEPT-code05 XXXXXXXXXXXXXXXXXXX')
                                
                                try:
                                    texto_recusa = self.act.obter_texto(self.xpath['formulario_inicial']['mensagem_erro'], By.XPATH)
                                except:
                                    texto_recusa = self.act.obter_texto('//form', By.XPATH)
                                
                                if 'Encerrar' in texto_recusa or 'Operação impossibilitada de prosseguir para o CPF' in texto_recusa:
                                    print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                                    dados_atualizacao = {}
                                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                    dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                    logging.info(f"Contrato: {contrato['codigo_con']} - PI2")
                                    continue
                                
                                if 'Renda Mínima Não atingida' in texto_recusa:
                                    print('XXXXXXXXXXXXXXXXXXXXX Renda Mínima Não atingida XXXXXXXXXXXXXXXXXXXXX')
                                    self.act.clicar_elemento('//button[contains(text(),"VOLTAR")]', By.XPATH)
                                    self.verificar_loading()
                                    self.act.enviar_texto(self.xpath['formulario_inicial']['renda'],  "2000.00", By.XPATH)
                                    self.act.clicar_elemento(self.xpath['formulario_inicial']['botao_avancar'], By.XPATH)

                            self.verificar_loading()
                            
                        else:
                            
                            print('----------------- Contrato pré-aprovado -----------------')
                            documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
                
                            if len(documentos_pessoais) < 6:
                                print('XXXXXXXX CPF aprovado, mas documentos estão incompletos... XXXXXXXX')
                                dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                print('----------------------------------------------------------------------------------------')
                                logging.info(f"Contrato: {contrato['codigo_con']} - XX")
                                continue
                            
                            else:
                                
                                baixa_renda = "ALTA RENDA"
                                if baixa_renda:
                                    baixa_renda = "BAIXA RENDA"
                                
                                dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                                dados_atualizacao['observacao_emp'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                                dados_atualizacao['observacao'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                                dados_atualizacao['erro'] = ""
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                                print('XXXXXXXXXXXXXXXXXX TUDO OK E DOCUMENTACAO PULANDO... XXXXXXXXXXXXXXXXXX')
                                logging.info(f"Contrato: {contrato['codigo_con']} - VV")
                                continue
                    
                    else:
                        formulario_inicial = False
                            
                    try:
                        texto_recusa = self.act.obter_texto(self.xpath['simulacao']['mensagem_erro'], By.XPATH)

                        if 'Encerrar' in texto_recusa:
                            print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao = {}
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                            dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                            dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            logging.info(f"Contrato: {contrato['codigo_con']} - PI3")
                            continue
                        
                        else:
                            print('XXXXXXXXXXXXXXXXXXXXX Classificar recusa XXXXXXXXXXXXXXXXXXXXX')
                            pdb.set_trace()
                    except:
                        texto_recusa = ''
                        pass

                    if formulario_inicial == False:   
                        try:
                            self.act.clicar_elemento('//button[contains(text(),"Parar")]', By.XPATH)
                            time.sleep(2)
                            print('>>>>> Cancelando proposta...')
                            self.act.enviar_texto('//*[@id="select-input-reason"]', 'Sem', By.XPATH)
                            time.sleep(1)
                            self.act.press_enter('//*[@id="select-input-reason"]', By.XPATH)
                            time.sleep(1)
                            self.act.clicar_elemento('//button[contains(text(),"CANCELAR")]', By.XPATH)
                            self.verificar_loading()
                            continue
                        except Exception as e:                 
                            self.preencher_valores_simulacao(informacoes, baixa_renda, contrato)
                        
                    if 'personal-reference' in self.driver.current_url or 'residential-data' in self.driver.current_url:
                        baixa_renda = "ALTA RENDA"
                        if baixa_renda:
                            baixa_renda = "BAIXA RENDA"
                        
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                        dados_atualizacao['observacao'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                        dados_atualizacao['erro'] = ""
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                        print('XXXXXXXXXXXXXXXXXX TUDO OK E DOCUMENTACAO PULANDO... XXXXXXXXXXXXXXXXXX')
                        logging.info(f"Contrato: {contrato['codigo_con']} - VV")
                        continue

                    print('>>>>>> Definindo caminho')
                    self.verificar_loading()

                    print('----------------- Verificando se o contrato foi pre-aprovado -----------------')
                    try:
                        #REMOVER O COMENTARIO DA ATUALIACAO
                        texto_recusa = self.act.obter_texto(self.xpath['simulacao']['texto_recusa'], By.XPATH)
                        if 'Encerrar' in texto_recusa:
                            print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna produto XXXXXXXXXXXXXXXXXXXXX')
                            
                            if(baixa_renda == False):
                                print('>>>>> Recusa de contrato sem ser baixa renda. Tentando agora produto Baixa Renda')    
                                baixa_renda = True
                                self.cancelar_proposta()
                                self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
                                self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                                self.verificar_loading()
                                
                                if(self.act.quantidade_elemento(self.xpath['formulario_inicial']['renda'], By.XPATH) == 1):
                                    formulario_inicial = True
                                    
                                if formulario_inicial:
                                    print('>>>>> Preenchendo Dados iniciais')
                                    self.act.clicar_elemento(self.xpath['formulario_inicial']['botao_avancar'], By.XPATH)
                                    self.verificar_loading()
                                    self.preencher_valores_simulacao(informacoes, baixa_renda, contrato)
                                    
                                    try:
                                        texto_recusa = self.act.obter_texto(self.xpath['formulario_inicial']['mensagem_erro'], By.XPATH)
                                    except:
                                        texto_recusa = self.act.obter_texto('//form', By.XPATH)
                                    
                                    if 'Encerrar' in texto_recusa:
                                        print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                                        dados_atualizacao = {}
                                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                        dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                        logging.info(f"Contrato: {contrato['codigo_con']} - PI4")
                                        continue
                                    
                                else:
                                    print('XXXXXXXXXX CLASSIFICAR ESSE ERRO XXXXXXXXXX')
                                    pdb.set_trace()
                                
                            else:
                                dados_atualizacao = {}
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                logging.info(f"Contrato: {contrato['codigo_con']} - PI5")
                                continue
                                
                    except:
                        
                        try:
                            texto_recusa = self.act.obter_texto(self.xpath['simulacao']['texto_recusa_novo'], By.XPATH)
                            if('Valor fora do permitido') in texto_recusa and self.valor_contrato < 200:
                                print('XXXXXXXXXXXXXXXXXXXXX Valor fora do permitido XXXXXXXXXXXXXXXXXXXXX')
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = f'Valor fora do permitido {str(self.valor_contrato)}'
                                dados_atualizacao['observacao'] = 'Valor fora do permitido'
                                dados_atualizacao['erro'] = 'Valor fora do permitido'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                logging.info(f"Contrato: {contrato['codigo_con']} - VAL")
                                continue
                        except:
                            pass
                        
                        texto_recusa = ''
                        pass
                    
                    print('Pré aprovado 2... Seguindo para o preenchimento dos dados pessoais')

                documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
                
                if len(documentos_pessoais) < 6:
                    print('XXXXXXXX CPF aprovado, mas documentos estão incompletos... XXXXXXXX')
                    dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    print('----------------------------------------------------------------------------------------')
                    logging.info(f"Contrato: {contrato['codigo_con']} - XX")
                    continue
                
                else:
                
                    baixa_renda = "ALTA RENDA"
                    if baixa_renda:
                        baixa_renda = "BAIXA RENDA"
                    
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                    dados_atualizacao['observacao'] = "Pre aprovado automacao CPF e docs - " + baixa_renda
                    dados_atualizacao['erro'] = ""
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

                    print('XXXXXXXXXXXXXXXXXX TUDO OK E DOCUMENTACAO PULANDO... XXXXXXXXXXXXXXXXXX')
                    logging.info(f"Contrato: {contrato['codigo_con']} - VV")
                    continue

            except Exception as e:
                
                if 'Elemento não pôde ser encontrado' in str(e):
                    print('XXXXXXXXXXXXXXXXXXX ERRO nao encontrado XXXXXXXXXXXXXXXXXXX')
                    dados_atualizacao = {}
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = 'Element not interactable'
                    dados_atualizacao['observacao'] = 'Element not interactable'
                    dados_atualizacao['status_con'] = "A Inserir"
                    dados_atualizacao['erro'] = 'Element not interactable'
                    
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    
                    logging.info(f"Contrato: {contrato['codigo_con']} - XX ENI XX")
                    
                    self.driver.quit()
                    
                    #self.analisa_contrato()
                    
                    continue
                
                
                logging.info(f"Contrato: {contrato['codigo_con']} - EE {e}")
                
                self.driver.quit()

                # dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                # dados_atualizacao['observacao_emp'] = e
                # dados_atualizacao['observacao'] = e
                # dados_atualizacao['status_con'] = "Aguardando Comercial"
                # dados_atualizacao['erro'] = e
                # self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                continue
    
    def preencher_referencias(self, informacoes):
        print('----------------- Preenchendo Referencias -----------------')
        self.act.clicar_elemento(self.xpath['tela_referencia']['botao_adicionar_referencia'], By.XPATH)
        
        self.act.enviar_texto( self.xpath['tela_referencia']['input_nome'], informacoes['contrato']['referencia_pessoal']['nome'], By.XPATH)
        self.act.enviar_texto( self.xpath['tela_referencia']['input_celular'], informacoes['contrato']['referencia_pessoal']['telefone'], By.XPATH)
        #self.act.enviar_texto( self.xpath['tela_referencia']['input_email'], informacoes['contrato']['referencia_pessoal']['email'], By.XPATH)
        self.act.enviar_texto( self.xpath['tela_referencia']['select_tipo_referencia'], 'Pessoal', By.XPATH)
        self.act.press_enter( self.xpath['tela_referencia']['select_tipo_referencia'], By.XPATH)
        self.act.clicar_elemento( self.xpath['tela_referencia']['botao_salvar_modal'], By.XPATH)

        time.sleep(2)
        self.act.clicar_elemento(self.xpath['tela_referencia']['botao_avancar'], By.XPATH)

        self.verificar_loading()
    
    def preencher_valores_simulacao(self, informacoes, baixa_renda, contrato):
        
        dados_atualizacao = {}
        
        print('>>>>> Pré aprovado... Seguindo análise...')
        print('----------------- Preenchendo dados da simulação -----------------')
        
        valor_contrato = self.act.obter_texto(self.xpath['simulacao']['valor_contrato'], By.XPATH)
        
        if valor_contrato == 'R$ 500,00':
            print('>>>>>> Preenchendo dados do Baixa Renda') 
            informacoes['contrato']['prazo'] = '8'
            informacoes['contrato']['valorParcela'] = self.act.obter_texto('/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]', By.XPATH).replace('R$ ','')

        else:
            print('>>>>>> Preenchendo parcela do contrato')
            
            self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
            self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
            time.sleep(0.5)
            self.act.enviar_texto(self.xpath['simulacao']['input_parcela'], informacoes['contrato']['valorParcela'], By.XPATH)

            try:
                extrair_valor = lambda texto: re.search(r'R\$ ?([\d.,]+)', texto).group(1).replace('.', '')
                texto_alerta_valor = self.act.obter_texto(self.xpath['simulacao']['alerta_parcela'], By.XPATH)
                
                if('O valor não pode ser maior que' in texto_alerta_valor):
                    print('>>>>>>>> Ajustando valor da parcela')
                    informacoes['contrato']['valorParcela'] = extrair_valor(texto_alerta_valor)
                    time.sleep(3)
                    self.act.enviar_texto(self.xpath['simulacao']['input_parcela'], informacoes['contrato']['valorParcela'], By.XPATH)
            except:
                pass
            
            self.act.clicar_elemento(self.xpath['simulacao']['botao_confirmar_parcela'], By.XPATH)
            print('>>>>>> Preenchendo prazo do contrato')
            self.act.clicar_elemento(self.xpath['simulacao']['botao_prazo'], By.XPATH)
            self.act.clicar_elemento(self.xpath['simulacao']['botao_prazo'], By.XPATH)
            
            time.sleep(1)
            # if(baixa_renda):
            #     if(int(informacoes['contrato']['prazo']) > 8):
            #         informacoes['contrato']['prazo'] = '8'
            #         informacoes['contrato']['valorParcela'] = self.act.obter_texto('/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]', By.XPATH).replace('R$ ','')
                
            self.act.enviar_texto(self.xpath['simulacao']['input_prazo'], informacoes['contrato']['prazo'], By.XPATH)
            
            try:
                self.act.clicar_elemento(self.xpath['simulacao']['botao_confirmar_prazo'], By.XPATH)

            except:
                texto_alerta_prazo = self.act.obter_texto(self.xpath['simulacao']['alerta_parcela'], By.XPATH)
                
                if('O valor não pode ser maior que' in texto_alerta_prazo):
                    print('>>>>>>>> Ajustando valor do prazo')
                    extrair_valor = lambda texto: int(re.search(r'\b(\d+)\s*x', texto).group(1))
                    informacoes['contrato']['prazo'] = extrair_valor(texto_alerta_prazo)
                    self.act.enviar_texto(self.xpath['simulacao']['input_prazo'], informacoes['contrato']['prazo'], By.XPATH)
                    self.act.clicar_elemento(self.xpath['simulacao']['botao_confirmar_prazo'], By.XPATH)
                    informacoes['contrato']['valorParcela'] = self.act.obter_texto('/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]', By.XPATH).replace('R$ ','')
                    
                pass

            print('>>>>>> Atualizando o valor do contrato')
            valor_contrato = self.act.obter_texto(self.xpath['simulacao']['valor_contrato'], By.XPATH)

        dados_atualizacao['mensagem'] = 'Atualizar Valor'
        self.valor_contrato = dados_atualizacao['valorContrato'] = "{:.2f}".format(formatar_moeda(valor_contrato))
        dados_atualizacao['textoMensagem'] = 'Valores atualizados'
        dados_atualizacao['prazo'] = informacoes['contrato']['prazo']
        dados_atualizacao['valorParcela'] = informacoes['contrato']['valorParcela']
        
        print('>>>>>>>> Valores: ', dados_atualizacao)
        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
        
        print('>>>>>> Clicando em contratar')
        self.act.clicar_elemento(self.xpath['simulacao']['botao_contratar'], By.XPATH)
    
    def verificar_loading(self, interacoes = 60):
        
        print('Verificando loading...')
        retorno = True
        while ('Atualizando' in self.driver.title 
               or 'Carregando' in self.driver.title 
               or self.act.esta_presente("//div[contains(@class, 'Loading__Wrapper')]", By.XPATH)
               or self.act.quantidade_elemento('/html/body/div/main/div[2]/div/section/div/div/div', By.XPATH) == 1):
            print('Aguardando Loading...')

            if('data-confirmation-personal-address-occupation' in self.driver.current_url):
                if self.act.quantidade_elemento('/html/body/div/main/div[2]/div/section/div/ol/li[1]/div/button', By.XPATH) == 1:
                    return True
            
            if 'occupation-data' in self.driver.current_url:
                if self.act.quantidade_elemento(self.xpath['dados_pessoais']['ocupacao'], By.XPATH) == 1:
                    return True
            
            interacoes -= 1
            time.sleep(1)
            if(interacoes < 1):
                return False

        return retorno
    
    def cancelar_proposta(self):
        print('----------------- Cancelando Proposta -----------------')
        self.act.clicar_elemento('//span[contains(text(),"Parar")]', By.XPATH)
        print('>>>>> Cancelando proposta...')
        self.act.enviar_texto('//*[@id="select-input-reason"]', 'Sem', By.XPATH)
        time.sleep(1)
        self.act.press_enter('//*[@id="select-input-reason"]', By.XPATH)
        
        time.sleep(1)
        self.act.clicar_elemento('//button[contains(text(),"CANCELAR")]', By.XPATH)
        self.verificar_loading()