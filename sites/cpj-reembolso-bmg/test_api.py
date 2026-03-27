"""
Script de teste para integração com a API
Este script testa apenas a autenticação e chamadas básicas à API
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Adiciona o diretório pai ao path para importar do main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa as funções do main.py
from main import (
    api_login,
    api_buscar_lancamentos,
    processar_lancamentos,
    processar_documentos_registros
)

# Configurações da API
API_BASE_URL = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
API_LOGIN = 'api'
API_PASSWORD = '2025'

def test_login():
    """Testa o login na API e extrai o token Bearer"""
    print('\n=== TESTE DE LOGIN NA API ===')
    print(f'URL Base: {API_BASE_URL}')
    print(f'Login: {API_LOGIN}')
    print('-' * 50)
    
    try:
        session = requests.Session()
        login_url = f'{API_BASE_URL}/api/v2/login'
        
        print(f'\nTestando endpoint: {login_url}')
        
        # Dados do login
        login_data = {
            'login': API_LOGIN,
            'password': API_PASSWORD
        }
        
        # Tenta fazer login com JSON
        try:
            response = session.post(login_url, json=login_data, timeout=10)
            print(f'  Status: {response.status_code}')
            
            if response.status_code == 200:
                print(f'  ✓ Login bem-sucedido!')
                
                # Tenta parsear a resposta JSON
                try:
                    response_data = response.json()
                    print(f'\n  Resposta JSON:')
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    
                    # Extrai o token
                    token = response_data.get('token')
                    status = response_data.get('2FA_status')
                    id_usuario = response_data.get('idUsuario')
                    
                    if token:
                        print(f'\n  ✓ Token extraído com sucesso!')
                        print(f'    Status: {status}')
                        print(f'    ID Usuário: {id_usuario}')
                        print(f'    Token (primeiros 50 chars): {token[:50]}...')
                        print(f'    Token (completo): {token}')
                        
                        # Configura o header de autorização para a sessão
                        session.headers.update({'Authorization': f'Bearer {token}'})
                        
                        return {'session': session, 'token': token, 'data': response_data}
                    else:
                        print(f'\n  ⚠ Token não encontrado na resposta')
                        return None
                        
                except json.JSONDecodeError:
                    print(f'  ⚠ Resposta não é JSON válido: {response.text[:200]}')
                    return None
                    
            elif response.status_code == 404:
                print(f'  ✗ Endpoint não encontrado')
                return None
            else:
                print(f'  ✗ Falha no login')
                print(f'  Resposta: {response.text[:200]}')
                return None
                    
        except Exception as e:
            print(f'  Erro: {e}')
            return None
        
    except Exception as e:
        print(f'✗ Erro ao testar login: {e}')
        return None

def test_api_connection():
    """Testa a conexão básica com a API"""
    print('\n=== TESTE DE CONEXÃO COM A API ===')
    print(f'URL: {API_BASE_URL}')
    print('-' * 50)
    
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        print(f'Status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        print(f'Resposta (primeiros 500 chars):\n{response.text[:500]}')
        
        if response.status_code == 200:
            print('\n✓ Conexão estabelecida com sucesso!')
        else:
            print(f'\n⚠ Conexão estabelecida mas retornou status {response.status_code}')
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f'\n✗ Erro ao conectar: {e}')
        return False

def test_buscar_lancamentos(session, token):
    """Testa a busca de lançamentos"""
    print('\n=== TESTE DE BUSCA DE LANÇAMENTOS ===')
    print('-' * 50)
    
    try:
        # Define data como ontem
        data_ontem = datetime.now() - timedelta(days=1)
        data_str = data_ontem.strftime('%Y-%m-%d')
        
        print(f'Data: {data_str}')
        print(f'Conta Corrente: 1397 (Banco BMG)')
        
        # Monta o body
        body = {
            "filter": {
                "_and": [
                    {
                        "numero_cc": {
                            "_eq": 1397
                        }
                    },
                    {
                        "data_lancamento": {
                            "_gte": data_str
                        }
                    },
                    {
                        "data_lancamento": {
                            "_lte": data_str
                        }
                    }
                ]
            },
            "sort": "data_lancamento",
            "limit": 5000
        }
        
        # Faz a requisição
        url = f'{API_BASE_URL}/api/v2/cclan/listar'
        headers = {'Authorization': f'Bearer {token}'}
        
        print(f'\nPOST {url}')
        response = session.post(url, json=body, headers=headers, timeout=30)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'\n✓ Requisição bem-sucedida!')
            
            # Trata diferentes estruturas de resposta
            if isinstance(data, list):
                # Se a resposta já é uma lista
                lancamentos = data
            elif isinstance(data, dict):
                # Se é um objeto, tenta extrair a lista
                lancamentos = data.get('data', data.get('items', None))
            else:
                lancamentos = None
            
            if lancamentos and isinstance(lancamentos, list):
                print(f'\n✓ Total de lançamentos: {len(lancamentos)}')
                
                if len(lancamentos) > 0:
                    print(f'\n--- Exemplo do primeiro lançamento ---')
                    print(json.dumps(lancamentos[0], indent=2, ensure_ascii=False))
                else:
                    print('\n⚠ Nenhum lançamento encontrado para a data especificada')
            else:
                print(f'\n⚠ Estrutura de resposta inesperada:')
                print(f'Tipo: {type(data)}')
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                
            return True
        else:
            print(f'\n✗ Erro na requisição')
            print(f'Resposta: {response.text[:300]}')
            return False
            
    except Exception as e:
        print(f'\n✗ Erro: {e}')
        return False

def test_processar_lancamento_completo(session, token):
    """Testa o processamento completo de um lançamento"""
    print('\n=== TESTE DE PROCESSAMENTO COMPLETO ===')
    print('-' * 50)
    
    try:
        # Busca lançamentos reais da API
        data_hoje = datetime.now()
        data_str = data_hoje.strftime('%Y-%m-%d')
        
        print(f'Buscando lançamentos reais de: {data_str}')
        
        headers = {'Authorization': f'Bearer {token}'}
        body_lancamentos = {
            "filter": {
                "_and": [
                    {"numero_cc": {"_eq": 1397}},
                    {"data_lancamento": {"_gte": data_str}},
                    {"data_lancamento": {"_lte": data_str}}
                ]
            },
            "sort": "data_lancamento",
            "limit": 5000
        }
        
        url_lancamentos = f'{API_BASE_URL}/api/v2/cclan/listar'
        response_lancamentos = session.post(url_lancamentos, json=body_lancamentos, headers=headers, timeout=30)
        
        if response_lancamentos.status_code != 200:
            print(f'✗ Erro ao buscar lançamentos: {response_lancamentos.text[:200]}')
            return False
        
        lancamentos = response_lancamentos.json()
        
        if not lancamentos or not isinstance(lancamentos, list) or len(lancamentos) == 0:
            print('⚠ Nenhum lançamento encontrado para processar')
            return False
        
        print(f'✓ {len(lancamentos)} lançamento(s) encontrado(s)')
        
        # Pega o primeiro lançamento para testar
        lancamento = lancamentos[0]
        
        print(f'\nProcessando primeiro lançamento:')
        print(f'  Documento: {lancamento.get("documento", "N/A")}')
        print(f'  Valor: {lancamento.get("valor", "N/A")}')
        print(f'  Data: {lancamento.get("data_lancamento", "N/A")}')
        
        # 1. Sanitiza documento
        import re
        documento = lancamento.get('documento', '')
        if not documento:
            print('✗ Documento não encontrado no lançamento')
            return False
        
        numeros = re.findall(r'\d+', documento)
        id_spf = numeros[0] if numeros else ""
        print(f'\n→ ID SPF extraído: {id_spf}')
        
        if not id_spf:
            print('✗ Não foi possível extrair ID SPF')
            return False
        
        # 2. Busca SPF
        headers = {'Authorization': f'Bearer {token}'}
        
        body_spf = {
            "filter": {
                "_and": [
                    {"id_spf": {"_eq": id_spf}}
                ]
            },
            "limit": 1
        }
        
        url_spf = f'{API_BASE_URL}/api/v2/spf/listar'
        print(f'\n→ Buscando SPF em: {url_spf}')
        response_spf = session.post(url_spf, json=body_spf, headers=headers, timeout=30)
        
        print(f'  Status: {response_spf.status_code}')
        
        if response_spf.status_code != 200:
            print(f'✗ Erro ao buscar SPF: {response_spf.text[:200]}')
            return False
        
        spf_data = response_spf.json()
        spf = spf_data[0] if isinstance(spf_data, list) and len(spf_data) > 0 else None
        
        if not spf:
            print('✗ SPF não encontrado')
            return False
        
        pj = spf.get('pj', '')
        print(f'  ✓ PJ encontrado: {pj}')
        
        if not pj:
            print('⚠ PJ não encontrado no SPF')
            return False
        
        # 3. Busca Processo
        body_processo = {
            "filter": {
                "_and": [
                    {"pj": {"_eq": pj}}
                ]
            },
            "limit": 1
        }
        
        url_processo = f'{API_BASE_URL}/api/v2/processo'
        print(f'\n→ Buscando processo em: {url_processo}')
        response_processo = session.post(url_processo, json=body_processo, headers=headers, timeout=30)
        
        print(f'  Status: {response_processo.status_code}')
        
        if response_processo.status_code != 200:
            print(f'✗ Erro ao buscar processo: {response_processo.text[:200]}')
            return False
        
        processo_data = response_processo.json()
        processo = processo_data[0] if isinstance(processo_data, list) and len(processo_data) > 0 else None
        
        if not processo:
            print('✗ Processo não encontrado')
            return False
        
        numero_processo = processo.get('numero_processo', '')
        # Sanitiza número do processo para conter apenas números
        numero_processo = ''.join(c for c in numero_processo if c.isdigit())
        print(f'  ✓ Número do processo: {numero_processo}')
        
        numero_integracao = processo.get('numero_integracao', '')
        print(f'  ✓ Número de integração: {numero_integracao}')
        
        # 4. Formata data
        data_lancamento_raw = lancamento.get('data_lancamento', '')
        # Formata data de YYYY-MM-DD para DD/MM/YYYY
        if 'T' in data_lancamento_raw:
            data_obj = datetime.fromisoformat(data_lancamento_raw.replace('Z', '+00:00'))
        else:
            data_obj = datetime.strptime(data_lancamento_raw, '%Y-%m-%d')
        data_lancamento = data_obj.strftime('%d/%m/%Y')
        
        # 5. Monta resultado final no formato padrão
        print('\n--- RESULTADO FINAL ---')
        
        # Formata valor com 2 casas decimais e vírgula (formato brasileiro)
        valor_raw = lancamento.get('valor', '')
        try:
            valor_float = float(str(valor_raw).replace(',', '.'))
            valor = f"{valor_float:.2f}".replace('.', ',')
        except (ValueError, AttributeError):
            valor = str(valor_raw).replace('.', ',')
        
        registro = {
            'historico': '',
            'data_lancamento': data_lancamento,
            'valor_em_r': valor,
            'debito_na_moeda': valor,
            'credito_na_moeda': '0',
            'saldo': valor,
            'pro_numero_de_integracao': numero_integracao,
            'pro_numero_do_processo': numero_processo,
            'id_spf': id_spf,
            'ccc_pes_nome': 'BANCO BMG S.A.',
            'tco_descricao': 'Clientes - Recup. Custas processuais'
        }
        
        resultado_final = {
            'contagem': 1,
            'valor_somado': valor,
            'registros': [registro]
        }
        
        print(json.dumps(resultado_final, indent=2, ensure_ascii=False))
        print('\n✓ Processamento completo bem-sucedido!')
        return True
        
    except Exception as e:
        print(f'\n✗ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_processar_documentos():
    """Testa o processamento e download de documentos dos registros"""
    print('\n=== TESTE DE PROCESSAMENTO DE DOCUMENTOS ===')
    print('-' * 60)
    
    try:
        # 1. Faz login
        print('→ Fazendo login...')
        resultado_login = api_login()
        if not resultado_login:
            print('✗ Falha no login')
            return False
        
        print('✓ Login realizado com sucesso')
        
        # 2. Processa os documentos dos registros do JSON
        print('\n→ Processando documentos dos registros...')
        processar_documentos_registros()
        
        print('\n✓ Processamento de documentos concluído!')
        return True
        
    except Exception as e:
        print(f'\n✗ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_processar_todos_lancamentos():
    """Testa o processamento completo de todos os lançamentos"""
    print('\n=== TESTE DE PROCESSAMENTO COMPLETO - TODOS OS LANÇAMENTOS ===')
    print('-' * 60)
    
    try:
        # 1. Faz login
        print('→ Fazendo login...')
        resultado_login = api_login()
        if not resultado_login:
            print('✗ Falha no login')
            return False
        
        print('✓ Login realizado com sucesso')
        
        # 2. Busca lançamentos do dia
        data_hoje = datetime.now()
        
        print(f'\n→ Buscando lançamentos de: {data_hoje.strftime("%Y-%m-%d")}')
        print(f'  Conta corrente: 1397')
        
        lancamentos = api_buscar_lancamentos(
            data_inicial=data_hoje,
            data_final=data_hoje,
            numero_cc=1397,
            limit=5000
        )
        
        if not lancamentos:
            print('⚠ Nenhum lançamento encontrado')
            return False
        
        print(f'✓ {len(lancamentos)} lançamento(s) encontrado(s)')
        
        # 3. Processa todos os lançamentos usando a função do main.py
        print(f'\n→ Processando todos os lançamentos...')
        resultado = processar_lancamentos(lancamentos)
        
        # 4. Exibe resultado final
        print('\n' + '=' * 60)
        print('RESULTADO FINAL')
        print('=' * 60)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        print('\n' + '=' * 60)
        print(f'✓ Total processado: {resultado["contagem"]} lançamentos')
        print(f'✓ Valor total: R$ {resultado["valor_somado"]}')
        print('=' * 60)
        
        return True
        
    except Exception as e:
        print(f'\n✗ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa os testes"""
    print('\n' + '=' * 60)
    print('TESTE DE INTEGRAÇÃO COM API')
    print('=' * 60)
    
    # Teste 1: Processar lançamentos
    print('\n[TESTE 1] Processamento de Lançamentos')
    if test_processar_todos_lancamentos():
        print('\n✓ TESTE 1: SUCESSO')
    else:
        print('\n✗ TESTE 1: FALHOU')
    
    # Teste 2: Processar documentos
    print('\n\n[TESTE 2] Processamento de Documentos')
    if test_processar_documentos():
        print('\n✓ TESTE 2: SUCESSO')
    else:
        print('\n✗ TESTE 2: FALHOU')
    
    print('\n' + '=' * 60)
    print('FIM DOS TESTES')
    print('=' * 60 + '\n')

if __name__ == '__main__':
    main()
