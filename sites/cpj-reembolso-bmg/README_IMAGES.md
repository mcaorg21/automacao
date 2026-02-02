# Instruções para Capturar Imagens

Para que o reconhecimento de imagem funcione, você precisa capturar screenshots dos elementos da interface.

## Imagens Necessárias

### 1. Menu Icon (menu_icon.png) - OPCIONAL
- **Descrição**: Ícone de menu lateral (se houver botão para expandir)
- **Como capturar**: 
  1. Abra o CPJ e faça login
  2. Use a Ferramenta de Captura do Windows (Win + Shift + S)
  3. Selecione apenas o ícone do menu
  4. Salve como `images/menu_icon.png`

### 2. Menu Conta Corrente (menu_conta_corrente.png) - OBRIGATÓRIO
- **Descrição**: Item do menu "Conta corrente de clientes e fornecedores"
- **Como capturar**:
  1. Abra o CPJ e faça login
  2. Localize o item "Conta corrente de clientes e fornecedores" no menu lateral
  3. Use Win + Shift + S e selecione APENAS o texto/ícone deste item
  4. Salve como `images/menu_conta_corrente.png`

### 3. Printer Button (printer_button.png) - OBRIGATÓRIO
- **Descrição**: Botão de impressão (F5)
- **Como capturar**:
  1. Abra o CPJ, faça login e navegue até a tela de Conta Corrente
  2. Localize o botão de impressão (geralmente tem ícone de impressora ou texto "Imprimir")
  3. Use Win + Shift + S e selecione APENAS o botão
  4. Salve como `images/printer_button.png`

### 4. Análise de Lançamento (analise_lancamento.png) - OBRIGATÓRIO
- **Descrição**: Menu/opção "Análise de Lançamento"
- **Como capturar**:
  1. Após clicar no botão de impressão, procure a opção "Análise de Lançamento"
  2. Use Win + Shift + S e selecione APENAS esta opção
  3. Salve como `images/analise_lancamento.png`

### 5. Relatório da Conta (relatorio_conta.png) - OBRIGATÓRIO
- **Descrição**: Opção "Relatório da Conta"
- **Como capturar**:
  1. No mesmo menu de impressão, localize "Relatório da Conta"
  2. Use Win + Shift + S e selecione APENAS esta opção
  3. Salve como `images/relatorio_conta.png`

## Dicas Importantes

1. **Qualidade**: Capture com boa resolução, mas não excessiva
2. **Fundo**: Inclua um pouco do fundo ao redor do elemento (1-2 pixels)
3. **Contraste**: Certifique-se que o elemento está claramente visível
4. **Estado**: Capture o elemento no estado normal (não hover/pressionado)
5. **Tamanho**: Não precisa ser muito grande - o elemento deve estar claro

## Verificar Capturas

Depois de capturar todas as imagens, verifique que elas estão na pasta `images/`:
- menu_icon.png (opcional)
- menu_conta_corrente.png
- printer_button.png
- analise_lancamento.png
- relatorio_conta.png

## Ajuste de Confidence

Se o reconhecimento não funcionar bem:
- Confidence muito alta (0.9-1.0): Muito restritivo, pode não encontrar
- Confidence muito baixa (0.5-0.6): Pode encontrar elementos errados
- **Recomendado**: 0.7-0.8 para começar

Você pode ajustar o parâmetro `confidence` nas chamadas `click_image()` se necessário.
