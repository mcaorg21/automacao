"""
CPJ API Functions - Funções de integração com a API do CPJ Agnes
Autor: Sistema de Automação CPJ
Data: 2026-02-13
"""

import os
import json
import pdb
import re
import traceback
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from PyPDF2 import PdfMerger
import requests

# Variáveis globais para sessão e token
API_SESSION = None
API_TOKEN = None

# Configurações que serão definidas externamente
API_BASE_URL = None
API_LOGIN = None
API_PASSWORD = None
JSON_PATH = None
PLANILHA_PATH = None
PDF_MERGE_PATH = None

# Caminho do arquivo de configuração
CONFIG_JSON_PATH = r'C:\www\automacao\sites\cpj-reembolso-bmg\config.json'

def set_api_credentials(base_url: str, login: str, password: str, json_path: str = None, planilha_path: str = None, pdf_merge_path: str = None, config_json_path: str = None):
    """Configura as credenciais da API
    
    Args:
        base_url: URL base da API
        login: Login da API
        password: Senha da API
        json_path: Caminho do arquivo JSON (opcional)
        planilha_path: Caminho da pasta de planilhas (opcional)
        pdf_merge_path: Caminho da pasta pdf_merge (opcional)
        config_json_path: Caminho do arquivo config.json (opcional)
    """
    global API_BASE_URL, API_LOGIN, API_PASSWORD, JSON_PATH, PLANILHA_PATH, PDF_MERGE_PATH, CONFIG_JSON_PATH
    API_BASE_URL = base_url
    API_LOGIN = login
    API_PASSWORD = password
    if json_path:
        JSON_PATH = json_path
    if planilha_path:
        PLANILHA_PATH = planilha_path
    if pdf_merge_path:
        PDF_MERGE_PATH = pdf_merge_path
    if config_json_path:
        CONFIG_JSON_PATH = config_json_path

def get_api_session():
    """Retorna a sessão atual da API"""
    return API_SESSION

def get_api_token():
    """Retorna o token atual da API"""
    return API_TOKEN

def api_login():
    """Realiza o login na API e retorna o token Bearer
    
    Returns:
        str: Token Bearer para autenticação
        None: Se o login falhar
    """
    global API_SESSION, API_TOKEN
    
    print('\n=== Realizando login na API ===')
    print(f'URL: {API_BASE_URL}')
    print(f'Login: {API_LOGIN}')
    
    try:
        # Cria uma nova sessão
        session = requests.Session()
        
        # Dados do login
        login_data = {
            'login': API_LOGIN,
            'password': API_PASSWORD
        }
        
        # Endpoint de login
        login_url = f'{API_BASE_URL}/api/v2/login'
        
        print(f'Tentando autenticar em: {login_url}')
        response = session.post(login_url, json=login_data, timeout=180)
        
        # Verifica se o login foi bem-sucedido
        if response.status_code == 200:
            response_data = response.json()
            
            # Extrai o token da resposta
            token = response_data.get('token')
            status = response_data.get('2FA_status')
            id_usuario = response_data.get('idUsuario')
            
            if token:
                print('✓ Login realizado com sucesso!')
                print(f'  Status: {status}')
                print(f'  ID Usuário: {id_usuario}')
                print(f'  Token: {token[:50]}...')
                
                # Armazena o token globalmente
                API_TOKEN = token
                API_SESSION = session
                
                # Configura o header de autorização padrão para todas as requisições
                session.headers.update({'Authorization': f'Bearer {token}'})
                
                return token
            else:
                print('✗ Token não encontrado na resposta')
                print(f'Resposta: {response_data}')
                return None
        else:
            print(f'✗ Falha no login. Status: {response.status_code}')
            print(f'Resposta: {response.text[:200]}')
            return None
            
    except requests.exceptions.RequestException as e:
        print(f'✗ Erro ao conectar com a API: {e}')
        return None
    except Exception as e:
        print(f'✗ Erro inesperado no login: {e}')
        traceback.print_exc()
        return None

def api_logout():
    """Realiza o logout da API
    
    Returns:
        bool: True se logout bem-sucedido, False caso contrário
    """
    global API_SESSION, API_TOKEN
    
    print('\n=== Realizando logout da API ===')
    
    # Se não há sessão ativa, não precisa fazer logout
    if not API_TOKEN or not API_SESSION:
        print('⚠ Nenhuma sessão ativa para deslogar')
        return True
    
    try:
        # Endpoint de logout
        logout_url = f'{API_BASE_URL}/api/v2/logout'
        
        print(f'Fazendo logout em: {logout_url}')
        
        # Headers com Bearer token
        headers = {'Authorization': f'Bearer {API_TOKEN}'}
        
        response = API_SESSION.post(logout_url, headers=headers, timeout=180)
        
        if response.status_code in [200, 201, 204]:
            print('✓ Logout realizado com sucesso!')
            
            # Limpa as variáveis globais
            API_TOKEN = None
            API_SESSION = None
            
            return True
        else:
            print(f'⚠ Resposta inesperada do logout. Status: {response.status_code}')
            print(f'Resposta: {response.text[:200]}')
            
            # Mesmo assim limpa as variáveis
            API_TOKEN = None
            API_SESSION = None
            
            return True
            
    except requests.exceptions.RequestException as e:
        print(f'✗ Erro ao conectar com a API para logout: {e}')
        # Limpa as variáveis mesmo com erro
        API_TOKEN = None
        API_SESSION = None
        return False
    except Exception as e:
        print(f'✗ Erro inesperado no logout: {e}')
        traceback.print_exc()
        # Limpa as variáveis mesmo com erro
        API_TOKEN = None
        API_SESSION = None
        return False

def api_get(endpoint: str, params: dict = None):
    """Faz uma requisição GET autenticada na API
    
    Args:
        endpoint: Endpoint da API (ex: '/processos', '/cliente/123')
        params: Parâmetros opcionais da query string
        
    Returns:
        dict: Resposta da API em formato JSON
        None: Se a requisição falhar
    """
    global API_SESSION, API_TOKEN
    
    # Garante que há um token ativo
    if not API_TOKEN or not API_SESSION:
        print('Token não encontrado. Realizando login...')
        if not api_login():
            return None
    
    try:
        url = f'{API_BASE_URL}{endpoint}'
        print(f'GET {url}')
        
        # Headers com Bearer token
        headers = {'Authorization': f'Bearer {API_TOKEN}'}
        
        response = API_SESSION.get(url, params=params, headers=headers, timeout=180)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print('✗ Token expirado ou inválido. Tentando reautenticar...')
            if api_login():
                # Tenta novamente com o novo token
                headers = {'Authorization': f'Bearer {API_TOKEN}'}
                response = API_SESSION.get(url, params=params, headers=headers, timeout=180)
                if response.status_code == 200:
                    return response.json()
            print(f'✗ Falha na reautenticação')
            return None
        else:
            print(f'✗ Erro na requisição. Status: {response.status_code}')
            print(f'Resposta: {response.text[:200]}')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao fazer requisição GET: {e}')
        traceback.print_exc()
        return None

def api_post(endpoint: str, data: dict = None):
    """Faz uma requisição POST autenticada na API
    
    Args:
        endpoint: Endpoint da API
        data: Dados a serem enviados no corpo da requisição
        
    Returns:
        dict: Resposta da API em formato JSON
        None: Se a requisição falhar
    """
    global API_SESSION, API_TOKEN
    
    # Garante que há um token ativo
    if not API_TOKEN or not API_SESSION:
        print('Token não encontrado. Realizando login...')
        if not api_login():
            return None
    
    try:
        url = f'{API_BASE_URL}{endpoint}'
        print(f'POST {url}')
        
        # Headers com Bearer token
        headers = {'Authorization': f'Bearer {API_TOKEN}'}
        
        response = API_SESSION.post(url, json=data, headers=headers, timeout=180)
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code in [400, 401]:
            print(f'✗ Erro {response.status_code}. Tentando reautenticar...')
            if api_login():
                # Tenta novamente com o novo token
                headers = {'Authorization': f'Bearer {API_TOKEN}'}
                response = API_SESSION.post(url, json=data, headers=headers, timeout=180)
                if response.status_code in [200, 201]:
                    return response.json()
                print(f'✗ Falha após reautenticação. Status: {response.status_code}')
                print(f'Resposta: {response.text[:200]}')
            else:
                print(f'✗ Falha na reautenticação')
            return None
        else:
            print(f'✗ Erro na requisição. Status: {response.status_code}')
            print(f'Resposta: {response.text[:200]}')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao fazer requisição POST: {e}')
        traceback.print_exc()
        return None

