# OMNI-CONCILIACAO-CONTA-CORRENTE Automation

Automação para conciliação de conta corrente no sistema OMNI com integração à API CPJ Agnes.

## Descrição

Este robô realiza a conciliação de conta corrente no portal Omnifácil, buscando tarefas
via API CPJ e processando cada uma delas no sistema web.

## Estrutura

| Arquivo | Descrição |
|---|---|
| `main.py` | Script principal da automação |
| `config.json` | Configurações (URL, credenciais, datas, próxima execução) |
| `cookies.json` | Cookies de sessão do navegador |
| `tarefas.json` | JSON com as tarefas buscadas na API CPJ |
| `erros_conciliacao.json` | Registro de erros encontrados durante a conciliação |

## Configuração

Edite o `config.json` com as credenciais e parâmetros necessários:

```json
{
  "web_url": "https://www.omnifacil.com.br/...",
  "web_login": "SEU_LOGIN",
  "web_password": "SUA_SENHA",
  "2fa_secret": "SEU_SECRET_2FA",
  "data_inicial": "2026-05-01",
  "data_final": "2026-05-11",
  "proxima_execucao": ""
}
```
