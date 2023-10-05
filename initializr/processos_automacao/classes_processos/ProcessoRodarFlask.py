from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper
from initializr.processos_automacao.config.MainConfig import MainConfig
from time import sleep
from initializr.processos_automacao import STDWAIT



class Rodar_Flask(ProcessWrapper):
    def __init__(self):
        super().__init__(proc_name=self.__class__.__name__)
        self.__config: MainConfig = MainConfig()
        self.__config.load_process_path(self.proc_name)

    @property
    def main_config(self) -> MainConfig:
        return self.__config

    def run(self):
        process = self.__config.build_sub_process()
        self.cmd_proc = process
        self.set_py_sub_process(process)

        sleep(STDWAIT)
        self.all_procs = process.children(recursive=True)