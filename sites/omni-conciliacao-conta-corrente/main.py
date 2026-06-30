#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/omni-conciliacao-conta-corrente/main.py

| projeto: automacao-python
| data: 2026-05-11
| autor: Marcelo Amancio
"""
import pdb
import re
import time
import os
import sys
import json
import shutil
import pyotp
from datetime import datetime, timedelta
import traceback
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

# Adiciona o caminho dos módulos
sys.path.append('C:\\www\\automacao')

# Importa funções do módulo CPJ API
from cpj_api import (
    set_api_credentials,
    api_login,
    api_logout,
    api_buscar_processo_tarefa,
    api_buscar_processo_por_pj,
    api_buscar_processo_por_ficha,
    api_atualizar_tarefa,
    api_buscar_processo_tarefa_por_data,
    api_buscar_lancamentos,
    api_buscar_lancamentos_filtro,
    api_buscar_spf,
    sanitizar_documento
)

import PATHS

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Configurações da API
API_BASE_URL = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
API_LOGIN = 'api'
API_PASSWORD = '2025'

# Configurações do sistema web OMNI
WEB_URL = WEB_URL_INICIAL = 'https://www.omnifacil.com.br/'
WEB_LOGIN = 'usuario'
WEB_PASSWORD = 'senha'

# Caminhos
BASE_PATH = PATHS.project_path()
DRIVER_PATH = PATHS.driver_path()
COOKIES_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.json')

# URL da página de processo a ser visitada após login
PAGINA_PROCESSO_URL = 'https://www.omnifacil.com.br/pls/webdad/pck_sj_processo_juridico.consulta_acao?p_cod_acao_omni=3572019&p_nome=2614MARCELO&p_emp=2614&p_ide=|ID_SESSAO|&p_cpf=06050694680'

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Caminho do arquivo de tarefas JSON
TAREFAS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarefas.json')

# URL personalizada para acessar o processo usando o número de integração (pasta)
PAGINA_PROCESSO_URL_PERSONALIZADA = (
    'https://www.omnifacil.com.br/pls/webdad/pck_sj_processo_juridico.consulta_acao'
    '?p_cod_acao_omni=|PASTA_NUMERO_INTEGRACAO|'
    '&p_nome=2614MARCELO&p_emp=2614&p_ide=|ID_SESSAO|&p_cpf=06050694680'
)

# Eventos a processar para conciliação de conta corrente
EVENTOS = ['CCR']

ID_SESSAO = None


def atualizar_proxima_execucao(horas=2):
    """Atualiza o campo proxima_execucao no config.json para daqui a N horas."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config_data['proxima_execucao'] = (datetime.now() + timedelta(hours=horas)).strftime('%Y-%m-%dT%H:%M:%S')
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f'✓ proxima_execucao atualizada para: {config_data["proxima_execucao"]}')
    except Exception as e:
        print(f'✗ Erro ao atualizar config.json: {e}')


