from collections import Callable
from functools import wraps, partial

from sites.elementos import TextInput


def __preencher_se_vazio(func: Callable, text_input: TextInput) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not text_input.esta_vazio():
            return
        return func(*args, **kwargs)
    return wrapper


def PreencherSeVazio(text_input: TextInput):
    return partial(__preencher_se_vazio, text_input=text_input)