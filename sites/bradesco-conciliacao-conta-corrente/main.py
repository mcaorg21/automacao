#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/bradesco-conciliacao-conta-corrente/main.py

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


def atualizar_datas_execucao():
    """Atualiza data_inicial (hoje-8) e data_final (hoje) no config.json."""
    global DATA_INICIAL, DATA_FIM
    DATA_INICIAL = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
    DATA_FIM = datetime.now().strftime('%Y-%m-%d')
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

        atualizar_datas_execucao()

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

        CONTAS_CORRENTE = "1449"
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
                            if _resultado_ficha and isinstance(_resultado_ficha, list) and len(_resultado_ficha) > 0:
                                item['lancamentos_ficha'] = _resultado_ficha

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
                            #     print(f'      ✓ Ficha {ficha} → pasta={processos[-1].get("numero_integracao", "")}')

                            #     _materia_cod = processos[-1].get('materia')

                            #     match _materia_cod:
                            #         case 1:
                            #             item['dados_processo']['materia_descricao'] = 'CÍVEL - FÓRUM'
                            #             item['dados_processo']['materia_sigla'] = 'CIV'
                            #         case 2:
                            #             item['dados_processo']['materia_descricao'] = 'CÍVEL - JUIZADO ESPECIAL'
                            #             item['dados_processo']['materia_sigla'] = 'JEC'
                            #         case 3:
                            #             item['dados_processo']['materia_descricao'] = 'Trabalhista'
                            #             item['dados_processo']['materia_sigla'] = 'TRA'
                            #         case 4:
                            #             item['dados_processo']['materia_descricao'] = 'ÓRGÃOS ADMINISTRATIVOS'
                            #         case 5:
                            #             item['dados_processo']['materia_descricao'] = 'Tributário'
                            #         case 6:
                            #             item['dados_processo']['materia_descricao'] = 'Criminal'
                            #         case 7:
                            #             item['dados_processo']['materia_descricao'] = 'Empresarial'
                            #         case 9:
                            #             item['dados_processo']['materia_descricao'] = 'TRATATIVA DE ACORDO'
                            #         case 10:
                            #             item['dados_processo']['materia_descricao'] = 'Consultoria'
                            #         case 11:
                            #             item['dados_processo']['materia_descricao'] = 'DELEGACIA ESTADUAL'
                            #         case 12:
                            #             item['dados_processo']['materia_descricao'] = 'TREINAMENTO'
                            #         case 13:
                            #             item['dados_processo']['materia_descricao'] = 'Tribunal de Justiça'
                            #         case 14:
                            #             item['dados_processo']['materia_descricao'] = 'CEJUSC'
                            #             item['dados_processo']['materia_sigla'] = 'CEJUSC'
                            #         case 15:
                            #             item['dados_processo']['materia_descricao'] = 'Faturamentos'
                            #         case 16:
                            #             item['dados_processo']['materia_descricao'] = 'teste Helen'
                            #         case 17:
                            #             item['dados_processo']['materia_descricao'] = 'Execução Fiscal IPVA'
                            #         case 18:
                            #             item['dados_processo']['materia_descricao'] = 'ALVARÁ JUDICIAL'
                            #         case _:
                            #             item['dados_processo']['materia_descricao'] = f'DESCONHECIDO ({_materia_cod})'

                            # else:
                            #     print(f'      ⚠ Ficha {ficha} → nenhum processo encontrado')
                            #     continue

                            _tabela_valores_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tabela_valores.json')
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

                            # array_contratos_invalidos = ['BRAD-2600035227']
                                                         
                            # if numero_integracao in array_contratos_invalidos:
                            #     continue

                            #pj = item['dados_processo']['pj']

                            item['valor_tabela_base'] = 0
                            item['conciliacao_errada'] = 'sim'
                            item['valor_divergencia'] = ''
                            item['a_fazer'] = f'Verificar numero de contrato cliente incorreto'
                            item['motivo_conciliacao_errada'] = f'Sem conciliarão possível, contrato cliente {contrato_cliente} não tem tabela de valores definida para comparação'

                            if contrato_cliente == 880:
                                
                                item['dados_processo']['materia_sigla'] = 'CIV'

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])

                                if resultado_situacao == 3:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros

                                    if len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'indefinido'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
    

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                        
                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    else:
                                        
                                        pdb.set_trace() #debug 880_3_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 2:

                                    _ultimo_valor = list(_dados_tabela[-1].values())[0] if _dados_tabela and _dados_tabela[-1] else 0
                                    _soma_1_2_4 = sum(list(d.values())[0] for d in _dados_tabela[:2] if d) + _ultimo_valor
                                    item['valor_tabela_base'] = _soma_1_2_4

                                    if len(_resultado_ficha) == 1:
                                        
                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_1_2_4})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
    
                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_1_2_4:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                       
                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 4:

                                        if valor_recebido < _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                       
                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        
                                    else:   
                                        pdb.set_trace() #debug 880_2_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 4:
                                    
                                    _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                    item['valor_tabela_base'] = _soma_3_primeiros

                                    if len(_resultado_ficha) == 1:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido > _soma_3_primeiros:    

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO  ({_soma_3_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido > _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO  ({_soma_3_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido > _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO E ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')



                                    else:
                                        pdb.set_trace() #debug 880_4_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 5:

                                    _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                    item['valor_tabela_base'] = _soma_3_primeiros

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor que tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 2:

                                        if  valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido > _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    elif len(_resultado_ficha) ==3:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido > _soma_3_primeiros:    

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 880_5_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 6:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')   

                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 880_6_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 7:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_coniliacao_errada"]} → divergencia={item["valor_divergencia"]}') 

                                    elif len(_resultado_ficha) == 3:
                                        
                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                        
                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')


                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')



                                    else:
                                        pdb.set_trace() #debug 880_7_len, quais campos usar para comparação, et

                                elif resultado_situacao == 8:

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] =  valor_recebido
                                    item['a_fazer'] = f'Verificar lançamentos, houve perda de patrocínio do processo. Valor recebido ({valor_recebido})'
                                    item['motivo_conciliacao_errada'] = f'Verificar lançamentos, houve perda de patrocínio do processo. Valor recebido ({valor_recebido})'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
    
                                
                                else:
                                    pdb.set_trace() #debug 880_0, quais campos usar para comparação, etc

                            elif contrato_cliente == 947:

                                item['dados_processo']['materia_sigla'] = 'JEC'

                                print(f'⚠ Contrato cliente tipo: {contrato_cliente}')

                                _dados_tabela = _tabela_valores.get(str(contrato_cliente), {}).get('dados', [])
                                _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                item['valor_tabela_base'] = _soma_3_primeiros
                                print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}')                               

                                if resultado_situacao == 2:

                                    _ultimo_valor = list(_dados_tabela[-1].values())[0] if _dados_tabela and _dados_tabela[-1] else 0
                                    _soma_1_2_4 = sum(list(d.values())[0] for d in _dados_tabela[:2] if d) + _ultimo_valor
                                    item['valor_tabela_base'] = _soma_1_2_4

                                    if len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_1_2_4:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    

                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_1_2_4:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 4:

                                        if valor_recebido < _soma_1_2_4:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_1_2_4:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_1_2_4:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_1_2_4
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')



                                    elif len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_1_2_4 - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_1_2_4}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e IMPROCEDENCIA ({_soma_1_2_4})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:   
                                        pdb.set_trace() #debug 947_2_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 3:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros

                                    if len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')        

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                            

                                    elif len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 947_3_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 4:

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif valor_recebido > _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_3_primeiros:    

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 947_4_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 6:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 2:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                               
                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')                   

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de desistência'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 947_6_len, quais campos usar para comparação, etc
                            
                                elif resultado_situacao == 7:

                                    _soma_2_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:2] if d)
                                    item['valor_tabela_base'] = _soma_2_primeiros
                                    print(f'      ✓ Soma 2 primeiros da tabela: {_soma_2_primeiros}') 
                                    
                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                       
                                    elif len(_resultado_ficha) == 2:
                                        
                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')    
                                        
                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')   
                                        
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente}'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 3:

                                        if valor_recebido < _soma_2_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_2_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido == _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}') 
                                    
                                        elif valor_recebido > _soma_2_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_2_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de extinção sem resolução de mérito'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO E ENCERRAMENTO_PROCESSO ({_soma_2_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    else:
                                        pdb.set_trace() #debug 947_7_len, quais campos usar para comparação, etc    

                                elif resultado_situacao == 5:

                                    _soma_3_primeiros = sum(list(d.values())[0] for d in _dados_tabela[:3] if d)
                                    item['valor_tabela_base'] = _soma_3_primeiros
                                    print(f'      ✓ Soma 3 primeiros da tabela: {_soma_3_primeiros}') 

                                    if len(_resultado_ficha) == 1:

                                        item['conciliacao_errada'] = 'indefinido'
                                        item['valor_divergencia'] = valor_recebido
                                        item['a_fazer'] = f'Verificar lançamentos faltantes, PODE SER PROCESSO MIGRADO, pois valor recebido ({valor_recebido}) é menor que tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                        item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                        print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')

                                    elif len(_resultado_ficha) == 2:

                                        if  valor_recebido < _soma_3_primeiros:
                                            
                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = _soma_3_primeiros - valor_recebido
                                            item['a_fazer'] = f'Verificar lançamentos faltantes, pois valor recebido ({valor_recebido}) é menor ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) menor que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')  

                                        elif valor_recebido == _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'nao'
                                            item['valor_divergencia'] = 0
                                            item['a_fazer'] = f'Valor recebido está correto, conforme soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) igual à soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            print(f'      ✓ Conciliação correta: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                        
                                        elif valor_recebido > _soma_3_primeiros:

                                            item['conciliacao_errada'] = 'sim'
                                            item['valor_divergencia'] = valor_recebido - _soma_3_primeiros
                                            item['a_fazer'] = f'Verificar lançamentos extras, pois valor recebido ({valor_recebido}) é maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros}) tabela de valores para contrato cliente {contrato_cliente} em caso de acordo'
                                            item['motivo_conciliacao_errada'] = f'Valor recebido ({valor_recebido}) maior que soma de ENTRADA_PROCESSO, ENCERRAMENTO_PROCESSO e ACORDO ({_soma_3_primeiros})'   
                                            print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
                                    
                                    else:
                                        pdb.set_trace() #debug 947_5_len, quais campos usar para comparação, etc

                                elif resultado_situacao == 8:

                                    item['conciliacao_errada'] = 'indefinido'
                                    item['valor_divergencia'] =  valor_recebido
                                    item['a_fazer'] = f'Verificar lançamentos, houve perda de patrocínio do processo. Valor recebido ({valor_recebido})'
                                    item['motivo_conciliacao_errada'] = f'Verificar lançamentos, houve perda de patrocínio do processo. Valor recebido ({valor_recebido})'
                                    print(f'      ✗ Conciliação errada: {item["motivo_conciliacao_errada"]} → divergencia={item["valor_divergencia"]}')
    
                                
                                else:
                                    pdb.set_trace() #debug 947_0, quais campos usar para comparação, etc 

                            else:

                                item['conciliacao_errada'] = 'sim'
                                item['valor_divergencia'] = 'N/A'
                                item['a_fazer'] = f'Contrato cliente incorreto'
                                item['motivo_conciliacao_errada'] = f'Contrato cliente incorreto'
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

    except Exception as e:
        print(f'\n✗ ERRO CRÍTICO na automação: {e}')
        traceback.print_exc()


if __name__ == '__main__':
    main()
