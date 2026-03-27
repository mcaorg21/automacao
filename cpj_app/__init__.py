"""
Módulo CPJ App - Funções para automação do aplicativo desktop CPJ
"""

from .app_functions import (
    # Funções de gerenciamento
    set_cpj_config,
    close_controle_processos_windows,
    open_cpj_application,
    close_cpj_application,
    
    # Funções de navegação
    perform_login,
    click_menu,
    click_printer,
    navigate_to_analise_lancamento,
    navigate_to_relatorio_conta,
    fill_cliente_and_dates,
    export_file,
    close_window,
    open_search_area,
    
    # Funções de processamento
    process_csv,
    fill_descritivo_pdf,
    fill_planilha_modelo,
    fill_planilha_modelo_v2,
    fill_planilha_modelo_v4,
    fill_planilha_modelo_v5,
    process_record_for_pdf,
    
    # Funções utilitárias
    to_snake_case,
    get_system_dpi,
    get_resolution,
    auto_scale_coords,
    smart_click,
    valida_data,
    sleep_with_countdown,
    click_image,
    wait_for_element,
    
    # Funções de limpeza
    clean_planilha_folder,
    clean_pdf_merge_folder,
)

__all__ = [
    # Funções de gerenciamento
    'set_cpj_config',
    'close_controle_processos_windows',
    'open_cpj_application',
    'close_cpj_application',
    
    # Funções de navegação
    'perform_login',
    'click_menu',
    'click_printer',
    'navigate_to_analise_lancamento',
    'navigate_to_relatorio_conta',
    'fill_cliente_and_dates',
    'export_file',
    'close_window',
    'open_search_area',
    
    # Funções de processamento
    'process_csv',
    'fill_descritivo_pdf',
    'fill_planilha_modelo',
    'fill_planilha_modelo_v2',
    'fill_planilha_modelo_v4',
    'fill_planilha_modelo_v5',
    'process_record_for_pdf',
    
    # Funções utilitárias
    'to_snake_case',
    'get_system_dpi',
    'get_resolution',
    'auto_scale_coords',
    'smart_click',
    'valida_data',
    'sleep_with_countdown',
    'click_image',
    'wait_for_element',
    
    # Funções de limpeza
    'clean_planilha_folder',
    'clean_pdf_merge_folder',
]
