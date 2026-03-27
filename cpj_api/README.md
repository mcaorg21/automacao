# CPJ API - Módulo de Integração

Módulo reutilizável para integração com a API do CPJ Agnes.

## Instalação

O módulo está localizado em `C:\www\automacao\cpj_api` e pode ser importado por qualquer projeto Python.

## Uso Básico

```python
import sys
sys.path.append('C:\\www\\automacao')

from cpj_api import (
    set_api_credentials,
    api_login,
    api_logout,
    api_buscar_lancamentos,
    processar_lancamentos,
    processar_documentos_registros
)

# 1. Configurar credenciais
set_api_credentials(
    base_url='https://app.leviatan.com.br/dcncadv/cpj/agnes',
    login='api',
    password='2025',
    json_path='caminho/para/importados.json',
    planilha_path='caminho/para/planilha'
)

# 2. Fazer login
token = api_login()

# 3. Buscar lançamentos
from datetime import datetime
lancamentos = api_buscar_lancamentos(
    data_inicial=datetime(2026, 2, 1),
    data_final=datetime(2026, 2, 13),
    numero_cc=1397
)

# 4. Processar lançamentos
dados = processar_lancamentos(
    lancamentos,
    filtro_integracao='CIV'  # Filtra apenas integrações contendo 'CIV'
)

# 5. Processar documentos
processar_documentos_registros()

# 6. Fazer logout
api_logout()
```

## Funções Disponíveis

### Autenticação
- `set_api_credentials(base_url, login, password, json_path, planilha_path)` - Configura credenciais
- `api_login()` - Realiza login e retorna token
- `api_logout()` - Realiza logout
- `get_api_session()` - Retorna sessão atual
- `get_api_token()` - Retorna token atual

### Requisições HTTP
- `api_get(endpoint, params)` - Requisição GET autenticada
- `api_post(endpoint, data)` - Requisição POST autenticada

### Busca de Dados
- `api_buscar_lancamentos(data_inicial, data_final, numero_cc, limit)` - Busca lançamentos
- `api_buscar_spf(id_spf)` - Busca SPF por ID
- `api_buscar_processo(pj)` - Busca processo por PJ
- `api_buscar_documentos_spf(id_spf)` - Busca documentos de um SPF
- `api_buscar_processo_tarefa(evento, data_inicial, limit)` - Busca tarefas de processo por evento e data

### Processamento
- `processar_lancamentos(lancamentos, filtro_integracao, json_path, planilha_path)` - Processa lançamentos
- `processar_documentos_registros(json_path, output_folder)` - Baixa e mescla documentos PDF

### Utilitários
- `sanitizar_documento(documento)` - Extrai números de documento
- `formatar_data_lancamento(data_str)` - Formata data de YYYY-MM-DD para DD/MM/YYYY
- `api_baixar_documento(id_ged, destino_path)` - Baixa um documento específico

## Dependências

```
requests
PyPDF2
```

## Estrutura de Retorno

### processar_lancamentos()
```python
{
    'contagem': int,
    'valor_somado': str,  # Formato: "1234,56"
    'registros': [
        {
            'historico': str,
            'data_lancamento': str,  # DD/MM/YYYY
            'valor_em_r': str,
            'debito_na_moeda': str,
            'credito_na_moeda': str,
            'saldo': str,
            'pro_numero_de_integracao': str,
            'pro_numero_do_processo': str,
            'id_spf': str,
            'ccc_pes_nome': str,
            'tco_descricao': str
        }
    ]
}
```

## Exemplo Completo

Ver [cpj-reembolso-bmg/main.py](../sites/cpj-reembolso-bmg/main.py) para um exemplo completo de uso.

## Autor

Sistema de Automação CPJ - 2026