def api_buscar_lancamentos(data_inicial: datetime = None, data_final: datetime = None, numero_cc: int = 1397, limit: int = 5000, titulo: str = None, valor_limite_original: bool = True, documento_spf: str = True):
    """Busca lançamentos da conta corrente na API
    
    Args:
        data_inicial: Data inicial para busca (padrão: ontem)
        data_final: Data final para busca (padrão: ontem)
        numero_cc: Número da conta corrente (padrão: 1397 - Banco BMG)
        limit: Limite de registros (padrão: 5000)
        
    Returns:
        list: Lista de lançamentos encontrados
        None: Se a requisição falhar
    """
    try:
        print('\n=== Buscando lançamentos na API ===')

        # Define data padrão como ontem se não informada
        if data_inicial is None:
            data_inicial = datetime.now() - timedelta(days=1)
        if data_final is None:
            data_final = datetime.now() - timedelta(days=1)
        
        # Formata datas para o formato da API (YYYY-MM-DD)
        data_inicial_str = data_inicial.strftime('%Y-%m-%d')
        data_final_str = data_final.strftime('%Y-%m-%d')
        
        print(f'Conta Corrente: {numero_cc}')
        print(f'Data Inicial: {data_inicial_str}')
        print(f'Data Final: {data_final_str}')
        print(f'Limite: {limit} registros')
        
        # Monta o body da requisição
        body = {
            "filter": {
                "_and": [
                    {
                        "ccl.numero_cc": {
                            "_in": numero_cc
                        }
                    },
                    {
                        "data_lancamento": {
                            "_gte": data_inicial_str
                        }
                    },
                    {
                        "data_lancamento": {
                            "_lte": data_final_str
                        }
                    }
                ]
            },
            "sort": "data_lancamento",
            "limit": limit
        }

        if titulo:
            body["filter"]["_and"].append({"id_titulo": {"_eq": titulo}})

        if valor_limite_original:
            body["filter"]["_and"].append({"valor_original": {"_lt": 4000000000}})
        
        if documento_spf:
            body["filter"]["_and"].append({"documento": {"_like": "SPF"}})

        # Faz a requisição POST
        response = api_post('/api/v2/cclan/listar', data=body)

        if numero_cc == 1397:
            # Carrega lista de bloqueados do arquivo JSON
            bloqueados_json_path = os.path.join(os.path.dirname(__file__), 'bloqueados_id_spf.json')
            bloqueados = []
            try:
                with open(bloqueados_json_path, 'r', encoding='utf-8') as f:
                    bloqueados_data = json.load(f)
                    bloqueados = bloqueados_data.get('bloqueados', [])
            except Exception as e:
                print(f'⚠ Erro ao carregar bloqueados_id_spf.json: {e}')

        if response:
            # Verifica se a resposta tem dados
            if isinstance(response, list):
                # Se a resposta já é uma lista
                lancamentos = response
            elif isinstance(response, dict):
                # Se é um objeto, tenta extrair a lista
                lancamentos = response.get('data', response.get('items', None))
            else:
                lancamentos = None
            
            if lancamentos and isinstance(lancamentos, list):
                # Filtra lançamentos que contêm "pagamento de condenacao" na nota
                lancamentos_filtrados = []
                removidos = 0
                lancamentos_nao_classificados = []

                for lancamento in lancamentos:
                    nota = lancamento.get('nota', '')
                    nota_normalizada = normalizar_texto(nota)

                    #BANCO PAN
                    if numero_cc == 1506:

                        # • APELAÇÃO
                        # • CUSTAS FINAIS
                        # • DESARQUIVAMENTO
                        # • OFÍCIO
                        # • PROTOCOLO POSTAL
                        # • RECURSO ESPECIAL
                        # • RECURSO EXTRAORDINÁRIO
                        # • RECURSO INOMINADO
                        # • HONORÁRIOS DO CONCILIADOR
                        # • HONORÁRIOS DO PERITO
                        # • AGRAVO DE INSTRUMENTO
                        # • AGRAVO INTERNO
                        
                        lancamento['id_spf'] = sanitizar_documento(lancamento['documento'])
                        detalhes_spf = api_buscar_spf(lancamento['id_spf'], limit=10)
                        lancamento['pj'] = detalhes_spf.get('pj', '')
                        tipo_despesa = normalizar_texto(detalhes_spf.get('resumo_solicitacao', '')).strip()

                        if 'apelacao' in tipo_despesa or 'apelcao' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'APELAÇÃO'
                        elif 'recurso' in tipo_despesa or 'preparo recursal' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'PREPARO RECURSAL'
                        elif 'custas finais' in tipo_despesa or 'custas cumprimento de sentenca' in tipo_despesa or 'custas processuais' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS FINAIS'
                        elif 'conciliador' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'HONORÁRIOS DO CONCILIADOR'
                        elif 'contadoria' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS CONTADORIA'
                        elif 'divida ativa' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'DÍVIDA ATIVA'
                        elif 'divida ativa' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'DÍVIDA ATIVA'
                        elif 'custas desarquivamento' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS DESARQUIVAMENTO'
                        elif 'agravo de instrumento' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'AGRAVO DE INSTRUMENTO'
                        elif tipo_despesa == '':
                            lancamento['tipo_despesa'] = 'VAZIO'
                        else:
                            lancamento['tipo_despesa'] = 'CUSTAS FINAIS'
                            # lancamento['tipo_despesa'] = f'NAO_IDENTIFICADO_{tipo_despesa}'
                            # pdb.set_trace()  # Debug: Verificar tipo de despesa desconhecido
                            #lancamento['tipo_despesa'] = 'OUTRO'

                        dados_processo = api_buscar_processo_por_pj(lancamento['pj'])

                        #for parcela in api_buscar_spf(lancamento['id_spf'])['parcela']: 
                        lancamento['valores_parcelas'] = ','.join(str(parcela.get('valor', '')) for parcela in detalhes_spf['parcela']) 

                        # if lancamento['id_spf'] == '51884':
                        #     pdb.set_trace()  # Debug: Verificar dados do processo e parcelas para o lançamento

                        lancamento['numero_processo'] = dados_processo[0].get('numero_processo', '')
                        lancamento['autor_nome'] = dados_processo[0].get('autor_nome').upper()
                        lancamento['id_caso'] = sanitizar_documento(dados_processo[0].get('numero_integracao', ''))

                        if lancamento['tipo_despesa'] == 'VAZIO':
                            lancamentos_nao_classificados.append(dados_processo[0].get('numero_integracao', ''))


                        lancamentos_filtrados.append(lancamento)

                    #BANCO BMG
                    elif numero_cc == 1397:

                        if 'condenacao' not in nota_normalizada and all(bloqueado not in lancamento['documento'] for bloqueado in bloqueados):
                            lancamentos_filtrados.append(lancamento)
                        else:
                            id_spf = sanitizar_documento(lancamento['documento'])
                            civ = api_buscar_processo(api_buscar_spf(id_spf)['pj'])['numero_integracao']
                            registrar_removido(civ, nota_normalizada, CONFIG_JSON_PATH)
                            removidos += 1

                    elif numero_cc in "36, 1394, 1373, 1449, 1479":
                        lancamentos_filtrados.append(lancamento)

                print(f'✓ {len(lancamentos_filtrados)} lançamento(s) encontrado(s)!')
                if removidos > 0:
                    print(f'  ⚠ {removidos} lançamento(s) removido(s)')

                # if lancamentos_nao_classificados:
                #     pdb.set_trace()  # Debug: Verificar lançamentos vazios
                
                return lancamentos_filtrados
            else:
                print(f'✓ Resposta recebida (formato não esperado)')
                return response
        else:
            print('✗ Nenhum lançamento encontrado')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar lançamentos: {e}')
        traceback.print_exc()
        return None

