"""
Funções que armazenam elementos em list e/ou dict e retornam coleções em
sua totalidade ou elementos específicos de acordo com parâmetros.

Funções de uso específico para classes do robô PanInserção.
"""
from selenium.webdriver.common.by import By


def localizador(label, args=None):
    """
    Localizadores e métodos para a busca dos elementos web em <PanInsercaoAuto>
    :param label: rótulo para identificar o seletor desejado
    :type label: str
    :type args: any
    """
    locs = {
        # Inserção #
        # <preencher_form_login> --------------------------------------------------- #
        'input_cpf_login': ('//*[@id="txtCPF_CAMPO"]', By.XPATH),
        'focus_parceiro': ('//*[@id="cbParceiros_CAMPO_EDIT"]', By.XPATH),
        'select_parceiro': ('//*[@id="cbParceiros_CAMPO"]', By.XPATH),
        'input_senha': ('//input[@id="ESenha_CAMPO"]', By.XPATH),
        'link_entrar': ('//a[@id="LKentrar"]', By.XPATH),

        # <preencher_cadastro_consig_simplificado> -----------------------------------#
        'select_empregador': ('//select[@name="ctl00$Cph$ucP$JN$JpOrg$cbOrg4$CAMPO"]',
                              By.XPATH),
        'select_orgao': ('//select[@name="ctl00$Cph$ucP$JN$JpOrg$cbOrg5$CAMPO"]',
                         By.XPATH),
        'input_cpf_cadastro': ('//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtCPF$CAMPO"]',
                               By.XPATH),
        'dt_nascimento': ('//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtDtNasc$CAMPO"]',
                          By.XPATH),
        'input_ddd': ('//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtDdd$CAMPO"]',
                      By.XPATH),
        'input_telefone': ('//input[@name="ctl00$Cph$ucP$JN$JpOrg$txtTel$CAMPO"]',
                           By.XPATH),
        'input_matricula': ('//input[@name="ctl00$Cph$ucP$JN$JpOrg$ucMat$txtMatricula$CAMPO"]',
                            By.XPATH),
        'a_consulta': ('//a[@id="btnConsultar_txt"]', By.XPATH),
        'frame_modal': 'ctl00_Cph_ucP_ppCli_frameAjuda',
        'header_modal': ('//*[@id="ctl00_cph_FIJanela1"]/tbody/tr[1]/td/div[2]/span',
                         By.XPATH),
        'linhas_tabela_modal':
            ('//table[@id="ctl00_cph_FIJanela1_FIJanelaPanel1_grvHomo"]//tr',
             By.XPATH),
        'link_selec_matricula':
            (f'//table/tbody/tr[1]/td/div/table/tbody/tr[{str(args)}]//a',
             By.XPATH),

        # <preencher_form_insercao> ---------------------------------------------------#
        'select_op': ('//*[@id="ctl00_Cph_ucP_JN_JpTpOper_cbTpOper_CAMPO"]', By.XPATH),
        'ipt_renda': '//*[@id="ctl00_Cph_ucP_JN_JpSim_txtRnd_CAMPO"]',
        'ipt_valor': ('//*[@id="ctl00_Cph_ucP_JN_JpSim_txtVlrSol_CAMPO"]', By.XPATH),
        'a_calcular': ('//*[@id="btnCalcular_txt"]', By.XPATH),
        'tabelaNormalAumento':
            ('//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl15_ckSel"]', By.XPATH),
        'tabelaInvalidezPericiaAumento': (
            '//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl14_ckSel"]', By.XPATH),
        'tabelaInvalidezPericia':
            ('//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl12_ckSel"]', By.XPATH),
        'tabelaNormal':
            ('//*[@id="ctl00_Cph_ucP_JN_JpSim_gvCond_ctl02_ckSel"]', By.XPATH),

        'vr_dados_pessoais': ('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNome_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_cbECivil_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtDoc_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEnd_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtNr_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCompl_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtBai_CAMPO"]',
                              '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtMae_CAMPO"]',
                              ),
        'ipt_email': ('//*[@id="ctl00_Cph_ucP_JN_JpCli_txtEmail_CAMPO"]', By.XPATH),
        'ipt_cep': '//*[@id="ctl00_Cph_ucP_JN_JpCli_txtCEP_CAMPO"]',
        # __modal_meio_liberacao
        'cartao_mag': '//*[@id="ctl00_Cph_ucP_JN_JpAverb_cbCartBen_CAMPO"]',
        'meio_liberacao': '//*[@id="ctl00_Cph_ucP_JN_JpLib_cbLib_CAMPO"]',
        'frame_agencias': '//*[@id="ctl00_Cph_ucP_ppBnc_frameAjuda"]',
        'input_cod_agencia': '//*[@id="ctl00_cph_E_TXTPESC_CAMPO"]',
        'btn_pesquisar': '//*[@id="BB_Pesq_txt"]',
        'a_agencia': '//*[@id="ctl00_cph_GR_Resolt_ctl02_lnkCodigo"]',
        # fim modal
        'select_tipo_conta': ('//*[@id="ctl00_Cph_ucP_JN_JpLib_cbTpCtLib_CAMPO"]', By.XPATH),
        'ipt_cpf_operador': ('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtCpfOrg3o_CAMPO"]',
                             By.XPATH),
        'ipt_nome_operador': ('//*[@id="ctl00_Cph_ucP_JN_JpOperador_txtNomeOrg3o_CAMPO"]',
                              By.XPATH),
        # verificar campos vazios - dados bancários
        'vr_dados_bc_AVB': ('//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtBen_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_cbUFBen_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtBncAvb_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtAgAvb_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtDvAgAvb_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtCtAvb_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpAverb_txtDvCtAvb_CAMPO"]',
                            ),
        # IDEM, porém provavelmente redundante...
        'vr_dados_bc_LIB': ('//*[@id="ctl00_Cph_ucP_JN_JpLib_txtBncLib_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpLib_txtAgLib_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvAgLib_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpLib_txtCtLib_CAMPO"]',
                            '//*[@id="ctl00_Cph_ucP_JN_JpLib_txtDvCtLib_CAMPO"]'),

        'a_salvar_cadastro': ('//*[@id="btnGravar_txt"]', By.XPATH),
        'bt_confirmar': ('//*[@id="btnConfirmar_txt"]', By.XPATH),
        'bt_formalizar': ('//*[@id="btnConfirmar_txt"]', By.XPATH),
        # Exeçoes Confirmar Inserção
        'divergencia': '//span[text()="Aviso de Divergência INSS"]',
        'a_aprovar': '//*[@id="BBApr_txt"]',
        # Assinatura digital #
        # <selecionar_proposta>
        'input_pesquisar': (f'//*[@id="ctl00_Cph_AprCons_txtPesquisa_CAMPO"]', By.XPATH),
        'bt_pesquisar': '//*[@id="btnPesquisar_txt"]',
        'a_status': '//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr[2]/td[6]/a',
        # <selecionar_formalizacao>
        'div_form': '//app-signature-proposals/app-list-item/div/div[1]/div',
        'divs_multi_ass': '//p[contains(text(), "Proposta")]',
        'div_assinar': '//app-signature-proposals/div/div[3]/app-list-item/div/div[2]/div',
        'radio_assinatura': '//pan-radio-option[1]/div/label/div[2]/p[2]',
        'radio_assin_multi_assin': ('//app-capture-type-container/div/div/pan-radio-option['
                                    '1]/div/label/div[1]'),
        'bt_continuar': '//app-footer/div/div/div[2]/pan-button/button/span',
        'a_link': '//*[@id="mh-input-11"]',
        'input_enviar_link': '//app-send-link-container/div/pan-input/div/input',
        'bt_enviar': '//app-send-link-container/div/div[3]/pan-button/button/span'
    }

    return locs[label]


