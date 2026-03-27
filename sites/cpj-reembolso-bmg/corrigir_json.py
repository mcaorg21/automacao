import json

# Caminho do JSON
json_path = r'c:\www\automacao\sites\cpj-reembolso-bmg\planilha\importados.json'

# Lê o JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Corrige cada registro
print(f'Corrigindo {len(data["registros"])} registros...\n')

for idx, registro in enumerate(data['registros'], 1):
    numero_processo_original = registro['pro_numero_do_processo']
    # Remove pontos, traços e mantém apenas números
    numero_processo_limpo = ''.join(c for c in numero_processo_original if c.isdigit())
    
    if numero_processo_original != numero_processo_limpo:
        print(f'[{idx}] {numero_processo_original} → {numero_processo_limpo}')
        registro['pro_numero_do_processo'] = numero_processo_limpo

# Salva o JSON corrigido
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n✓ JSON corrigido e salvo em: {json_path}')
