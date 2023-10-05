@echo off

cd %~dp0

echo Fechando Robos com erro. . .
start %cd%\start\close_error_robots.bat
timeout 5

echo Iniciando robos fechados. . .
set path_main=%cd%\start\main.bat


tasklist /v | find "Fila INSS Reprovado Conferir por Margem"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% filaInssReprovadoConferir
)

tasklist /v | find "Atualiza Status Proposta Ole Portal Orienta"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% oleConsignadoPortalOrienta
)

tasklist /v | find "Atualiza Status Proposta IbConsig"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% ibConsigConsultaStatus
)


timeout 10