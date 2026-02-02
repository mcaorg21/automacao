"""
#   A classe ProcessWrapper tem como propósito o gerenciamento de processos externos
# criados pela classe psutil.Popen. Para isso, contém variáveis de instância que
# armazenam dados relativos a um processo e métodos que manipulam esses dados.
#   Os métodos da classe realizam tarefas como verificar se o processo está ativo,
# retornar o estado do processo, matar o processo e todos seus subprocessos,
# filtrar e retornar o subprocesso python filho do processo principal e reiniciar
# o processo, caso não esteja ativo.
"""
import psutil as pt
from typing import List


class ProcessWrapper:
    def __init__(self, proc_name: str):
        self.suprocess: pt.Process = None
        self.cmd_proc: pt.Process = None
        self.all_procs: List[pt.Process] = []
        self.proc_name: str = proc_name
        self.active: bool = True

    def show_children(self):
        if self.cmd_proc is not None:
            try:
                print(self.cmd_proc.children(recursive=True))
            except pt.NoSuchProcess:
                print("Processo não encontrado")

    def get_children_safe(self, process: pt.Process) -> List[pt.Process]:
        """Retorna os filhos do processo de forma segura"""
        try:
            if process is not None:
                return process.children(recursive=True)
        except pt.NoSuchProcess:
            pass
        return []

    @property
    def is_alive(self) -> bool:
        if self.suprocess is None:
            return False
        try:
            return self.suprocess.is_running()
        except pt.NoSuchProcess:
            self.suprocess = None
            return False

    @property
    def proc_status(self):
        return self.proc_name, self.is_alive

    def kill_all(self):
        # Mata o processo principal e todos subprocessos
        if self.cmd_proc is not None:
            for proc in self.all_procs:
                try:
                    proc.kill()
                except Exception as e:
                    pass
        self.suprocess = None

    def kill_cmd_proc(self):
        # Mata o processo específico ao shell de comando
        try:
            if self.cmd_proc is not None:
                self.cmd_proc.kill()
                self.suprocess = None

        except pt.NoSuchProcess as e:
            self.suprocess = None

    def set_py_sub_process(self, process: pt.Process):
        # Filtra o subprocesso python e o atribui à
        # variável de instância <subprocess>
        max_tentativas = 30
        tentativas = 0
        while self.suprocess is None and tentativas < max_tentativas:
            try:
                children = process.children(recursive=True)
                self.suprocess = self.__get_python_proc(children)
            except pt.NoSuchProcess:
                self.suprocess = None
                break
            tentativas += 1

    def reinit_if_dead(self, proc_obj: object, activate: dict, init=False):
        """
        Verifica se o processo está ativo e se está marcado para ser
        ativado no arquivo ativacao.json. Caso ambas as condições sejam
        verdadeiras, mata todos os processos relacionados e reinicia o
        processo desejado.
        :param proc_obj: instância do processo a ser inicializado
        :type proc_obj: ProcessWrapper
        :param activate: diretriz para o processo ser iniciado.
        :type activate: dict
        :param init:  parâmetro que indica se a chamada do método
            ocorre na inicialização do sistema
        """
        if self.is_alive and not activate[self.proc_name]:
            self.kill_all()
            self.kill_cmd_proc()

        elif not self.is_alive and activate[self.proc_name]:
            if not init:
                self.kill_all()
                self.kill_cmd_proc()
            proc_obj.run()

    @staticmethod
    def __get_python_proc(children: List[pt.Process]) -> pt.Process:
        for child in children:
            if "python" in child.name():
                return child

    def __repr__(self):
        return f"{self.proc_status}"
