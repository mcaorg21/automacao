# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# PORTAL DE PREVENÇÃO DE FRAUDES #
        (IbConsigWeb)
| projeto: automacao-python
| arquivo: main.py
| data: 2019-11-19
| autor: Gustavo Belleza
"""
import sys
sys.path.append('../../../')
from datetime import datetime
from time import sleep
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.ibConsig.ib_analise_de_fraude.analise_docs_man import PortalAnaliseDocsMan


class Main:
    def __init__(self):
        self.portal_analise_docs = PortalAnaliseDocsMan()
        self.timer = 60
        self.ultima_atualizacao = datetime.now()

        self.log_status = False

    def main(self):
        definir_nome_robo("Itau Anexa Doc Ajuste Restricao Margem")
        while True:
            print(f"\n> {datetime.now()} <")
            print(f"> {self.portal_analise_docs.chrome_driver.current_url} <")
            # if self.portal_analise_docs.verificar_nova_margem_restricao():
            #     print(f">> {str(datetime.now())} <<")
            #     print("In100 Nova Margem")

            if self.portal_analise_docs.anexar_documentos_fluxo100():
                print(f">> {str(datetime.now())} <<")
                print("In100")
                
            if self.portal_analise_docs.anexar_documentos_contrato_no_portal():
                print(f">> {str(datetime.now())} <<")
                print(f"Iniciando análises documentais.")
            
            if self.portal_analise_docs.anexar_documentos_ib_consig_portabilidade():
                print(f">> {str(datetime.now())} <<")
                print(f"Iniciando análises documentais portabilidade.")

            
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
