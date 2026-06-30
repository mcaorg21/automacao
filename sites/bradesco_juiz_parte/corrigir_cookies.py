# -*- coding: utf-8 -*-
"""Corrige arquivos de cookies exportados pelo console do Chrome (cookieStore.getAll)."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

for i in range(1, 11):
    path = os.path.join(DIR, f"cookies_jusbrasil_conta_{i}.json")
    if not os.path.exists(path):
        print(f"conta_{i}: nao encontrado")
        continue

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Testa se ja e valido
    try:
        json.loads(content)
        print(f"conta_{i}: OK (sem correcao necessaria)")
        continue
    except json.JSONDecodeError:
        pass

    # Aplica correcao de \\" -> \"
    content_fix = content.replace('\\\\"', '\\"')
    try:
        json.loads(content_fix)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content_fix)
        print(f"conta_{i}: CORRIGIDO")
    except json.JSONDecodeError as e:
        print(f"conta_{i}: ERRO mesmo apos correcao -> {e}")
