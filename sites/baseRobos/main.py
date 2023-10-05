"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: main.py
| data: 22/10/2019
| autor: Gustavo Belleza

| funcionamento:
| classe responsável pela execuçao das tarefas constantes
| na classe PortalConsignado. Implementa, assim, a automaçao
| da busca por dados de consignaçao dos funcionarios estaduais
| de SP e MT.
"""
from datetime import datetime
from time import sleep

from sites.portal_consig.managers.portalConsig_man import PortalConsigMan


class Main:
    def __init__(self):
        self.portal_consig = PortalConsigMan()

        self.timer = 60
        self.ultima_atualizacao = datetime.now()

        self.log_status = False

    def main(self):

        if self.portal_consig.chrome_driver.current_url.find("consignatario") == -1:
            print("É necessário realizar o Login antes de continuar\n")

        while True:
            print(f"\n> {datetime.now()} <\n")

            self.portal_consig.login_portal()
            self.portal_consig.processar_solicitacoes_sp()

            self.verificar_tempo_execucao()

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print("Tempo entre atualizações: {}".format(time_between_updates))
        print("Timer: {} segundos".format(self.timer))

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            print("Esperando {} segundos antes de recomeçar a fila!".format(wait_time))

            if wait_time > 0:
                sleep(wait_time)

            self.timer += 1
        else:
            self.timer -= 1

        self.ultima_atualizacao = datetime.now()


if __name__ == '__main__':
    teste = Main()
    teste.main()
