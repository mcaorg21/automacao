##################################
####### /sites/pan/main.py #######
##################################

import sys, pdb, json, unidecode,re
sys.path.append('../../')
import PATHS
import pickle
#from sites.pan.pan_gerar_contratos.gerar_contratos import GerarContratos
from sites.pan.pan_consulta_status.consulta_status_pan import Pan
from sites.pan.pan_insercao.data.pan_inserc_data import PanInsercaoData
#from sites.pan.pan_anexo_docs.manager.anexo_docs import PanAnexoDocsMan
# Imports Classes Robôs
#from sites.pan.pan_insercao.manager.pan_inserc_man import PanInsercaoMan
from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import ConsultaRefin

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.helpers import definir_nome_robo, aguardar_n_segundos
from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import ConsultaRefin
from pathlib import Path

from sites.pan.configs.pan078 import configs

from sites.pan.auxiliares.sessao import login
from time import sleep
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_actions import SeleniumActions as SeleniumActions2
from dados.APIDataSource import APIDataSource
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By

from dados.database.queries.query_dados_robos import query_login_pass_robo


PREFS = {
    "download.default_directory": str(Path(PATHS.project_path() + "/pan/anexos/")),
    'profile.default_content_setting_values.automatic_downloads': True,
    'download.prompt_for_download': False,
    'plugins.plugins_disabled': 'Chrome PDF Viewer',
    "useAutomationExtension" : False,
    "excludeSwitches":["enable-automation"]
}
ID_BANCO: int = 68


