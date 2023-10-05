def dados_erros_identificados(datas):
    erros = [
        # {
        #     "erro": "Nenhuma proposta encontrada para o intervalo de 0 mês. Período: {} à {}.".format(
        #         datas['inicial'], datas['final']),
        #     "mensagem": "Sem possibilidade de baixar contrato"
        # },
        {
            'erro': "Nenhuma proposta encontrada para o(s) filtro(s) informado(s).",
            'mensagem': "Sem possibilidade de anexar"
        }, {
            'erro': "O telefone celular informado já está associado a outro CPF. Favor entrar em contato com o "
                    "parceiro Olé para solicitar alteração.",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': "O telefone celular informado já está associado a outro CPF.",
            'mensagem': "Aguardando Autorização",
            'observacao': "Telefone vinculado a outro CPF.",
            'textoMensagem': "O telefone informado por você está vinculado à outro CPF. Informe um outro telefone celular.",
            'pedidoDocumentacao': 5
        }, {
            'erro': 'Data de emissão do RG deve ser maior que a data de nascimento.',
            'mensagem': 'Reprovado a Conferir',
            'observacao': 'Realizar por outro banco pois data RG é maior que data de nascimento.'
        }, {
            'erro': "Não existe produto para as condições informadas.",
            'mensagem': "Reprovado a Conferir",
            'observacao': "Veja no histórico. Provavelmente em função da idade (confira) o pedido foi reprovado."
        }, {
            'erro': "Cliente possui contrato com inadimplência.",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': "CPF não aprovado.",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': "Valor solicitado é maior do que o permitido para a Idade do Financiado.",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': 'Cliente não atende à regra interna deste benefício.',
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': 'CPF possui restrição.',
            'mensagem': "Reprovado a Conferir"
        },
        {
            'erro': "Número da agência é obrigatório.",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na identificação da agência."
        }, {
            'erro': "Agência selecionada não é permitida para Forma de Pagamento .",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na identificação da agência."
        }, {
            'erro': "Telefone celular informado não é um tipo de telefone celular válido.",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na inserção do telefone celular"
        }, {
            'erro': 'Saldo devedor mais valor solicitado excede o valor de RISCO MÁXIMO.',
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema ao calcular a simulação"
        }, {
            'erro': 'A extensão do documento é inválida.',
            'mensagem': "Anexo no formato invalido"
        }, {
            'erro': 'O tamanho total dos arquivos excedeu o limite máximo de 10MB.',
            'mensagem': "Arquivo acima de 10 MB"
        }, {
            'erro': 'A extensão do(s) arquivo(s) é inválida para o produto.',
            'mensagem': "Anexo no formato invalido"
        }, {
            'erro': 'Benefício inativado pelo órgão. Em caso de dúvidas, gentileza verificar junto ao INSS.',
            'mensagem': "Reprovado a Conferir",
            'observacao': "Benefício cessado"
        }, {
            'erro': r"CEP na lista restritiva.",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r'object reference not set to an instance of an object',
            'mensagem': "ErrorOleException"
        }, {
            'erro': r'Pagina fora do ar.',
            'mensagem': "ErrorOleException"
        }, {
            "erro": "Erro encontrado: CPF com suspeita de óbito.",
            "mensagem": "Reprovado a Conferir"
        }, {
            "erro": "Já existe um dossiê ativo ou proposta paga com aceite para este CPF vinculado ao celular "
                    r"([(]\d{2}[)]\s\w{5}-\w{4}).",

            'mensagem': "Aguardando Autorização",
            'textoMensagem': "Como você já fez operações neste banco com o telefone celular |CELULAR|, " 
                            r"precisamos que nos informe este para conseguirmos seguir com a operação. "
                            r"Caso queira mudar basta nos informar para abrirmos o chamado no banco, que leva cerca de 24 horas para a troca.", 
            'pedidoDocumentacao': 3,
            'interacaoHumana': 1
        }, {
            'erro': r'CEP é obrigatório',
            'mensagem': "ErrorOleException"
        }, {
            'erro': r'CEP inválido',
            'mensagem': "Aguardando Autorização",
            'textoMensagem': "O CEP informado por você está inválido. Favor confirmar número do CEP.", 
            'pedidoDocumentacao': 3,
            'interacaoHumana': 1
        }, {
            'erro': r'parece que você informou muitos e-mails incorretos nas últimas digitações',
            'mensagem': "ErrorOleException"
        }, {
            'erro': r'CEP consta na lista restritiva',
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r'O e-mail informado já está associado a outro CPF',
            'mensagem': "Aguardando Autorização",
            'observacao': "Email vinculado a outro CPF.",
            'textoMensagem': "O email informado por você está vinculado à outro CPF. Informe um outro.",
            'pedidoDocumentacao': 3
        },{
            'erro': r"Valor da taxa está fora dos limites do parâmetro.",
            'mensagem': "Reprovado a Conferir",
            'textoMensagem': "Banco não disponibilizou uma taxa de portabilidade que viabilizasse a operação."
        },{
            'erro': r"Não foi possível simular comissionamento do complemento de portabilidade com os dados informados.",
            'mensagem': "ErrorOleException"
            #'mensagem': "Reprovado a Conferir",
            #'textoMensagem': "Banco não disponibilizou uma taxa de portabilidade que viabilizasse a operação."
        },{
            'erro': r"Já existe uma proposta ativa para este CPF/Contrato.",
            'mensagem': "Inserir pos",
            'observacao': "Como existe uma outra proposta em andamento somente poderemos inserir após finalização.",
            'adiarPropostaDias': 3
        },{
            'erro': r"O valor total do contrato, somando outras operações existentes, excede o RISCO MÁXIMO. Refaça a simulação para enquadrar a operação dentro da regra.",
            'mensagem': "Reprovado a Conferir",
            'observacao': "Risco máximo atingido no banco."
        },{
            'erro': r"Este convenio não poderá ser utilizado, pois o cliente possuirá \d{2} anos no vencimento da operação",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Diminua o prazo do contrato",
            'mensagem': "Conferir dados do contrato",
            'interacaoHumana': 1
        },{
            'erro': r'Matrícula inválida',
            'mensagem': "Reprovado a Conferir",
            'observacao': "Matrícula incorreta"
        },{
                'erro': r"CPF não encontrado na Dataprev. Verifique o número informado e tente novamente",
                'mensagem': "Reprovado a Conferir"
        },{
            'erro': r'Órgão é obrigatório',
            'observacao': "Cadastrar órgão no campo dentro do contrato",
            'mensagem': "Conferir dados do contrato"
        }
    ]

    return erros


