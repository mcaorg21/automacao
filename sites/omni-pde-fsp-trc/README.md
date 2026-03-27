# OMNI-PDE-FSP-TRC Automation

Automação para o sistema OMNI-PDE-FSP-TRC com integração à API CPJ Agnes.

## 📋 Estrutura

```
omni-pde-fsp-trc/
├── __init__.py      # Módulo Python
├── main.py          # Script principal (estrutura funcional)
├── config.json      # Configurações (URL, credenciais)
└── README.md        # Documentação
```

## ✨ Funcionalidades

- ✅ Estrutura modular sem classes (baseada em cpj-reembolso-bmg)
- ✅ Integração com API CPJ Agnes
- ✅ Login automatizado no sistema web
- ✅ Busca de tarefas de processo por evento e data
- ✅ Configurações via `config.json`
- ⏳ Automação web completa (em desenvolvimento)

## 🚀 Como usar

### 1. Configurar credenciais

Edite o arquivo `config.json` com as informações corretas:

```json
{
  "web_url": "https://sistema-real.com.br/login",
  "web_login": "seu_usuario",
  "web_password": "sua_senha"
}
```

### 2. Ajustar seletores CSS

Abra o arquivo `main.py` e ajuste os seletores na função `login_web_sistema()` conforme os elementos reais do sistema:

```python
# Ajuste os seletores CSS conforme o HTML do sistema
login_input = wait.until(EC.presence_of_element_located((By.ID, 'campo_login')))
senha_input = driver.find_element(By.ID, 'campo_senha')
btn_login = driver.find_element(By.ID, 'btn_entrar')
```

### 3. Executar

```bash
cd C:\www\automacao
python -m sites.omni-pde-fsp-trc.main
```

Ou diretamente:

```bash
python C:\www\automacao\sites\omni-pde-fsp-trc\main.py
```

## 📝 Estrutura do Código

### Configurações Globais

```python
# Configurações da API CPJ
API_BASE_URL = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
API_LOGIN = 'api'
API_PASSWORD = '2025'

# Configurações do sistema web (carregadas do config.json)
WEB_URL = 'https://sistema.exemplo.com.br/login'
WEB_LOGIN = 'usuario'
WEB_PASSWORD = 'senha'
```

### Funções Principais

1. **`open_chrome_browser()`** - Abre o navegador Chrome com configurações otimizadas
2. **`login_web_sistema(driver)`** - Realiza login no sistema web
3. **`main()`** - Função principal que orquestra toda a automação

### Fluxo de Execução

```
main()
  ├─> ETAPA 1: Autenticação na API CPJ
  ├─> ETAPA 2: Buscar tarefas/processos (opcional)
  └─> ETAPA 3: Automação Web
       ├─> open_chrome_browser()
       ├─> login_web_sistema()
       └─> TODO: Próximas automações
```

## 🔧 Próximos Passos

1. ✅ Login implementado
2. ⏳ Navegar para páginas específicas após login
3. ⏳ Preencher formulários
4. ⏳ Extrair dados
5. ⏳ Processar tarefas da API

## 🐛 Troubleshooting

### ChromeDriver não encontrado

Se o ChromeDriver não for encontrado automaticamente, siga as instruções exibidas no console:

1. Verifique a versão do Chrome em `chrome://settings/help`
2. Baixe o ChromeDriver correspondente
3. Adicione ao PATH ou coloque em `C:\chromedriver\`

### Erro de login

1. Verifique se a URL está correta no `config.json`
2. Inspecione o HTML da página de login
3. Ajuste os seletores CSS na função `login_web_sistema()`

## 📚 API CPJ - Endpoint /api/v2/processo/tarefa

A automação utiliza o endpoint `/api/v2/processo/tarefa` para buscar tarefas de processo.

### Exemplo de uso

```python
from cpj_api import api_buscar_processo_tarefa

tarefas = api_buscar_processo_tarefa(
    evento='OMNI_PDE_FSP_TRC',
    data_inicial='2026-03-25',
    limit=10
)
```

## 📄 Licença

Projeto interno - DCN Advogados

# Buscar tarefas por evento e data
tarefas = api_buscar_processo_tarefa(
    evento="EVENTO_EXEMPLO",
    data_inicial="2026-03-01",
    limit=10
)
```

### Estrutura do POST

```json
{
  "filter": {
    "_and": [
      {
        "evento": {
          "_eq": "{{EVENTO}}"
        }
      },
      {
        "update_data_hora": {
          "_gte": "{{YYYY-MM-DD}}"
        }
      }
    ]
  },
  "limit": 1
}
```

## Configuração

As credenciais da API estão configuradas no arquivo `main.py`:

```python
self.api_base_url = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
self.api_login = 'api'
self.api_password = '2025'
```

## Próximos passos

1. ✅ Integração com API CPJ
2. ⏳ Definir URL do sistema web
3. ⏳ Implementar seletores de login
4. ⏳ Implementar lógica de processamento de tarefas
5. ⏳ Adicionar tratamento de erros específicos
6. ⏳ Adicionar logs detalhados
7. ⏳ Testar em diferentes cenários

## Dependências

- selenium
- requests
- PyPDF2 (via cpj_api)

## Autor

Marcelo Amancio - 2026
