import sys

print("=== DIAGNÓSTICO DE IMPORT ===\n")

# Teste 1: tkinter
try:
    print("[1/6] Testando tkinter...")
    import tkinter as tk
    print("  ✓ tkinter OK")
except Exception as e:
    print(f"  ✗ PROBLEMA COM TKINTER: {e}")
    print("  Solução: O tkinter pode não estar instalado ou configurado corretamente")

# Teste 2: docx2pdf
try:
    print("[2/6] Testando docx2pdf...")
    from docx2pdf import convert
    print("  ✓ docx2pdf OK")
except Exception as e:
    print(f"  ✗ PROBLEMA COM docx2pdf: {e}")
    print("  Solução: pip install docx2pdf")

# Teste 3: pywinauto
try:
    print("[3/6] Testando pywinauto...")
    from pywinauto import Application, Desktop
    print("  ✓ pywinauto OK")
except Exception as e:
    print(f"  ✗ PROBLEMA COM pywinauto: {e}")
    print("  Solução: pip install pywinauto")

# Teste 4: pyautogui
try:
    print("[4/6] Testando pyautogui...")
    import pyautogui
    print("  ✓ pyautogui OK")
except Exception as e:
    print(f"  ✗ PROBLEMA COM pyautogui: {e}")
    print("  Solução: pip install pyautogui")

# Teste 5: xlrd/xlwt
try:
    print("[5/6] Testando xlrd/xlwt/xlutils...")
    import xlrd
    from xlwt import Workbook
    from xlutils.copy import copy as xl_copy
    print("  ✓ xlrd/xlwt/xlutils OK")
except Exception as e:
    print(f"  ✗ PROBLEMA: {e}")
    print("  Solução: pip install xlrd xlwt xlutils")

# Teste 6: selenium
try:
    print("[6/6] Testando selenium...")
    from selenium import webdriver
    print("  ✓ selenium OK")
except Exception as e:
    print(f"  ✗ PROBLEMA: {e}")
    print("  Solução: pip install selenium")

print("\n=== FIM DO DIAGNÓSTICO ===")
