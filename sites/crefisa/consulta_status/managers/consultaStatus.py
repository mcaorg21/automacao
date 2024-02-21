from selenium.webdriver import Chrome

from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres

from sites.crefisa.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By

HORARIO_COMERCIAL = 8, 20


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False):
        super().__init__()

        self.urls = {
            "consulta": "https://app1.gerencialcredito.com.br/CREFISA/EsteiraAnaliseContrato.asp"
        }
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome):

        run = ConsultaStatus(driver)
        try:
            run.consultar_status_proposta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_status_proposta(self):     

        self.verificar_loading()       
        print('Inciando sincronização...')
        status_a_consultar = self.dados.get_ades()[1:]

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        #para testes
        #status_a_consultar = [['508020005927', '31522563881', '634296']]

        self.chrome_driver.get(self.urls["consulta"])

        if(self.driver.find_element(By.CSS_SELECTOR,"#chkNaoExibeCancelado").is_selected() == True):
            self.act.clicar_elemento('//*[@id="chkNaoExibeCancelado"]', By.XPATH)
        
        if(self.driver.find_element(By.CSS_SELECTOR,"#chkNaoExibeRecebido").is_selected() == True):
            self.act.clicar_elemento('//*[@id="chkNaoExibeRecebido"]', By.XPATH)

        if not status_a_consultar:
            print('Sem atualizações para realizar...')
            return False

        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")

            try:
                
                print("Consultando proposta:", proposta)

                ade, cpf_bd = proposta[0], proposta[1]
                cod_con = proposta[2]
                dados_consulta = {}

                dados_consulta['ade'] = ade
                dados_consulta["codigoCon"] = cod_con

                print(dados_consulta)        

                self.act.enviar_texto('//*[@id="txtNumeroAde"]', ade, By.XPATH)
                self.act.clicar_elemento('//*[@id="btnBuscaContratos"]', By.XPATH)

                self.verificar_loading()

                dados_consulta["statusPropostaBanco"] = self.act.obter_texto('//*[@id="linhaContratoId_114677"]/td[6]/ul/li[2]/div/span[1]/b', By.XPATH)
                dados_consulta['observacaoDetalhadaBanco'] = self.act.obter_texto('//*[@id="linhaContratoId_114677"]/td[6]/ul/li[5]/span[2]/span', By.XPATH)

                pdb.set_trace()

                self.dados.post_dados_consultados(dados_consulta)                         

                
            except Exception as e:
                print(e)

                self.dados.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )

                continue

        #self.dados.data_source.atualizar_sincronizacao()
        self.dados.api_registrar_log_robo(log="Sincronizado com sucesso.",status=2)


    def aguardar_consulta(self,segundos = 3):
        time.sleep(segundos)


    def verificar_loading(self, interacoes=300, aguardar = False):
        while (self.act.quantidade_elemento('/html/body/div[9]', By.XPATH) == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(0.5)
            interacoes -= 1
            if self.act.quantidade_elemento('//*[@id="linhaContratoId_114677"]/td[6]/ul/li[2]/div/span[1]/b', By.XPATH) == 1:
                return
            if(interacoes < -35):
                self.driver.quit()