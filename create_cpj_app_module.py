"""
Script para extrair funções do CPJ App e criar o módulo
"""

import os

# Lê o arquivo main.py
with open(r'c:\www\automacao\sites\cpj-reembolso-bmg\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Define os imports necessários
header = '''"""
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
import pdb
import traceback
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
    """Configura as variáveis globais do módulo CPJ App"""
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
# FUNÇÕES DO CPJ APP
# ============================================================================

'''

# Extrai funções do CPJ app (linhas 120 a 1800)
cpj_functions_lines = lines[119:1800]  # linha 120 = índice 119

# Salva o arquivo
output_path = r'c:\www\automacao\cpj_app\app_functions.py'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(header)
    f.writelines(cpj_functions_lines)

print(f'✓ Módulo criado: {output_path}')
print(f'✓ Total de linhas: {len(cpj_functions_lines)}')