def api_buscar_lancamentos_filtro(filtros: list, limit: int = 5000, sort: str = 'data_lancamento'):
    """Busca lançamentos da conta corrente com filtro customizado
    
    Args:
        filtros: Lista de condições para o campo _and do filtro (ex: [{"numero_cc": {"_eq": 36}}, ...])
        limit: Limite de registros (padrão: 5000)
        sort: Campo de ordenação (padrão: 'data_lancamento')
        
    Returns:
        list: Lista de lançamentos encontrados
        None: Se a requisição falhar
    """
    try:
        body = {
            "filter": {
                "_and": filtros
            },
            "sort": sort,
            "limit": limit
        }

        response = api_post('/api/v2/cclan/listar', data=body)
        
        if response:
            if isinstance(response, list):
                print(f'✓ {len(response)} lançamento(s) encontrado(s)!')
                return response
            elif isinstance(response, dict):
                data = response.get('data', response.get('items', None))
                if isinstance(data, list):
                    print(f'✓ {len(data)} lançamento(s) encontrado(s)!')
                    return data
            print(f'✓ Resposta recebida (formato não esperado)')
            return response
        else:
            print('✗ Nenhum lançamento encontrado')
            return None

    except Exception as e:
        print(f'✗ Erro ao buscar lançamentos: {e}')
        traceback.print_exc()
        return None

def api_buscar_lancamentos_bmg(data_inicial: datetime = None, data_final: datetime = None, numero_cc: int = 1397, limit: int = 5000, titulo: str = None, valor_limite_original: bool = True, documento_spf: str = True, tipo_lancamento: str = "Reembsolso"):
    """Busca lançamentos da conta corrente na API
    
    Args:
        data_inicial: Data inicial para busca (padrão: ontem)
        data_final: Data final para busca (padrão: ontem)
        numero_cc: Número da conta corrente (padrão: 1397 - Banco BMG)
        limit: Limite de registros (padrão: 5000)
        titulo: Título do lançamento (padrão: None)
        valor_limite_original: Se deve considerar o valor limite original (padrão: True)
        documento_spf: Se deve considerar o documento SPF (padrão: True)
        tipo_lancamento: Tipo de lançamento (padrão: "Reembsolso")
    Returns:
        list: Lista de lançamentos encontrados
        None: Se a requisição falhar
    """
    try:
        print('\n=== Buscando lançamentos na API ===')

        # Define data padrão como ontem se não informada
        if data_inicial is None:
            data_inicial = datetime.now() - timedelta(days=1)
        if data_final is None:
            data_final = datetime.now() - timedelta(days=1)
        
        # Formata datas para o formato da API (YYYY-MM-DD)
        data_inicial_str = data_inicial.strftime('%Y-%m-%d')
        data_final_str = data_final.strftime('%Y-%m-%d')
        
        print(f'Conta Corrente: {numero_cc}')
        print(f'Data Inicial: {data_inicial_str}')
        print(f'Data Final: {data_final_str}')
        print(f'Limite: {limit} registros')
        
        # Monta o body da requisição
        body = {
            "filter": {
                "_and": [
                    {
                        "id_titulo": {
                            "_in": titulo
                        }
                    }
                ]
            },
            "sort": "data_lancamento",
            "limit": limit
        }
        
        # Faz a requisição POST
        response = api_post('/api/v2/cclan/listar', data=body)

        # Carrega lista de bloqueados do arquivo JSON
        bloqueados_json_path = os.path.join(os.path.dirname(__file__), 'bloqueados_id_spf.json')
        bloqueados = []
        try:
            with open(bloqueados_json_path, 'r', encoding='utf-8') as f:
                bloqueados_data = json.load(f)
                bloqueados = bloqueados_data.get('bloqueados', [])
        except Exception as e:
            print(f'⚠ Erro ao carregar bloqueados_id_spf.json: {e}')

        if response:
            # Verifica se a resposta tem dados
            if isinstance(response, list):
                # Se a resposta já é uma lista
                lancamentos = response
            elif isinstance(response, dict):
                # Se é um objeto, tenta extrair a lista
                lancamentos = response.get('data', response.get('items', None))
            else:
                lancamentos = None

            if tipo_lancamento == "Reembolso":
            
                if lancamentos and isinstance(lancamentos, list):
                    # Filtra lançamentos que contêm "pagamento de condenacao" na nota
                    lancamentos_filtrados = []
                    removidos = 0
                    lancamentos_nao_classificados = []

                    for lancamento in lancamentos:
                        nota = lancamento.get('nota', '')
                        nota_normalizada = normalizar_texto(nota)

                        if 'condenacao' not in nota_normalizada and all(bloqueado not in lancamento['documento'] for bloqueado in bloqueados):
                            lancamentos_filtrados.append(lancamento)
                        else:
                            id_spf = sanitizar_documento(lancamento['documento'])
                            civ = api_buscar_processo(api_buscar_spf(id_spf)['pj'])['numero_integracao']
                            registrar_removido(civ, nota_normalizada, CONFIG_JSON_PATH)
                            removidos += 1


                    print(f'✓ {len(lancamentos_filtrados)} lançamento(s) encontrado(s)!')
                    if removidos > 0:
                        print(f'  ⚠ {removidos} lançamento(s) removido(s)')

                # if lancamentos_nao_classificados:
                #     pdb.set_trace()  # Debug: Verificar lançamentos vazios
                
                return lancamentos_filtrados
            else:
                print(f'✓ Resposta recebida (formato não esperado)')
                return response
        else:
            print('✗ Nenhum lançamento encontrado')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar lançamentos: {e}')
        traceback.print_exc()
        return None

