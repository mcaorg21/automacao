from time import sleep


def registro_erros_form_insercao(**kwargs) -> list:
    alert_text = kwargs.get('alert_text', "")

    vals_ideais = kwargs.get('vals_ideais', {'null': 'null'})

    if not vals_ideais:
        vals_ideais = {'null': 'null'}

    return [
        {
            'erro': r'Taxa do troco superior à máxima do convênio',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': 'Não achou tabela para adequar a taxa ponderada do refinanciamento.',
            'textoMensagem': 'Não achou tabela para adequar a taxa ponderada do refinanciamento.',
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }
        ,
        {
            'erro': r'diferente do cadastro da Receita Federal',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': alert_text,
            'textoMensagem': alert_text,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 1
        }
        ,
        {
            'erro': r'Não foi encontrada nenhuma Tabela de TAC e a entidade não está parametrizada para utilizar a tabela padrão.',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': 'Analfabeto ou tabela de refin possui taxa de juros menor.',
            'textoMensagem': 'Analfabeto ou tabela de refin possui taxa de juros menor.',
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 1
        }
        ,
        {
            'erro': 'Agência não encontrada',
            'atualizar': True,
            'mensagem': "Aguardando Autorização",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Agência incorreta:' + alert_text,
            'textoMensagem': 'Favor confirmar o número da agência.',
            'pedidoDocumentacao': 3,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 1
        },
        {
            'erro': r"CEP não foi informado",
            'atualizar': True,
            'mensagem': "Aguardando Autorização",
            'observacao': 'Conferir os dados de endereço informados pelo cliente.',
            'textoMensagem': 'Favor conferir seu endereço completo. E também o CEP, pois o informado o banco não está aceitando.',
            'pedidoDocumentacao': 3,
            'modal': True,
            'textoModal': alert_text
        }, {
            'erro': r"Não foi possível alterar o registro deste servidor, "
                    r"pois já existe outro com a mesma matrícula e mesmo "
                    r"órgão cadastrado no Sistema.",
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': "O CPF vinculado ao pedido é de outra pessoa. "
                          "Para adicionar um novo perfil, no canto "
                          "superior direito clique no ícone de configurações "
                          "e escolha GERENCIAR PERFIS. Assim "
                          "poderá adicionar outra pessoa à sua conta. "
        }, {
            'erro': r'Idade: 19',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': "Parametrização de risco operacional não encontrada. Idade."
        }, {
            'erro': r'Parametrização de risco operacional',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': "Parametrização de risco operacional não encontrada. Idade."
        },
        {
            'erro': r'O atributo Valor da Margem informado é inválido.',
            'aceitar': True
        }, {
            'erro': r'Saldo insuficiente',
            'aceitar': True,
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': "Abaixo do minimo permitido."
        }, {
            'erro': r'Campo nome está diferente do cadastro da Receita Federal',
            'aceitar': True
        }, {
            'erro': r'O atributo obrigatório Número do banco não foi informado',
            'dados_bancarios': True
        }, {
            'erro': r'O atributo obrigatório Agência não foi informado',
            'dados_bancarios': True
        }, {
            'erro': r'O DDD do telefone deve possuir 2 dígitos.',
            'atualizar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Conferir os dados de contato informados pelo cliente.'
        }, {
            "erro": "Erro encontrado: Telefone celular 1: O número do telefone deve possuir no mínimo "
                    "8 e no máximo 9 dígitos - zeros à esquerda não são considerados.",
            'atualizar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Conferir os dados de contato informados pelo cliente.'
        }, {
            'erro': r'O atributo obrigatório Margem não foi informado.',
            'pular': True
        }, {
            'erro': r'Taxa não pode ser negativa',
            'atualizar': True,
            'aceitar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Conferir os valores de parcela e prazo.'
        }, {
            'erro': r'A taxa de juros da tabela selecionada não permite refinanciamento',
            'atualizar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Conferir os valores de parcela e prazo.'
        }, {
            'erro': r'Número de prestações inválido conforme parametrização da '
                    r'Entidade. Número de prestações deve ser no máximo: 48',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 48x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 48x. Vamos '
                             'recalcular o contrato neste prazo. A proposta irá '
                             'atualizar para um valor menor e caso não seja do seu '
                             'interesse você pode pedir o cancelamento via chat.',
            'valor': vals_ideais.get('48', 0),
            'prazo': 48,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }, {
            'erro': r'Número de prestações inválido conforme parametrização da Entidade. '
                    r'Número de prestações deve ser no máximo: 60',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 60x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 60x. '
                             'Vamos recalcular o contrato neste prazo. '
                             'A proposta irá atualizar para um valor menor e '
                             'caso não seja do seu interesse você pode pedir '
                             'o cancelamento via chat.',
            'valor': vals_ideais.get('60', 0),
            'prazo': 60,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }, {
            'erro': r'Número de prestações inválido conforme parametrização da Entidade. '
                    r'Número de prestações deve ser no máximo: 36',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 36x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 36x. '
                             'Vamos recalcular o contrato neste prazo. '
                             'A proposta irá atualizar para um valor menor e '
                             'caso não seja do seu interesse você pode pedir '
                             'o cancelamento via chat.',
            'valor': vals_ideais.get('36', 0),
            'prazo': 36,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }, {
            'erro': r'Número de prestações inválido conforme parametrização da Entidade. '
                    r'Número de prestações deve ser no máximo: 72',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 72x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 72x. '
                             'Vamos recalcular o contrato neste prazo. '
                             'A proposta irá atualizar para um valor menor e '
                             'caso não seja do seu interesse você pode pedir '
                             'o cancelamento via chat.',
            'valor': vals_ideais.get('72', 0),
            'prazo': 72,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }, {
            'erro': r'Número de prestações inválido conforme parametrização da Entidade. '
                    r'Número de prestações deve ser no máximo: 24',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 72x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 24x. '
                             'Vamos recalcular o contrato neste prazo. '
                             'A proposta irá atualizar para um valor menor e '
                             'caso não seja do seu interesse você pode pedir '
                             'o cancelamento via chat.',
            'valor': vals_ideais.get('24', 0),
            'prazo': 24,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        },  {
            'erro': r'Número de prestações inválido conforme parametrização da Entidade. '
                    r'Número de prestações deve ser no máximo: 12',
            'atualizar': True,
            'mensagem': "Conferir dados do contrato",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Oferecido prazo menor 12x:' + alert_text,
            'textoMensagem': 'O banco permite o prazo máximo em 12x. '
                             'Vamos recalcular o contrato neste prazo. '
                             'A proposta irá atualizar para um valor menor e '
                             'caso não seja do seu interesse você pode pedir '
                             'o cancelamento via chat.',
            'valor': vals_ideais.get('12', 0),
            'prazo': 12,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        },  {
            'erro': r'Parametrização de risco operacional não encontrada',
            'atualizar': True,
            'mensagem': "Reprovado a Conferir",
            'modal': True,
            'textoModal': alert_text,
            'observacao': 'Parametrização idade' + alert_text,
            'textoMensagem': '',
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 1
        },
        {
            'erro': r'O atributo obrigatório Número de Prestações não foi informado.',
            'atualizar': True,
            'aceitar': True,
            'pular': True
        }
        , {
            'erro': r'O atributo Data Nascimento informado é inválido.',
            'aceitar': True,
            'pular': True
        }, {
            'erro': r"O atributo obrigatório Valor do empréstimo não foi informado.",
            'atualizar': True,
            'aceitar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Valor do empréstimo está zerado? Se não '
                          'Favor atualizae e colocar para inserir automático',
            'pular': True,
            'interacaoHumana': 1
        }, {
            'erro': r"Não é permitido gerar a proposta pois sua taxa "
                    r"(\(\d+\.\d{1,}\%\)) é superior à taxa máxima "
                    r"(\(\d\.\d{1,}\%\)) da entidade.",
            'atualizar_valor': True
        }, {
            'erro': r"Taxa nao pode ser negativa.",
            'atualizar': True,
            'aceitar': True,
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Valor do empréstimo precisa ser atualizado. '
                          'Favor atualiza e colocar para inserir automático',
            'pular': True,
            'interacaoHumana': 1
        }, {
            'erro': r"O atributo obrigatório Valor do empréstimo não foi informado. "
                    r"O atributo obrigatório Número de Prestações não foi informado.",
            'atualizar': True,
            'aceitar': True,
            'mensagem': 'Pular',
            'observacao': 'Valor e prestações não informado.',
            'pular': True,
            'interacaoHumana': 1
        },
        {
            'erro': "Para operações abaixo de R$622.00 orientamos a fazer "
                    "Refinanciamento onde poderá ser liberado um valor maior "
                    "para o cliente. Deseja realmente gravar a "
                    "Operação Nova ao invés do Refinanciamento?",
            'aceitar': True,
            # 'confirmar': True,
            # 'dados_bancarios': True

        }, {
            'erro': 'O atributo obrigatório Forma de Crédito não foi informado.',
            'confirmar': True,
            'dados_bancarios': True
        }, {
            'erro': 'O atributo obrigatório Agência da Ordem de Pagamento não foi informado.',
            'dados_bancarios': True
        }, {
            'erro': r"O atributo obrigatório Nome do pai não foi informado.",
            'atualizar': True,
            'mensagem': "Aguardando Autorização",
            'observacao': 'Pedido nome do pai',
            'textoMensagem': 'Informe nome do pai.',
            'pular': True,
            'interacaoHumana': 1,
            'pedidoDocumentacao': 3
        }, {
            'erro': r"Favor redigitar valores da operação (Valor empréstimo, número de prestações).",
            'ErroDadosProposta': True
        }, {
            'erro': 'Tabela de coeficientes não foi parametrizada corretamente para este produto/loja',
            'aceitar': True,
            'retornar': True
        }, {
            'erro': "Erro encontrado: Agencia de ordem de pagamento vazia.",
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        }, {
            'erro': "Não encontrado!",
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Agencia não encontrada no sistema do banco',
            'atualizar': True
        }, {
            'erro': 'O atributo Conta informado é inválido.',
            'mensagem': "Aguardando Autorização",
            'atualizar': True,
            'modal': True,
            'textoModal': alert_text,
            'pedidoDocumentacao': 3,
            'aceitar': True,
            'pular': True,
            'interacaoHumana': 0
        }, {
            'erro': r"Erro encontrado: Valor relativo ao prazo "
                    r"não encontrado na tabela de simulação.",
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        }, {
            'erro': (r"Erro encontrado: Dados do servidor"
                     r" federal indisponíveis no portal transparência."),
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        }, {
            'erro': 'Erro encontrado: código do órgao no portal transparência = 00000',
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        }, {
            'erro': r'Saldo devedor abaixo do ticket mínimo definido para a portabilidade',
            'atualizar': True,
            'aceitar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': 'Saldo devedor abaixo do ticket mínimo definido para a portabilidade',
        }, {
            'erro': r'Valor da Parcela da Portabilidade deve ser menor que o Saldo Devedor',
            'atualizar': True,
            'aceitar': True,
            'mensagem': "Reprovado a Conferir",
            'observacao': 'Saldo devedor ainda pequeno para a portabilidade.',
        }, {
            'erro': r"Cliente não eleito a contratação devido a política de crédito.",
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aceitar': True,
            'observacao': 'Cliente não eleito a contratação devido a política de crédito.',
        }, {
            'erro': r'CPF com status irregular na Receita Federal',
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aceitar': True,
            'observacao': 'CPF irregular.'
        }, {
            'erro': r'Não foi possível obter o Código do Termo de Autorização',
            'aceitar': True,
            'confirmar': True
        }, {
            'erro': r"Cliente não elegível a contratação",
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aceitar': True,
            'observacao': 'Cliente não eleito a contratação devido a política de crédito.'
        }
    ]


