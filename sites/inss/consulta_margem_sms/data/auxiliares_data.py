"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: auxiliares_data
| data: 2020-03-02
| autor: Gustavo Belleza

| funcionamento:
"""


def get_beneficios_inss() -> dict:

    return {
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
        57: 'APOSENTADORIA POR TEMPO DE SERVICO DE PROFESSORES',
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
        96: 'PENSAO ESPECIAL HANSENIASE LEI 11520/07'
    }


def registro_erros() -> list:
    return [
        {
            'erro': 'Precisamos confirmar algumas informações para que você possa acessar o Meu INSS',
            'ErroLoginAtualizar': True
        },
        {
            "erro": r"Usuário e/ou senha inválidos.",
            "ErroLoginAtualizar": True
        }, {
            "erro": r"Não foi possível encontrar uma conta para o CPF informado. Por favor, "
                    r"crie sua conta.",
            "ErroLoginAtualizar": True
        }, {
            "erro": r"Não foi possível acessar o Google reCAPTCHA",
            "Pular": True
        }, {
            "erro": r"Ocorreu um erro na tentativa de login.",
            "Pular": True
        }, {
            "erro": r"É necessário definir uma nova senha para o cadastro",
            "ErroLoginAtualizar": True
        }, {
            "erro": r"computador",
            "Aguardar Pular": True
        }, {
            "erro": r"Autorização de uso de dados pessoais",
            "Autorizar": True
        }, {
            "erro": r"Nenhuma informação encontrada para o documento informado \d{10}",
            "Atualizar": True
        }, {
            "erro": r"Ocorreu um erro na sua requisição. Tente novamente mais tarde.",
            "Pular": True
        }, {
            "erro": r"Recuperação de conta",
            "ErroLoginAtualizar": True
        }, {
            "erro": r"Ativação de conta",
            "ErroLoginAtualizar": True

        }, {'erro': ('Não foi possível encontrar uma conta para o '
                     'CPF informado. Por favor, crie sua conta.'),
            "Atualizar": True
            }, {
            'erro': 'Ocorreu um erro ao buscar seus dados.',
            'Aguardar': True
        }, {
            'erro': 'Foram encontradas divergências cadastrais.',
            'ErroDadosConsultaException': True,
        }, {
            "erro": f"O CPF informado não foi localizado na base de dados do INSS (CNIS)",
            "ErroLoginAtualizar": True
        }, {
            'erro': 'Para prosseguir para Meu INSS é necessário atualizar o seu cadastro.',
            "ErroLoginAtualizar": True
        }, {
            'erro': r'Não é possível executar o serviço por divergências cadastrais',
            "ErroDadosConsultaException": True
        }, {
            "erro": r"Captcha inválido. Tente novamente.",
            "Pular": True
        },
    ]

