from sites.baseRobos.core.data_helpers import similaridade
from datetime import datetime


def tipo_beneficio(beneficio):
    """
    Função que retorna o código do benefício, sendo essa seleção feita por similaridade do parâmetro com os itens do
    dict tipos, em que o código retornando é aquele que apresenta similaridade superior a 90%.
    :param beneficio: nome do benefício a ser retornado o código (str)
    :return: código do benefício (int)
    """

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

    tipos = {
        1: 'PENSAO POR MORTE DE TRABALHADOR RURAL',
        2: 'PENSAO POR MORTE ACIDENTARIA-TRAB. RURAL',
        3: 'PENSAO POR MORTE DE EMPREGADOR RURAL',
        4: 'APOSENTADORIA POR INVALIDEZ-TRAB. RURAL',
        5: 'APOSENT. INVALIDEZ ACIDENTARIA-TRAB.RUR.',
        6: 'APOSENT. INVALIDEZ EMPREGADOR RURAL',
        7: 'APOSENTADORIA POR VELHICE - TRAB. RURAL',
        8: 'APOSENT. POR IDADE - EMPREGADOR RURAL',
        19: 'PENSAO DE ESTUDANTE (LEI 7.004/82)',
        20: 'PENSAO POR MORTE DE EX-DIPLOMATA',
        21: 'PENSAO POR MORTE PREVIDENCIARIA',
        22: 'PENSAO POR MORTE ESTATUTARIA',
        23: 'PENSAO POR MORTE DE EX-COMBATENTE',
        24: 'PENSAO ESPECIAL (ATO INSTITUCIONAL)',
        26: 'PENSAO POR MORTE ESPECIAL',
        27: 'PENSAO MORTE SERVIDOR PUBLICO FEDERAL',
        28: 'PENSAO POR MORTE REGIME GERAL',
        29: 'PENSAO POR MORTE EX-COMBATENTE MARITIMO',
        32: 'APOSENTADORIA INVALIDEZ PREVIDENCIARIA',
        33: 'APOSENTADORIA INVALIDEZ AERONAUTA',
        34: 'APOSENT. INVAL. EX-COMBATENTE MARITIMO',
        37: 'APOSENTADORIA EXTRANUMERARIO CAPIN',
        38: 'APOSENT. EXTRANUM. FUNCIONARIO PUBLICO',
        41: 'APOSENTADORIA POR IDADE',
        42: 'APOSENTADORIA POR TEMPO DE CONTRIBUIÇÃO',
        43: 'APOSENT. POR TEMPO SERVICO EX-COMBATENTE',
        44: 'APOSENTADORIA ESPECIAL DE AERONAUTA',
        45: 'APOSENT. TEMPO SERVICO JORNALISTA',
        46: 'APOSENTADORIA ESPECIAL',
        49: 'APOSENTADORIA ORDINARIA',
        51: 'APOSENT. INVALIDEZ EXTINTO PLANO BASICO',
        52: 'APOSENT. IDADE EXTINTO PLANO BASICO',
        54: 'PENSAO ESPECIAL VITALICIA - LEI 9793/99',
        55: 'PENSAO POR MORTE EXTINTO PLANO BASICO',
        56: 'PENSAO VITALICIA SINDROME TALIDOMIDA',
        57: 'APOSENT. TEMPO DE SERVICO DE PROFESSOR',
        58: 'APOSENTADORIA DE ANISTIADOS',
        59: 'PENSAO POR MORTE DE ANISTIADOS',
        60: 'PENSAO ESPECIAL PORTADOR DE SIDA',
        72: 'APOSENT. TEMPO SERVICO - LEI DE GUERRA',
        78: 'APOSENTADORIA IDADE - LEI DE GUERRA',
        81: 'APOSENTADORIA COMPULSORIA EX-SASSE',
        82: 'APOSENTADORIA TEMPO DE SERVICO EX-SASSE',
        83: 'APOSENTADORIA POR INVALIDEZ EX-SASSE',
        84: 'PENSAO POR MORTE EX-SASSE',
        87: 'AMPARO ASSISTENCIAL AO DEFICIENTE',
        88: 'AMPARO ASSISTENCIAL AO IDOSO',
        89: 'PENSAO ESP. VITIMAS HEMODIALISE-CARUARU',
    }

    for chave, tipo in tipos.items():
        if similaridade(tipo, beneficio) > 90:
            return chave

    input("BENEFICIO NÃO ENCONTRADO NA TABELA, VERIFIQUE O QUE OCORREU! >>> HELPERS.PY <<<")


def get_agencia(banco):
    """
    Obtém a agência a partir de um array no seguinte formato: AA - NOME DO BANCO
    :param banco: array contendo o banco e agência (str)
    :return: código da agência (str)
    """
    cod = ''
    for letter in banco:
        if letter.isdigit():
            cod = cod + letter

    return cod


def formatar_valor(valor, seletor):
    """
    Formata o valor de moeda para padrão americano, sendo duas opções, uma com o valor contendo R$ e outra somente com o
     valor.
    :param valor: valor a ser formatado, podendo ser R$ XXXX,xx ou somente XXXX,xx. (str)
    :param seletor: seleciona qual o modelo do valor, sendo que True para valor contendo R$ e False caso contrário(bool)
    :return: valor formatado no padrão americano. (str)
    """
    if seletor:
        return valor[2:].replace(".", "").replace(",", ".").strip()
    else:
        return valor.replace(".", "").replace(",", ".").strip()


def formatar_matricula(matricula, tipo):
    """
    Formata a matrícula da solicitação para o mesmo formata que a matrícula se encontra no portal.

    :param tipo: seletor para caso a matricula já possua o '-' incorporado ou não.
    :param matricula: matricula da solicitação.
    :return: matricula formatada.
    """
    aux = ''
    count = 0
    for letter in str(matricula):
        if count % 3 == 0 and count > 0:
            if count != 9:
                aux += '.'
            else:
                if tipo == 1:
                    aux += '-'
        aux += letter
        count += 1

    return aux


def calcula_parcelas_pagas(inicio):
    """
    Calcula a quantidade de parcelas pagas com base no mês de início da cobrança e no mês atual.

    :param inicio: data de início da cobrança, no modelo de DD/MM/AAAA. (str)
    :return: valor inteiro da quantidade de parcelas pagas. (int)
    """
    mes_inicio = int(inicio[:2])
    ano_inicio = int(inicio[3:])
    data = datetime.now()

    if data.year == ano_inicio:
        return mes_inicio - data.month
    else:
        return ((data.year - ano_inicio) * 12) - (mes_inicio - data.month)
