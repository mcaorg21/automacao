class RestricaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class NotFoundResultException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class CaptchaRecusadoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ErroDadosProposta(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


class ErroRetornarFila(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class DadosBancariosException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PreenchimentoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class TaxaSuperiorException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message: str = message


class PularCheckboxException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class RefinIndisponivelException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __repr__(self):
        return self.message


class SessaoExpiradaError(ConnectionError):
    def __init__(self):
        self.__msg = "Sessao Expirada"

    def __repr__(self):
        return self.__msg


class MargemNaoPreenchidaException(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Margem não preenchida no fomulário de inserção."

    def __repr__(self):
        return self.msg


class ParcelaNaoEncontradaException(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Parcela não foi gerada no fomulário de inserção."

    def __repr__(self):
        return self.msg


class TentativaAcessoCampoVazio(Exception):
    def __init__(self, campo):
        super().__init__()
        self.msg = (f"Campo {campo} vazio. Favor verificar "
                    f"se foi atribuido algum valor ao campo.")

    def __repr__(self):
        return self.msg


class ValidacaoInsercaoException(Exception):
    def __init__(self, campo, dado):
        self.msg = f"Não foi possível validar o campo <{campo}> com o valor <{dado}>"

    def __repr__(self):
        return self.msg


class DadoIndisponivelException(Exception):
    def __init__(self, nome: str, valor: str = ""):
        self.msg = f"Dado [{nome} : {valor}] indisponível no site"

    def __repr__(self):
        return self.msg

class PreenchimentoTabelaException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __repr__(self):
        return self.message
