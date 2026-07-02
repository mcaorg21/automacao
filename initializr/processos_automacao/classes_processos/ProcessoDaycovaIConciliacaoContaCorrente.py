from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper
from initializr.processos_automacao.config.MainConfig import MainConfig
from time import sleep
from initializr.processos_automacao import STDWAIT
import json
from datetime import datetime, timedelta
from pathlib import Path
from PATHS import project_path


class DaycovaIConciliacaoContaCorrente(ProcessWrapper):
    def __init__(self):
        super().__init__(proc_name=self.__class__.__name__)
        self.__config: MainConfig = MainConfig()
        self.__config.load_process_path(self.proc_name)

    @property
    def main_config(self) -> MainConfig:
        return self.__config

    def _proxima_execucao_futura(self) -> bool:
        try:
            config_path = Path(project_path()) / "daycoval-conciliacao-conta-corrente/config.json"
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
            proxima = config.get("proxima_execucao", "")
            if not proxima:
                return False
            dt = datetime.strptime(proxima, "%Y-%m-%dT%H:%M:%S")
            if dt > datetime.now():
                print(f"[{self.proc_name}] Próxima execução agendada para {dt.strftime('%d/%m/%Y às %H:%M')}. Processo não iniciado.")
                return True
            return False
        except Exception:
            return False

    def _consumir_executar_agora(self) -> bool:
        try:
            config_path = Path(project_path()) / "daycoval-conciliacao-conta-corrente/config.json"
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
            if config.get("executar_agora"):
                config["executar_agora"] = False
                with open(config_path, "w", encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"[{self.proc_name}] Execução forçada manualmente. Ignorando restrições.")
                return True
            return False
        except Exception:
            return False

    def _dia_execucao_permitido(self) -> bool:
        try:
            config_path = Path(project_path()) / "daycoval-conciliacao-conta-corrente/config.json"
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
            dias = config.get("dias_execucao", [])
            if not dias:
                return True
            hoje = datetime.now().isoweekday()  # Seg=1 ... Dom=7
            if hoje not in dias:
                nomes = {1:'Segunda',2:'Terça',3:'Quarta',4:'Quinta',5:'Sexta',6:'Sábado',7:'Domingo'}
                print(f"[{self.proc_name}] Hoje é {nomes.get(hoje, hoje)}. Dias permitidos: {dias}. Processo não iniciado.")
                return False
            return True
        except Exception:
            return True

    def _atualizar_datas(self):
        try:
            config_path = Path(project_path()) / "daycoval-conciliacao-conta-corrente/config.json"
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
            hoje = datetime.now().date()
            config["data_inicial"] = (hoje - timedelta(days=7)).isoformat()
            config["data_final"] = hoje.isoformat()
            with open(config_path, "w", encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"[{self.proc_name}] Datas atualizadas: {config['data_inicial']} a {config['data_final']}")
        except Exception as e:
            print(f"[{self.proc_name}] Erro ao atualizar datas: {e}")

    def run(self):
        if self._consumir_executar_agora():
            pass  # soberano: ignora proxima_execucao e dias_execucao
        elif self._proxima_execucao_futura():
            return
        elif not self._dia_execucao_permitido():
            return

        self._atualizar_datas()

        process = self.__config.build_sub_process()
        self.cmd_proc = process
        self.set_py_sub_process(process)

        sleep(STDWAIT)
        self.all_procs = self.get_children_safe(process)
