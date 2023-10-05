@echo off

cd %~dp0

echo Fechando Robos com erro. . .
start %cd%\start\close_error_robots.bat
timeout 30

echo Iniciando robos fechados. . .
set path_main=%cd%\start\main.bat

tasklist /v | find "Consulta User Explorer Analytics"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% googleAnalyticsConsultaUserExplorer
)
timeout 30
tasklist /v | find "Consulta INSS"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% promoBank
)
timeout 30
::tasklist /v | find "Consulta Margem Marinha"
::IF "%ERRORLEVEL%" NEQ "0" (
::    start %path_main% consultaMargemMarinha
::)

tasklist /v | find "Consulta Margem SP"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% portal_consig
)
timeout 30

tasklist /v | find "Pan Todas Tarefas"
set robo_pan_todas_tarefas=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% robo_pan_todas_tarefas
)
timeout 30

tasklist /v | find "PanConsultaRefin064"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% robo_pan_consulta_refinanciamento064
)
timeout 30

tasklist /v | find "PanConsultaRefin035"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% robo_pan_consulta_refinanciamento035
)
timeout 30

tasklist /v | find "Refinanciamento Bradesco"
IF "%ERRORLEVEL%" NEQ "0" (
   start %path_main% bradescoRefinanciamento
)
timeout 30

tasklist /v | find "Inserir IbConsig"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ibConsig
)
timeout 30

tasklist /v | find "Liberacao BMG"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% liberacao_bmg
)
timeout 30

tasklist /v | find "Consulta Margem INSS"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% margem_inss
)

tasklist /v | find "Download contrato IbConsig"
set refinIbConsig=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% gerarIbConsig
    timeout 180
)

tasklist /v | find "Refinanciamento IbConsig"
set gerarIbConsig=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ibConsigRefinanciamento
)
timeout 30

tasklist /v | find "Refinanciamento IbConsig N2"
set gerarIbConsig=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ibConsigRefinanciamentoN2
)
timeout 30

tasklist /v | find "Ib Analise de Fraude"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ib_analise_de_fraude
)
timeout 30

tasklist /v | find "Atualiza Status Proposta IbConsig"
set ibConsigConsultaStatus=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ibConsigConsultaStatus
)
timeout 30

tasklist /v | find "Ole Refin Sincronizacao Anexo Liberacao SMS"
set robo_refin_anex_lib_sms=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% robo_refin_anex_lib_sms
    timeout 300
)

tasklist /v | find "Ole Insercao Gerar"
set robo_sinc_insercao=%ERRORLEVEL%
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% robo_sinc_insercao
)
timeout 30

tasklist /v | find "Itau Insercao Listener"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% itau_insercao_auto_init
)


timeout 5