# Carrega configurações do config.json se existir
if os.path.exists(CONFIG_PATH):

    print("Carregando configurações de config.json...")

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    WEB_URL = config.get('web_url', WEB_URL)
    WEB_LOGIN = config.get('web_login', WEB_LOGIN)
    WEB_PASSWORD = config.get('web_password', WEB_PASSWORD)
    T2FA_SECRET = config.get('2fa_secret', None)
    DATA_INICIAL = config.get('data_inicial', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    DATA_FIM = config.get('data_final', datetime.now().strftime('%Y-%m-%d'))

    print(f"Configurações carregadas:")
    print(f"  - URL: {WEB_URL}")
    print(f"  - Login: {WEB_LOGIN}")
    print(f"  - Data Inicial: {DATA_INICIAL}")
    print(f"  - Data Final: {DATA_FIM}")

# Configura as credenciais da API no módulo CPJ
set_api_credentials(
    base_url=API_BASE_URL,
    login=API_LOGIN,
    password=API_PASSWORD
)

print('\n' + '='*70)
print('OMNI - Conciliação Conta Corrente - Automação')
print('='*70)

# ============================================================================
# FUNÇÕES WEB (Selenium)
# ============================================================================

def carregar_cookies(driver):
    """Carrega cookies do arquivo cookies.json no navegador"""
    try:
        if not os.path.exists(COOKIES_JSON_PATH):
            print(f'⚠ Arquivo de cookies não encontrado: {COOKIES_JSON_PATH}')
            return False

        with open(COOKIES_JSON_PATH, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        if not cookies:
            return False

        print(f'\nCarregando {len(cookies)} cookie(s) de {COOKIES_JSON_PATH}...')

        SAMESIDE_MAP = {
            'no_restriction': 'None',
            'lax': 'Lax',
            'strict': 'Strict',
        }

        adicionados = 0
        for cookie in cookies:
            selenium_cookie = {
                'name': cookie['name'],
                'value': cookie['value'],
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', False),
            }
            if 'domain' in cookie:
                selenium_cookie['domain'] = cookie['domain']
            if 'expirationDate' in cookie:
                selenium_cookie['expiry'] = int(cookie['expirationDate'])
            sameSite = SAMESIDE_MAP.get(cookie.get('sameSite', '').lower())
            if sameSite:
                selenium_cookie['sameSite'] = sameSite

            try:
                driver.add_cookie(selenium_cookie)
                adicionados += 1
            except Exception as e:
                print(f'  ⚠ Cookie ignorado ({cookie["name"]}): {e}')

        print(f'✓ {adicionados}/{len(cookies)} cookie(s) carregado(s) com sucesso!')

        print(f'\nAcessando página de processo...')
        driver.get(WEB_URL_INICIAL)

        url = driver.current_url
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        global ID_SESSAO
        ID_SESSAO = params.get('p_ide', [''])[0]
        driver.get(PAGINA_PROCESSO_URL.replace('|ID_SESSAO|', ID_SESSAO))

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'td_despesa'))
            )
            print(f'✓ Sessão ativa via cookies!')
            return True
        except Exception:
            print(f'⚠ Cookies insuficientes, será necessário login.')
            return False

    except Exception as e:
        print(f'✗ Erro ao carregar cookies: {e}')
        traceback.print_exc()
        return False


def open_chrome_browser():
    """Abre o navegador Chrome usando Selenium"""
    try:
        print('\nAbrindo navegador Chrome...')

        chrome_options = Options()
        chrome_options.add_argument('--window-size=1200,800')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors')

        try:
            print('Tentando usar ChromeDriver do PATH do sistema...')
            driver = webdriver.Chrome(options=chrome_options)
            print('✓ Chrome aberto com sucesso usando ChromeDriver do PATH!')
            return driver
        except Exception as path_error:
            print(f'⚠ ChromeDriver não encontrado no PATH: {path_error}')

        try:
            print('Tentando instalar ChromeDriver automaticamente com webdriver-manager...')
            cache_path = os.path.join(os.path.expanduser('~'), '.wdm')
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path)
                    print('✓ Cache limpo, baixando ChromeDriver novamente...')
                except Exception as cache_error:
                    print(f'⚠ Erro ao limpar cache: {cache_error}')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print('✓ Chrome aberto com sucesso usando webdriver-manager!')
            return driver

        except Exception as manager_error:
            print(f'✗ Erro com webdriver-manager: {manager_error}')

        raise Exception('Não foi possível inicializar o ChromeDriver')

    except Exception as e:
        print(f'\n✗ ERRO CRÍTICO: Não foi possível abrir o Chrome')
        print(f'Erro: {e}')
        traceback.print_exc()
        raise