def dados_erros_regex():
    erros = [
        {
            'erro': r"Este convenio não poderá ser utilizado, pois o cliente possuirá \d{2} anos no vencimento da operação",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Diminua o prazo do contrato",
            'mensagem': "Conferir dados do contrato",
            'interacaoHumana': 1
        }, {
            'erro': r"Este convenio não poderá ser utilizado, pois o cliente possui \d{2} anos",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r"Endereço\(s\) inexistente\(s\) para o CEP informado.",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na inserção do endereço, conferir o CEP informado!"
        }, {
            'erro': r"Data de nascimento divergente da Receita Federal",
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r"Dados cadastrais consultados. Beneficiário não poderá ser atendido pois não possui margem consignável disponível para empréstimo.",
            'mensagem': "Reprovado a Conferir",
            'observacao': "Margem Insuficiente"
        }, {
            'erro': r"O telefone precisa estar no formato",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na inserção do telefone celular"
        }, {
            'erro': r"O valor solicitado, somando outras operações existentes, excede o RISCO MÁXIMO. Refaça a simulacão para enquadrar a operação dentro da regra.",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema no cálculo de parcelas"
        }, {
            'erro': r'Service Unavailable',
            'mensagem': 'ErrorOleException'
        }, {
            'erro': r"Para prosseguir, a Data de Liberação informada deve ser igual à \d{2}\/\d{2}\/\d{4}",
            'mensagem': 'ErrorOleException'
        }, {
            'erro': r"Não foi possivel consultar parcelas do Produto.",
            'mensagem': 'ErrorOleException'
        },  {
            'erro': r"Data emissão RG não pode ser maior que a data atual.",
            'mensagem': "Aguardando Autorização",
            'textoMensagem': "Confirme por favor a data de emissão completa do seu RG.",
            'pedidoDocumentacao': 3,
            'interacaoHumana': 1
        }, {
            'erro': r'Valor financiado não pode ser menor que o valor mínimo '
                    r'cadastrada no produto. valor mínimo: \d{3}',
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r'object reference not set to an instance of an object',
            'mensagem': "ErrorOleException"
        },
        # {
        #     'erro': "Ocorreu um erro inesperado, tente novamente mais tarde.",
        #     'mensagem': "ErrorOleException"
        # }
        {
            'erro': ("Erro encontrado: O valor da parcela "
                     "excede o valor máximo calculado sobre a renda."),
            'mensagem': "Conferir dados do contrato",
            'observacao': "Inserir manualmente",
            'interacaoHumana': 1
        }, {
            'erro': r"O telefone celular informado já está associado a outro CPF.",
            'mensagem': "Aguardando Autorização",
            'textoMensagem': "O telefone informado por você já está registrado "
                             "para outro cpf. Informe outro telefone celular.",
            'pedidoDocumentacao': 5,
            'interacaoHumana': 1,
            'observacao': 'Inserir manualmente',

        }, {
            "erro": "Erro encontrado: CPF com suspeita de óbito.",
            "mensagem": "Reprovado a Conferir"
        }, {
            "erro": "Erro encontrado: O CPF é inválido ou está em um formato inválido.",
            'mensagem': "Conferir dados do contrato"
        }, {
            "erro": "Já existe um dossiê ativo ou proposta paga com aceite para este CPF vinculado ao celular "
                    r"([(]\d{2}[)]\s\w{5}-\w{4}).",

            'mensagem': "Aguardando Autorização",
            'textoMensagem': "Como você já fez operações neste banco com o telefone celular |CELULAR|, " 
                            r"precisamos que nos informe este para conseguirmos seguir com a operação. "
                            r"Caso queira mudar basta nos informar para abrirmos o chamado no banco, que leva cerca de 24 horas para a troca.", 
            'pedidoDocumentacao': 3,
            'interacaoHumana': 1
        }, {'erro': 'Erro encontrado: Endereço(s) inexistente(s) para o CEP informado.',
            'mensagem': "Conferir dados do contrato"
            }, {
            'erro': ('Erro encontrado: Benefício inativado pelo órgão. '
                     'Em caso de dúvidas, gentileza verificar junto ao INSS.'),
            'mensagem': "Conferir dados do contrato"
        }, {
            'erro': 'OCORREU UM ERRO INESPERADO, TENTE NOVAMENTE MAIS TARDE.',
            'mensagem': 'ErrorOleException'
        }, {
            'erro': (r'Este convenio não poderá ser utilizado, pois o cliente possuirá \d+ anos'
                     r' no vencimento da operação e não existem planos à serem aplicados para cadastro '
                     r'da proposta devido o limite de idade ser de \d+ anos no vencimento da Operação. '
                     r'Favor utilizar outro convenio.'),
            "mensagem": "Reprovado a Conferir"

        }, {
            'erro': r'CEP consta na lista restritiva',
            'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r'O e-mail informado já está associado a outro CPF',
            'mensagem': "Aguardando Autorização",
            'observacao': "Email vinculado a outro CPF.",
            'textoMensagem': "O email informado por você está vinculado à outro CPF. Informe um outro.",
            'pedidoDocumentacao': 3
        },{
            'erro': r'Matrícula inválida',
            'mensagem': "Conferir dados do contrato",
            'observacao': "Matrícula incorreta"
        },{
                'erro': r"CPF não encontrado na Dataprev. Verifique o número informado e tente novamente",
                'mensagem': "Reprovado a Conferir"
        }, {
            'erro': r'VALOR DA PARCELA NÃO PODE ULTRAPASSAR O VALOR LIMITE DE',
            'mensagem': "Conferir dados do contrato",
            'observacao': "Parcela acima do valor permitido pelo banco.",
            'interacaoHumana': 1
        }
    ]

    return erros