def registro_erros_form_identificacao():
    return [
        {
            'texto': r"Palavra de verificação da imagem está incorreta, por favor tente novamente.",
            'preenchimento': True
        }, {
            'texto': r"A palavra de verificação expirou, por favor gere outra imagem.",
            'preenchimento': True
        }, {
            'texto': r"Sistema temporariamente indisponível. Tente mais tarde.",
            'aprovar': True,
            'preenchimento': True
        }, {
            'texto': r"Cliente não eleito a contratação devido a política de crédito.",
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aprovar': True
        }, {
            'texto': r"CPF com status irregular na Receita Federal.",
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aprovar': True
        }, {
            'texto': 'NÃ£o foi localizado nenhum contrato com os dados fornecidos.',
            'mensagem': 'Reprovado a Conferir',
            'observacao': 'Não achou contrato na lista de possíveis refinanciamentos',
            'atualizar': True,
            'aprovar': True
        }, {
            'texto': (r"Erro encontrado: Dados do servidor"
                     r" federal indisponíveis no portal transparência."),
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        }, {
            'texto': 'Erro encontrado: código do órgao no portal transparência = 00000',
            'mensagem': 'Conferir dados do contrato',
            'atualizar': True,
        },  {
            'texto': r"Não foi encontrado nenhum contrato para o cpf",
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
            'texto': r"Não foi localizado nenhum contrato com os dados fornecidos.",
            'finalizar': True,
            'aprovar': True
        }, {
            'texto': r"Cliente não elegível a contratação",
            'mensagem': 'Reprovado a Conferir',
            'atualizar': True,
            'aprovar': True,
            'observacao': 'Cliente não eleito a contratação devido a política de crédito.'
        }
    ]
