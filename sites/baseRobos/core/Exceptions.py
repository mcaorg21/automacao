from typing import Tuple


class ForaHorarioComercialError(ConnectionAbortedError):
    def __init__(self):
        self.msg = f"Fora do Horário Comercial"

    def __repr__(self):
        return self.msg
