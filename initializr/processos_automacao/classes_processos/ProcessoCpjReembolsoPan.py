from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper
from initializr.processos_automacao.config.MainConfig import MainConfig
from time import sleep
from initializr.processos_automacao import STDWAIT
import json
from pathlib import Path
from PATHS import project_path


class CpjReembolsoPan(ProcessWrapper):
    def __init__(self):
        super().__init__(proc_name=self.__class__.__name__)
        self.__config: MainConfig = MainConfig()
        self.__config.load_process_path(self.proc_name)

    @property
    def main_config(self) -> MainConfig:
        return self.__config

    def _config_valida(self) -> bool:
        try:
            config_path = Path(project_path()) / "cpj-reembolso-pan/config.json"
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
            numero = config.get("numero_recibo", "")
            data_ini = config.get("data_inicial", "")
            data_fim = config.get("data_final", "")
            return bool(numero and numero.isdigit() and data_ini and data_fim)
        except Exception:
            return False

    def run(self):
        if not self._config_valida():
            print(f"[{self.proc_name}] Configuração incompleta (numero_recibo, data_inicial ou data_final ausentes). Processo não iniciado.")
            return

        process = self.__config.build_sub_process()
        self.cmd_proc = process
        self.set_py_sub_process(process)

        sleep(STDWAIT)
        self.all_procs = self.get_children_safe(process)
