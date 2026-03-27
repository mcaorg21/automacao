# Integração com API

## Configuração

A integração com a API foi implementada no arquivo `main.py` com as seguintes configurações:

- **URL Base**: `https://app.leviatan.com.br/dcncadv/cpj/agnes`
- **Login**: `api`
- **Senha**: `2025`
- **Autenticação**: Bearer Token (JWT)

## Resposta do Login

O endpoint de login retorna um objeto JSON com os seguintes campos:

```json
{
    "2FA_status": "Login OK",
    "2FA_status_codigo": 1,
    "idUsuario": 19108,
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJhcHAiOiJDUEotM0MiLCJyZyI6IiIsImlkIjoiMTkxMDgiLCJ1c2VySWQiOjE5MTA4LCJ1c2VyVHlwZSI6MywiaWF0IjoxNzcwNzU4NzYzLCJleHAiOjE3NzA3NjA1NjN9.crDbjHJnq_zfntxS_VzPtjtdAxCIvOOC0z8UqsFB5ns"
}
```

O **token** é usado em todas as requisições subsequentes como **Bearer Token** no header `Authorization`.

## Funções Implementadas

### 1. `api_login()`
Realiza a autenticação na API e retorna o token Bearer.

```python
token = api_login()
if token:
    print("Login realizado com sucesso!")
    print(f"Token: {token}")
```

**Retorno:**
- `str`: Token Bearer (JWT) para autenticação
- `None`: Se o login falhar

**O que a função faz:**
1. Envia credenciais para `/login`
2. Extrai o token da resposta JSON
3. Armazena o token globalmente (`API_TOKEN`)
4. Configura o header `Authorization: Bearer <token>` automaticamente

### 2. `api_get(endpoint, params)`
Faz requisições GET autenticadas na API usando Bearer token.

```python
# Exemplo: buscar processos
processos = api_get('/processos', params={'data': '2025-01-01'})
```

**Headers automáticos:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

**Recursos:**
- Autenticação automática com Bearer token
- Reautenticação automática se o token expirar (erro 401)
- Timeout de 30 segundos

### 3. `api_post(endpoint, data)`
Faz requisições POST autenticadas na API usando Bearer token.

```python
# Exemplo: criar um novo registro
resultado = api_post('/processos', data={
    'numero': '12345',
    'tipo': 'reembolso'
})
```

**Headers automáticos:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Recursos:**
- Autenticação automática com Bearer token
- Reautenticação automática se o token expirar (erro 401)
- Timeout de 30 segundos

## Como Usar

### No fluxo principal (main.py)

A integração está ativada automaticamente na variável `etapa_integracao = True`. O login é realizado no início do processo e o token Bearer é extraído:

```python
if etapa_integracao:
    token = api_login()
    if not token:
        print('Falha ao autenticar. Abortando...')
        return
    
    # O token agora está disponível globalmente
    # Todas as requisições usarão automaticamente:
    # Authorization: Bearer <token>
```

### Testando a integração

Execute o script de teste para verificar a conexão e autenticação:

```bash
python test_api.py
```

O script de teste irá:
1. Testar a conexão básica com a API
2. Realizar login e extrair o token Bearer
3. Exibir o token completo e informações do usuário
4. Mostrar como usar o token em requisições curl

### Exemplo de uso do token em curl

Após obter o token, você pode testá-lo diretamente:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
     https://app.leviatan.com.br/dcncadv/cpj/agnes/algum-endpoint
```

## Próximos Passos

### 1. Enviar dados do processo
Após processar o CSV e gerar os arquivos, enviar informações para a API:

```python
# Exemplo de envio após processamento
def enviar_dados_api(data):
    """Envia os dados processados para a API"""
    payload = {
        'numero_recibo': NUMERO_RECIBO,
        'valor_total': data['valor_somado'],
        'data_inicial': DATA_INICIAL_PESQUISA,
        'data_final': DATA_FINAL_PESQUISA,
        'registros': data['registros']
    }
    
    resultado = api_post('/processos/criar', payload)
    return resultado
```

### 2. Upload de arquivos
Implementar upload dos PDFs gerados:

```python
def api_upload_file(endpoint, file_path):
    """Faz upload de um arquivo para a API"""
    global API_SESSION
    
    if not API_SESSION:
        api_login()
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        url = f'{API_BASE_URL}{endpoint}'
        response = API_SESSION.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()
        return None
```

### 3. Consultar status
Verificar o status de processos enviados:

```python
# Buscar processo pelo número
processo = api_get(f'/processos/{NUMERO_RECIBO}')
if processo:
    print(f"Status: {processo['status']}")
```

## Troubleshooting

### Erro de conexão
- Verificar se a URL está acessível
- Verificar firewall/proxy
- Testar com `curl` ou Postman

### Erro 401 (Não autorizado)
- **Token expirado**: As funções tentam reautenticar automaticamente
- **Token inválido**: Verificar se o login retornou o token corretamente
- **Header incorreto**: Verificar se está usando `Authorization: Bearer <token>`

Para debug, você pode verificar o token:

```python
# Verificar se o token está definido
from main import API_TOKEN
print(f"Token atual: {API_TOKEN}")

# Verificar headers da sessão
from main import API_SESSION
print(f"Headers: {API_SESSION.headers}")
```

### Erro 404 (Não encontrado)
- Verificar se o endpoint existe na API
- Consultar documentação da API
- Testar endpoints alternativos

## Notas Técnicas

- A biblioteca `requests` é usada para comunicação HTTP
- A autenticação usa **Bearer Token (JWT)** no header `Authorization`
- O token é armazenado globalmente (`API_TOKEN`) e reutilizado em todas as requisições
- A sessão mantém o header `Authorization` configurado automaticamente
- **Reautenticação automática**: Se uma requisição retornar 401, o sistema tenta fazer login novamente
- Timeout padrão: 30 segundos
- As requisições incluem tratamento de erros e logs detalhados

### Estrutura do Token

O token é um JWT (JSON Web Token) com a seguinte estrutura:

```json
{
  "app": "CPJ-3C",
  "rg": "",
  "id": "19108",
  "userId": 19108,
  "userType": 3,
  "iat": 1770758763,  // Timestamp de emissão
  "exp": 1770760563   // Timestamp de expiração (30 minutos)
}
```

**Importante**: O token expira após 30 minutos. As funções `api_get` e `api_post` detectam automaticamente a expiração e renovam o token.
