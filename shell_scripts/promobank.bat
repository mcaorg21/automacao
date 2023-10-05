@echo off

cd %~dp0

echo Fechando Robos com erro. . .
start %cd%\start\close_error_robots.bat
timeout 5

echo Iniciando robos fechados. . .
set path_main=%cd%\start\main.bat

tasklist /v | find "Consulta INSS"
IF "%ERRORLEVEL%" NEQ "0" (
    start %path_main% promoBank
)