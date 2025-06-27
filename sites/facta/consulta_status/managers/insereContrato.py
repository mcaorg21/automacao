
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
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.pyautogui_helper import find_elements_on_screen

from sites.facta.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

import cv2
import pyautogui
import PATHS

HORARIO_COMERCIAL = 7, 22

class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False, ordem: str = 'desc'):
        super().__init__()

        self.urls = {
            "insercao": "https://desenv.facta.com.br/sistemaNovo/propostaSimulador.php"
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

        self.div_principal = 7
        
        self.cadastro_proposta_field = '17'
        
        self.xpath = {
        
            "cadastro_proposta": {
                "produto": '//*[@id="produto"]',
                "tipo_operacao" : '//*[@id="tipoOperacao"]',
                "orgao_empregador" : '//*[@id="averbador"]',
                "banco":'//*[@id="banco"]',
                "cpf":'//*[@id="cpf"]',
                "data_nascimento":'//*[@id="dataNascimento"]',
                "texto_modal_cpf":'/html/body/div[8]/div/div[2]',
                "texto_modal_cpf2":'/html/body/div[7]/div/div[2]',
                "botao_ok_cpf": f'/html/body/div[8]/div/div[6]/button[1]',
                "nome_cliente":'//*[@id="nomeCliente"]',
                "nome_social":'//*[@id="nome_social"]',
                "data_admissao":'//*[@id="ct_data_admissao"]',
                "matricula":'//*[@id="ct_matricula"]',
                "matricula_opcao_1" : '//*[@id="ct_matricula"]/option[1]',
                "valor_maximo" : '//*[@id="ct_maximo_prestacao"]',
                "celular":'//*[@id="ct_celular"]',
                "forma_envio":'//*[@id="ct_tipo_envio"]',
                "botao_enviar":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[3]/div/div[3]/button',
                "valor":'//*[@id="valor"]',
                "valor_solicitado_select":'//*[@id="opcaoValor"]',
                "prazo_solicitado":'//*[@id="prazo"]',
                "texto_resultado":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[3]/div',
                "texto_resultado2":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div',
                "texto_resultado3":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[3]/div',
                "texto_resultado4":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[2]',
                "botao_ok_whatsapp": f'/html/body/div[8]/div/div[6]/button[1]',
                "botao_ok_whatsapp2": f'/html/body/div[7]/div/div[6]/button[1]',
                "botao_pesquisar":'//*[@id="pesquisar"]',
                "resultado_pesquisa":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div/div/table/tbody/tr/td',
                "resultado_pesquisa2":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div/div/div/table/tbody/tr/td',
                "resultado_pesquisa3":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[2]/div/div/div/table/tbody/tr/td',
                "resultado_pesquisa4":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[2]/div/div/table/tbody/tr/td',
                "valor_contrato" : '/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div/div/div/table/tbody/tr[1]/td[8]',
                "valor_parcela" : '//*[@id="tdVlrParcela"]',
                "texto_modal": f'/html/body/div[8]/div/div[2]',
                "texto_modal2": f'/html/body/div[7]/div/div[2]',
                "botao_ok_modal": f'/html/body/div[8]/div/div[6]/button[1]',
                "botao_ok_modal2": f'/html/body/div[7]/div/div[6]/button[1]',
                "valor_solicitado_input":'//*[@id="valor"]',
                "div_resultado":'//*[@id="resultado"]',
                "escolha_plano":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div/div/div/table/tbody/tr[1]',
                "escolha_plano2":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[2]/div/div/div/table/tbody/tr[1]',
                "valor_contrato" : "/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[17]/div[2]/div/div/div/table/tbody/tr[1]/td[8]",
                "proxima_etapa":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/button',
                "fechar_chat": f'/html/body/div[{self.div_principal}]/img[1]'

            },
            
            "certificado": {
                "indicacao_parceiro": '//*[@id="indicacao_parceiro"]',
                "cpfVendedor": '//*[@id="cpfVendedor"]',
                "proxima_etapa": '/html/body/div[2]/section/div/div/div/div/div/div/form/div[1]/div[2]/div/button',

            }, 
              
            "cadastro_dados_pessoais": {
                "sexo": '//*[@id="sexo"]', # F ou M
                "estado_civil": '//*[@id="estadoCivil"]', # 4 - Solteiro(a), 3 - Casado(a), 2 - Divorciado(a), 5- Viúvo(a), 1 - Separado(a), 9 - União Estável
                "identidade": '//*[@id="rg"]',
                "orgao_emissor": '//*[@id="orgaoEmissor"]',
                "uf_emissor": '//*[@id="estadoRg"]',
                "data_emissao_rg": '//*[@id="emissaoRg"]',
                "nacionalidade": '//*[@id="nacionalidade"]',
                "uf_naturalidade": '//*[@id="estadoNatural"]',
                "option_naturalidade": '/html/body/div[1]/section/div[2]/div/div/div/div/div[1]/form/div/div[3]/fieldset/div[2]/div[8]/select/option',
                "cidade_naturalidade": '//*[@id="cidadeNatural"]',
                "nome_mae": '//*[@id="nomeMae"]',
                "nome_pai": '//*[@id="nomePai"]',
                "valor_patrimonio": '//*[@id="valorPatrimonio"]',
                "iletrado": '//*[@id="clienteAnalfabeto"]', # S ou N
                "matricula": '//*[@id="ct_matricula"]',
                "categoria": '//*[@id="ct_categoria"]',
                "renda": '//*[@id="ct_valor_renda"]',
                "data_admissao": '//*[@id="ct_data_admissao"]',
                "cep": '//*[@id="cep"]',
                "pesquisar_cep": '//*[@id="pesquisar_cep"]',
                "texto_modal_cep": f'/html/body/div[8]/div/div/div[2]/div',
                "botao_ok_modal": f'/html/body/div[8]/div/div/div[3]/button',
                "botao_ok_modal2": f'/html/body/div[7]/div/div/div[3]/button',
                "valor_contrato": '//*[@id="valor"]',
                "logradouro": '//*[@id="endereco"]',
                "numero": '//*[@id="numero"]',
                "complemento": '//*[@id="complemento"]',
                "bairro": '//*[@id="bairro"]',
                "select_cidade": '//*[@id="cidade"]',
                "option_cidade": '/html/body/div[1]/section/div[2]/div/div/div/div/div[1]/form/div/fieldset[2]/div[2]/div[5]/select/option',
                "celular": '//*[@id="celular"]',
                "proxima_etapa": '/html/body/div[1]/section/div[2]/div/div/div/div/div[1]/form/div/div[4]/button',
            },
            
            "liberacao_dados_profissionais": {
                'texto_modal': f'/html/body/div[8]',
                'botao_ok_modal': f'/html/body/div[8]/div/div/div[3]/button',
                "forma_pagamento": '//*[@id="forma_pagamento"]',
                "tipo_credito": '//*[@id="tipoCredito"]',
                "banco_liberacao": '//*[@id="bancoLiberacao"]',
                "agencia_iberacao": '//*[@id="agenciaLiberacao"]',
                "conta_liberacao": '//*[@id="contaLiberacao"]',
                "tipo_profissao": '//*[@id="id_tipo_profissao"]',
                "proxima_etapa": '/html/body/div[1]/section/div/div/div/div/div/div/form/div/div/button',
                "finalizar_documentos" : '/html/body/div[2]/div/div/div[2]/div[2]/button[2]',
                "numero_ade" : '/html/body/div[1]/section/div/div/div/div/div/div[2]/h3',
                "formalizacao_whatsapp" : '/html/body/div[1]/section/div/div/div/div/div/div[3]/div[2]/div[1]/input',
                "realizar_formalizacao" : '//*[@id="btnRealizaFormalizacao"]',
                "botao_ok_formalizacao": f'/html/body/div[5]/div/div/div[3]/button',
                "botao_ok_formalizacao2": f'/html/body/div[6]/div/div/div[3]/button',
                "botao_ok_formalizacao3": f'//*[@id="corpo"]/div[9]/div/div[6]/button[1]',
                "botao_ok_finalizacao": f'/html/body/div[9]/div/div[2]',
                "texto_reprovacao_final" : f'/html/body/div[1]/section/div/div/div/div/div/div[1]/div',
                "texto_final_insercao" : f'/html/body/div[1]/section/div/div/div/div/div/div[2]'
            },

            "pesquisa": {
                "campo_pesquisa_cpf": '//*[@id="cpf"]',
                "botao_pesquisar": '//*[@id="pesquisar"]',
                "link_resultado_pesquisa": '/html/body/div[1]/section/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/table/tbody/tr/td[12]/a',
                "valor_contrato" :'//*[@id="valorLiquido"]',
                "valor_parcela" : '//*[@id="valorParcela"]',
                "prazo" : '//*[@id="prazo"]',
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
    def inserir_contrato(self, configuracao: bool = False):    

        self.driver.execute_script("document.body.style.zoom='80%'")     
        print(f'Iniciando inserção de contrato... Ordem: {self.ordem}')
        
        if configuracao == False:
            fila = '1'
            if 'Windows' in platform.system():
                
                fila = input('Informe: 1- para fila ou 2- para contrato teste \n')
                
                if fila == '1':
                    self.ordem = input('Qual ordem da fila? desc ou asc? \n')
                    
                    self.deseja_escala = input('Quer escala? S ou N? \n')
                    
                    if(self.deseja_escala == 'S'):
                        self.fila_contrato = input('Qual numero dessa fila de 0 a 9?\n')
                    else:
                        self.fila_contrato = ''
                        
                else:
                    self.ordem = 'desc'
                    self.fila_contrato = ''
            
            else:
                fila = '1'
                self.fila_contrato = ''

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
            
            if(self.fila_contrato != ''):
                if self.fila_contrato != contrato['codigo_con'][-1]:
                    print('>>>>>>>>>>>>> Pulando contrato por escala <<<<<<<<<<<<<<')
                    continue
                else:
                    definir_nome_robo(f'Facta {self.fila_contrato} ESCALA Insercao')
            
            
            self.driver.get(self.urls['insercao'])

            if self.act.quantidade_elemento('//*[@id="footer-text"]', By.XPATH) == 1:
                print('Resolva o desafio')
                time.sleep(60)
                #x, y = find_elements_on_screen(cv2.imread(PATHS.project_path()+'/facta/consulta_status/managers/confirmar.jpg'))
                #pyautogui.click(141,429)
                if 'Windows' not in platform.system():
                    # Traz a janela do Chrome para frente
                    os.system("wmctrl -a 'Chrome'")
                    
                print('Clicando tentativa 1')
                pyautogui.click(593,332)
                
                time.sleep(50)
                try:
                    print('Clicando tentativa 2')
                    pyautogui.click(593,332)
                    #pyautogui.click(x,y)
                except:
                    pass
                    
                time.sleep(15)

            self.div_principal = 7
            dados_atualizacao = {}
            try:

                informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
                pprint(informacoes)
                
                dados_atualizacao['mensagem'] = 'Inserir contrato'
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                
                if 'Inserir manual o robô já tentou por 5x e não conseguiu' in contrato['observacao_emp'] or '5 tentativas ou mais' in contrato['observacao_emp']:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['observacao'] = "5 tentativas ou mais de inserção"
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = "5 tentativas ou mais de inserção"
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
                
                try:
                    print('----------------- Configurando o produto -----------------')
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['produto'], 'D', By.XPATH)
                    time.sleep(1)
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['tipo_operacao'], '13', By.XPATH)
                    time.sleep(1)
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['orgao_empregador'], '10010', By.XPATH)
                    time.sleep(1)
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['banco'], '3', By.XPATH)
                    print('-----------------------------------------------------------------')
                except:
                    print('XXXXXXXXXXXXXXXXXXXXX Erro ao configurar produto XXXXXXXXXXXXXXXXXXXXX')
                    
                    # if self.act.quantidade_elemento('//*[@id="wrapper"]', By.XPATH) == 0:
                    #     return False
                    
                    continue
                    #self.inserir_contrato()
                
                print('----------------- Configurando dados do cliente -----------------')
                self.act.enviar_texto(self.xpath['cadastro_proposta']['cpf'], informacoes['contrato']['cpf'], By.XPATH)
                self.act.clicar_elemento(self.xpath['cadastro_proposta']['data_nascimento'], By.XPATH)
                
                time.sleep(1)
                if self.verificar_loading_cadastro() == False:
                    continue
                    
                try:
                    try:
                        texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal_cpf'], By.XPATH)
                    except: 
                        texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal_cpf2'], By.XPATH)
                        pass
                    if('CPF não encontrado na base' in texto_modal):
                        print('XXXXXXXXXXXXXXXXXXXXX Erro de CPF na base XXXXXXXXXXXXXXXXXXXXX')    
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'CPF não encontrado na base'
                        dados_atualizacao['observacao'] = ''    
                        dados_atualizacao['erro'] = 'CPF não encontrado'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                except:
                    texto_modal = ""
                    pass
                
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['fechar_chat'], By.XPATH)
                except:
                    pass

                try:
                    self.act.enviar_texto(self.xpath['cadastro_proposta']['data_nascimento'], informacoes['contrato']['dataNascimento'], By.XPATH)
                except:
                    pass
                
                try:
                    self.act.enviar_texto(self.xpath['cadastro_proposta']['nome_cliente'], unidecode.unidecode(informacoes['contrato']['nome']), By.XPATH)
                except:
                    pass
                
                self.act.enviar_texto(self.xpath['cadastro_proposta']['nome_social'], unidecode.unidecode(informacoes['contrato']['nome'].split(' ')[0]), By.XPATH)
                
                self.act.enviar_texto('//*[@id="ct_data_admissao"]', informacoes['contrato']['dadosProfissionais']['admissao'], By.XPATH)
                
                print('-----------------------------------------------------------------')
                try:
                    if(self.act.quantidade_elemento(self.xpath['cadastro_proposta']['matricula'], By.XPATH) == 1):
                        print('----------------- Verificando dados do trabalhador -----------------')
                        opcoes_select = self.act.retornar_opcoes_select(self.xpath['cadastro_proposta']['matricula'], By.XPATH)
                        for i in opcoes_select: 
                            if 'Selecione' not in i.text:
                                matricula = i.text
                                i.click()
                                if self.verificar_loading_cadastro() == False:
                                    continue
                                break
                        
                        url = "https://desenv.facta.com.br/sistemaNovo/ajax/funcoes.php"    
                        payload = f'matricula={matricula}&cpf={informacoes["contrato"]["cpf"]}&acao=carregaCTMatriculas'
                        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                        response = requests.request("POST", url, headers=headers, data=payload)
                        
                        # DADOS QUE RETORNAM
                        # {
                        #     'ENCONTROU': 'S', 'CPF': '88818616153', 'MATRICULA': 
                        #     'C047S000464496', 
                        #     'GRUPO_CODIGO': '1', 
                        #     'GRUPO_NOME': 'Empregado e Trabalhador Temporário', 
                        #     'CATEGORIA_CODIGO': '101', 
                        #     'CATEGORIA_NOME': 'Empregado - Geral, inclusive o empregado público da administração direta ou indireta contratado pela CLT', 
                        #     'VALOR_RENDA': '2224.17', 'DATA_ADMISSAO': '04/09/2023', 
                        #     'CNPJ_EMPRESA': '2914460', 'ELEGIVEL': 'SIM', 'VALOR_BASE_MARGEM': '1595.65', 
                        #     'VALOR_MARGEM_DISPONIVEL': '558.48', 'VALOR_MAXIMO_PRESTACAO': '335.09', 'CNAE': '10'
                        # }

                        if response.status_code == 403:
                            retorno_valor_maximo = False
                            while retorno_valor_maximo == False:
                                try:
                                    element = self.driver.find_element(By.ID, "ct_maximo_prestacao")
                                    valor = element.get_attribute("value")
                                    retorno_valor_maximo = True
                                except:
                                    print('Aguardando o campo de valor maximo aparecer...')
                                    time.sleep(1)

                            if float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.')) >= float(valor):
                                print('>>>>>>  Usando máximo de margem disponível')
                                informacoes['contrato']['valorParcela'] = valor

                        else:
                            try:    
                                dados = json.loads(response.text)
                                if 'ENCONTROU' in dados:
                                    if dados['ENCONTROU'] == 'S':
                                        if float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.')) >= float(dados['VALOR_MAXIMO_PRESTACAO']):
                                            print('>>>>>>  Usando máximo de margem disponível')
                                            informacoes['contrato']['valorParcela'] = dados['VALOR_MAXIMO_PRESTACAO']
                                    else:
                                        try:
                                            resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado'], By.XPATH) 
                                        except:
                                            resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado3'], By.XPATH) 
                                            pass
                                        
                                        if 'não está elegível para o empréstimo' in resultado:
                                            print('XXXXXXXXXXXXXXXXXXXXX Erro de elegibilidade XXXXXXXXXXXXXXXXXXXXX')
                                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                            dados_atualizacao['observacao_emp'] = 'Não está elegível para o empréstimo'
                                            dados_atualizacao['observacao'] = ''
                                            dados_atualizacao['erro'] = 'Não está elegível para o empréstimo'
                                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)   
                                            continue 
                                        
                                        print('XXXXXXXXXXXXXXXXXXXXX TRATAR ERRO DE POST XXXXXXXXXXXXXXXXXXXXX')
                                        pdb.set_trace()
                                else:
                                    print('XXXXXXXXXXXXXXXXXXXXX TRATAR ERRO DE RESPONSE XXXXXXXXXXXXXXXXXXXXX')    
                            except:
                                pass

                        if float(informacoes['contrato']['valorParcela'].replace(',','.')) < 1:

                            print('XXXXXXXXXXXXXXXXXXXXX VALOR MARGEM QUE 1 XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Valor da margem é de menor que 1'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Valor da margem é de menor que 1'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                               
                except:
                    
                    print('----------------- Configurando dados do contato -----------------')
                    self.act.enviar_texto(self.xpath['cadastro_proposta']['celular'],'('+informacoes['contrato']['dddCelular']+') '+informacoes['contrato']['celular'][0:5]+'-'+informacoes['contrato']['celular'][5:9], By.XPATH)
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['forma_envio'], 'WHATSAPP', By.XPATH)
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_enviar'], By.XPATH)
                    time.sleep(4)
                                        
                    try:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_whatsapp'], By.XPATH)    
                    except:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_whatsapp2'], By.XPATH)    
                        pass
                    
                    print('XXXXXXXXXXXXXXXXXXX PEDIDO DE AUTORIZAÇÃO XXXXXXXXXXXXXXXXXXXXX')
                    dados_atualizacao['mensagem'] = 'Pendente Dados'
                    dados_atualizacao['textoMensagem'] = 'Enviamos um link de autorização de consulta de seus dados em seu Whatsapp. Verifique se recebeu e nos informe para dar prosseguimento. Se não tiver recebido confirme seu telefone celular com DDD'
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue
                        
                print('-----------------------------------------------------------------')
                print('----------------- Configurando valores do contrato -----------------')
                #self.act.enviar_texto(self.xpath['cadastro_proposta']['valor'], informacoes['contrato']['valorParcela'], By.XPATH)
                self.act.enviar_texto_intervalado(self.xpath['cadastro_proposta']['valor'], informacoes['contrato']['valorParcela'], By.XPATH, True, 0.1)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['valor_solicitado_select'], '2', By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_proposta']['prazo_solicitado'], informacoes['contrato']['prazo'], By.XPATH)
                
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                    time.sleep(4)
                except:
                    
                    try:
                        resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado'], By.XPATH) 
                    except:
                        resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado3'], By.XPATH) 
                        pass
                    
                    if 'não está elegível para o empréstimo' in resultado:
                        print('XXXXXXXXXXXXXXXXXXXXX Erro de elegibilidade XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Não está elegível para o empréstimo'
                        dados_atualizacao['observacao'] = ''
                        dados_atualizacao['erro'] = 'Não está elegível para o empréstimo'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)   
                        continue 
                    
    
                time.sleep(4)
                
                print('-----------------------------------------------------------------')
                print('----------------- Escolhendo o plano  -----------------')
                # pesquisar_novamente = False
                # remover_popup = self.act.quantidade_elemento('//*[@id="corpo"]/div[7]', By.XPATH)
                
                # while remover_popup == 1:
                #     try:
                #         print('>>>>> Removendo tela...')
                #         remover_popup = self.act.quantidade_elemento('//*[@id="corpo"]/div[7]', By.XPATH)
                #         self.act.clicar_elemento('/html/body/div[7]/div/div/div[3]/button', By.XPATH)
                #         pesquisar_novamente = True
                #     except:
                #         remover_popup = 0
                #         pass
                
                # if pesquisar_novamente == True:
                #     print('>>>>> Preenchendo data de nasicmento...')
                #     self.act.enviar_texto(self.xpath['cadastro_proposta']['data_nascimento'], informacoes['contrato']['dataNascimento'], By.XPATH)
                #     print('>>>>> Pesquisando novamente...')
                #     self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                #     time.sleep(4)
                
                self.driver.execute_script("document.body.style.zoom='60%'")
                resultado = ""
               
                try:
                    try: 
                        resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado3'], By.XPATH) 
                    except:
                        try:
                            resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado'], By.XPATH) 
                        except:
                            resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado4'], By.XPATH)
                        pass

                    if('não é possível cobrir o saldo devedor em nenhuma das tabelas disponíveis' in resultado or 
                        'Não foram encontradas tabelas para os filtros realizados' in resultado):
                        retorno_tabela = False
                        nova_parcela = str(round(float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.')) - 50.00,2))
                        while retorno_tabela == False:
                            
                            print(f'>>>>> Tentando novo valor de parcela...{str(nova_parcela)}')
                            
                            self.act.enviar_texto_intervalado(self.xpath['cadastro_proposta']['valor'], str(nova_parcela), By.XPATH, True, 0.1)
                            self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                            
                            try: 
                                resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado3'], By.XPATH) 
                            except:
                                try:
                                    resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado'], By.XPATH) 
                                except:
                                    resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado4'], By.XPATH)
                                pass
                            
                            if 'Não foram encontradas tabelas para os filtros realizados' in resultado or float(nova_parcela) < 80:
                                retorno_tabela = False
                                nova_parcela = round(float(nova_parcela) - 20,2)
                            
                            else:
                                informacoes['contrato']['valorParcela'] = str(nova_parcela)
                                retorno_tabela = True
                                break
                                

                        if retorno_tabela == False:
                            
                            print('XXXXXXXXXXXXXXXXXXXXX Erro de calculo de tabela XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Para as condições informadas nesta simulação, não é possível cobrir o saldo devedor em nenhuma das tabelas disponíveis'
                            dados_atualizacao['observacao'] = ''
                            dados_atualizacao['erro'] = 'Para as condições informadas nesta simulação, não é possível cobrir o saldo devedor em nenhuma das tabelas disponíveis'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"

                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            self.remove_div()                        
                            continue   
                    
                    if('Valor da operação é inferior ao mínimo permitido' in resultado):
                        
                        print('XXXXXXXXXXXXXXXXXXXXX Valor da operação é inferior ao mínimo permitido XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Valor da operação é inferior ao mínimo permitido.'
                        dados_atualizacao['observacao'] = ''
                        dados_atualizacao['erro'] = 'Valor da operação é inferior ao mínimo permitido.'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"

                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        self.remove_div()                        
                        continue  
                        
                except:
                    pass   
                 
                #self.act.obter_texto('//*[@id="resultado"]', By.XPATH)    
                try:
                    try:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano2'], By.XPATH)        
                    except:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano'], By.XPATH)
                except:
                    try:
                        texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa'], By.XPATH)
                    except:
                        texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa4'], By.XPATH)
                        pass
                    if('Valor da operação é inferior ao mínimo permitido.' in texto_resultado):
                        print('XXXXXXXXXXXXXXXXXXXXX Valor mínimo não atingido XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Valor da operação é inferior ao mínimo permitido.'
                        dados_atualizacao['observacao'] = ''
                        dados_atualizacao['erro'] = 'Valor da operação é inferior ao mínimo permitido.'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)                        
                        continue
                    
                    if('Valor solicitado maior que o permitido para a idade do cliente.' in texto_resultado):
                        retorno = True
                        while retorno == True:
                            informacoes['contrato']['prazo'] = str(int(informacoes['contrato']['prazo']) - 2)  
                            novo_prazo = str(informacoes['contrato']['prazo'])
                            print(f'>>>>>>>>>>>> Tentando novo prazo de {novo_prazo}')
                            self.act.enviar_texto(self.xpath['cadastro_proposta']['prazo_solicitado'], informacoes['contrato']['prazo'], By.XPATH)
                            self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                            
                            dados_atualizacao['prazo'] = informacoes['contrato']['prazo']
                                
                            time.sleep(3)
                            try:
                                texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa'], By.XPATH)
                            except:
                                try:
                                    texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa2'], By.XPATH)
                                except:
                                    texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_resultado4'], By.XPATH)
                                pass
                                
                            retorno = 'Não foram encontradas tabelas para os filtros realizados' in texto_resultado or 'Valor solicitado maior que o permitido para a idade do cliente' in texto_resultado
                                                               
                            if int(informacoes['contrato']['prazo']) <= 2:
                                retorno = True
                                break
                                
                            if retorno == False:
                                try:
                                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano'], By.XPATH)
                                except:
                                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano2'], By.XPATH)
                                    pass
                                break
                        
                        if retorno == True:
                            print('XXXXXXXXXXXXXXXXXXXXX Valor mínimo não atingido XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Valor solicitado maior que o permitido para a idade do cliente'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Valor solicitado maior que o permitido para a idade do cliente'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)  
                            
                            continue    
                    
                    pass
                
                print('----------------- Atualizando valor do contrato  -----------------')
                valor_contrato = self.act.obter_texto(self.xpath['cadastro_proposta']['valor_contrato'], By.XPATH)
                dados_atualizacao['valorContrato'] = valor_contrato
                dados_atualizacao['valorParcela'] = informacoes['contrato']['valorParcela'].replace('.',',')
                
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                except:
                    time.sleep(5)
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                    pass
                
                print('-----------------------------------------------------------------')                
                print('----------------- Verificando erros de simulação -----------------')
                try:
                    time.sleep(2)
                    try:
                        texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal'], By.XPATH)
                    except:
                        texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal2'], By.XPATH)
                        pass
                    
                    if('meses' not in texto_modal):
                        print('XXXXXXXXXXXXXXXXXXXXX Erro cálculo de simulação XXXXXXXXXXXXXXXXXXXXX')
                        
                        if('possui contrato em andamento' in texto_modal):
                            print('Verificando contrato em andamento 1...')
                            
                            self.driver.get('https://desenv.facta.com.br/sistemaNovo/andamentoPropostas.php')
                            cpf_formatado = informacoes['contrato']['cpf'].replace('.','').replace('-','')    
                                                 
                            campo_cpf = self.driver.find_element(By.ID, 'cpf')
                            self.act.press_backspace(self.xpath['pesquisa']['campo_pesquisa_cpf'], 20, By.XPATH)
                            campo_cpf.send_keys(cpf_formatado)
                                              
                            self.act.clicar_elemento(self.xpath['pesquisa']['botao_pesquisar'], By.XPATH)
                            time.sleep(2)
                            
                            try:
                                link_proposta = self.act.obter_atributo(self.xpath['pesquisa']['link_resultado_pesquisa'], 'href', By.XPATH)
                            except:
                                print(f'XXXX PROPOSTA NÃO EXISTE EM NOME NOSSO XXXX')
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = 'Cliente possui contrato em andamento'
                                dados_atualizacao['observacao'] = ''
                                dados_atualizacao['erro'] = 'Cliente possui contrato em andamento'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)                  
                                continue
                            
                            self.verificar_loading_cadastro()
                            dados_atualizacao = {}
                            dados_atualizacao['ade'] = link_proposta.split('codigo=')[1].split('&')[0] 
                            dados_atualizacao['valorContrato'] = self.act.obter_atributo(self.xpath['pesquisa']['valor_contrato'], 'value', By.XPATH).replace('.','').replace(',','.')
                            dados_atualizacao['valorParcela'] = self.act.obter_atributo(self.xpath['pesquisa']['valor_parcela'], 'value', By.XPATH).replace('.',',')
                            dados_atualizacao['prazo'] = self.act.obter_atributo(self.xpath['pesquisa']['prazo'], 'value', By.XPATH)

                            print('>>>>>>Realizando o post do link de assinatura') 
                            url = "https://desenv.facta.com.br/sistemaNovo/ajax/propostas/copiaLinkFormalizacao.php"    
                            payload = {'codigo': str(dados_atualizacao['ade']), 'averbador': '10010'}
                            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                            response = requests.request("POST", url, headers=headers, data=payload)
                                           
                            
                            dados_atualizacao['linkAssinatura'] = response.text.strip()
                            dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                            dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                            dados_atualizacao['status_con'] = "Pendente"
                            dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                            dados_atualizacao['liberarDoc'] = 1
                            dados_atualizacao['pedidoDocumentacao'] = 3
                            
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            
                            continue
                        
                        print(f'XXXX {texto_modal} XXXX')
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = texto_modal
                        dados_atualizacao['observacao'] = ''
                        dados_atualizacao['erro'] = texto_modal
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)                  
                        continue
                    
                    print('----------------- Recalculando proposta  -----------------')        
                    regex = r"é de (\d{1,2}) meses"          
                    prazo_maximo = re.search(regex, texto_modal).group(1)
                    
                    try:
                        regex_valor_maximo = r"(\d{1,2}\.\d{3}\,\d{2})|(\d{2,3}\,\d{2})"
                        valor_maximo = float(formatar_moeda(re.search(regex_valor_maximo, texto_modal).group(0)))
                    except:
                        pass
                    
                    try:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_modal'], By.XPATH)
                    except:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_modal2'], By.XPATH)
                        pass
                    
                    if(valor_maximo <= float(informacoes['contrato']['valorContrato'])):
                        print('>>>>> Valor máximo menor que o solicitado')
                        self.act.enviar_texto(self.xpath['cadastro_proposta']['valor_solicitado_input'], "{:.2f}".format(valor_maximo), By.XPATH)    
                        self.act.select_drop_down(self.xpath['cadastro_proposta']['valor_solicitado_select'], '1', By.XPATH)
                        dados_atualizacao['valorContrato'] = "{:.2f}".format(valor_maximo)
                    else:
                        self.act.enviar_texto(self.xpath['cadastro_proposta']['valor_solicitado_input'], "{:.2f}".format(float(informacoes['contrato']['valorContrato'])), By.XPATH)
                        self.act.select_drop_down(self.xpath['cadastro_proposta']['valor_solicitado_select'], '1', By.XPATH)
                        dados_atualizacao['valorContrato'] = "{:.2f}".format(float(informacoes['contrato']['valorContrato']))

                    self.act.enviar_texto(self.xpath['cadastro_proposta']['prazo_solicitado'], prazo_maximo, By.XPATH)
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                    time.sleep(4)

                    try:
                        try:
                            texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa3'], By.XPATH)
                        except:
                            try:
                                texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa'], By.XPATH)
                            except:
                                texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa4'], By.XPATH)
                            pass
                        
                        if('Não foram encontradas tabelas para os filtros realizados' in texto_resultado or 'Valor solicitado ou idade do cliente superior ao máximo permitido.' in texto_resultado or 'Valor solicitado maior que o permitido para a idade do cliente' in texto_resultado):
                            retorno = True
                            while retorno == True:
                                
                                valor_maximo = valor_maximo - 300
                                print(f'>>>>>>>>>>>> Tentando novo valor de R${str(valor_maximo)}')
                                self.act.enviar_texto(self.xpath['cadastro_proposta']['valor_solicitado_input'], "{:.2f}".format(valor_maximo), By.XPATH)    
                                self.act.select_drop_down(self.xpath['cadastro_proposta']['valor_solicitado_select'], '1', By.XPATH)
                                dados_atualizacao['valorContrato'] = "{:.2f}".format(valor_maximo)
                                
                                self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                                
                                time.sleep(3)
                                try:
                                    texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa3'], By.XPATH)
                                except:
                                    try:
                                        texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa2'], By.XPATH)
                                    except:
                                        try:
                                            texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa'], By.XPATH)
                                        except:
                                            texto_resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['resultado_pesquisa4'], By.XPATH)
                                            pass
                                        pass
                                    pass
                                
                                retorno = 'Não foram encontradas tabelas para os filtros realizados' in texto_resultado or 'Valor solicitado ou idade do cliente superior ao máximo permitido.' in texto_resultado or 'Valor solicitado maior que o permitido para a idade do cliente' in texto_resultado

                                if valor_maximo <= 800 or 'Valor da operação é inferior ao mínimo permitido.' in texto_resultado:
                                    retorno = True
                                    break
                                
                                if retorno == False:
                                    break
                            
                            if retorno == True:
                                print('XXXXXXXXXXXXXXXXXXXXX Valor mínimo não atingido XXXXXXXXXXXXXXXXXXXXX')
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = 'Valor solicitado maior que o permitido para a idade do cliente'
                                dados_atualizacao['observacao'] = ''    
                                dados_atualizacao['erro'] = 'Valor solicitado maior que o permitido para a idade do cliente'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)  
                            
                                continue
                        time.sleep(3)
                        # elif('Não foram encontradas tabelas para os filtros realizados' in texto_resultado):
                            
                        #     print('XXXXXXXXXXXXXXXXXXXXX Não foram encontradas tabela XXXXXXXXXXXXXXXXXXXXX')   
                        #     pdb.set_trace() 
                        #     dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        #     dados_atualizacao['observacao_emp'] = 'Não foram encontradas tabelas para os filtros realizados'
                        #     dados_atualizacao['observacao'] = ''
                        #     dados_atualizacao['erro'] = 'Não foram encontradas tabelas para os filtros realizados'
                        #     dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        #     self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        #     continue
                        
                        # else:
                        #     print('XXXXXXXXXXXXXXXXXXXXX CLASSIFICAR ERRO DE TEXTO RESULTADO XXXXXXXXXXXXXXXXXXXXX')
                        #     pdb.set_trace()

                    except:
                        pass
                       
                    print('----------------- Atualizando valor do contrato  -----------------')
                    self.driver.execute_script("document.body.style.zoom='40%'")
                    # valor_contrato = self.act.obter_texto(self.xpath['cadastro_proposta']['valor_contrato'], By.XPATH)
                    # dados_atualizacao['valorContrato'] = "{:.2f}".format(valor_maximo)
                    dados_atualizacao['prazo'] = prazo_maximo
                    dados_atualizacao['valorParcela'] = self.act.obter_texto(self.xpath['cadastro_proposta']['valor_parcela'], By.XPATH).replace('.',',')
                    print('>>>>>>>> Valores: ', dados_atualizacao)
                    
                    try:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano2'], By.XPATH)
                    except:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano'], By.XPATH)
                    
                    try:
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                    except:
                        time.sleep(5)
                        self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                        pass
                    
                    time.sleep(2)                    
                    try:
                        try:
                            texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal'], By.XPATH)
                        except:
                            texto_modal = self.act.obter_texto(self.xpath['cadastro_proposta']['texto_modal2'], By.XPATH)
                        
                        if('meses' not in texto_modal):
                            print('XXXXXXXXXXXXXXXXXXXXX Erro cálculo de simulação XXXXXXXXXXXXXXXXXXXXX')
                            
                            if('possui contrato em andamento' in texto_modal):
                                print('Verificando contrato em andamento...')
                                
                                self.driver.get('https://desenv.facta.com.br/sistemaNovo/andamentoPropostas.php')
                                cpf_formatado = informacoes['contrato']['cpf'].replace('.','').replace('-','')                            
                                campo_cpf = self.driver.find_element(By.ID, 'cpf')
                                self.act.press_backspace(self.xpath['pesquisa']['campo_pesquisa_cpf'], 20, By.XPATH)
                                campo_cpf.send_keys(cpf_formatado)
                                                
                                self.act.clicar_elemento(self.xpath['pesquisa']['botao_pesquisar'], By.XPATH)
                                time.sleep(2)
                                
                                try:
                                    link_proposta = self.act.obter_atributo(self.xpath['pesquisa']['link_resultado_pesquisa'], 'href', By.XPATH)
                                except:
                                    print(f'XXXX PROPOSTA NÃO EXISTE EM NOME NOSSO XXXX')
                                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                    dados_atualizacao['observacao_emp'] = 'Cliente possui contrato em andamento'
                                    dados_atualizacao['observacao'] = ''
                                    dados_atualizacao['erro'] = 'Cliente possui contrato em andamento'
                                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)                  
                                    continue
                                
                                self.driver.get(link_proposta)
                                
                                self.verificar_loading_cadastro()
                                dados_atualizacao = {}
                                dados_atualizacao['ade'] = link_proposta.split('codigo=')[1].split('&')[0] 
                                dados_atualizacao['valorContrato'] = self.act.obter_atributo(self.xpath['pesquisa']['valor_contrato'], 'value', By.XPATH).replace('.','').replace(',','.')
                                dados_atualizacao['valorParcela'] = self.act.obter_atributo(self.xpath['pesquisa']['valor_parcela'], 'value', By.XPATH).replace('.',',')
                                dados_atualizacao['prazo'] = self.act.obter_atributo(self.xpath['pesquisa']['prazo'], 'value', By.XPATH)

                                print('>>>>>>Realizando o post do link de assinatura') 
                                url = "https://desenv.facta.com.br/sistemaNovo/ajax/propostas/copiaLinkFormalizacao.php"    
                                payload = {'codigo': str(dados_atualizacao['ade']), 'averbador': '10010'}
                                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                                response = requests.request("POST", url, headers=headers, data=payload)
                                            
                                
                                dados_atualizacao['linkAssinatura'] = response.text.strip()
                                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                                dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                                dados_atualizacao['status_con'] = "Pendente"
                                dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                                dados_atualizacao['liberarDoc'] = 1
                                dados_atualizacao['pedidoDocumentacao'] = 3
                                
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                
                                continue
                        
                        
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = texto_modal
                            dados_atualizacao['observacao'] = ''
                            dados_atualizacao['erro'] = texto_modal
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)   
                            try:
                                self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_modal'], By.XPATH)   
                            except:
                                self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_modal2'], By.XPATH)
                                pass              
                            continue
                    
                        print('-----------------------------------------------------------------')
                    except:
                        pass
                except:
                    pass
                
                if self.verificar_loading_cadastro() == False:
                    continue

                time.sleep(3)
                print('----------------- Etapa de certificação -----------------')
                self.driver.execute_script("document.body.style.zoom='60%'")
                try:
                    self.act.select_drop_down(self.xpath['certificado']['indicacao_parceiro'], '94485', By.XPATH)
                except: 
                    self.act.select_drop_down(self.xpath['certificado']['indicacao_parceiro'], '92095', By.XPATH)
                self.act.enviar_texto(self.xpath['certificado']['cpfVendedor'], '06050694680', By.XPATH)
                self.act.clicar_elemento(self.xpath['certificado']['proxima_etapa'], By.XPATH)
                print('-----------------------------------------------------------------')
                
                if self.verificar_loading_cadastro() == False:
                    continue
                                
                print('----------------- Preechendo dados pessoais -----------------')
                self.driver.execute_script("document.body.style.zoom='50%'")
                
                print('>>>Preenchendo sexo')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['sexo'], informacoes['contrato']['sexo'][0], By.XPATH)
                
                print('>>>Preenchendo estado civil')
                switch = {'CASADO(A)': '3','SOLTEIRO(A)':'4','DIVORCIADO(A)': '2','VIÚVO(A)': '5'}        
                codigoEstadoCivil = switch.get(informacoes['contrato']['estadoCivil'].replace(" ","").upper(), '4')      
                codigoEstadoCivil = '4'          
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['estado_civil'], codigoEstadoCivil, By.XPATH)
                
                print('>>>Preenchendo identidade')
                identidade_numero = re.sub('[^0-9]', '', informacoes['contrato']['identidade'])
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['identidade'], identidade_numero, By.XPATH)
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['orgao_emissor'], 'SSP', By.XPATH)
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['uf_emissor'],  informacoes['contrato']['estadoEmissor'], By.XPATH)
                
                print('>>>Preenchendo data de emissão do RG')
                data_rg = informacoes['contrato']['dataEmissao']
                campo_data = self.driver.find_element(By.ID, 'emissaoRg')
                self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['data_emissao_rg'], 20, By.XPATH)
                campo_data.send_keys(data_rg)
                
                print('>>>Preenchendo dados de nacionalidade e naturalidade')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['nacionalidade'], '1', By.XPATH)
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['uf_naturalidade'], informacoes['contrato']['estadoNaturalidade'], By.XPATH)
                time.sleep(3)
                print('>>>Preenchendo cidade de naturalidade')
                naturalidade = unidecode.unidecode(informacoes['contrato']['naturalidade']).upper()
                opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_dados_pessoais']['cidade_naturalidade'], By.XPATH))
                
                while opcoes_select <= 5:
                    print('Aguardando carregar cidades...')
                    opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_dados_pessoais']['cidade_naturalidade'], By.XPATH))
                    time.sleep(3)

                self.act.obter_elemento_enviar_texto_clicar(self.xpath['cadastro_dados_pessoais']['cidade_naturalidade'], naturalidade, By.XPATH)
                
                print('>>>Preenchendo nome da mãe e do pai')
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['nome_mae'], unidecode.unidecode(informacoes['contrato']['nomeMae']).upper(), By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['nome_pai'], (lambda nome: nome if nome != "" else "nao declarado")(unidecode.unidecode(informacoes['contrato']['nomePai']).upper()), By.XPATH)
                
                print('>>>Preenchendo valor do patrimônio')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['valor_patrimonio'], '2', By.XPATH)
                
                print('>>>Preenchendo se é iletrado')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['iletrado'], 'N', By.XPATH)

                print('>>>Preenchendo matricula') 
                try:
                    opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_proposta']['matricula'], By.XPATH))
                    tentativa = 0   
                    while opcoes_select <= 1:
                        print('Aguardando carregar matricula...')
                        opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_proposta']['matricula'], By.XPATH))
                        time.sleep(2)
                        tentativa += 1
                        print(tentativa)
                        if tentativa >= 30:
                            continue
                            break
                                            
                    self.act.select_drop_down(self.xpath['cadastro_proposta']['matricula'], matricula, By.XPATH)
                    
                except:
                    self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['matricula'], matricula, By.XPATH)                  
                
                if self.verificar_loading_cadastro() == False:
                    continue

                try:
                    value_opcao_categoria = '101'
                    opcoes_select = self.act.retornar_opcoes_select(self.xpath['cadastro_dados_pessoais']['categoria'], By.XPATH)
                    for i in opcoes_select: 
                        if i.get_attribute('value') !='' :
                            value_opcao_categoria = i.get_attribute('value')
                            self.verificar_loading_cadastro()
                            self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['categoria'], i.get_attribute('value'), By.XPATH)
                            self.verificar_loading_cadastro()
                            print(i.text)
                            #i.click()
                            self
                            break
                    
                except:
                    pass
                
                try:
                    print('>>>Preenchendo renda') 
                    self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['renda'], informacoes['contrato']['renda'], By.XPATH)
                except:
                    pass
                #print('>>>Preenchendo matrícula, categoria, renda e data de admissão')
                #self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['matricula'], informacoes['contrato']['matricula'], By.XPATH)
                #self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['categoria'], '105', By.XPATH)
                #self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['renda'], informacoes['contrato']['renda'], By.XPATH)
                #TODO REMOVER OU MOCKUP
                # campo_data = self.driver.find_element(By.ID, 'ct_data_admissao')
                # self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['data_admissao'], 20, By.XPATH)
                # campo_data.send_keys(informacoes['contrato']['dadosProfissionais']['admissao'])
                
                print('>>>Preenchendo endereço')              
                campo_cep = self.driver.find_element(By.ID, 'cep')
                self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['cep'], 20, By.XPATH)
                campo_cep.send_keys(informacoes['contrato']['cep'])
                #self.act.clicar_elemento(self.xpath['cadastro_dados_pessoais']['pesquisar_cep'], By.XPATH)
                #time.sleep(3)
                try:
                    try:
                        texto_modal = self.act.obter_texto(self.xpath['cadastro_dados_pessoais']['texto_modal_cep'], By.XPATH)
                    except:
                        pass
 
                    if 'CEP não encontrado' in texto_modal:
                        print('XXXXXXXXXXXXXXXXXXXXX CEP NÃO ENCONTRADO XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = 'O CEP informado não foi encontrado. Informe outro CEP ou confirme o atual.'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        self.act.clicar_elemento(self.xpath['cadastro_dados_pessoais']['botao_ok_modal'], By.XPATH)
                        continue
                except:
                    pass
                
                if(len(informacoes['contrato']['logradouro'].replace('.','')) < 4):
                    informacoes['contrato']['logradouro'] = 'RUA ' + informacoes['contrato']['logradouro'].replace('.','')
                
                if informacoes['contrato'].get('numeroCasa') in [0,'0', None]:
                    informacoes['contrato']['numeroCasa'] = '1'
                    
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['logradouro'], informacoes['contrato']['logradouro'].replace('.',''), By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['numero'], informacoes['contrato']['numeroCasa'], By.XPATH) 
                
                if informacoes['contrato']['complemento'] is not None:
                    self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['complemento'], informacoes['contrato']['complemento'], By.XPATH)
                else:
                    self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['complemento'], 'CASA', By.XPATH)
                    
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['bairro'], informacoes['contrato']['bairro'].replace('.',''), By.XPATH)

                print('>>>Preenchendo cidade')   
                self.driver.execute_script("document.body.style.zoom='50%'")             
                cidade_endereco = unidecode.unidecode(informacoes['contrato']['cidade']).upper()
                opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_dados_pessoais']['select_cidade'], By.XPATH))
                while opcoes_select <= 5:
                    print('Aguardando carregar cidades...')
                    opcoes_select = len(self.act.retornar_opcoes_select(self.xpath['cadastro_dados_pessoais']['select_cidade'], By.XPATH))
                    time.sleep(1)
                
                self.act.obter_elemento_enviar_texto_clicar(self.xpath['cadastro_dados_pessoais']['select_cidade'], cidade_endereco, By.XPATH)

                print('>>>Preenchendo celular')
                campo_celular = self.driver.find_element(By.ID, 'celular')
                self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['celular'], 20, By.XPATH)
                #self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['celular'], '('+informacoes['contrato']['dddCelular']+') '+informacoes['contrato']['celular'][0:5]+'-'+informacoes['contrato']['celular'][5:9], By.XPATH)
                campo_celular.send_keys(informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'][0:5]+'-'+informacoes['contrato']['celular'][5:9])
                
                
                print('>>>Preenchendo novamente cidade Naturalidade')
                self.act.obter_elemento_enviar_texto_clicar(self.xpath['cadastro_dados_pessoais']['cidade_naturalidade'], naturalidade, By.XPATH)

                if self.act.obter_valor(self.xpath['cadastro_dados_pessoais']['categoria'], By.XPATH) == '':
                    print('>>>Preenchendo novamente categoria')    
                    self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['categoria'], value_opcao_categoria, By.XPATH)
                
                print('>>>Clicando em próxima etapa')
                self.act.clicar_elemento(self.xpath['cadastro_dados_pessoais']['proxima_etapa'], By.XPATH)
                time.sleep(4)
                if self.verificar_loading_cadastro() == False:
                    continue

                try:
                    texto_modal = self.act.obter_texto(self.xpath['liberacao_dados_profissionais']['texto_modal'], By.XPATH)

                    if('Preencha com um número de celular válido' in texto_modal):
                        print('XXXXXXXXXXXXXXXXXXXXX CELULAR VINCULADO A OUTRO CPF XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'   
                        dados_atualizacao['textoMensagem'] = 'O número de celular está vinculado a outro CPF. Informe outro número.'   
                        dados_atualizacao['observacao_emp'] = 'Celular vinculado a outro CPF.' 
                        dados_atualizacao['pedidoDocumentacao'] = 3
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    if('idade miníma' in texto_modal or 'idade máxima' in texto_modal):
                        print('XXXXXXXXXXXXXXXXXXXXX IDADE FORA DA POLÍTICA DE CRÉDITO XXXXXXXXXXXXXXXXXXXXX')   
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Idade fora da política de crédito'
                        dados_atualizacao['observacao'] = ''
                        dados_atualizacao['erro'] = 'Idade fora da política de crédito'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    try:
                        match = re.search(r'\d{1,4},\d{2}', texto_modal)
                        valor_str = match.group()  # Pega o texto encontrado (ex: "0,00")
                        valor_float = float(valor_str.replace(',', '.'))  # Troca a vírgula por ponto e converte para float
    
                        if valor_float.replace(',','.') < 1:
                            print('XXXXXXXXXXXXXXXXXXXXX VALOR MARGEM QUE 1 XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Valor da margem é de menor que 1'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Valor da margem é de menor que 1'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"    
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                    except:
                        pass
                except:
                    pass
                
                print('----------------- Preechendo Pix e Dados Bancários-----------------')
                self.act.select_drop_down(self.xpath['liberacao_dados_profissionais']['forma_pagamento'], '6', By.XPATH)
                
                try:
                    while self.act.quantidade_elemento(self.xpath['liberacao_dados_profissionais']['tipo_credito'], By.XPATH) == 0:
                        print('Aguardando abertura de formulário de dados bancários...')
                    
                    self.act.select_drop_down(self.xpath['liberacao_dados_profissionais']['tipo_credito'], 'C', By.XPATH)

                    try:
                        self.act.select_drop_down(self.xpath['liberacao_dados_profissionais']['banco_liberacao'], str(int(informacoes['contrato']['numeroBanco'])), By.XPATH)
                    except:
                        print('XXXXXXXXXXXXXXXXXXX BANCO NÃO ENCONTRADO XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = 'O banco que escolheu para depósito não está disponível para receber o crédito. Informe outro banco, agência e conta.'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                        
                    self.act.enviar_texto(self.xpath['liberacao_dados_profissionais']['agencia_iberacao'], informacoes['contrato']['agencia'], By.XPATH)
                    
                    if(informacoes['contrato']['numeroConta'][0] == '0'):
                        informacoes['contrato']['numeroConta'] = informacoes['contrato']['numeroConta'][1:]
                    
                    if(informacoes['contrato']['digitoConta'].upper() == 'X'):
                        informacoes['contrato']['digitoConta'] = '0'
                        
                    self.act.enviar_texto(self.xpath['liberacao_dados_profissionais']['conta_liberacao'], informacoes['contrato']['numeroConta']+informacoes['contrato']['digitoConta'], By.XPATH)
                
                except:
                    pass
                
                self.act.obter_elemento_enviar_texto_clicar(self.xpath['liberacao_dados_profissionais']['tipo_profissao'], informacoes['contrato']['dadosProfissionais']['profissao'], By.XPATH)

                print('----------------- CLicando em finalizar -----------------')
                #self.driver.execute_script("document.body.style.zoom='50%'")
                self.driver.find_element(By.ID, 'observacao').send_keys(Keys.END)
                self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['proxima_etapa'], By.XPATH)

                time.sleep(2)
                print('----------------- Finalizando documentos -----------------')
                try:
                    self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['finalizar_documentos'], By.XPATH)
                except:
                    pass
                
                
                if self.verificar_loading_cadastro() == False:
                    continue
                
                print('----------------- Registrando a Ade e Atualizando o Contrato -----------------')
                
                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                dados_atualizacao['status_con'] = "Pendente"
                dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                dados_atualizacao['liberarDoc'] = 1
                dados_atualizacao['pedidoDocumentacao'] = 3
                                
                try:
                    texto_ade = self.act.obter_texto(self.xpath['liberacao_dados_profissionais']['numero_ade'], By.XPATH)                    
                except:
                    texto_modal_final = ""
                    try:
                        texto_modal_final = self.act.obter_texto(self.xpath['liberacao_dados_profissionais']['botao_ok_finalizacao'], By.XPATH)
                    except:
                        texto_modal_final = self.act.obter_texto(self.xpath['liberacao_dados_profissionais']['texto_reprovacao_final'], By.XPATH)
                        pass
                    
                    if re.search(r'A conta corrente deve ter [0-9] algar[íi]smos mais o dígito verificador', texto_modal_final, re.IGNORECASE):
                        print('XXXXXXXXXXXXXXXXXXX CONTA INCORRETA XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = 'Os dados de conta corrente estão incorretos. Confirme Banco, agência e conta novamente.'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    if 'conta informada da CEF (Agência 3880) não poderá ser aceita' in texto_modal_final:
                        print('XXXXXXXXXXXXXXXXXXX CONTA NÃO ACEITA XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = 'A conta informada da CEF (Agência 3880) não poderá ser aceita para recebimento do empréstimo, pois possui limitação de movimentação mensal de valores.'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    elif 'Proposta reprovada automaticamente' in texto_modal_final:
                        print('XXXXXXXXXXXXXXXXXXXXX Reprovada automaticamente XXXXXXXXXXXXXXXXXXXXX')    
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = texto_modal_final.split('\n')[1]
                        dados_atualizacao['observacao'] = ''    
                        dados_atualizacao['erro'] = texto_modal_final.split('\n')[1]
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    elif 'O número da agência deve ser 0001' in texto_modal_final:
                        self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['botao_ok_formalizacao3'], By.XPATH)
                        self.act.enviar_texto(self.xpath['liberacao_dados_profissionais']['agencia_iberacao'], '0001', By.XPATH)
                        print('----------------- CLicando em finalizar -----------------')
                        #self.driver.execute_script("document.body.style.zoom='50%'")
                        self.driver.find_element(By.ID, 'observacao').send_keys(Keys.END)
                        self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['proxima_etapa'], By.XPATH)

                        time.sleep(2)
                        print('----------------- Finalizando documentos -----------------')
                        try:
                            self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['finalizar_documentos'], By.XPATH)
                        except:
                            pass
                        
                        if self.verificar_loading_cadastro() == False:
                            continue
                        
                        print('----------------- Registrando a Ade e Atualizando o Contrato -----------------')
                        
                        dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                        dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                        dados_atualizacao['status_con'] = "Pendente"
                        dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                        dados_atualizacao['liberarDoc'] = 1
                        dados_atualizacao['pedidoDocumentacao'] = 3

                    else:
                        print('XXXXXXXXXXXXXXXXXXX CLASSIFICAR ERRO FINAL XXXXXXXXXXXXXXXXXXXXX')
                        pdb.set_trace()

                ade = re.search(r"\b\d{8,12}\b", texto_ade).group(0)
                dados_atualizacao['ade'] = ade                
                print('>>>>>>Ade: ' + ade)
                
                url = "https://desenv.facta.com.br/sistemaNovo/ajax/propostas/copiaLinkFormalizacao.php"    
                payload = {'codigo': str(ade), 'averbador': '10010'}
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.request("POST", url, headers=headers, data=payload)
                print('>>>>>>Realizando o post do link de assinatura')                
                dados_atualizacao['linkAssinatura'] = response.text.strip()
                
                try:
                    self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['formalizacao_whatsapp'], By.XPATH)
                    time.sleep(1)
                    self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['realizar_formalizacao'], By.XPATH)
                    time.sleep(1)
                    try:
                        self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['botao_ok_formalizacao'], By.XPATH)
                    except: 
                        self.act.clicar_elemento(self.xpath['liberacao_dados_profissionais']['botao_ok_formalizacao2'], By.XPATH)
                        pass
                except:
                    try:
                        texto_final_insercao = self.act.obter_texto(self.xpath['liberacao_dados_profissionais']['texto_final_insercao'], By.XPATH)
                        if 'política de crédito' in texto_final_insercao:
                            print('XXXXXXXXXXXXXXXXXXXXX Reprovada automaticamente XXXXXXXXXXXXXXXXXXXXX')    
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = texto_final_insercao.split('\n')[1]
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = texto_final_insercao.split('\n')[1]
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                    except:
                        pass
                        pdb.set_trace()
                    pass
                
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                print('-----------------------------------------------------------------')
                print('----------------- Finalizado -----------------')
                
            except Exception as e:
                
                print(e)
                continue
                #pdb.set_trace()
                # if(self.act.quantidade_elemento('//*[@id="wrapper"]', By.XPATH) == 1):
                #     self.inserir_contrato(configuracao = True)
                # else:
                #     pdb.set_trace()
                    
                # if 'localhost' in e:
                #     #self.inserir_contrato()
                #     # self.driver.delete_all_cookies()
                #     self.driver.quit()

                # else:
                #     dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                #     dados_atualizacao['observacao_emp'] = e
                #     dados_atualizacao['observacao'] = e
                #     dados_atualizacao['status_con'] = "Aguardando Comercial"
                #     dados_atualizacao['erro'] = e
                #     self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                #     continue
        

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
    
    def verificar_loading_cadastro(self, interacoes = 60):
        
        print('Verificando loading...')
        retorno = True
        while (self.sh.buscar_quantidade_elemento('#loadGiraGira\\:visible') == 1):
            print('Aguardando Loading...')

            interacoes -= 1
            self.aguardar_consulta(1)
            if(interacoes < 1):
                return False

        return retorno

    def verificar_loading(self, interacoes=300, aguardar = False):
        time.sleep(1)

        while (self.act.quantidade_elemento('//*[@id="loadGiraGira"]', By.XPATH) == 1 or self.act.quantidade_elemento('/html/body/div[8]', By.XPATH) == 1 or self.act.quantidade_elemento('//*[@id="swal2-content"]', By.XPATH) == 1):
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


    def registra_data_rg(self,informacoes, forjar_data = False):
        self.remove_div()
        #self.driver.execute_script("""document.querySelector("body > div.loadingoverlay").remove()""")
        
                
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