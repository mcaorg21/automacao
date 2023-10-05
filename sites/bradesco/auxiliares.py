from sites.baseRobos.core.data_helpers import similaridade
from typing import List

erros: List[dict] = [
    {
        "erro": "Sessão Expirada",
        "login": True
    }
]


def identificar_erros_sessao(txt_erro: str, throw=False) -> bool:
    # raises ErroSessaoException
    for erro in erros:
        similar: bool = similaridade(erro["erro"], txt_erro) > 90

        if similar and throw:
            raise ErroSessaoException(str(txt_erro))
        elif similar:
            return True

    return False


class ErroSessaoException(Exception):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return self.msg
