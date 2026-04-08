#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/omni-pde-fsp-trc/main.py

| projeto: automacao-python
| data: 2026-03-06
| autor: Marcelo Amancio
"""
import re
import time
import os
import sys
import json
import pdb
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
    api_atualizar_tarefa,
    api_buscar_processo_tarefa_por_data
)

import PATHS

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Configurações da API
API_BASE_URL = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
API_LOGIN = 'api'
API_PASSWORD = '2025'

# Configurações do sistema web OMNI-PDE-FSP-TRC
WEB_URL = WEB_URL_INICIAL = 'https://www.omnifacil.com.br/'  # URL do sistema
WEB_LOGIN = 'usuario'  # Login do sistema
WEB_PASSWORD = 'senha'  # Senha do sistema

# Caminhos
BASE_PATH = PATHS.project_path()
DRIVER_PATH = PATHS.driver_path()
COOKIES_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.json')

# URL da página de processo a ser visitada após login
PAGINA_PROCESSO_URL = 'https://www.omnifacil.com.br/pls/webdad/pck_sj_processo_juridico.consulta_acao?p_cod_acao_omni=3580512&p_nome=2614MARCELO&p_emp=2614&p_ide=|ID_SESSAO|&p_cpf=06050694680'

# Caminho do arquivo de configuração (opcional)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Caminho do arquivo de tarefas JSON
TAREFAS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarefas.json')

# URL personalizada para acessar o processo usando o número de integração (pasta)
PAGINA_PROCESSO_URL_PERSONALIZADA = (
            'https://www.omnifacil.com.br/pls/webdad/pck_sj_processo_juridico.consulta_acao'
            '?p_cod_acao_omni=|PASTA_NUMERO_INTEGRACAO|'
            '&p_nome=2614MARCELO&p_emp=2614&p_ide=|ID_SESSAO|&p_cpf=06050694680'
        )
#
EVENTOS = ['TRC','PDE', 'FSP', 'FTP', 'TRC', 'FPB', 'FTE', 'FBA']
OPTIONS_SELECT = {

    "PDE_V1":[
        {"p_cod_custo" : "139"},#INDENIZATÓRIAS - CONTESTAÇÃO - 1ª VERSÃO
        {"p_cod_tipo_documento" : "5"},#CONTESTAÇÃO
        {"tipo_documento" : "C"}
    ]
    ,
    "PDE_V2":[
        {"p_cod_custo" : "133"},#INDENIZATÓRIAS - CONTESTAÇÃO - 2ª VERSÃ
        {"p_cod_tipo_documento" : "5"},#CONTESTAÇÃO
        {"tipo_documento" : "C"}
    ]
    ,
    "FSP_V1":[
        {"p_cod_custo" : "140"},#INDENIZATÓRIAS - SENTENÇA - 1ª VERSÃO
        {"p_cod_tipo_documento" : "7"},#SENTENÇA
        {"tipo_documento" : "S"}
    ]
    ,
    "FSP_V2":[
        {"p_cod_custo" : "134"},#INDENIZATÓRIAS - SENTENÇA - 2ª VERSÃO
        {"p_cod_tipo_documento" : "7"},#SENTENÇA
        {"tipo_documento" : "S"}
    ]
    ,
    "FTP_V1":[
        {"p_cod_custo" : "141"},#INDENIZATÓRIAS - TRÂNSITO EM JULGADO - 1ª VERSÃO
        {"p_cod_tipo_documento" : "39"},#TRÂNSITO EM JULGADO
        {"tipo_documento" : "T"}
    ]
    ,
    "FTP_V2":[
        {"p_cod_custo" : "135"},#INDENIZATÓRIAS - TRÂNSITO EM JULGADO - 2ª VERSÃO
        {"p_cod_tipo_documento" : "39"},#TRÂNSITO EM JULGADO
        {"tipo_documento" : "T"}
    ]
     ,
    "TRC_V1":[
        {"p_cod_custo" : "141"},#INDENIZATÓRIAS - TRÂNSITO EM JULGADO - 1ª VERSÃO
        {"p_cod_tipo_documento" : "39"},#TRÂNSITO EM JULGADO
        {"tipo_documento" : "T"}
    ]
    ,
    "TRC_V2":[
        {"p_cod_custo" : "135"},#INDENIZATÓRIAS - TRÂNSITO EM JULGADO - 2ª VERSÃO
        {"p_cod_tipo_documento" : "39"},#TRÂNSITO EM JULGADO
        {"tipo_documento" : "T"}
    ]
    ,
    "FPB_V1":[
        {"p_cod_custo" : "142"},#INDENIZATÓRIAS - ÊXITO - 1ª VERSÃO
        {"p_cod_tipo_documento" : "7"},#SENTENÇA
        {"tipo_documento" : "B"}
    ],
    "FPB_V2":[
        {"p_cod_custo" : "136"},#INDENIZATÓRIAS - ÊXITO - 2ª VERSÃO
        {"p_cod_tipo_documento" : "7"},#SENTENÇA
        {"tipo_documento" : "B"}
    ],
    "FBA_PRE_V1":[
        {"p_cod_custo" : "143"},#INDENIZATÓRIAS - ACORDO PRÉ SENTENÇA - 1ª VERSÃO
        {"p_cod_tipo_documento" : "74"},#TERMO DE ACORDO
        {"tipo_documento" : "A"}
    ],
    "FBA_PRE_V2":[
        {"p_cod_custo" : "137"},#INDENIZATÓRIAS - ACORDO PRÉ SENTENÇA - 2ª VERSÃO
        {"p_cod_tipo_documento" : "74"},#TERMO DE ACORDO
        {"tipo_documento" : "A"}
    ],
    "FBA_POS_V1":[
        {"p_cod_custo" : "144"},#INDENIZATÓRIAS - ACORDO PRÉ SENTENÇA - 2ª VERSÃO
        {"p_cod_tipo_documento" : "74"}, #TERMO DE ACORDO
        {"tipo_documento" : "A"}
    ],
    "FBA_POS_V2":[
        {"p_cod_custo" : "138"},#INDENIZATÓRIAS - ACORDO PÓS SENTENÇA - 2ª VERSÃO
        {"p_cod_tipo_documento" : "74"}, #TERMO DE ACORDO
        {"tipo_documento" : "A"}
    ],
    "CEJUSC_PROCON_V2":[
        {"p_cod_custo" : "226"},#INDENIZATÓRIAS - ACORDO PÓS SENTENÇA - 2ª VERSÃO
        {"p_cod_tipo_documento" : "5"}, #TERMO DE ACORDO
        {"tipo_documento" : "C"}
    ],
    "ACOES_PATIO":[
        {"p_cod_custo" : "244"},#DESPESA DE PATIO - SENTENÇA
        {"p_cod_tipo_documento" : "7"},#SENTENÇA
        {"tipo_documento" : "S"}
    ],



}

ID_SESSAO = None

URL_REGISTRO_DESPESA = "https://www.omnifacil.com.br/pls/webdad/pck_sj_despesa_utils.registro_despesa?P_NOME=2614MARCELO&P_EMP=2614&P_IDE=|ID_SESSAO|&P_CPF=06050694680"

# Carrega configurações do config.json se existir
if os.path.exists(CONFIG_PATH):

    print("Carregando configurações de config.json...")

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Sobrescreve configurações se existirem no arquivo
    WEB_URL = config.get('web_url', WEB_URL)
    WEB_LOGIN = config.get('web_login', WEB_LOGIN)
    WEB_PASSWORD = config.get('web_password', WEB_PASSWORD)
    T2FA_SECRET = config.get('2fa_secret', None)
    DATA_INICIAL = config.get('data_inicial', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    DATA_FIM = config.get('data_final', (datetime.now()).strftime('%Y-%m-%d'))


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
print('OMNI-PDE-FSP-TRC - Automação')
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

        # Debug: Verificar cookies carregados antes de navegar
        # Navega para a página de processo e verifica se o login funcionou
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
            print(f'✓ Elemento td_despesa encontrado - sessão ativa via cookies!')
            return True
        except Exception:
            print(f'⚠ Elemento td_despesa não encontrado - cookies insuficientes, será necessário login.')
            return False

    except Exception as e:
        print(f'✗ Erro ao carregar cookies: {e}')
        traceback.print_exc()
        return False


def open_chrome_browser():
    """Abre o navegador Chrome usando Selenium"""
    try:
        print('\nAbrindo navegador Chrome...')
        
        # Configura opções do Chrome
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Descomente para rodar sem interface gráfica
        chrome_options.add_argument('--window-size=1200,800')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        # Método 1: Tentar sem especificar o service (usa ChromeDriver do PATH)
        try:
            print('Tentando usar ChromeDriver do PATH do sistema...')
            driver = webdriver.Chrome(options=chrome_options)
            print('✓ Chrome aberto com sucesso usando ChromeDriver do PATH!')
            return driver
        except Exception as path_error:
            print(f'⚠ ChromeDriver não encontrado no PATH: {path_error}')
        
        # Método 2: Tentar com webdriver-manager (download automático)
        try:
            print('Tentando instalar ChromeDriver automaticamente com webdriver-manager...')
            
            # Limpa o cache primeiro para forçar novo download
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
        
        # Se chegou aqui, nenhum método funcionou
        raise Exception('Não foi possível inicializar o ChromeDriver')
        
    except Exception as e:
        print(f'\n✗ ERRO CRÍTICO: Não foi possível abrir o Chrome')
        print(f'Erro: {e}')
        print('\n' + '='*70)
        print('SOLUÇÃO MANUAL - Siga estes passos:')
        print('='*70)
        print('\n1. Verifique a versão do seu Chrome:')
        print('   - Abra o Chrome')
        print('   - Vá em: chrome://settings/help')
        print('   - Anote a versão (ex: 131.0.6778.86)')
        print('\n2. Baixe o ChromeDriver correspondente:')
        print('   - Acesse: https://googlechromelabs.github.io/chrome-for-testing/')
        print('   - Baixe a versão EXATA do seu Chrome para Windows 64-bit')
        print('   - Escolha o arquivo chromedriver-win64.zip')
        print('\n3. Extraia e configure:')
        print('   - Extraia o arquivo chromedriver.exe')
        print('   - Coloque em: C:\\chromedriver\\chromedriver.exe')
        print('   - Ou adicione a pasta ao PATH do sistema')
        print('\n4. Reinicie este script')
        print('='*70)
        
        traceback.print_exc()
        raise


def login_web_sistema(driver):
    """Faz login no sistema web OMNI-PDE-FSP-TRC"""
    try:
        print('\n' + '='*70)
        print('REALIZANDO LOGIN NO SISTEMA WEB')
        print('='*70)

        # Navegar para a URL de login
        print(f'\nAcessando {WEB_URL}...')
        driver.get(WEB_URL)
        print('✓ Página carregada')
        
        # Aguarda a página carregar
        wait = WebDriverWait(driver, 10)
        
        # Encontra e preenche o campo de login
        print('Preenchendo campo de login...')
        login_input = wait.until(EC.presence_of_element_located((By.ID, 'p-nome')))
        login_input.clear()
        login_input.send_keys(WEB_LOGIN)
        print(f'✓ Login digitado: {WEB_LOGIN}')
        
        # Encontra e preenche o campo de senha
        print('Preenchendo campo de senha...')
        senha_input = driver.find_element(By.ID, 'p-senha')
        senha_input.clear()
        senha_input.send_keys(WEB_PASSWORD)
        print('✓ Senha digitada')
        
        # Clica no botão de login e aguarda o campo MFA ficar interativo
        print('Clicando no botão de login...')
        btn_login = driver.find_element(By.ID, 'btn-conectar')
        btn_login.click()
        print('✓ Botão de login clicado!')

        # O campo p-codigo-mfa já existe no HTML mas só fica interativo após o clique.
        # Fica tentando escrever nele; se falhar, clica em btn-conectar novamente.
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

        # Solicita o código 2FA ao usuário
        #codigo_mfa = input('\n>>> Digite o código 2FA/MFA e pressione Enter: ').strip()
        codigo_mfa = pyotp.TOTP(T2FA_SECRET).now() if T2FA_SECRET else input('\n>>> Digite o código 2FA/MFA e pressione Enter: ').strip()
        mfa_input.send_keys(codigo_mfa)

        print(f'✓ Código MFA inserido: {codigo_mfa}')
        botao_enviar = driver.find_element(By.ID, "bt-enviar-mfa").click()

        # Aguarda um pouco para o login processar
        time.sleep(3)
        
        print('✓ Login realizado com sucesso!')

        # Salva cookies em cookies.json
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
        print('\n⚠ ATENÇÃO: Os seletores CSS precisam ser ajustados conforme o sistema real!')
        print('   Abra o navegador manualmente e inspecione os elementos de login.')
        traceback.print_exc()
        return False


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def registrar_despesa(driver, tarefa=None, valor_despesa=None, option_do_select_despesa=None, tipo_documento=None, documento=None):
    """Registra uma despesa no sistema web para a tarefa informada"""

    texto_alerta = ""

    try:
        wait = WebDriverWait(driver, 10)
        
        # Data de hoje no formato ddmmyyyy (sem máscara, o campo aplica automaticamente)
        data_hoje = datetime.now().strftime('%d%m%Y')

        # Preenche a data da despesa
        print(f'  Preenchendo data da despesa: {data_hoje}')
        campo_data = wait.until(EC.presence_of_element_located((By.NAME, 'p_dat_despesa')))
        campo_data.clear()
        campo_data.send_keys(data_hoje)
        print(f'  ✓ Data preenchida: {data_hoje}')

        # Preenche o código da ação (pasta)
        print(f'  Preenchendo p_cod_acao_omni: {tarefa["pasta_numero_integracao"] if tarefa else None}')
        campo_acao = driver.find_element(By.NAME, 'p_cod_acao_omni')
        campo_acao.clear()
        campo_acao.send_keys(str(tarefa['pasta_numero_integracao']))
        campo_acao.send_keys(webdriver.Keys.TAB)
        time.sleep(2)
        print(f'  ✓ p_cod_acao_omni preenchido')

        # Seleciona o tipo de custo/despesa
        print(f'  Selecionando p_cod_custo: {option_do_select_despesa}')
        opcoes = 1
        tentativa = 0

        while opcoes <= 2:
            print(f'  Aguardando select e opções: {option_do_select_despesa}')
            select_custo = Select(wait.until(EC.presence_of_element_located((By.NAME, 'p_cod_custo'))))
            opcoes = len(select_custo.options)
            time.sleep(2)
            tentativa += 1

            if tentativa > 10:
                return registra_erro(tarefa, "Erro de seleção de custo: opção não disponível.")

        select_custo.select_by_value(str(option_do_select_despesa))
        print(f'  ✓ p_cod_custo selecionado: {option_do_select_despesa}')
        opcoes = len(select_custo.options)
        
        # Seleciona o tipo de documento
        print(f'  Selecionando p_cod_tipo_documento: {tipo_documento}')
        select_tipo_doc = Select(wait.until(EC.presence_of_element_located((By.NAME, 'p_cod_tipo_documento'))))
        select_tipo_doc.select_by_value(str(tipo_documento))
        print(f'  ✓ p_cod_tipo_documento selecionado: {tipo_documento}')

        # Preenche o número do documento
        print(f'  Preenchendo p_dsc_nr_documento: {documento}')
        campo_documento = driver.find_element(By.NAME, 'p_dsc_nr_documento')
        campo_documento.clear()
        campo_documento.send_keys(str(documento))
        print(f'  ✓ p_dsc_nr_documento preenchido: {documento}')
       
        
        # Preenche o valor da despesa
        print(f'  Preenchendo p_num_valor: {valor_despesa}')
        campo_valor = driver.find_element(By.NAME, 'p_num_valor')
        campo_valor.clear()
        campo_valor.send_keys(f"{valor_despesa:.2f}")  # Formata o valor com 2 casas decimais
        print(f'  ✓ p_num_valor preenchido: {valor_despesa}')

        try:
            time.sleep(2)
            # Clica no botão Ok
            print(f'  Preenchendo p_num_valor: {valor_despesa}')
            botao_ok = driver.find_element(By.ID, 'btnOk')
            botao_ok.click()
            print(f'  ✓ p_num_valor preenchido: {valor_despesa}')
        
        except Exception as e:
            
            print(f'  ✗ Erro ao preencher valor da despesa: {e}')
            texto_alerta = driver.find_element(By.ID, "popup_message").text

            if 'Não foi localizado parametrização para o lançamento da despesa' in texto_alerta:
                print(f'  [Alert] Configuração ausente para despesa: {texto_alerta}')
                return False, texto_alerta
            else:

                if texto_alerta != "":
                    return False, texto_alerta
                
                pdb.set_trace()  # Debug: Verificar por que o campo de valor não está sendo preenchido corretamente

        try:
            texto_alerta = driver.find_element(By.ID, "popup_message").text
            return registra_erro(tarefa, texto_alerta)

        except:
            print(f'  [Alert] Nenhum alerta modal encontrado.')
            pass

        
        #pdb.set_trace()  # Debug: Verificar se o valor da despesa foi preenchido corretamente antes de clicar em gravar
        # Clica em gravar
        print(f'  Preenchendo p_num_valor: {valor_despesa}')

        #pdb.set_trace()  # Debug: Verificar estado do formulário antes de clicar em gravar
        botao_gravar = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='button' and @value='Gravar']")
            ))
        botao_gravar.click()

        #clica no Alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f'  [Alert] Texto: {alert_text}')
            if 'Confirma Gravação' in alert_text:
                alert.accept()
                print(f'  ✓ Clicou em OK no alert de confirmação.')
                print(f'  ✓ Formulário de despesa preenchido com sucesso!')
                return True, texto_alerta
            else:
                alert.dismiss()
                print(f'  [Alert] Texto inesperado, alert dispensado.')
                return False, texto_alerta

        except Exception:
            print(f'  [Alert] Nenhum alert encontrado.')
            return False, texto_alerta


    except Exception as e:
        print(f'  ✗ Erro ao registrar despesa: {e}')
        #pdb.set_trace()  # Debug: Verificar por que o registro de despesa falhou
        traceback.print_exc()
        return False, texto_alerta

def registra_erro(tarefa, texto_alerta):

    #if('ultrapassou o limite' in texto_alerta):
    print(f'  [Alert] Limite ultrapassado: {texto_alerta}')

    limites_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'erros_registro_despesa.json')
    limites_lista = []

    if os.path.exists(limites_json_path):
        try:
            with open(limites_json_path, 'r', encoding='utf-8') as _f:
                conteudo = _f.read().strip()
                if conteudo:
                    limites_lista = json.loads(conteudo)
        except (json.JSONDecodeError, ValueError):
            limites_lista = []

    # Evita duplicatas pelo id_tramitacao
    id_tramitacao = tarefa['id_tramitacao']
    limites_lista = [t for t in limites_lista if t.get('id_tarefa') != id_tramitacao]
    limites_lista.append({
        'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tarefa': tarefa,
        'texto_alerta': texto_alerta,
        'id_tarefa': id_tramitacao
    })

    with open(limites_json_path, 'w', encoding='utf-8') as _f:
        json.dump(limites_lista, _f, ensure_ascii=False, indent=2)

    print(f'  ✓ Registrado em erros_registro_despesa.json ({len(limites_lista)} total)')
    return False, texto_alerta

def normalizar_texto(texto: str, somente_alfanumerico: bool = True) -> str:
    if not texto:
        return ""

    # 1. remove acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')

    # 2. remove quebras de linha / tabs
    texto = re.sub(r'[\r\n\t]+', ' ', texto)

    # 3. remove caracteres especiais
    if somente_alfanumerico:
        # mantém só letras, números e espaço
        texto = re.sub(r'[^a-zA-Z0-9 ]+', '', texto)
    else:
        # mantém pontuação básica (se quiser algo menos agressivo)
        texto = re.sub(r'[^\w\s\.\,\-\/]+', '', texto)

    # 4. remove espaços duplicados
    texto = re.sub(r'\s+', ' ', texto)

    return texto.strip()

def main():
    """Executa o fluxo completo da automação"""
    driver = None
    
    try:
        print('\n' + '='*70)
        print('INICIANDO AUTOMAÇÃO')
        print('='*70)

        integracao = True

        if integracao:
            # ====================================================================
            # ETAPA 1: Autenticação na API CPJ
            # ====================================================================
            print('\n[ETAPA 1/3] Autenticação na API CPJ')
            print('-'*70)
            
            token = api_login()
            
            if not token:
                print('✗ Falha ao autenticar na API. Abortando processo...')
                return
            
            print('✓ Autenticação na API concluída com sucesso!')
            print(f'✓ Token Bearer configurado e pronto para uso!')
            
            # ====================================================================
            # ETAPA 2: Buscar tarefas/processos por evento e consolidar em JSON
            # ====================================================================
            print('\n[ETAPA 2/3] Buscar tarefas/processos')
            print('-'*70)

            if os.path.exists(TAREFAS_JSON_PATH):
                os.remove(TAREFAS_JSON_PATH)
                print(f'✓ Arquivo anterior removido: tarefas.json')

            todas_tarefas = []
            resumo = {}
            ids_vistos = set()  # <-- DECLARAÇÃO AQUI (fora do loop)

            for evento in EVENTOS:
                print(f'\nBuscando evento: {evento}...')

                # if 'PDE' in evento or 'TRC' in evento:
                tarefas = []

                _dt_inicio = datetime.strptime(DATA_INICIAL, '%Y-%m-%d')
                _dt_fim = datetime.strptime(DATA_FIM, '%Y-%m-%d')
                _dia_atual = _dt_inicio
                conta_dias = 1
                while _dia_atual <= _dt_fim:
                    _dia_seguinte = _dia_atual + timedelta(days=conta_dias)
                    print(f'  Buscando {evento} data {_dia_atual.strftime("%Y-%m-%d")} → {_dia_seguinte.strftime("%Y-%m-%d")}...')

                    _resultado = api_buscar_processo_tarefa_por_data(
                        evento=evento,
                        data_inicial=_dia_atual,
                        data_fim=_dia_seguinte,
                        id_tramitacao_situacao=0
                    )
                    _dia_atual = _dia_seguinte
                    #conta_dias += 1

                if _resultado:
                    novos = []
                    for item in _resultado:
                        _id = item.get("id_tramitacao")
                        if _id not in ids_vistos:
                            ids_vistos.add(_id)
                            novos.append(item)

                    tarefas.extend(novos)

                    print(f'+ {len(novos)} novas tarefas (filtrado de {len(_resultado)})')

                # else:
                        
                #     tarefas = api_buscar_processo_tarefa_por_data(
                #             evento=evento,
                #             data_inicial=_dia_atual,
                #             data_fim=_dia_seguinte,
                #             id_tramitacao_situacao=0
                #         )

                if tarefas:
                    print(f'  ✓ {len(tarefas)} tarefa(s) encontrada(s) para {evento}')
                    todas_tarefas.extend(tarefas)
                    resumo[evento] = len(tarefas)
                else:
                    print(f'  ⚠ Nenhuma tarefa encontrada para {evento}')
                    resumo[evento] = 0
            
            print(f'\n--- Resumo da busca ---')
            for evento, qtd in resumo.items():
                print(f'  {evento}: {qtd} tarefa(s)')
            print(f'  TOTAL: {len(todas_tarefas)} tarefa(s)')

            # Salva todas as tarefas num único JSON
            payload_json = {
                'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_inicial': DATA_INICIAL,
                'data_final': DATA_FIM,
                'eventos': EVENTOS,
                'resumo': resumo,
                'total': len(todas_tarefas),
                'tarefas': todas_tarefas
            }

            with open(TAREFAS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(payload_json, f, ensure_ascii=False, indent=2)

            print(f'\n✓ JSON consolidado salvo em: {TAREFAS_JSON_PATH}')
            
            if not todas_tarefas:
                print('\n⚠ Nenhuma tarefa encontrada para nenhum evento. Encerrando.')
                return
            
            # ====================================================================
            # ETAPA 3: Buscar numero_integracao (pasta) para cada tarefa
            # ====================================================================
            print('\n[ETAPA 3/4] Buscar número de integração (pasta) por processo')
            print('-'*70)

            sem_integracao = 0
            for idx, tarefa in enumerate(todas_tarefas, 1):
                id_processo = tarefa.get('id_processo')
                if not id_processo:
                    print(f'  [{idx}/{len(todas_tarefas)}] ⚠ id_processo ausente, pulando...')
                    tarefa['pasta_numero_integracao'] = None
                    sem_integracao += 1
                    continue

                processos = api_buscar_processo_por_pj(pj=id_processo)

                if processos and isinstance(processos, list) and len(processos) > 0:
                    numero_integracao = processos[0].get('numero_integracao')
                    contrato_cliente = processos[0].get('contrato_cliente')

                    if processos[0].get('numero_processo'):
                        
                        _num_proc = processos[0]['numero_processo']
                        _CNJ_PATTERN = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$')
                        if not _CNJ_PATTERN.match(str(_num_proc).strip()):
                            print(f'  [!] numero_processo "{_num_proc}" não é um processo CNJ válido — registrando em pastas_sem_contrato.json e pulando tarefa.')
                            _pastas_sem_contrato_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pastas_sem_contrato.json')
                            _pastas_sem_contrato = []
                            if os.path.exists(_pastas_sem_contrato_path):
                                try:
                                    with open(_pastas_sem_contrato_path, 'r', encoding='utf-8') as _f:
                                        _conteudo = _f.read().strip()
                                        if _conteudo:
                                            _pastas_sem_contrato = json.loads(_conteudo)
                                except (json.JSONDecodeError, ValueError):
                                    _pastas_sem_contrato = []

                            _id_tarefa = tarefa.get('id_tramitacao')

                            if any(t.get('tarefa', {}).get('id_tramitacao') == _id_tarefa for t in _pastas_sem_contrato):
                                print(f'  [!] Tarefa id_tramitacao={_id_tarefa} já registrada em pastas_sem_contrato.json, pulando.')
                                tarefa['pasta_numero_integracao'] = None
                                sem_integracao += 1
                                continue

                            if 'OMNI' in processos[0].get('autor_nome', '') or 'OMNI' in processos[0].get('reu_nome', ''):

                                _pastas_sem_contrato.append({
                                    'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'tarefa': tarefa,
                                    'processo': processos[0]
                                })
                                

                                with open(_pastas_sem_contrato_path, 'w', encoding='utf-8') as _f:
                                    json.dump(_pastas_sem_contrato, _f, ensure_ascii=False, indent=2)
                                print(f'  ✓ Registrado em pastas_sem_contrato.json ({len(_pastas_sem_contrato)} total)')
                                tarefa['pasta_numero_integracao'] = None
                                sem_integracao += 1

                            continue

                        else:

                            print(f'  [!] Processo encontrado com número de processo: {_num_proc} - isso pode indicar que o processo já está integrado ou que há mais de um processo para o mesmo id_processo. Verifique manualmente se necessário.')

                    reu_nome = processos[0].get('reu_nome')
                    update_cliente_processo = processos[0].get('update_usuario')
                    tarefa['pasta_numero_integracao'] = numero_integracao
                    tarefa['contrato_cliente'] = contrato_cliente
                    tarefa['reu_nome'] = reu_nome
                    tarefa['update_cliente_processo'] = update_cliente_processo
                    print(f'  [{idx}/{len(todas_tarefas)}] ✓ id_processo={id_processo} → pasta={numero_integracao}, contrato_cliente={contrato_cliente}, reu_nome={reu_nome}')
                else:
                    tarefa['pasta_numero_integracao'] = None
                    tarefa['contrato_cliente'] = None
                    tarefa['reu_nome'] = None
                    tarefa['update_cliente_processo'] = None
                    sem_integracao += 1
                    print(f'  [{idx}/{len(todas_tarefas)}] ⚠ Nenhum processo encontrado para id_processo={id_processo}')

            # Atualiza o JSON com os dados enriquecidos
            payload_json['tarefas'] = todas_tarefas
            payload_json['sem_integracao'] = sem_integracao
            with open(TAREFAS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(payload_json, f, ensure_ascii=False, indent=2)

            print(f'\n✓ JSON atualizado com pasta_numero_integracao: {TAREFAS_JSON_PATH}')
            print(f'  - Com integração: {len(todas_tarefas) - sem_integracao}')
            print(f'  - Sem integração: {sem_integracao}')
        

          # Debug: Verificar tarefas antes de iniciar automação web
        # ====================================================================
        # ETAPA 4: Automação Web
        # ====================================================================
        print('\n[ETAPA 4/4] Automação Web - Login no Sistema')
        print('-'*70)

        # Abre o navegador
        driver = open_chrome_browser()

        # Navega ao domínio base para poder adicionar cookies
        print(f'\nAcessando domínio base para carregar cookies...')
        driver.get(WEB_URL)

        # Carrega cookies do arquivo e verifica se a sessão já está ativa
        sessao_ativa = carregar_cookies(driver)
        
        if not sessao_ativa:
            # Cookies insuficientes - faz login completo
            login_sucesso = login_web_sistema(driver)

            if not login_sucesso:
                print('\n✗ Falha no login. Abortando...')
                return

            # Após login, navega para a página de processo
            print(f'\nAcessando página de processo após login...')
            driver.get(PAGINA_PROCESSO_URL)
        else:
            print(f'✓ Sessão ativa via cookies, login ignorado.')

        # ====================================================================
        # ETAPA 5: Processar tarefas - navegar e clicar em td_despesa
        # ====================================================================
        print('\n[ETAPA 5/5] Processar tarefas')
        print('-'*70)

        # PDE: Constestação CONTESTAÇÃO
        # FSP: Sentença SENTENÇA
        # FTP/TRC: Transito
        # FPB: Bonus
        # FTE: Revisionais
        # FBA: Acordo

        # Carrega tarefas do JSON
        with open(TAREFAS_JSON_PATH, 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
        tarefas_processamento = dados_json.get('tarefas', [])

        tarefas_validas = [t for t in tarefas_processamento if t.get('pasta_numero_integracao')]
        tarefas_sem_pasta = len(tarefas_processamento) - len(tarefas_validas)

        print(f'  Total de tarefas: {len(tarefas_processamento)}')
        print(f'  Com pasta_numero_integracao: {len(tarefas_validas)}')
        print(f'  Sem pasta_numero_integracao (serão ignoradas): {tarefas_sem_pasta}')

        sucesso = 0
        falha = 0

        # Carrega tabela de valores
        TABELA_VALORES_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tabela_valores.json')
        with open(TABELA_VALORES_JSON_PATH, 'r', encoding='utf-8') as f:
            tabela_valores = json.load(f)
        print(f'✓ tabela_valores.json carregado: {len(tabela_valores)} registro(s)')
        
        # Carrega erros anteriores para evitar retrabalho
        _erros_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'erros_registro_despesa.json')
        _erros_lista = []
        if os.path.exists(_erros_json_path):
            try:
                with open(_erros_json_path, 'r', encoding='utf-8') as _f:
                    _conteudo = _f.read().strip()
                    if _conteudo:
                        _erros_lista = json.loads(_conteudo)
            except (json.JSONDecodeError, ValueError):
                _erros_lista = []
        _erros_pastas = {str(t.get('tarefa', {}).get('pasta_numero_integracao')) for t in _erros_lista}
        print(f'✓ erros_registro_despesa.json carregado: {len(_erros_lista)} registro(s), {len(_erros_pastas)} pasta(s) com erro')

        for idx, tarefa in enumerate(tarefas_validas, 1):
            
            
            # if '3585581' in str(tarefa.get('pasta_numero_integracao')):
            #     continue

            if str(tarefa.get('pasta_numero_integracao'))  in _erros_pastas:
                print(f'  [{idx}/{len(tarefas_validas)}] pasta={tarefa.get("pasta_numero_integracao")} já consta em erros_registro_despesa.json, pulando...')
                continue

            if "OMNI" not in tarefa.get('reu_nome', ''):
                print(f'  [{idx}/{len(tarefas_validas)}] Evento {tarefa.get("evento")} não é OMNI, pulando...')
                continue
             
            pasta = tarefa['pasta_numero_integracao']
            evento = tarefa.get('evento', '')
            url = PAGINA_PROCESSO_URL_PERSONALIZADA.replace('|PASTA_NUMERO_INTEGRACAO|', str(pasta)).replace("|ID_SESSAO|", ID_SESSAO)
            url_despesa = URL_REGISTRO_DESPESA.replace("|ID_SESSAO|", ID_SESSAO)
            chave_tabela_valores = ""

            print(f'\n  [{idx}/{len(tarefas_validas)}] pasta={pasta}')
            print(f'  Acessando: {url}')

            try:             
                driver.get(url)

                cejusc_procon = False

                time.sleep(1)  # Espera a página carregar um pouco antes de buscar elementos

                texto_demanda = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'div_basico'))   
                ).text

                time.sleep(1)  # Espera a página carregar um pouco antes de buscar elementos

                if 'CEJUSC' in texto_demanda or 'PROCON' in texto_demanda:
                    cejusc_procon = True
                    print(f'  Evento CEJUSC_PROCON identificado, buscando texto específico na página para confirmar...')

                texto_orgao = WebDriverWait(driver, 1000).until(
                    EC.presence_of_element_located((By.ID, 'theform'))   
                ).text

                td_despesa = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'td_despesa'))
                )

                td_despesa.click()
                print(f'  ✓ td_despesa clicado!')

                texto = driver.find_element(By.ID, "theformDespesa").text

                # PDE: Constestação
                # FSP: Sentença
                # FTP/TRC: Transito
                # FPB: Bonus
                # FTE: Revisionais
                # FBA: Acordo

                prefixo = ""
                jec_civ = ""
                
                if cejusc_procon:
                    if 'CONTESTAÇÃO' in texto:
                        print(f'  ✓ Evento PDE confirmado no texto da página.')
                    else:
                        #de acordo com chat AMANDA CEJUS ou PROCON sempre sao eventos de contestação
                        tarefa['contrato_cliente'] = 999
                        evento = "CEJUSC_PROCON"
                        chave_tabela_valores = 'CONTESTACAO'  # Debug: Verificar texto para PDE
                else:    

                    if 'PDE' in evento: 
                        if 'CONTESTAÇÃO' in texto:
                            print(f'  ✓ Evento PDE confirmado no texto da página.')
                        else:
                            chave_tabela_valores = 'CONTESTACAO'  # Debug: Verificar texto para PDE

                            if tarefa['contrato_cliente'] == 829:
    
                                if 'juizado' in normalizar_texto(texto_orgao).lower():
                                    jec_civ = "_JEC"
                                else:
                                    jec_civ = "_CIV"
                                
                                #pdb.set_trace()  # Debug: Verificar texto orgao para definir JEC ou CIV para contrato 829

                    if 'FSP' in evento: 
                        if 'SENTENÇA' in texto:
                            print(f'  ✓ Evento FSP confirmado no texto da página.')
                        else:

                            chave_tabela_valores = 'SENTENCA'

                            if tarefa['contrato_cliente'] > 800 and tarefa['contrato_cliente'] <= 829:
                                
                                tarefa['contrato_cliente'] = 829
                                
                                if texto_orgao == "":
                                    pdb.set_trace()  # Debug: Verificar texto orgao vazio

                                if 'vara civel' in normalizar_texto(texto_orgao).lower():
                                    jec_civ = "_CIV"
                                else:
                                    jec_civ = "_JEC"
                            
                    if 'FTP' in evento or 'TRC' in evento:
                        if 'TRÂNSITO EM JULGADO' in texto:
                            print(f'  ✓ Evento FTP/TRC confirmado no texto da página.')
                        else:  
                            chave_tabela_valores = 'TRANSITO'
                    
                    if 'FPB' in evento:
                        if 'ÊXITO' in texto or 'BONUS' in texto or 'BÔNUS' in texto:
                            print(f'  ✓ Evento FPB confirmado no texto da página.')
                        else:  
                            chave_tabela_valores = 'BONUS'  # Debug: Verificar texto para FPB

                    if 'FTE' in evento:
                        if 'REVISIONAIS' in texto or 'Revisionais' in texto:
                            print(f'  ✓ Evento FTE confirmado no texto da página.')
                        else:  
                            chave_tabela_valores = 'REVISIONAIS'  # Debug: Verificar texto para FTE

                    if 'FBA' in evento:
                        if 'ACORDO PÓS' in texto or 'ACORDO PRÉ' in texto:
                            print(f'  ✓ Evento FBA confirmado no texto da página.')
                        else:  

                            pdb.set_trace()  # Debug: Verificar texto para definir chave de acordo pré ou pós
                            if "ACORDO POS" in tarefa['texto'] or "ACORDO PÓS" in tarefa['texto']:
                                chave_tabela_valores = 'ACORDO_POS'  # Debug: Verificar texto para FBA POS
                                prefixo = "_POS"
                            elif "ACORDO PRE" in tarefa['texto'] or "ACORDO PRÉ" in tarefa['texto']:
                                chave_tabela_valores = 'ACORDO_PRE'  # Debug: Verificar texto para FBA PRE
                                prefixo = "_PRE"
                            else:
                                registra_erro(tarefa, "[URGENTE] Evento FBA não identificado como ACORDO PRÉ ou PÓS no texto da tarefa, e nem na página. Verificar manualmente. Texto tarefa: " + tarefa['texto'])
                                continue #retirar quando

                if chave_tabela_valores != "":
                    print('  ✓ Evento não identificado na OMNI, usando chave para tabela_valores: ' + chave_tabela_valores)
                    try:
                        print(str(tarefa['contrato_cliente']) + ' Numero do contrato Cliente  - Dias Costa...')
                        lista = tabela_valores[str(tarefa['contrato_cliente']) + jec_civ]['dados']
                        produto = tabela_valores[str(tarefa['contrato_cliente']) + jec_civ]['produto']

                        valor_despesa = next((v[chave_tabela_valores] for v in lista if chave_tabela_valores in v), None)
                        
                        if valor_despesa is None:
                        
                            if 'FPB' in evento:
                                chave_tabela_valores = "EXITO"
                                valor_despesa = next((v[chave_tabela_valores] for v in lista if chave_tabela_valores in v), None)

                            if 'FBA' in evento:
                                if 'ACORDO_PRE' in chave_tabela_valores:
                                    print(f'  X Acordo não permite registro FBA PRE: ACORDO')
                                    api_atualizar_tarefa(tarefa['id_tramitacao'],2,tarefa['update_data_hora'], tarefa['update_usuario'])

                            #pdb.set_trace()  # Debug: COnfirmar evento FPB FBA para definir chave de êxito caso valor da chave bonus seja None

                        versao = str(tabela_valores[str(tarefa['contrato_cliente']) +jec_civ]['versao'] )
                        
                        if valor_despesa is not None:
                            print(f'  ✓ Valor encontrado na tabela_valores para contrato_cliente={tarefa["contrato_cliente"]} e chave={chave_tabela_valores}')
                            driver.get(url_despesa)

                            #pdb.set_trace()  # Debug: Verificar tarefa atual antes de processar
                            
                            if produto == 'ACOES_PATIO':
                                option_select_despesa = OPTIONS_SELECT[produto][0]['p_cod_custo']
                                option_select_documento = OPTIONS_SELECT[produto][1]['p_cod_tipo_documento']
                                input_tipo_documento = OPTIONS_SELECT[produto][2]['tipo_documento']
                            else:
                                option_select_despesa = OPTIONS_SELECT[evento + prefixo + '_V'+ versao][0]['p_cod_custo']
                                option_select_documento = OPTIONS_SELECT[evento + prefixo + '_V'+ versao][1]['p_cod_tipo_documento']
                                input_tipo_documento = OPTIONS_SELECT[evento + prefixo + '_V'+ versao][2]['tipo_documento']

                            registrar_despesa_retorno = registrar_despesa(driver, tarefa, valor_despesa, option_select_despesa, option_select_documento, input_tipo_documento)

                            if registrar_despesa_retorno[0] == False:

                                if "Não foi localizado parametrização para o lançamento da despesa" in registrar_despesa_retorno[1]:
                                    print(f'  ✗ Configuração ausente para despesa: {registrar_despesa_retorno[1]}')
                                    #pdb.set_trace()  # Debug: Verificar detalhes da configuração ausente para despesa
                                    api_atualizar_tarefa(tarefa['id_tramitacao'],2,tarefa['update_data_hora'], tarefa['update_usuario'],re.sub(r'\s+', ' ',unicodedata.normalize('NFD', registrar_despesa_retorno[1]).encode('ascii','ignore').decode()).strip())
                                    continue
                                
                                elif 'Demanda Encontra-se Encerrada' in registrar_despesa_retorno[1]:
                                    print(f'  ✗ Demanda Encontra-se Encerrada: {registrar_despesa_retorno[1]}')
                                    #pdb.set_trace()  # Debug: Verificar detalhes da demanda encerrada
                                    registra_erro(tarefa, registrar_despesa_retorno[1])

                                else:
                                    print(f'  ✗ Erro ao registrar despesa: {registrar_despesa_retorno[1]}')
                                    #pdb.set_trace()  # Debug: Verificar o motivo de registrar despesa nao ter funcionado
                                    registra_erro(tarefa, registrar_despesa_retorno[1])
                                continue
      
                        else:
                            pdb.set_trace()  # Debug: Verificar o valor de despesa

                    except KeyError:   
                        pdb.set_trace()  # Debug: erro de chaves
                        registra_erro(tarefa, f'Chave de valor não encontrada: contrato_cliente={tarefa["contrato_cliente"]} chave={chave_tabela_valores}')
                        
                        continue
                
                #pdb.set_trace()  # Debug: Verificar qual é o evento e o texto para definir a chave da tabela de valores
                api_atualizar_tarefa(tarefa['id_tramitacao'],1,tarefa['update_data_hora'], tarefa['update_usuario'])

                if integracao == False:
                    with open(TAREFAS_JSON_PATH, 'r', encoding='utf-8') as _f:
                        _dados = json.load(_f)
                    _dados['tarefas'] = [t for t in _dados['tarefas'] if t.get('id_tramitacao') != tarefa['id_tramitacao']]
                    _dados['total'] = len(_dados['tarefas'])
                    with open(TAREFAS_JSON_PATH, 'w', encoding='utf-8') as _f:
                        json.dump(_dados, _f, ensure_ascii=False, indent=2)
                    print(f'  ✓ Tarefa id_tramitacao={tarefa["id_tramitacao"]} removida de tarefas.json')

                sucesso += 1

            except Exception as e:
                print(f'  ✗ Erro na tarefa pasta={pasta}: {e}')
                falha += 1
                continue

        print(f'\n--- Resumo do processamento ---')
        print(f'  ✓ Sucesso: {sucesso}')
        print(f'  ✗ Falha:   {falha}')
        print(f'  - Ignoradas (sem pasta): {tarefas_sem_pasta}')

        print('\n✓ Automação concluída com sucesso!')
        
    except Exception as e:
        print(f'\n✗ Falha na automação: {e}')
        traceback.print_exc()
        raise
        
    finally:
        # Logout da API
        print('\nFinalizando...')
        api_logout()
        
        # Fecha o navegador
        if driver:
            driver.quit()
            print('✓ Navegador fechado')
        
        print('\n' + '='*70)
        print('FIM DA EXECUÇÃO')
        print('='*70)


if __name__ == '__main__':
    main()
