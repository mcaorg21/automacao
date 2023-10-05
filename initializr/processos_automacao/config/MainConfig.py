"""
#   MainConfig tem como função a criação de um novo subprocesso, com base
# no caminho do arquivo a ser executado e nas configruações específicas ao
# sistema operacional (Windows ou Linux). A classe utiliza as constantes globais
# CURR_SHELL, que representa o shell de escolha, segundo o SO, e BASE_CMD, que consiste
# no comando base para execução do processo, também de acordo com o SO.
#   Os caminhos dos arquivos dos processos a serem executados encontram-se no módulo
# initializr/processos_automacao/config/robos_main_paths.py, que contém um dict no qual
# as chaves são os nomes das classes dos processos e os valores são os caminhos.
#   O método "build_sub_process" reune as configurações do sistema e o caminho do arquivo
# para criar um novo processo, que será retornado.
"""
import psutil as pt
import subprocess as sp
from pathlib import Path


from initializr.processos_automacao.config.robos_main_paths import main_paths
from initializr.processos_automacao import (
    CURR_SHELL, SO, BASE_CMD
)

from PATHS import project_path


class MainConfig:
    def __init__(self):
        self.__shell = CURR_SHELL
        self.__so = SO
        self.__base_cmd = BASE_CMD
        self.__process_path: str = ""
        self.__process_cmd: list = []

    @property
    def process_path(self):
        return self.__process_path

    @property
    def process_cmd(self):
        return self.__process_cmd

    @property
    def shell(self):
        return self.__shell

    @property
    def operating_system(self):
        return self.__so

    @property
    def base_command(self):
        return self.__base_cmd

    def load_process_path(self, nome_robo: str):
        """
        Carrega o caminho do arquivo no qual será executado o processo.
        O caminho é carregado do arquivo /config/robos_main_paths.py,
        que contém um dict com os nomes dos robos referenciando os caminhos
        dos processos.
        """
        path = Path(project_path()+main_paths[nome_robo])
        self.__process_path = str(path)
        self.__set_cmd_target_path()

    def __set_cmd_target_path(self):
        new_cmd: list = BASE_CMD.copy()
        new_cmd[-1] += f" {self.process_path}"

        self.__process_cmd = new_cmd

    def build_sub_process(self, args: str="") -> pt.Process:
        """
        De acordo com o sistema operacional, reune o comando base, o shell de
        comando e o caminho do processo em uma única linha de comando que executará
        o processo.
        """
        if not self.__process_path:
            raise Exception(
                "Property <MainConfig.__process_cmd> must be set,"
                " using MainConfig.load_process_path method.")
        if args:
            if args not in self.__process_cmd[-1]:
                arg_cmd = self.__process_cmd[-1] + args
                self.__process_cmd[-1] = arg_cmd
        print("Iniciando processo:", self.__process_cmd)
        process = None
        if "win" in SO:
            process = pt.Popen(self.__process_cmd, creationflags=sp.CREATE_NEW_CONSOLE)
        elif "linux" in SO:
            process = pt.Popen(self.__process_cmd, stderr=sp.PIPE)
        return process


