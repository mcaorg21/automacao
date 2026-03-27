import sys
import os

print("=== TESTE DE EXECUCAO - PASSO A PASSO ===\n")

# Adiciona o caminho dos módulos
sys.path.append('C:\\www\\automacao')

print("[1/10] Imports basicos... ", end='', flush=True)
import time, subprocess, csv, json, shutil, re
from datetime import datetime, timedelta
from pathlib import Path
import traceback
from PyPDF2 import PdfMerger
import requests
print("OK")

print("[2/10] Selenium... ", end='', flush=True)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
print("OK")

print("[3/10] cpj_api... ", end='', flush=True)
from cpj_api import (
    set_api_credentials,
    api_login,
    api_logout,
    api_post,
    api_buscar_lancamentos,
    processar_lancamentos,
    processar_documentos_registros
)
print("OK")

print("[4/10] cpj_app... ", end='', flush=True)
from cpj_app import (
    set_cpj_config,
    get_system_dpi,
    get_resolution,
    auto_scale_coords,
    smart_click,
    valida_data,
    sleep_with_countdown,
    click_image,
    wait_for_element,
    to_snake_case,
    clean_planilha_folder,
    clean_pdf_merge_folder,
    close_controle_processos_windows,
    open_cpj_application,
    close_cpj_application,
    perform_login,
    click_menu,
    click_printer,
    navigate_to_analise_lancamento,
    navigate_to_relatorio_conta,
    fill_cliente_and_dates,
    export_file,
    close_window,
    open_search_area,
    process_csv,
    fill_descritivo_pdf,
    fill_planilha_modelo,
    fill_planilha_modelo_v2,
    fill_planilha_modelo_v4,
    fill_planilha_modelo_v5,
    process_record_for_pdf
)
print("OK")

print("[5/10] Carregando config.json... ", end='', flush=True)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:    config = json.load(f)
print("OK")

print("[6/10] Validando configuracoes... ", end='', flush=True)
NUMERO_RECIBO = config['numero_recibo']
DATA_INICIAL_PESQUISA = datetime.strptime(config['data_inicial'], "%d/%m/%Y")
DATA_FINAL_PESQUISA = datetime.strptime(config['data_final'], "%d/%m/%Y")

if not NUMERO_RECIBO.isdigit():
    raise ValueError("INFORME O NUMERO DO RECIBO VALIDO")

if DATA_INICIAL_PESQUISA > DATA_FINAL_PESQUISA:
    raise ValueError("DATA_INICIAL_PESQUISA nao pode ser maior que DATA_FINAL_PESQUISA")

DATA_INICIAL_PESQUISA = DATA_INICIAL_PESQUISA.strftime('%d/%m/%Y')
DATA_FINAL_PESQUISA = DATA_FINAL_PESQUISA.strftime('%d/%m/%Y')
print("OK")

print("[7/10] Configuracoes:")
print(f"  - Numero Recibo: {NUMERO_RECIBO}")
print(f"  - Data Inicial: {DATA_INICIAL_PESQUISA}")
print(f"  - Data Final: {DATA_FINAL_PESQUISA}")

print("[8/10] Configurando cpj_api... ", end='', flush=True)
set_api_credentials(
    base_url='https://app.leviatan.com.br/dcncadv/cpj/agnes',
    login='api',
    password='2025',
    json_path=os.path.join(os.path.dirname(__file__), 'planilha', 'importados.json'),
    planilha_path=os.path.join(os.path.dirname(__file__), 'planilha'),
    pdf_merge_path=os.path.join(os.path.dirname(__file__), 'pdf_merge')
)
print("OK")

print("[9/10] Configurando cpj_app... ", end='', flush=True)
# Nao vou chamar set_cpj_config porque ele pode travar em get_system_dpi ou tkinter
print("PULADO (pode travar)")

print("[10/10] Teste concluido!")

print("\n=== RESULTADO ===")
print("SUCESSO! O problema esta provavelmente na funcao set_cpj_config()")
print("ou nas funcoes helper como get_system_dpi() ou get_resolution()")
print("que usam tkinter e ctypes.windll.user32")
