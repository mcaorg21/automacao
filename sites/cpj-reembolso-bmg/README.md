# CPJ Automation - Python

Automação do aplicativo CPJ usando PyWinauto para interação nativa com controles Windows.

## Vantagens sobre a versão TypeScript

- **Interação nativa**: Acessa controles Windows diretamente (sem reconhecimento de imagem)
- **Mais robusto**: Não depende de posições fixas ou resolução da tela
- **Mais rápido**: Execução mais eficiente sem busca por imagens
- **Melhor para apps legados**: PyWinauto é especializado em automação Windows

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Estrutura

```
cpj-reembolso-bmg/
├── main.py              # Script principal
├── requirements.txt     # Dependências Python
├── README.md           # Este arquivo
└── planilha/           # Pasta para arquivos CSV/JSON (criada automaticamente)
```

## Fluxo da automação

1. **Login**: Abre o CPJ e faz login automático
2. **Navegação**: Acessa menus e relatórios
3. **Exportação**: Gera arquivo CSV com dados
4. **Processamento**: Converte CSV para JSON estruturado
5. **Geração de PDFs**: Processa registros individuais

## Configuração

Edite as constantes no início do arquivo `main.py`:

```python
CPJ_PATH = r'C:\CPJ3C_Client\cpj3cclient.exe'
LOGIN = 'MOAO'
PASSWORD = 'LM0G'
PLANILHA_PATH = r'C:\www\automacao\sites\cpj-reembolso-bmg\planilha'
```

## Próximos passos

1. Descobrir os identificadores corretos dos controles Windows (use `inspect.exe` do Windows SDK)
2. Substituir `send_keys()` e `click()` por acesso direto aos controles quando possível
3. Adicionar tratamento de erros mais robusto
4. Implementar logs detalhados

## Ferramentas úteis

- **inspect.exe**: Ferramenta do Windows SDK para inspecionar controles de UI
- **spy++**: Ferramenta alternativa para inspecionar janelas

## Notas

- O código ainda usa coordenadas de tela em alguns lugares (como na versão TypeScript)
- Para melhorar, identifique os controles Windows e use `app.window().child_window()` ao invés de clicks em coordenadas
