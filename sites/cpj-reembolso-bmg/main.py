import time
import os
import subprocess
import csv
import json
import pdb
import shutil
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
import traceback
from PyPDF2 import PdfMerger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Adiciona o caminho dos módulos
sys.path.append('C:\\www\\automacao')

# Importa funções do módulo CPJ API
from cpj_api import (
    set_api_credentials,
    api_login,
    api_logout,
    api_post,
    api_buscar_lancamentos,
    processar_lancamentos,
    processar_documentos_registros
)

# Importa funções do módulo CPJ App (aplicativo desktop)
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

# Configurações da API (serão passadas para o módulo)
API_BASE_URL = 'https://app.leviatan.com.br/dcncadv/cpj/agnes'
API_LOGIN = 'api.teste5'
API_PASSWORD = 'dcnc2025'

# Configurações
CPJ_PATH = r'C:\CPJ3C_Client\cpj3cclient.exe'
LOGIN = 'MOAO'
PASSWORD = 'LM0G'
PLANILHA_PATH = r'C:\www\automacao\sites\cpj-reembolso-bmg\planilha'
CSV_PATH = os.path.join(PLANILHA_PATH, 'importados.csv')
JSON_PATH = os.path.join(PLANILHA_PATH, 'importados.json')

#resolucao padrao
BASE_DPI = 144
BASE_WIDTH = 2560
BASE_HEIGHT = 1600

# Caminhos das imagens para reconhecimento
IMAGES_PATH = r'C:\www\automacao\sites\cpj-reembolso-bmg\images'
IMAGE_MENU_ICON = os.path.join(IMAGES_PATH, 'menu_icon.png')
IMAGE_MENU_CONTA_CORRENTE = os.path.join(IMAGES_PATH, 'menu_conta_corrente.png')
IMAGE_PRINTER_BUTTON = os.path.join(IMAGES_PATH, 'impressora.png')
IMAGE_ANALISE_LANCAMENTO = os.path.join(IMAGES_PATH, 'analise_lancamento.png')
IMAGE_RELATORIO_CONTA = os.path.join(IMAGES_PATH, 'relatorio_conta.png')
IMAGE_PASTA = os.path.join(IMAGES_PATH, 'pasta.png')

#caminho dos pdfs temporarios
PDF_FOLDER = f'C:\\Users\\{os.environ.get("USERNAME")}\\Downloads\\pdf_cpj'
PDF_MERGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_merge')

# Caminho da planilha modelo
PLANILHA_MODELO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planilha_modelo', 'bmg', 'planilha_modelo_custas.xls')
PLANILHA_MODELO_PATH_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planilha_modelo', 'bmg', 'planilha_modelo_custas_2.xls')
PLANILHA_MODELO_EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planilha_modelo_excel', 'planilha_modelo_custas_modelo.xls')

# Caminho do documento modelo
DOCX_MODELO = r'C:\www\automacao\sites\cpj-reembolso-bmg\documento_modelo\bmg\descritivo_custas.docx'
DOCX_OUTPUT = r'C:\www\automacao\sites\cpj-reembolso-bmg\documento_modelo\bmg\descritivo_custas_preenchido.docx'
PDF_OUTPUT = r'C:\www\automacao\sites\cpj-reembolso-bmg\documento_modelo\bmg\descritivo_custas_preenchido.pdf'

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Carrega parâmetros: se tiver args usa args, senão lê do config.json
if len(sys.argv) >= 4:
    # Modo linha de comando
    NUMERO_RECIBO = sys.argv[1]
    DATA_INICIAL_PESQUISA = datetime.strptime(sys.argv[2], "%d/%m/%Y")
    DATA_FINAL_PESQUISA = datetime.strptime(sys.argv[3], "%d/%m/%Y")
else:
    # Modo config.json
    print("Nenhum argumento fornecido. Lendo configurações de config.json...")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    NUMERO_RECIBO = config['numero_recibo']
    DATA_INICIAL_PESQUISA = datetime.strptime(config['data_inicial'], "%d/%m/%Y")
    DATA_FINAL_PESQUISA = datetime.strptime(config['data_final'], "%d/%m/%Y")

if not NUMERO_RECIBO.isdigit():
    raise ValueError("INFORME O NÚMERO DO RECIBO VÁLIDO")

# regra básica de sanidade
if DATA_INICIAL_PESQUISA > DATA_FINAL_PESQUISA:
    raise ValueError("DATA_INICIAL_PESQUISA não pode ser maior que DATA_FINAL_PESQUISA")

DATA_INICIAL_PESQUISA = DATA_INICIAL_PESQUISA.strftime('%d/%m/%Y')
DATA_FINAL_PESQUISA = DATA_FINAL_PESQUISA.strftime('%d/%m/%Y')

print(f"Configurações carregadas:")
print(f"  - Número Recibo: {NUMERO_RECIBO}")
print(f"  - Data Inicial: {DATA_INICIAL_PESQUISA}")
print(f"  - Data Final: {DATA_FINAL_PESQUISA}")

# Configura as credenciais da API no módulo CPJ
set_api_credentials(
    base_url=API_BASE_URL,
    login=API_LOGIN,
    password=API_PASSWORD,
    json_path=JSON_PATH,
    planilha_path=PLANILHA_PATH,
    pdf_merge_path=PDF_MERGE_PATH
)

# Configura as variáveis do módulo CPJ App
set_cpj_config(
    cpj_path=CPJ_PATH,
    login=LOGIN,
    password=PASSWORD,
    planilha_path=PLANILHA_PATH,
    csv_path=CSV_PATH,
    json_path=JSON_PATH,
    images_path=IMAGES_PATH,
    pdf_folder=PDF_FOLDER,
    pdf_merge_path=PDF_MERGE_PATH,
    planilha_modelo_path=PLANILHA_MODELO_PATH,
    planilha_modelo_path_2=PLANILHA_MODELO_PATH_2,
    planilha_modelo_excel_path=PLANILHA_MODELO_EXCEL_PATH,
    docx_modelo=DOCX_MODELO,
    docx_output=DOCX_OUTPUT,
    pdf_output=PDF_OUTPUT,
    data_inicial_pesquisa=DATA_INICIAL_PESQUISA,
    data_final_pesquisa=DATA_FINAL_PESQUISA,
    numero_recibo=NUMERO_RECIBO,
    base_dpi=BASE_DPI,
    base_width=BASE_WIDTH,
    base_height=BASE_HEIGHT
)

