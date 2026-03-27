"""
EXEMPLO DE USO DO MÓDULO CPJ_API EM OUTRO PROJETO

Este arquivo demonstra como usar o módulo cpj_api em qualquer projeto.
"""

import sys
from datetime import datetime, timedelta

# ============================================================================
# 1. ADICIONAR O CAMINHO DO MÓDULO
# ============================================================================
sys.path.append('C:\\www\\automacao')

# ============================================================================
# 2. IMPORTAR FUNÇÕES NECESSÁRIAS
# ============================================================================
from cpj_api import (
    set_api_credentials,
    api_login,
    api_logout,
    api_buscar_lancamentos,
    processar_lancamentos,
    processar_documentos_registros
)

# ============================================================================
# 3. CONFIGURAR CREDENCIAIS E CAMINHOS DO SEU PROJETO
# ============================================================================
# IMPORTANTE: Ajuste estes caminhos para o seu projeto!
PROJETO_PATH = r'C:\www\meu_projeto'
PLANILHA_PATH = f'{PROJETO_PATH}\\planilha'
JSON_PATH = f'{PLANILHA_PATH}\\importados.json'

set_api_credentials(
    base_url='https://app.leviatan.com.br/dcncadv/cpj/agnes',
    login='api',
    password='2025',
    json_path=JSON_PATH,
    planilha_path=PLANILHA_PATH
)

# ============================================================================
# 4. EXECUTAR WORKFLOW COMPLETO
# ============================================================================

def workflow_completo():
    """Workflow completo: Login -> Buscar -> Processar -> Logout"""
    
    print('='*80)
    print('INICIANDO WORKFLOW DE PROCESSAMENTO CPJ')
    print('='*80)
    
    # 4.1. Fazer login
    print('\n[1/5] Fazendo login na API...')
    token = api_login()
    if not token:
        print('✗ Erro no login! Abortando...')
        return False
    print('✓ Login realizado com sucesso!')
    
    try:
        # 4.2. Definir período de busca (exemplo: ontem)
        print('\n[2/5] Definindo período de busca...')
        ontem = datetime.now() - timedelta(days=1)
        print(f'  Data: {ontem.strftime("%d/%m/%Y")}')
        
        # 4.3. Buscar lançamentos
        print('\n[3/5] Buscando lançamentos...')
        lancamentos = api_buscar_lancamentos(
            data_inicial=ontem,
            data_final=ontem,
            numero_cc=1397  # Banco BMG
        )
        
        if not lancamentos:
            print('⚠ Nenhum lançamento encontrado')
            return True
        
        print(f'✓ {len(lancamentos)} lançamento(s) encontrado(s)')
        
        # 4.4. Processar lançamentos
        print('\n[4/5] Processando lançamentos...')
        resultado = processar_lancamentos(lancamentos)
        
        print(f'\n✓ Processamento concluído:')
        print(f'  - Registros processados: {resultado["contagem"]}')
        print(f'  - Valor total: R$ {resultado["valor_somado"]}')
        print(f'  - JSON salvo em: {JSON_PATH}')
        
        # 4.5. Processar documentos (opcional)
        resposta = input('\nDeseja processar documentos (baixar e fazer merge)? (s/n): ')
        if resposta.lower() == 's':
            print('\n[5/5] Processando documentos...')
            processar_documentos_registros()
            print('✓ Documentos processados!')
        else:
            print('\n[5/5] Processamento de documentos pulado')
        
        print('\n' + '='*80)
        print('WORKFLOW CONCLUÍDO COM SUCESSO!')
        print('='*80)
        return True
        
    except Exception as e:
        print(f'\n✗ Erro durante o processamento: {e}')
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 4.6. Sempre fazer logout
        print('\nFazendo logout...')
        api_logout()
        print('✓ Logout realizado')


def workflow_simples():
    """Workflow simplificado: apenas buscar e processar lançamentos"""
    
    print('Iniciando workflow simplificado...\n')
    
    # Login
    if not api_login():
        return False
    
    try:
        # Buscar e processar
        ontem = datetime.now() - timedelta(days=1)
        lancamentos = api_buscar_lancamentos(ontem, ontem, 1397)
        
        if lancamentos:
            resultado = processar_lancamentos(lancamentos)
            print(f'\n✓ Total: {resultado["contagem"]} registros | R$ {resultado["valor_somado"]}')
            return True
        else:
            print('⚠ Nenhum lançamento encontrado')
            return True
            
    finally:
        api_logout()


def workflow_personalizado():
    """Workflow personalizado com período específico"""
    
    print('Workflow personalizado\n')
    
    # Define período manualmente
    data_inicial = datetime(2026, 2, 1)
    data_final = datetime(2026, 2, 13)
    
    print(f'Período: {data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}\n')
    
    # Login
    if not api_login():
        return False
    
    try:
        # Buscar
        lancamentos = api_buscar_lancamentos(
            data_inicial=data_inicial,
            data_final=data_final,
            numero_cc=1397,
            limit=10000  # Aumenta limite se necessário
        )
        
        if lancamentos:
            # Processar
            resultado = processar_lancamentos(lancamentos)
            print(f'\n✓ Processados: {resultado["contagem"]} registros')
            print(f'✓ Valor total: R$ {resultado["valor_somado"]}')
            
            # Opcionalmente processar documentos
            processar_documentos_registros()
            
            return True
        else:
            print('⚠ Nenhum lançamento encontrado')
            return True
            
    finally:
        api_logout()


# ============================================================================
# EXECUTAR EXEMPLO
# ============================================================================

if __name__ == '__main__':
    print('\nEscolha o workflow:')
    print('1 - Workflow Completo (com menu interativo)')
    print('2 - Workflow Simples (automático)')
    print('3 - Workflow Personalizado (período específico)')
    print('0 - Sair')
    
    escolha = input('\nOpção: ')
    
    if escolha == '1':
        workflow_completo()
    elif escolha == '2':
        workflow_simples()
    elif escolha == '3':
        workflow_personalizado()
    else:
        print('Saindo...')
