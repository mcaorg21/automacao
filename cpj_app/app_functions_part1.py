"""
Funções para automação do aplicativo desktop CPJ

Este módulo contém todas as funções necessárias para interagir com o aplicativo desktop CPJ,
incluindo login, navegação, preenchimento de formulários e exportação de dados.
"""

import time
import os
import csv
import json
import shutil
import ctypes
import tkinter as tk
import pyautogui
from datetime import datetime, timedelta
from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys
from pywinauto.mouse import click
from PyPDF2 import PdfMerger
import xlrd
from xlwt import Workbook
from xlutils.copy import copy as xl_copy
from docx import Document
from docx2pdf import convert

# ============================================================================
# VARIÁVEIS GLOBAIS DO MÓDULO
# ============================================================================

# Configurações do CPJ (devem ser definidas via set_cpj_config)
CPJ_PATH = None
LOGIN = None
PASSWORD = None
PLANILHA_PATH = None
CSV_PATH = None
JSON_PATH = None
BASE_DPI = 144
BASE_WIDTH = 2560
BASE_HEIGHT = 1600
IMAGES_PATH = None
PDF_FOLDER = None
PLANILHA_MODELO_PATH = None
PLANILHA_MODELO_PATH_2 = None
DOCX_MODELO = None
DOCX_OUTPUT = None
PDF_OUTPUT = None
DATA_INICIAL_PESQUISA = None
DATA_FINAL_PESQUISA = None
NUMERO_RECIBO = None

def set_cpj_config(**config):
    """Configura as variáveis globais do módulo CPJ App
    
    Args:
        cpj_path: Caminho do executável CPJ
        login: Login do CPJ
        password: Senha do CPJ
        planilha_path: Caminho da pasta planilha
        csv_path: Caminho do arquivo CSV
        json_path: Caminho do arquivo JSON
        images_path: Caminho das imagens
        pdf_folder: Caminho da pasta de PDFs
        planilha_modelo_path: Caminho da planilha modelo
        planilha_modelo_path_2: Caminho da planilha modelo 2
        docx_modelo: Caminho do modelo DOCX
        docx_output: Caminho do DOCX de saída
        pdf_output: Caminho do PDF de saída
        data_inicial_pesquisa: Data inicial de pesquisa
        data_final_pesquisa: Data final de pesquisa
        numero_recibo: Número do recibo
        base_dpi: DPI base (padrão: 144)
        base_width: Largura base (padrão: 2560)
        base_height: Altura base (padrão: 1600)
    """
    global CPJ_PATH, LOGIN, PASSWORD, PLANILHA_PATH, CSV_PATH, JSON_PATH
    global BASE_DPI, BASE_WIDTH, BASE_HEIGHT, IMAGES_PATH, PDF_FOLDER
    global PLANILHA_MODELO_PATH, PLANILHA_MODELO_PATH_2
    global DOCX_MODELO, DOCX_OUTPUT, PDF_OUTPUT
    global DATA_INICIAL_PESQUISA, DATA_FINAL_PESQUISA, NUMERO_RECIBO
    
    CPJ_PATH = config.get('cpj_path', CPJ_PATH)
    LOGIN = config.get('login', LOGIN)
    PASSWORD = config.get('password', PASSWORD)
    PLANILHA_PATH = config.get('planilha_path', PLANILHA_PATH)
    CSV_PATH = config.get('csv_path', CSV_PATH)
    JSON_PATH = config.get('json_path', JSON_PATH)
    IMAGES_PATH = config.get('images_path', IMAGES_PATH)
    PDF_FOLDER = config.get('pdf_folder', PDF_FOLDER)
    PLANILHA_MODELO_PATH = config.get('planilha_modelo_path', PLANILHA_MODELO_PATH)
    PLANILHA_MODELO_PATH_2 = config.get('planilha_modelo_path_2', PLANILHA_MODELO_PATH_2)
    DOCX_MODELO = config.get('docx_modelo', DOCX_MODELO)
    DOCX_OUTPUT = config.get('docx_output', DOCX_OUTPUT)
    PDF_OUTPUT = config.get('pdf_output', PDF_OUTPUT)
    DATA_INICIAL_PESQUISA = config.get('data_inicial_pesquisa', DATA_INICIAL_PESQUISA)
    DATA_FINAL_PESQUISA = config.get('data_final_pesquisa', DATA_FINAL_PESQUISA)
    NUMERO_RECIBO = config.get('numero_recibo', NUMERO_RECIBO)
    BASE_DPI = config.get('base_dpi', BASE_DPI)
    BASE_WIDTH = config.get('base_width', BASE_WIDTH)
    BASE_HEIGHT = config.get('base_height', BASE_HEIGHT)
    
    print('✓ Configurações do CPJ App atualizadas')

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def get_system_dpi():
    """Obtém o DPI do sistema"""
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetDpiForSystem()

def get_resolution():
    """Obtém a resolução da tela"""
    root = tk.Tk()
    root.withdraw()
    return root.winfo_screenwidth(), root.winfo_screenheight()

def auto_scale_coords(x, y):
    """Escala automaticamente coordenadas baseado no DPI e resolução"""
    dpi = get_system_dpi()
    width, height = get_resolution()

    dpi_factor = dpi / BASE_DPI
    width_factor = width / BASE_WIDTH
    height_factor = height / BASE_HEIGHT

    final_x = int(x * dpi_factor * width_factor)
    final_y = int(y * dpi_factor * height_factor)

    return final_x, final_y

def smart_click(x, y):
    """Wrapper do click com escala automática"""
    sx, sy = auto_scale_coords(x, y)
    return sx, sy 

def valida_data(data_str: str) -> datetime:
    """Valida formato de data"""
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        raise ValueError(
            f"Data inválida: {data_str}. Formato obrigatório: dd/mm/YYYY"
        )

