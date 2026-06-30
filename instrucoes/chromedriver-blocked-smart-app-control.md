# ChromeDriver bloqueado pelo Smart App Control (WinError 4551)

## Sintoma

```
⚠ ChromeDriver não encontrado no PATH: [WinError 4551] Uma política de Controle de Aplicativo bloqueou este arquivo
```
ou
```
'chromedriver.exe' foi bloqueado pela política do Device Guard da sua organização.
```

## Causa

O Chrome atualizou para uma versão nova e o ChromeDriver ficou desatualizado **ou** o ChromeDriver foi baixado e o **Smart App Control** do Windows 11 bloqueou a execução do executável.

O Smart App Control bloqueia qualquer `.exe` baixado da internet sem reputação reconhecida pela Microsoft — inclusive o `chromedriver.exe` e o `selenium-manager.exe`.

## Solução

### Passo 1 — Verificar versão do Chrome instalado

```powershell
reg query "HKLM\SOFTWARE\Google\Chrome\BLBeacon" /v version
```
ou via PowerShell:
```powershell
(Get-Item 'C:\Program Files\Google\Chrome\Application\chrome.exe').VersionInfo.FileVersion
```

### Passo 2 — Baixar ChromeDriver compatível

Substituir `147.0.7727.56` pela versão encontrada no passo anterior:

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/chrome-for-testing-public/147.0.7727.56/win64/chromedriver-win64.zip" -OutFile "C:\www\automacao\drivers\chromedriver.zip"
Expand-Archive -Path "C:\www\automacao\drivers\chromedriver.zip" -DestinationPath "C:\www\automacao\drivers\" -Force
Move-Item "C:\www\automacao\drivers\chromedriver-win64\chromedriver.exe" "C:\www\automacao\drivers\chromedriver.exe" -Force
Unblock-File -Path "C:\www\automacao\drivers\chromedriver.exe"
```

### Passo 3 — Desativar Smart App Control (se ainda bloqueado)

Testar se o chromedriver roda:
```cmd
C:\www\automacao\drivers\chromedriver.exe --version
```

Se ainda aparecer erro de Device Guard/política:

1. Abrir **Windows Security** (Segurança do Windows)
2. Ir em **App & browser control**
3. Clicar em **Smart App Control settings**
4. Mudar para **Off**

> ⚠ Operação permanente — só volta a ativar reinstalando o Windows. Normal em máquinas de desenvolvimento.

Após desativar, testar novamente:
```cmd
C:\www\automacao\drivers\chromedriver.exe --version
```

### Passo 4 — Confirmar que o Selenium funciona

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import PATHS

options = webdriver.ChromeOptions()
service = Service(PATHS.driver_path())
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://www.google.com')
print(driver.title)
driver.quit()
```

## Links úteis

- Todas as versões do ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/
- Download direto por versão: `https://storage.googleapis.com/chrome-for-testing-public/{VERSAO}/win64/chromedriver-win64.zip`