def api_buscar_lancamentos_pan(data_inicial: datetime = None, data_final: datetime = None, numero_cc: int = 1397, limit: int = 5000, titulo: str = None, valor_limite_original: bool = True, documento_spf: str = True):
    """Busca lançamentos da conta corrente na API
    
    Args:
        data_inicial: Data inicial para busca (padrão: ontem)
        data_final: Data final para busca (padrão: ontem)
        numero_cc: Número da conta corrente (padrão: 1397 - Banco BMG)
        limit: Limite de registros (padrão: 5000)
        
    Returns:
        list: Lista de lançamentos encontrados
        None: Se a requisição falhar
    """
    try:
        print('\n=== Buscando lançamentos na API ===')

        # Define data padrão como ontem se não informada
        if data_inicial is None:
            data_inicial = datetime.now() - timedelta(days=1)
        if data_final is None:
            data_final = datetime.now() - timedelta(days=1)
        
        # Formata datas para o formato da API (YYYY-MM-DD)
        data_inicial_str = data_inicial.strftime('%Y-%m-%d')
        data_final_str = data_final.strftime('%Y-%m-%d')
        
        print(f'Conta Corrente: {numero_cc}')
        print(f'Data Inicial: {data_inicial_str}')
        print(f'Data Final: {data_final_str}')
        print(f'Limite: {limit} registros')
        
        # Monta o body da requisição
        body = {
            "filter": {
                "_and": [
                    {
                        "id_titulo": {
                            "_in": titulo
                        }
                    }
                ]
            },
            "sort": "data_lancamento",
            "limit": limit
        }
        
        # Faz a requisição POST
        response = api_post('/api/v2/cclan/listar', data=body)

        if response:
            # Verifica se a resposta tem dados
            if isinstance(response, list):
                # Se a resposta já é uma lista
                lancamentos = response
            elif isinstance(response, dict):
                # Se é um objeto, tenta extrair a lista
                lancamentos = response.get('data', response.get('items', None))
            else:
                lancamentos = None
            
            if lancamentos and isinstance(lancamentos, list):
                # Filtra lançamentos que contêm "pagamento de condenacao" na nota
                lancamentos_filtrados = []
                removidos = 0
                lancamentos_nao_classificados = []

                for lancamento in lancamentos:
                    nota = lancamento.get('nota', '')
                    nota_normalizada = normalizar_texto(nota)

                    #BANCO PAN
                    if numero_cc == 1506:

                        # • APELAÇÃO
                        # • CUSTAS FINAIS
                        # • DESARQUIVAMENTO
                        # • OFÍCIO
                        # • PROTOCOLO POSTAL
                        # • RECURSO ESPECIAL
                        # • RECURSO EXTRAORDINÁRIO
                        # • RECURSO INOMINADO
                        # • HONORÁRIOS DO CONCILIADOR
                        # • HONORÁRIOS DO PERITO
                        # • AGRAVO DE INSTRUMENTO
                        # • AGRAVO INTERNO
                        
                        lancamento['id_spf'] = sanitizar_documento(lancamento['documento'])
                        detalhes_spf = api_buscar_spf(lancamento['id_spf'], limit=10)
                        lancamento['pj'] = detalhes_spf.get('pj', '')
                        tipo_despesa = normalizar_texto(detalhes_spf.get('resumo_solicitacao', '')).strip()

                        if 'apelacao' in tipo_despesa or 'apelcao' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'APELAÇÃO'
                        elif 'recurso' in tipo_despesa or 'preparo recursal' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'PREPARO RECURSAL'
                        elif 'custas finais' in tipo_despesa or 'custas cumprimento de sentenca' in tipo_despesa or 'custas processuais' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS FINAIS'
                        elif 'conciliador' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'HONORÁRIOS DO CONCILIADOR'
                        elif 'contadoria' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS CONTADORIA'
                        elif 'divida ativa' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'DÍVIDA ATIVA'
                        elif 'divida ativa' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'DÍVIDA ATIVA'
                        elif 'custas desarquivamento' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'CUSTAS DESARQUIVAMENTO'
                        elif 'agravo de instrumento' in tipo_despesa:
                            lancamento['tipo_despesa'] = 'AGRAVO DE INSTRUMENTO'
                        elif tipo_despesa == '':
                            lancamento['tipo_despesa'] = 'VAZIO'
                        else:
                            lancamento['tipo_despesa'] = 'CUSTAS FINAIS'
                            # lancamento['tipo_despesa'] = f'NAO_IDENTIFICADO_{tipo_despesa}'
                            # pdb.set_trace()  # Debug: Verificar tipo de despesa desconhecido
                            #lancamento['tipo_despesa'] = 'OUTRO'

                        dados_processo = api_buscar_processo_por_pj(lancamento['pj'])

                        #for parcela in api_buscar_spf(lancamento['id_spf'])['parcela']: 
                        lancamento['valores_parcelas'] = ','.join(str(parcela.get('valor', '')) for parcela in detalhes_spf['parcela']) 

                        # if lancamento['id_spf'] == '51884':
                        #     pdb.set_trace()  # Debug: Verificar dados do processo e parcelas para o lançamento

                        lancamento['numero_processo'] = dados_processo[0].get('numero_processo', '')
                        lancamento['autor_nome'] = dados_processo[0].get('autor_nome').upper()
                        lancamento['id_caso'] = sanitizar_documento(dados_processo[0].get('numero_integracao', ''))

                        if lancamento['tipo_despesa'] == 'VAZIO':
                            lancamentos_nao_classificados.append(dados_processo[0].get('numero_integracao', ''))


                        lancamentos_filtrados.append(lancamento)

                print(f'✓ {len(lancamentos_filtrados)} lançamento(s) encontrado(s)!')
                if removidos > 0:
                    print(f'  ⚠ {removidos} lançamento(s) removido(s)')

                # if lancamentos_nao_classificados:
                #     pdb.set_trace()  # Debug: Verificar lançamentos vazios
                
                return lancamentos_filtrados
            else:
                print(f'✓ Resposta recebida (formato não esperado)')
                return response
        else:
            print('✗ Nenhum lançamento encontrado')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar lançamentos: {e}')
        traceback.print_exc()
        return None


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e substituindo ç por c
    
    Args:
        texto: Texto a ser normalizado
        
    Returns:
        str: Texto normalizado em lowercase
    """
    if not texto:
        return ""
    
    # Mapeamento de caracteres acentuados
    acentos = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C'
    }
    
    texto_normalizado = texto.lower()
    for acentuado, sem_acento in acentos.items():
        texto_normalizado = texto_normalizado.replace(acentuado.lower(), sem_acento.lower())
    
    return texto_normalizado

def registrar_removido(civ: str, nota_normalizada: str, config_path: str = None):
    """Registra nota desconhecida no config.json
    
    Args:
        civ: Número do processo CIV
        nota_normalizada: Nota normalizada
        config_path: Caminho do arquivo config.json (opcional, usa CONFIG_JSON_PATH global se não fornecido)
    """
    _config_path = config_path or CONFIG_JSON_PATH
    
    if not _config_path:
        print('  ⚠ CONFIG_JSON_PATH não configurado, não é possível registrar nota desconhecida')
        return
    
    try:
        # Lê o config.json atual
        if os.path.exists(_config_path):
            with open(_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Cria a key lancamentos_removidos se não existir
        if 'lancamentos_removidos' not in config:
            config['lancamentos_removidos'] = []
        
        # Obtém a data atual (sem hora)
        data_atual = datetime.now().strftime('%Y-%m-%d')
        
        # Verifica se já existe um registro com a mesma data
        ja_existe = False
        for registro_existente in config['lancamentos_removidos']:
            data_existente = registro_existente.get('data_hora', '')[:10]  # Pega apenas YYYY-MM-DD
            if data_existente == data_atual and registro_existente.get('civ') == civ:
                ja_existe = True
                print(f'  ℹ Já existe registro de lançamento {civ} removido para a data {data_atual}, não será duplicado')
                #pdb.set_trace()  # Debug: Verificar registro existente para o mesmo CIV e data
                break
        
        # Adiciona o novo registro somente se não existir
        if not ja_existe:
            registro = {
                'civ': civ,
                'nota_normalizada': nota_normalizada,
                'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            config['lancamentos_removidos'].append(registro)
            
            # Salva o config.json
            with open(_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f'  ℹ Lançamento removido registrado no config.json')
        
    except Exception as e:
        print(f'  ⚠ Erro ao registrar lançamento removido: {e}')

def sanitizar_documento(documento: str) -> str:
    """Extrai apenas os números do documento, removendo hífen e dígito verificador
    
    Args:
        documento: String no formato "SPF 49815-3"
        
    Returns:
        str: Números sem hífen e dígito (ex: "49815")
    """
    # Remove tudo que não é número
    numeros = re.findall(r'\d+', documento)
    if numeros:
        # Pega o primeiro grupo de números (antes do hífen)
        return numeros[0]
    return ""

def formatar_data_lancamento(data_str: str) -> str:
    """Formata data do formato da API (YYYY-MM-DD) para DD/MM/YYYY
    
    Args:
        data_str: Data no formato YYYY-MM-DD
        
    Returns:
        str: Data no formato DD/MM/YYYY
    """
    try:
        # Tenta parse de diferentes formatos
        if 'T' in data_str:
            # Formato ISO com hora: 2026-02-10T00:00:00
            data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        else:
            # Formato simples: 2026-02-10
            data = datetime.strptime(data_str, '%Y-%m-%d')
        
        return data.strftime('%d/%m/%Y')
    except Exception as e:
        print(f'⚠ Erro ao formatar data {data_str}: {e}')
        return data_str

def api_buscar_spf(id_spf: str, limit: int = 1):
    """Busca informações do SPF pelo ID
    
    Args:
        id_spf: ID do SPF (ex: "49815")
        limit: Número máximo de resultados a serem retornados (padrão: 1)   
        
    Returns:
        dict: Dados do SPF encontrado
        None: Se não encontrar
    """
    try:
        body = {
            "filter": {
                "_and": [
                    {
                        "id_spf": {
                            "_eq": id_spf
                        }
                    }
                ]
            },
            "limit": limit
        }
        
        response = api_post('/api/v2/spf/listar', data=body)
        
        if response:
            # Verifica estrutura da resposta
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            elif isinstance(response, dict):
                data = response.get('data', response.get('items', None))
                if data and len(data) > 0:
                    return data[0]
        
        return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar SPF {id_spf}: {e}')
        return None

def api_buscar_processo(pj: str):
    """Busca informações do processo pelo PJ
    
    Args:
        pj: Número do PJ
        
    Returns:
        dict: Dados do processo encontrado
        None: Se não encontrar
    """
    try:
        body = {
            "filter": {
                "_and": [
                    {
                        "pj": {
                            "_eq": pj
                        }
                    }
                ]
            },
            "limit": 1
        }
        
        response = api_post('/api/v2/processo', data=body)
        
        if response:
            # Verifica estrutura da resposta
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            elif isinstance(response, dict):
                data = response.get('data', response.get('items', None))
                if data and len(data) > 0:
                    return data[0]
        
        return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar processo PJ {pj}: {e}')
        return None

def api_buscar_processo_por_pj(pj: int):
    """Busca processos pelo número PJ retornando todos os resultados
    
    Args:
        pj: Número do PJ
        
    Returns:
        list: Lista de processos encontrados
        None: Se não encontrar
    """
    try:
        print(f'\n=== Buscando processos pelo PJ {pj} ===')
        
        body = {
            "filter": {
                "_and": [
                    {
                        "pj": {
                            "_eq": pj
                        }
                    }
                ]
            },
            "limit": 1000,
            "sort": "update_data_hora"
        }
        
        response = api_post('/api/v2/processo', data=body)
        
        if response is not None:
            if isinstance(response, list):
                print(f'✓ {len(response)} processo(s) encontrado(s)')
                return response
            elif isinstance(response, dict):
                data = response.get('data', response.get('items', None))
                if isinstance(data, list):
                    print(f'✓ {len(data)} processo(s) encontrado(s)')
                    return data
        
        print(f'✗ Nenhum processo encontrado para PJ {pj}')
        return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar processos PJ {pj}: {e}')
        traceback.print_exc()
        return None

def api_buscar_processo_por_ficha(ficha: str):
    """Busca processos pelo número de ficha retornando todos os resultados
    
    Args:
        ficha: Número da ficha
        
    Returns:
        list: Lista de processos encontrados
        None: Se não encontrar
    """
    try:
        print(f'\n=== Buscando processos pela ficha {ficha} ===')
        
        body = {
            "filter": {
                "_and": [
                    {
                        "ficha": {
                            "_eq": ficha
                        }
                    }
                ]
            },
            "limit": 1000,
            "sort": "update_data_hora"
        }
        
        response = api_post('/api/v2/processo', data=body)
        
        if response is not None:
            if isinstance(response, list):
                print(f'✓ {len(response)} processo(s) encontrado(s)')
                return response
            elif isinstance(response, dict):
                data = response.get('data', response.get('items', None))
                if isinstance(data, list):
                    print(f'✓ {len(data)} processo(s) encontrado(s)')
                    return data
        
        print(f'✗ Nenhum processo encontrado para ficha {ficha}')
        return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar processos por ficha {ficha}: {e}')
        traceback.print_exc()
        return None

def processar_lancamentos(lancamentos: list, filtro_integracao: str = 'CIV', json_path: str = None, planilha_path: str = None):
    """Processa cada lançamento e busca informações relacionadas
    
    Args:
        lancamentos: Lista de lançamentos obtidos da API
        filtro_integracao: String que deve estar presente no numero_integracao (padrão: 'CIV')
        json_path: Caminho para salvar o JSON (opcional, usa JSON_PATH global se não fornecido)
        planilha_path: Caminho da pasta planilha (opcional, usa PLANILHA_PATH global se não fornecido)
        
    Returns:
        dict: Dicionário com contagem, valor_somado e registros processados
    """
    # Usa paths globais se não fornecidos
    _json_path = json_path or JSON_PATH
    _planilha_path = planilha_path or PLANILHA_PATH
    
    # Dicionário de mapeamento número_integração -> histórico
    historico_map = {}
    
    print(f'\n=== Processando {len(lancamentos)} lançamento(s) ===')
    
    registros = []
    valor_total = 0.0
    remover_registros = 0
    
    
    for idx, lancamento in enumerate(lancamentos, start=1):
        try:
            print(f'\n[{idx}/{len(lancamentos)}] Processando lançamento...')
            
            # 1. Extrai documento e sanitiza
            documento = lancamento.get('documento', '')
            if not documento:
                print(f'  ⚠ Documento não encontrado, pulando...')
                continue
            
            id_spf = sanitizar_documento(documento)
            print(f'  Documento: {documento} → ID SPF: {id_spf}')
            
            if not id_spf:
                print(f'  ⚠ Não foi possível extrair ID SPF, pulando...')
                continue
            
            # 2. Extrai valor
            valor_raw = lancamento.get('valor', '')
            print(f'  Valor: {valor_raw}')
            
            # Converte valor para float (ainda não soma no total)
            try:
                valor_float = float(str(valor_raw).replace(',', '.'))
                # Formata valor com 2 casas decimais e vírgula (formato brasileiro)
                valor = f"{valor_float:.2f}".replace('.', ',')
            except (ValueError, AttributeError):
                print(f'  ⚠ Não foi possível converter valor: {valor_raw}')
                valor = valor_raw
                valor_float = 0.0
            
            # 3. Extrai e formata data
            data_lancamento_raw = lancamento.get('data_lancamento', '')
            data_lancamento = formatar_data_lancamento(data_lancamento_raw)
            print(f'  Data: {data_lancamento}')
            
            # 4. Busca SPF
            print(f'  → Buscando SPF {id_spf}...')
            spf = api_buscar_spf(id_spf)
            
            if not spf:
                print(f'  ✗ SPF não encontrado')
                continue
            
            pj = spf.get('pj', '')
            print(f'  ✓ PJ encontrado: {pj}')
            
            if not pj:
                print(f'  ⚠ PJ não encontrado no SPF')
                continue
            
            # 5. Busca Processo
            print(f'  → Buscando processo PJ {pj}...')
            processo = api_buscar_processo(pj)
            
            if not processo:
                print(f'  ✗ Processo não encontrado')
                continue
            
            numero_processo = processo.get('numero_processo', '')
            # Sanitiza número do processo para conter apenas números
            numero_processo = ''.join(c for c in numero_processo if c.isdigit())
            print(f'  ✓ Número do processo: {numero_processo}')
            
            numero_integracao = processo.get('numero_integracao', '')
            print(f'  ✓ Número de integração: {numero_integracao}')
            
            # Filtra apenas processos que contenham o filtro no numero_integracao
            if filtro_integracao and filtro_integracao not in numero_integracao:
                print(f'  ⚠ Número de integração não contém "{filtro_integracao}", pulando...')
                remover_registros += 1
                continue

            # 6. Busca histórico
            # Primeiro tenta pegar do SPF
            #nota = spf.get('nota', '').strip()
            
            # Normaliza espaços múltiplos no campo nota
            
            if lancamento['nota'] is not None:
                lancamento['nota'] = ' '.join(lancamento['nota'].split())
                nota_upper = lancamento['nota'].upper()
                
                # Switch case para diferentes tipos de custas
                if 'APELAÇÃO CIVEL' in nota_upper or 'APELACAO CIVEL' in nota_upper or 'APELACAO CÍVEL' in nota_upper or 'APELAÇÃO CÍVEL' in nota_upper:
                    lancamento['nota'] = 'APELAÇÃO CIVEL'
                
                elif 'CUSTA FINAIS' in nota_upper or 'CUSTAS FINAIS' in nota_upper or 'CUSTA FINAS' in nota_upper:
                    lancamento['nota'] = 'CUSTA FINAIS'
                
                elif 'DESARQUIVAMENTO' in nota_upper:
                    lancamento['nota'] = 'DESARQUIVAMENTO'
                
                elif 'OFICIO' in nota_upper or 'OFÍCIO' in nota_upper:
                    lancamento['nota'] = 'OFICIO'
                
                elif 'PROTOCOLO INTEGRADO' in nota_upper or 'PROTOCOLO POSTAL' in nota_upper:
                    lancamento['nota'] = 'PROTOCOLO INTEGRADO OU PROTOCOLO POSTAL'
                
                elif 'RECURSO ESPECIAL' in nota_upper:
                    lancamento['nota'] = 'RECURSO ESPECIAL'
                
                elif 'RECURSO EXTRAORDINARIO' in nota_upper or 'RECURSO EXTRAORDINÁRIO' in nota_upper:
                    lancamento['nota'] = 'RECURSO EXTRAORDINARIO'
                
                elif 'RECURSO INOMINADO' in nota_upper:
                    lancamento['nota'] = 'RECURSO INOMINADO'

                elif 'AGRAVO DE INSTRUMENTO' in nota_upper:
                    lancamento['nota'] = 'AGRAVO DE INSTRUMENTO'
                    
                
                elif 'PAGAMENTO DE CONDENAÇÃO' in nota_upper or 'PAGAMENTO DE CONDENACAO' in nota_upper:
                    remover_registros += 1
                    continue
                
                else:
                    # Default - Registra nota desconhecida
                    # nota_original = lancamento['nota']
                    # nota_normalizada_para_log = normalizar_texto(nota_original)
                    # registrar_nota_desconhecida(nota_original, nota_normalizada_para_log)
                    # if 'CUSTAS DIVERSAS' in nota_upper:
                    #     lancamento['nota'] = "CUSTAS DIVERSAS E TAXAS JUDICIAIS / TRIBUNAL DE JU"
                    # else:
                    #     #lancamento['nota'] = "CUSTAS DIVERSAS E TAXAS JUDICIAIS / TRIBUNAL DE JU"
                    #     print('-------> ENTROU NO ELSE')
                    #     pdb.set_trace()

                    lancamento['nota'] = "CUSTAS DIVERSAS E TAXAS JUDICIAIS / TRIBUNAL DE JU"

                    
            else:
                lancamento['nota'] = "CUSTAS DIVERSAS E TAXAS JUDICIAIS / TRIBUNAL DE JU"

            # Soma o valor no total somente se passou no filtro
            valor_total += valor_float

            historico = lancamento['nota'].strip()
            
            # Se vazio, busca no dicionário de mapeamento pelo numero_integracao
            if not historico:
                historico = historico_map.get(numero_integracao, '')
                if historico:
                    print(f'  ✓ Histórico encontrado no mapeamento: {historico}')
                else:
                    print(f'  ⚠ Histórico não encontrado')
                    pdb.set_trace()
            else:
                print(f'  ✓ Histórico do SPF: {historico}')
            
            # 7. Monta resultado no formato padrão
            registro = {
                'historico': historico,
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
            
            registros.append(registro)
            print(f'  ✓ Lançamento processado com sucesso!')
            
        except Exception as e:
            print(f'  ✗ Erro ao processar lançamento {idx}: {e}')
            traceback.print_exc()
            continue
    
    # Formata valor total com vírgula
    valor_somado = f"{valor_total:.2f}".replace('.', ',')
    
    resultado_final = {
        'contagem': len(registros),
        'valor_somado': valor_somado,
        'registros': registros
    }
    
    print(f'\n✓ Total de lançamentos processados: {len(registros) - remover_registros}/{len(lancamentos)}')
    print(f'✓ Valor total somado: R$ {valor_somado}')
    
    # Salva JSON na pasta planilha
    if _json_path and _planilha_path:
        try:
            # Cria a pasta planilha se não existir
            os.makedirs(_planilha_path, exist_ok=True)
            
            # Salva o JSON
            with open(_json_path, 'w', encoding='utf-8') as f:
                json.dump(resultado_final, f, indent=2, ensure_ascii=False)
            
            print(f'\n✓ JSON salvo em: {_json_path}')
            
        except Exception as e:
            print(f'\n✗ Erro ao salvar JSON: {e}')
            traceback.print_exc()
    
    return resultado_final

def api_buscar_documentos_spf(id_spf: str):
    """Busca documentos de um SPF pelo ID
    
    Args:
        id_spf: ID do SPF
        
    Returns:
        list: Lista de documentos encontrados
        None: Se não encontrar
    """
    try:
        endpoint = f'/api/v2/documento/7/{id_spf}'
        response = api_post(endpoint, data={})
        
        if response and isinstance(response, list):
            return response
        
        return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar documentos do SPF {id_spf}: {e}')
        return None

def api_buscar_documentos_pj(origem: int, pj: int):
    """Busca documentos de um processo pelo PJ.

    Args:
        pj: Identificador do processo (PJ)

    Returns:
        list: Lista de documentos encontrados
        None: Se não encontrar
    """
    try:
        endpoint = f'/api/v2/documento/{origem}/{pj}'
        response = api_post(endpoint, data={})

        if response and isinstance(response, list):
            return response

        if isinstance(response, dict):
            data = response.get('data', response.get('items', None))
            if isinstance(data, list):
                return data

        return None

    except Exception as e:
        print(f'✗ Erro ao buscar documentos do PJ {pj}: {e}')
        return None

def api_baixar_documento(id_ged: int, destino_path: str):
    """Baixa um documento pelo ID GED
    
    Args:
        id_ged: ID do documento no GED
        destino_path: Caminho completo onde o arquivo será salvo
        
    Returns:
        bool: True se sucesso, False se falha
    """
    global API_SESSION, API_TOKEN
    
    # Garante que há um token ativo
    if not API_TOKEN or not API_SESSION:
        print('Token não encontrado. Realizando login...')
        if not api_login():
            return False
    
    try:
        endpoint = f'/api/v2/documento/baixar/{id_ged}'
        url = f'{API_BASE_URL}{endpoint}'
        print(f'GET {url}')
        
        # Headers com Bearer token
        headers = {'Authorization': f'Bearer {API_TOKEN}'}
        
        response = API_SESSION.get(url, headers=headers, timeout=180, stream=True)
        
        if response.status_code == 200:
            # Salva o arquivo
            with open(destino_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f'  ✓ Documento salvo: {os.path.basename(destino_path)}')
            return True
            
        elif response.status_code in [400, 401]:
            print(f'✗ Erro {response.status_code}. Invalidando token e reautenticando...')
            API_TOKEN = None
            API_SESSION = None
            if api_login():
                # Tenta novamente com novo token gerado pelo login
                headers = {'Authorization': f'Bearer {API_TOKEN}'}
                response = API_SESSION.get(url, headers=headers, timeout=180, stream=True)
                if response.status_code == 200:
                    with open(destino_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f'  ✓ Documento salvo: {os.path.basename(destino_path)}')
                    return True
            print(f'✗ Falha na reautenticação')
            return False
        else:
            print(f'✗ Erro ao baixar documento. Status: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'✗ Erro ao baixar documento {id_ged}: {e}')
        traceback.print_exc()
        return False

def processar_documentos_registros(json_path: str = None, output_folder: str = None):
    """Processa documentos de cada registro do JSON
    
    Para cada registro:
    1. Busca documentos do SPF
    2. Baixa cada documento (PDF)
    3. Faz merge dos PDFs
    4. Salva na pasta pdf_merge
    
    Args:
        json_path: Caminho do arquivo JSON (opcional, usa JSON_PATH global se não fornecido)
        output_folder: Pasta base para salvar os PDFs (opcional, usa diretório do script se não fornecido)
    """
    # Usa paths globais se não fornecidos
    _json_path = json_path or JSON_PATH
    _output_folder = output_folder or os.path.dirname(os.path.abspath(__file__))
    
    try:
        print('\n=== Processando documentos dos registros ===')
        
        # Lê o JSON
        with open(_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        registros = data.get('registros', [])
        print(f'✓ Total de registros: {len(registros)}')
        
        # Cria pasta temporária para PDFs
        pdf_temp_folder = os.path.join(_output_folder, 'pdf_temporarios')
        os.makedirs(pdf_temp_folder, exist_ok=True)
        print(f'✓ Pasta temporária: {pdf_temp_folder}')
        
        # Cria pasta para PDFs mesclados
        pdf_merge_folder = PDF_MERGE_PATH if PDF_MERGE_PATH else os.path.join(_output_folder, 'pdf_merge')
        os.makedirs(pdf_merge_folder, exist_ok=True)
        print(f'✓ Pasta de merge: {pdf_merge_folder}')
        
        # Processa cada registro
        for idx, registro in enumerate(registros, start=1):
            try:
                print(f'\n[{idx}/{len(registros)}] Processando registro...')
                
                id_spf = registro.get('id_spf', '')
                integracao = registro.get('pro_numero_de_integracao', '').strip()
                processo = registro.get('pro_numero_do_processo', '').strip()
                debito = registro.get('debito_na_moeda', '').strip()
                
                if not id_spf:
                    print(f'  ⚠ ID SPF não encontrado, pulando...')
                    continue
                
                print(f'  ID SPF: {id_spf}')
                print(f'  Integração: {integracao}')
                print(f'  Processo: {processo}')
                
                # 1. Busca documentos do SPF
                print(f'  → Buscando documentos do SPF {id_spf}...')
                documentos = api_buscar_documentos_spf(id_spf)
                
                if not documentos or len(documentos) == 0:
                    print(f'  ⚠ Nenhum documento encontrado')
                    continue
                
                print(f'  ✓ {len(documentos)} documento(s) encontrado(s)')
                
                # 2. Baixa cada documento
                pdf_paths = []
                for doc_idx, documento in enumerate(documentos, start=1):
                    id_ged = documento.get('id_ged')
                    if not id_ged:
                        print(f'    [{doc_idx}] ⚠ ID GED não encontrado')
                        continue
                    
                    print(f'    [{doc_idx}] Baixando documento ID GED: {id_ged}')
                    
                    # Nome do arquivo temporário
                    pdf_filename = f'{id_spf}_{id_ged}.pdf'
                    pdf_path = os.path.join(pdf_temp_folder, pdf_filename)
                    
                    # Baixa o documento
                    if api_baixar_documento(id_ged, pdf_path):
                        pdf_paths.append(pdf_path)
                    else:
                        print(f'    [{doc_idx}] ✗ Falha ao baixar documento')
                
                if len(pdf_paths) == 0:
                    print(f'  ⚠ Nenhum PDF foi baixado')
                    continue
                
                print(f'  ✓ Total de PDFs baixados: {len(pdf_paths)}')
                
                # 3. Faz merge dos PDFs
                merged_filename = f'{integracao}_{processo}_{debito}.pdf'
                merged_path = os.path.join(pdf_merge_folder, merged_filename)
                
                # Verifica se já existe arquivo com esse nome e adiciona sufixo numérico se necessário
                if os.path.exists(merged_path):
                    contador = 1
                    while True:
                        merged_filename = f'{integracao}_{processo}_{debito}_{contador}.pdf'
                        merged_path = os.path.join(pdf_merge_folder, merged_filename)
                        if not os.path.exists(merged_path):
                            print(f'  ⚠ Arquivo duplicado detectado, criando cópia #{contador}')
                            break
                        contador += 1
                
                print(f'  → Fazendo merge dos PDFs...')
                print(f'    Nome: {merged_filename}')
                
                merger = PdfMerger()
                
                for pdf_path in pdf_paths:
                    merger.append(pdf_path)
                    print(f'      + {os.path.basename(pdf_path)}')
                
                # Salva o PDF mesclado
                merger.write(merged_path)
                merger.close()
                
                print(f'  ✓ PDF mesclado salvo: {merged_filename}')
                
                # 4. Remove arquivos temporários
                for pdf_path in pdf_paths:
                    try:
                        os.unlink(pdf_path)
                    except:
                        pass
                
                print(f'  ✓ Registro processado com sucesso!')
                
            except Exception as e:
                
                print(f'  ✗ Erro ao processar registro {idx}: {e}')
                traceback.print_exc()
                continue
        
        # Limpa pasta temporária
        try:
            shutil.rmtree(pdf_temp_folder)
            print(f'\n✓ Pasta temporária removida')
        except:
            pass
        
        print(f'\n✓ Processamento de documentos concluído!')
        
    except Exception as e:
        print(f'✗ Erro ao processar documentos: {e}')
        traceback.print_exc()
        raise

def api_buscar_processo_tarefa(evento: str, ag_data_hora: str = None, id_tramitacao_inicio: int = 13000000, id_tramitacao_fim: int = 15000000, id_tramitacao_situacao: int = 0, limit: int = 1000):
    """Busca tarefas de processo na API com filtro por evento e data
    
    Args:
        evento: Código/nome do evento a ser filtrado
        ag_data_hora: Data inicial de agendamento no formato YYYY-MM-DD (opcional, padrão: hoje)
        id_tramitacao_inicio: ID mínimo de tramitação para filtro _gte (opcional, padrão: 13000000)
        id_tramitacao_fim: ID máximo de tramitação para filtro _lte (opcional, padrão: 15000000)
        id_tramitacao_situacao: Situação da tramitação (padrão: 0)
        limit: Limite de registros retornados (padrão: 1000)
        
    Returns:
        list: Lista de tarefas encontradas
        None: Se a requisição falhar
        
    Exemplo:
        >>> api_buscar_processo_tarefa("FBA", "2026-03-25", id_tramitacao=13000368, limit=1000)
    """
    try:
        print('\n=== Buscando tarefas de processo na API ===')
        print(f'Evento: {evento}')
        
        # Define data padrão como hoje se não informada
        if ag_data_hora is None:
            ag_data_hora = datetime.now().strftime('%Y-%m-%d')
        
        print(f'ag_data_hora: {ag_data_hora}')
        print(f'id_tramitacao_situacao: {id_tramitacao_situacao}')
        print(f'Limite: {limit} registro(s)')
        
        # Monta os filtros base
        filtros = [
            {
                "evento": {
                    "_eq": evento
                }
            },
            {
                "id_tramitacao": {
                    "_gte": id_tramitacao_inicio,
                    "_lte": id_tramitacao_fim
                }
            },
            {
                "id_tramitacao_situacao": {
                    "_eq": id_tramitacao_situacao
                }
            }
        ]

        # ,
        #     {
        #         "ag_data_hora": {
        #             "_gte": ag_data_hora
        #         }
        #     }
        
        # Adiciona filtro de id_tramitacao se informado
        # if id_tramitacao is not None:
        #     print(f'id_tramitacao >= {id_tramitacao}')
        #     filtros.insert(1, {
        #         "id_tramitacao": {
        #             "_gte": id_tramitacao
        #         }
        #     })
        
        # Monta o body da requisição
        body = {
            "filter": {
                "_and": filtros
            },
            "limit": limit
        }
        
        # Faz a requisição POST
        endpoint = '/api/v2/processo/tarefa'
        print(f'Endpoint: {endpoint}')
        print(f'Body: {json.dumps(body, indent=2)}')
        
        response = api_post(endpoint, data=body)
        
        if response is not None:
            # Verifica se a resposta tem dados
            if isinstance(response, list):
                print(f'✓ {len(response)} tarefa(s) encontrada(s)')
                return response
            elif isinstance(response, dict):
                # Se for dict, pode ter uma propriedade 'data' ou similar
                data = response.get('data', response)
                if isinstance(data, list):
                    print(f'✓ {len(data)} tarefa(s) encontrada(s)')
                    return data
                else:
                    print(f'✓ 1 tarefa encontrada')
                    return [data]
            else:
                print(f'✓ Resposta recebida')
                return response
        else:
            print('✗ Nenhuma resposta recebida')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao buscar tarefas de processo: {e}')
        traceback.print_exc()
        return None

def api_buscar_processo_tarefa_por_data(evento: str, data_inicial: datetime = None, data_fim: datetime = None, id_tramitacao_situacao: int = 0, limit: int = 1000):
    """Busca tarefas de processo na API com filtro por evento e intervalo de datas em data_hora_lan
    
    Args:
        evento: Código/nome do evento a ser filtrado
        data_inicial: Data inicial do filtro (padrão: hoje - 7 dias)
        data_fim: Data final do filtro (padrão: hoje)
        id_tramitacao_situacao: Situação da tramitação (padrão: 0)
        limit: Limite de registros retornados (padrão: 1000)
        
    Returns:
        list: Lista de tarefas encontradas
        None: Se a requisição falhar
    """
    try:
        print('\n=== Buscando tarefas de processo por data na API ===')
        print(f'Evento: {evento}')

        hoje = datetime.now()
        if data_inicial is None:
            data_inicial = hoje - timedelta(days=7)
        if data_fim is None:
            data_fim = hoje

        data_inicial_str = data_inicial.strftime('%Y-%m-%d') if isinstance(data_inicial, datetime) else data_inicial
        data_fim_str = data_fim.strftime('%Y-%m-%d') if isinstance(data_fim, datetime) else data_fim

        print(f'data_inicial: {data_inicial_str}')
        print(f'data_fim: {data_fim_str}')
        print(f'id_tramitacao_situacao: {id_tramitacao_situacao}')
        print(f'Limite: {limit} registro(s)')

        body = {
            "filter": {
                "_and": [
                    {
                        "evento": {
                            "_eq": evento
                        }
                    },
                    {
                        "id_tramitacao_situacao": {
                            "_eq": id_tramitacao_situacao
                        }
                    },
                    {
                        "data_hora_lan": {
                            "_gte": data_inicial_str+'T00:00:00.000-03:00'
                        }
                    },
                    {
                        "data_hora_lan": {
                            "_lte": data_fim_str+'T23:59:59.999-03:00'
                        }
                    }
                ]
            },
            "sort": "data_hora_lan",
            "limit": limit
        }

        endpoint = '/api/v2/processo/tarefa'
        print(f'Endpoint: {endpoint}')
        print(f'Body: {json.dumps(body, indent=2)}')

        response = api_post(endpoint, data=body)

        if response is not None:
            if isinstance(response, list):
                print(f'✓ {len(response)} tarefa(s) encontrada(s)')
                return response
            elif isinstance(response, dict):
                data = response.get('data', response)
                if isinstance(data, list):
                    print(f'✓ {len(data)} tarefa(s) encontrada(s)')
                    return data
                else:
                    print(f'✓ 1 tarefa encontrada')
                    return [data]
            else:
                print(f'✓ Resposta recebida')
                return response
        else:
            print('✗ Nenhuma resposta recebida')
            return None

    except Exception as e:
        print(f'✗ Erro ao buscar tarefas de processo por data: {e}')
        traceback.print_exc()
        return None

def api_buscar_processo_tarefa_filter(filter_data: dict, limit: int = 1000, sort: str = None, offset: int = None):
    """Busca tarefas de processo na API aceitando um filtro completo.

    Args:
        filter_data: Objeto completo do campo "filter" aceito pela API.
            Exemplo: {"_and": [{"evento": {"_eq": "PDE"}}, {"id_tramitacao_situacao": {"_eq": 0}}]}
        limit: Limite de registros retornados (padrão: 1000)
        sort: Campo de ordenação (opcional)
        offset: Offset para paginação (opcional)

    Returns:
        list: Lista de tarefas encontradas
        None: Se a requisição falhar
    """
    try:
        print('\n=== Buscando tarefas de processo com filtro completo ===')

        if not isinstance(filter_data, dict) or not filter_data:
            raise ValueError('filter_data deve ser um dict não vazio contendo o filtro da API')

        body = {
            "filter": filter_data,
            "limit": limit
        }

        if sort:
            body["sort"] = sort
        if offset is not None:
            body["offset"] = offset

        endpoint = '/api/v2/processo/tarefa'
        print(f'Endpoint: {endpoint}')
        print(f'Body: {json.dumps(body, indent=2)}')

        response = api_post(endpoint, data=body)

        if response is not None:
            if isinstance(response, list):
                print(f'✓ {len(response)} tarefa(s) encontrada(s)')
                return response
            elif isinstance(response, dict):
                data = response.get('data', response)
                if isinstance(data, list):
                    print(f'✓ {len(data)} tarefa(s) encontrada(s)')
                    return data
                else:
                    print('✓ 1 tarefa encontrada')
                    return [data]
            else:
                print('✓ Resposta recebida')
                return response
        else:
            print('✗ Nenhuma resposta recebida')
            return None

    except Exception as e:
        print(f'✗ Erro ao buscar tarefas de processo com filtro completo: {e}')
        traceback.print_exc()
        return None

def api_atualizar_tarefa(id_tramitacao: int, id_tramitacao_situacao: int = 1, update_data_hora: str = None, update_usuario: int = 19192):
    """Atualiza a situação de uma tarefa de processo na API
    
    Args:
        id_tramitacao: ID da tramitação a ser atualizada
        id_tramitacao_situacao: Nova situação da tramitação (padrão: 1)
        update_usuario: ID do usuário responsável pela atualização (padrão: 19192)
        update_data_hora: Data e hora da atualização (opcional)
    Returns:
        dict: Resposta da API em caso de sucesso
        None: Se a requisição falhar
        
    Exemplo:
        >>> api_atualizar_tarefa(13000368)
        >>> api_atualizar_tarefa(13000368, id_tramitacao_situacao=2)
    """

    try:
        print(f'\n=== Atualizando tarefa (id_tramitacao={id_tramitacao}) ===')
        
        endpoint = f'/api/v2/processo/tarefa/atualizar/{id_tramitacao}'
        
        body = {
            'update_data_hora': update_data_hora,
            'update_usuario': update_usuario,
            'id_tramitacao_situacao': id_tramitacao_situacao
        }
        
        print(f'Endpoint: {endpoint}')
        print(f'Body: {json.dumps(body, indent=2)}')
        
        response = api_post(endpoint, data=body)
        
        if response is not None:
            print(f'✓ Tarefa {id_tramitacao} atualizada com sucesso (situacao={id_tramitacao_situacao})')
            return response
        else:
            print(f'✗ Falha ao atualizar tarefa {id_tramitacao}')
            return None
            
    except Exception as e:
        print(f'✗ Erro ao atualizar tarefa: {e}')
        traceback.print_exc()
        return None

def api_atualizar_processo(pj: str, fields: dict, update_usuario: int = 1, update_data_hora: str = None):
    """Atualiza dados de um processo identificado pelo PJ
    
    Args:
        pj: Identificador PJ do processo a ser atualizado (obrigatório)
        fields: Dicionário com os campos a serem atualizados (ex: {'variavel_1': 'Administrativo', 'variavel_2': 'Aux RH'})
        update_usuario: ID do usuário responsável pela atualização (padrão: 1)
        update_data_hora: Data e hora da atualização (ISO 8601). Usa o momento atual se não informado.

    Returns:
        dict: Resposta da API em caso de sucesso
        None: Se a requisição falhar

    Exemplo:
        >>> api_atualizar_processo('PJ123', {'variavel_1': 'Administrativo', 'variavel_2': 'Aux RH', 'variavel_3': '1800,00'})
    """
    try:
        print(f'\n=== Atualizando processo (pj={pj}) ===')

        endpoint = f'/api/v2/processo/atualizar/{pj}'

        if update_data_hora is None:
            update_data_hora = datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%S.000-03:00')

        body = {
            'update_data_hora': update_data_hora,
            'update_usuario': update_usuario,
            **fields,
        }

        print(f'Endpoint: {endpoint}')
        print(f'Body: {json.dumps(body, indent=2)}')

        response = api_post(endpoint, data=body)

        if response is not None:
            print(f'✓ Processo {pj} atualizado com sucesso')
            return response
        else:
            print(f'✗ Falha ao atualizar processo {pj}')
            return None

    except Exception as e:
        print(f'✗ Erro ao atualizar processo: {e}')
        traceback.print_exc()
        return None