# ============================================================================
# MÓDULOS CONFIGURADOS (cpj_api e cpj_app)
# ============================================================================

# ============================================================================
# FUNÇÕES WEB (Selenium - Exyon BMG)
# ============================================================================

def open_chrome_browser():
    """Abre o navegador Chrome usando Selenium"""
    try:
        print('\nLimpando pasta planilha...')
        
        if not os.path.exists(PLANILHA_PATH):
            os.makedirs(PLANILHA_PATH)
            print(f'✓ Pasta criada: {PLANILHA_PATH}')
            return
        
        for file in os.listdir(PLANILHA_PATH):
            file_path = os.path.join(PLANILHA_PATH, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f'✓ Arquivo removido: {file}')
        
        print('✓ Pasta planilha limpa com sucesso!')
    except Exception as e:
        print(f'✗ Erro ao limpar pasta planilha: {e}')
        raise

# ============================================================================
# FUNÇÕES WEB (Selenium - Exyon BMG)
# ============================================================================

def open_chrome_browser():
    """Abre o navegador Chrome usando Selenium"""
    try:
        print('\nAbrindo navegador Chrome...')
        
        # Configura opções do Chrome
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Descomente para rodar sem interface gráfica
        #chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=1200,800')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
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
        
        import traceback
        traceback.print_exc()
        raise

def login_web_exyon_bmg(driver):
    """Faz login no sistema web"""
    try:
        print('\nRealizando login no sistema...')

        # Navegar para a URL de login
        print('\nAcessando sistema jurídico...')
        driver.get('https://juridico.bancobmg.com.br/Paginas/Principal/_FSet_Abertura.asp?Pagina=Logon')
        print('✓ Página carregada')
        
        # Aguarda a página carregar
        wait = WebDriverWait(driver, 10)
        
        # Encontra e preenche o campo de login
        print('Preenchendo campo de login...')
        login_input = wait.until(EC.presence_of_element_located((By.ID, 'txtcd_Logon')))
        login_input.clear()
        login_input.send_keys('rafael.dias')
        print('✓ Login digitado: rafael.dias')
        
        # Encontra e preenche o campo de senha
        print('Preenchendo campo de senha...')
        senha_input = driver.find_element(By.ID, 'txtcd_Pwd')
        senha_input.clear()
        senha_input.send_keys('npisv9VSb0lZQGsR')
        print('✓ Senha digitada')
        
        # Clica no botão OK
        print('Clicando no botão OK...')
        btn_ok = driver.find_element(By.ID, 'btOK')
        btn_ok.click()
        print('✓ Botão OK clicado!')
        
        # Aguarda um pouco para o login processar
        time.sleep(2)
        print('✓ Login realizado com sucesso!')
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao fazer login: {e}')
        import traceback
        traceback.print_exc()
        return False

def selecionar_unidade(driver):
    """Seleciona a unidade após o login"""
    try:
        print('\nAguardando seleção de unidade...')
        
        # Aguarda o elemento cmbUnidade aparecer
        wait = WebDriverWait(driver, 10)
        print('Aguardando elemento cmbUnidade aparecer...')
        select_element = wait.until(EC.presence_of_element_located((By.ID, 'cmbUnidade')))
        print('✓ Elemento cmbUnidade encontrado')
        
        # Cria objeto Select para manipular o dropdown
        select = Select(select_element)
        
        # Seleciona a opção com value 106
        print('Selecionando unidade (value=106)...')
        select.select_by_value('106')
        print('✓ Unidade 106 selecionada')
        
        # Clica no botão Entrar (btOk)
        print('Clicando no botão Entrar...')
        btn_entrar = driver.find_element(By.ID, 'btOk')
        btn_entrar.click()
        print('✓ Botão Entrar clicado!')
        
        # Aguarda um pouco para processar
        time.sleep(2)
        print('✓ Unidade selecionada com sucesso!')
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao selecionar unidade: {e}')
        import traceback
        traceback.print_exc()
        return False

def executar_script_menu(driver):
    """Executa o script JavaScript para mudar o menu"""
    try:
        print('\nExecutando script de menu...')
        
        # Aguarda um pouco para garantir que a página carregou
        time.sleep(2)
        
        # Muda para o frame FraMenu
        print('Mudando para o frame FraMenu...')
        wait = WebDriverWait(driver, 10)
        frame = wait.until(EC.presence_of_element_located((By.ID, 'FraMenu')))
        driver.switch_to.frame(frame)
        print('✓ Frame FraMenu encontrado e selecionado')
        
        # Executa o script JavaScript
        script = "MudaClasseMenu('Menu_1', '6');Carrega_Combo('FI');"
        print(f'Executando: {script}')
        driver.execute_script(script)
        print('✓ Script executado com sucesso!')
        
        # Volta para o contexto principal
        driver.switch_to.default_content()
        print('✓ Voltou ao contexto principal')
        
        # Aguarda o script processar
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao executar script: {e}')
        import traceback
        traceback.print_exc()
        return False

def executar_script_menu_lateral(driver):
    """Executa o script JavaScript do menu lateral"""
    try:
        print('\nExecutando script de menu lateral...')
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Muda para o frame FraMenu
        print('Mudando para o frame FraMenu...')
        wait = WebDriverWait(driver, 10)
        frame = wait.until(EC.presence_of_element_located((By.ID, 'FraMenu')))
        driver.switch_to.frame(frame)
        print('✓ Frame FraMenu encontrado e selecionado')
        
        # Executa o script JavaScript
        script = "MudaClasseMenuLateral('LNF');Mnu_Click_Handler('LNF');parent.document.getElementById('__submenu').style.display='none';parent.document.getElementById('__submenu').innerHTML = '';document.getElementById('__setinha').src = 'imagens/icone-select.png';"
        print(f'Executando script do menu lateral...')
        driver.execute_script(script)
        print('✓ Script do menu lateral executado com sucesso!')
        
        # Volta para o contexto principal
        driver.switch_to.default_content()
        print('✓ Voltou ao contexto principal')
        
        # Aguarda o script processar
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao executar script do menu lateral: {e}')
        import traceback
        traceback.print_exc()
        return False