def login_web_sistema(driver):
    """Faz login no sistema web OMNI"""
    try:
        print('\n' + '='*70)
        print('REALIZANDO LOGIN NO SISTEMA WEB')
        print('='*70)

        print(f'\nAcessando {WEB_URL}...')
        driver.get(WEB_URL)
        driver.delete_all_cookies()
        print('✓ Página carregada')

        wait = WebDriverWait(driver, 10)

        print('Preenchendo campo de login...')
        login_input = wait.until(EC.presence_of_element_located((By.ID, 'p-nome')))
        login_input.clear()
        login_input.send_keys(WEB_LOGIN)
        print(f'✓ Login digitado: {WEB_LOGIN}')

        print('Preenchendo campo de senha...')
        senha_input = driver.find_element(By.ID, 'p-senha')
        senha_input.clear()
        senha_input.send_keys(WEB_PASSWORD)
        print('✓ Senha digitada')

        print('Clicando no botão de login...')
        btn_login = driver.find_element(By.ID, 'btn-conectar')
        btn_login.click()
        print('✓ Botão de login clicado!')

        print('Aguardando campo MFA ficar interativo...')
        tentativa = 1
        while True:
            try:
                mfa_input = driver.find_element(By.ID, 'p-codigo-mfa')
                mfa_input.click()
                mfa_input.clear()
                print(f'✓ Campo MFA interativo na tentativa {tentativa}!')
                break
            except Exception:
                print(f'  Tentativa {tentativa}: campo MFA ainda não interativo, clicando novamente em btn-conectar...')
                try:
                    try:
                        driver.find_element(By.XPATH, "//button[contains(text(), 'ok')]").click()
                    except Exception:
                        pass
                    driver.find_element(By.ID, 'btn-conectar').click()
                except Exception:
                    pass
                time.sleep(2)
                tentativa += 1

        codigo_mfa = pyotp.TOTP(T2FA_SECRET).now() if T2FA_SECRET else input('\n>>> Digite o código 2FA/MFA e pressione Enter: ').strip()
        mfa_input.send_keys(codigo_mfa)
        print(f'✓ Código MFA inserido: {codigo_mfa}')

        try:
            time.sleep(2)
            botao_enviar = driver.find_element(By.ID, "bt-enviar-mfa")
            webdriver.ActionChains(driver).move_to_element(botao_enviar).click().perform()
        except Exception:
            pass

        time.sleep(5)
        print('✓ Login realizado com sucesso!')

        try:
            cookies = driver.get_cookies()
            with open(COOKIES_JSON_PATH, 'w', encoding='utf-8') as _f:
                json.dump(cookies, _f, ensure_ascii=False, indent=2)
            print(f'✓ {len(cookies)} cookie(s) salvos em cookies.json')
        except Exception as _e:
            print(f'⚠ Erro ao salvar cookies: {_e}')

        print('='*70)
        return True

    except Exception as e:
        print(f'\n✗ Erro ao fazer login: {e}')
        traceback.print_exc()
        return False


# ============================================================================
# FUNÇÕES DE CONCILIAÇÃO
# ============================================================================

def registra_erro(tarefa, mensagem):
    """Registra um erro na conciliação no arquivo erros_conciliacao.json"""
    erros_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'erros_conciliacao.json')
    erros_lista = []

    if os.path.exists(erros_json_path):
        try:
            with open(erros_json_path, 'r', encoding='utf-8') as _f:
                conteudo = _f.read().strip()
                if conteudo:
                    erros_lista = json.loads(conteudo)
        except (json.JSONDecodeError, ValueError):
            erros_lista = []

    id_tramitacao = tarefa.get('id_tramitacao')
    erros_lista = [t for t in erros_lista if t.get('id_tarefa') != id_tramitacao]
    erros_lista.append({
        'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tarefa': tarefa,
        'mensagem': mensagem,
        'id_tarefa': id_tramitacao
    })

    with open(erros_json_path, 'w', encoding='utf-8') as _f:
        json.dump(erros_lista, _f, ensure_ascii=False, indent=2)

    print(f'  ✓ Registrado em erros_conciliacao.json ({len(erros_lista)} total)')
    return False


def processar_conciliacao(driver, tarefa):
    """Processa a conciliação de conta corrente para a tarefa informada"""
    try:
        pasta = tarefa['pasta_numero_integracao']
        url = PAGINA_PROCESSO_URL_PERSONALIZADA.replace('|PASTA_NUMERO_INTEGRACAO|', str(pasta)).replace('|ID_SESSAO|', ID_SESSAO)

        print(f'  Acessando: {url}')
        driver.get(url)
        time.sleep(1)

        wait = WebDriverWait(driver, 10)

        # TODO: implementar a lógica específica de conciliação de conta corrente
        # Exemplo: verificar saldo, comparar lançamentos, etc.

        print(f'  ✓ Conciliação processada para pasta={pasta}')
        return True

    except Exception as e:
        print(f'  ✗ Erro ao processar conciliação: {e}')
        traceback.print_exc()
        registra_erro(tarefa, str(e))
        return False


