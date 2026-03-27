#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontra o início e fim das funções duplicadas
start_line = None
end_line = None

for i, line in enumerate(lines):
    # Procura pela primeira def open_chrome_browser (a errada - linha ~208)
    if start_line is None and 'def open_chrome_browser():' in line and i > 200 and i < 250:
        # Começa 5 linhas antes (no comentário de seção)
        start_line = i - 5
        print(f'Início encontrado na linha {start_line + 1}')
    
    # Procura pela segunda def open_chrome_browser (a correta - linha ~1840)
    if start_line is not None and 'def open_chrome_browser():' in line and i > 1800:
        end_line = i
        print(f'Fim encontrado na linha {end_line + 1}')
        break

if start_line is not None and end_line is not None:
    print(f'Removendo linhas {start_line + 1} a {end_line}')
    
    # Mantém o cabeçalho da seção web
    header_lines = [
        '# ============================================================================\n',
        '# FUNÇÕES WEB (Selenium - Exyon BMG)\n',
        '# ============================================================================\n',
        '\n'
    ]
    
    new_lines = lines[:start_line] + header_lines + lines[end_line:]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    removed_lines = (end_line - start_line) - len(header_lines)
    print(f'✓ Removidas {removed_lines} linhas de código duplicado!')
    print(f'  Arquivo tinha {len(lines)} linhas')
    print(f'  Arquivo agora tem {len(new_lines)} linhas')
else:
    print('✗ Não encontrou as linhas corretas')
    print(f'start_line: {start_line}')
    print(f'end_line: {end_line}')
