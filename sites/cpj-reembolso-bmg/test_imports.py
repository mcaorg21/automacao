import sys
import traceback

print("=" * 60)
print("TESTE DE IMPORTAÇÃO - main.py")
print("=" * 60)

# Adiciona o caminho dos módulos
sys.path.append('C:\\www\\automacao')

# Teste 1: Imports básicos
try:
    print("\n[1/5] Testando imports básicos...")
    import time, os, subprocess, csv, json, shutil, re
    from datetime import datetime, timedelta
    from pathlib import Path
    from PyPDF2 import PdfMerger
    print("✓ Imports básicos OK")
except Exception as e:
    print(f"✗ Erro nos imports básicos: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 2: Selenium
try:
    print("\n[2/5] Testando imports do Selenium...")
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import requests
    print("✓ Selenium OK")
except Exception as e:
    print(f"✗ Erro no Selenium: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 3: CPJ API
try:
    print("\n[3/5] Testando imports do cpj_api...")
    from cpj_api import (
        set_api_credentials,
        api_login,
        api_logout,
        api_post,
        api_buscar_lancamentos,
        processar_lancamentos,
        processar_documentos_registros
    )
    print("✓ cpj_api OK")
except Exception as e:
    print(f"✗ Erro no cpj_api: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 4: CPJ App
try:
    print("\n[4/5] Testando imports do cpj_app...")
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
    print("✓ cpj_app OK")
except Exception as e:
    print(f"✗ Erro no cpj_app: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 5: Verificar config.json
try:
    print("\n[5/5] Verificando config.json...")
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        print(f"✗ Arquivo config.json não encontrado: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"✓ config.json OK")
    print(f"  - numero_recibo: {config.get('numero_recibo')}")
    print(f"  - data_inicial: {config.get('data_inicial')}")
    print(f"  - data_final: {config.get('data_final')}")
    
    # Validação do número do recibo
    if not config['numero_recibo'].isdigit():
        print(f"⚠ AVISO: numero_recibo não é numérico: '{config['numero_recibo']}'")
    
    # Validação das datas
    try:
        data_inicial = datetime.strptime(config['data_inicial'], "%d/%m/%Y")
        data_final = datetime.strptime(config['data_final'], "%d/%m/%Y")
        
        if data_inicial > data_final:
            print(f"⚠ AVISO: data_inicial é maior que data_final")
    except Exception as e:
        print(f"⚠ AVISO: Erro ao validar datas: {e}")
        
except Exception as e:
    print(f"✗ Erro ao verificar config.json: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print("\nO problema não está nos imports ou no config.json.")
print("Tente executar o main.py e veja o que acontece.")