def normalizar_texto(texto: str, somente_alfanumerico: bool = True) -> str:
    if not texto:
        return ""
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[\r\n\t]+', ' ', texto)
    if somente_alfanumerico:
        texto = re.sub(r'[^a-zA-Z0-9 ]+', '', texto)
    else:
        texto = re.sub(r'[^\w\s\.\,\-\/]+', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa o fluxo completo da automação de conciliação de conta corrente"""
    driver = None

    try:
        print('\n' + '='*70)
        print('INICIANDO AUTOMAÇÃO - Conciliação Conta Corrente')
        print('='*70)

        # ====================================================================
        # ETAPA 1: Autenticação na API CPJ
        # ====================================================================
        print('\n[ETAPA 1/4] Autenticação na API CPJ')
        print('-'*70)

        token = api_login()

        if not token:
            print('✗ Falha ao autenticar na API. Abortando processo...')
            return

        print('✓ Autenticação na API concluída com sucesso!')

        # ====================================================================
        # ETAPA 2: Buscar lançamentos de conta corrente (CC 36, 1394, 1373)
        # ====================================================================
        print('\n[ETAPA 2/4] Buscar lançamentos de conta corrente')
        print('-'*70)

        if os.path.exists(TAREFAS_JSON_PATH):
            os.remove(TAREFAS_JSON_PATH)
            print(f'✓ Arquivo anterior removido: tarefas.json')

        CONTAS_CORRENTE = "36, 1394, 1373"
        todos_lancamentos = []
        resumo_cc = {}

        _dt_inicio = datetime.strptime(DATA_INICIAL, '%Y-%m-%d')
        _dt_fim = datetime.strptime(DATA_FIM, '%Y-%m-%d')

        #for numero_cc in CONTAS_CORRENTE:
        print(f'\nBuscando lançamentos — CC {CONTAS_CORRENTE}...')
        lancamentos_cc = []
        ids_vistos = set()

        _janela_inicio = _dt_inicio
        lancamentos_analisados = []
        
        while _janela_inicio <= _dt_fim:
            _janela_fim = min(_janela_inicio + timedelta(days=1), _dt_fim)

            print(f'  [{CONTAS_CORRENTE}] {_janela_inicio.strftime("%Y-%m-%d")} → {_janela_fim.strftime("%Y-%m-%d")}...')

            _resultado = api_buscar_lancamentos(
                data_inicial=_janela_inicio,
                data_final=_janela_fim,
                numero_cc=CONTAS_CORRENTE,
                documento_spf = False,
                limit=5000
            )
            
            _janela_inicio = _janela_fim + timedelta(days=1)

            #pdb.set_trace()  # Debug: Verificar resultado bruto da API para lançamentos de conta corrente
            
            if _resultado:
                
                _total_resultado = len(_resultado)
                for _idx_resultado, item in enumerate(_resultado, 1):
                    print ('='*70)
                    print(f'\033[92m  [{_idx_resultado}/{_total_resultado}] {_idx_resultado/_total_resultado*100:.1f}%\033[0m')
                    print ('='*70)
                    _id = item.get('id') or item.get('id_lancamento') or id(item)
                    if _id not in ids_vistos:
                        ids_vistos.add(_id)
                        ficha = sanitizar_documento(item.get('ficha', ''))
                        if ficha:
                            _filtros = [
                                {"numero_cc": {"_in": CONTAS_CORRENTE}},
                                {"ficha": {"_eq": ficha}},
                                {"dc": {"_eq": 1}},
                            ]
                            _resultado_ficha = api_buscar_lancamentos_filtro(filtros=_filtros)
                            if _resultado_ficha and isinstance(_resultado_ficha, list) and len(_resultado_ficha) > 0:
                                item['lancamentos_ficha'] = _resultado_ficha

                                valor_recebido = item['valor_original_total'] = sum(
                                    lf.get('valor_original', 0) or 0 for lf in _resultado_ficha
                                )

                                print(f'      ✓ Ficha {ficha} → dc=1 → {len(_resultado_ficha)} lançamento(s) → total={item["valor_original_total"]}')

                            else:
                                print(f'      ⚠ Ficha {ficha} → dc=1 → nenhum lançamento encontrado')
                                valor_recebido = 0

                            processos = api_buscar_processo_por_ficha(ficha)
                            if processos and isinstance(processos, list) and len(processos) > 0:
                                item['dados_processo'] = processos[-1]
                                print(f'      ✓ Ficha {ficha} → pasta={processos[-1].get("numero_integracao", "")}')

                                _materia_cod = processos[-1].get('materia')
                                match _materia_cod:
                                    case 1:
                                        item['dados_processo']['materia_descricao'] = 'CÍVEL - FÓRUM'
                                        item['dados_processo']['materia_sigla'] = 'CIV'
                                    case 2:
                                        item['dados_processo']['materia_descricao'] = 'CÍVEL - JUIZADO ESPECIAL'
                                        item['dados_processo']['materia_sigla'] = 'JEC'
                                    case 3:
                                        item['dados_processo']['materia_descricao'] = 'Trabalhista'
                                        item['dados_processo']['materia_sigla'] = 'TRA'
                                    case 4:
                                        item['dados_processo']['materia_descricao'] = 'ÓRGÃOS ADMINISTRATIVOS'
                                    case 5:
                                        item['dados_processo']['materia_descricao'] = 'Tributário'
                                    case 6:
                                        item['dados_processo']['materia_descricao'] = 'Criminal'
                                    case 7:
                                        item['dados_processo']['materia_descricao'] = 'Empresarial'
                                    case 9:
                                        item['dados_processo']['materia_descricao'] = 'TRATATIVA DE ACORDO'
                                    case 10:
                                        item['dados_processo']['materia_descricao'] = 'Consultoria'
                                    case 11:
                                        item['dados_processo']['materia_descricao'] = 'DELEGACIA ESTADUAL'
                                    case 12:
                                        item['dados_processo']['materia_descricao'] = 'TREINAMENTO'
                                    case 13:
                                        item['dados_processo']['materia_descricao'] = 'Tribunal de Justiça'
                                    case 14:
                                        item['dados_processo']['materia_descricao'] = 'CEJUSC'
                                        item['dados_processo']['materia_sigla'] = 'CEJUSC'
                                    case 15:
                                        item['dados_processo']['materia_descricao'] = 'Faturamentos'
                                    case 16:
                                        item['dados_processo']['materia_descricao'] = 'teste Helen'
                                    case 17:
                                        item['dados_processo']['materia_descricao'] = 'Execução Fiscal IPVA'
                                    case 18:
                                        item['dados_processo']['materia_descricao'] = 'ALVARÁ JUDICIAL'
                                    case _:
                                        item['dados_processo']['materia_descricao'] = f'DESCONHECIDO ({_materia_cod})'

                            else:
                                print(f'      ⚠ Ficha {ficha} → nenhum processo encontrado')
                                continue

                            _tabela_valores_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'omni-pde-fsp-trc', 'tabela_valores.json')
                            _tabela_valores = {}
                            try:
                                with open(_tabela_valores_path, 'r', encoding='utf-8') as _f:
                                    _tabela_valores = json.load(_f)
                                print(f'      ✓ tabela_valores.json carregada ({len(_tabela_valores)} entradas)')
                            except Exception as _e:
                                print(f'      ⚠ Erro ao carregar tabela_valores.json: {_e}')
   
                            contrato_cliente = item['dados_processo']['contrato_cliente']

                            # Em andamento - 1
                            # Sentença favorável - 2
                            # Sentença desfavorável - 3
                            # Acordo pré sentença - 4
                            # Acordo pós sentença - 5
                            # Desistência - 6
                            # Extinção sem resolução de mérito - 7
                            resultado_situacao = item['dados_processo']['resultado_situacao'] 

                            if resultado_situacao == 1:
                                continue

                            numero_integracao = item['dados_processo']['numero_integracao']
                            #pj = item['dados_processo']['pj']

                            item['valor_tabela_base'] = 0
                            item['conciliacao_errada'] = 'sim'
                            item['valor_divergencia'] = ''
                            item['a_fazer'] = f'Verificar numero de contrato cliente incorreto'
                            item['motivo_conciliacao_errada'] = f'Sem conciliarão possível, contrato cliente {contrato_cliente} não tem tabela de valores definida para comparação'

                            if '35' in str(contrato_cliente):
                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               

                                if resultado_situacao == 1:

                                    if valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'   
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 35_1, quais campos usar para comparação, etc

                                elif resultado_situacao == 3:

                                    if valor_recebido < _soma_3_primeiros:
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                
                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'   
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                elif resultado_situacao == 2:
                                    valor_exito = next(
                                            (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                            None
                                        )
                                    if valor_recebido < (_soma_3_primeiros + valor_exito):
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_exito) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de exito R$ {valor_exito} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == (_soma_3_primeiros + valor_exito):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                
                                    else:
                                        pdb.set_trace() #debug 35_2, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 4:

                                    #35 nao tem acordo pre sentença, mas tem valor de acordo pre sentença na tabela de valores, entao considerar que valor de acordo pre sentença deve ser lançado para complementar valor recebido, e comparar valor recebido com soma de Contestacao, Sentenca, Transito + valor de acordo pre sentença   

                                    if valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'   
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 35_4, quais campos usar para comparação, etc

                                elif resultado_situacao == 6:

                                    if valor_recebido < _soma_3_primeiros:
                                        
                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Esse caso é de desistência...'
                                        item['motivo_conciliacao_errada'] = f'Valor de desistencia não definido.'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 3563, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 7:
                                   
                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = 0
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito, mas valor recebido está igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), então verificar detalhes do processo para entender o cenário'
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas caso é de extinção sem resolução de mérito'
                                    print(f'      ✓ Conciliação indefinida: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                else:
                                    pdb.set_trace() #debug 35_0, quais campos usar para comparação, etc

                            elif '736' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               

                                if resultado_situacao == 1:
                                    if valor_recebido == _soma_3_primeiros:
                                        
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 736_1, quais campos usar para comparação, etc

                                elif resultado_situacao == 2:
                                    valor_exito = next(
                                            (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                            None
                                        )
                                    if valor_recebido < (_soma_3_primeiros + valor_exito):
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_exito) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de exito R$ {valor_exito} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    else:
                                        pdb.set_trace() #debug 736_2, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 3:   

                                    if valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0  
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')       
                                    

                                    elif valor_recebido < _soma_3_primeiros:
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 736_3, quais campos usar para comparação, etc

                                elif resultado_situacao == 7:

                                    #if valor_recebido < _soma_3_primeiros:
                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito...'
                                    item['motivo_conciliacao_errada'] = f'Valor de extinção sem resolução de mérito não definido.'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                            
                                
                                else:
                                    pdb.set_trace() #debug 736_0, quais campos usar para comparação, etc 

                            elif '737' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               

                                if ficha == '950317':
                                    pdb.set_trace() #debug específico para ficha 924827, contrato cliente 737, verificar quais campos usar para comparação, etc

                                if resultado_situacao == 1:

                                    if valor_recebido == _soma_3_primeiros:
                                    
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'   
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 737_1, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 2:
                                    valor_exito = next(
                                            (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                            None
                                        )
                                    if valor_recebido < (_soma_3_primeiros + valor_exito):
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_exito) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de exito R$ {valor_exito} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == (_soma_3_primeiros + valor_exito):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 737_2, quais campos usar para comparação, etc

                                elif resultado_situacao == 3:

                                    if valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')       
                                    
                                    else:
                                        pdb.set_trace() #debug 737_3, quais campos usar para comparação, etc

                                elif resultado_situacao == 5:
                                    valor_acordo_pos_sentenca = next(
                                            (item['ACORDO_POS'] for item in _dados_tabela if 'ACORDO_POS' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pos_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de acordo pós sentença R$ {valor_acordo_pos_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_acordo_pos_sentenca)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contest    acao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 737_5, quais campos usar para comparação, etc

                                elif resultado_situacao == 7:

                                    #nao da direito a exito e nem acordos

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = 0
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito, mas valor recebido está igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), então verificar detalhes do processo para entender o cenário'
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas caso é de extinção sem resolução de mérito'
                                    print(f'      ✓ Conciliação indefinida: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                               
                                else:
                                    pdb.set_trace() #debug 737_0, quais campos usar para comparação, etc  

                            elif '740' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')

                                if resultado_situacao == 5:
                                    
                                    valor_acordo_pos_sentenca = next(
                                            (item['ACORDO_POS'] for item in _dados_tabela if 'ACORDO_POS' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pos_sentenca):
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pos_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de acordo pós sentença R$ {valor_acordo_pos_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_acordo_pos_sentenca)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 740_2, quais campos usar para comparação, etc        

                            elif '741' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               


                                if resultado_situacao == 1 or resultado_situacao == 3:

                                    if valor_recebido == _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 741_1, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 2:
                                    valor_exito = next(
                                            (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                            None
                                        )
                                    if valor_recebido < (_soma_3_primeiros + valor_exito):
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_exito) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de exito R$ {valor_exito} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == (_soma_3_primeiros + valor_exito): 
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito}), mas verificar se valor de êxito foi lançado corretamente'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')   

                                    elif valor_recebido > (_soma_3_primeiros + valor_exito):
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_exito)
                                        item['a_fazer'] = f'Revisar lançamento de valor de êxito, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                    
                                    else:
                                        pdb.set_trace() #debug 741_2, quais campos usar para comparação, etc

                                elif resultado_situacao == 5:   

                                    valor_acordo_pos_sentenca = next(
                                            (item['ACORDO_POS'] for item in _dados_tabela if 'ACORDO_POS' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pos_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de acordo pós sentença R$ {valor_acordo_pos_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_acordo_pos_sentenca)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                elif resultado_situacao == 7:
                                    #nao da direito a exito e nem acordos

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = 0
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito, mas valor recebido está igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), então verificar detalhes do processo para entender o cenário'
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas caso é de extinção sem resolução de mérito'
                                    print(f'      ✓ Conciliação indefinida: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                else:
                                    pdb.set_trace() #debug 741_0, quais campos usar para comparação, etc  

                            elif '739' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               


                                if resultado_situacao == 1 or resultado_situacao == 3:

                                    if valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    

                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    

                                    else:
                                        pdb.set_trace() #debug 739_1, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 2:

                                    valor_exito = next(
                                            (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                            None
                                        )
                                    
                                    if valor_recebido < (_soma_3_primeiros + valor_exito):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_exito) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de exito R$ {valor_exito} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == (_soma_3_primeiros + valor_exito):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_exito):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_exito)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de êxito ({valor_exito})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    else:
                                        pdb.set_trace() #debug 739_2, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 4:
                                    valor_acordo_pre_sentenca = next(
                                            (item['ACORDO_PRE'] for item in _dados_tabela if 'ACORDO_PRE' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pre_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pre_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pre_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de acordo pré sentença R$ {valor_acordo_pre_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_acordo_pre_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_acordo_pre_sentenca)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 739_4, quais campos usar para comparação, etc
                                
                                elif resultado_situacao == 5:

                                    valor_acordo_pos_sentenca = next(
                                            (item['ACORDO_POS'] for item in _dados_tabela if 'ACORDO_POS' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pos_sentenca):
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pos_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valor de acordo pós sentença R$ {valor_acordo_pos_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    else:
                                        pdb.set_trace() #debug 739_5, quais campos usar para comparação, etc

                                elif resultado_situacao == 6:
                                    valor_acordo_pre_sentenca = next(
                                            (item['ACORDO_PRE'] for item in _dados_tabela if 'ACORDO_PRE' in item),
                                            None
                                        )
                                    
                                    if valor_recebido == (_soma_3_primeiros + valor_acordo_pre_sentenca + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido < (_soma_3_primeiros + valor_acordo_pre_sentenca + valor_acordo_pos_sentenca):

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = (_soma_3_primeiros + valor_acordo_pre_sentenca + valor_acordo_pos_sentenca) - valor_recebido
                                        item['a_fazer'] = f'Lançar valores de acordo pré sentença R$ {valor_acordo_pre_sentenca} e pós sentença R$ {valor_acordo_pos_sentenca} para complementar valor recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > (_soma_3_primeiros + valor_acordo_pre_sentenca + valor_acordo_pos_sentenca):
                                        
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros + valor_acordo_pre_sentenca + valor_acordo_pos_sentenca)
                                        item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pré sentença ({valor_acordo_pre_sentenca}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                elif resultado_situacao == 7:

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito...'
                                    item['motivo_conciliacao_errada'] = f'Valor de extinção sem resolução de mérito não definido.'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                
                                else:
                                    pdb.set_trace() #debug 739_0, quais campos usar para comparação, etc  

                            elif '742' in str(contrato_cliente):    
                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')

                                if resultado_situacao == 2:
                                    #nao permite lancamento de valor de exito
                                    # valor_exito = next(
                                    #         (item['EXITO'] for item in _dados_tabela if 'EXITO' in item),
                                    #         None
                                    #     )
                                    if valor_recebido < _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Lançar valor referente a Contestacao, Sentenca ou Transito para complementar valor recebido, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == _soma_3_primeiros: 
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas verificar se valor de êxito foi lançado corretamente'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas sem valor de êxito lançado'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')   

                                    elif valor_recebido > _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - (_soma_3_primeiros)
                                        item['a_fazer'] = f'Revisar lançamento, pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    else:
                                        pdb.set_trace() #debug 742_2, quais campos usar para comparação, etc

                                elif resultado_situacao == 7:

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito...'
                                    item['motivo_conciliacao_errada'] = f'Valor de extinção sem resolução de mérito não definido.'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                elif resultado_situacao == 5:

                                    if valor_recebido == (_soma_3_primeiros):

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) + valor de acordo pós sentença ({valor_acordo_pos_sentenca})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 742_5, quais campos usar para comparação, etc

                                else:
                                    pdb.set_trace() #debug 742_0, quais campos usar para comparação, etc 

                            elif '743' in str(contrato_cliente):
                                #é CDC nao prevê lancamento de valor de recebimento de PERDA, EXITO, ACORDO POS OU ACORDO PRE 

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)

                                if resultado_situacao == 1:

                                    if valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Valor recebido está divergente do esperado com base na tabela de valores (R$ {_dados_tabela[:3]})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')   
                                    
                                    else:
                                        pdb.set_trace() #743_1, quais campos usar para comparação, etc

                                elif resultado_situacao == 2:

                                    
                                    if valor_recebido < _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Lançar valor para complementar valor recebido de {valor_recebido}, pois está menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas verificar se valor de êxito foi lançado corretamente'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas sem valor de êxito lançado'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Revisar pois valor recebido ({valor_recebido}) é maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 743_2, quais campos usar para comparação, etc

                                elif resultado_situacao == 3:

                                    if valor_recebido == _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')       
                                    
                                    elif valor_recebido < _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido > _soma_3_primeiros:

                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                        item['a_fazer'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), revisar lançamentos para identificar origem de valor a mais recebido'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 743_3, quais campos usar para comparação, etc

                                elif resultado_situacao == 5:
                                   
                                    if valor_recebido == _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'nao'
                                        item['valor_divergencia'] = 0   
                                        item['a_fazer'] = f'N/A'
                                        item['motivo_conciliacao_errada'] = f'N/A'
                                        print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    else:
                                        pdb.set_trace() #debug 3, quais campos usar para comparação, etc

                                elif resultado_situacao == 7:
                                    
                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] = 0
                                    item['a_fazer'] = f'Esse caso é de extinção sem resolução de mérito, mas valor recebido está igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), então verificar detalhes do processo para entender o cenário'
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}), mas caso é de extinção sem resolução de mérito'
                                    print(f'      ✓ Conciliação indefinida: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                else:
                                    pdb.set_trace() #743_0, analisar resultado situacao para entender qual é o cenário de conciliação errada, quais campos usar para comparação, etc
                                                       
                            elif contrato_cliente is None or '809' in str(contrato_cliente) or '9' in str(contrato_cliente)  or '0' in str(contrato_cliente) or '1' in str(contrato_cliente) or '2' in str(contrato_cliente) or '5' in str(contrato_cliente) or '6' in str(contrato_cliente) or '8' in str(contrato_cliente) or '4' in str(contrato_cliente):
                                continue

                                if resultado_situacao == 2:
                                    pdb.set_trace() #debug 5
                                
                                elif resultado_situacao == 1:
                                    if valor_recebido < _soma_3_primeiros:
                                        item['conciliacao_errada'] = 'sim'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Aguardar sentença, mas já sinalizar que valor recebido está divergente do esperado com base na tabela de valores (R$ {_soma_3_primeiros})'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')
                    
                            elif '829' in str(contrato_cliente):

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')
                                _sigla_contrato = '_' + item['dados_processo']['materia_sigla']
                                _dados_tabela = _tabela_valores.get(str(contrato_cliente)+_sigla_contrato, {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')

                                if valor_recebido == _soma_3_primeiros:

                                    item['conciliacao_errada'] = 'nao'
                                    item['valor_divergencia'] = 0   
                                    item['a_fazer'] = f'Valor recebido está correto, conforme soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})' 
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                    print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                
                                elif valor_recebido < _soma_3_primeiros: 

                                    item['conciliacao_errada'] = 'sim'
                                    item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                    item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                    item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de Contestacao, Sentenca e Transito ({_soma_3_primeiros})'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                else:
                                    pdb.set_trace() #debug 829_0, quais campos usar para comparação, etc

                            else:
                                
                                print(f'      ✓ Contrato cliente: {contrato_cliente} PROGRAMAR')
                                pdb.set_trace() #debug Contrato cliente:  PROGRAMAR



                            lancamentos_analisados.append(item)
        
        print(f'  ✓ {len(lancamentos_analisados)} lançamento(s) no total')

        _output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
        os.makedirs(_output_dir, exist_ok=True)
        _hoje = datetime.now().strftime('%d-%m-%Y')
        _dt_ini_br = datetime.strptime(DATA_INICIAL, '%Y-%m-%d').strftime('%d-%m-%Y')
        _dt_fim_br = datetime.strptime(DATA_FIM, '%Y-%m-%d').strftime('%d-%m-%Y')
        _nome_arquivo = f"de_{_dt_ini_br}_ate_{_dt_fim_br}_______processado_{_hoje}.json"
        _output_path = os.path.join(_output_dir, _nome_arquivo)
        with open(_output_path, 'w', encoding='utf-8') as _f:
            json.dump(lancamentos_analisados, _f, ensure_ascii=False, indent=2, default=str)
        print(f'  ✓ Resultados salvos em: {_output_path}')

        pdb.set_trace() #debug depois remover

        atualizar_proxima_execucao(horas=168)

    except Exception as e:
        print(f'\n✗ ERRO CRÍTICO na automação: {e}')
        traceback.print_exc()


if __name__ == '__main__':
    main()
