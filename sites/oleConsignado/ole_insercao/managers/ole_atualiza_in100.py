import logging,pdb,time

from selenium.webdriver import Chrome
from sites.baseRobos.manager import Manager
from sites.oleConsignado.config.paths_ole import PATH_ID_4_2
from sites.baseRobos.core.helpers import identificar_erro_robo, definir_nome_robo
from sites.oleConsignado.ole_insercao.data.dados_ole_insercao import DadosInsercaoOle
from sites.core.selenium_helper import SeleniumHelper
from sites.oleConsignado.ole_insercao.auto.executar_insercao import (
    preencher_dados_In100
)
from sites.oleConsignado.robos.auxiliares import GerenciarSessao, ErroSessaoOle, verificar_loading

from PATHS import chrome_user
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from selenium.webdriver.common.by import By
from sites.core.selenium_actions import SeleniumActions

from sites.baseRobos.core.data_helpers import similaridade

HORARIO_COMERCIAL = 8, 20


class OleConsigInssCem(Manager):

    id_robo = 4
    id_banco = 123

    def __init__(self, driver: Chrome=False):
        super().__init__()
        self.user = chrome_user('ole_consig_in100')

        self.set_options(
            '--ignore-ssl-errors', "--start-maximized",
            '--enable-automation', self.user)
        self.urls = {
            'aba_inicial': 'https://ola.oleconsignado.com.br/Identificacao',
            'aba_simulacao': 'https://ola.oleconsignado.com.br/Simulacao/Index/?&',
            'aba_insercao': 'https://ola.oleconsignado.com.br/Identificacao/'}
        self.criar_pasta_usuario_chrome(self.user)
        self.init_chrome_driver(import_driver=driver)
        self.data = DadosInsercaoOle()
        self.reCaptcha_key = "6LepATAUAAAAALJCpk3eDBkBiVZuai3DeOsXBFRv"
        self.sel_help = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.sessao = GerenciarSessao(self.chrome_driver)
        self.cookies_path = PATH_ID_4_2

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = OleConsigInssCem(driver)
        try:
            run.executar_consulta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def executar_consulta(self):
        """
        Método principal na implementação da automação do processo
        de inserção. Gerencia a fila de contratos, sua inserção e
        assinatura digital.
        :return: None
        """
        print("Buscar contratos para inserção.")
        infos_contratos = self.data.get_lista_contratos()

        if not infos_contratos['contratos']:
            print("Não há contratos...")
            return False
        for cnt, info_contrato in enumerate(infos_contratos['contratos'], 1):
            print(f"[{cnt}]Fila Consulta IN100 Contratos")

            atualizacoes = {}

            self.data.api_iniciar_log_robo(
                idRobo=self.id_robo,
                idContrato=info_contrato['codigo_con']
            )

            definir_nome_robo("Ole - Consulta In100")

            contrato = self.data.get_dados_contrato(info_contrato['codigo_con'])

            self.contrato_tipo_contrato = info_contrato['tipo']
            print("\nRealizando procedimento no contrato: ", contrato['codigoContrato'])
            print("Contrato tipo: ", info_contrato['tipo'])

            if('Consultada IN100' in contrato['observacao_empresa']):
                print('Pulando contrato pois IN100 já foi consultada')
                continue

            try:
                self.sessao.verificar_estado()
               
                cpf_url = contrato['cpf'].replace(".", "").replace("-", "")
                self.chrome_driver.get(self.urls['aba_insercao'])
                self.sel_help.atribuir_valor_campo_driver('#CPF',cpf_url)
                self.sel_help.press_enter('#btnIniciarOperacao')
                verificar_loading(self.act)

                if(info_contrato['tipo'] == 'PORTABILIDADE'):
                    try:
                        quantidade_digitacoes = self.act.quantidade_elemento('//*[@id="divGridIdentificacao"]/div/table/tbody/tr', By.XPATH)
                        print('Apagando as portabilidades já digitadas e incompletas...')
                        if(quantidade_digitacoes > 0):
                            for i in range(0,quantidade_digitacoes):
                                self.act.clicar_elemento('//*[@id="divGridIdentificacao"]/div/table/tbody/tr/td[1]/a/img', By.XPATH)
                                verificar_loading(self.act)
                                self.act.clicar_elemento('//*[@id="btnCancelarOperacao"]', By.XPATH)
                                verificar_loading(self.act)
                                self.act.clicar_elemento('//*[@id="btnCancalarOperacaoSim"]', By.XPATH)
                                verificar_loading(self.act)
                                self.sel_help.atribuir_valor_campo_driver('#CPF',cpf_url)
                                self.sel_help.press_enter('#btnIniciarOperacao')
                                verificar_loading(self.act)
                    except:
                        pass

                if info_contrato['tipo'] == 'REFINANCIAMENTO' or info_contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM':
                    
                    print('Não irá consultar por ser refinanciamento...')
                    continue

                    if(info_contrato['tipo'] == 'REFINANCIAMENTO SOMANDO MARGEM'):
                        continue

                    matricula = contrato['matricula']

                    try:
                        self.act.obter_texto(f'//*[@id="id_{matricula}"]', By.XPATH)
                    except:
                        #para outros orgaos estaduais
                        matricula_portal = self.act.obter_texto('/html/body/div[2]/main/div/div[2]/div/form/div[4]/div[1]/div[3]/div[1]/div/div/table/tbody/tr/td[1]', By.XPATH)
                        compara_matricula =  similaridade(matricula_portal,matricula)
                        if(compara_matricula < 70):
                            raise Exception()

                    try:
                        self.act.clicar_elemento('//*[@id="linkSimularRefin"]/a', By.XPATH)
                    except:
                        try: 
                            self.act.clicar_elemento('//*[@id="tabs"]/li[2]/a', By.XPATH)
                            self.act.clicar_elemento('//*[@id="linkSimularRefin"]/a', By.XPATH)                            
                        except:                            
                            print('Não encontrou parcela')
                            continue
                else:
                    try:
                        self.sel_help.press_enter('#Nova')
                    except:
                        pass

                if(self.verifica_erro_tela(contrato['codigoContrato']) == True):
                    continue

                atualizacoes: dict = preencher_dados_In100(self.chrome_driver, contrato, self.contrato_tipo_contrato)

                if atualizacoes == False or ('retorno' in atualizacoes and atualizacoes['retorno'] == False):
                    if 'autorizar_token' in atualizacoes:
                        atualizacoes['mensagem'] = 'Aguardando Autorização'
                        #atualizacoes['textoMensagem'] = 'Informe no campo abaixo somente o token (código de 4 números) que foi enviado via mensagem de texto (SMS) em seu celular ('+contrato['dddCelular']+'-'+contrato['celular']+') para que possamos consultar sua margem no INSS. Caso não tenha recebido peça abaixo o reenvio.'
                        atualizacoes['textoMensagem'] = 'Adicione nosso whatsapp 3140420041 para que possamos gerar seu código para consulta de dados no INSS e assim sua operação prosseguir.'
                        atualizacoes['interacaoHumana'] = 0
                        atualizacoes['pedidoDocumentacao'] = 3
                        self.data.atualizar_contrato(contrato['codigoContrato'], atualizacoes)
                        print('Enviado para autorização para aguardar o token')
                        continue

                        
                    if('pular'in atualizacoes):
                        print('Pulando contrato...')
                        continue

                    if(atualizacoes['margem'] < 0):
                        print('Margem negativa, atualizando o contrato...')
                        atualizacoes['mensagem'] = 'Reprovado a Conferir'
                        atualizacoes['observacao'] = 'Consultada IN100. Margem negativa de '+str(atualizacoes['margem'])+'. Se possível ajuste e volta para a fila A Inserir' 
                        self.data.atualizar_contrato(contrato['codigoContrato'], atualizacoes)
                        continue

                else:
                    pdb.set_trace()
                    if(atualizacoes['margem'] != ''):
                        valor_parcela = float(contrato['valorParcela'].replace('.','').replace(',','.'))

                        atualizacoes['mensagem'] = 'Autorizada insercao'
                        atualizacoes['interacaoHumana'] = 0
                        atualizacoes['observacao'] = 'Consultada IN100. Margem de '+atualizacoes['margem']+'.' 

                        if(valor_parcela > atualizacoes['margem']):
                            atualizacoes['interacaoHumana'] = 1
                            atualizacoes['observacao'] = 'Consultada IN100. Margem de '+str(atualizacoes['margem'])+', ajustar e colocar para inserção automática.' 

                        self.data.atualizar_contrato(contrato['codigoContrato'], atualizacoes)

                    continue
            except ErroSessaoOle:
                self.data.api_registrar_log_robo(
                    log="ERRO: queda na conexão com o site.",
                    status=0
                )
                self.sessao.aguardar_load_cookies(self.cookies_path)

            except Exception as e:
                logging.exception(e)
                self.data.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )
                #identificar_erro_robo()
                continue
                self.executar_insercao()

    def verifica_erro_tela(self,codigo_contrato):
        erro = ''
        try:
            erro = self.act.obter_texto('//*[@id="divCpfContratoInadimplente"]/div/div/span',By.XPATH)
        except:
            pass

        if(erro):
            mensagem = 'Conferir dados do contrato'
            textoMensagem = ''
            pedidoDocumentacao = ''
            if('CPF possui contrato (s) inadimplente (s), regularize a situação efetuando o refinanciamento' in erro):
                mensagem = 'Aguardando Autorização'
                textoMensagem = 'Você possui contrato inadimplente neste banco. Autoriza a realização do refinanciamento diponível para quitação da dívida?'
                pedidoDocumentacao = 3

            self.data.uconecte.atualizar_contrato(codigo_contrato,  
                {
                'mensagem': mensagem, 
                'textoMensagem' : textoMensagem,
                'pedidoDocumentacao': pedidoDocumentacao
                })

            return True

        return False

if __name__ == '__main__':
    import time as t

    while True:
        OleConsigInssCem.executar_insercao()
        t.sleep(120)
