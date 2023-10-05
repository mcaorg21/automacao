from dados.dados_apis import UCONECTE, WEBADMIN

GET = {
    # fila saques acreditar
    "fila-saques-acreditar": UCONECTE + '/v1/carteira/consultarTransacoesAbertas?key=f689f1e12a0399fba803cb2365fc362f&situacao=2',

    # fila pagamentos acreditar
    "fila-pagamentos-acreditar": UCONECTE + '/v1/carteira/consultarTransacoesAbertas?key=f689f1e12a0399fba803cb2365fc362f&situacao=1&idTransacao=755',

    # TarefasPan078
    "proposta-ade-pan-78": UCONECTE + '/v1/contratos/ade/informacoes?key=f689f1e12a0399fba803cb2365fc362f',
    "pan-propostas-78": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=pan-fgts',
    "pan-sincronizacao": WEBADMIN + '/v1/contratos/em-analise/banco-pan/?key=f689f1e12a0399fba803cb2365fc362f',

    # Previsul
    "previsul-sincronizacao": WEBADMIN + '/v1/contratos/em-analise/seguradora-previsul/?key=f689f1e12a0399fba803cb2365fc362f',
    "previsul-insercao-dados": UCONECTE + '/v1/contratos/ade/informacoes?key=f689f1e12a0399fba803cb2365fc362f',
    "previsul-insercao": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=previsul-seguradora&ordem=asc',

    # Safra
    "dados-insercao-safra-auxilio": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-auxilio&ordem=desc',
    "dados-insercao4-safra": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-fgts&ordem=desc',
    "dados-insercao-ajuda-a-inserir-safra": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-fgts&ordem=desc&limite=3',
    "dados-insercao3-safra": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-fgts&ordem=desc&statusContrato=Pendente&limite=2',
    "dados-insercao2-safra": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-fgts&ordem=asc&statusContrato=Pendente&limite=15',
    "dados-aprovar-safra": WEBADMIN + '/v1/contratos/a-liberar/banco-safra/?key=f689f1e12a0399fba803cb2365fc362f',
    "dados-insercao-safra": UCONECTE + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=safra-fgts&ordem=asc&limite=10',
    "dados-proposta-sincronizacao-safra": WEBADMIN + '/v1/contratos/em-analise/banco-safra/?key=f689f1e12a0399fba803cb2365fc362f',
    "dados-proposta-insercao-safra": UCONECTE + '/v1/contratos/codigo_con/informacoes?key=f689f1e12a0399fba803cb2365fc362f',

    # pegar todas as propostas para o robo daycoval propostas
    "todas-propostas-daycoval-proposta": UCONECTE  + '/v1/contratos/status/inserir?key=f689f1e12a0399fba803cb2365fc362f&consulta=insercao&banco=daycoval-imobiliario&ordem=asc',

    # pegar cpf para sincronização no Daycoval
    "pegar-dados-sincronizacao-daycoval": WEBADMIN + "/v1/contratos/em-analise/banco-daycoval/imobiliario/?key=f689f1e12a0399fba803cb2365fc362f",

    # propostas do ole que estão com o status envio/recebimento
    "proposta-recebimento-ole": WEBADMIN + "/v1/contratos/restricao/margem-sigla-conta/banco-ole/?key=f689f1e12a0399fba803cb2365fc362f",

    # propostas em pedente com restrição de margem
    "propostas_em_pedente_ibconsig": WEBADMIN + "/v1/contratos/restricao/margem/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f",

    # Daycoval
    "daycoval_anexar_documentos": WEBADMIN + '/v1/contratos/enviar-documentos-banco/banco-daycoval/?key=f689f1e12a0399fba803cb2365fc362f',
    # propostas imovel Daycoval real
    "daycoval_propostas_imoveis_real": UCONECTE + "/v1/contratos/codigo/informacoes?key=f689f1e12a0399fba803cb2365fc362f",
    
    # propostas simulacao imovel Daycoval
    "daycoval_proposta_imoveis_simulacao": UCONECTE  + "/v1/consultas/consultarEmprestimoImobiliario?key=f689f1e12a0399fba803cb2365fc362f",

    # propostas para o In100
    "propostas_In100": WEBADMIN + "/v1/contratos/enviar-documentos-banco/banco-itau-consignado/in100/?key=f689f1e12a0399fba803cb2365fc362f",
   
    # arquivo proposta In100 (colocar {} ente CPF e ADE)
    "arquivos_proposta_in100": UCONECTE  + '/v1/assinaturas/arquivosFluxoIn100/?key=f689f1e12a0399fba803cb2365fc362f&cpf={cpf}&ade={ade}',

    # pdf arquivo do contrato para atualizar contratos iccdigital
    "arquivo_pdf_ade_iccdigital": WEBADMIN + '/v1/contratos/gerar-pdf-portal/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f&ade={ade}&codigoCli={codigo_cli}',

    # pegar os arquivos para consulta no icDigital
    "arquivos_icdigital": WEBADMIN + '/v1/contratos/gerar-pdf-portal/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f',
    
    # consultar propostas no icconsig
    "propostas_icconsig_itau": WEBADMIN + '/v1/contratos/status-assinatura/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f&teste=0',
    
    # realizar a consulta da simulacao no cetelem
    "cetelem-simulacao": UCONECTE + "/v1/solicitacoes/refinanciamento?key=f689f1e12a0399fba803cb2365fc362f&banco=6",
    
    # realizar a consulta de cpf no site da receita federal
    "consulta-cpf-federal":WEBADMIN + "/v1/consulta/receita-federal/situacao-cpf/",

    # realizar a consulta de cpf no site do tse
    "consulta-cpf-tse": WEBADMIN + "/v1/consulta/justica_federal/",
    
    # fila de contratos a serem inseridos *ok
    "fila-insercao": UCONECTE + "/v1/contratos/status/inserir",

    # links com documentos associados a um contrato
    "documentos-contrato": UCONECTE + "/v1/contratos/documentos",

    # filas de propostas com liberação pendente
    "liberar-propostas": WEBADMIN + "/v1/contratos/a-liberar/banco-{nome-banco}",

    # contratos filas 'aguardando gerar contrato -> gerar contratos'
    "gerar-contrato": UCONECTE + '/v1/contratos/status/gerar',

    # fila de contratos que necessitam de análise documental para assinatura digital
    "docs-assinaturas-log": UCONECTE + "/v1/assinaturas/log",

    # fila de contratos que necessitam de análise documental para assinatura digital
    "docs-portabilidade": UCONECTE + "/v1/Assinaturas/arquivosPortabilidade",

    # fila de contratos que necessitam anexar contratos
    "enviar-docs": WEBADMIN + "/v1/contratos/enviar-documentos-banco/banco-{nome-banco}/",

    # fila de contratos que necessitam anexar contratos
    "enviar-docs-portabilidade": WEBADMIN + "/v1/contratos/enviar-documentos-banco/banco-{nome-banco}/portabilidade",

    # fila de contratos que necessitam de sincronização/consulta de dados no banco
    "consulta-status": WEBADMIN + "/v1/contratos/em-analise/banco-{nome-banco}",

    # fila de contratos que necessitam de sincronização/consulta de dados no banco
    "consulta-status-parceiro": WEBADMIN + "/v1/contratos/em-analise/{nome-banco}",

    # lista de solicitações para consulta por refinanciamentos
    "refinanciamento": UCONECTE + '/v1/solicitacoes/refinanciamento',

    # lista de solicitações para consulta por refinanciamentos em potencial
    "crm": UCONECTE + "/v1/consultas/crm/",

    # /nome-banco/{key} [ocorr=analytics-todos-bancos]
    "contratos-finalizados": "/v1/contratos/finalizados/{nome-banco}/",

    # lista de perfis com dados para serem consultados no MeuINSS
    "consulta-meu-inss": UCONECTE + "/v1/consultas/consultarMeuInss",

    # lista de perfis para consulta de margem portal marinha
    "consulta-marinha": UCONECTE + "/v1/Consultas/consultarMargemMarinha",

    # informações detalhadas de um contrato específico
    "informacoes-contrato": UCONECTE + "/v1/contratos/{codigo-contrato}/informacoes",

    # lista para reenvio de sms
    "reenvio-sms": WEBADMIN + "/v1/contratos/a-reenviar-sms/banco-{nome-banco}/",

    # lista de perfis para consulta da marge no Portal do Consignado
    "portal-consignado": UCONECTE + "/v1/Consultas/consultarMargemServidor",

    # lista de solicitações pra consulta no Promobank
    "solicitacoes-promobank": UCONECTE + "/v1/solicitacoes/{tipo-consulta}/",

    # lista de perfis reprovado a conferir
    "reprovado-conferir": WEBADMIN + "/v1/contratos/reprovado-conferir/consulta-margem",

    # atualiza o horário de sincronização do contrato
    "atualiza-sincronizacao": WEBADMIN + "/v1/atualiza-status/banco-{nome-banco}/sincronizacao/",
}
