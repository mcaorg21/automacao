# ─── Painel de Automação ─────────────────────────────────────────────────────
# Executa Flask, ngrok e Initializr em janelas separadas

$ROOT = "C:\www\automacao"

# 1. Flask
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ROOT\automacao_app'; `$env:FLASK_APP='__init__.py'; flask run"
)

# Aguarda Flask subir antes de iniciar o ngrok
Start-Sleep -Seconds 3

# 2. ngrok
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "ngrok http 5000"
)

# 3. Initializr
Start-Process "$ROOT\initializr\Automacao.bat"
