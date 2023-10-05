import logging as log
from inspect import getframeinfo, stack
from time import sleep

class DebugTools(log.Logger):
    def __init__(self, name="Default", debugging=True):
        super().__init__(name)
        self.debugging = debugging
        if self.debugging:
            log.warning("\n[!] DEBUGGING = TRUE   [!]"
                        "\n[!] BREAKPOINTS ATIVOS [!]\n"
                        f"{getframeinfo(stack()[1][0]).filename}")
            self.level = log.DEBUG

    def debug_mode(self, mode: bool):
        self.debugging = mode

        if not self.debugging:
            self.level = log.INFO

    @staticmethod
    def prompt_warning(msg: str):
        log.warning(msg)
        input("[aperte qualquer tecla para seguir]: ")

    def debugger(self):
        if not self.debugging:
            return lambda: 1
        sleep(0.2)
        self.warning(getframeinfo(stack()[1][0]).filename)
        sleep(0.2)
        self.warning(("Linha:", getframeinfo(stack()[1][0]).lineno))
        sleep(0.5)
        return breakpoint()
