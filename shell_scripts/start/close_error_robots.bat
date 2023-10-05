@echo off
setlocal enableDelayedExpansion

echo Fechando robos com problema!

for /f "tokens=1 delims=" %%a in ('
    tasklist /V /FI "Imagename eq cmd.exe"
') do (
    set inicio=%%a
    set replace=!inicio:ERRORROBO=ENCONTRADO!

    if !inicio! NEQ !replace! (
        for /F "tokens=2" %%b in ("%%a") do (
            taskkill /PID %%b
        )
    )
)

echo Fechando essa janela...
timeout 2
exit