
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
from sites.baseRobos.core.helpers import deleta_todos_arquivos,get_id_perfil,apagar_arquivo
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from sites.euro17.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from datetime import datetime

from sites.baseRobos.core.helpers import definir_nome_robo

HORARIO_COMERCIAL = 7, 22

class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False, ordem: str = 'desc', limite_insercoes: int = 999):
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
        self.limite_insercoes = limite_insercoes
    
        self.path_documentos = sys.path[0]+'/documentos/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+'/sites/euro17/documentos/'

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
                "input_valor_contrato" : '//*[@id="input_text_Solicitado_textfield"]',
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
                "perfil_clique": '//*[@id="natureOfOccupation"]',
                "perfil_seleciona": '//*[@id="select-input-natureOfOccupation"]',
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
    def iniciar_horario_comercial(cls, driver: Chrome, ordem, limite_insercoes=9999):

        run = InserirContrato(driver, ordem, limite_insercoes)
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
        numero_fila = '99'
        
        if 'Windows' in platform.system():
            fila = input('Informe: 1- para fila ou 2- para contrato teste \n')
            if fila == '1':
                self.ordem = input('Qual ordem da fila? desc ou asc? \n')
                numero_fila = input('De a 0 a 9 qual numero da fila? 99 para todos \n')
            else:
                self.ordem = 'desc'
                

        if(fila == '1'):
            
            contratos = self.dados.get_contratos_inserir(self.ordem)  

            if not contratos['contratos']:
                print('Sem contratos para inserir...')
                time.sleep(10)
                return False

        else:

            n_contrato = input('Informe número contrato: \n')

            while n_contrato == "":
                n_contrato = input('Informe número contrato: \n')

            perfil = input('Qual perfil? Copie do WEBADMIN')
            while perfil == "":
                perfil = input('Qual perfil? Copie do WEBADMIN')
                
            #testes
            contratos = {}
            contratos['contratos'] = [{'codigo_con' : n_contrato, 'perfil' : perfil, 'observacao_emp' : 'Pre aprovado BAIXA RENDA'}] 

        # if(numero_fila == '99'):
            #definir_nome_robo('Euro17 Inserção - Desc - Fila: Todos')
        # else:
            #definir_nome_robo(numero_fila + ' - ' + self.ordem + ' - Fila: ' + numero_fila)

        definir_nome_robo('Euro17 Inserção - ' + self.ordem)
        
        for contrato in contratos['contratos']:

            # if 'CLT' in contrato['perfil']:
            #     print(contrato['perfil'])
            #     print ('>>>>>>>>> Será tratado futuramente')
            #     continue

            if 'Pre aprovado' not in contrato['observacao_emp']:
                print(contrato['observacao_emp'])
                print ('XXXXXXXXXXXXXXXXX AINDA NAO ANALISADO PELO ROBO XXXXXXXXXXXXXXXXX')
                continue
            
            self.limite_insercoes -= 1
            
            if self.limite_insercoes < 1:
                print('Limite de inserções atingido para essa execução...')
                break
            
            print('----------------- Iniciando inserção do contrato -----------------')
            
            dados_atualizacao = {}
            baixa_renda = False
            id_perfil = get_id_perfil(contrato['perfil'])
            
            dados_atualizacao['mensagem'] = 'Inserir contrato'
            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
            
            print(f'>>>>> Inserindo contrato: {contrato["codigo_con"]}')
            
            if(contrato['codigo_con'][-1] != numero_fila and numero_fila != '99'):
                print('>>>>> Pulando esse contrato...')
                continue
            
            informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
            pprint(informacoes)
            cpf = informacoes['contrato']['cpf'].replace('-','').replace('.','')
            self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
            
            baixa_renda = False
            if 'BAIXA RENDA' in contrato['observacao_emp']:
                baixa_renda = True
                
            try:

                if 'Inserir manual o robô já tentou por 5x e não conseguiu' in contrato['observacao_emp'] or '5 tentativas ou mais' in contrato['observacao_emp']:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['observacao'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = "5 tentativas ou mais de inserção"
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
                    
                if baixa_renda:
                    print('----------------- Clicando em emprestimo pessoal BR BAIXA RENDA -----------------')
                    try:
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias_baixa_renda'], By.XPATH)
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                    except:
                        try:
                            print('----------------- Clicando em emprestimo pessoal ALTA RENDA -----------------')
                            self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
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
                            print ('XXXXXXXXX tratar erro')
                            print('----------------- Clicando em emprestimo pessoal BR BAIXA RENDA NOVAMENTE -----------------')
                            self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
                            self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                            self.verificar_loading()

                else:
                    print('----------------- Clicando em emprestimo pessoal -----------------')
                    
                    try:
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias'], By.XPATH)
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                    except:
                        self.driver.get(self.urls['insercao'].replace('|CPF|',cpf))
                        self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep'], By.XPATH)

                self.verificar_loading()

                # try:
                #     self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep'], By.XPATH)
                # except:
                #     time.sleep(10)
                #     self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep'], By.XPATH)

                #self.verificar_loading()
                
                # try:
                    
                #     escolha_produto = self.act.quantidade_elemento(self.xpath['formulario_inicial']['escolha_produto'], By.XPATH)
                #     self.act.clicar_elemento('/html/body/div/div/div[2]/div/div[2]/div[1]', By.XPATH)
                
                #     if(escolha_produto > 0):
                #         self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias'], By.XPATH)
                        
                #         if self.act.quantidade_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH) == 1:
                #             baixa_renda = False
                #             self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                        
                #         else:
                #             print('>>>>>> Tentando produto Baixa Renda')
                #             baixa_renda = True
                #             self.act.clicar_elemento(self.xpath['pesquisa_inicial']['botao_iniciar'], By.XPATH)
                #             self.act.clicar_elemento(self.xpath['formulario_inicial']['escolha_produto_ep_br'], By.XPATH)
                #             self.verificar_loading()
                            
                #             try:
                #                 self.act.clicar_elemento(self.xpath['formulario_inicial']['pendencias_baixa_renda'], By.XPATH)

                #                 try:
                #                     self.act.clicar_elemento(self.xpath['formulario_inicial']['continuar'], By.XPATH)
                #                 except:
                #                     print('XXXXXXXXXXXXXXXXXXX Política Interna XXXXXXXXXXXXXXXXXXX')
                #                     dados_atualizacao = {}
                #                     dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                #                     dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                #                     dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                #                     dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                #                     dados_atualizacao['status_con'] = "Reprovado a Conferir"
                #                     self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                #                     continue
                #                     #self.verificar_loading()
                #             except:
                #                 pass
                            
                # except:
                #     pass
                
                time.sleep(2)
                if('data-confirmation-personal-address-occupation' not in self.driver.current_url):
                    
                    self.verificar_loading()
                    print('>>>>> Verificando a aprovação')
                    
                    if 'personal-reference' in self.driver.current_url:
                        self.preencher_referencias(informacoes)

                    if self.act.quantidade_elemento(self.xpath['formulario_inicial']['nome'], By.XPATH) == 1:
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

                                if 'Cliente não elegível' in texto_recusa or 'Encerrar' in texto_recusa or 'Operação impossibilitada de prosseguir para o CPF' in texto_recusa:
                                    print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna XXXXXXXXXXXXXXXXXXXXX')
                                    dados_atualizacao = {}
                                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                    dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['observacao'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
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
                                continue
                            
                            self.preencher_dados_pessoais(informacoes)
                            self.preencher_endereco(informacoes)
                            self.preencher_ocupacao(informacoes, id_perfil)
                            self.preencher_dados_bancarios(informacoes)
                            self.confirmar_dados_pix()
                            self.preencher_referencias(informacoes)
                            self.registrar_contrato_ade(contrato)
                            self.anexar_documentos(documentos_pessoais)
                            self.finalizar_contrato()

                            print(f'VVVVVVVVV Finalizada Inserção Codigo: {contrato["codigo_con"]} VVVVVVVVV')
                            
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
                        
                    if 'personal-reference' in self.driver.current_url:
                        self.preencher_referencias(informacoes)
                                                          
                    if 'residential-data' in self.driver.current_url:
                        self.preencher_endereco(informacoes)

                    print('>>>>>> Definindo caminho')
                    self.verificar_loading()

                    print('----------------- Verificando se o contrato foi pre-aprovado -----------------')
                    try:
                        #REMOVER O COMENTARIO DA ATUALIACAO
                        texto_recusa = self.act.obter_texto(self.xpath['simulacao']['texto_recusa'], By.XPATH)
                        if 'Encerrar' in texto_recusa:
                            print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna produto 2 XXXXXXXXXXXXXXXXXXXXX')
                            
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
                                continue
                        except:
                            pass
                        
                        texto_recusa = ''
                        pass
                    
                    print('Pré aprovado 2... Seguindo para o preenchimento dos dados pessoais')

                documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
                
                # if len(documentos_pessoais) < 6:
                #     print('XXXXXXXX CPF aprovado, mas documentos estão incompletos... XXXXXXXX')
                #     dados_atualizacao['mensagem'] = 'Pendente Documentacao'
                #     self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                #     print('----------------------------------------------------------------------------------------')
                #     continue
                
                # print('----------------- Contrato foi pre-aprovado -----------------')

                atualizar = False
                if('data-confirmation-personal-address-occupation' in self.driver.current_url):
                    print('>>>>>> Passando por cada área para atualizar...')
                    atualizar = True
                    
                if('simulator-personal-loan' in self.driver.current_url):
                    print('>>>>>> Passando pelo simulador novamente...')
                    self.preencher_valores_simulacao(informacoes, baixa_renda, contrato)
                    texto_recusa = self.act.obter_texto(self.xpath['simulacao']['texto_recusa'], By.XPATH)
                    if 'Encerrar' in texto_recusa:
                        print('XXXXXXXXXXXXXXXXXXXXX Recusa de contrato por política interna produto 1 XXXXXXXXXXXXXXXXXXXXX')
                        
                        if(baixa_renda == False):
                            print('>>>>> Recusa de contrato sem ser baixa renda -  TENTATIVA 2. Tentando agora produto Baixa Renda')    
                            baixa_renda = True
                            self.act.clicar_elemento('//span[contains(text(),"Parar")]', By.XPATH)
                            print('>>>>> Cancelando proposta...')
                            self.act.enviar_texto('//*[@id="select-input-reason"]', 'Sem', By.XPATH)
                            time.sleep(1)
                            self.act.press_enter('//*[@id="select-input-reason"]', By.XPATH)
                            
                            time.sleep(1)
                            self.act.clicar_elemento('//button[contains(text(),"CANCELAR")]', By.XPATH)
                            self.verificar_loading()
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
                                self.verificar_loading()
                                
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
                                    continue
                                else:
                                    print('XXXXXXXXXX CONTINUAR PROGRAMACAO 2 XXXXXXXXXX')
                                    pdb.set_trace()  
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
                            continue
                    
                if 'dashboard' in self.driver.current_url:
                    print('XXXXXXXXXXXXXXXXXXXXX Contrato sem possibilidade de prosseguir XXXXXXXXXXXXXXXXXXXXX')
                    dados_atualizacao = {}
                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'  
                    dados_atualizacao['observacao_emp'] = 'Recusa de contrato por política interna'
                    dados_atualizacao['observacao'] = 'Recusa de contrato por política interna' 
                    dados_atualizacao['erro'] = 'Recusa de contrato por política interna'
                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
                
                if(atualizar):
                    self.act.clicar_elemento('/html/body/div/main/div[2]/div/section/div/ol/li[1]/div/button', By.XPATH)              
                    
                #if(formulario_inicial == False):
                self.preencher_dados_pessoais(informacoes)
                
                if(atualizar):
                    self.act.clicar_elemento('/html/body/div/main/div[2]/div/section/div/ol/li[2]/div/button', By.XPATH)

                #if formulario_inicial == False:
                self.preencher_endereco(informacoes)

                if(atualizar):
                    self.act.clicar_elemento('/html/body/div/main/div[2]/div/section/div/ol/li[3]/div/button', By.XPATH)
                
                #if formulario_inicial == False:
                self.preencher_ocupacao(informacoes, id_perfil)

                if(atualizar):
                    self.act.clicar_elemento(self.xpath['dados_pessoais']['botao_avancar'], By.XPATH)
                    self.verificar_loading()
                    
                #if formulario_inicial == False:
                self.preencher_dados_bancarios(informacoes)

                #if formulario_inicial == False:
                self.confirmar_dados_pix()

                #if formulario_inicial == False:
                self.preencher_referencias(informacoes)
                self.registrar_contrato_ade(contrato)
                self.anexar_documentos(documentos_pessoais)
                self.finalizar_contrato()

                print(f'VVVVVVVVV Finalizada Inserção Codigo: {contrato["codigo_con"]} VVVVVVVVV')

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
    
    def confirmar_dados_pix(self):
        print('>>>>>>>> Confirmando modal')
        try:
            texto_modal = self.act.obter_texto(self.xpath['dados_bancarios']['texto_modal'], By.XPATH)
            if 'Confirmar chave pix?' in texto_modal:
                self.act.clicar_elemento(self.xpath['dados_bancarios']['botao_avancar_modal'], By.XPATH)
            else:
                print('XXXXXXXXXXXXXXXXXXXXX Modal Classificar Nova Interacao XXXXXXXXXXXXXXXXX')
                pdb.set_trace()
        except:
            print('XXXXXXXXXXXXXXXXXXXXX Erro ao confirmar modal XXXXXXXXXXXXXXXXX')
            pdb.set_trace()
            pass
        
        self.verificar_loading()
    
    def finalizar_contrato(self, interacoes = 60):
        time.sleep(2)
        
        try:
            self.act.clicar_elemento(self.xpath['finalizacao']['finalizar_avancar'], By.XPATH)
            print('----------------- Finalizando o contrato -----------------')
            while self.act.quantidade_elemento(self.xpath['pesquisa_inicial']['cpf'], By.XPATH) == 0:
                print('Aguardando finalização...')
                time.sleep(1)
                interacoes +=1
                
                if interacoes > 60:
                    print('XXXXXX LIMITE DE INTERACOES XXXXXX') 
                    return False
                
            
            self.verificar_loading()
        
        except:
            pass
    
    def anexar_documentos(self, documentos_pessoais):
        print('----------------- Anexando documentos -----------------')

        #documentos_pessoais = buscar_documentos_contrato(informacoes['dadosContrato']['codigoContrato'])['arquivos']
        counter = 1

        try:
            for doc in documentos_pessoais:
                
                extrato_anexado = False
                
                if 'SELFIE' in doc:
                    print('>>>>>>>>> Documento selfie, pulando...')
                    continue
                
                try:
                    self.act.clicar_elemento('//button[contains(text(),"Anexar documentos")]', By.XPATH)
                except:
                    print('XXXXXXXXXXXXXXXXXXXXX Erro ao clicar em Anexar documentos XXXXXXXXXXXXXXXXX')
                    break

                id_arquivo = doc.split('/uploads')[1].split('/')[1]
                extensao = doc.split('?')[0].split('.')[-1]
                arquivo = self.path_documentos + f'{id_arquivo}_arquivo.{extensao}'

                if 'documentoPessoal' in doc:
                    label = "IDENTIFICAÇÃO"
                    if 'VERSO' in doc:
                        label = "CTPS"
                        
                elif 'COMPROVANTE_ENDERECO' in doc:
                    label = "RESIDÊNCIA"
                elif 'CONTRA_CHEQUE' in doc:
                    label = "ÚLTIMO CONTRACHEQUE"
                elif 'CONTRACHEQUE_PENuLTIMO_MeS' in doc:
                    label = "PENÚLTIMO CONTRACHEQUE"
                elif 'EXTRATO_BANCaRIO' in doc or 'ARQUIVO_PDF_DO_EXTRATO_BANCaRIO' in doc:
                    label = "EXTRATO"
                    
                if(extrato_anexado):
                    continue
                    
                print('>>>>>>>>> Selecionando na lista:', label)
                self.act.enviar_texto('//*[@id="select-input-checklist"]', label, By.XPATH)
                time.sleep(1)
                print('>>>>>>>>> Escolhendo na lista:', label)
                self.act.press_enter('//*[@id="select-input-checklist"]', By.XPATH)
                print('>>>>>>>>> Download na lista:', label)
                download(doc, arquivo)

                print('>>>>>>>>> Element:', label)
                upload = self.driver.find_element(By.XPATH,'/html/body/section/div[2]/div/div/div[2]/div/div[2]/label/input')
                print('>>>>>>>>> Send keys:', label)
                upload.send_keys(arquivo)

                time.sleep(5)
                print('>>>>>>>>> Enviando documento:', label)
                try:
                    self.act.clicar_elemento('//button[contains(text(),"Enviar documento")]', By.XPATH)
                except:
                    time.sleep(10)
                    self.act.clicar_elemento('//button[contains(text(),"Enviar documento")]', By.XPATH)
                    break
                time.sleep(5)
                counter += 1
                
                print('>>>>>>>>> Documento enviado:', label)
                print(f'>>>>> Deletando arquivo numero {id_arquivo}.')
                apagar_arquivo(arquivo)

                if 'EXTRATO_BANCaRIO' in doc or 'ARQUIVO_PDF_DO_EXTRATO_BANCaRIO' in doc:
                    extrato_anexado = True
                    
        except:
            print('XXXXXXXXXXXXXXXXXXXXX Erro ao anexar documentos XXXXXXXXXXXXXXXXX')
       
    def registrar_contrato_ade(self, contrato):
        
        dados_atualizacao = {}
        
        try:
            ade = dados_atualizacao['ade'] = self.act.obter_texto('/html/body/div/div/div[1]/div[1]/div/div[2]/div[1]/span[2]', By.XPATH).strip().split(' ')[0]
        except:
            ade = dados_atualizacao['ade'] = self.act.obter_texto(self.xpath['simulacao']['ade'], By.XPATH).strip()
        
        self.act.clicar_elemento(self.xpath['finalizacao']['link_formalizacao_button'], By.XPATH)
        time.sleep(2)
        dados_atualizacao['linkAssinatura'] = self.act.obter_texto(self.xpath['finalizacao']['link_formalizacao'], By.XPATH).strip().replace('http','https')

        self.act.clicar_elemento(self.xpath['finalizacao']['fechar_link_formalizacao'], By.XPATH)

        print('----------------- Registrando a Ade e Atualizando o Contrato -----------------')
        
        dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
        dados_atualizacao['ade'] = ade
        dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
        dados_atualizacao['status_con'] = "Pendente"
        dados_atualizacao['status_cor_con'] = "Enviado ao banco"
        dados_atualizacao['liberarDoc'] = 1
        dados_atualizacao['pedidoDocumentacao'] = 3                              

        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
        print('----------------- Finalizando -> Enviando link formalização no email -----------------')
            
        self.act.clicar_elemento(self.xpath['finalizacao']['enviar_link_formalizacao_remota'], By.XPATH)
        time.sleep(1)
        self.act.clicar_elemento(self.xpath['finalizacao']['input_email_link'], By.XPATH)
        time.sleep(1)
    
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
        
    def preencher_dados_bancarios(self, informacoes):
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
        if('CHAVE_ALEATORIA' in informacoes['contrato']['pix']['tipo']):
            self.act.enviar_texto(self.xpath['dados_bancarios']['pix_tipo'],  "Aleat", By.XPATH)
            self.act.press_enter(self.xpath['dados_bancarios']['pix_tipo'], By.XPATH)
            self.act.enviar_texto(self.xpath['dados_bancarios']['pix_chave'], informacoes['contrato']['pix']['chave'], By.XPATH)
        else:
            
            if informacoes['contrato']['pix']['tipo'] == 'INVALIDO':
                informacoes['contrato']['pix']['tipo'] = 'CPF'
                
            self.act.enviar_texto(self.xpath['dados_bancarios']['pix_tipo'],  informacoes['contrato']['pix']['tipo'], By.XPATH)
            self.act.press_enter(self.xpath['dados_bancarios']['pix_tipo'], By.XPATH)

        
        print('>>>>>>>> Clicando em avançar')
        self.act.clicar_elemento(self.xpath['dados_bancarios']['botao_avancar'], By.XPATH)
        time.sleep(2)
    
    def preencher_ocupacao(self, informacoes, id_perfil):
        
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

        self.act.enviar_texto(self.xpath['dados_pessoais']['ocupacao'], get_ocupacao(id_perfil), By.XPATH)
        time.sleep(1)
        self.act.press_enter(self.xpath['dados_pessoais']['ocupacao'], By.XPATH)
        
        
        time.sleep(1)
        if id_perfil in [1,2,3,6,7,8,9,10,11]:
            print('----------------- Preenchendo Profissão -----------------')
            self.act.enviar_texto(self.xpath['dados_pessoais']['profissao'], get_ocupacao(id_perfil), By.XPATH)
            print('----------------- Preenchendo Empresa -----------------')
            self.act.enviar_texto(self.xpath['dados_pessoais']['empresa'],  informacoes['contrato']['dadosProfissionais']['nomeEmpresa'], By.XPATH)

        elif id_perfil in [4,5]:
            print('----------------- Preenchendo Perfil -----------------')
            self.act.clicar_elemento(self.xpath['dados_pessoais']['perfil_clique'], By.XPATH)
            self.act.enviar_texto(self.xpath['dados_pessoais']['perfil_seleciona'], get_ocupacao(id_perfil), By.XPATH)
            self.act.press_enter(self.xpath['dados_pessoais']['perfil_seleciona'], By.XPATH)

        print('----------------- Preenchendo data admissao -----------------')
        pdb.set_trace()
        if 'Windows' in platform.system():
            self.act.enviar_texto(self.xpath['dados_pessoais']['data_admissao'], informacoes['contrato']['dadosProfissionais']['admissao'], By.XPATH)
        else:
            invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
            self.act.enviar_texto(self.xpath['dados_pessoais']['data_admissao'], invert_data(informacoes['contrato']['dadosProfissionais']['admissao']), By.XPATH)   
            
        print('>>>>>>>> Clicando em avançar')
        self.act.clicar_elemento(self.xpath['dados_pessoais']['botao_avancar'], By.XPATH)                
        self.verificar_loading()
    
    def preencher_endereco(self, informacoes):
        print('----------------- Preenchendo CEP -----------------')
        self.act.enviar_texto(self.xpath['dados_pessoais']['cep'], informacoes['contrato']['cep'], By.XPATH)
        #self.verificar_loading()
        time.sleep(2)
        
        print('>>>>>>>> Preenchendo endereço')
        self.act.enviar_texto(self.xpath['dados_pessoais']['endereco'], informacoes['contrato']['logradouro'], By.XPATH)
        if(informacoes['contrato']['numeroCasa'] == ''):
            informacoes['contrato']['numeroCasa'] = '1'
            
        print('>>>>>>>> Preenchendo número da casa')
        self.act.enviar_texto(self.xpath['dados_pessoais']['numero'], informacoes['contrato']['numeroCasa'], By.XPATH)

        if(informacoes['contrato']['complemento'] is None):
                informacoes['contrato']['complemento'] = 'CASA'
        
        if(informacoes['contrato']['complemento'] != ''):
            print('>>>>>>>> Preenchendo complemento')
            self.act.enviar_texto(self.xpath['dados_pessoais']['complemento'], informacoes['contrato']['complemento'], By.XPATH)
        
        print('>>>>>>>> Preenchendo bairro')
        self.act.enviar_texto(self.xpath['dados_pessoais']['bairro'], informacoes['contrato']['bairro'], By.XPATH)
            
        print('>>>>>>>> Preenchendo cidade')
        self.act.enviar_texto(self.xpath['dados_pessoais']['cidade'], informacoes['contrato']['cidade'], By.XPATH)

        print('>>>>>>>> Clicando em avançar')
        self.act.clicar_elemento("//button[normalize-space()='AVANÇAR']", By.XPATH)
        
        self.verificar_loading()
       
    def preencher_valores_simulacao(self, informacoes, baixa_renda, contrato):
        
        dados_atualizacao = {}
        
        print('>>>>> Pré aprovado... Seguindo análise...')
        print('----------------- Preenchendo dados da simulação -----------------')

        preencheu_valor_contrato = False
        if(float(informacoes['contrato']['valorContrato'].replace(',','.')) <= 300):
            print('>>>>>> Preenchendo Valor Minimo de 300 reais') 
            informacoes['contrato']['valorContrato'] = '300,00'
            self.act.clicar_elemento(self.xpath['simulacao']['valor_contrato'], By.XPATH)
            time.sleep(1)
            self.act.enviar_texto(self.xpath['simulacao']['input_valor_contrato'], informacoes['contrato']['valorContrato'], By.XPATH)
            self.act.clicar_elemento('//button[contains(text(),"Ok")]', By.XPATH)
            time.sleep(1)
            preencheu_valor_contrato = True
            
        valor_contrato = self.act.obter_texto(self.xpath['simulacao']['valor_contrato'], By.XPATH)
        
        if valor_contrato == 'R$ 500,00':
            print('>>>>>> Preenchendo dados do Baixa Renda') 
            informacoes['contrato']['prazo'] = '8'
            informacoes['contrato']['valorParcela'] = self.act.obter_texto('/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]', By.XPATH).replace('R$ ','')

        else:
            
            if(preencheu_valor_contrato == False):
                print('>>>>>> Preenchendo parcela do contrato')
                
                self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
                self.act.clicar_elemento(self.xpath['simulacao']['botao_parcela'], By.XPATH)
                time.sleep(0.5)
                
                valor_parcela_float = float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.'))
                if 60 < valor_parcela_float < 62:
                    print('>>>>>> Ajustando valor da parcela para 62 reais') 
                    informacoes['contrato']['valorParcela'] = '62,00'

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

                texto_alerta_prazo = ""
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
        
        try:
            dados_atualizacao['valorParcela'] = informacoes['contrato']['valorParcela'] = self.act.obter_texto("//p[normalize-space(text())='Parcela']/following-sibling::p[1]", By.XPATH).replace('R$','').strip()
        except:
            dados_atualizacao['valorParcela'] = informacoes['contrato']['valorParcela']
            pass
        
        print('>>>>>>>> Valores: ', dados_atualizacao)
        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
        
        print('>>>>>> Clicando em contratar')
        self.act.clicar_elemento(self.xpath['simulacao']['botao_contratar'], By.XPATH)
        
        self.verificar_loading()
    
    def preencher_dados_pessoais(self, informacoes):
        print('---------------- Preenchendo dados pessoais -----------------')
                
        print('>>>>>>>> Preenchendo sexo')
        self.act.enviar_texto(self.xpath['dados_pessoais']['sexo'], informacoes['contrato']['sexo'], By.XPATH)
        self.act.press_enter(self.xpath['dados_pessoais']['sexo'], By.XPATH)
            
        print('>>>>>>>> Preenchendo nome da mae')
        self.act.enviar_texto(self.xpath['dados_pessoais']['nome_mae'], informacoes['contrato']['nomeMae'], By.XPATH)

        print('>>>>>>>> Preenchendo nacionalidade')
        self.act.enviar_texto(self.xpath['dados_pessoais']['nacionalidade'], "Brasileira", By.XPATH)
        self.act.press_enter(self.xpath['dados_pessoais']['nacionalidade'], By.XPATH)
            
        print('>>>>>>>> Preenchendo naturalidade')  
         
        if('Candangolândia' in informacoes['contrato']['naturalidade'] or  'Ceilândia' in informacoes['contrato']['naturalidade']):
            informacoes['contrato']['naturalidade'] = 'Brasília'
            
        self.act.enviar_texto(self.xpath['dados_pessoais']['naturalidade'], informacoes['contrato']['naturalidade'][0:5], By.XPATH)
        time.sleep(3)
        self.act.press_enter(self.xpath['dados_pessoais']['naturalidade'], By.XPATH)
            
        print('>>>>>>>> Preenchendo dados do documento')
        self.act.enviar_texto(self.xpath['dados_pessoais']['tipo_documento'], 'DOCUMENTO DE IDENTIFICAÇÃO', By.XPATH)
        time.sleep(1)
        self.act.press_enter(self.xpath['dados_pessoais']['tipo_documento'], By.XPATH)
                
        print('>>>>>>>> Preenchendo número do documento')                
        self.act.enviar_texto(self.xpath['dados_pessoais']['numero_documento'], informacoes['contrato']['identidade'], By.XPATH)                
            
        if 'Windows' in platform.system():
            self.act.enviar_texto(self.xpath['dados_pessoais']['data_emissao'], informacoes['contrato']['dataEmissao'], By.XPATH)
        else:
            invert_data = lambda d: f"{d[3:5]}/{d[0:2]}/{d[6:]}"
            self.act.enviar_texto(self.xpath['dados_pessoais']['data_emissao'], invert_data(informacoes['contrato']['dataEmissao']), By.XPATH)
                
        print('>>>>>>>> Preenchendo orgão emissor')
        if 'DETRAN' in informacoes['contrato']['orgaoEmissor']:
            informacoes['contrato']['orgaoEmissor'] = 'DETRAN'
        else:
            informacoes['contrato']['orgaoEmissor'] = 'SSP'                  
        
        self.act.enviar_texto(self.xpath['dados_pessoais']['orgao_emissor'], informacoes['contrato']['orgaoEmissor'], By.XPATH)
        self.act.press_enter(self.xpath['dados_pessoais']['orgao_emissor'], By.XPATH)
            
        print('>>>>>>>> Preenchendo UF de emissão')
        self.act.enviar_texto(self.xpath['dados_pessoais']['uf_emissao'], informacoes['contrato']['estadoEmissor'], By.XPATH)
        self.act.press_enter(self.xpath['dados_pessoais']['uf_emissao'], By.XPATH)
            
        print('>>>>>>>> Preenchendo estado civil')      
        self.act.enviar_texto(self.xpath['dados_pessoais']['estado_civil'], '', By.XPATH)          
        self.act.enviar_texto(self.xpath['dados_pessoais']['estado_civil'], informacoes['contrato']['estadoCivil'][0:4], By.XPATH)
        self.act.press_enter(self.xpath['dados_pessoais']['estado_civil'], By.XPATH)
        
        
        if 'Casado' in informacoes['contrato']['estadoCivil']:
            print('>>>>>>>> Preenchendo tipo regime do conjuge')
            self.act.enviar_texto(self.xpath['dados_pessoais']['tipo_regime'], 'Comu', By.XPATH)
            time.sleep(1)
            self.act.press_enter(self.xpath['dados_pessoais']['tipo_regime'], By.XPATH)
            self.act.enviar_texto(self.xpath['dados_pessoais']['nome_conjuge'], informacoes['contrato']['conjuge'], By.XPATH)

        print('>>>>>>>> Clicando em avancar')
        self.act.clicar_elemento(self.xpath['dados_pessoais']['botao_avancar'], By.XPATH)
        self.verificar_loading()
    
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