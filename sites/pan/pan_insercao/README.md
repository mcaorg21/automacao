Robô Pan Inserção.

Realiza a automação do processo de inserção das propostas de
empréstimo dos clientes no Banco Panamericano. Para isso, 
conta com tres categorias de módulos:
  1. Manager: realiza as interfaces entre as diferentes 
  classes e funções responsáveis tanto pelas requisições e
  processamento de dados, quanto pela interação com o DOM
  e o navegador.
  2. Auto: possui um módulo com classes que representam cada
  campo do formulário e as ações que serão aplicadas a eles.
  Possui também um módulo contento funçoes que realizam a 
  concatenação lógica entre as ações dos campos contidas
  nas classes.
  3. Data: possui uma classe que armazena os dados das APIs
  utilizadas pelo robô, bem como métodos que realizam as 
  requisições de dados e o tratamento desses dados para serem
  utilizados durante a automação.
  
  Estrutura:
  
 /pan/pan_insercao/
 |--- auto/
 |    |--- executar_insercao.py
 |    |--- pan_inserc_formularios.py
 |    |___ pan_assinatura_digital_auto.py
 |
 |--- manager/
 |    |___ pan_inserc_man.py
 |
 |--- data/
 |    |--- pan_inserc_data.py
 |    |___ collections.py
 
