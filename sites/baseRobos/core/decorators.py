from typing import Callable
from functools import wraps, partial
from sites.baseRobos.core.helpers import verificar_horario_comercial, esta_horario_comercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError


def __apenas_horario_comercial(func: Callable, inicio: int, fim: int) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not esta_horario_comercial(inicio, fim):
            raise ForaHorarioComercialError
        return func(*args, **kwargs)
    return wrapper


def ApenasHorarioComercial(inicio: int, fim: int):
    return partial(__apenas_horario_comercial, inicio=inicio, fim=fim)


def __aguardar_horario_comercial(func: Callable, inicio: int, fim: int) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        verificar_horario_comercial(inicio, fim)
        return func(*args, **kwargs)
    return wrapper


def AguardarHorarioComercial(inicio: int, fim: int):
    return partial(__aguardar_horario_comercial, inicio=inicio, fim=fim)
