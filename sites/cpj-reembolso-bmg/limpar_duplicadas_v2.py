#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas antes: {len(lines)}')

# Remove as linhas 208 até 1842 (incluindo a linha 1843 que tem a def duplicada)
# As linhas em Python são indexadas em 0, então linha 208 = índice 207
# Queremos manter até linha 207 (índice 206) e depois pular até linha 1844 (índice 1843)

start_keep = 207  # Linha 208 será removida (índice 207)
end_skip = 1843   # Linha 1844 será mantida (índice 1843)

new_lines = lines[:start_keep] + lines[end_skip:]

print(f'Total de linhas depois: {len(new_lines)}')
print(f'Linhas removidas: {len(lines) - len(new_lines)}')

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✓ Arquivo atualizado!')
