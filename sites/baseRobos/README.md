BaseRobos contém três superclasses, que servem de base para as
classes filhas que compõe os robôs. Contem, também, um pacote de
funções e classes auxiliares no processo de automação.

Superclasses:
1. Manager: possui atributos e métodos que gerenciam e inicializam
o chrome driver e suas configurações.

2. Data Handler: responsável pela requisição, armazenamento, limpeza
e processamento de dados. Os dados geralmente são oriundos de requests e 
do scrapping dos elementos web realizado pelo selenium.

3. AutoGUI: realiza a automação da interface gráfica do navegador. Executa
as diversas funções do webdriver para acessar e armazenar dados de elementos
web.

4. Main: classe responsável por executar as tarefas das classes manager.

Pacote 'core', conteúdo:
    1. selenium_actions
    2. selenium_helper
    3. my_selenium_listener
    4. captcha
    5. data_helpers
    6. helpers
    7. uconecte
    8. pyautogui_helper
    
Padrão:
A automação será realizada pela implementação de três classes filhas, a saber:
NomeBancoMan(Manager), NomeBancoData(DataHadler), NomeBancoAuto(AutoGUI).

NomeBancoAuto realiza apenas a automação da interface do navegador por meio 
das funções do chrome_driver (implementadas pelo selenium_helpers e selenium_actions).
NomeBancoData realiza as requests, armazena, limpa e processa dados, de todas as
origens. As interfaces entre as duas nunca é feita diretamente, mas apenas no
corpo dos métodos da classe  NomeBancoMan. NomeBancoMan implementa métodos que
representam tarefas ou subtarefas de automação, em que métodos das duas outras
classes interagem para executar determinada tarefa.

Por fim, cada tarefa que se deseja executar, contida em NomeBancoMan, deve ser 
executada em Main, realizando, de fato, a automação. 