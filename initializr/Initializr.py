"""
#   A classe Initializr tem como funções centralizar, executar e gerenciar
# os processos dos robôs que compõem o sistema de automação. As funções que
# concretizam os propósitos da classe são executadas no método Initializr.main.
#   Initializr.main consiste em um loop indefinido que realiza iterativamente as
# seguintes tarefas: 1. carregar as informações do arquivo ativacao.json, que informa
# quais robôs estarão ativos a cada iteração, 2. reportar o estado de cada processo,
# se estão ativos ou não, 3. iniciar todos os processos marcados como ativos e que
# ainda não estiverem ativos.
#   As variáveis de instância da classe consistem em instâncias de classes que
# contem as configurações para execução de cada processo.
#   Além disso, Initializr contém duas variáveis de classe, a saber:
# 1. activate: a esta variável será atribuído um dict carregado do arquivo json
# ativacao.json.
# 2. segundos_atualizacao: o tempo de espera entre cada iteração realizada por
# Initializr.main.
"""
from typing import List

import os,sys,pdb
sys.path.append('../')
#sys.path.insert(1, '/home/gustavo/Desktop/automacao-python/')



from initializr.processos_automacao.classes_processos.InstanciasProcessos import INSTANCIAS
# Imports configuracoes
from initializr.processos_automacao import (
    CURR_SHELL, BASE_CMD, SO
)
# Imports stdlib e auxiliares
from datetime import datetime as dt
import logging as log
from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper


from sites.baseRobos.core.helpers import aguardar_n_segundos
from time import sleep
from sites.baseRobos.core.helpers import definir_nome_robo
log.basicConfig(level=log.INFO)

# Cabeçalho que apresenta as configurações do ecossistema no qual os processos
# serão iniciados.
definir_nome_robo("Initializr - Automação")
print("\n####### Iniciando Processos com as Configurações #######")
sleep(0.4)
print(f"# Sistema Operacional: {SO}")
sleep(0.4)
print(f"# Shell: {CURR_SHELL}")
sleep(0.4)
print(f"# Comando base de execução: {BASE_CMD}")
sleep(0.4)
print("########################################################\n")
sleep(0.4)


class Initializr:

    activate: dict = {}
    segundos_atualizacao = 10
    init = True

    def __init__(self):
        super().__init__()
        self.processos: List[ProcessWrapper] = list(INSTANCIAS.values())

    def main(self):
        while True:
            # Carrega o arquivo ativacao.json
            self.load_activation_status()

            # Apresenta o estado de todos os processos.
            self.report_status()

            # Itera por uma lista contendo instâncias de todos os processos.
            # Em cada iteração o processo é inicializado, caso não esteja
            # em execução E esteja marcado como ativo em ativacao.json
            for proc in self.processos:
                proc.reinit_if_dead(proc, self.activate, init=self.init)

            aguardar_n_segundos(self.segundos_atualizacao)
            self.init = False

    def report_status(self):
        print("\n+---------- Status dos processos ----------+")
        print(f"\t\t[{dt.now().hour}:{dt.now().minute}:{dt.now().second}]")

        for proc in self.processos:
            print("+------------------------------------------+")
            print(proc)

        print("+==========================================+\n")

    def load_activation_status(self):
        # Carrega o arquivo ativacao.json e armazena seus dados na
        # forma de um dict na variável de classe <activate>
        import json
        from pathlib import Path
        # if(dt.today().weekday() !=  6):
        #     path = str(Path(os.path.dirname(__file__), "ativacao.json"))
        # else:
        path = str(Path(os.path.dirname(__file__), "ativacao.json"))
        try:
            with open(path) as fObj:
                self.activate = json.loads(fObj.read())
        except Exception as e:
            print(e)


if __name__ == "__main__":
    Initializr().main()
