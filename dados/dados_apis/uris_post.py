from dados.dados_apis import UCONECTE, WEBADMIN

POST = {
        # ia vertex
        "ia-vertex-arquivo": UCONECTE + '/v1/consultas/response_ia_file_vertex/',

        # ia vertex
        "ia-vertex-texto": UCONECTE + '/v1/consultas/simple_response_ia_vertex/',
        
        # post dos dados insercao itau
        "enviar-dados-itau-sincronizacao": WEBADMIN + '/v1/atualiza-status/banco-itau-consignado/contratos/',
        
        #post que envia mensagem push
        "enviar-mensagem-push":WEBADMIN + '/v1/mensagem/push/enviar/',

        #post que envia mensagem sms
        "enviar-mensagem-sms":WEBADMIN + '/v1/mensagem/sms/enviar/',

        #post que envia mensagem whatsapp
        "enviar-mensagem-whatsapp":WEBADMIN + '/v1/mensagem/whatsapp/enviar/',

        "pan-78-primeiro-post": WEBADMIN + '/v1/atualiza-status/banco-pan/contratos/',

        "enviar-dados-previsul": UCONECTE + '/v1/contratos/gerar?consulta=gerar',

        "enviar-dados-liberar-safra":WEBADMIN + '/v1/atualiza-status/banco-safra/liberacao-proposta/?key=f689f1e12a0399fba803cb2365fc362f',
        
        "sincronizar-previsul": WEBADMIN + '/v1/atualiza-status/seguradora-previsul/contratos/?key=f689f1e12a0399fba803cb2365fc362f',

        "enviar-dados-safra": WEBADMIN + '/v1/atualiza-status/banco-safra/contratos/fgts-consignado/?key=f689f1e12a0399fba803cb2365fc362f',

        # post dos dados insercao safra
        "enviar-dados-safra-insercao": UCONECTE + '/v1/contratos/gerar?consulta=gerar',

        # enviar dados da sincronizacao do site daycoval
        "enviar-dados-sincronizacao-daycoval": WEBADMIN + "/v1/atualiza-status/banco-daycoval/contratos/imobiliario/",

        #enviar dados da inserção e preencimento pdf daycoval
        "enviar-pdf-ade-daycoval": UCONECTE + "/v1/contratos/gerar",

        # enviar dados recebimento ole
        "enviar-dados-recebimento-ole": WEBADMIN + "/v1/atualiza-status/banco-ole/contratos/",

        # enviar margem disponivel IbConsig
        "enviar-margem-disponivel-ibconsig": WEBADMIN + "/v1/atualiza-dados/atualiza-margem/portal-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f",

        # enviar dados da propostas imobiliarias
        "enviar-proposa-imobiliaria-daycoval":  UCONECTE + "/calcular/emprestimo_imobiliario",

        # enviar infos das propostas do iccdigital
        "enviar-dados-propostas-iccdigital": WEBADMIN + '/v1/atualiza-status/banco-itau-consignado/status-assinatura-digital/',
        
        # enviar infos do arquivo pego no site Daycoval
        "enviar-dados-arquivo-daycoval": WEBADMIN + '/v1/atualiza-status/banco-daycoval/contratos/',

        # enviar infos sobre o cpf consultado no site da receita federal
        "enviar-infos-cpf-federal": WEBADMIN + '/v1/atualiza-dados/atualiza-situacao-cpf-receita/',
        
        # enviar infos sobre o cpf consultado no site do tse
        "enviar-info-cpfs-tse": WEBADMIN + '/v1/atualiza-dados/atualiza-justica-federal/',
        
        # atualiza o contrato com status portabilidade
        "retencao-portabilidade": WEBADMIN + '/v1/atualiza-status/banco-itau-consignado'
                                             '/retencao-portabilidade',

        # envia os dados do contrato gerado em base64
        "gerar-contrato": UCONECTE + "/v1/contratos/gerar",

        # atualiza o status resultante da liberação da proposta
        "atualiza-status-liberacao": WEBADMIN + "/v1/atualiza-status/banco-{nome-banco}"
                                                "/liberacao-proposta",

        # atualiza infos específicadas de um contrato especificado
        "atualiza-status-contrato": WEBADMIN + "/v1/atualiza-status/banco-{nome-banco}/contratos/",

        # envia os dados de refinanciamentos em potencial consultados
        "crm": UCONECTE + "/v1/ofertas/crm",

        # insere uma mensagem no histórico da solicitação
        "historico-refin": UCONECTE + '/v1/solicitacoes/{idSolicitacao}/historico',

        # boqueia o perfil de uma pessoa
        "bloqueio": UCONECTE + "/v1/pessoas/{id-pessoa}/bloqueio",

        # **dados-consultados **solicitacao
        "calcular-emprestimo": UCONECTE + "/calcular/emprestimo_novo",

        # utiliza os dados consultados pra calcular o refin
        "calcular-refin": UCONECTE + "/calcular/refinanciamento",

        # **dados-consultados **solicitacao
        "finalizar-solicitacao": UCONECTE + "/calcular/finalizar_solicitacao",

        # ocorr=[google-analytics]
        "tabela-google-analytics": WEBADMIN + "/v1/atualiza-tabela-google-analytics/",

        # envia os dados cosnultados do perfil no MeuINSS e no Promobank
        "consulta-inss": UCONECTE + "/v1/consultas/inss",

        # atualiza o status da situação de um contrato (ocorr=consultaMeuINSS - falha)
        "atualiza-situacao-contrato": UCONECTE + "/consultas/atualizaSituacaoContrato",

        # atualiza status de reevio de sms
        "reenvio-sms": WEBADMIN + "/v1/atualiza-status/banco-{nome-banco}/sms-envio/",

        # envia a margem consultada no perfil em reprovado a conferir
        "reprovado-conferir": WEBADMIN + "/v1/contratos/reprovado-conferir/atualiza-margem/",

        # utiliza os dados consultados pra calcular o cartao consignado
        "calcular-cartao": UCONECTE + "calcular/cartao_consignado"
}