def executar_script_classificacao(driver):
    """Executa o script de classificação financeira e seleciona CUSTAS"""
    try:
        print('\nExecutando script de classificação financeira...')
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Muda para o frame FraDetalhe
        print('Mudando para o frame FraDetalhe...')
        wait = WebDriverWait(driver, 10)
        frame = wait.until(EC.presence_of_element_located((By.ID, 'FraDetalhe')))
        driver.switch_to.frame(frame)
        print('✓ Frame FraDetalhe encontrado e selecionado')
        
        # Guarda a janela principal
        janela_principal = driver.current_window_handle
        
        # Executa o script que abre o popup
        script = "searcher('ClassificacaoFinanceira_List_pop.asp');"
        print(f'Executando: {script}')
        driver.execute_script(script)
        print('✓ Script executado - popup deve ter aberto')
        
        # Aguarda o popup abrir
        time.sleep(2)
        
        # Muda para a nova janela popup
        print('Procurando janela popup...')
        todas_janelas = driver.window_handles
        for janela in todas_janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                print('✓ Popup encontrado e selecionado')
                break
        
        # Aguarda o frame do popup carregar e muda para ele
        print('Aguardando frame do popup...')
        time.sleep(1)
        frame_popup = wait.until(EC.presence_of_element_located((By.XPATH, '/html/frameset/frame')))
        driver.switch_to.frame(frame_popup)
        print('✓ Frame do popup encontrado e selecionado')
        
        # Executa o script select no popup
        script_select = "select('34','CUSTAS');"
        print(f'Executando no popup: {script_select}')
        driver.execute_script(script_select)
        print('✓ Script select executado no popup!')
        
        # Aguarda processar
        time.sleep(2)
        
        # Volta para a janela principal
        driver.switch_to.window(janela_principal)
        print('✓ Voltou à janela principal')
        
        # Volta para o contexto padrão
        driver.switch_to.default_content()
        print('✓ Voltou ao contexto padrão')
        
        # Muda para o frame FraDetalhe para preencher a data
        print('Mudando para o frame FraDetalhe...')
        frame_detalhe = wait.until(EC.presence_of_element_located((By.ID, 'FraDetalhe')))
        driver.switch_to.frame(frame_detalhe)
        print('✓ Frame FraDetalhe selecionado')

        print('\nExecutando script de seleção de empresa...')
        
        # Aguarda um pouco
        time.sleep(2)

        # Guarda a janela principal
        janela_principal = driver.current_window_handle
        
        # Executa o script que abre o popup
        script = "searcher('Empresa_list_pop.asp');"
        print(f'Executando: {script}')
        driver.execute_script(script)
        print('✓ Script executado - popup deve ter aberto')
        
        # Aguarda o popup abrir
        time.sleep(2)
        
        # Muda para a nova janela popup
        print('Procurando janela popup...')
        todas_janelas = driver.window_handles
        for janela in todas_janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                print('✓ Popup encontrado e selecionado')
                break
        
        # Aguarda o frame do popup carregar e muda para ele
        print('Aguardando frame do popup...')
        time.sleep(1)
        frame_popup = wait.until(EC.presence_of_element_located((By.XPATH, '/html/frameset/frame')))
        driver.switch_to.frame(frame_popup)
        print('✓ Frame do popup encontrado e selecionado')
        
        # Executa o script select no popup
        script_select = "select('28','BANCO BMG S.A');"
        print(f'Executando no popup: {script_select}')
        driver.execute_script(script_select)
        print('✓ Script select executado no popup!')
        
        # Aguarda processar
        time.sleep(2)
        
        # Aguarda processar
        time.sleep(2)
        
        # Volta para a janela principal
        driver.switch_to.window(janela_principal)
        print('✓ Voltou à janela principal')
        
        # Volta para o contexto padrão
        driver.switch_to.default_content()
        print('✓ Voltou ao contexto padrão')
        
        # Muda para o frame FraDetalhe para preencher a data
        print('Mudando para o frame FraDetalhe...')
        frame_detalhe = wait.until(EC.presence_of_element_located((By.ID, 'FraDetalhe')))
        driver.switch_to.frame(frame_detalhe)
        print('✓ Frame FraDetalhe selecionado')
        
        # Aguarda o popup abrir
        return True
        
    except Exception as e:
        print(f'✗ Erro ao executar script de classificação: {e}')
        import traceback
        traceback.print_exc()
        return False

def executar_preenchimento_formulario(driver, valor_somado):
    """Executa o script de preenchimento do formulário"""
    try:
        print('\nExecutando preenchimento do formulário..')
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Preenche a data de emissão
        print('Preenchendo data de emissão...')
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        dt_emissao = driver.find_element(By.ID, 'dt_Emissao')
        dt_emissao.clear()
        dt_emissao.click()
        dt_emissao.send_keys(data_hoje)
        print(f'✓ Data de emissão preenchida: {data_hoje}')
        
        # Aguarda processar
        time.sleep(1)
        
        # Preenche o número da NF
        print('Solicitando número da NF...')
        #numero_nf = input('Digite o número da NF: ').strip()
        numero_nf = NUMERO_RECIBO
        
        print(f'Preenchendo número da NF: {numero_nf}...')
        nu_nf = driver.find_element(By.ID, 'nu_NF')
        nu_nf.clear()
        nu_nf.click()
        nu_nf.send_keys(numero_nf)
        print(f'✓ Número da NF preenchido: {numero_nf}')
        
        # Aguarda processar
        time.sleep(1)
        
        # Preenche o valor da nota
        print(f'Preenchendo valor da nota: {valor_somado}...')
        vl_nota = driver.find_element(By.ID, 'vl_Nota')
        vl_nota.clear()
        vl_nota.click()
        vl_nota.send_keys(valor_somado)
        print(f'✓ Valor da nota preenchido: {valor_somado}')
        
        # Aguarda processar
        # Faz upload do arquivo
        
        print(f'Fazendo upload do arquivo: {PLANILHA_MODELO_PATH}...')
        arquivo_input = driver.find_element(By.ID, 'ArqCarga')
        arquivo_input.send_keys(PLANILHA_MODELO_PATH)
        print(f'✓ Arquivo enviado: {PLANILHA_MODELO_PATH}')
        
        # Aguarda processar
        time.sleep(1)
        print('Abrindo arquivo no Excel...')
        os.startfile(PLANILHA_MODELO_PATH)

        # Aguarda o Excel abrir
        time.sleep(3)

        # Clica no botão Enviar
        print('Clicando no botão Enviar...')
        btn_enviar = driver.find_element(By.ID, 'btn_Enviar')
        btn_enviar.click()
        print('✓ Botão Enviar clicado!')
        
        # Aguarda alert aparecer
        time.sleep(1)
        
        # Aceita o alert que aparecer
        try:
            print('Aguardando alert...')
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            print('✓ Alert detectado, aceitando...')
            alert.accept()
            print('✓ Alert aceito!')
        except:
            print('⚠ Nenhum alert detectado')

        #Agora fecha o Excel programaticamente
        print('Fechando Excel...')
        os.system(f'taskkill /F /IM EXCEL.EXE')
                
        # Aguarda processar
        time.sleep(1)
        
        # Aguarda elemento aparecer
        print('Aguardando elemento aparecer...')

        fieldset_imgs = len(driver.find_elements(By.XPATH, '/html/body/fieldset/form/div[1]/fieldset/div/center/table/tbody/tr[3]/td/center/img'))
        itercaoes = 0
        while fieldset_imgs == 1:
            print('Elemento ainda não encontrado, aguardando mais 5 segundos...')
            time.sleep(5)
            fieldset_imgs = len(driver.find_elements(By.XPATH, '/html/body/fieldset/form/div[1]/fieldset/div/center/table/tbody/tr[3]/td/center/img'))
            itercaoes += 1
            if itercaoes >= 12:  # Limite de 1 minuto
                print('✗ Tempo esgotado aguardando o elemento aparecer')
                return False

        print('✓ Elemento encontrado!')
        
        # Aguarda processar
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao executar script de classificação: {e}')
        import traceback
        traceback.print_exc()
        return False

