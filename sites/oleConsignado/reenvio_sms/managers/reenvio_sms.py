"""
sites/oleConsignado/reenvio_sms/managers/reenvio_sms.py
|
    A classe <ReenvioSMS> utiliza realiza a interface entre a classe
<DadosReenviarSNS>, responsável por realizar as requisições com
as APIs, e função <executar_reenvio>, que implementa o preenchimento
dos campos do formulário.
    O método <reenviar_sms> manipula os resultados das requisições
para passar dados do cliente para a função <executar_reenvio> que,
por sua vez, retorna dados para serem atualizdos na API uConecte.
"""
from sites.baseRobos.manager import Manager
from sites.oleConsignado.reenvio_sms.auto.executar_reenvio import executar_reenvio_sms
from sites.oleConsignado.reenvio_sms.data.dados_reenvio_sms import DadosReenviarSMS
from sites.oleConsignado.robos.auxiliares import GerenciarSessao, ErroSessaoOle
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver import Chrome

HORARIO_COMERCIAL = 9, 22


class ReenvioSMS(Manager):

    id_robo = 22

    def __init__(self, driver: Chrome=False):
        super().__init__()
        self.urls = {
            "reenvio": "https://ola.oleconsignado.com.br/ConsultaBiometriaFacial",
            "principal": "https://ola.oleconsignado.com.br/",
        }
        self.chrome_user = self.PATHS.chrome_user("reenvio_sms_ole")
        self.criar_pasta_usuario_chrome(self.chrome_user)
        self.set_options('--ignore-ssl-errors', self.chrome_user)
        self.init_chrome_driver(import_driver=driver)
        self.dados = DadosReenviarSMS()
        self.sessao = GerenciarSessao(self.chrome_driver)

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = ReenvioSMS(driver)
        try:
            run.reenviar_sms()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def reenviar_sms(self):
        self.sessao.verificar_estado()
        a_reenviar = self.dados.get_ades()[1:]

        print("Atualizando status do robô.")
        self.dados.uconecte.atualizar_status_robo(7)

        if not a_reenviar:
            return False

        for cnt, proposta in enumerate(a_reenviar, 1):
            print(f"[{cnt}]Fila Reenviar SMS")
            try:
                self.dados.api_iniciar_log_robo(
                    idContrato=proposta[3],
                    idRobo=self.id_robo
                )
                self.sessao.resolver_estado()
                status: int = 99
                dados_envio: dict = {
                    'ade': proposta[0],
                    'ddd': proposta[1],
                    'celular': proposta[2]
                }
                print(dados_envio)
                self.chrome_driver.get(self.urls["reenvio"])

                print("Reenviando SMS para contrato:", proposta[3])
                status = executar_reenvio_sms(dados_envio, self.chrome_driver)

                dados_contrato: dict = {
                    'codigoCon': proposta[3],
                    'retorno': status,
                    'tipo': proposta[4],
                    'status_con': proposta[5]
                }

                print(dados_contrato)
                self.sessao.verificar_estado()

                if 0 <= status <= 2:
                    self.dados.post_dados_consultados(dados_contrato)
                    self.dados.api_registrar_log_robo(
                        log=f"SMS reenviado com sucesso.",
                        status=2
                    )
                else:
                    raise Exception("Não foi possível realizar reenvio")

            except ErroSessaoOle:
                raise Exception("Necessário carregar novos cookies...")

            except Exception as e:
                self.dados.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )
                self.sessao.verificar_estado()
                print(e)


if __name__ == "__main__":
    import time

    while True:
        ReenvioSMS.iniciar_horario_comercial()
        time.sleep(100)
