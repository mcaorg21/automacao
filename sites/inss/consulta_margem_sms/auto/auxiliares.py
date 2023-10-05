
import re
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.data_helpers import similaridade
from sites.inss.consulta_margem_sms.data.auxiliares_data import (
    get_beneficios_inss, registro_erros
)
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By
from sites.baseRobos.core.DebugTools import DebugTools
dt = DebugTools(debugging=False)


def verificar_erros(act: SeleniumActions, by: By) -> str:
    locs_erros = [
        '//div/div[2]/main/div/div[2]/label[1]',
        '//div[2]/main/div/main/div[2]/label[1]',
        '//div[3]/div[2]/h1',
        '//*[@id="root"]/div/div[2]/main/div/div[2]/label[1]',
        '//*[@id="root"]/div/div[2]/main/div/main/div[2]/label[1]',
        '//*[@id="root"]/div/div[2]/main/div/span',
        '//*[contains(text(), "erro ao buscar")]',
        '//*[@id="root"]/div/div[3]/main/div/div[2]/label[1]',
        '//*[@id="root"]/div/div[3]/div/div/label[1]',
        '//*[@id="root"]/div/div[3]/main/div/span',
        '//*[@id="root"]/div/div[3]/main/div/div[2]/div[1]/label[1]'
    ]
    act.time_out = 1

    for loc in locs_erros:
        try:
            msg_erro = act.obter_texto(loc, by.XPATH)
            print("Erro no site:", msg_erro)
            act.time_out = 2

            return msg_erro
        except TimeoutException:
            continue

    act.time_out = 2
    return ''


def tratar_erros(erro: str, perfil=''):
    dt.debugger()
    if not erro:
        return

    erros_regex = registro_erros()

    for erro_regex in erros_regex:
        regex = re.compile(erro_regex['erro'])
        erro_encontrado = [erro for match in [
            regex.search(erro)] if match]

        similar = similaridade(erro, erro_regex['erro']) > 90

        if not erro_encontrado and not similar:
            continue

        if 'ErroLoginAtualizar' in erro_regex:
            raise ErroLoginAtualizar({'erro': erro_regex['erro'], "retorno": 0})

        if "ErroDadosConsultaException" in erro_regex:
            raise ErroDadosConsultaException({"erro": erro_regex['erro'], "retorno": 0})

        if 'Atualizar' in erro_regex:
            return {'erro': erro_regex}

        if "Aguardar" in erro_regex:
            # aguardar_n_segundos(1800)
            print('Entrou no aguardar...')
            return {'erro': erro_regex}
            #raise Exception(erro_encontrado)

        if "Pular" in erro_regex:
            print(erro_regex['erro'])
            raise Exception(erro)


def tipo_beneficio(beneficio: str) -> int:
    """
    Função que retorna o código do benefício, sendo essa seleção feita por similaridade do parâmetro com os itens do
    dict tipos, em que o código retornando é aquele que apresenta similaridade superior a 90%.
    :param beneficio: nome do benefício a ser retornado o código
    :return: código do benefício
    """

    tipos = get_beneficios_inss()
    # incluir  APOSENTADORIA POR TEMPO DE SERVICO DE PROFESSORES
    if similaridade(beneficio, "APOSENTADORIA INVALIDEZ - ACIDENTE DE TRABALHO") > 90:
        return 32
    elif similaridade(beneficio, "PENSAO POR MORTE POR ACIDENTE DE TRABALHO") > 90:
        return 2
    elif similaridade(beneficio, "PENSAO MENSAL VITALICIA - SINDROME DA TALIDOMIDA - LEI 7070/82") > 90:
        return 56
    elif similaridade(beneficio, "BENEFÍCIO DE PRESTAÇÃO CONTINUADA A PESSOA IDOSA") > 90:
        return 88
    elif similaridade(beneficio, "BENEFÍCIO DE PRESTAÇÃO CONTINUADA A PESSOA COM DEFICIÊNCIA") > 90:
        return 87

    for chave, tipo in tipos.items():
        if similaridade(tipo, beneficio) > 90:
            return chave

    input("BENEFICIO NÃO ENCONTRADO NA TABELA, VERIFIQUE O QUE OCORREU! >>> HELPERS.PY <<<")


class ErroDadosConsultaException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class ErroLoginAtualizar(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

class ErroLoading(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

class BeneficioCancelado(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