def formatar_numero_processo(numero_processo):
    """Formata o número do processo no padrão CNJ.
    
    Exemplo: 50000591620268210038 -> 5000059-16.2026.8.21.0038
    Padrão: NNNNNNN-DD.AAAA.J.TR.OOOO
    
    Args:
        numero_processo: Número do processo sem formatação (apenas dígitos)
        
    Returns:
        str: Número do processo formatado ou número original se não for possível formatar
    """
    try:
        # Remove caracteres não numéricos
        apenas_numeros = re.sub(r'[^0-9]', '', str(numero_processo))
        
        # Verifica se tem o tamanho correto (20 dígitos)
        if len(apenas_numeros) != 20:
            print(f'    ⚠ Tamanho inválido para formatação: {len(apenas_numeros)} dígitos (esperado 20)')
            return numero_processo
        
        # Aplica a máscara do padrão CNJ
        # NNNNNNN-DD.AAAA.J.TR.OOOO
        formatado = f'{apenas_numeros[0:7]}-{apenas_numeros[7:9]}.{apenas_numeros[9:13]}.{apenas_numeros[13]}.{apenas_numeros[14:16]}.{apenas_numeros[16:20]}'
        
        print(f'    ✓ Processo formatado: {apenas_numeros} -> {formatado}')
        return formatado
        
    except Exception as e:
        print(f'    ✗ Erro ao formatar processo: {e}')
        return numero_processo


def buscar_processo_alternativo(numero_integracao, numero_processo, nao_procurar_pelo_processo=None, tentativa=-1):
    """Busca processo alternativo pelo número de integração.
    Retorna o processo com a data mais antiga (key 'entrada').
    
    Args:
        numero_integracao: Número de integração do processo
        numero_processo: Número do processo
        nao_procurar_pelo_processo: Número do processo que não deve ser considerado
        tentativa: Número da tentativa atual
    Returns:
        str: Número do processo alternativo com data mais antiga ou None
    """
    print('XXXXXXXXXXXX TROCAR NA PLANILHA DE IMPORTAÇÃO  XXXXXXXXXXXX')
    print(f'  → Buscando processo alternativo para integração: {numero_integracao}')
    print(f'  → Tentativa: {tentativa}')
    
    # Faz requisição ao endpoint /api/v2/processo
    body = {
        "filter": {
            "_and": [
                {
                    "numero_integracao": {
                        "_eq": numero_integracao
                    }
                }
            ]
        },
        "limit": 100
    }
    
    response = api_post('/api/v2/processo', data=body)
    
    if response:
        print(f'  ✓ Resposta recebida com {len(response) if isinstance(response, list) else "N/A"} processos')
        
        # Percorre os processos buscando um com numero_processo diferente
        processos_list = response if isinstance(response, list) else response.get('data', response.get('items', []))
        
        processo_mais_antigo = None
        data_mais_antiga = None

        indice_resultados = 0 

        for processo in processos_list:
            numero_processo_resp = re.sub(r'[^0-9]', '', processo.get('numero_processo', ''))
            
            if numero_processo_resp != numero_processo:
                if tentativa >= 0 and tentativa == indice_resultados:
                    print(f'  → Tentando agora com numero de processo: {numero_processo_resp}')
                    return numero_processo_resp

                else:

                    print(f'  → Processo diferente encontrado: {numero_processo_resp} <> {numero_processo}')

                    # Obtém a data de entrada
                    data_entrada = processo.get('entrada')
                    
                    if data_entrada:
                        print(f'    Data de entrada: {data_entrada}')
                        
                        # Se é a primeira vez ou encontrou uma data mais antiga
                        if processo_mais_antigo is None or data_entrada < data_mais_antiga:
                            processo_mais_antigo = numero_processo_resp
                            data_mais_antiga = data_entrada
                            print(f'    ✓ Processo com data mais antiga atualizado: {numero_processo_resp} ({data_entrada})')
                
            indice_resultados += 1 

        if processo_mais_antigo:
            print(f'  ✓ Processo mais antigo selecionado: {processo_mais_antigo} (data: {data_mais_antiga})')
            return processo_mais_antigo
    
    print('  ✗ Nenhum processo alternativo encontrado')
    return None

