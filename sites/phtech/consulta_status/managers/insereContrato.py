import os,time,pdb,re,requests,json,sys,os,platform,base64,unidecode
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

from sites.phtech.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource

from datetime import datetime, timedelta

import logging

import pyperclip

HORARIO_COMERCIAL = 7, 22

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='phtech_automation.log'
)
logger = logging.getLogger(__name__)

class InserirContrato(Manager,SeleniumActions):

    def __init__(self, driver: Chrome = False, ordem: str = 'desc'):
        super().__init__()

        self.urls = {
            "insercao": "https://phtech.uy3.com.br/ccb/simular"
        }

        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.atualiza = Uconecte()
        self.request_get = APIDataSource()
        self.ordem = ordem
        self.nome_banco = 'phtech'
    
        self.path_documentos = sys.path[0]+f'/sites/{self.nome_banco}/documentos/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+f'/sites/{self.nome_banco}/documentos/'

        # Dicionário de seletores XPath e CSS
        # self.act.clicar_elemento("//label[contains(text(), 'Data do primeiro pagamento')]/following-sibling::div//input", By.XPATH)
        # self.act.press_backspace("//label[contains(text(), 'Data do primeiro pagamento')]/following-sibling::div//input", 10, By.XPATH)
        # self.act.enviar_texto("//label[contains(text(), 'Data do primeiro pagamento')]/following-sibling::div//input", "03/07/2025", By.XPATH) 
        #self.act.clicar_elemento("//span[contains(text(), 'Abrir operação')]", By.XPATH)
        self.xpath = {
            "login": {
                "button": "//button[contains(text(), 'Entrar')]",
                "dashboard_label": "//div[contains(text(), 'Dashboard')]",
                "email": "input[name='email']",
                "password": "input[name='password']"
            },
            "menu": {
                "credit": "//a[contains(text(), 'Crédito')]",
                "simulate": "//a[contains(text(), 'Simular')]",
                "simulate_page_title": "//h1[contains(text(), 'Simulação')]"
            },
            "simulacao": {
                "produto_input": "//label[contains(text(), 'Produto')]/following-sibling::div//input",
                "produto_option": lambda code: f"//h6[contains(text(), '{code}')]",                
                "tipo_calculo": "//label[contains(text(), 'Tipo de cálculo')]/following-sibling::div",
                "tipo_calculo_opcao": "//li[contains(text(), 'Valor da Parcela')]",
                "parcelas_input": "//label[contains(text(), 'Quantidade de parcelas')]/following-sibling::div//input",
                "valor_input": "//label[contains(text(), 'Valor da parcela')]/following-sibling::div//input",
                "data_simular": "//label[contains(text(), 'Data do primeiro pagamento')]/following-sibling::div//input",
                "botao_simular": "//span[contains(text(), 'Simular')]",
                "resultado": "//div[contains(text(), 'Resultado da operação')]",
                "valor_contrato": "//span[contains(text(), 'Valor Líquido')]/following-sibling::p",
                "texto_alerta" : "/html/body/div/div/div[5]/div/div[2]"
            },
            "operacao": {
                "abrir_operacao": "//span[contains(text(), 'Abrir operação')]",
                "titulo_pagina": "//h1[contains(text(), 'Nova operação')]",
                "botao_salvar": "//button[@type='submit' and .//span[text()='Salvar']]",
                "confirmacao_salvar": "//span[contains(text(), 'Operação') and (contains(text(), 'criada com sucesso') or contains(text(), 'atualizada com sucesso'))]",
                "numero_operacao": "//h4[contains(text(), 'Operação #')]",
                "enviar_aprovacao": "//span[contains(text(), 'Enviar para aprovação')]",
                "aprovacao_sucesso": "//div[contains(text(), 'Operação enviada para aprovação')]",
                "enviar_aprovacao_botao": "//span[contains(text(), 'Enviar para aprovação')]",
                "alerta": "//div[contains(@class, 'alert') or contains(@class, 'warning')]"
            },
            "garantia": {
                "aba_garantia": "//a[contains(text(), 'Garantias')]",
                "botao_adicionar": "//button[contains(text(), 'Adicionar garantia')]",
                "form_titulo": "//span[contains(text(), 'Adicionar/Alterar Garantia')]",
                "tipo_dropdown": "//label[contains(text(), 'Tipo de garantia')]/following-sibling::div",
                "tipo_opcao": lambda text: f"//li[contains(text(), '{text}')]",
                "cnpj_empregador": "//label[contains(text(), 'CNPJ do Empregador')]/following::input[@id='dataprev_EmployerRegistrationNumber']",
                "nome_empregador": "//label[contains(text(), 'Nome do Empregador')]/following::input[@id='dataprev_EmployerName']",
                "matricula": "//label[contains(text(), 'Matrícula do Trabalhador')]/following::input[@id='dataprev_EmployeeCode']",
                "data_admissao": "//label[contains(text(), 'Data de admissão')]/following::input[@type='text'][1]",
                "competencia_desconto": "input[name='dataprev_DiscountStartPeriod']",
                "valor_margem": "//*[@id='totalValue']",
                "botao_adicionar_garantia": "//button[.//text()='Adicionar' and @type='submit']"
            },
            "bancario": {
                "aba_informacoes": "//a[contains(text(), 'Informações')]",
                "botao_adicionar": "//button[contains(text(), 'Adicionar dados bancários')]",
                "form_titulo": "//span[contains(text(), 'Adicionar dados bancários')]",
                "tipo_operacao": "//label[contains(text(), 'Tipo de Operação')]/following-sibling::div",
                "tipo_chave": "//label[contains(text(), 'Tipo de chave')]/following-sibling::div",
                "chave_input": lambda label: f"//label[contains(text(), '{label}')]/following-sibling::div//input",
                "botao_salvar": "//button[contains(text(), 'Salvar')]",
                "conta_liquidacao": "//label[contains(text(), 'Conta de liquidação')]/following-sibling::div",
                "opcao_pix": "//li[contains(text(), 'Pix')]"
            },
            "tomador": {
                "botao_adicionar": "//button[contains(text(), 'Adicionar tomador')]",
                "form_titulo": "//h2[contains(text(), 'Adicionar/Alterar Tomador')]",
                "tipo_cadastro": "//span[contains(text(), 'Pessoa física')]/following-sibling::div",
                "continuar": "//button[contains(text(), 'Continuar')]",
                "cpf": "input[name='registrationNumber']",
                "nome": "input[name='name']",
                "email": "input[name='email']",
                "nascimento_div": "//label[contains(text(), 'Data de nascimento')]/following-sibling::div",
                "nascimento_input": "//label[contains(text(), 'Data de nascimento')]/following-sibling::div//input",
                "nacionalidade_input": "input[name='nationality']",
                "select_estado_civil": "//label[contains(text(), 'Não Informado')]",
                "estado_civil_li": "//ul[contains(text(), 'Estado Civil')]", 
                "celular": "input[name='phone']",
                "ocupacao": "input[name='occupation']",
                "nome_mae": "input[name='mothersName']",
                "rg": "input[name='documentNumber']",
                "lista_orgao_emissor": "//div[@role='button' and @id='documentIssuer']" ,
                "orgao_emissor": lambda label: f"//li[contains(text(), '{label}')]",
                "nacionalidade": "input[name='nationality']",
                "cep": "input[name='address.zipCode']",
                "logradouro": "input[name='address.addressName']",    
                "numero": "input[name='address.number']",            
                "complemento": "input[name='address.complement']",
                "bairro": "input[name='address.district']",
                "cidade": "input[name='address.city']",
                "estado": "//label[contains(text(), 'UF')]/following::div[@role='button' and @id='address.uf']", 
                "botao_continuar": "//button[contains(text(), 'Continuar')]",
                "botao_salvar_cadastro": "//button[contains(text(), 'Salvar cadastro')]"
            },
            "alertas": {
                "sucesso": "//span[contains(text(), 'Ação realizada com sucesso')]"
            },
            "assinatura": {
                "link": "//a[contains(text(), 'Assinaturas')]",
                "copiar_link": "/html/body/div/div/form/div[6]/div/div/div[7]/div/div[3]/div/div/div[2]/div[2]/div/div/div/div/div[5]/div/button",
                "botao_atualizar": "//span[contains(text(), 'Atualizar')]",
                "botao_historico": "//a[contains(text(), 'Histórico')]",
                
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
            #fila = '2'
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

            codigo = input('Informe número contrato: \n')

            while codigo == "":
                codigo = input('Informe número contrato: \n')

            #testes
            contratos = {}
            contratos['contratos'] = [{'codigo_con' : codigo, 'observacao_emp' : "Pre aprovado"}]

        for contrato in contratos['contratos']:
            
            self.driver.get(self.urls['insercao'])
            self.div_principal = 7
            id_perfil = get_id_perfil(contrato['perfil'])
            dados_atualizacao = {}
            
            informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
            pprint(informacoes)
            
            try:    
                #11 4766-0026 whatsapp
                #link pra front end
                #https://consultadpv.phng.app/auth?redirect=/consulta
                # Login: consulta.glm
                # Senha: m9O5uw3s5d22
                
                if(id_perfil in [10]):

                    respostaSMS = requests.post('https://consultadpv.phng.dev/auth/login', data={'usuario': 'consulta.glm', 'senha': 'm9O5uw3s5d22'})
                    token = respostaSMS.json().get('token')

                    respostaSMS = requests.get('https://consultadpv.phng.dev/api/dataprev/consultar/' + informacoes['contrato']['cpf'], headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }, timeout=10)
                    
                    if respostaSMS.status_code == 500:
                        print('XXXXXXXXXXXXXXX Erro 500: Problema no servidor ao consultar o CPF XXXXXXXXXXXXXXX')
                        continue
                    
                    matriculas_elegiveis = []
                    encontrou_empresa_com_matricula = False
                    
                    if 'multiplasMatriculas' in respostaSMS.json():
                        
                        for item in respostaSMS.json()['matriculas']:
                            if(item['elegivel'] == True):
                                matriculas_elegiveis.append(item['matricula'])
                                encontrou_empresa_com_matricula = True
                        
                        if encontrou_empresa_com_matricula == False:
                            
                            print('XXXXXXXXXXXXX Nenhuma matrícula elegível encontrada. XXXXXXXXXXXXX')
                            
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Nenhuma matrícula elegível encontrada'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Nenhuma matrícula elegível encontrada'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                    if(len(matriculas_elegiveis) > 0):

                        print('>>> Múltiplas matrículas encontradas.')

                        for matricula in matriculas_elegiveis:
                            
                            payload = json.dumps({
                                "matricula": matricula
                            })

                            respostaSMS = requests.post('https://consultadpv.phng.dev/api/dataprev/consultar/' + informacoes['contrato']['cpf'], headers={
                                'Authorization': f'Bearer {token}',
                                'Content-Type': 'application/json'
                            }, data=payload, timeout=10)
                            
                            if(respostaSMS.json()['qtdEmprestimosAtivosSuspensos'] > 0):
                                print('>>> Matricula com emprestimo ativo suspenso, continuando...')
                                continue

                            valor_margem = float(respostaSMS.json().get('valorMargemDisponivelDigitacao').replace('.','').replace(',','.'))
                            
                            if(valor_margem > 0):
                                print(f'>>> Usando matrícula {matricula} com margem disponível de {valor_margem}')
                                encontrou_empresa_com_matricula = True
                                break
                            
                            if float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.')) >= float(valor_margem):
                                print('>>>>>>  Usando máximo de margem disponível')
                                informacoes['contrato']['valorParcela'] = dados['valorMargemDisponivelDigitacao']
                        
                            if not encontrou_empresa_com_matricula:
                                
                                print('>>> Nenhuma matrícula elegível encontrada.')
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = 'Nenhuma matrícula elegível encontrada'
                                dados_atualizacao['observacao'] = ''    
                                dados_atualizacao['erro'] = 'Nenhuma matrícula elegível encontrada'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue

                    texto_mensagem = respostaSMS.json().get('mensagem')              

                    if respostaSMS.status_code == 409:
                        
                        if("Valor de remuneração zerado" in texto_mensagem):
                            
                            print('XXXXXXXXXXXXXXXXXXXXX Sem remuneração XXXXXXXXXXXXXXXXXXXXX')    
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'CPF não encontrado na base'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'CPF não encontrado'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                        if("Empréstimo legado informado pela instituição financeira" in texto_mensagem):
                            
                            print('XXXXXXXXXXXXXXXXXXXXX Sem remuneração XXXXXXXXXXXXXXXXXXXXX')    
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Cliente possui contrato em andamento'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Cliente possui contrato em andamento'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue

                        if("Vínculo com data de desligamento" in texto_mensagem):

                            print('XXXXXXXXXXXXXXXXXXXXX Possui data de desligamento XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Cliente com data de desligamento'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'Cliente com data de desligamento'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                        if("Sem remuneração na última competência" in texto_mensagem):

                            print('XXXXXXXXXXXXXXXXXXXXX Sem remuneração na última competência XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Cliente sem remuneração na última competência'
                            dados_atualizacao['observacao'] = ''
                            dados_atualizacao['erro'] = 'Cliente sem remuneração na última competência'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue

                        if('Empréstimo legado registrado no eSocial' in texto_mensagem):

                            print('XXXXXXXXXXXXXXXXXXXXX Empréstimo legado registrado no eSocial XXXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Cliente com empréstimo legado registrado no eSocial'
                            dados_atualizacao['observacao'] = ''
                            dados_atualizacao['erro'] = 'Cliente com empréstimo legado registrado no eSocial'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                        print('XXXXXXXXXXXXXXXXXXX CLASSIFICAR NOVO ERRO 409 XXXXXXXXXXXXXXXXXXXXX')
                        pdb.set_trace()
                        # CPF já cadastrado, tratar erro
                        print(">>>> Erro 409: CPF já cadastrado no sistema")
                        print('XXXXXXXXXXXXXXXXXXX PEDIDO DE AUTORIZAÇÃO XXXXXXXXXXXXXXXXXXXXX')
                        dados_atualizacao['mensagem'] = 'Pendente Dados'
                        dados_atualizacao['textoMensagem'] = 'Adicione o Whatsapp (11)4766-0026 para dar autorização de consulta de seus dados. Assim que fizer nos informe por aqui.'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue
                    
                    elif respostaSMS.status_code == 404:
                        
                        if('CPF não encontrado na base' in texto_mensagem):
                            print('XXXXXXXXXXXXXXXXXXXXX Erro de CPF na base XXXXXXXXXXXXXXXXXXXXX')    
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'CPF não encontrado na base'
                            dados_atualizacao['observacao'] = ''    
                            dados_atualizacao['erro'] = 'CPF não encontrado'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                        elif 'Trabalhador nao autorizado para consulta' in texto_mensagem:
                            
                            data={
                                    'cpf': informacoes['contrato']['cpf'],
                                    'numero': informacoes['contrato']['dddCelular'] + informacoes['contrato']['celular'],
                                    'primeiroNome': informacoes['contrato']['nome'].split(' ')[0],
                                }
                            
                            resposta = requests.post('https://consultadpv.phng.dev/api/dataprev/enviarSms', headers={
                                'Authorization': f'Bearer {token}',
                                'Content-Type': 'application/json'
                            }, data=data, timeout=10)
                            
                            texto_mensagem = resposta.json().get('mensagem')
                            
                            if "SMS Enviado com sucesso" in texto_mensagem:
                                print('XXXXXXXXXXXXXXXXXXX PEDIDO DE AUTORIZAÇÃO XXXXXXXXXXXXXXXXXXXXX')
                                print('SMS enviado com sucesso para o CPF:', informacoes['contrato']['cpf'])
                                dados_atualizacao['mensagem'] = 'Pendente Dados'
                                dados_atualizacao['textoMensagem'] = 'Enviamos um link de autorização de consulta de seus dados via SMS. Se o SMS não chegar adicione o Whatsapp (11)4766-0026 para dar autorização. Assim que fizer nos informe por aqui.'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue
                            
                            if "Numero de telefone ja cadastrado para outro cpf" in texto_mensagem:
                                print('XXXXXXXXXXXXXXXXXXX PEDIDO DE AUTORIZAÇÃO XXXXXXXXXXXXXXXXXXXXX')
                                print('Mensagem para adicionar Whatsapp enviada para o CPF:', informacoes['contrato']['cpf'])
                                dados_atualizacao['mensagem'] = 'Pendente Dados'
                                dados_atualizacao['textoMensagem'] = 'Adicione o Whatsapp (11)4766-0026 para dar autorização de consulta de seus dados. Assim que fizer nos informe por aqui.'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue
                            
                            
                            
                        else:
                            print('XXXXXXXX TRATAMENTO DE ERRO 404 XXXXXXXXXXXXXXX')
                            pdb.set_trace()
                            
                    elif respostaSMS.status_code == 200:
                        print('VVVVVVVVVVV ENCONTRADO CADASTRO - 200 VVVVVVVVVVV')
                        
                        if 'cnae' in respostaSMS.text:
                            
                            dados = respostaSMS.json()
                            #{'cpf': 37199980884, 'matricula': '232', 'empregador': 'CNPJ - 66699125', 'nomeEmpregador': 'CAMPO VERDE DISTRIBUIDORA DE GENEROS ALIMENTICIOS LTDA', 'nome': 'RODNEI EMILIO SANTARELLI', 'nomeMae': 'EURIDES DE SANTANA SANTARELLI', 'sexo': 'Masculino', 'dataNascimento': '08/09/1986', 'dataNascimentoDetalhada': '38 anos, 9 meses e 2 dias', 'elegibilidadeDataNascimento': True, 'codigoCategoriaTrabalhador': 101, 'elegibilidadeCodigoCategoriaTrabalhador': True, 'elegivel': True, 'motivoInelegibilidade': '', 'dataAdmissao': '16/12/2024', 'elegibilidadeAdmissao': False, 'pessoaExpostaPoliticamente': 'Pessoa Não Exposta Politicamente', 'elegibilidadePessoaExpostaPoliticamente': True, 'dataInicioAtividadeEmpregador': '08/08/1991', 'elegibilidadeDataInicioAtividadeEmpregador': True, 'paisNacionalidade': 'BRASIL', 'cbo': '783210 - CARREGADOR (ARMAZEM)', 'cnae': '4639701 - COMERCIO ATACADISTA DE PRODUTOS ALIMENTICIOS EM GERAL', 'qtdEmprestimosAtivosSuspensos': 1, 'elegibilidadeQtdEmprestimosAtivosSuspensos': False, 'valorTotalVencimentos': '2.940,76', 'valorBaseMargem': '1.830,94', 'valorMargemDisponivel': '315,63', 'valorMargemDisponivelDigitacao': '157,82', 'prazoMinimno': 0, 'prazoMaximo': 0, 'valorMaximo': '0,00', 'telefone': 11958478978}
                            print(f'>>> Dados encontrados na consulta. Margem: {dados['valorMargemDisponivelDigitacao']}')

                            valor_margem = float(dados['valorMargemDisponivelDigitacao'].replace('.','').replace(',','.'))
                            
                            if valor_margem < 1:
                                
                                print(f'XXXXXXXXXXXXXXXXXXX Valor margem: {str(valor_margem)} XXXXXXXXXXXXXXXXXXXX')
                                            
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = f'Valor menor do que o permitido para o produto - Margem {str(valor_margem)}'
                                dados_atualizacao['observacao'] = f'Valor menor do que o permitido para o produto - Margem {str(valor_margem)}'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"    
                                dados_atualizacao['erro'] = f'Valor menor do que o permitido para o produto - Margem {str(valor_margem)}'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue
                    
                            if float(informacoes['contrato']['valorParcela'].replace('.','').replace(',','.')) >= float(valor_margem):
                                print('>>>>>>  Usando máximo de margem disponível')
                                informacoes['contrato']['valorParcela'] = dados['valorMargemDisponivelDigitacao']
                            else:
                                informacoes['contrato']['valorParcela'] = informacoes['contrato']['valorParcela']
                            
                            informacoes['contrato']['dadosProfissionais']['cnpjEmpresa'] = dados['empregador'].replace('CNPJ - ','').replace('CNPJ -','').strip()
                            informacoes['contrato']['dadosProfissionais']['nomeEmpresa'] = dados['nomeEmpregador']   
                            informacoes['contrato']['dadosProfissionais']['admissao'] = dados['dataAdmissao']
                            informacoes['contrato']['dadosProfissionais']['matricula'] = dados['matricula']
                            
                            dados_atualizacao['valorParcela'] = informacoes['contrato']['valorParcela']

                        else:
                            data={
                                    'cpf': informacoes['contrato']['cpf'],
                                    'numero': informacoes['contrato']['dddCelular'] + informacoes['contrato']['celular'],
                                    'primeiroNome': informacoes['contrato']['nome'].split(' ')[0],
                                }
                            
                            resposta = requests.post('https://consultadpv.phng.dev/api/dataprev/enviarSms', headers={
                                'Authorization': f'Bearer {token}',
                                'Content-Type': 'application/json'
                            }, data=data, timeout=10)
                            
                            texto_mensagem = resposta.json().get('mensagem')
                            
                            if "SMS Enviado com sucesso" in texto_mensagem:
                                print('XXXXXXXXXXXXXXXXXXX PEDIDO DE AUTORIZAÇÃO XXXXXXXXXXXXXXXXXXXXX')
                                print('SMS enviado com sucesso para o CPF:', informacoes['contrato']['cpf'])
                                dados_atualizacao['mensagem'] = 'Pendente Dados'
                                dados_atualizacao['textoMensagem'] = 'Enviamos um link de autorização de consulta de seus dados via SMS. Se o SMS não chegar adicione o Whatsapp (11)4766-0026 para dar autorização. Assim que fizer nos informe por aqui.'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue


                        # {
                        #     "cbo": "783210 - CARREGADOR (ARMAZEM)",
                        #     "cnae": "4639701 - COMERCIO ATACADISTA DE PRODUTOS ALIMENTICIOS EM GERAL",
                        #     "codigoCategoriaTrabalhador": 101,
                        #     "cpf": "37199980884",
                        #     "dataAdmissao": "16/12/2024",
                        #     "dataInicioAtividadeEmpregador": "08/08/1991",
                        #     "dataNascimento": "08/09/1986",
                        #     "dataNascimentoDetalhada": "38 anos, 9 meses e 2 dias",
                        #     "elegibilidadeAdmissao": false,
                        #     "elegibilidadeCodigoCategoriaTrabalhador": true,
                        #     "elegibilidadeDataInicioAtividadeEmpregador": true,
                        #     "elegibilidadeDataNascimento": true,
                        #     "elegibilidadePessoaExpostaPoliticamente": true,
                        #     "elegibilidadeQtdEmprestimosAtivosSuspensos": false,
                        #     "elegivel": true,
                        #     "empregador": "CNPJ - 66699125",
                        #     "matricula": "232",
                        #     "motivoInelegibilidade": "",
                        #     "nome": "RODNEI EMILIO SANTARELLI",
                        #     "nomeEmpregador": "CAMPO VERDE DISTRIBUIDORA DE GENEROS ALIMENTICIOS LTDA",
                        #     "nomeMae": "EURIDES DE SANTANA SANTARELLI",
                        #     "paisNacionalidade": "BRASIL",
                        #     "pessoaExpostaPoliticamente": "Pessoa Não Exposta Politicamente",
                        #     "prazoMaximo": 0,
                        #     "prazoMinimno": 0,
                        #     "qtdEmprestimosAtivosSuspensos": 1,
                        #     "sexo": "Masculino",
                        #     "telefone": "11958478978",
                        #     "valorBaseMargem": "1.830,94",
                        #     "valorMargemDisponivel": "315,63",
                        #     "valorMargemDisponivelDigitacao": "157,82",
                        #     "valorMaximo": "0,00",
                        #     "valorTotalVencimentos": "2.940,76"
                        #     }

                    else:
                        print('XXXXXXXX TRATAMENTO DE ERRO XXXXXXXXXXXXXXX')
                        pdb.set_trace()
                
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

                    # Selecionar produto    
                    
                    #idperfil 10 
                    produto_selecionar = "3010499" #CONSIGNADO CLT
                    if id_perfil == 2:  
                        produto_selecionar = "2010180" #CONSIGNADO SERVIDOR PUBLICO

                    if not self.selecionar_produto(produto_selecionar):
                        raise Exception("Falha ao selecionar produto")

                    # Definir tipo de cálculo
                    if not self.definir_tipo_calculo():
                        raise Exception("Falha ao definir tipo de cálculo")
                    
                    # Definir valor solicitado
                    if not self.definir_valor_parcela(informacoes['contrato']['valorParcela']):
                        raise Exception("Falha ao definir valor parcela")
                    
                    # Definir número de parcelas
                    if not self.definir_parcelas(informacoes['contrato']['prazo']):
                        raise Exception("Falha ao definir número de parcelas")
                    
                    # Definir data do primeiro pagamento
                    if not self.definir_data_primeiro_pagamento():
                        raise Exception("Falha ao definir data do primeiro pagamento")

                    # Executar simulação
                    if not self.executar_simulacao():
                        raise Exception("Falha ao executar simulação")

                    try:
                        texto_alerta = self.act.obter_texto(self.xpath['simulacao']['texto_alerta'], By.XPATH)
                    except Exception as e:
                        texto_alerta = None
                        
                    if texto_alerta is not None:
                        
                        if 'é menor do que o permitido para o produto' in texto_alerta:
                            
                            print(f'XXXXXXXXXXXXXXXXXXX Valor menor margem: {respostaSMS.json()['valorMargemDisponivelDigitacao']} XXXXXXXXXXXXXXXXXXXX')
                            
                            reprova_valor_maximo = True
                            
                            if int(informacoes['contrato']['prazo']) < 36:

                                informacoes['contrato']['prazo'] = '36'
                                print('>>>> Tentando prazo máximo')                                
                                self.definir_parcelas('36')
                                self.executar_simulacao()
                                
                                time.sleep(5)
                                
                                try:
                                    texto_alerta = self.act.obter_texto(self.xpath['simulacao']['texto_alerta'], By.XPATH)
                                except:
                                    texto_alerta = ''
                                    
                                if 'é menor do que o permitido para o produto' in texto_alerta:
                                    reprova_valor_maximo = True
                                else:
                                    reprova_valor_maximo = False
                                    print('>>>> Prazo máximo aceito')
                                    dados_atualizacao['valorContrato'] = '36'

                            if reprova_valor_maximo: 
                                
                                print('XXXXXXXXXXXXXXXXXXX Valor menor do que o permitido para o produto XXXXXXXXXXXXXXXXXXXX')
                                                               
                                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                dados_atualizacao['observacao_emp'] = f'Valor menor do que o permitido para o produto - Margem {valor_margem}'
                                dados_atualizacao['observacao'] = f'Valor menor do que o permitido para o produto - Margem {valor_margem}'
                                dados_atualizacao['status_con'] = "Reprovado a Conferir"    
                                dados_atualizacao['erro'] = f'Valor menor do que o permitido para o produto - Margem {valor_margem}'
                                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                continue
                        
                        else: 
                            print('''XXXXXXXXXXXXXXXXXXX TRATAR ERRO ALERTA XXXXXXXXXXXXXXXXXXXX''')
                            pdb.set_trace()

                    valor_contrato = self.act.obter_texto(self.xpath['simulacao']['valor_contrato'], By.XPATH)
                    dados_atualizacao['valorContrato'] = "{:.2f}".format(formatar_moeda(valor_contrato))

                    # Abrir operação
                    if not self.abrir_operacao():
                        raise Exception("Falha ao abrir operação")

                    # Adicionar tomador
                    dados_endereco = {
                        "cep": informacoes['contrato']['cep'],
                        "logradouro": informacoes['contrato']['logradouro'],
                        "cidade": informacoes['contrato']['cidade'],
                        "uf": informacoes['contrato']['uf'],
                        "bairro": informacoes['contrato']['bairro'],
                        "numero": informacoes['contrato']['numeroCasa']
                    }

                    if not self.adicionar_tomador(
                        cpf=informacoes['contrato']['cpf'],
                        nome=informacoes['contrato']['nome'],
                        email=informacoes['contrato']['email'],
                        data_nascimento=informacoes['contrato']['dataNascimento'],
                        estado_civil=informacoes['contrato']['estadoCivil'],
                        telefone=informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'],
                        situacao_funcional=informacoes['contrato']['dadosProfissionais'],                        
                        dados_endereco=dados_endereco,
                        outras_informacoes=informacoes
                    ):
                        raise Exception("Falha ao adicionar tomador")
                    
                    # Adicionar dados bancários
                    if not self.adicionar_dados_bancarios(
                        tipo_operacao="Pix",
                        tipo_chave="CPF",
                        valor_chave=informacoes['contrato']['cpf']
                    ):
                        raise Exception("Falha ao adicionar dados bancários")
                    
                    # Selecionar conta de liquidação
                    if not self.selecionar_conta_liquidacao():
                        raise Exception("Falha ao selecionar conta de liquidação")
                    
                    # Adicionar garantia
                    
                    if id_perfil in [10]:
                        if not self.adicionar_garantia(
                            tipo_garantia="Crédito do Trabalhador",
                            cnpj_empregador=informacoes['contrato']['dadosProfissionais']['cnpjEmpresa'],
                            nome_empregador=informacoes['contrato']['dadosProfissionais']['nomeEmpresa'],
                            matricula=informacoes['contrato']['dadosProfissionais']['matricula'],
                            data_admissao=informacoes['contrato']['dadosProfissionais']['admissao'],
                            inicio_desconto=self.data_desconto,
                            valor_margem=informacoes['contrato']['valorParcela']
                        ):
                            raise Exception("Falha ao adicionar garantia")
                    
                    elif id_perfil in [2]:
                        print('Adicionando garantia para servidor público')
                        # if not self.adicionar_garantia_consignado_publico(
                        #     tipo_garantia = "Consignado Público",
                        #     codigo_convenio = "",
                        #     codigo_orgao = "",
                        #     matricula = contrato['matricula'],
                        #     situacao_funcional = contrato['situacao_funcional'],
                        #     inicio_desconto=self.data_desconto,
                        #     valor_margem = informacoes['contrato']['valorParcela']
                        # ):
                        #     raise Exception("Falha ao adicionar garantia")
                        pdb.set_trace()

                    # Salvar operação
                    if not self.salvar_operacao():
                        dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                        dados_atualizacao['observacao_emp'] = 'Operação não em conformidade ou Valor menor do que o permitido para o produto'
                        dados_atualizacao['observacao'] = 'Operação não em conformidade ou Valor menor do que o permitido para o produto'
                        dados_atualizacao['status_con'] = "Reprovado a Conferir"    
                        dados_atualizacao['erro'] = 'Operação não em conformidade ou Valor menor do que o permitido para o produto'
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        continue

                    # Tentar enviar para aprovação
                    if not self.enviar_para_aprovacao():
                        
                        if 'o tomador precisa ter até 74 anos' in self.alert_text:
                            print('XXXXXXXXXXXXXXXXXXX Idade maior que 74 anos XXXXXXXXXXXXXXXXXXXX')
                            dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                            dados_atualizacao['observacao_emp'] = 'Tomador maior que 74 anos'
                            dados_atualizacao['observacao'] = 'Tomador maior que 74 anos'
                            dados_atualizacao['status_con'] = "Reprovado a Conferir"    
                            dados_atualizacao['erro'] = 'Tomador maior que 74 anos'
                            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                            continue
                        
                        raise Exception("Falha ao enviar para aprovação")

                    # Obter número da operação
                    ade = self.ade
                    if ade:
                        print(f'----------------- Registrando a Ade {ade} e Atualizando o Contrato -----------------')
                        
                        dados_atualizacao['ade'] = ade                        
                        dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'
                        dados_atualizacao['textoMensagem'] = "Faça a assinatura digital do seu contrato. Ao entrar em sua proposta clique no botão |Assinatura Digital|"
                        dados_atualizacao['status_con'] = "Pendente"
                        dados_atualizacao['status_cor_con'] = "Enviado ao banco"
                        dados_atualizacao['prazo'] = informacoes['contrato']['prazo']
                        dados_atualizacao['liberarDoc'] = 1
                        dados_atualizacao['pedidoDocumentacao'] = 3
                        dados_atualizacao['linkAssinatura'] = self.obter_link_assinatura()
                        
                        if(dados_atualizacao['linkAssinatura'] == 'null'):
                            print('XXXXXX Erro link NULL Assinatura XXXXXX')
                            pdb.set_trace() 
                        
                        if not dados_atualizacao['linkAssinatura']:
                            print('>>>>> Erro ao obter link de assinatura')
                            self.act.clicar_elemento(self.xpath['assinatura']['botao_atualizar'], By.XPATH)
                            time.sleep(1)
                            self.act.clicar_elemento(self.xpath['assinatura']['botao_historico'], By.XPATH)
                            time.sleep(1)
                            try:
                                texto_historico = self.act.obter_texto('//*[@id="simple-tabpanel-9"]/div/div/div[3]/ul', By.XPATH)

                                if 'Reprovação de Compliance' in texto_historico:
                                    print('>>>>> Reprovação de Compliance detectada')
                                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                                    dados_atualizacao['status_con'] = "Reprovado a Conferir"
                                    dados_atualizacao['observacao_emp'] = 'Reprovação de Compliance'
                                    dados_atualizacao['observacao'] = 'Reprovação de Compliance'
                                    dados_atualizacao['erro'] = 'Reprovação de Compliance'
                                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                                    continue
                            
                            except:
                                print('>>>>> Erro ao obter histórico')
                                pdb.set_trace()
                                
                        
                    else:
                        print("Número da operação não encontrado. Verificar.")
                        pdb.set_trace()

                    print('>>>>> Prosseguir com a atualização do contrato.?')

                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    
                except Exception as e:
                    print(f"Erro durante a automação: {str(e)}")
               
                
            except Exception as e:
                
                print(e)
                #pdb.set_trace()
                if(self.act.quantidade_elemento('//*[@id="wrapper"]', By.XPATH) == 1):
                    self.inserir_contrato()
                # else:
                #     pdb.set_trace()
                    
                if 'localhost' in e:
                    #self.inserir_contrato()
                    # self.driver.delete_all_cookies()
                    self.driver.quit()

                else:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = e
                    dados_atualizacao['observacao'] = e
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = e
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue

    def navegar_para_simulacao_credito(self):
        """
        Navega até a página de simulação de crédito
        
        Returns:
            bool: True se a navegação for bem-sucedida, False caso contrário
        """
        try:
            print("Navegando para a área de simulação de crédito")
            
            # Clicar em Crédito
            self.act.clicar_elemento(self.xpath["menu"]["credit"], By.XPATH)
            time.sleep(1)
            
            # Clicar em Simular
            self.act.clicar_elemento(self.xpath["menu"]["simulate"], By.XPATH)
            
            # Verificar se a página de simulação foi carregada
            self.act.obter_texto(self.xpath["menu"]["simulate_page_title"], By.XPATH)
            print("Página de simulação de crédito acessada com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao navegar para simulação de crédito: {str(e)}")
            return False
    
    def selecionar_produto(self, codigo_produto):
        """
        Seleciona um produto pelo código
        
        Args:
            codigo_produto (str): Código do produto a ser selecionado
        
        Returns:
            bool: True se a seleção for bem-sucedida, False caso contrário
        """
        try:
            print(f"Selecionando produto: {codigo_produto}")
            
            # Clicar no campo de produto
            self.act.clicar_elemento(self.xpath["simulacao"]["produto_input"], By.XPATH)
            time.sleep(1)
            
            # Digitar o código do produto
            self.act.enviar_texto(self.xpath["simulacao"]["produto_input"], codigo_produto, By.XPATH)
            time.sleep(1)
            
            # Selecionar o produto no dropdown
            produto_option = self.xpath["simulacao"]["produto_option"](codigo_produto)
            self.act.clicar_elemento(produto_option, By.XPATH)
            
            self.data_desconto = self.act.obter_valor(self.xpath["simulacao"]["data_simular"], By.XPATH)

            print(f"Produto {codigo_produto} selecionado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao selecionar produto: {str(e)}")
            return False

    def definir_tipo_calculo(self, tipo_calculo = "Valor da Parcela"):
        """
        Define o tipo de cálculo
        
        Args:
            tipo_calculo (str): Tipo de cálculo a ser definido

        Returns:
            bool: True se a definição for bem-sucedida, False caso contrário
        """
        try:
            print(f"Definindo tipo de cálculo: {tipo_calculo}")
            time.sleep(3)
            # Localizar campo de tipo de cálculo
            self.act.clicar_elemento(self.xpath["simulacao"]["tipo_calculo"], By.XPATH)
            
            self.act.clicar_elemento(self.xpath["simulacao"]["tipo_calculo_opcao"], By.XPATH)

            print(f"Tipo de cálculo definido: {tipo_calculo}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir tipo de cálculo: {str(e)}")
            return False
        
    def definir_parcelas(self, parcelas):
        """
        Define o número de parcelas
        
        Args:
            parcelas (int): Número de parcelas
        
        Returns:
            bool: True se a definição for bem-sucedida, False caso contrário
        """
        try:
            print(f"Definindo número de parcelas: {parcelas}")
            
            # Localizar campo de parcelas
            self.act.press_backspace(self.xpath["simulacao"]["parcelas_input"], 10, By.XPATH)
            self.act.enviar_texto(self.xpath["simulacao"]["parcelas_input"], str(parcelas), By.XPATH, clear=True)
            self.act.press_TAB(self.xpath["simulacao"]["parcelas_input"], By.XPATH)

            print(f"Número de parcelas definido: {parcelas}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir número de parcelas: {str(e)}")
            return False
    
    def definir_valor_parcela(self, valor):
        """
        Define o valor da parcela

        Args:
            valor (float): Valor da parcela

        Returns:
            bool: True se a definição for bem-sucedida, False caso contrário
        """
        try:
            
            valor = valor.replace('.', '')            
            print(f"Definindo valor da parcela: R$ {valor}")

            # Localizar campo de valor
            self.act.press_backspace(self.xpath["simulacao"]["valor_input"], 20, By.XPATH)
            self.act.enviar_texto(self.xpath["simulacao"]["valor_input"], str(valor), By.XPATH)
            self.act.press_TAB(self.xpath["simulacao"]["valor_input"], By.XPATH)

            print(f"Valor da parcela definido: R$ {valor}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir valor da parcela: {str(e)}")
            return False
    
    def definir_data_primeiro_pagamento(self, data = "03/07/2025"):
        """
        Define a data do primeiro pagamento
        
        Args:
            data (str): Data do primeiro pagamento no formato DD/MM/AAAA
        
        Returns:
            bool: True se a definição for bem-sucedida, False caso contrário
        """
        try:
            print(f"Definindo data do primeiro pagamento: {data}")
            
            # hoje = datetime.today()
            # mes = hoje.month + 1
            # ano = hoje.year

            # # Se passar de dezembro, ajusta o ano e o mês
            # if mes > 12:
            #     mes = 1
            #     ano += 1

            # # Tenta criar a nova data — se o dia não existir (ex: 31/02), ajusta para o último dia do mês
            # try:
            #     nova_data = hoje.replace(year=ano, month=mes)
            # except ValueError:
            #     # Ajusta para o último dia do próximo mês
            #     nova_data = (hoje.replace(day=1, month=mes, year=ano) + timedelta(days=50)).replace(day=1) - timedelta(days=1)

            # self.data_desconto = nova_data.strftime('%d/%m/%Y')
            
            if(self.data_desconto != '21/10/2025'):            
                self.data_desconto = '21/10/2025'  # Forçando a data para teste
                
            print(f"Data do primeiro pagamento ajustada: {self.data_desconto}")
            
            # Localizar campo de data
            self.act.clicar_elemento(self.xpath["simulacao"]["data_simular"], By.XPATH)
            
            # self.act.press_backspace(self.xpath["simulacao"]["data_simular"], 10, By.XPATH)
            # self.act.enviar_texto(self.xpath["simulacao"]["data_simular"], self.data_desconto[:-2], By.XPATH)
            self.act.press_backspace(self.xpath["simulacao"]["data_simular"], 10, By.XPATH)
            self.act.enviar_texto(self.xpath["simulacao"]["data_simular"], self.data_desconto, By.XPATH)

            print(f"Data do primeiro pagamento definida: {data}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir data do primeiro pagamento: {str(e)}")
            return False
    
    def executar_simulacao(self):
        """
        Executa a simulação
        
        Returns:
            bool: True se a simulação for bem-sucedida, False caso contrário
        """
        try:
            print("Executando simulação")
            
            # Clicar no botão Simular
            self.act.clicar_elemento(self.xpath["simulacao"]["botao_simular"], By.XPATH)
            
            print("Simulação executada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar simulação: {str(e)}")
            return False
    
    def abrir_operacao(self):
        """
        Abre uma operação a partir da simulação
        
        Returns:
            bool: True se a abertura for bem-sucedida, False caso contrário
        """
        try:
            print("Abrindo operação")
            
            # Clicar no botão Abrir operação
            self.act.clicar_elemento(self.xpath["operacao"]["abrir_operacao"], By.XPATH)
            
            # Aguardar carregamento da página de nova operação
            #self.act.obter_texto(self.xpath["operacao"]["titulo_pagina"], By.XPATH)
            
            print("Operação aberta com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao abrir operação: {str(e)}")
            return False
    
    def adicionar_tomador(self, cpf, nome, email, data_nascimento, estado_civil, telefone, situacao_funcional, dados_endereco, outras_informacoes=None):
        """
        Adiciona um tomador à operação
        
        Args:
            cpf (str): CPF do tomador
            nome (str): Nome do tomador
            data_nascimento (str): Data de nascimento (formato DD/MM/AAAA)
            estado_civil (str): Estado civil
            telefone (str): Telefone celular
            situacao_funcional (str): Situação funcional
            dados_endereco (dict): Dados de endereço (CEP, logradouro, cidade, UF, bairro, número)
        
        Returns:
            bool: True se a adição for bem-sucedida, False caso contrário
        """
        try:
            print(f"Adicionando tomador: {nome}")
            
            # Clicar no botão Adicionar tomador
            self.act.clicar_elemento(self.xpath["tomador"]["botao_adicionar"], By.XPATH)            
            time.sleep(2)

            # Preencher Tipo de Cadastro
            self.act.clicar_elemento(self.xpath["tomador"]["tipo_cadastro"], By.XPATH)
            
            # Clicando continuar
            self.act.clicar_elemento(self.xpath["tomador"]["continuar"], By.XPATH)

            # Preencher Nome
            self.act.enviar_texto(self.xpath["tomador"]["nome"], nome)
            
            # Preencher CPF
            self.act.enviar_texto(self.xpath["tomador"]["cpf"], cpf)

            # Preencher Email
            self.act.enviar_texto(self.xpath["tomador"]["email"], email)
            
            # Preencher Data de Nascimento
            self.act.clicar_elemento(self.xpath["tomador"]["nascimento_div"], By.XPATH)
            self.act.enviar_texto(self.xpath["tomador"]["nascimento_input"], data_nascimento, By.XPATH)
            
            #Preencher Nacionalidade
            self.act.enviar_texto(self.xpath["tomador"]["nacionalidade_input"], "Brasileira")

            # Selecionar Estado Civil
            self.act.clicar_elemento("//div[contains(text(), 'Não informado')]", By.XPATH)
            self.act.clicar_elemento(f"//li[contains(text(), '{estado_civil[:4]}')]", By.XPATH)
            
            # Preencher Telefone
            self.act.enviar_texto(self.xpath["tomador"]["celular"], telefone)

            # Selecionar Situação Funcional
            self.act.enviar_texto(self.xpath["tomador"]["ocupacao"], situacao_funcional['perfil'])
            
            #Preencher Nome Mae
            try:
                self.act.enviar_texto(self.xpath["tomador"]["nome_mae"], outras_informacoes['contrato']['nomeMae'])
            except:
                pass
            
            try:
                #Preencher RG
                self.act.enviar_texto(self.xpath["tomador"]["rg"], outras_informacoes['contrato']['identidade'])
                        
                #Preencher uf Emissor
                self.act.clicar_elemento(self.xpath["tomador"]["lista_orgao_emissor"], By.XPATH)
                time.sleep(1)
                self.act.clicar_elemento(self.xpath["tomador"]["orgao_emissor"](outras_informacoes['contrato']['estadoEmissor']), By.XPATH)
            except:
                pass
            
            # Clicar no botão Continuar
            self.act.clicar_elemento(self.xpath["tomador"]["continuar"], By.XPATH)
            
            # Preencher Endereço
            # CEP
            self.act.enviar_texto(self.xpath["tomador"]["cep"], dados_endereco["cep"])

            # Aguardar preenchimento automático e completar campos restantes
            while self.act.obter_texto(self.xpath["tomador"]["estado"], By.XPATH) == '':
                print("Aguardando preenchimento automático do CEP...")
                time.sleep(1)

            # Logradouro
            rua = self.act.obter_valor(self.xpath["tomador"]["logradouro"])
            if not rua:
                self.act.enviar_texto(self.xpath["tomador"]["logradouro"], dados_endereco["logradouro"])
                
            # Número
            self.act.enviar_texto(self.xpath["tomador"]["numero"], dados_endereco["numero"])
            
            # Complemento
            self.act.enviar_texto(self.xpath["tomador"]["complemento"], dados_endereco.get("complemento", ""))
   
            # Bairro
            bairro = self.act.obter_valor(self.xpath["tomador"]["bairro"])
            if not bairro:
                self.act.enviar_texto(self.xpath["tomador"]["bairro"], dados_endereco["bairro"])
            
            # Cidade
            cidade = self.act.obter_valor(self.xpath["tomador"]["cidade"])
            if not cidade:
                self.act.enviar_texto(self.xpath["tomador"]["cidade"], dados_endereco["cidade"])
            
            # UF
            # estado = self.act.obter_valor(self.xpath["tomador"]["estado"])
            # if not estado:
            #     self.act.clicar_elemento(self.xpath["tomador"]["estado"])
            #     state_option = self.xpath["simulacao"]["produto_option"](dados_endereco['uf'])
            #     self.act.clicar_elemento(state_option, By.XPATH)

             # Clicar em salvar cadastro
            self.act.clicar_elemento(self.xpath["tomador"]["botao_salvar_cadastro"], By.XPATH)

            time.sleep(2)
            # Verificar se o formulário foi salvo com sucesso
            # Aguardar confirmação
            try:
                self.act.obter_texto(self.xpath["alertas"]["sucesso"], By.XPATH)
            except Exception as e:
                print('XXXXXXXXXXXXX ERRO AO OBTER CONFIRMAÇÃO DE SUCESSO XXXXXXXXXXXXX')
                pdb.set_trace()
                logger.error(f"Erro ao obter confirmação de sucesso: {str(e)}")
                raise Exception("Falha ao salvar cadastro do tomador")
            
            print(f"Tomador {nome} adicionado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar tomador: {str(e)}")
            return False
    
    def adicionar_garantia(self, tipo_garantia, cnpj_empregador, nome_empregador, matricula, data_admissao, inicio_desconto, valor_margem):
        """
        Adiciona uma garantia à operação
        
        Args:
            tipo_garantia (str): Tipo de garantia
            cnpj_empregador (str): CNPJ do empregador
            nome_empregador (str): Nome do empregador
            matricula (str): Matrícula do trabalhador
            data_admissao (str): Data de admissão (formato DD/MM/AAAA)
            inicio_desconto (str): Competência início desconto (formato MM/AAAA)
            valor_margem (float): Valor da margem
        
        Returns:
            bool: True se a adição for bem-sucedida, False caso contrário
        """
        try:
            print("Navegando para a aba Garantias")
            
            time.sleep(1)
            
            # Clicar na aba Garantias
            self.act.clicar_elemento(self.xpath["garantia"]["aba_garantia"], By.XPATH)
            
            # Clicar no botão Adicionar garantia
            self.act.clicar_elemento(self.xpath["garantia"]["botao_adicionar"], By.XPATH)
            
            # Aguardar carregamento do formulário
            #self.act.obter_texto(self.xpath["garantia"]["form_titulo"], By.XPATH)
            
            time.sleep(1)
            
            # Selecionar tipo de garantia
            self.act.clicar_elemento(self.xpath["garantia"]["tipo_dropdown"], By.XPATH)
            
            time.sleep(2)
            guarantia = self.xpath["garantia"]["tipo_opcao"](tipo_garantia)
            self.act.clicar_elemento(guarantia, By.XPATH)
            
            time.sleep(1)
            
            # Preencher CNPJ do Empregador
            self.act.enviar_texto(self.xpath["garantia"]["cnpj_empregador"], cnpj_empregador, By.XPATH)

            # Preencher Nome do Empregador
            self.act.enviar_texto(self.xpath["garantia"]["nome_empregador"], nome_empregador, By.XPATH)
            
            # Preencher Matrícula do Trabalhador
            self.act.enviar_texto(self.xpath["garantia"]["matricula"], matricula, By.XPATH)
            
            # Preencher Data de admissão
            self.act.clicar_elemento(self.xpath["garantia"]["data_admissao"], By.XPATH)
            self.act.press_backspace(self.xpath["garantia"]["data_admissao"], 10, By.XPATH)
            self.act.enviar_texto(self.xpath["garantia"]["data_admissao"], data_admissao, By.XPATH)

            # Preencher Competência início desconto
            self.act.enviar_texto("input[name='dataprev_DiscountStartPeriod']", inicio_desconto[3:])
            
            # Preencher Valor margem
            self.act.enviar_texto(self.xpath["garantia"]["valor_margem"], str(valor_margem).replace(".", ","), By.XPATH)
            
            # Clicar em Adicionar
            self.act.clicar_elemento(self.xpath["garantia"]["botao_adicionar_garantia"], By.XPATH)

            # Aguardar confirmação
            # self.act.obter_texto(self.xpath["alertas"]["sucesso"], By.XPATH)
            
            print("Garantia adicionada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar garantia: {str(e)}")
            return False
    
    def adicionar_dados_bancarios(self, tipo_operacao, tipo_chave, valor_chave):
        """
        Adiciona dados bancários à operação
        
        Args:
            tipo_operacao (str): Tipo de operação (ex: "Pix")
            tipo_chave (str): Tipo de chave (ex: "CPF")
            valor_chave (str): Valor da chave
        
        Returns:
            bool: True se a adição for bem-sucedida, False caso contrário
        """
        try:
            print("Adicionando dados bancários")
            
            # Clicar no botão Adicionar dados bancários
            self.act.clicar_elemento(self.xpath["bancario"]["botao_adicionar"], By.XPATH)
            
            # Aguardar carregamento do formulário
            self.act.obter_texto(self.xpath["bancario"]["form_titulo"], By.XPATH)
            
            # Selecionar tipo de operação
            self.act.clicar_elemento(self.xpath["bancario"]["tipo_operacao"], By.XPATH)
            tipo_pix = self.xpath["garantia"]["tipo_opcao"](tipo_operacao)
            self.act.clicar_elemento(tipo_pix, By.XPATH)
            
            # Selecionar tipo de chave
            self.act.clicar_elemento(self.xpath["bancario"]["tipo_chave"], By.XPATH)
            tipo_chave = self.xpath["garantia"]["tipo_opcao"](tipo_chave)
            self.act.clicar_elemento(tipo_chave, By.XPATH)

            # Preencher valor da chave
            self.act.enviar_texto('input[name="keyPix"]', valor_chave)
            
            # Clicar em Salvar
            self.act.clicar_elemento(self.xpath["bancario"]["botao_salvar"], By.XPATH)
            
            # Aguardar confirmação
            try:
                self.act.obter_texto(self.xpath["alertas"]["sucesso"], By.XPATH)
            except Exception as e:
                print('XXXXXXXXXXXXX ERRO AO OBTER CONFIRMAÇÃO DE SUCESSO XXXXXXXXXXXXX')
                pdb.set_trace()
                logger.error(f"Erro ao obter confirmação de sucesso: {str(e)}")
                raise Exception("Falha ao salvar cadastro do tomador")
            
            print("Dados bancários adicionados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar dados bancários: {str(e)}")
            return False
    
    def selecionar_conta_liquidacao(self):
        """
        Seleciona a conta de liquidação
        
        Returns:
            bool: True se a seleção for bem-sucedida, False caso contrário
        """
        try:
            print("Selecionando conta de liquidação")
            
            # Clicar no campo de conta de liquidação
            self.act.clicar_elemento(self.xpath["bancario"]["conta_liquidacao"], By.XPATH)
            
            # Selecionar a primeira opção disponível
            self.act.clicar_elemento(self.xpath["bancario"]["opcao_pix"], By.XPATH)
            
            print("Conta de liquidação selecionada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao selecionar conta de liquidação: {str(e)}")
            return False
    
    def salvar_operacao(self):
        """
        Salva a operação
        
        Returns:
            bool: True se o salvamento for bem-sucedido, False caso contrário
        """
        try:
            print("Salvando operação")
            
            # Clicar no botão Salvar
            self.act.clicar_elemento("//button[@type='submit' and .//span[text()='Salvar']]", By.XPATH)
            time.sleep(2)
            # Aguardar confirmação
            try:
                self.act.obter_texto(self.xpath["operacao"]["confirmacao_salvar"], By.XPATH)
            except Exception as e:
                print('XXXXXXXXXXXXX ERRO AO OBTER CONFIRMAÇÃO DE SALVAR XXXXXXXXXXXXX')
                time.sleep(2)
                self.act.clicar_elemento("//button[@type='submit' and .//span[text()='Salvar']]", By.XPATH)
                time.sleep(2)
                
                try:
                    texto_alerta = self.act.obter_texto('/html/body/div/div/div[4]/div/div/div/div[1]/div[2]/span[2]', By.XPATH)
                except:
                    texto_alerta = ''
                
                if 'não está em conformidade com as configurações do convênio do produto' in texto_alerta:
                    print('>>>>> Produto não está em conformidade com as configurações do convênio')
                    return False
                
                if 'é menor do que o permitido para o produto' in texto_alerta:
                    print('>>>>> Valor menor que o permitido')
                    return False
                
                else:
                    print('>>>>>> Erro ao salvar operação NOVO MOTIVO')
                    pdb.set_trace()

            # Extrair número da operação
            ade = self.act.obter_texto("//h4[contains(text(), 'Operação #')]", By.XPATH)
            self.ade = ade.split("#")[1].strip()
            
            print(f"Operação #{self.ade} salva com sucesso")

            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar operação: {str(e)}")
            return False
    
    def enviar_para_aprovacao(self):
        """
        Envia a operação para aprovação
        
        Returns:
            bool: True se o envio for bem-sucedido, False caso contrário
        """
        try:
            print("Enviando operação para aprovação")
            
            time.sleep(3)
            # Clicar no botão Enviar para aprovação
            self.act.clicar_elemento(self.xpath["operacao"]["enviar_aprovacao_botao"], By.XPATH)
            time.sleep(3)
            # Verificar se há alertas
            try:
                self.alert_text = self.act.obter_texto('/html/body/div/div/form/div[1]/div/div/div/div[1]/div[2]/span[2]', By.XPATH)
                logger.warning(f"Alerta ao enviar para aprovação: {alert_text}")
                return False, alert_text
            except:
                # Se não houver alerta, verificar confirmação de envio
                # success_message = self.act.obter_texto(self.xpath["operacao"]["aprovacao_sucesso"], By.XPATH)
                # print("Operação enviada para aprovação com sucesso")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar operação para aprovação: {str(e)}")
            return False
    
    def obter_link_assinatura(self):
        """
        Retorna o link da assinatura digital

        Returns:
            str: Link da assinatura digital ou None se não disponível
        """
        link = 'null'
        tentativa_link = 0
        
        time.sleep(5)
        self.act.clicar_elemento(self.xpath["assinatura"]["link"], By.XPATH)
        time.sleep(1)

        try:
            
            while link == 'null':
                
                self.act.clicar_elemento(self.xpath["assinatura"]["botao_atualizar"], By.XPATH)
                time.sleep(2)
                self.act.clicar_elemento("//*[@id='simple-tabpanel-5']/div/div[2]/div[2]/button", By.XPATH)
                time.sleep(2)
                self.act.clicar_elemento(self.xpath["assinatura"]["copiar_link"], By.XPATH)
                time.sleep(1)
                link = pyperclip.paste()
                
                if tentativa_link > 10:
                    print("Tentativas excedidas para obter link NULL de assinatura")
                    return False
                
                tentativa_link += 1
                
            
            return link
            
        except Exception as e:
            print(f"XXXXXXXXXXXXX Erro ao copiar link de assinatura XXXXXXXXXXXXXX")
            tentativa = 0
            
            #aguarda o botao copiar de assinatura digital aparecer
            while self.act.quantidade_elemento(self.xpath["assinatura"]["copiar_link"], By.XPATH) == 0:
                self.act.clicar_elemento("//*[@id='simple-tabpanel-5']/div/div[2]/div[2]/button", By.XPATH)
                time.sleep(1)
                print('>>>>> Aguardando link de assinatura...')
                tentativa += 1
                    
                if tentativa > 10:
                    print("Tentativas excedidas para obter link de assinatura")
                    return False
                
            while link == 'null':
                
                self.act.clicar_elemento(self.xpath["assinatura"]["botao_atualizar"], By.XPATH)
                time.sleep(2)
                self.act.clicar_elemento("//*[@id='simple-tabpanel-5']/div/div[2]/div[2]/button", By.XPATH)
                time.sleep(2)
                self.act.clicar_elemento(self.xpath["assinatura"]["copiar_link"], By.XPATH)
                time.sleep(1)
                link = pyperclip.paste()
                
                if tentativa_link > 10:
                    print("Tentativas excedidas para obter link NULL de assinatura")
                    return False
                
                tentativa_link += 1
                
            
            return link
            
            # self.act.clicar_elemento(self.xpath["assinatura"]["copiar_link"], By.XPATH)
            # time.sleep(1)
            # tentativa_link += 1
            # link = pyperclip.paste()

        return link