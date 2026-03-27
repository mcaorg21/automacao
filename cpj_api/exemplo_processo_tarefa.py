"""
Exemplo de uso da função api_buscar_processo_tarefa
Autor: Sistema de Automação CPJ
Data: 2026-03-06
"""

import sys
sys.path.append('C:\\www\\automacao')

from cpj_api import (
    set_api_credentials,
    api_login,
    api_buscar_processo_tarefa,
    api_logout
)

def exemplo_buscar_tarefa():
    """Exemplo de como buscar tarefas de processo"""
    
    # 1. Configurar credenciais
    set_api_credentials(
        base_url='https://app.leviatan.com.br/dcncadv/cpj/agnes',
        login='api.teste2',
        password='2025'
    )
    
    # 2. Fazer login
    print("Fazendo login...")
    if not api_login():
        print("Erro ao fazer login!")
        return
    
    # 3. Solicitar dados do usuário
    print("\n" + "="*50)
    print("Configuração da busca")
    print("="*50)
    
    evento = input("\nDigite o código do evento (ex: EVENTO_EXEMPLO): ").strip()
    if not evento:
        evento = "EVENTO_EXEMPLO"
        print(f"Usando evento padrão: {evento}")
    
    data_inicial = input("Digite a data inicial YYYY-MM-DD (ou Enter para hoje): ").strip()
    if not data_inicial:
        from datetime import datetime
        data_inicial = datetime.now().strftime('%Y-%m-%d')
        print(f"Usando data de hoje: {data_inicial}")
    
    try:
        limit = int(input("Digite o limite de registros (padrão 10): ").strip() or "10")
    except:
        limit = 10
        print(f"Usando limite padrão: {limit}")
    
    # 4. Buscar tarefas de processo
    print("\n" + "="*50)
    print("Buscando tarefas de processo...")
    print("="*50)
    
    tarefas = api_buscar_processo_tarefa(
        evento=evento,
        data_inicial=data_inicial,
        limit=limit
    )
    
    if tarefas:
        print(f"\n✓ {len(tarefas)} tarefa(s) encontrada(s)")
        for idx, tarefa in enumerate(tarefas, 1):
            print(f"\n{'='*50}")
            print(f"Tarefa {idx}")
            print(f"{'='*50}")
            # Imprime campos específicos se disponíveis
            if isinstance(tarefa, dict):
                for key, value in tarefa.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {tarefa}")
    else:
        print("\n✗ Nenhuma tarefa encontrada.")
    
    # 5. Fazer logout
    print("\n" + "="*50)
    api_logout()
    print("="*50)

if __name__ == "__main__":
    exemplo_buscar_tarefa()
