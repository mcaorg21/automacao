
def registros_erros_refin():
    return [
        {
            'texto': r"Não foi possível realizar a consulta no momento",
            'Continue': True
        }, {
            'texto': r"Banco ou Agência inválido.",
            'Continue': True
        }, {
            'texto': r"Falha de comunicação com o serviço externo após",
            'Continue': True
        }, {
            'texto': r"Agência \d{4} esta inativa.",
            'Continue': True
        }, {
            'texto': r"Quantidade de dígitos informados deve ser igual a 8.",
            'InfoNotFound': True
        }, {
            'texto': r"Quantidade de dígitos informado deve ser no máximo 7.",
            'MatriculaErrorServidor': True
        }, {
            'texto': r"A data informada no campo Dt. Nasc: é inválida",
            'Preenchimento': True
        }, {
            'texto': r"É necessário informar o campo ORGAO",
            'Preenchimento': True
        }, {
            'texto': r"Não existem prazos disponíveis",
            'InfoNotFound': True
        }, {
            'texto': r"Não existem prazos disponíveis nas condições informadas",
            'InfoNotFound': True
        }, {
            'texto': r"Cliente pré-aprovado para prosseguimento da proposta. "
                     "Não existem prazos disponíveis nas condições informadas.",
            'InfoNotFound': True
        }
        , {
            'texto': r"Nenhuma operação encontrada para o CPF\/CNPJ informado",
            'InfoNotFound': True
        }, {
            'texto': r"Recusa Definitiva",
            'Restricao': True
        }, {
            'texto': r"O conteúdo do campo Dt. Nasc",
            'InfoNotFound': True
        }, {
            'texto': (
                "Consulta de Margem. O tipo de operação 'Refinanciamento' não está autorizado "
                "por esse servidor. Margem será calculada pela função."),
            'Continue': True
        }, {
            'texto': ('Não possui contratos. Mensagem Sistema: Nenhuma '
                      'operação encontrada para o CPF/CNPJ informado.'),
            'InfoNotFound': True
        }, {
            "texto": 'Quantidade de parcelas vencidas superior ao permitido!',
            'Restricao': True
        }, {
            'texto': r"É necessário informar o campo EMPREGADOR",
            'InfoNotFound': True
        },{
            'texto': r"Cliente pré-aprovado",
            'Continue': True
        },{
            'texto': r"Quantidade de dígitos informados deve ser igual a",
            'InfoNotFound': True
        },{
            'texto': r"PDR - CPF Cadastrado no Não Me Perturbe",
            'InfoNotFound': True
        }
    ]
