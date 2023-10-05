from typing import List
import re

from sites.baseRobos.core.captcha import TwoCaptcha
from sites.baseRobos.core.uconecte import Uconecte
from sites.ibConsig.IbConsigInsercao.data.registros_erros import registro_erros_form_identificacao
from sites.ibConsig.libs.exceptions.Exceptions import *


class ErrorHandler:
    def __init__(self, codigoCon: str):
        self.codigoCon: str = codigoCon
        self.registroErros: List[dict] = []
        self.msgErro: str = ""
        self.tratativaSelecionada: dict = {}
        self.idCaptcha: str = '0'
        self.captchaAprovado: bool = False
        self.repreencherFormulario: bool = False
        self.atualizarContrato: bool = False

    def flush(self):
        self.msgErro = None
        self.tratativaSelecionada = None
        self.captchaAprovado = None
        self.repreencherFormulario = None
        self.atualizarContrato = None

    def avaliarTratativasDeErro(self):
        print(self.tratativaSelecionada, self.msgErro)
        if not self.msgErro:
            return
        for mensagem in self.registroErros:

            regex = re.compile(mensagem['texto'])
            mensagem_encontrada = regex.search(self.msgErro)

            print(f"Reg: {mensagem['texto']} - Erro: {self.msgErro}")

            if not mensagem_encontrada:
                continue

            self.captchaAprovado = mensagem.get('aprovar', False)
            self.repreencherFormulario = mensagem.get("preenchimento", False)
            self.atualizarContrato = mensagem.get("atualizar", False)

            self.tratativaSelecionada = mensagem
            break

    def aplicarTratativasDeErro(self):
        print(self.tratativaSelecionada, self.msgErro)
        if self.tratativaSelecionada is None:
            return True
        
        if self.repreencherFormulario:
            raise PreenchimentoException(
                message='Não foi possível passar do formulário de identificação')
        if self.atualizarContrato:
            Uconecte().atualizar_contrato(
                codigo_contrato=self.codigoCon,
                dados={
                    "erro": self.msgErro,
                    "mensagem": self.tratativaSelecionada["mensagem"]
                }
            )
            return False

        loc_cpf_vazio = '//*[@id="identificacao-form"]/table/tbody/tr[3]/td[2]/span'
        

        if self.captchaAprovado:
            print('Captcha Aprovado')
            TwoCaptcha(None).mudar_status_captcha(self.idCaptcha, "1")


class ErrorHandlers:
    @staticmethod
    def formularioIdentificacao(codigoCon: str) -> ErrorHandler:
        handler = ErrorHandler(codigoCon)
        handler.registroErros = registro_erros_form_identificacao()
        return handler
