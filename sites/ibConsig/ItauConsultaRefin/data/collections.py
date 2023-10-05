
def registro_erros_form_identificacao_refin():
    return [
        {
            'texto': r"Não foi encontrado nenhum contrato para o cpf",
            'finalizar': True,
            'aprovar': True
        }, {
            'texto': r"Não foi localizado nenhum contrato com os dados fornecidos.",
            'finalizar': True,
            'aprovar': True
        }, {
            'texto': r"Palavra de verificação da imagem está incorreta, por favor tente novamente.",
            'preencher': True
        }, {
            'texto': r"A palavra de verificação expirou, por favor gere outra imagem.",
            'preencher': True
        }, {
            'texto': r"Não foi possível localizar código do cliente com o CPF.",
            'finalizar': True,
            'aprovar': True
        }, {
            'texto': r"NÃ£o foi localizado nenhum contrato com os dados fornecidos.",
            'finalizar': True,
            'aprovar': True
        },  {
            'texto': r"Cliente não elegível a contratação",
            'finalizar': True,
            'aprovar': True
        }

    ]


def registro_erros_forms_refin():
    return [
        {
            'texto': r"Sistema temporariamente indisponível. Tente mais tarde.",
            'selecionar': True
        }, {
            'texto': r"Favor selecionar pelo menos um contrato para refinanciamento.",
            'selecionar': True
        }, {
            'texto': r"Cliente não eleito a contratação devido a política de crédito.",
            'restricao': True
        }, {
            'texto': r"CPF com status irregular na Receita Federal.",
            'restricao': True
        }, {
            'texto': r"Parametrização de risco operacional não encontrada",
            'restricao': True
        }, {
            'texto': r"Tabela de coeficientes não foi parametrizada corretamente",
            'clicar': True
        }, {
            'texto': r"Não foi possível localizar código do cliente com o CPF.",
            'localizar': True
        }, {
            'texto': r"O atributo Valor da Margem informado é inválido. O atributo obrigatório Margem não foi informado.",
            'pular': True
        }, {
            "texto": "O atributo Data Nascimento informado é inválido.",
            "return": True
        }, {
            "texto": r"Cliente não elegível a contratação",
            'restricao': True
        }
    ]