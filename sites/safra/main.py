import pdb, sys, json, base64, pickle, smtplib, ssl
from os import walk
from datetime import datetime
sys.path.append('../../')
#sys.path.append('../')
from sites.baseRobos.core.helpers import definir_nome_robo, enviar_email_gmail_uconecte
from sites.baseRobos.core.helpers import formatar_moeda, convert_file_base_64, deleta_todos_arquivos
from dados.APIDataSource import APIDataSource
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from sites.core.selenium_actions import SeleniumActions
from time import sleep
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from dados.database.queries.query_dados_robos import query_login_pass_robo

HORARIO_COMERCIAL = 8, 21
counter_login = 0

class Consulta_Safra_Sinc():

    TITLE = "Safra - Sincronizacao e Aprovador"

    def __init__(self):
        self.path = '/home/gustavo/Desktop/automacao-python/sites/safra/pdfs/'
        self.path_cookies = '/home/gustavo/Desktop/automacao-python/sites/safra/'
        self.nome_cookies = 'cookies.pkl'

        #self.path = 'C:\\wamp64\\www\\automacao-python\\sites\\safra\\pdfs\\'
        #self.path_cookies = 'C:\\wamp64\\www\\automacao-python\\sites\\safra\\'
        open(self.path_cookies+'cookies.pkl', 'w').close()
        self.usuario = "CBSU154420"

        dados_login = query_login_pass_robo('3', "CBSU154420")
        self.login = {'usuario': "CBSU154420", 'senha': dados_login['senha'], 'nome_usuario' : 'Michelle'}
        self.agente = '05906929681'

        self.chrome_options = ChromeOptions()
        prefs = {'download.default_directory' : self.path}
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.driver = Chrome(chrome_options=self.chrome_options)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(973, 900)


    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        definir_nome_robo(self.TITLE)     

        self.driver.get('https://epfweb.safra.com.br/PainelControle')   

        try:
            cookies = pickle.load(open(self.path_cookies + self.nome_cookies, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
                sleep(1)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass

        sleep(1)
        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        
        self.act = SeleniumActions(self.driver)

        logou = False
        try:
            self.act.enviar_texto('//*[@id="txtUsuario"]', self.login['usuario'], By.XPATH)            
        except:
            logou = True

        if not logou: 
            self.driver.delete_all_cookies()
            open(self.path_cookies + self.nome_cookies, 'w').close()
            print('Logando...')
            self.act.enviar_texto('//*[@id="txtSenha"]', self.login['senha'], By.XPATH)
            print('Terminando de fazer login...')
            sleep(2)
            self.act.hover_e_clique('//*[@id="btnEntrar"]', By.XPATH)
            sleep(45)
            try:
                self.act.hover_e_clique('//*[@id="btnEntrar"]', By.XPATH)
            except:
                pass
            print('Enviando email de login...')
            msg = "Subject: ######Login realizado -> Robo Safra Insercao#### \n\n Login realizado -" + self.login['nome_usuario'] + " - " + self.login['usuario']
            #enviar_email_gmail_uconecte("notifica4@uconecte.me", "mcaorg@gmail.com", msg)
            payload = {"telefoneDDD": '31993448917',"mensagem": msg,"key": "f9223937d6a342a75fa449a2e5bbd75b"}
            response = APIDataSource().post_request_v2('enviar-mensagem-whatsapp', payload)
            sleep(30)
        
        self.verificar_loading()
        
        if not logou:
            with open(self.path_cookies+"cookies.pkl", "wb") as file:
                pickle.dump(self.driver.get_cookies(), file)
                sleep(1)
            sleep(5)

        self.driver.get('https://epfweb.safra.com.br/PainelControle')

        global counter_login
        try:
            self.act.obter_texto('//*[@id="tblLogin"]/tbody/tr/td/div/label[1]', By.XPATH)
            counter_login += 1
            print('Tentativa de LOGIN: ' + str(counter_login))
            if counter_login == 3:
                port = 465
                context = ssl.create_default_context()
                msg = "Subject: ######Problema -> Robo Safra Sinc. Aprovador#### \n\nTerceira tentativa de no login (" + self.login['usuario'] + ") feita no sincronizador e aprovador. Para corrigir o problema delete os cookies."
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login("notifica4@uconecte.me", "marcelo2126")
                    server.sendmail("notifica4@uconecte.me", "mcaorg@gmail.com", msg.encode('utf-8'))
                print('XXXXXXXXXXXXXXXXXXXX ERRO NO LOGIN XXXXXXXXXXXXXXXXXXXX')
                open(self.path_cookies+self.nome_cookies, 'w').close()
                sleep(1800)
                counter_login = 0
        except:
            counter_login = 0
            pass

        try:
            self.aprovador()
            self.sincronizador()            
            print('Esperando 60 segundos...........')

        except:
            print("Unexpected error:", sys.exc_info()[0])
            definir_nome_robo('####ERRO####' + self.TITLE)

   
    def menu_opcoes(self, xpath_clique, texto):
        try:
            self.act.clicar_elemento(xpath_clique, By.XPATH)
            xpath_input = xpath_clique[::-1]
            xpath_input = xpath_input.replace('a', '', 1)
            xpath_input = xpath_input[::-1]
            xpath_input += 'div/div/input'
            self.act.enviar_texto(xpath_input, texto, By.XPATH)
            self.act.press_enter(xpath_input, By.XPATH)
        except:
            pass

    def aprovador(self):
        print('#####INICIANDO FILA APROVADOR######')
        self.driver.set_window_size(973, 900)
        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        response = APIDataSource().get_request('dados-aprovar-safra').text
        dados = json.loads(response)
        self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
        for i in dados[1:]:
            # Pesquisar
            # Campo Proposta
            self.act.enviar_texto('//*[@id="PainelControle_numeroContrato"]', i[0], By.XPATH)
            # Clicar em pesquisar
            self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
            try:
                self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
            except:
                pass
            sleep(2)
            try:
                self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[19]/a/img', By.XPATH)
                self.act.clicar_elemento('//*[@id="toast-container"]/div/div/a[1]', By.XPATH)
                sleep(3)
            except:
                pass
            payload = {
                "codigoCon": i[1],
                "liberarProposta": 2
            }

            response = APIDataSource().post_request_v2('enviar-dados-liberar-safra', payload)
            print(response)
            # Preparar para buscar outro
            self.act.clicar_elemento('//*[@id="ui-accordion-DivPrincipal-header-0"]', By.XPATH)
        self.driver.get('https://epfweb.safra.com.br/PainelControle')
        print("######FINALIZADA FILA APROVADOR######")
    
    def simulador(self):
        for i in propostas:
            # Nova Proposta
            self.act.clicar_elemento('//*[@id="PainelControle_novaProposta"]', By.XPATH)
            sleep(1)
            self.act.enviar_texto_intervalado('//*[@id="txtAgenteCertificado"]', self.agente, By.XPATH)
            self.act.clicar_elemento('//*[@id="ui-id-1"]', By.XPATH)

            try:
                self.act.clicar_elemento('//*[@id="btnProsseguir"]/span', By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="btnProsseguir"]/span', By.XPATH)

            # Convenio
            self.menu_opcoes('//*[@id="ddlConvenio_chzn"]/a', 'FGTS')
            # Produto
            self.menu_opcoes('//*[@id="ddlProduto_chzn"]/a', 'NOVO')
            # Cpf
            self.act.enviar_texto('//*[@id="txtCPF"]', self.agente, By.XPATH)
            # Nome
            self.act.enviar_texto('//*[@id="txtNome"]', proposta['referenciaPessoal']['nome'], By.XPATH)
            # Tipo de formalização
            self.menu_opcoes('//*[@id="ddlTipoFormalizacao_chzn"]/a', 'DIGITAL WHATSAPP')
            # Celular MSG
            self.act.enviar_texto('//*[@id="txtDddWhatsAppDP"]', proposta['referenciaPessoal']['telefone'][1:3], By.XPATH)
            self.act.enviar_texto('//*[@id="txtTelWhatsAppDP"]', proposta['referenciaPessoal']['telefone'][5:].replace('-',''), By.XPATH)
            # UF
            self.menu_opcoes('//*[@id="ddlUFsCliente_chzn"]/a', 'MG')
            # MAtricula
            self.act.enviar_texto('//*[@id="txtMatricula"]', By.XPATH)
            # Prosseguir
            self.act.clicar_elemento('//*[@id="btnProsseguirSimulador"]', By.XPATH)

    def aguardar_carregar_proposta(self, ade, rec = 0):
        print('Consultando...' + str(rec))
        consulta = True
        try:            
            proposta = self.act.quantidade_elemento(f'//*[@id="{ade}"]/td[1]/a/img',By.XPATH) 
            if(proposta == 1):
                return consulta
        except:
            rec += 1
            if(rec > 30):
                consulta = False

            print('Tentando pesquisar novamente...')
            sleep(1)
            try:
                self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
                self.verificar_loading()
            except:
                print('Abrindo filtro para pesquisar nvoamente')
                return False
                # self.act.clicar_elemento('//*[@id="ui-accordion-DivPrincipal-header-0"]', By.XPATH)
                # sleep(2)
                # self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
                # self.verificar_loading()

            self.aguardar_carregar_proposta(ade, rec)

        return consulta


    def sincronizador(self):
        response = APIDataSource().get_request('dados-proposta-sincronizacao-safra').text
        dados = json.loads(response)
        self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
        
        for i in dados[1:]:
            print('Pesquisando...')
            self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
            # ade 
            try:
                self.act.enviar_texto('//*[@id="PainelControle_numeroContrato"]', i[0], By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="FiltroProposta"]/img', By.XPATH)
                self.act.enviar_texto('//*[@id="PainelControle_numeroContrato"]', i[0], By.XPATH)

            try:
                self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
            except:
                self.sincronizador()

            sleep(1)
            print('Verificando loading...')
            
            self.verificar_loading()
            # Primeira Letra
            status = None

            #aguarda carregamento de proposta
            if self.aguardar_carregar_proposta(i[0]) == False:
                print('Pulando proposta, site com lentidão...')
                continue

            print('Passou pela consulta de pesquisa...')

            try:
                if str(i[0]) not in self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]', By.XPATH):
                    print('A primeira linha não é da proposta')
                    self.sincronizador()
            except:
                print('A primeira linha não é da proposta --- EXCEPT ')
                self.sincronizador()

            try:
                status = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[5]/span', By.XPATH)
            except:
                self.act.clicar_elemento('//*[@id="PainelControle_pesquisar"]', By.XPATH)
                try:
                    status = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[5]/span', By.XPATH)
                except:
                    continue

            if status == 'Em Digitação':
                print('Proposta em digitação pulando...')
                payload = {"statusPropostaBanco": "Em digitacao", "observacaoDetalhadaBanco": "Verificar o que está acontecendo com esta proposta", "codigoCon": i[2]}
                response = APIDataSource().post_request_v2('enviar-dados-safra', payload)
                continue

            if status == 'Recusada':
                self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[5]/span', By.XPATH)
                self.verificar_loading()
                length = self.act.quantidade_elemento('//*[@id="ui-id-1"]/div/ul/li/ul/li/ul/li', By.XPATH)
                textos_recusada = []
                for j in range(1, length + 1):
                    textos_recusada.append(self.act.obter_texto(f'//*[@id="ui-id-1"]/div/ul/li/ul/li/ul/li[{j}]', By.XPATH).replace('- ', ''))
                try:
                    self.act.clicar_elemento('/html/body/div[10]/div[1]/button', By.XPATH)
                except:
                    self.act.clicar_elemento('/html/body/div[9]/div[1]/button', By.XPATH)
                    pass

            try:
                letra1 = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[3]/a/span', By.XPATH)
            except:
                letra1 = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[2]/span', By.XPATH)

            titulo_letra1 = ''
            texto_letra1 = ''
            
            if status != 'Pago' and letra1 != 'P':
                self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[3]/a/span', By.XPATH)
                self.verificar_loading()
                # Titulo 
                try:
                    titulo_letra1 = self.act.obter_texto('/html/body/div[9]/div[1]/span', By.XPATH)
                    tr_pendencia = 3
                    div = '9'
                except:
                    titulo_letra1 = self.act.obter_texto('/html/body/div[10]/div[1]/span', By.XPATH)
                    tr_pendencia = 3
                    div = '10'
                    pass

                    try:
                        texto_letra1 = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/fieldset/p', By.XPATH)
                    except:
                        try:
                            texto_letra1 = self.act.obter_texto('//*[@id="ui-id-3"]/fieldset/div', By.XPATH)
                        except:
                            texto_letra1 = self.act.obter_texto('//*[@id="ui-id-1"]/fieldset/div', By.XPATH)
                            tr_pendencia = 1


                        if('Pendências' in texto_letra1): 
                            texto_letra1 += '\n' + self.act.obter_texto(f'//*[@id="ui-id-{tr_pendencia}"]/fieldset/table/tbody/tr[1]/td[1]', By.XPATH)


                # botão X
                self.act.clicar_elemento(f'/html/body/div[{div}]/div[1]/button', By.XPATH)

            elif status == 'Pago' and letra1 == 'P':
                print('Contrato nao pago pegar a letra 1')
                titulo_letra1 = 'Contrato com retorno de credito'
                texto_letra1 = ''

            # Segunda Letra
            try:
                letra2 = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[4]/a/span', By.XPATH)
            except:
                letra2 = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[4]/span', By.XPATH)

            #clica nos detalhes da formalizacao
            self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[4]/a/span', By.XPATH)
            self.verificar_loading()

            try:
                titulo_letra2 = self.act.obter_texto(f'/html/body/div[10]/div[1]/span', By.XPATH)
                div = '10'
            except: 
                titulo_letra2 = self.act.obter_texto(f'/html/body/div[9]/div[1]/span', By.XPATH)
                div = '9'

            url_bruta = None
            self.verificar_loading()
            
            try:
                quantidade_td = self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/fieldset/table/tbody/tr', By.XPATH)

                d_textos = {}
                for j in range(1, quantidade_td + 1): 
                    d_textos[self.act.obter_texto(f'html/body/div[{div}]/div[2]/fieldset/table/tbody/tr[{j}]/td[1]', By.XPATH) + str(j)] = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/fieldset/table/tbody/tr[{j}]/td[2]', By.XPATH)
                
                for k in d_textos:
                    if "Clique" in k:
                        url_bruta = k.split()
                        url_bruta = url_bruta[-1][0:-1]
                        break
            except:
                d_textos = ''
                pass
            
            self.act.clicar_elemento(f'/html/body/div[{div}]/div[1]/button', By.XPATH)
            # STATUS
            self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[5]/span', By.XPATH)
            status += ' ' + self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div/ul/li/ul/li', By.XPATH)
            status = status.split()
            try:
                status = ' '.join(status[:status.index('-')])
            except:
                status = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/div/ul/li/ul/li', By.XPATH)

            if 'Contrato Integrado' in status:
                try:
                    status += ' ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[2]/td[4]',By.XPATH)
                except:
                    pass

            self.act.clicar_elemento(f'/html/body/div[{div}]/div[1]/button', By.XPATH)
            # E
            self.driver.set_window_size(973, 900)
            e = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[21]/p', By.XPATH).strip()
            self.act.clicar_elemento('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[21]/p', By.XPATH)
            self.verificar_loading()

            titulo_e = ''
            e_texto = ''
            texto_historico_averbacoes = ''
            
            try:
                titulo_e = self.act.obter_texto(f'/html/body/div[{div}]/div[1]/span', By.XPATH)
                e_texto = self.act.obter_texto(f'/html/body/div[{div}]/div[2]/span', By.XPATH)
                self.act.clicar_elemento(f'/html/body/div[{div}]/div[1]/button', By.XPATH)
                texto_historico_averbacoes = "\n" + titulo_e + "\n\n" + e_texto + "\n\n"
            except:
                titulo_e = 'Historico Tentativa Averbacao'  
                quantidade_tr = self.act.quantidade_elemento(f'/html/body/div[{div}]/div[2]/table/tbody/tr', By.XPATH)
                if(quantidade_tr == 1):
                    try:
                        e_texto = self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[6]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[7]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[2]', By.XPATH)
                    except:
                        e_texto = self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[5]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[6]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr/td[2]', By.XPATH)

                else:
                    try:
                        e_texto = self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[5]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[6]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[2]', By.XPATH)
                    except:
                        e_texto = self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[5]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[7]', By.XPATH) + ' - ' + self.act.obter_texto('//*[@id="detalhes-pagamento"]/tbody/tr[1]/td[2]', By.XPATH)

                self.act.clicar_elemento(f'/html/body/div[{div}]/div[1]/button', By.XPATH)
                texto_historico_averbacoes = "\n" + titulo_e + "\n\n" + e_texto + "\n\n"
                pass

            # Principal
            principal = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[13]', By.XPATH)
            
            #pega primeiro quadrando que pode ou nao estar vazio
            if(self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[2]', By.XPATH) != ''):
                status_quadrante = self.act.obter_texto('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[2]', By.XPATH)+'-'
            else:
                status_quadrante = ''

            #verifica se o pagamento ja foi liberado
            texto_liberar_pagamento = ''
            try:            
                if(self.act.obter_atributo('/html/body/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[3]/div/table/tbody/tr[2]/td[19]/a/img','title',By.XPATH) == 'Alçada Master'):
                    texto_liberar_pagamento = '***PAGAMENTO AINDA NAO LIBERADO PELO MASTER****' + "\n\n"
            except:
                texto_liberar_pagamento = ''

            if status == 'Pago':
                texto_observacao_banco = titulo_letra2 + "\n\n"    
            else:
                texto_observacao_banco = texto_liberar_pagamento + titulo_letra1 + "\n\n" + texto_letra1 + "\n\n\n" + titulo_letra2 + "\n\n"

            if(d_textos):
                for k, v in d_textos.items():
                    texto_observacao_banco += k + ' ' + v + "\n"

                texto_observacao_banco += "\n\n"
            else:
                texto_observacao_banco = ''

            try:
                for j in textos_recusada:
                    texto_observacao_banco += j + '\n'
                texto_observacao_banco += '\n\n'
            except:
                pass

            payload = {
                "statusPropostaBanco": f"{status_quadrante}{letra1}-{letra2}-{status}-{e}",
                "observacaoDetalhadaBanco": texto_historico_averbacoes + texto_observacao_banco,
                "valorCon": formatar_moeda(principal),
                "linkAssinaturaDigital": url_bruta,
                "codigoCon": i[2],
                "ade": i[0]
            }

            print(payload)

            response = APIDataSource().post_request_v2('enviar-dados-safra', payload)
            print(response)
            self.driver.refresh()
            continue

        print('#######################FINALIZOU A FILA DE SINCRONIZACAO#######################')

    def verificar_loading(self, interacoes=100, aguardar = False):
        sleep(0.3)
        while (self.act.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
            print('Aguardando Loading...' + str(interacoes))
            sleep(0.5)
            interacoes -= 1
    

if __name__ == '__main__':
    robo = Consulta_Safra_Sinc()
    while True:
        robo.main()
        sleep(60)


'''
payload = {"codigoCliente":proposta['codigoCliente'], "codigoContrato":proposta['codigoContrato'],"ade":ade, "base64":pdf_base64, "linkAssinaturaDigital":None,"banco":"safra-fgts","valorCon":formatar_moeda(principal), "key":"f689f1e12a0399fba803cb2365fc362f"}
'''