def anexar_pdfs_formulario(driver,  nao_procurar_pelo_processo = None, tentativa=-1, tentativa_formatacao=False):
    """Anexa os PDFs da pasta pdf_merge nos inputs correspondentes do formulário"""
    try:
        print('\nAnexando PDFs ao formulário...')

        # Lista para armazenar processos alternativos
        processos_alternativos = []

        # Continuar processo anexar
        continuar_anexar = True

        # Caminho da pasta pdf_merge
        pdf_merge_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_merge')
        
        if not os.path.exists(pdf_merge_folder):
            print(f'✗ Pasta não encontrada: {pdf_merge_folder}')
            return False
        
        # Lista todos os PDFs da pasta
        pdf_files = [f for f in os.listdir(pdf_merge_folder) if f.lower().endswith('.pdf')]
        print(f'✓ Total de PDFs encontrados: {len(pdf_files)}')
        
        if not pdf_files:
            print('⚠ Nenhum PDF encontrado na pasta pdf_merge')
            return False
        
        # Processa cada PDF
        for pdf_file in pdf_files:
            print(f'\nProcessando PDF: {pdf_file}')
            
            # Remove a extensão .pdf
            nome_sem_extensao = os.path.splitext(pdf_file)[0]
            
            # Faz split por underline
            partes = nome_sem_extensao.split('_')
            
            if len(partes) < 3:
                print(f'⚠ Nome do arquivo inválido: {pdf_file}')
                continue
            
            # Extrai numero_integracao (posição 0) e valor_pleito (posição 2)
            numero_integracao = partes[0]
            valor_pleito = partes[2].strip()
            numero_processo = partes[1].strip()
            
            print(f'  Número Integração: {numero_integracao}')
            print(f'  Valor Pleito: {valor_pleito}')
            print(f'  Número Processo: {numero_processo}')

            # Procura o input correspondente no formulário
            encontrado = False
            indice = 1
            indice_simbolo = 2
            
            while True:
                try:

                    # Tenta encontrar o input cau_X
                    cau_input = driver.find_element(By.ID, f'cau_{indice}')
                    cau_value = cau_input.get_attribute('value')
                    
                    # Tenta encontrar o input Pleito_X
                    pleito_input = driver.find_element(By.ID, f'Pleito_{indice}')
                    pleito_value = pleito_input.get_attribute('value').strip().replace('.','')
                    
                    # Encontra o numero do processo importado no sistema
                    numero_processo_sistema = driver.find_element(By.ID, f'pro_{indice}')
                    numero_processo_sistema_value = numero_processo_sistema.get_attribute('value')
                    
                    # Verifica se os valores correspondem
                    if cau_value == numero_integracao and pleito_value == valor_pleito:

                        elemento = driver.find_element(By.XPATH, f'/html/body/fieldset/form/div[1]/fieldset/table[1]/tbody/tr[{indice_simbolo}]')
                        html_interno = elemento.get_attribute('innerHTML')
                        # and numero_processo == numero_processo_sistema_value
                        if '/images/check_green.gif' not in html_interno:
                            
                            if '#3146c7' in html_interno and tentativa_formatacao == False:
                                print('  ⚠ Processo com status não encontrado, nova tentativa de importacao com formatação acontecerá')
                                
                                processos_alternativos.append({
                                    "numero_integracao": numero_integracao, 
                                    "processo_alternativo": numero_processo,
                                    "valor" : valor_pleito,
                                    "numero_processo_original": numero_processo,
                                    "atualiza_historico_padrao": False 
                                })
                            
                            elif '#3146c7' in html_interno and tentativa > -1:

                                processo_alternativo = buscar_processo_alternativo(numero_integracao, numero_processo, nao_procurar_pelo_processo, tentativa)
                                print(f'  ✓ Processo alternativo: {processo_alternativo}')

                                processos_alternativos.append({
                                    "numero_integracao": numero_integracao, 
                                    "processo_alternativo": processo_alternativo,
                                    "valor" : valor_pleito,
                                    "numero_processo_original": numero_processo,
                                    "atualiza_historico_padrao": False    
                                })

                            elif '#00ff21' in html_interno:
                                print('  ⚠ Processo com status verde encontrado, mas sem processo alternativo, Processo não Encontrado...')
                                print('XXXXXXXXXXXXXXXXXXX TRATAR ERRO VERDE XXXXXXXXXXXXXXXXXXX')
                                
                                processos_alternativos.append({
                                    "numero_integracao": numero_integracao, 
                                    "processo_alternativo": numero_processo,
                                    "valor" : valor_pleito,
                                    "numero_processo_original": numero_processo,
                                    "atualiza_historico_padrao": True  
                                })

                            else:
                                print('XXXXXXXXXXXXXXXXXXX TRATAR STATUS NOVO XXXXXXXXXXXXXXXXXXX')
                                pdb.set_trace()

                            continuar_anexar = False
                            break

                        if continuar_anexar == False:
                            print(f'  ✗ Processo já possui um processo alternativo, pulando anexar para: {numero_integracao}')
                            break

                        # if  numero_integracao == 'CIV1232920':
                        #     pdb.set_trace()
                        #     processo_alternativo = buscar_processo_alternativo(numero_integracao, numero_processo)
                        #     print(f'  ✓ Processo alternativo: {processo_alternativo}')
                        #     return {"retorno":  False, "numero_integracao":numero_integracao, "processo_alternativo":processo_alternativo}

                        print(f'  ✓ Correspondência encontrada no índice {indice}')

                        pdf_path = os.path.join(pdf_merge_folder, pdf_file)
                        
                        # Se for o primeiro índice (cau_1), faz merge com descritivo
                        if indice == 1:
                            print('  → Primeira posição: fazendo merge com descritivo...')
                            # Nome do arquivo com descritivo
                            nome_base = os.path.splitext(pdf_file)[0]
                            pdf_com_descritivo = f'{nome_base}_COM_DESCRITIVO.pdf'
                            pdf_final_path = os.path.join(pdf_merge_folder, pdf_com_descritivo)
                            
                            # Faz o merge
                            merger = PdfMerger()
                            
                            # Adiciona o descritivo primeiro
                            merger.append(PDF_OUTPUT)
                            print(f'    + {os.path.basename(PDF_OUTPUT)}')
                            
                            # Adiciona o PDF original
                            merger.append(pdf_path)
                            print(f'    + {pdf_file}')
                            
                            # Salva o PDF mesclado
                            merger.write(pdf_final_path)
                            merger.close()
                            
                            print(f'  ✓ PDF com descritivo criado: {pdf_com_descritivo}')
                            
                            # Usa o PDF mesclado para anexar
                            pdf_path = pdf_final_path
                        
                        # Anexa o PDF no input docLancfin_X
                        doc_input = driver.find_element(By.ID, f'docLancfin_{indice}')
                        
                        # Verifica se o campo já está preenchido
                        campo_preenchido = doc_input.get_attribute('value')
                        if campo_preenchido:
                            print(f'  ⚠ Campo docLancfin_{indice} já preenchido, pulando...')
                            encontrado = True
                        
                        else:
                            doc_input.send_keys(pdf_path)
                            
                            print(f'  ✓ PDF anexado: {os.path.basename(pdf_path)}')
                            encontrado = True
                            time.sleep(0.5)
                            break
                        
                    indice += 1
                    indice_simbolo +=  4
                        
                    
                except:
                    # Se não encontrar mais inputs, sai do loop
                    break
            
            if not encontrado:
                print(f'  ✗ Correspondência não encontrada para: {pdf_file}')
        
        print('\n✓ Todos os PDFs foram processados!')
        
        # Retorna os processos alternativos encontrados
        if processos_alternativos:
            return {"retorno": False, "processos_alternativos": processos_alternativos}
        else:
            return {"retorno": True, "processos_alternativos": []}
        
    except Exception as e:
        print(f'✗ Erro ao anexar PDFs: {e}')
        import traceback
        traceback.print_exc()
        return {"retorno": True, "processos_alternativos": []}