def sleep_with_countdown(seconds: int, message: str = 'Aguardando'):
    """Aguarda com countdown visual"""
    for i in range(seconds, 0, -1):
        print(f'\r{message}: {i}s restantes...', end='', flush=True)
        time.sleep(1)
    print(f'\r{message}: concluído!          ')

def click_image(image_path: str, confidence: float = 0.8, timeout: int = 10, description: str = ''):
    """Procura uma imagem na tela e clica no centro dela"""
    if not os.path.exists(image_path):
        print(f'✗ Arquivo de imagem não encontrado: {image_path}')
        return False
    
    desc = description or os.path.basename(image_path)
    print(f'Procurando imagem: {desc}...')
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            try:
                location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            except TypeError:
                location = pyautogui.locateCenterOnScreen(image_path)
            
            if location:
                print(f'✓ Imagem encontrada em: {location}')
                pyautogui.click(location)
                time.sleep(0.5)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            if time.time() - start_time < 1:
                print(f'Aviso: {e}')
                print('Continuando sem parâmetro confidence...')
        time.sleep(0.5)
    
    print(f'✗ Imagem não encontrada após {timeout}s: {desc}')
    return False

def wait_for_element(app, class_name: str = None, title: str = None, timeout: int = 60, check_interval: float = 0.5):
    """Aguarda até que um elemento apareça na tela"""
    print(f'\nAguardando elemento aparecer...')
    if class_name:
        print(f'  classe: {class_name}')
    if title:
        print(f'  título: {title}')
    print(f'  timeout: {timeout}s')
    
    elapsed = 0
    while elapsed < timeout:
        try:
            dlg = app.top_window()
            
            if class_name and title:
                element = dlg.child_window(class_name=class_name, title=title)
            elif class_name:
                element = dlg.child_window(class_name=class_name)
            elif title:
                element = dlg.child_window(title=title)
            else:
                raise ValueError('Especifique class_name ou title')
            
            if element.exists():
                print(f'\r✓ Elemento encontrado após {elapsed:.1f}s!          ')
                return True
                
        except Exception:
            pass
        
        remaining = timeout - elapsed
        print(f'\rProcurando... {remaining:.0f}s restantes', end='', flush=True)
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    print(f'\r✗ Timeout: elemento não encontrado após {timeout}s')
    return False

def to_snake_case(text: str) -> str:
    """Converte string para snake_case"""
    import unicodedata
    import re
    
    if text is None or not isinstance(text, str):
        return ''
    
    # Remove acentos
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Converte para lowercase e substitui
    text = text.lower()
    text = text.replace('.', '_').replace(' ', '_')
    text = ''.join(c if c.isalnum() or c == '_' else '' for c in text)
    text = '_'.join(filter(None, text.split('_')))
    
    return text

# ============================================================================
# FUNÇÕES DE LIMPEZA
# ============================================================================

def clean_planilha_folder():
    """Limpa a pasta planilha"""
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

def clean_pdf_merge_folder():
    """Limpa a pasta pdf_merge"""
    try:
        merge_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_merge')
        print(f'\nLimpando pasta pdf_merge: {merge_folder}...')
        
        if not os.path.exists(merge_folder):
            os.makedirs(merge_folder)
            print(f'✓ Pasta criada: {merge_folder}')
            return
        
        for item in os.listdir(merge_folder):
            item_path = os.path.join(merge_folder, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                    print(f'  ✓ Arquivo removido: {item}')
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f'  ✓ Pasta removida: {item}')
            except Exception as e:
                print(f'  ✗ Erro ao remover {item}: {e}')
        
        print('✓ Pasta pdf_merge limpa com sucesso!')
    except Exception as e:
        print(f'✗ Erro ao limpar pasta pdf_merge: {e}')
        raise

# ============================================================================
# FUNÇÕES DE GERENCIAMENTO DO APLICATIVO
# ============================================================================

def close_controle_processos_windows():
    """Fecha o aplicativo CPJ se estiver em execução"""
    try:
        print('\nFechando aplicativo CPJ...')
        
        try:
            app = Application(backend='win32').connect(path=CPJ_PATH, timeout=5)
            print('✓ Aplicativo CPJ encontrado em execução')
            time.sleep(2)
            try:
                app.kill()
                print('✓ Aplicativo CPJ fechado com sucesso')
            except Exception as e:
                print(f'⚠ Erro ao fechar: {e}')
                
        except Exception:
            print('✓ Aplicativo CPJ não está em execução')
            
    except Exception as e:
        print(f'✗ Erro ao fechar aplicativo: {e}')

def open_cpj_application():
    """Abre o aplicativo CPJ"""
    try:
        print('Abrindo aplicativo CPJ...')
        app = Application(backend='win32').start(CPJ_PATH)
        print('✓ Aplicativo CPJ iniciado!')
        
        print('Aguardando aplicativo carregar...')
        time.sleep(5)
        
        return app
        
    except Exception as e:
        print(f'✗ Erro ao abrir aplicativo: {e}')
        try:
            print('Tentando conectar ao processo existente...')
            app = Application(backend='win32').connect(path=CPJ_PATH, timeout=10)
            return app
        except:
            raise

def close_cpj_application(app):
    """Fecha o aplicativo CPJ normalmente"""
    try:
        print('\nFechando aplicativo CPJ...')
        dlg = app.top_window()
        dlg.close()
        print('✓ Aplicativo CPJ fechado!')
    except Exception as e:
        print(f'✗ Erro ao fechar aplicativo: {e}')

# ==================================================================================================================
# CONTINUA NO PRÓXIMO BLOCO (arquivo muito grande, será dividido)
# ==================================================================================================================
"""