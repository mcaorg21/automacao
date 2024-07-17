from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.data_helpers import formatar_moeda,formatar_cpf_sem_caracteres,formatar_data_banco_dados,abreviar_nomes_meio
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.data_helpers import similaridade

import os,time,pdb,re
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from sites.novosaque.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

HORARIO_COMERCIAL = 8, 20


class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()
        #https://nsaque.ultragate.com.br
        self.urls = {
            "consulta": "https://sistema.novosaque.com.br/admin/contracts",
            "insercao": "https://sistema.novosaque.com.br/admin/customer-services/create",
            "consulta_status": "https://sistema.novosaque.com.br/admin/contracts?cpf="
        }
        #https://nsaque.ultragate.com.br/admin/contracts?cpf=84986301004
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.atualiza = Uconecte()
        self.taxa_proposta = '9.00%'

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

        #self.chrome_driver.get(self.urls["consulta"])

        #print("Atualizando status do robô.")
        #self.dados.uconecte.atualizar_status_robo(7)

        if contratos['tipo'] == 'alert':
            print('Sem contratos para inserir...')
            return False

        for contrato in contratos['contratos']:
            dados_atualizacao = {}     
            dados_atualizacao['mensagem'] = 'Inserir contrato'
            self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)

            if(float(contrato['valor_con']) < 1):
                dados_atualizacao['ade'] = 0
                dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                dados_atualizacao['erro'] = 'Dados invalidos'
                dados_atualizacao['observacao'] = 'Erro de dados'            
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)    
                print('XXXXXXXXX Valor do contrato está incorreto, possivelmente erro de contratação XXXXXXXXXXX')
                continue   
            
            try:

                self.driver.get(self.urls['insercao'])            
                print('Iniciando inserção do contrato ' +  contrato['codigo_con'])

                informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])   

                if(informacoes['contrato']['endereco']['bairro'] == None):
                    dados_atualizacao['ade'] = 0
                    dados_atualizacao['mensagem'] = 'Reprovado a Conferir'
                    dados_atualizacao['erro'] = 'Dados invalidos'
                    dados_atualizacao['observacao'] = 'Erro de dados'            
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)    
                    print('XXXXXXXXX Dados incorretos, possivelmente erro de contratação XXXXXXXXXXX')
                    continue

                if(informacoes['contrato']['banco']['numeroConta'] == '' 
                    or informacoes['contrato']['banco']['numeroConta'] == '' 
                    or informacoes['contrato']['banco']['agencia'] == '0000'
                    ):
                    dados_atualizacao['mensagem'] = 'Aguardando Autorização'  
                    dados_atualizacao['textoMensagem'] = 'Atualize seus dados bancários por favor.'    
                    dados_atualizacao['pedidoDocumentacao'] = 6   
                    dados_atualizacao['interacaoHumana'] = 0      
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    print('XXXXXXXXXXXXXXXXXXXX Pedido de dados bancários realizado XXXXXXXXXXXXXXXXXXXX')
                    continue

                print('Preenchendo formulário inicial')
                
                self.act.press_backspace('//*[@id="cpf"]', metodo = By.XPATH, end = True, loop = 20, delay = 0)
                self.act.enviar_texto('//*[@id="cpf"]',contrato['cpf_cli'],By.XPATH)

                if(len(informacoes['contrato']['nome']) > 20):
                    informacoes['contrato']['nome'] = abreviar_nomes_meio(informacoes['contrato']['nome'])

                self.act.enviar_texto('//*[@id="name"]',informacoes['contrato']['nome'],By.XPATH)

                loop_apagar = len(self.act.obter_valor('//*[@id="email"]',By.XPATH))
                self.act.press_backspace('//*[@id="email"]', metodo = By.XPATH, end = True, loop = loop_apagar, delay = 0)
                self.act.enviar_texto('//*[@id="email"]',informacoes['contrato']['email'],By.XPATH)

                #reescreve nome em funcao do bug
                self.act.enviar_texto('//*[@id="name"]',informacoes['contrato']['nome'],By.XPATH)

                self.act.clicar_elemento('//*[@id="phone"]',By.XPATH)  
                self.aguardar_consulta(2) 
                self.act.enviar_texto('//*[@id="phone"]',informacoes['contrato']['dddCelular']+informacoes['contrato']['celular'],By.XPATH)

                self.act.clicar_elemento('//*[@id="phone_store"]',By.XPATH)  
                self.aguardar_consulta(1) 
                #telefone da loja
                self.aguardar_consulta(1)
                self.act.enviar_texto('//*[@id="phone_store"]',"31993448917",By.XPATH)

                loc_radio_tipo_calculo = '//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[2]/div/div/fieldset/div/div[3]/div/label/input'
                tentativa = 0
                while(self.act.quantidade_elemento(loc_radio_tipo_calculo, By.XPATH) == 0):
                    print('Aguardando radio button abrir...')
                    tentativa += 1
                    self.aguardar_consulta(2)
                    if(tentativa > 30):
                        continue

                self.aguardar_consulta(2)
                self.act.clicar_elemento(loc_radio_tipo_calculo,By.XPATH)  

                while 'Carregando' in self.act.obter_texto('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[2]/div[3]/div[2]/div[1]/div[2]',By.XPATH):
                    self.aguardar_consulta(2)
                
                self.aguardar_consulta(1)
                self.act.enviar_texto('//*[@id="value_installment"]',informacoes['contrato']['valorParcela'],By.XPATH)
                self.aguardar_consulta(2)

                taxa = ''
                for i in range(1,30):
                    self.act.press_DOWN('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[2]/div[3]/div[1]/div[2]/div/div/div',By.XPATH)
                    #self.aguardar_consulta(2)
                    j = 0
                    while 'Carregando' in self.act.obter_texto('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[2]/div[3]/div[2]/div[1]/div[2]',By.XPATH):
                        print('Aguardando calculo...')
                        j += 1 
                        self.aguardar_consulta(3)
                        if j > 20:
                            self.chrome_drive.quit()


                    taxa = self.act.obter_texto('/html/body/div/div[1]/div[2]/div/div/div/div[2]/form/div[2]/div[3]/div[1]/div[2]/div/div/div/div[1]', By.XPATH)

                    if(self.taxa_proposta == taxa):
                        print('Achou a taxa...')
                        self.aguardar_consulta(15)
                        break
                
                dados_atualizacao['valorContrato'] = formatar_moeda(self.act.obter_valor('//*[@id="value_free"]', By.XPATH).replace('R$',''))
                print('Valor atualizado para: ' + str(dados_atualizacao['valorContrato']))

                self.act.clicar_elemento('/html/body/div/div[1]/div[2]/div/div/div/div[2]/form/div[3]/button',By.XPATH)

                print('Preenchendo dados pessoais...')
                self.verificar_loading()              
                self.act.clicar_elemento('/html/body/div[2]/div/div[4]/div[2]/button', By.XPATH)
                self.verificar_loading()

                loop_apagar = len(self.act.obter_valor('//*[@id="email"]',By.XPATH))
                self.act.press_backspace('//*[@id="email"]', metodo = By.XPATH, end = True, loop = loop_apagar, delay = 0)

                self.act.enviar_texto('//*[@id="name"]',informacoes['contrato']['nome'],By.XPATH)

                if "yahoo.com" in informacoes['contrato']['email']:
                    self.act.enviar_texto('//*[@id="email"]',"empfacil@outlook.com",By.XPATH)
                else:
                    self.act.enviar_texto('//*[@id="email"]',informacoes['contrato']['email'],By.XPATH)

                self.act.enviar_texto('//*[@id="mother_name"]',informacoes['contrato']['nomeMae'],By.XPATH)
                
                if(informacoes['contrato']['nomePai'] == ''):
                    informacoes['contrato']['nomePai'] = 'Não declarado'   
                self.act.enviar_texto('//*[@id="father_name"]',informacoes['contrato']['nomePai'],By.XPATH)
                self.act.press_TAB('//*[@id="father_name"]',By.XPATH)

                data_nascimento = formatar_data_banco_dados(informacoes['contrato']['dataNascimento'])              
                self.driver.execute_script(f""" document.getElementById('birth_date').value = '{data_nascimento}'; """)
                self.act.clicar_elemento('//*[@id="birth_date"]', By.XPATH)
                self.act.press_UP('//*[@id="birth_date"]', By.XPATH);
                self.act.press_DOWN('//*[@id="birth_date"]', By.XPATH);

                self.act.enviar_texto('//*[@id="rg"]',informacoes['contrato']['identidade']['numero'],By.XPATH)
                
                print('Preenchendo dados de endereço...')

                self.act.enviar_texto('//*[@id="zip_code"]',informacoes['contrato']['endereco']['cep'],By.XPATH)
                self.act.clicar_elemento('//*[@id="street"]', By.XPATH)

                try:     
                    self.aguardar_consulta(2)               
                    erro_cep = self.act.obter_texto('/html/body/div[3]/div/div/div/div[1]',By.XPATH)
                except:
                    erro_cep = ''

                if(erro_cep == 'CEP inválido'):
                    dados_atualizacao['mensagem'] = 'Aguardando Autorização'  
                    dados_atualizacao['textoMensagem'] = 'O CEP informado está incorreto. Favor confirmar o número.'    
                    dados_atualizacao['pedidoDocumentacao'] = 3   
                    dados_atualizacao['interacaoHumana'] = 1      
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    print('XXXXXXXXXXXXXXXXXXXX Pulando inserção por erro no CEP XXXXXXXXXXXXXXXXXXXX')
                    continue


                self.act.enviar_texto('//*[@id="street"]',informacoes['contrato']['endereco']['logradouro'],By.XPATH)
                self.aguardar_consulta(2)
                self.act.enviar_texto('//*[@id="number"]',informacoes['contrato']['endereco']['numero'],By.XPATH)
                self.act.enviar_texto('//*[@id="district"]',informacoes['contrato']['endereco']['bairro'],By.XPATH)
                self.act.enviar_texto('//*[@id="complement"]',informacoes['contrato']['endereco']['complemento'],By.XPATH)

                print('Preenchendo dados bancários...')

                try:
                    self.aguardar_consulta(2)
                    self.act.select_drop_down('//*[@id="kind_pix"]','random', By.XPATH)
                except:
                    pass

                try:
                    self.act.select_drop_down('//*[@id="kind_account"]','ted', By.XPATH)
                except:
                    pass

                #self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[3]/div[1]/div/div/div/div/div[1]',By.XPATH)  
                
                if(informacoes['contrato']['banco']['numeroBanco'] == '955'):
                    informacoes['contrato']['banco']['numeroBanco'] = '033'

                try:
                    self.act.enviar_texto('//*[@id="react-select-2-input"]',informacoes['contrato']['banco']['numeroBanco'],By.XPATH)
                    self.aguardar_consulta(1)
                    self.act.press_TAB('//*[@id="react-select-2-input"]',By.XPATH)  
                except:
                    self.act.enviar_texto('//*[@id="react-select-3-input"]',informacoes['contrato']['banco']['numeroBanco'],By.XPATH)                
                    self.aguardar_consulta(1)
                    self.act.press_TAB('//*[@id="react-select-3-input"]',By.XPATH)  
                    
                self.act.clicar_elemento('//*[@id="agency_account"]',By.XPATH)  
                self.act.enviar_texto('//*[@id="agency_account"]',informacoes['contrato']['banco']['agencia'],By.XPATH)
                #self.act.enviar_texto('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[3]/div[2]/div[2]/div/input',informacoes['contrato']['banco']['digitoAgencia'],By.XPATH)
                self.act.enviar_texto('//*[@id="number_account"]',informacoes['contrato']['banco']['numeroConta'],By.XPATH)

                self.act.enviar_texto('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[5]/div[3]/div[4]/div/input',informacoes['contrato']['banco']['digitoConta'],By.XPATH)
                
                if(informacoes['contrato']['banco']['tipoConta'] == 'Conta-corrente'):
                    tipo_conta = '0'
                else:
                    tipo_conta = '1'
                self.act.select_drop_down('//*[@id="account_kind"]',tipo_conta, By.XPATH)

                
                self.verificar_loading() 
                
                #self.act.select_drop_down('//*[@id="kind_account"]','ted', By.XPATH)
                #self.act.select_drop_down('//*[@id="kind_account"]','cpf_cnpj', By.XPATH)
                #self.act.enviar_texto('//*[@id="pix"]',formatar_cpf_sem_caracteres(contrato['cpf_cli']),By.XPATH)
                self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[6]/button', By.XPATH)
                #self.verificar_loading()

                print('Finalizando ficha do contrato...')

                email_invalido = self.act.quantidade_elemento('/html/body/div[3]/div/div/div',By.XPATH)
                tentativa = 0
                texto_email_invalido = ""

                self.verificar_loading() 

                try:
                    while email_invalido == 0:
                        print('Tentando pegar email inválido')
                        email_invalido = self.act.quantidade_elemento('/html/body/div[3]/div/div/div',By.XPATH)
                        texto_email_invalido = self.act.obter_texto('/html/body/div[3]/div/div/div',By.XPATH)
                        tentativa += 1
                        if(tentativa > 30):
                            break
                except:
                    pass

                time.sleep(5)
  
                self.aguardar_consulta(2)
                self.verificar_loading()  
                
                if email_invalido == 1 and 'Email inválido' in texto_email_invalido:
                    print('Preenchendo novamente email...') 
                    self.act.enviar_texto('//*[@id="email"]',informacoes['contrato']['email']+'.br',By.XPATH)  
                    self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[4]/button', By.XPATH)  

                try:          
                    self.act.clicar_elemento('/html/body/div[2]/div/div[4]/div[2]/button', By.XPATH)
                except:
                    self.aguardar_consulta(3)
                    if(informacoes['contrato']['email'][-2:] == 'br'):
                        self.act.enviar_texto('//*[@id="email"]',informacoes['contrato']['email'][:-3],By.XPATH)
                    else:
                        self.act.enviar_texto('//*[@id="email"]','empfacil@outlook.com',By.XPATH)

                    self.aguardar_consulta(3)
                    self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[2]/form/div[4]/button', By.XPATH)
                    self.aguardar_consulta(3)
                    self.act.clicar_elemento('/html/body/div[2]/div/div[4]/div[2]/button', By.XPATH)

                self.aguardar_consulta(5)

                try:
                    self.act.select_drop_down('//*[@id="payment_method"]','credit_card', By.XPATH)
                except:
                    pass
                
                try:
                    self.act.select_drop_down('//*[@id="month"]',informacoes['contrato']['cartao']['dataFatura'].split('/')[0], By.XPATH)
                except:
                    self.act.select_drop_down('//*[@id="month"]','05', By.XPATH)
                    pass

                if 'Consignado INSS' in informacoes['contrato']['cartao']['tipoCartao']:
                    informacoes['contrato']['cartao']['tipoCartao'] = 'Cartão Consignado INSS (RMC)'

                self.aguardar_consulta(3)

                nova_data = int(informacoes['contrato']['cartao']['dataFatura'].split('/')[0]) -2
                if(nova_data < 10):
                    if(nova_data <= 0):
                        nova_data = "08"
                    else:
                        nova_data = "0" + str(nova_data)
                    
                else:
                    nova_data = str(nova_data)

                self.act.select_drop_down('//*[@id="month"]',nova_data, By.XPATH)
                self.aguardar_consulta(5)
                self.act.select_drop_down('//*[@id="kind_credit_card"]',informacoes['contrato']['cartao']['tipoCartao'], By.XPATH)
                self.aguardar_consulta(5)
                #self.act.clicar_elemento('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[5]/button', By.XPATH) 

                # try:
                #     nova_data = str(int(informacoes['contrato']['cartao']['dataFatura'].split('/')[0]) -1)
                #     self.act.select_drop_down('//*[@id="month"]',nova_data, By.XPATH)
                #     self.act.clicar_elemento('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[5]/button', By.XPATH) 
                # except:
                #     pass

                tentativa = 0
                while(self.act.quantidade_elemento('//*[@id="cpf_cnpj"]', By.XPATH) == 1):
                    print('Tentando salvar contrato... Tentativa '+ str(tentativa))
                    tentativa += 1

                    if(tentativa > 1):
                        nova_data = str(30 - tentativa) 
                        self.act.select_drop_down('//*[@id="month"]',nova_data, By.XPATH)

                    if(tentativa > 2):
                        self.act.select_drop_down('//*[@id="kind_credit_card"]','Cartão Consignado INSS (RMC)', By.XPATH)

                        if(tentativa > 3):
                            self.act.select_drop_down('//*[@id="kind_credit_card"]',informacoes['contrato']['cartao']['tipoCartao'], By.XPATH)


                    try:         
                        self.act.clicar_elemento('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[5]/button', By.XPATH) 
                    except:
                        self.act.clicar_elemento('/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/div[5]/div/button', By.XPATH) 
                        #pdb.set_trace()
                        pass
                    
                    self.aguardar_consulta(5) 
                    self.verificar_loading()
                
                #self.verificar_loading()   

                self.aguardar_consulta(3)         

                print('Pesquisando a ade gerada...')
                cpf_formatado = formatar_cpf_sem_caracteres(contrato['cpf_cli'])

                nome = self.act.obter_texto('/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[3]', By.XPATH)

                if(similaridade(nome,informacoes['contrato']['nome']) < 50):
                    print("XXXXXXXXXXXXXXXXXXXXXXXX TRATAR ERRO DA BUSCA DE ADE xxxxxxxxxxxxxxxxxxxxxxxxxx")
                    pdb.set_trace()

                # self.act.clicar_elemento('//*[@id="root"]/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/button[1]', By.XPATH)
                # self.aguardar_consulta(2)
                # self.act.enviar_texto('//*[@id="filterCpf"]',contrato['cpf_cli'], By.XPATH)
                # self.clicar_elemento('/html/body/div[4]/div/div[1]/div/div/div[3]/button[3]', By.XPATH)


                # self.driver.get(self.urls['consulta_status']+contrato['cpf_cli'])

                # self.aguardar_consulta(4)
                # self.verificar_loading()
                
                # if self.act.quantidade_elemento('//*[@id="table-responsive-custom"]/tbody/tr', By.XPATH) == 0:
                #     print('Se resultado pelo cpf formatado sem sucesso, tentando sem ser formatado...')
                #     #cpf_formatado = formatar_cpf_sem_caracteres(contrato['cpf_cli'])
                #     #self.driver.get(f'https://nsaque.ultragate.com.br/admin/contracts?cpf={cpf_formatado}')
                #     self.driver.get(self.urls['consulta_status']+cpf_formatado)
                #     self.verificar_loading()
                #     self.aguardar_consulta(5)
                
                #self.aguardar_consulta(2) 
                
                print('Atualizando contrato no web_admin')
                ade = ''
                rec = 0
                pular_insercao = False
                while ade == '':
                    try:
                        try:
                            ade = self.act.obter_texto('/html/body/div/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr/th/div/div/span',By.XPATH)
                        except:
                            print('Procurando ade pelo link')
                            self.act.clicar_elemento('//*[@id="table-responsive-custom"]/tbody/tr[1]/td[1]/div/a', By.XPATH)
                            link_ade = self.act.obter_atributo('/html/body/div[1]/div[1]/div[2]/div/div/div/div[3]/table/tbody/tr[1]/td[1]/div/div/a','href',By.XPATH)
                            ade = re.findall('\\d+',link_ade)[0]

                        print(ade)
                    except:
                        rec += 1
                        ade = ''
                        self.driver.get(self.urls['consulta_status']+cpf_formatado)
                        print('Aguardando consultar ADE...')
                        self.aguardar_consulta(2)
                        if(rec > 10):
                            print('Contrato nao inserido... Tentativa '+str(rec))
                            pular_insercao = True
                            break
                            
                if(pular_insercao):
                    print('Pulando inserção')
                    continue

                dados_atualizacao['ade'] = ade
                dados_atualizacao['mensagem'] = 'Aguardando Gerar Contrato'            
                self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                
            except Exception as e:
                print(e)

                self.dados.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )

                continue

            self.dados.api_registrar_log_robo(log="Inserção efetuada com sucesso.",status=2)


    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)

    def verificar_loading(self, interacoes=300, aguardar = False):
        while (self.act.quantidade_elemento('//*[@id="modal-root"]/div/div', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(0.5)
            interacoes -= 1
            if(interacoes < -35):
                self.driver.quit()
