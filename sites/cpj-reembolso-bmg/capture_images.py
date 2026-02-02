"""
Script auxiliar para capturar imagens da tela do CPJ para reconhecimento.

Este script permite capturar screenshots de elementos específicos da interface
do CPJ para usar com reconhecimento de imagem no pyautogui.

Uso:
1. Execute este script: python capture_images.py
2. Siga as instruções na tela
3. Posicione o mouse sobre o elemento que quer capturar
4. Pressione a tecla indicada para capturar
"""

import pyautogui
import time
import os
from datetime import datetime

# Configurações
IMAGES_PATH = r'C:\www\automacao\sites\cpj-reembolso-bmg\images'

# Garante que a pasta existe
os.makedirs(IMAGES_PATH, exist_ok=True)

def capture_region(name: str, description: str):
    """Captura uma região da tela"""
    print(f"\n{'='*60}")
    print(f"CAPTURANDO: {name}")
    print(f"Descrição: {description}")
    print(f"{'='*60}")
    print("\nInstruções:")
    print("1. Posicione a janela do CPJ de forma visível")
    print("2. Localize o elemento a ser capturado")
    print("3. Quando estiver pronto, pressione ENTER")
    
    input("\nPressione ENTER quando estiver pronto...")
    
    print("\nAguarde 3 segundos...")
    time.sleep(3)
    
    print("\nUSE O MOUSE para selecionar a região:")
    print("  - Clique e arraste para selecionar o elemento")
    print("  - Solte o mouse para capturar")
    
    try:
        # Captura região selecionada pelo usuário
        region = pyautogui.screenshot()
        
        # Salva
        filename = os.path.join(IMAGES_PATH, name)
        region.save(filename)
        
        print(f"\n✓ Imagem salva: {filename}")
        print(f"  Tamanho: {region.size}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao capturar: {e}")
        return False

def capture_with_region_select(name: str, description: str):
    """Captura usando seleção de região com coordenadas"""
    print(f"\n{'='*60}")
    print(f"CAPTURANDO: {name}")
    print(f"Descrição: {description}")
    print(f"{'='*60}")
    print("\nInstruções:")
    print("1. Posicione a janela do CPJ de forma visível")
    print("2. Localize o elemento na tela")
    print("3. Pressione ENTER para iniciar")
    
    input("\nPressione ENTER quando estiver pronto...")
    
    print("\nVocê tem 5 segundos para posicionar o mouse no CANTO SUPERIOR ESQUERDO do elemento...")
    for i in range(5, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    
    # Captura primeira posição
    x1, y1 = pyautogui.position()
    print(f"\n✓ Primeira posição: ({x1}, {y1})")
    
    print("\nAgora você tem 5 segundos para posicionar o mouse no CANTO INFERIOR DIREITO do elemento...")
    for i in range(5, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    
    # Captura segunda posição
    x2, y2 = pyautogui.position()
    print(f"\n✓ Segunda posição: ({x2}, {y2})")
    
    # Calcula região
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    print(f"\nCapturando região: ({left}, {top}, {width}, {height})")
    
    try:
        # Captura a região
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        
        # Salva
        filename = os.path.join(IMAGES_PATH, name)
        screenshot.save(filename)
        
        print(f"\n✓ Imagem salva: {filename}")
        print(f"  Tamanho: {screenshot.size}")
        
        # Mostra preview
        print(f"\nPara verificar a imagem, abra: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao capturar: {e}")
        return False

def main():
    """Menu principal"""
    print("="*60)
    print("CAPTURA DE IMAGENS PARA RECONHECIMENTO - CPJ")
    print("="*60)
    print(f"\nAs imagens serão salvas em: {IMAGES_PATH}\n")
    
    images_to_capture = [
        {
            'name': 'menu_icon.png',
            'description': 'Ícone do menu lateral (se houver botão para expandir)',
            'optional': True
        },
        {
            'name': 'menu_conta_corrente.png',
            'description': 'Item "Conta corrente de clientes e fornecedores" no menu',
            'optional': False
        },
        {
            'name': 'printer_button.png',
            'description': 'Botão de impressão (ícone de impressora ou "Imprimir")',
            'optional': False
        },
        {
            'name': 'analise_lancamento.png',
            'description': 'Opção "Análise de Lançamento" no menu de impressão',
            'optional': False
        },
        {
            'name': 'relatorio_conta.png',
            'description': 'Opção "Relatório da Conta" no menu',
            'optional': False
        }
    ]
    
    print("Imagens a capturar:")
    for i, img in enumerate(images_to_capture, 1):
        status = "(OPCIONAL)" if img['optional'] else "(OBRIGATÓRIO)"
        print(f"{i}. {img['name']} {status}")
        print(f"   {img['description']}")
    
    print("\n" + "="*60)
    
    for i, img in enumerate(images_to_capture, 1):
        print(f"\n\n{'#'*60}")
        print(f"# IMAGEM {i}/{len(images_to_capture)}")
        print(f"{'#'*60}")
        
        if img['optional']:
            resp = input("\nEsta imagem é OPCIONAL. Deseja capturá-la? (s/N): ").strip().lower()
            if resp not in ['s', 'sim', 'y', 'yes']:
                print("Pulando...")
                continue
        
        # Captura usando seleção por coordenadas
        capture_with_region_select(img['name'], img['description'])
        
        if i < len(images_to_capture):
            input("\nPressione ENTER para continuar para a próxima imagem...")
    
    print("\n" + "="*60)
    print("CAPTURA CONCLUÍDA!")
    print("="*60)
    print(f"\nVerifique as imagens em: {IMAGES_PATH}")
    print("\nDicas:")
    print("- Abra cada imagem e verifique se está clara e bem enquadrada")
    print("- O elemento deve estar visível e sem cortes")
    print("- Se alguma imagem não ficou boa, execute o script novamente")
    print("\nAgora você pode executar o main.py com reconhecimento de imagem!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCaptura cancelada pelo usuário.")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
