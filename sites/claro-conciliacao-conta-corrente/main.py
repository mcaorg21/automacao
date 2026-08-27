#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/claro-conciliacao-conta-corrente/main.py

| projeto: automacao-python
| data: 2026-08-13
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
WEB_URL = WEB_URL_INICIAL = ''
WEB_LOGIN = ''
WEB_PASSWORD = ''

# Caminhos
BASE_PATH = PATHS.project_path()
DRIVER_PATH = PATHS.driver_path()
COOKIES_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.json')

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Caminho do arquivo de tarefas JSON
TAREFAS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarefas.json')

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


def _ultima_sexta_do_mes(data):
    """Retorna a última sexta-feira do mês da data informada."""
    from calendar import monthrange
    ultimo_dia = monthrange(data.year, data.month)[1]
    ultimo = data.replace(day=ultimo_dia)
    dias_atras = (ultimo.weekday() - 4) % 7
    return ultimo - timedelta(days=dias_atras)


def atualizar_datas_execucao():
    """Atualiza data_inicial e data_final no config.json.
    Execução manual → usa as datas já gravadas no config (reseta execucao_manual).
    Última sexta do mês → cobre o mês inteiro (dia 1 até hoje).
    Demais dias → últimos 8 dias (hoje-8 até hoje).
    """
    global DATA_INICIAL, DATA_FIM
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        if config_data.get('execucao_manual'):
            config_data['execucao_manual'] = False
            DATA_INICIAL = config_data.get('data_inicial', DATA_INICIAL)
            DATA_FIM = config_data.get('data_final', DATA_FIM)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print(f'✓ Execução manual — usando datas do config: {DATA_INICIAL} → {DATA_FIM}')
            return
    except Exception as e:
        print(f'⚠ Erro ao verificar execucao_manual: {e}')
    hoje = datetime.now()
    DATA_FIM = hoje.strftime('%Y-%m-%d')
    if hoje.date() == _ultima_sexta_do_mes(hoje).date():
        DATA_INICIAL = hoje.replace(day=1).strftime('%Y-%m-%d')
        print(f'✓ Última sexta-feira do mês — cobertura mensal: {DATA_INICIAL} → {DATA_FIM}')
    else:
        DATA_INICIAL = (hoje - timedelta(days=8)).strftime('%Y-%m-%d')
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config_data['data_inicial'] = DATA_INICIAL
        config_data['data_final'] = DATA_FIM
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f'✓ Datas atualizadas automaticamente: {DATA_INICIAL} → {DATA_FIM}')
    except Exception as e:
        print(f'⚠ Erro ao atualizar datas no config.json: {e}')


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

        #atualizar_datas_execucao()

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
        # ETAPA 2: Buscar lançamentos de conta corrente (CC 1449)
        # ====================================================================
        print('\n[ETAPA 2/4] Buscar lançamentos de conta corrente')
        print('-'*70)

        if os.path.exists(TAREFAS_JSON_PATH):
            os.remove(TAREFAS_JSON_PATH)
            print(f'✓ Arquivo anterior removido: tarefas.json')

        CONTAS_CORRENTE = ["1495","1496"]
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
            _janela_fim = min(_janela_inicio + timedelta(days=60), _dt_fim)

            print(f'  [{CONTAS_CORRENTE}] {_janela_inicio.strftime("%Y-%m-%d")} → {_janela_fim.strftime("%Y-%m-%d")}...')

            _resultado = api_buscar_lancamentos(
                data_inicial=_janela_inicio,
                data_final=_janela_fim,
                numero_cc=CONTAS_CORRENTE,
                documento_spf = False,
                limit=5000
            )

            _janela_inicio = _janela_fim + timedelta(days=1)

            if _resultado:
                
                _total_resultado = len(_resultado)
                for _idx_resultado, item in enumerate(_resultado, 1):
                    print ('='*70)
                    print(f'\033[92m  [{_idx_resultado}/{_total_resultado}] {_idx_resultado/_total_resultado*100:.1f}%\033[0m')
                    print ('='*70)
                    _id = item.get('id') or item.get('id_lancamento') or id(item)
                    if _id not in ids_vistos:
                        ids_vistos.add(_id)
                        ficha = item.get('ficha', '')
                        if ficha:
                            _filtros = [
                                {"ccl.numero_cc": {"_in": CONTAS_CORRENTE}},
                                {"ficha": {"_eq": ficha}},
                                {"dc": {"_eq": 1}},
                            ]
                            _resultado_ficha = api_buscar_lancamentos_filtro(filtros=_filtros)
                            array_valores = []
                            if _resultado_ficha and isinstance(_resultado_ficha, list) and len(_resultado_ficha) > 0:
                                item['lancamentos_ficha'] = _resultado_ficha

                                for i, lf in enumerate(_resultado_ficha, 1):
                                    array_valores.append(lf.get('valor_original', 0) or 0)

                                valor_recebido = item['valor_original_total'] = sum(
                                    lf.get('valor_original', 0) or 0 for lf in _resultado_ficha
                                )

                                print(f'      ✓ Ficha {ficha} → dc=1 → {len(_resultado_ficha)} lançamento(s) → total={item["valor_original_total"]}')

                            else:
                                print(f'      ⚠ Ficha {ficha} → dc=1 → nenhum lançamento encontrado')
                                valor_recebido = 0
                                continue
                            
                            processos = api_buscar_processo_por_ficha(ficha)

                            if processos and isinstance(processos, list) and len(processos) > 0:
                                item['dados_processo'] = processos[-1]

                            _tabela_valores_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tabela_valores.json')
                            _tabela_valores = {}

                            try:
                                with open(_tabela_valores_path, 'r', encoding='utf-8') as _f:
                                    _tabela_valores = json.load(_f)
                                print(f'      ✓ tabela_valores.json carregada ({len(_tabela_valores)} entradas)')
                            except Exception as _e:
                                print(f'      ⚠ Erro ao carregar tabela_valores.json: {_e}')

                            try:
                                contrato_cliente = item['dados_processo']['contrato_cliente']
                            except KeyError:
                                print(f'      ⚠ Ficha {ficha} → contrato_cliente não encontrado')
                                continue

                            _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])

                            entrada_processo = _dados_tabela[0].get('ENTRADA_PROCESSO', 0) if len(_dados_tabela) > 0 else 0
                            encerramento_processo = _dados_tabela[1].get('ENCERRAMENTO_PROCESSO', 0) if len(_dados_tabela) > 1 else 0
                            acordo = _dados_tabela[2].get('ACORDO', 0) if len(_dados_tabela) > 2 else 0
                            improcedencia = _dados_tabela[3].get('IMPROCEDENCIA', 0) if len(_dados_tabela) > 3 else 0
                            extincao = _dados_tabela[4].get('EXTINCAO', 0) if len(_dados_tabela) > 4 else 0
                            valor_migracao = _dados_tabela[5].get('MIGRACOES', 0) if len(_dados_tabela) > 5 else 0

                            
                            if valor_migracao in array_valores:
                                migrado = True
                                valor_base = valor_migracao + encerramento_processo
                                texto_migrado = "ENTRADA_PROCESSO_MIGRADO"
                                item['migrado'] = 'Sim'
                            else:
                                migrado = False
                                valor_base = entrada_processo + encerramento_processo
                                texto_migrado = "ENTRADA_PROCESSO"
                                item['migrado'] = 'Não'

                            if contrato_cliente == 938:
                                item['dados_processo']['materia_sigla'] = 'CIV'
                                
                            elif contrato_cliente == 939:
                                item['dados_processo']['materia_sigla'] = 'JEC'
                            else:
                                pdb.set_trace()  # Debug: para contrato_cliente diferente de 938 ou 939


                            # Em andamento - 1
                            # Sentença favorável - 2
                            # Sentença desfavorável - 3
                            # Acordo pré sentença - 4
                            # Acordo pós sentença - 5
                            # Desistência - 6
                            # Extinção sem resolução de mérito - 7
                            # Extinção com resolução de mérito - 8
                            # Suspensão - 9

                            resultado_situacao = item['dados_processo']['resultado_situacao'] 

                            if resultado_situacao == 1:
                                continue

                            numero_integracao = item['dados_processo']['numero_integracao']

                            item['valor_tabela_base'] = 0
                            item['conciliacao_errada'] = 'sim'
                            item['valor_divergencia'] = ''
                            item['a_fazer'] = f'Verificar numero de contrato cliente incorreto'
                            item['motivo_conciliacao_errada'] = f'Sem conciliarão possível, contrato cliente {contrato_cliente} não tem tabela de valores definida para comparação'

                            if resultado_situacao == 2: # Sentença favorável - 2
                                item['valor_tabela_base'] = valor_receber = valor_base + improcedencia
                                texto = " + IMPROCEDÊNCIA"

                            elif resultado_situacao == 3: # Sentença desfavorável - 3
                                item['valor_tabela_base'] = valor_receber = valor_base
                                texto = ""

                            elif resultado_situacao == 4: # Acordo pré sentença - 4
                                item['valor_tabela_base'] = valor_receber = valor_base + acordo   
                                texto = " + ACORDO"

                            elif resultado_situacao == 5: # Acordo pós sentença - 5
                                item['valor_tabela_base'] = valor_receber = valor_base + acordo
                                texto = " + ACORDO"

                            elif resultado_situacao == 6: # Desistência - 6
                                item['valor_tabela_base'] = valor_receber = valor_base    
                                texto = ""                                                                                                                                    

                            elif resultado_situacao == 7: # Extinção sem resolução de mérito - 7
                                item['valor_tabela_base'] = valor_receber = valor_base + extincao
                                texto = " + EXTINÇÃO"

                            elif resultado_situacao == 8: # Extinção com resolução de mérito - 8
                                item['valor_tabela_base'] = valor_receber = valor_base + extincao
                                texto = " + EXTINÇÃO"

                            else:
                                pdb.set_trace()  # Debug:  para resultado_situacao diferente de 1 a 8


                            if valor_recebido < valor_receber:
                                                                            
                                item['conciliacao_errada'] = 'sim'
                                item['valor_divergencia'] = valor_recebido - valor_receber
                                item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor do que a receber ({valor_receber}),  {texto_migrado} + ENCERRAMENTO_PROCESSO {texto} para tabela de valores para contrato cliente {contrato_cliente}'
                                item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que valor a receber ({valor_receber})'
                                print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                            elif valor_recebido == valor_receber:

                                item['conciliacao_errada'] = 'nao'
                                item['valor_divergencia'] = 0
                                item['a_fazer'] = f'Valor recebido está correto, conforme valor a receber ({valor_receber}) tabela de valores para contrato cliente {contrato_cliente}'
                                item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual ao valor a receber ({valor_receber})'
                                print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                        
                            elif valor_recebido > valor_receber:

                                item['conciliacao_errada'] = 'sim'
                                item['valor_divergencia'] = valor_recebido - valor_receber
                                item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que valor a receber ({valor_receber}) tabela de valores para contrato cliente {contrato_cliente}'
                                item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que valor a receber ({valor_receber})'
                                print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

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

        atualizar_proxima_execucao(168)

        api_logout()

    except Exception as e:
        print(f'\n✗ ERRO CRÍTICO na automação: {e}')
        traceback.print_exc()


if __name__ == '__main__':
    main()