def mensagens_alertas():
    """
    Retorna um dicionário com as mensagens dos alertas e suas devidas
    tratativas.
    :rtype: dict
    """
    return [
        {
            'texto': r'NPR- Recusa Definitiva - Fora Da Politica Do Banco',
            'tratamento': ['atualizar'],
            'mensagem': 'Reprovado a Conferir',
            'erro': r"Cliente não eleito a contratação devido a política "
                    r"de crédito."
        },{
            'texto': r'Cliente pré-aprovado para prosseguimento da proposta.',
            'tratamento': ['aceitar']
        },{
            'texto': r'Existem despesas que são opcionais ou podem ser alteradas na condição selecionada.',
            'tratamento': ['aceitar']
        },{
            'texto': r'Agência \d{2,6} esta inativa',
            'tratamento': ['pular']
        }, {
            'texto': r"Consulta com retorno negativo para os dados informados. "
                     r"Verificar dados para nova consulta.",
            'tratamento': ['atualizar'],
            'mensagem': 'Reprovado a Conferir'
        }, {
            'texto': "Não foi possível realizar a consulta no momento. "
                     "A mesma será realizada após o cadastro da proposta.",
            'tratamento': ['pular']
        }, {
            'texto': r"Valor Solicitado não pode ser menor que o valor mínimo cadastrado na Regra.",
            'tratamento': ['atualizar'],
            'mensagem': 'Reprovado a Conferir',
            'erro': r"Valor liberado inferior ao mínimo permitido."
        }, {
            'texto': 'Cliente pré-aprovado com restrição no tipo de operação.',
            'erro': 'Não existe produto para as condições informadas',
            'mensagem': "Reprovado a Conferir",
            'tratamento': ['atualizar']
        }, {
            'texto': "Dados divergentes entre Digitação e Consulta DataPrev",
            'erro': "Erro encontrado: dados digitados diferentes dos consultados",
            'textoMensagem': 'Favor confirmar dados bancários vinculados ao seu benefício do INSS',
            'mensagem': "Aguardando Autorização",
            'pedidoDocumentacao': 6,
            'tratamento': ['atualizar'],
        }, {
            'texto': ("NPR - Recusa Definitiva  - Fora Do Roteiro (Benef 32) - Perfil Impedido De "
                      "Operar"),
            'erro': r"Cliente não eleito a contratação devido a política "
                    r"de crédito.",
            'mensagem': "Reprovado a Conferir",
            'tratamento': ['atualizar']
        }, {
            'texto': r'A Proposta \d{9} foi Reprovada. Verificar no campo de Observação o motivo',
            'mensagem': "Reprovado a Conferir",
            'tratamento': ['atualizar']
        },  {
            'texto': r'Banco ou Agência inválido.',
            'erro': "Erro encontrado: Problema na identificação da agência ou banco",
            'mensagem': 'Conferir dados do contrato',
            'tratamento': ['atualizar']
        }, {
            'texto': r'Valor da Operação não pode ser menor que o valor mínimo cadastrado. Valor mínimo',
            'erro': r'Valor financiado não pode ser menor que o valor mínimo cadastrada no produto. valor mínimo: \d{3}',
            'mensagem': 'Reprovado a Conferir',
            'tratamento': ['atualizar']
        }, {
            'texto': "Não foram localizados dados para o CPF informado.",
            'erro': r"Não foram localizados dados para o CPF informado.",
            'mensagem': 'Reprovado a Conferir',
            'tratamento': ['atualizar']
        }, {
            'texto': 'agencia nao encontrada',
            'erro': r'O atributo obrigatório Agência não foi informado',
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Sistema Pan não encontra agência para OP',
            'tratamento': ['atualizar']
        }, {  # TODO: TESTAR ANTES
            'texto': 'matricula nao encontrada',
            'erro': r"NÃO ENCONTRADO MATRÍCULA PARA O CPF INFORMADO",
            'mensagem': 'Conferir dados do contrato',
            'observacao': 'Matrícula não encontrada'
        }, {
            'texto': 'DDD  inválido para a UF informada no endereço do Cliente',
            'erro': r"O telefone precisa estar no formato",
            'mensagem': "Conferir dados do contrato",
            'observacao': "Problema na inserção do telefone celular"
        }, {
            'texto': 'Código da critica de validação da proposta não encontrado. Código: 99',
            'erro': "Erro encontrado: Código da critica de validação da proposta não encontrado. Código: 99",
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar'],
        }, {
            'texto': 'complemento vazio',
            'erro': 'Erro encontrado: dado "complemento" vazio',
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar'],
        }, {
            'texto': r'Dados da Averbação: A conta corrente informada \d{9} é inválida.',
            'erro': "Erro encontrado: A conta corrente informada é inválida.",
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar'],
        }, {
            'texto': 'JÁ POSSUI O NÚMERO MÁXIMO DE OPERAÇÕES EM ABERTO ',
            'erro': "Erro encontrado: CLIENTE COM O CPF/CGC E MATRICULA JÁ POSSUI O NÚMERO MÁXIMO DE OPERAÇÕES EM ABERTO PARA O(A) EMPREGADOr",
            'mensagem': 'Reprovado a Conferir',
            'tratamento': ['atualizar']
        }, {
            'texto': "Tipo do Benefício do cliente não foi encontrado na tabela",
            'erro': "Erro encontrado: Tipo do Benefício do cliente não foi encontrado na tabela",
            'mensagem': 'Conferir dados do contrato',
            'tratamento': ['atualizar']
        }, {
            'texto': r'Cep \d+ não Encontrado',
            'erro': 'Erro encontrado: Não foi possível encontrar CEP do cliente',
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar']
        }, {
            'texto': r"DDD  inválido.",
            'erro': "Erro encontrado: DDD  inválido.",
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar']
        }, {
            'texto': 'Cannot locate option with value',
            'erro:': 'Erro encontrado: ordem de pagamento indiponível para o cliente',
            'mensagem': "Conferir dados do contrato",
            'tratamento': ['atualizar']
        }, {
            'texto': 'Message: Cannot locate option with value: MargemLivre',
            'erro': 'Erro encontrado: Message: Cannot locate option with value: MargemLivre',
            'mensagem': "Conferir dados do contrato",
        }, {
            'texto': 'Não existem prazos disponíveis nas condições informadas.',
            'erro': "Não existem prazos disponíveis nas condições informadas",
            'mensagem': 'Reprovado a Conferir',
            'tratamento': ['atualizar']
        },{
            'texto': r'NPR - RECUSA DEFINITIVA - FORA DO ROTEIRO',
            'tratamento': ['atualizar'],
            'mensagem': 'Reprovado a Conferir',
            'erro': r"Cliente não eleito a contratação devido a política "
                    r"de crédito."
        },{
            'texto': r"Sua sessão foi encerrada por outra estação",
            'tratamento': ['aguardar_novo_login']
        },{
            'texto': r"DDD  inválido para a UF informada no endereço do Cliente",
            'erro': 'DDD inválido para UF do cliente',
            'mensagem': "Aguardando Autorização",
            'textoMensagem': "O telefone informado tem o DDD inválido para a região onde recebe o benefício",
            'tratamento': ['atualizar']
        },{
            'texto': r"CPF do agente informado na proposta não possui certificação para comercializar o produto",
            'tratamento': ['preencher_cpf_operador']
        }
    ]
