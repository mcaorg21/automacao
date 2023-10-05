from typing import Callable, List


def filtrar_dados(dados: List[dict], filtro: Callable) -> list:
    return [dado for dado in dados if filtro(dado)]

