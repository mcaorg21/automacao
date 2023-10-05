import os

from time import sleep
from datetime import datetime
from selenium import webdriver

from sites.core.helpers import countdown
from sites.marinha import Marinha
from sites.core.uconecte import Uconecte
from selenium.webdriver.chrome.options import Options
from PATHS import (
    driver_path, chrome_user, project_path)
from sites.baseRobos.core.helpers import definir_nome_robo


class Main:

    id_robo = 16

    def __init__(self):

        self.caminho_base = project_path()
        self.ultima_atualizacao = datetime.now()
        self.timer = 600
        self.uconecte = Uconecte()

        options = Options()
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(chrome_user("marinha"))

        self.driver = webdriver.Chrome(
            executable_path=driver_path(), options=options)

        #login e senha
        self.login = '5906929681'
        self.senha = '7russosHuge'

        self.marinha = Marinha(self.login, self.senha, self.driver)
        self.status_log = False

        self.driver.delete_all_cookies()

    @staticmethod
    def run():
        run: Main = Main()
        run.executar_consulta()

    def executar_consulta(self):

        self.driver.get('https://econsigmb.papem.mar.mil.br/mb/login/login.jsp?t=20160704085913#no-back')

        self.uconecte.atualizar_status_robo(self.id_robo)

        while True:
            definir_nome_robo("Consulta Margem Marinha")
            self.verifica_horario_comercial()
            self.__verifica_status_login()

            if not self.status_log:  # não logado
                self.marinha.login_sistema()

            self.marinha.confirmar_leitura()
            self.marinha.ir_tela_consulta()
            self.marinha.processar_filas_uconecte()

            self.verificar_tempo_execucao()

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print(f"\nTempo entre atualizações: {time_between_updates}")
        print(f"Timer: {self.timer} segundos")

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            print(f"Esperando {wait_time} segundos antes de recomeçar a fila!")

            if wait_time > 0:
                sleep(wait_time)

        self.ultima_atualizacao = datetime.now()
        self.uconecte.atualizar_status_robo(self.id_robo)

    def verifica_horario_comercial(self):
        data_hora = datetime.now()
        if data_hora.hour > 20:
            print('Fora do horário comercial... Inciando o processo para próxima manhã (7:00)...')
            self.driver.close()
            countdown(36000, 3600, 'Aguardando...')
            self.__init__()
            self.main()

    def __verifica_status_login(self):

        if self.driver.current_url.find("iniciarFsConsignataria#no-back") == -1:
            self.status_log = False
        else:
            self.status_log = True


if __name__ == "__main__":
    Main.run()
