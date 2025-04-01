
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

from sites.facta.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from dados.APIGetSource import APIDataSource




HORARIO_COMERCIAL = 7, 22


class InserirContrato(Manager):

    def __init__(self, driver: Chrome = False):
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

        self.path_documentos = sys.path[0]+'/sites/facta/documentos/'

        if 'Windows' in platform.system():
            self.path_documentos = sys.path[0]+'/sites/facta/documentos/'


        self.xpath = {
        
            "cadastro_proposta": {
                "produto": '//*[@id="produto"]',
                "tipo_operacao" : '//*[@id="tipoOperacao"]',
                "orgao_empregador" : '//*[@id="averbador"]',
                "banco":'//*[@id="banco"]',
                "cpf":'//*[@id="cpf"]',
                "data_nascimento":'//*[@id="dataNascimento"]',
                "nome_cliente":'//*[@id="nomeCliente"]',
                "nome_social":'//*[@id="nome_social"]',
                "data_admissao":'//*[@id="ct_data_admissao"]',
                "celular":'//*[@id="ct_celular"]',
                "forma_envio":'//*[@id="ct_tipo_envio"]',
                "botao_enviar":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[3]/div/div[3]/button',
                "valor":'//*[@id="valor"]',
                "valor_solicitado":'//*[@id="opcaoValor"]',
                "prazo_solicitado":'//*[@id="prazo"]',
                "botao_ok_whatsapp":'/html/body/div[8]/div/div[6]/button[1]',
                "botao_ok_whatsapp_variacao_1":'/html/body/div[7]/div/div[6]/button[1]',
                "botao_pesquisar":'//*[@id="pesquisar"]',
                "div_resultado":'//*[@id="resultado"]',
                "escolha_plano":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[16]/div[2]/div/div/div/table/tbody/tr[1]',
                "proxima_etapa":'/html/body/div[2]/section/div[1]/div/div/div/div/div/form/button',
                "fechar_chat":'/html/body/div[7]/img[1]'

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
                "logradouro": '//*[@id="endereco"]',
                "numero": '//*[@id="numero"]',
                "complemento": '//*[@id="complemento"]',
                "bairro": '//*[@id="bairro"]',
                "option_cidade": '/html/body/div[1]/section/div[2]/div/div/div/div/div[1]/form/div/fieldset[2]/div[2]/div[5]/select/option',
                "celular": '//*[@id="celular"]',
                
                
            },
              
        }

        

        #     "dados_complementares": {
        #         "icone": "/html/body/div[1]/div/div/div[2]/header/div/div/div/div/span/div/div[1]/div[3]/div"
        #     },    

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
        self.driver.execute_script("document.body.style.zoom='80%'")     
        print('Iniciando inserção de contrato...')

        # fila = input('Informe: 1- para fila ou 2- para contrato teste \n')

        # if(fila == '1'):

        #     contratos = self.dados.get_contratos_inserir('asc')  

        #     if contratos['tipo'] == 'alert':
        #         print('Sem contratos para inserir...')
        #         return False

        # else:

        #     contrato = input('Informe número contrato: \n')

        #     while contrato == "":
        #         contrato = input('Informe número contrato: \n')

        #     #testes
        #     contratos = {}
        contratos = {}
        contratos['contratos'] = [{'codigo_con' : '830987', 'observacao_emp' : "Pre aprovado"}] 

        for contrato in contratos['contratos']:
            self.driver.get(self.urls['insercao'])
            dados_atualizacao = {}
            try:
                informacoes = self.dados.get_informacoes_contrato(contrato['codigo_con'])
                
                pprint(informacoes)
                
                print('----------------- Configurando o produto -----------------')
                self.act.select_drop_down(self.xpath['cadastro_proposta']['produto'], 'D', By.XPATH)
                time.sleep(1)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['tipo_operacao'], '13', By.XPATH)
                time.sleep(1)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['orgao_empregador'], '10010', By.XPATH)
                time.sleep(1)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['banco'], '3', By.XPATH)
                print('-----------------------------------------------------------------')
                
                print('----------------- Configurando dados do cliente -----------------')
                self.act.enviar_texto(self.xpath['cadastro_proposta']['cpf'], informacoes['contrato']['cpf'], By.XPATH)
                self.act.clicar_elemento(self.xpath['cadastro_proposta']['data_nascimento'], By.XPATH)
                
                time.sleep(1)
                self.verificar_loading_cadastro()

                try:
                    self.act.enviar_texto(self.xpath['cadastro_proposta']['data_nascimento'], informacoes['contrato']['dataNascimento'], By.XPATH)
                except:
                    pass
                
                try:
                    self.act.enviar_texto(self.xpath['cadastro_proposta']['nome_cliente'], informacoes['contrato']['nome'], By.XPATH)
                except:
                    pass
                
                self.act.enviar_texto(self.xpath['cadastro_proposta']['nome_social'], informacoes['contrato']['nome'].split(' ')[0], By.XPATH)
                
                #TODO REMOVER OU MOCKUP
                self.act.enviar_texto('//*[@id="ct_data_admissao"]', '05/04/2000', By.XPATH)
                
                print('-----------------------------------------------------------------')
                
                print('----------------- Configurando dados do contato -----------------')
                #TODO REMOVER OU MOCKUP
                informacoes['contrato']['dddCelular'] = '31'
                informacoes['contrato']['celular'] = '993448917'
                self.act.enviar_texto(self.xpath['cadastro_proposta']['celular'],'('+informacoes['contrato']['dddCelular']+') '+informacoes['contrato']['celular'][0:5]+'-'+informacoes['contrato']['celular'][5:9], By.XPATH)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['forma_envio'], 'WHATSAPP', By.XPATH)
                self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_enviar'], By.XPATH)
                time.sleep(4)
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_whatsapp'], By.XPATH)    
                except:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_ok_whatsapp_variacao_1'], By.XPATH)    
                    pass
                print('-----------------------------------------------------------------')
                
                print('----------------- Configurando valores do contrato -----------------')
                self.act.enviar_texto(self.xpath['cadastro_proposta']['valor'], informacoes['contrato']['valorParcela'], By.XPATH)
                self.act.select_drop_down(self.xpath['cadastro_proposta']['valor_solicitado'], '2', By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_proposta']['prazo_solicitado'], informacoes['contrato']['prazo'], By.XPATH)
                self.act.clicar_elemento(self.xpath['cadastro_proposta']['botao_pesquisar'], By.XPATH)
                
                time.sleep(4)
                
                print('-----------------------------------------------------------------')
                
                print('----------------- Escolhendo o plano  -----------------')
                
                self.driver.execute_script("document.body.style.zoom='60%'")
                resultado = ""
                pdb.set_trace()
                try:
                    resultado = self.act.obter_texto(self.xpath['cadastro_proposta']['div_resultado'], By.XPATH)      
                    if('não é possível cobrir o saldo devedor em nenhuma das tabelas disponíveis' in resultado):
                        
                        print('XXXXXXXXXXXXXXXXXXXXX ERRO DE ESCOLHA DE PLANO XXXXXXXXXXXXXXXXXXXXX')
                        
                        dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                        dados_atualizacao['observacao_emp'] = "Valor pedido acima do saldo devedor"
                        dados_atualizacao['observacao'] = "Valor pedido acima do saldo devedor"
                        dados_atualizacao['status_con'] = "Aguardando Comercial"
                        
                        self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                        
                        continue
                        
                except:
                    pass    
                self.act.obter_texto('//*[@id="resultado"]', By.XPATH)    

                self.act.clicar_elemento(self.xpath['cadastro_proposta']['escolha_plano'], By.XPATH)
                
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['fechar_chat'], By.XPATH)
                except:
                    pass
                
                try:
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                except:
                    time.sleep(5)
                    self.act.clicar_elemento(self.xpath['cadastro_proposta']['proxima_etapa'], By.XPATH)
                    pass
                
                print('-----------------------------------------------------------------')
                
                self.verificar_loading_cadastro()
                
                print('----------------- Etapa de certificação -----------------')
                
                self.driver.execute_script("document.body.style.zoom='80%'")
                self.act.select_drop_down(self.xpath['certificado']['indicacao_parceiro'], '92095', By.XPATH)
                self.act.enviar_texto(self.xpath['certificado']['cpfVendedor'], '06050694680', By.XPATH)
                self.act.clicar_elemento(self.xpath['certificado']['proxima_etapa'], By.XPATH)
                
                #TODO atualizar valor do contrato
                #valor_contrato = self.act.obter_texto('/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[3]/div/div', By.XPATH)
                
                print('-----------------------------------------------------------------')
                
                self.verificar_loading_cadastro()
                                
                print('----------------- Preechendo dados pessoais -----------------')
                
                self.driver.execute_script("document.body.style.zoom='50%'")
                
                print('>>>Preenchendo sexo')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['sexo'], informacoes['contrato']['sexo'][0], By.XPATH)
                
                print('>>>Preenchendo estado civil')
                switch = {'CASADO(A)': '3','SOLTEIRO(A)':'4','DIVORCIADO(A)': '2','VIÚVO(A)': '5'}        
                codigoEstadoCivil = switch.get(informacoes['contrato']['estadoCivil'].replace(" ","").upper(), '4')                
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
                
                cidades = self.act.retornar_elementos(self.xpath['cadastro_dados_pessoais']['option_naturalidade'], By.XPATH)
                while len(cidades) == 1:
                    print('Aguardando cidades...')
                    time.sleep(1)
                    cidades = self.act.retornar_elementos(self.xpath['cadastro_dados_pessoais']['option_naturalidade'], By.XPATH)   
                    
                naturalidade = unidecode.unidecode(informacoes['contrato']['naturalidade']).upper()
                
                print('>>>Preenchendo cidade de naturalidade')
                for i in cidades:
                    if naturalidade in i.text.upper():
                        i.click()
                        
                print('>>>Preenchendo nome da mãe e do pai')
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['nome_mae'], informacoes['contrato']['nomeMae'], By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['nome_pai'], (lambda nome: nome if nome != "" else "não declarado")(informacoes['contrato']['nomePai']), By.XPATH)
                
                print('>>>Preenchendo valor do patrimônio')
                #TODO REMOVER OU MOCKUP
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['valor_patrimonio'], '2', By.XPATH)
                
                print('>>>Preenchendo se é iletrado')
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['iletrado'], 'N', By.XPATH)
                
                print('>>>Preenchendo matrícula, categoria, renda e data de admissão')
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['matricula'], informacoes['contrato']['matricula'], By.XPATH)
                
                #TODO REMOVER OU MOCKUP
                self.act.select_drop_down(self.xpath['cadastro_dados_pessoais']['categoria'], '105', By.XPATH)
                
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['renda'], informacoes['contrato']['renda'], By.XPATH)
                
                #TODO REMOVER OU MOCKUP
                campo_data = self.driver.find_element(By.ID, 'ct_data_admissao')
                self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['data_admissao'], 20, By.XPATH)
                campo_data.send_keys('25/04/2000')
                
                print('>>>Preenchendo endereço')                
                campo_cep = self.driver.find_element(By.ID, 'cep')
                self.act.press_backspace(self.xpath['cadastro_dados_pessoais']['cep'], 20, By.XPATH)
                campo_cep.send_keys(informacoes['contrato']['cep'])
                self.act.clicar_elemento(self.xpath['cadastro_dados_pessoais']['pesquisar_cep'], By.XPATH)
                time.sleep(3)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['logradouro'], informacoes['contrato']['logradouro'], By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['numero'], informacoes['contrato']['numeroCasa'], By.XPATH) 
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['complemento'], informacoes['contrato']['complemento'], By.XPATH)
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['bairro'], informacoes['contrato']['bairro'], By.XPATH)
                
                cidades = self.act.retornar_elementos(self.xpath['cadastro_dados_pessoais']['option_cidade'], By.XPATH)
                while len(cidades) == 1:
                    print('Aguardando cidades...')
                    time.sleep(1)
                    cidades = self.act.retornar_elementos(self.xpath['cadastro_dados_pessoais']['option_cidade'], By.XPATH)   
                    
                cidade_endereco = unidecode.unidecode(informacoes['contrato']['cidade']).upper()
                
                print('>>>Preenchendo cidade')
                for i in cidades:
                    if cidade_endereco == i.text.upper():
                        i.click()
                
                pdb .set_trace()
                self.act.enviar_texto(self.xpath['cadastro_dados_pessoais']['celular'], '('+informacoes['contrato']['dddCelular']+') '+informacoes['contrato']['celular'][0:5]+'-'+informacoes['contrato']['celular'][5:9], By.XPATH)
                
                #TODO atualizar valor do contrato
                #valor_contrato = self.act.obter_texto('/html/body/div[2]/section/div[1]/div/div/div/div/div/form/div[1]/fieldset[3]/div/div', By.XPATH)
                print('-----------------------------------------------------------------')
                pdb.set_trace()

            except Exception as e:
                print(e)
                if 'localhost' in e:
                    self.driver.delete_all_cookies()
                    self.driver.quit()

                else:
                    dados_atualizacao['mensagem'] = 'Conferir dados do contrato'
                    dados_atualizacao['observacao_emp'] = e
                    dados_atualizacao['observacao'] = e
                    dados_atualizacao['status_con'] = "Aguardando Comercial"
                    dados_atualizacao['erro'] = e
                    self.atualiza.atualizar_contrato(contrato['codigo_con'], dados_atualizacao)
                    continue


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

        while (self.sh.buscar_quantidade_elemento('#loadGiraGira\\:visible') == 1):
            print('Aguardando Loading...')

            interacoes -= 1
            self.aguardar_consulta(1)
            if(interacoes < 1):
                return


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