class TarefasPan078:

    timer: int = 60
    TITLE = 'Pan Todas Tarefas 078'

    def __init__(self):
        self.chrome_user: str = PATHS.chrome_user('TarefasPan078_FGTS')
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        self.driver_path: str = PATHS.driver_path()
        self.base_path: str = PATHS.project_path()

        opts = ('--disable-blink-features=AutomationControlled','--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,800","--ignore-autocomplete-off-autofill","disable-infobars")
        exp_opt = {"prefs": PREFS}
        self.driver = Manager.driver_factory(*opts, **exp_opt)
        self.ocioso: int = 0
        self.caminho_base = PATHS.project_path()
        self.cookies_path = self.caminho_base+"\\pan\\cookies\\" + "usuario_078.pkl"
        self.cookies_path_json = self.caminho_base+"\\pan\\cookies\\" + "usuario_078.json"
        self.act = SeleniumActions(self.driver)
        self.act2 = SeleniumActions2(self.driver)
        self.id_robo = '32'
        #self.usuario = '07823888688'
        self.usuario = '03507179660'
        #pdb.set_trace()
        #self.driver.delete_all_cookies()


    # Copia da func do arquivo gerar_contratos.py, não pode fazer o import dela por elas pertencer a classe do arquivo
    def aguardar_loading(self):
        sleep(3)

        try:
            while self.act.buscar_quantidade_elemento('.updateprogress:visible') == 1:
                print('Aguardando o Loading...')
                sleep(2)
        except:
            return

    def load_cookies(self, cookies_path, delete=False):
        if delete:
            self.driver.delete_all_cookies()
        for cookie in pickle.load(open(cookies_path, "rb")):
            self.driver.add_cookie(cookie)

    def save_cookies(self, cookies_path):
        pickle.dump(self.driver.get_cookies(), open(cookies_path, "wb"))
        print(self.driver.get_cookies())

    def preencher_operacao_cef(self, tipo_conta_banco):
        #self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbCodCEFLib_CAMPO"]', By.XPATH)
        self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbCodCEFLib_CAMPO"]', By.XPATH)
        if tipo_conta_banco == 'Conta-corrente':
            self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbCodCEFLib_CAMPO"]', "001", By.XPATH)
        else:
            self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbCodCEFLib_CAMPO"]', "013", By.XPATH)

    def rodar_pan078(self):
        definir_nome_robo(self.TITLE)
        #self.driver.delete_all_cookies()
        #login(self.driver, cpf_login=configs['login'], senha=configs['senha'], parceiros="003442")
        # try:
        #     self.driver.get("https://panconsig.pansolucoes.com.br/WebAutorizador/Login/AC.UI.LOGIN.aspx")
        #     self.load_cookies(self.cookies_path)
        #     self.driver.get("https://panconsig.pansolucoes.com.br/WebAutorizador/Cadastro/CardOferta")
        # except:
        #     pass

        dados_login = query_login_pass_robo(self.id_robo, self.usuario)
        #pdb.set_trace()

        login(self.driver, cpf_login=self.usuario, senha=dados_login['senha'], parceiros="003442")
        # self.load_cookies(self.cookies_path)

        while True:
            definir_nome_robo(self.TITLE)  

            #INCIA CONSULTA DE REFINANCIAMENTO
            Pan.iniciar_horario_comercial(self.driver, configs)     
               
            #INCIA CONSULTA DE REFINANCIAMENTO
            ConsultaRefin.get_standalone_instance(driver=self.driver, **configs).consultar_refins_e_potenciais()   

            #INCIAR A INSERCAO DO FGTS AQUI 
            # try:
            #     response = json.loads(APIDataSource().get_request('pan-propostas-78').text)
            # except:
            #     self.rodar_pan078()
            # contratos = response['contratos']
            # for contrato in contratos:
            #     print(contrato)
            #     print(contrato['codigo_con'])
            #     dados = json.loads(APIDataSource().get_request('proposta-ade-pan-78', edit=["ade", contrato['codigo_con']]).text)['contrato']
            #     # Proposta FGTS saque aniversario
            #     id_session = self.driver.current_url.split("=")[-1]
            #     self.driver.get(f"https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Cadastro/Proposta/UI.PropostaFGTSAniversario.aspx?FISession={id_session}")
                
            #     # Preencher dados para a consulta
            #     try:
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpOrg_txtCPF_CAMPO"]', dados['cpf'], By.XPATH)
            #         self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpOrg_txtDtNasc_CAMPO"]',  By.XPATH) 
            #         try:
            #             self.aguardar_loading()
            #             self.act.trocar_frame_seletor('#ctl00_Cph_ucP_ppCli_frameAjuda')
            #             self.act.clicar_elemento('//*[@id="btnFechar_txt"]',  By.XPATH)
            #             self.driver.switch_to.default_content()
            #         except:
            #             pass                                    
                    
            #         self.aguardar_loading()
            #         try:
            #             self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpOrg_txtDtNasc_CAMPO"]', dados['dataNascimento'], By.XPATH)
            #             self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpOrg_txtDdd_CAMPO"]', dados['dddCelular'], By.XPATH)
            #             self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpOrg_txtTel_CAMPO"]', dados['celular'], By.XPATH)

            #             # Apertar botão consulta
            #             self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpOrg_btnConsultar_dvCBtn"]', By.XPATH)
            #             sleep(1)
            #         except:
            #             self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpOrg_btnConsultar_dvCBtn"]', By.XPATH)
            #             #continue
            #     except:
            #         #self.driver.quit()
            #         #run = TarefasPan078()
            #         #run.rodar_pan078()
            #         continue
            #     status = None
            #     try:
            #         sleep(2)
            #         alert_erro = self.act.obter_texto_alerta()
            #         status = alert_erro
            #     except:
            #         pass
            #     self.aguardar_loading()

            #     if not status or 'Existem despesas que são opcionais' in status:
            #         quantidade_tabelas = self.act.quantidade_elemento('//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond"]/tbody/tr',By.XPATH)
            #         for i in range(2,quantidade_tabelas+1): 
            #             nome_tabela = self.act.obter_texto(f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond"]/tbody/tr[{i}]/td[3]',By.XPATH)
            #             if 'FLEX' in nome_tabela:
            #                 continue
            #             status = self.act.obter_atributo(f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond"]/tbody/tr[{i}]/td[7]', 'title', By.XPATH)

            #     if status != '':
            #         payload = {
            #             "statusPropostaBanco": status,
            #             "codigoCon": dados['codigoContrato'],
            #             "key": "f689f1e12a0399fba803cb2365fc362f"
            #         }
            #         APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #         continue
            #     qtd_parcelas = self.act.quantidade_elemento('//*[@id="ctl00_Cph_ucP_JN_JpSim_gvResultadoSaque"]/tbody/tr', By.XPATH)
            #     # Pega os valores/datas das parcelas
            #     dados_parcelas = []
            #     for i in range(2, qtd_parcelas + 1):
            #         dados_parcelas.append(self.act.obter_texto(f'//*[@id="ctl00_Cph_ucP_JN_JpSim_gvResultadoSaque"]/tbody/tr[{i}]', By.XPATH).split(' ')[1:3])
    
            #     valores_atualizados = {}
            #     count = 1
            #     dict_keys = ['valor', 'data']
            #     limites = []
            #     for i in dados_parcelas:
            #         # Converte o valor para float
            #         i[-1] = float(i[-1].replace('.', '').replace(',', '.'))
            #         limites.append(i[-1])
            #         valores_atualizados[f'saque{count}'] = dict(zip(dict_keys, i[::-1]))
            #         count += 1

            #     # Valor Liberado
            #     try:
            #         valor_total_antecipacao = self.driver.execute_script("""var valor = 0; $('.grid-view tr').each(function(){if($(this).text().includes('Liberado')){valor = $(this).text().trim().split(' '); return (valor);}}); return valor;""")
            #         valor_total_antecipacao = valor_total_antecipacao[-1]
            #     except:
            #         print('XXXXXXXX Erro ao pegar valor XXXXXXXXXXX')
            #         continue

            #     payload = {
            #         "statusPropostaBanco": "Atualiza valores FGTS",
            #         "codigoCon": dados['codigoContrato'],
            #         "valores_atualizados": json.dumps(valores_atualizados),
            #         "valor_total": sum(limites),
            #         "valor_total_antecipacao": valor_total_antecipacao,
            #         "key": "f689f1e12a0399fba803cb2365fc362f"
            #     }
            #     response = APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #     print(response)
            #     # Dados do CLiente
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNome_CAMPO"]', dados['nome'], By.XPATH)
            #     # nacionalidade
            #     if dados['nacionalidade'] == 'BRASILEIRA':
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpCli_cbNac_CAMPO"]', '01', By.XPATH)
            #     else:
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpCli_cbNac_CAMPO"]', '02', By.XPATH)
            #     estado_civil = unidecode.unidecode(dados['outrosDadosPessoais']['estadoCivil'].split(" ")[0])
            #     self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpCli_cbECivil_CAMPO"]', estado_civil, By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNat_CAMPO"]', dados['cidadeNascimento'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEmail_CAMPO"]', dados['outrosDadosPessoais']['email'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtDoc_CAMPO"]', dados['identidade']['numero'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEmi_CAMPO"]', dados['identidade']['emissor'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtDtEmi_CAMPO"]', dados['identidade']['dataEmissao'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtRnd_CAMPO"]', '5000,00', By.XPATH)
            #     sleep(1)

            #     # Endereço
            #     self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]', By.XPATH)
            #     try:
            #         self.act.enviar_texto_intervalado('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]', dados['endereco']['cep'], By.XPATH, delay=0.5)
            #     except:
            #         print('Entrou no except do cep')
            #         self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]', By.XPATH)
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]', dados['endereco']['cep'], By.XPATH)

            #     self.act2.press_TAB('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]', By.XPATH)
            #     try:
            #         texto_alerta_cep = self.act.obter_texto_alerta()
            #         if(texto_alerta_cep is not None):
            #             payload = {
            #                 'statusPropostaBanco': 'Cep invalido',
            #                 'codigoCon': dados['codigoContrato'],
            #                 'key': 'f689f1e12a0399fba803cb2365fc362f'
            #                 }
            #             response = APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #             self.act.manusear_alerta(acao='aceitar')
            #             continue
            #     except:
            #         pass
            #     self.aguardar_loading()

            #     try:
            #         self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEnd_CAMPO"]', By.XPATH)
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEnd_CAMPO"]',dados['endereco']['logradouro'], By.XPATH)
            #     except:
            #         pass
            #     self.aguardar_loading()
            #     self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNr_CAMPO"]', By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNr_CAMPO"]', dados['endereco']['numero'], By.XPATH)
            #     try:
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtBai_CAMPO"]', dados['endereco']['bairro'], By.XPATH)
            #     except:
            #         pass
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCompl_CAMPO"]', dados['endereco']['complemento'], By.XPATH)

            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtMae_CAMPO"]', dados['nomeMae'], By.XPATH)
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtPai_CAMPO"]', dados['nomePai'], By.XPATH)
                
            #     if dados['banco']['numeroBanco'] == '623':
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbLib_CAMPO"]', '024', By.XPATH)
            #         self.aguardar_loading()
            #     self.driver.find_element_by_xpath('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtBncLib_CAMPO"]').clear()
            #     # BUG sleep(2)
            #     self.aguardar_loading()
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtBncLib_CAMPO"]', dados['banco']['numeroBanco'], By.XPATH)   

            #     self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtAgLib_CAMPO"]', By.XPATH)
            #     self.aguardar_loading()
            #     self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtAgLib_CAMPO"]', dados['banco']['agencia'], By.XPATH)
            #     self.aguardar_loading()

            #     # Liberacaos
            #     if dados['banco']['tipoConta'] == 'Conta-corrente':
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbTpCtLib_CAMPO"]', '01', By.XPATH)
            #     else:
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbTpCtLib_CAMPO"]', '02', By.XPATH)
            #     sleep(1)

            #     texto_alerta_bancario = ""
            #     try:
            #         texto_alerta_bancario =  self.act.obter_texto_alerta()
            #     except:                    
            #         pass
                
            #     if texto_alerta_bancario is not None and 'Banco ou Agência inválido.' in texto_alerta_bancario:
            #         payload = {
            #                 "statusPropostaBanco": texto_alerta_bancario,
            #                 "codigoCon": dados['codigoContrato'],
            #                 "key": "f689f1e12a0399fba803cb2365fc362f"
            #                 }
            #         APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #         self.act.manusear_alerta(acao='aceitar')
            #         print('Erro de dados bancários')
            #         continue

            #     if self.act.obter_propriedade('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtBncLib_CAMPO"]', 'value', By.XPATH) == '':
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtBncLib_CAMPO"]', dados['banco']['numeroBanco'], By.XPATH)
            #     self.aguardar_loading()


            #     self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtCtLib_CAMPO"]', By.XPATH)

            #     try:
            #         texto_alerta = self.act.obter_texto_alerta()
            #         if(texto_alerta is not None):
            #             payload = {
            #                 'statusPropostaBanco': texto_alerta,
            #                 'codigoCon': dados['codigoContrato'],
            #                 'key': 'f689f1e12a0399fba803cb2365fc362f'
            #                 }
            #             response = APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #             self.act.manusear_alerta(acao='aceitar')
            #             continue
            #     except:
            #         pass

            #     self.aguardar_loading()

            #     try:
            #         self.act.enviar_texto_intervalado('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtCtLib_CAMPO"]', dados['banco']['numeroConta'],  By.XPATH, delay=0.1)
            #     except UnexpectedAlertPresentException as e:
            #         # Limpeza universal no Exception object
            #         status = str(e).split('text :')[1].split('}')[0].replace(' ', '',1)
            #         payload = {
            #             'statusPropostaBanco': status,
            #             'codigoCon': dados['codigoContrato'],
            #             'key': 'f689f1e12a0399fba803cb2365fc362f'
            #             }
            #         response = APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #         print(response)
            #         continue
                
            #     except:
            #         try:
            #             self.act.enviar_texto_intervalado('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtCtLib_CAMPO"]', dados['banco']['numeroConta'],  By.XPATH)
            #         except StaleElementReferenceException:
            #             self.act.enviar_texto_intervalado('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtCtLib_CAMPO"]', dados['banco']['numeroConta'],  By.XPATH)

            #     if dados['banco']['numeroBanco'] == '104':
            #         self.preencher_operacao_cef(dados['banco']['tipoConta'])
                
            #     # Operador
            #     self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]', By.XPATH)
            #     self.aguardar_loading()
            #     self.act.enviar_texto_intervalado('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]', '03507179660', By.XPATH, delay=0.1)
            #     #self.act.press_enter('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]',By.XPATH)
                
            #     sleep(2.5)
            #     # Digitador
            #     self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpOperador_cbOrg6_CAMPO"]', '023693', By.XPATH)

            #     print('Preenchendo digito conta...')
            #     #forcar o clique no campo para eviter o erro de stale element
            #     self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', By.XPATH)
            #     try:
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', dados['banco']['digitoConta'], By.XPATH)
            #     except:
            #         self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', By.XPATH)
            #         self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', dados['banco']['digitoConta'], By.XPATH)

            #     self.act2.press_TAB('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', By.XPATH)

            #     if dados['banco']['numeroBanco'] == '623':
            #         self.act.select_drop_down('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbTpCtLib_CAMPO"]', '01', By.XPATH)


            #     rec_aguardando = 0
            #     seguir_insercao = True
            #     ade = None

            #     while self.act2.verificar_existencia_alerta() == False and ade == None:
            #         try:
            #             self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpBtn_ucBtn_btnGravar_dvTxt"]/table/tbody/tr/td',By.XPATH)
            #             try:
            #                 sleep(5)
            #                 ade = self.act.obter_texto_alerta().split(' ')[1]
            #                 print('Achou ade...')                            
            #                 break
            #             except:
            #                 ade = None
            #         except:
            #             pass
            #         print('Aguardando o alerta e loading...')
            #         self.aguardar_loading()
            #         rec_aguardando += 1
            #         if(rec_aguardando == 30):
            #             print('Verificar se inseriu')
            #             payload = {
            #                     "statusPropostaBanco": "Erro insercao FGTS",
            #                     "codigoCon": dados['codigoContrato'],
            #                     "key": "f689f1e12a0399fba803cb2365fc362f"
            #                 }
            #             APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #             seguir_insercao = False
            #             break

            #     if seguir_insercao == False:
            #         continue

            #     print('Finalizando insercao e entrando no true')

            #     if(re.search(r"\d{1,9}", str(ade))):
            #         print(f'Ade gerada -> \033[;32m{ade}\033[m\n')
            #         inserc_data = PanInsercaoData()
            #         inserc_data.atualizar_contrato_ade_sem_link(ade, dados['codigoContrato'], tabela = '900001  FGTS_CORBAN', observacao = '', valorContrato=valor_total_antecipacao)
            #         self.act.manusear_alerta(acao='aceitar')  
            #         continue

            #     count = 0              

            #     while True:
            #         try:
            #             print('Finalizando insercao')  
            #             try:
            #                 ade = self.act.obter_texto_alerta().split(' ')[1]
            #             except:
            #                 pass

            #             print('Print clicou no alerta...')                        

            #             try:
            #                 texto =  self.act.obter_texto_alerta()
            #             except:
            #                 texto = ''
            #                 pass

            #             if 'O conteúdo do campo Dv' in texto:
            #                 self.act.manusear_alerta(acao='aceitar')  
            #                 self.act2.forcar_clique_stale_element('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', By.XPATH)
            #                 self.act.enviar_texto('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]', dados['banco']['digitoConta'], By.XPATH)
            #                 rec_aguardando = 0
            #                 while self.act2.verificar_existencia_alerta() == False:
            #                     try:
            #                         self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpBtn_ucBtn_btnGravar_dvTxt"]/table/tbody/tr/td',By.XPATH)
            #                     except:
            #                         pass
            #                     print('Aguardando o alerta...')
            #                     sleep(5)
            #                     rec_aguardando += 1
            #                     if(rec_aguardando == 30):
            #                         print('Verificar se inseriu')
            #                         self.driver.quit()
            #                         break


            #             if 'Pagamento não permitido para esse banco' in texto:
            #                 payload = {
            #                     "statusPropostaBanco": texto,
            #                     "codigoCon": dados['codigoContrato'],
            #                     "key": "f689f1e12a0399fba803cb2365fc362f"
            #                 }
            #                 APIDataSource().post_request_v2('pan-78-primeiro-post', payload)
            #                 self.act.manusear_alerta(acao='aceitar')
            #                 print('Sair da funcao...')
            #                 seguir_insercao = False

            #             print('Clicando no alerta...')
            #             self.act.manusear_alerta(acao='aceitar')                        
            #             break
            #         except AttributeError:
            #             if count == 15:
            #                 # BUG Redundância para caso o clicar gravar tenha falhado
            #                 try:
            #                     if self.act.obter_texto('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtNomeOrg3o_L"]', By.XPATH) == 'Nome do Operador:':
            #                         self.act.clicar_elemento('//*[@id="ctl00_Cph_ucP_JN_JpBtn_ucBtn_btnGravar"]', By.XPATH)
            #                         self.aguardar_loading()
            #                 except:
            #                     pass
            #             pass
            #         count += 1

            #     if seguir_insercao == False:
            #         continue

            #     if(re.search(r"\d{1,9}", str(ade))):
            #         print(f'Ade gerada -> \033[;32m{ade}\033[m\n')
            #         inserc_data = PanInsercaoData()
            #         inserc_data.atualizar_contrato_ade_sem_link(ade, dados['codigoContrato'], tabela = '900001  FGTS_CORBAN', observacao = '', valorContrato=valor_total_antecipacao)
            #     else:
            #         print('Erro inserção tratar...')
            #         pdb.set_trace()


            # Não deixa deslogar
            print('Aguardando 45 segundos...')
            sleep(45)
            self.driver.refresh()

                
    def save_cookies(self, cookies_path):
        pickle.dump(self.driver.get_cookies(), open(cookies_path, "wb"))
        print(self.driver.get_cookies())


if __name__ == '__main__':
    run = TarefasPan078()
    run.rodar_pan078()