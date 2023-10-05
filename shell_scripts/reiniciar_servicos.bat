@echo off
setlocal enableDelayedExpansion

title FECHANDO

TASKKILL /IM chrome.exe /F

timeout 3

for /f "tokens=1 delims=" %%a in ('
    tasklist /V /FI "Imagename eq cmd.exe"
') do (
    set inicio=%%a
    set replace=!inicio:FECHANDO=ENCONTRADO!

    if !inicio! EQU !replace! (
        for /F "tokens=2" %%b in ("%%a") do (
            taskkill /PID %%b
        )
    )
)

echo Fechando essa janela...
timeout 2