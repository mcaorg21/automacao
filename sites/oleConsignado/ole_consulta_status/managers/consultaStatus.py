from selenium.webdriver import Chrome
from sites.baseRobos.manager import Manager
from sites.oleConsignado.ole_consulta_status.auto.executarConsultaSite import ExecutarConsultaStatus
from sites.oleConsignado.ole_consulta_status.data.dados_consulta_status import DadosConsultaStatus
from sites.baseRobos.core.selenium_helper import SeleniumHelper
import os,time
from sites.oleConsignado.config.paths_ole import PATH_ID_4
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

HORARIO_COMERCIAL = 7, 20


class ConsultaStatusOle(Manager):
    usuario_pc = '--user-data-dir=C:\\Users\\gustavo\\AppData\\Local\\Google\\Chrome\\OleConsig'
    usuario_servidor = '--user-data-dir=C:/Users/lucas.s/AppData/Local/Google/Chrome/User Ole 2'
    id_robo = 7

    def __init__(self, driver: Chrome = False):
        super().__init__()
        self.urls = {
            "emprestimo": "https://ola.oleconsignado.com.br/EmprestimoPropostaDetalhe/Index/{}/CONSULTA/",
            "refin": "https://ola.oleconsignado.com.br/RefinPropostaDetalhe/Index/{}/CONSULTA/",
            "principal": "https://ola.oleconsignado.com.br/",
            "consulta": "https://ola.oleconsignado.com.br/ConsultaDeProposta/Index"
        }
        self.set_options('--ignore-ssl-errors', self.usuario_servidor)
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.exec: ExecutarConsultaStatus = ExecutarConsultaStatus(self.chrome_driver)
        self.sh = SeleniumHelper(self.chrome_driver)
        self.caminho_base = os.getcwd().replace("\\", "/")
        self.cookies_path = PATH_ID_4

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = ConsultaStatusOle(driver)
        try:
            run.consultar_status_proposta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_status_proposta(self):
        status_a_consultar = self.dados.get_ades()[1:]

        print("Atualizando status do robô.")
        self.dados.uconecte.atualizar_status_robo(7)

        if not status_a_consultar:
            return False
        self.chrome_driver.get(self.urls["consulta"])
        for cnt, proposta in enumerate(status_a_consultar, 1):
            print(f"[{cnt}]Fila Consulta Status")
            try:
                print('loading cookies %s' % self.cookies_path)
                # self.sh.load_cookies(self.cookies_path)
                self.chrome_driver.get(self.urls["consulta"])
                print("Consultando proposta:", proposta)

                ade, cpr = proposta[0], proposta[1]
                cod_con, tipo_con = proposta[2], proposta[3]

                self.dados.api_iniciar_log_robo(
                    idContrato=cod_con, idRobo=self.id_robo
                )

                self.sh.atribuir_valor_campo_jquery("#NumeroProposta", ade)
                self.sh.clicar_elemento('#btnPesquisar')
                self.verificar_loading()
                self.sh.clicar_elemento('#Detalhes')

                # if "REFINANCIAMENTO" in tipo_con or 'PORTABILIDADE' in tipo_con:
                #     self.chrome_driver.get(self.urls["refin"].format(ade))
                # else:
                #     self.chrome_driver.get(self.urls["emprestimo"].format(ade))

                dados_consulta = self.exec.extrair_dados_consulta(tipo_con)
                dados_consulta["historicoObservacoes"] = self.exec.extrair_historico_modal()
                dados_consulta['ade'] = ade
                dados_consulta["codigoCon"] = cod_con

                self.dados.post_dados_consultados(dados_consulta)
                
            except Exception as e:
                print(e)
                self.dados.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )
        self.dados.data_source.atualizar_sincronizacao()

        self.dados.api_registrar_log_robo(log="Sincronizado com sucesso.",status=2)

    def verificar_loading(self, interacoes=35, aguardar = False):
        while (self.sh.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(2)
            interacoes -= 1