<h1>Initializr</h1>

<h2>Propósito</h2>
<p align="justify">
    O sistema Initializr tem como funções inicializar e monitorar os processos do robôs
    do sistema de automação. Essa funcionalidade é implemntada em um loop de indefinido
    no qual são realizadas as seguintes tarefas:
</p>
<ol>
    <li>
        Carregar as diretrizes de ativação dos processos (pela leitura do arquivo ativacao.json).
    </li>
    <li>
        Reportar o status de cada processo (ativo/inativo).
    </li>
    <li>
        Iniciar sequencialmente cada processo.
    </li>
    <li>
        Aguardar n segundos até a próxima iteração.
    </li>
</ol>

<h2>Conteúdo</h2>
    <h3>Initializr.py</h3>
    <pre>initializr/Initializr.py</pre>    
    <p>
        Módulo que contém a classe Initializr, responsável por iniciar o sistema para inicializar
        e monitorar os processos dos robôs.
    </p>
    <h3>ativacao.json</h3>
    <pre>initializr/ativacao.json</pre>    
    <p>
        Arquivo composto por chaves e valores, no qual as chaves são os nomes das classes dos
        processos a serem iniciados e os valoes são booleanos que indicam se determinado processo
        deve ou não ser iniciado.
    </p>
    <h3>\_\_init__.py (configurações de ambiente)</h3>
    <pre>initializr/processos_automacao/\_\_init__.py</pre>    
    <p>
        Contém as configurações de ambiente do sistema. Isso quer dizer constantes globais cujo
        valor depende do sistema operacional, como o tipo de shell a ser iniciado, bem como
        a base do código que será executado para iniciar todos os processos.
    </p>
    <h3>MainConfig.py</h3>
    <pre>initializr/processos_automacao/config/MainConfig.py</pre>    
    <p>
        Classe que utiliza das constantes de ambiente em \_\_init__.py e dos caminhos dos arquivos
        a serem executados (presentes em robos_main_paths.py) para configurar o comando de
        inicialização de cada processo que será executado usando psutil.Popen.
    </p> 
    <h3>ProcessWrapper.py</h3>
    <pre>initializr/processos_automacao/config/ProcessWrapper.py</pre>    
    <p>
        Consiste em uma abstração de um processo. A classe armazena o processo principal bem
        como seus processos filhos. Os métodos realizam tarefas de selecionar subprocessos
        específicos, matar o processo relativo ao shell, matar todos o processo e todos subprocessos,
        dentre outras.
    </p> 
    <h3>/classes_processos</h3>
    <pre>initializr/processos_automacao/classes_processos/</pre>    
    <p>
        Diretório que contém as classes que representam os processos dos robôs a serem executados.
        Todas as classes herdam ProcessWrapper e instanciam MainConfig. Utilizado métodos e dados
        de ambas, implementa o método run() que inicializa o processo de execução do robô.
    </p> 
    
<h2>Utilização</h2>
<p>
    A utilização básica consiste em executar o método <i>main</i> da classe Initializr, bem como
    em ajustar o status de ativação dos robôs que deseja executar e daqueles que deseja que
    permaneçam inativos.
</p>
<h3> Para Rodar o Sistema que Monitora e Inicializa os Robôs </h3>

    python C:\Users\gustavo\Documents\automacao-python\initializr\Initializr.py

<h3>Para Desativar ou Ativar um Robô Específico</h2>
<ul>
    <li>
        No arquivo "/initializr/ativacao.json" altere o valor a frente do nome do robô desejado
        para "true" (ativar) ou "false" (desativar).
    </li>
</ul>

<pre>
"/initializr/ativacao.json"
{
  "TarefasPan": true,               // será iniciado
  "PanConsultaRefin064": false,     // não será iniciado
  "PanConsultaRefin035": false,     // não será iniciado
  ...
}
  
</pre>

<h2> Estrutura do Sistema</h2>
<pre>
/initializr
|
│   ativacao.json
│   Initializr.py
│   README.md
│   __init__.py
│
├───processos_automacao
│   │   __init__.py
│   │
│   ├───classes_processos
│   │   │   ProcessoConsultaDadosMeuINSS.py
│   │   │   ProcessosBMG.py
│   │   │   ProcessosBradesco.py
│   │   │   ProcessosGoogleAnalytics.py
│   │   │   ProcessosItau.py
│   │   │   ProcessosMarinha.py
│   │   │   ProcessosOle.py
│   │   │   ProcessosPan.py
│   │   │   ProcessosPortalConsignado.py
│   │   │   ProcessosPromobank.py
│   │   │   __init__.py
│   │
│   ├───config
│   │   │   MainConfig.py
│   │   │   ProcessWrapper.py
│   │   │   robos_main_paths.py
│   │   │   __init__.py
</pre>