def atualizar_processo_json(numero_integracao, processo_alternativo, valor_pleito, atualiza_historico_padrao = False):
    """Atualiza o processo alternativo no JSON de importados.
    
    Args:
        numero_integracao: Número de integração do processo
        processo_alternativo: Novo número do processo alternativo
        
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    if not numero_integracao or not processo_alternativo:
        print('  ⚠ Dados insuficientes para atualizar JSON')
        return False
    
    try:
        print(f'\n📝 Atualizando JSON para {numero_integracao}...')
        
        # Lê o JSON
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
        
        # Procura e atualiza o registro
        atualizado = False
        for registro in data_json['registros']:
            if registro.get('pro_numero_de_integracao') == numero_integracao and registro.get('debito_na_moeda', '') == valor_pleito:
                registro['pro_numero_do_processo'] = processo_alternativo
                atualizado = True
                print(f'  ✓ Processo atualizado: {processo_alternativo}')
                #break

                if atualiza_historico_padrao:
                    registro['historico'] = "CUSTAS DIVERSAS E TAXAS JUDICIAIS / TRIBUNAL DE JU"

        if atualizado:
            # Salva o JSON atualizado
            with open(JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data_json, f, indent=2, ensure_ascii=False)
            print(f'  ✓ JSON salvo em: {JSON_PATH}')
            return True
        else:
            print(f'  ⚠ Registro não encontrado no JSON')
            return False
            
    except Exception as e:
        print(f'  ✗ Erro ao atualizar JSON: {e}')
        import traceback
        traceback.print_exc()
        return False

def zerar_config():
    """Zera os valores do arquivo config.json após submissão bem-sucedida"""
    try:
        print('\nZerando config.json...')
        
        # Lê o config atual para preservar lancamentos_removidos
        lancamentos_removidos = []
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config_atual = json.load(f)
                lancamentos_removidos = config_atual.get('lancamentos_removidos', [])
        except:
            pass
        
        config_vazio = {
            "numero_recibo": "",
            "data_inicial": "",
            "data_final": "",
            "iniciado_em": "",
            "lancamentos_removidos": lancamentos_removidos
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_vazio, f, indent=4, ensure_ascii=False)
        print('✓ Config.json zerado com sucesso!')
        return True
    except Exception as e:
        print(f'✗ Erro ao zerar config.json: {e}')
        return False

def finalizar_processo(driver, valor_somado):
    print('\nVerificando valor total...')
    try:
        # Pega o valor do campo txtTotalLiquidoTela
        total_tela = driver.find_element(By.ID, 'txtTotalLiquidoTela').get_attribute('value')
        print(f'Valor na tela: {total_tela}')
        
        # Normaliza os valores removendo pontos
        valor_somado_normalizado = valor_somado
        total_tela_normalizado = total_tela.replace('.', '')
        
        print(f'Valor esperado: {valor_somado_normalizado}')
        print(f'Valor na tela (normalizado): {total_tela_normalizado}')
        
        # Compara os valores
        if valor_somado_normalizado == total_tela_normalizado:
            print('\n✓✓✓ Pronto para submeter ✓✓✓')

            enviado = True

            # Clica no botão Submeter
            try:
                print('Clicando no botão Submeter...')
                btn_submeter = driver.find_element(By.ID, 'btn_Submeter')
                btn_submeter.click()
                print('✓ Botão Submeter clicado!')
                
                # Aguarda enquanto o botão mostrar "Aguarde"
                print('Aguardando processamento...')
                tempo_espera = 0
                while True:
                    try:
                        # PRIMEIRO verifica se há alert (aparece quando processamento termina)
                        try:
                            alert = driver.switch_to.alert
                            texto_alert = alert.text
                            print(f'  ℹ Alert detectado: "{texto_alert}"')
                            
                            if 'Nota fiscal gerada com sucesso' in texto_alert:
                                print(f'  ✓✓✓ SUCESSO! Nota fiscal gerada! (Total: {tempo_espera}s)')
                                alert.accept()
                                print('  ✓ Alert aceito')
                                break
                            else:
                                print(f'  ⚠ Alert inesperado: {texto_alert}')
                                alert.accept()
                                break
                        except:
                            # Não há alert, continua verificando o botão
                            pass
                        
                        # Verifica o texto do botão
                        btn_submeter = driver.find_element(By.ID, 'btn_Submeter')
                        texto_botao = btn_submeter.text.strip()
                        
                        if 'Aguarde' in texto_botao or 'aguarde' in texto_botao.lower():
                            print(f'  Processando... ({tempo_espera}s)')
                            time.sleep(2)
                            tempo_espera += 2
                            
                            # Timeout de segurança (10 minutos)
                            if tempo_espera >= 600:
                                print('  ⚠ Timeout: mais de 10 minutos aguardando')
                                enviado = False
                                break
                        else:
                            # Botão mudou, aguarda um pouco para ver se alert aparece
                            print(f'  ℹ Botão mudou para: "{texto_botao}", aguardando alert...')
                            time.sleep(1)
                            
                    except Exception as check_error:
                        print(f'  ⚠ Erro ao verificar: {check_error}')
                        # Tenta verificar se há alert antes de sair
                        try:
                            alert = driver.switch_to.alert
                            texto_alert = alert.text
                            print(f'  ℹ Alert encontrado após erro: "{texto_alert}"')
                            if 'Nota fiscal gerada com sucesso' in texto_alert:
                                print(f'  ✓✓✓ SUCESSO! Nota fiscal gerada!')
                                alert.accept()
                        except:
                            pass
                        break
                
                return enviado
                
            except Exception as submit_error:
                print(f'✗ Erro ao clicar no botão Submeter: {submit_error}')
            
            
        else:
            print(f'\n⚠ ATENÇÃO: Valores não conferem!')
            print(f'   Esperado: {valor_somado_normalizado}')
            print(f'   Na tela: {total_tela_normalizado}')

    except Exception as e:
        print(f'⚠ Erro ao verificar valor total: {e}')

def verificar_lancamentos(driver):
    """Verifica lançamentos do formulário"""

    print('⚠ Verificando lançamentos...')

    baixado = True

    elementos = driver.find_elements(By.XPATH, f'/html/body/fieldset/form/div[1]/fieldset/table[1]/tbody/tr')
    
    for html in elementos:
        html_interno = html.get_attribute('innerHTML')
        if '/images/check_green.gif' in html_interno:
            print(f'  ⚠ Há Lançamentos não baixados')
            baixado = False
            break

    return baixado

def main():
    """Executa o fluxo completo"""
    try:

        clean_pdf_merge_folder()
        clean_planilha_folder()

        etapa_integracao = True  # Controla se a etapa de integração com a API deve ser executada

        if etapa_integracao:
            etapa_cpj = False
            etapa_arquivos = True

            if etapa_arquivos:

                print('✓ Etapa Integração: Ativada')
                
                # Realiza o login na API
                token = api_login()
                
                if not token:
                    print('✗ Falha ao autenticar na API. Abortando processo...')
                    return
                
                print('✓ Autenticação na API concluída com sucesso!')
                print(f'✓ Token Bearer configurado e pronto para uso!')
                
                # Busca lançamentos (usando DATA_INICIAL_PESQUISA e DATA_FINAL_PESQUISA)
                data_inicial = datetime.strptime(DATA_INICIAL_PESQUISA, '%d/%m/%Y')
                data_final = datetime.strptime(DATA_FINAL_PESQUISA, '%d/%m/%Y')
                
                #reembolsos BMG
                lancamentos = api_buscar_lancamentos(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    numero_cc=1397
                )
                
                if lancamentos:
                    print(f'\n✓ Busca de lançamentos concluída!')
                    print(f'  Total encontrado: {len(lancamentos) if isinstance(lancamentos, list) else "N/A"}')
                    
                    # Processa os lançamentos para obter informações completas
                    dados_processados = processar_lancamentos(lancamentos)
                    
                    if dados_processados and dados_processados.get('registros'):
                        registros = dados_processados['registros']
                        print(f'\n✓ Dados processados com sucesso!')
                        print(f'  Total de registros: {len(registros)}')
                        print(f'  Valor total: R$ {dados_processados.get("valor_somado", "0,00")}')
                        
                        # Exibe resumo dos primeiros registros
                        print('\n--- Resumo dos dados processados ---')
                        for idx, item in enumerate(registros[:3], start=1):
                            print(f'\n[{idx}] ID SPF: {item["id_spf"]}')
                            print(f'    Integração: {item["pro_numero_de_integracao"]}')
                            print(f'    Processo: {item["pro_numero_do_processo"]}')
                            print(f'    Valor: {item["valor_em_r"]}')
                            print(f'    Data: {item["data_lancamento"]}')
                            print(f'    Histórico: {item["historico"]}')
                        
                        if len(registros) > 3:
                            print(f'\n... e mais {len(registros) - 3} registro(s)')
                        
                        # Processa os documentos dos registros
                        print('\n' + '='*60)
                        print('PROCESSAMENTO DE DOCUMENTOS')
                        print('='*60)
                        output_folder = os.path.dirname(os.path.abspath(__file__))
                        processar_documentos_registros(
                            json_path=JSON_PATH,
                            output_folder=output_folder
                        )
                        
                        # Verifica se o número de PDFs gerados corresponde ao número de lançamentos
                        pdf_merge_folder = os.path.join(output_folder, 'pdf_merge')
                        
                        if os.path.exists(pdf_merge_folder):
                            pdfs_gerados = [f for f in os.listdir(pdf_merge_folder) if f.lower().endswith('.pdf') and not f.endswith('_COM_DESCRITIVO.pdf')]
                            num_pdfs = len(pdfs_gerados)
                            num_lancamentos = len(lancamentos)
                            
                            print(f'\n📊 Validação de PDFs:')
                            print(f'  Lançamentos encontrados: {num_lancamentos}')
                            print(f'  PDFs gerados: {num_pdfs}')
                            
                            if num_pdfs != num_lancamentos and num_pdfs < len(registros):
                                print(f'\n✗ ERRO: Número de PDFs ({num_pdfs}) diferente do número de lançamentos ({num_lancamentos})')
                                print(f'  ⚠ Parando execução...')
                                
                                time.sleep(40)
                                return
                            else:
                                print(f'  ✓ Validação OK: Todos os lançamentos geraram PDFs!')
                        else:
                            print(f'\n✗ ERRO: Pasta pdf_merge não encontrada: {pdf_merge_folder}')
                            print(f'  ⚠ Parando execução...')
                            return

                    else:
                        print('\n⚠ Nenhum dado foi processado com sucesso')
                else:
                    print('\n⚠ Nenhum lançamento encontrado ou erro na busca')
                
        else:
        ## Etapa 1: Login e exportação do CSV
            etapa_cpj = True
            if etapa_cpj:
                print('✓ Etapa CPJ: Ativada')
                
            etapa_arquivos = False  

            if etapa_cpj and not etapa_arquivos:
                close_controle_processos_windows()                
                app = open_cpj_application()
                dlg = app.top_window()

                perform_login(app)   

                try:   
                    click_menu(app)
                except Exception as e:
                    close_cpj_application(app)
                    print(f'Erro ao clicar no menu: {e}')
                    dlg.type_keys('{ENTER}')
                    time.sleep(5)
                    app = open_cpj_application()
                    perform_login(app) 
                    
                click_printer(app)
                navigate_to_analise_lancamento(app)
                navigate_to_relatorio_conta(app)
                fill_cliente_and_dates(app)

                try:
                    export_file(app)
                    close_window(app)

                    ## Etapa 2: Processar CSV
                    process_csv()

                except Exception as e:
                    print(f'Erro ao exportar arquivo: {e}')
                    if 'No such file or directory' in str(e):
                        print('Não há arquivo para exportar...')
                        send_keys('%{F4}')
                        time.sleep(2)
                        send_keys('{ENTER}')
                        return

                # Etapa 3: Preparar PDFs
                #app = Application(backend='win32').connect(path=CPJ_PATH) 
                open_search_area(app)        
            
            
            if(etapa_arquivos):
                app = Application(backend='win32').connect(path=CPJ_PATH)

                ## Etapa 2: Processar CSV
                process_csv() 
                open_search_area(app)

                etapa_cpj = True
   
        ## Lê JSON processadoo
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f'\nTotal de registros: {data["contagem"]}')
        print('Processando todos os registros...\n')
        
        ## Processa todos os registros
        if etapa_cpj:
            if data['registros']:
                for index, registro in enumerate(data['registros']):
                    process_record_for_pdf(registro, index)

        ## Etapa 4: Preencher planilha modelo
        fill_planilha_modelo_v4()

        ## Etapa 5: Preencher o descritivo e gerar
        fill_descritivo_pdf()
        
        ## Etapa 6: Abrir Chrome com Selenium
        driver = open_chrome_browser()
        
        # Fazer login
        login_web_exyon_bmg(driver)
        
        # Selecionar unidade
        selecionar_unidade(driver)
        
        # Executar script de menu
        executar_script_menu(driver)
        
        # Executar script do menu lateral
        executar_script_menu_lateral(driver)
        
        # Executar script de classificação financeira
        executar_script_classificacao(driver)

        #Executa preenchimento formulario
        retorno = executar_preenchimento_formulario(driver, data['valor_somado'])

        if(retorno == False):
            print('\n✗ Falha no preenchimento do formulário!')
            driver.quit()
            pdb.set_trace()
        
        
        # Anexa os PDFs no formulário
        processar_pdf = anexar_pdfs_formulario(driver)
        tentativa_formatacao = False

        if processar_pdf['retorno'] == False:

            tentativa = -1

            ultima_formatacao = False

            while processar_pdf['retorno'] == False:

                # Atualiza o JSON com todos os processos alternativos
                if ultima_formatacao == False:
                    for processo_alt in processar_pdf['processos_alternativos']:

                        if tentativa_formatacao == False:
                            # Aplica máscara CNJ no processo alternativo
                            processo_formatado = formatar_numero_processo(processo_alt['numero_processo_original'])
                            
                            atualizar_processo_json(
                                processo_alt['numero_integracao'],
                                processo_formatado,
                                processo_alt['valor'],
                                processo_alt['atualiza_historico_padrao']
                            )
                            
                        else:
                            atualizar_processo_json(
                                processo_alt['numero_integracao'],
                                processo_alt['processo_alternativo'],
                                processo_alt['valor'],
                                processo_alt['atualiza_historico_padrao']
                            )

                ## Etapa 4: Preencher planilha modelo
                fill_planilha_modelo_v4()

                ## Etapa 5: Preencher o descritivo e gerar
                fill_descritivo_pdf()
                
                driver.refresh()

                # Executar script de menu
                executar_script_menu(driver)
                
                # Executar script do menu lateral
                executar_script_menu_lateral(driver)
                
                # Executar script de classificação financeira
                executar_script_classificacao(driver)

                #Executa preenchimento formulario
                retorno = executar_preenchimento_formulario(driver, data['valor_somado'])
                
                if(retorno == False):
                    print('\n✗ Falha no preenchimento do formulário!')
                    pdb.set_trace()

                # Anexa os PDFs no formulário
                processar_pdf = anexar_pdfs_formulario(driver, processo_alt['processo_alternativo'], tentativa, tentativa_formatacao)

                if processar_pdf['retorno'] == False:
                    tentativa_formatacao = True
                    tentativa += 1                    
                    print('\n✗ Ainda há processos com alternativas, repetindo o processo...')
                    print(processar_pdf['processos_alternativos'])

                    if tentativa >= 2:
                        
                        if tentativa == 2:
                            # Atualiza o JSON com todos os processos alternativos
                            for processo_alt in processar_pdf['processos_alternativos']:

                                # Aplica máscara CNJ no processo alternativo
                                processo_formatado = formatar_numero_processo(processo_alt['numero_processo_original'])
                                
                                atualizar_processo_json(
                                    processo_alt['numero_integracao'],
                                    processo_formatado,
                                    processo_alt['valor'],
                                    processo_alt['atualiza_historico_padrao']
                                )

                            ultima_formatacao = True

                        else:                
                            print('\n⚠ Muitas tentativas sem sucesso, verifique manualmente os processos alternativos:')
                            pdb.set_trace()
                    

            #pdb.set_trace()

            # retorno_anexos = processar_pdf['retorno']

        # Verifica se o valor total está correto
        finalizar_processo(driver, data['valor_somado'])

        # verifica lançamentos para garantir que foram baixados
        baixado = False
        while not baixado:

            print('\nVerificando lançamentos após submissão...')
            
            driver.refresh()

            # Executar script de menu
            executar_script_menu(driver)

            # Executar script do menu lateral
            executar_script_menu_lateral(driver)

            # Executar script de classificação financeira
            executar_script_classificacao(driver)

            #Executa preenchimento formulario
            executar_preenchimento_formulario(driver, data['valor_somado'])

            #verifica se os lançamentos estão baixados, se não estiverem, tenta novamente (pode ser necessário formatar processo alternativo)
            baixado = verificar_lancamentos(driver)

            if baixado:
                print('\n✓ Lançamentos verificados como baixados!')
                baixado = True
            else:
                print('\n⚠ Lançamentos ainda não baixados, tentando novamente...')
                anexar_pdfs_formulario(driver)

                finalizar_processo_envio = finalizar_processo(driver, data['valor_somado'])
                
                while finalizar_processo_envio == False:

                    print('\n⚠ Falha ao finalizar processo, tentando novamente...')
                    time.sleep(2)
                    driver.refresh()

                    # Executar script de menu
                    executar_script_menu(driver)

                    # Executar script do menu lateral
                    executar_script_menu_lateral(driver)

                    # Executar script de classificação financeira
                    executar_script_classificacao(driver)

                    #Executa preenchimento formulario
                    executar_preenchimento_formulario(driver, data['valor_somado'])

                    anexar_pdfs_formulario(driver)

                    finalizar_processo_envio = finalizar_processo(driver, data['valor_somado'])

                
        # Zera o config.json após submissão bem-sucedida
        zerar_config()

        # Faz logout da API
        api_logout()
        
        # Não esqueça de fechar o navegador ao final
        driver.quit()

        print('\n✓ Automação concluída com sucesso!')
        
    except Exception as e:
        print(f'\n✗ Falha na automação: {e}')
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
