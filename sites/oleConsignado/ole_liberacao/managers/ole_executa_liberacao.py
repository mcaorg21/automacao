from sites.baseRobos.manager import Manager
from sites.oleConsignado.ole_liberacao.data.dados_executa_liberacao import DadosConsultaLiberacao
from sites.oleConsignado.ole_liberacao.auto.executarLiberacaoSite import ExecutarLiberacao
from sites.oleConsignado.robos.auxiliares import GerenciarSessao, ErroSessaoOle
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver import Chrome

HORARIO_COMERCIAL = 8, 20


class ExecutaLiberacaoOle(Manager):

    id_robo = 21

    def __init__(self, driver: Chrome=False):
        super().__init__()
        self.urls = {
            "liberacao": "https://ola.oleconsignado.com.br/AtuacaoNaProposta/Index"}
        self.chrome_user = self.PATHS.chrome_user("ole_liberacao")
        self.criar_pasta_usuario_chrome(self.chrome_user)
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados = DadosConsultaLiberacao()
        self.exec = ExecutarLiberacao(self.chrome_driver)
        self.sessao = GerenciarSessao(self.chrome_driver)

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = ExecutaLiberacaoOle(driver)
        try:
            run.liberar_proposta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def liberar_proposta(self):
        self.sessao.verificar_estado()
        propostas_a_liberar = self.dados.get_ades()[1:]

        print("Atualizando status do robô.")
        self.dados.uconecte.atualizar_status_robo(7)

        if not propostas_a_liberar:
            print('Não há propostas a liberar!')
            return False

        for cnt, proposta in enumerate(propostas_a_liberar, 1):
            print(f"[{cnt}]Fila Liberar Propostas")
            try:
                self.sessao.resolver_estado()
                dados_consulta = dict()

                self.chrome_driver.get(self.urls["liberacao"])
                
                print("Consultando proposta:", proposta)

                ade, codigo_contrato = proposta[0], proposta[1]

                self.dados.api_iniciar_log_robo(
                    idRobo=self.id_robo, idContrato=codigo_contrato
                )

                liberar_proposta = self.exec.executar_liberacao_propostas(ade)
                
                dados_consulta["codigoCon"] = codigo_contrato
                dados_consulta['liberarProposta'] = liberar_proposta['retorno']

                self.dados.post_dados_consultados(dados_consulta)

                self.dados.api_registrar_log_robo(
                    log="Proposta liberada com sucesso.",
                    status=2
                )

                self.sessao.verificar_estado()

            except ErroSessaoOle:
                raise Exception("Necessário carregar novos cookies...")

            except Exception as e:
                self.sessao.verificar_estado()
                self.dados.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )
                print(e)


if __name__ == "__main__":
    import time
    while True:
        ExecutaLiberacaoOle.iniciar_horario_comercial()
        time.sleep(60)
