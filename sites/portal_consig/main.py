# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# PORTAL DO CONSIGNADO #
| projeto: automacao-python
| arquivo: main.py
| data: 22/10/2019
| autor: Gustavo Belleza
"""
from datetime import datetime
from time import sleep
from sites.portal_consig.manager.ConsultaMargemPortalConsig import PortalConsigMan

class Main:
    def __init__(self):
        self.portal_consig = PortalConsigMan()
        self.portal_consig.init_chrome_driver()

        self.timer = 60
        self.ultima_atualizacao = datetime.now()

        self.log_status = False

    def main(self):
        while True:
            print(f"\n> {datetime.now()} <")
            print(f"> {self.portal_consig.chrome_driver.current_url} <\n")

            status = self.portal_consig.executar_busca_margem()
            # if not status:
            #     self.portal_consig.atualizar_pagina(15, 5)

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print("Tempo entre atualizações: {}".format(time_between_updates))
        print("Timer: {} segundos".format(self.timer))

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            if wait_time > 70:
                wait_time = 60
            print("Esperando {} segundos antes de recomeçar a fila!".format(wait_time))

            if wait_time > 0:
                sleep(wait_time)

            self.timer += 1
        elif self.timer >= 60:
            self.timer -= 2

        self.ultima_atualizacao = datetime.now()


if __name__ == '__main__':
    teste = Main()
    teste.main()
