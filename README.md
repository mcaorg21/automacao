### Antes de começar leia as instruções abaixo

Existem diversos robôs criados, eles estão separados por categorias, sendo elas:
- Inserção
- Geração de contrato
- Consultas
- Consulta Status

Para iniciar qualquer um dos robôes é necessário ter o Python 3.7+ instalado na sua máquina.

Depois de instalar o python é necessário baixar o instalador de pacotes o pip.

Feito o download do pip execute o comando:

```
pip install -r requirements.txt
# Com esse comando você vai instalar as dependências base do projeto.
```

#adicione o comando abaixo no crontab -e pra sempre deletar a tmp
*/1 * * * * find /tmp -type f \( ! -user root \) -atime +1 -delete

Para iniciar o robô é só rodar o comando:

```
python main.py
# Com esse comando um menu de opções vai ser exibido com todos os robôs disponíveis, depois disso é só navegar com as setas do teclado e pressionar enter na opção desejada.
```

### Particularidades

- Robô de inserção Itaú:
-- Não pode minimizar a tela

- Robô de inserção/geração de contratos do Olé:
-- Criar um novo usuário do google Chrome para o Olé. Para isso navegue até a pasta C:/Users/lucas.s/AppData/Local/Google/Chrome e faça uma copia da pasta User Data com o nome User Ole
-- É necessário baixar um programa separado que faz a geração de pdfs com base em html. [Download do programa - WKHTMLTOPDF](https://wkhtmltopdf.org/){:target="_blank"}
-- Adicionar o C:\Program Files\wkhtmltopdf\bin No path do sistema operacional;
-- É necessário que a tela fique maximizada, ela pode permanecer em segundo plano, mas nunca minimizada;
-- Necessário um humano logar no sistema sem o navegador estar sendo controlado;

- Robô de status Olé:
-- Ao iniciar uma nova sessão no chrome, automaticamente ele inicia e se reinicia.Exceto quando o pc desligar.
-- A consulta de status acontece a cada 20 minutos e para às 19 horas
-- Ficar atento ao login e senha utilizados pois a sessão não cai e raramente é trocada a senha

- Robô Geração de contrato Itaú
-- Criar um novo usuário do Google Chrome para o IbConsig. Para isso navegue até a pasta C:/Users/lucas.s/AppData/Local/Google/Chrome e faça uma copia da pasta User Data com o nome New User
-- Entre nas configurações do Google Chrome, na barra de busca digite "PDF", entre no item "Configurações do Site", vá para a opção "Documentos em PDF", marque a opção "Fazer o download de arquivos" 
-- Não precisa que a tela fique aberta, pode ser minimizado;
-- Pode ficar rodando o dia todo para download de arquivos;
-- Caso esteja utilizando o mesmo navegador do Olé é necessário mudar o usuário;

- Robô Consulta AnaliseInfo
-- É necessário que ele fique aberto maximizado;
-- Controla o mouse e o teclado, impossibilitando o uso da máquina por outras pessoas;

- Robô de consulta de dados User Explorer Google
-- Será necessário rodá-lo sem constância. Apenas para atualizações no final do mês para que alimente a tabela de finalizados e pagos

### Sequência de ativação

Robôs inserção do itaú, inserção do olé e geração de contratos são iniciados na mesma máquina.
Passsos para iniciar:

- Entrar no navegador do olé sem utilizar o robô. Realizar o Login com captcha e depois fechar o navegador;
- Iniciar o robô do olé usando o comando python main.py; (Não pode minimizar o navegador)
- Iniciar o robô de geração de contratos do itaú;
- Iniciar o robô de inserção do itaú.
- Iniciar o robô de consulta de refinanciamentos

Robôs consulta status olé pode ser iniciado na mesma máquina do inserção olé, porém em sessões de Chrome diferentes.
Passsos para iniciar:

- Iniciar o robô do olé usando o comando python main.py; 

### Uso Multiplataforma
automacao-python está projetado de modo a ser executado em ambientes Windows e Linux. Para isso, é necessário
configurar o projeto de acordo com o sistema operacional em que será executado. Tais configurações podem ser
realizadas alterando-se os valores das constantes globais em:

    ./sites/baseRobos/PATHS.py

As constantes globais em PATHS.py definem: o sistema operacional, o sistema ou computador
específico e o nome da pasta HOME do sistema em que o projeto será executado.

Comandos específicos ao sistema Linux encontram-se na pasta ./linux_cli, nos arquivos:
<pre>
<strong>env_config.py</strong>
Contém constantes globais com comandos e caminhos para ativação do virtualenv, 
PYTHONPATH e do terminal usado pelo sistema.

<strong>unix_cmds</strong>
Comandos expecíficos do Linux para nomear a janela do terminal e do processo, para 
interromper processos, etc.

<strong>ui.py</strong>
Interface para seleção das tarefas dos robôs

<strong>threads.py</strong>
Funções que executam os comandos para inicializar as tarefas dos robôs.

<strong>producao.py</strong>
Implementa a interface do terminal para obter a opção relativa à tarefa
que o usuário deseja iniciar e inicia a tarefa selecionada.
</pre>

No ambiente Linux os robôs podem ser inicilizados com o comando, no Desktop:
<pre>
./exec.sh
</pre>

O controle de versionamento pode ser realizado pela linha de comando, usando
o comando git no terminal Linux, ou por meio de interface gráfica utilizando
o SmartGit.

A máquina virtual atualmente configurada para o projeto se chama:
<pre>instance-automacao</pre>

Ela pode ser inicializada no Console do GCP e acessada remotamente na url:
<pre>https://remotedesktop.google.com/access/</pre>

Instruções sobre o uso de softwares específicos à máquina virtual se encontram
no Desktop, em arquivo de texto com o nome da máquina.

<h4>Estrutura do projeto:</h3>
<pre><span style="color: #5555FF; "><b>.</b></span>
├── <span style="color: #5555FF; "><b>drivers</b></span>
├── <span style="color: #5555FF; "><b>linux_cli</b></span>
├── <span style="color: #5555FF; "><b>sites</b></span>
│   ├── <span style="color: #5555FF; "><b>analiseInfo</b></span>
│   │   └── <span style="color: #5555FF; "><b>imagens</b></span>
│   ├── <span style="color: #5555FF; "><b>baseRobos</b></span>
│   │   ├── <span style="color: #5555FF; "><b>core</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>__pycache__</b></span>
│   │   └── <span style="color: #5555FF; "><b>__pycache__</b></span>
│   ├── <span style="color: #5555FF; "><b>bmg</b></span>
│   ├── <span style="color: #5555FF; "><b>bradesco</b></span>
│   ├── <span style="color: #5555FF; "><b>cetelem</b></span>
│   ├── <span style="color: #5555FF; "><b>core</b></span>
│   │   └── <span style="color: #5555FF; "><b>__pycache__</b></span>
│   ├── <span style="color: #5555FF; "><b>google</b></span>
│   │   └── <span style="color: #5555FF; "><b>analytics</b></span>
│   ├── <span style="color: #5555FF; "><b>ib_consig</b></span>
│   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   ├── <span style="color: #5555FF; "><b>data_handlers</b></span>
│   │   ├── <span style="color: #5555FF; "><b>ib_analise_de_fraude</b></span>
│   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   ├── <span style="color: #5555FF; "><b>ibConsig</b></span>
│   │   ├── <span style="color: #5555FF; "><b>cookies</b></span>
│   │   ├── <span style="color: #5555FF; "><b>descriçao</b></span>
│   │   ├── <span style="color: #5555FF; "><b>__pycache__</b></span>
│   │   └── <span style="color: #5555FF; "><b>unificados</b></span>
│   ├── <span style="color: #5555FF; "><b>inss</b></span>
│   │   ├── <span style="color: #5555FF; "><b>0_legado</b></span>
│   │   └── <span style="color: #5555FF; "><b>consulta_margem_sms</b></span>
│   │       ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │       ├── <span style="color: #5555FF; "><b>data</b></span>
│   │       └── <span style="color: #5555FF; "><b>managers</b></span>
│   ├── <span style="color: #5555FF; "><b>marinha</b></span>
│   ├── <span style="color: #5555FF; "><b>multiBr</b></span>
│   ├── <span style="color: #5555FF; "><b>oleConsignado</b></span>
│   │   ├── <span style="color: #5555FF; "><b>database</b></span>
│   │   ├── <span style="color: #5555FF; "><b>ole_consulta_status</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>data</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   │   ├── <span style="color: #5555FF; "><b>ole_insercao</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>data</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   │   ├── <span style="color: #5555FF; "><b>ole_liberacao</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>data</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   │   ├── <span style="color: #5555FF; "><b>reenvio_sms</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>data</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   │   └── <span style="color: #5555FF; "><b>robos</b></span>
│   ├── <span style="color: #5555FF; "><b>oleOrientaStatusProposta</b></span>
│   ├── <span style="color: #5555FF; "><b>pan</b></span>
│   │   ├── <span style="color: #5555FF; "><b>database</b></span>
│   │   ├── <span style="color: #5555FF; "><b>pan_insercao</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   │   ├── <span style="color: #5555FF; "><b>data</b></span>
│   │   │   └── <span style="color: #5555FF; "><b>manager</b></span>
│   │   └── <span style="color: #5555FF; "><b>robos</b></span>
│   ├── <span style="color: #5555FF; "><b>portal_consig</b></span>
│   │   ├── <span style="color: #5555FF; "><b>auto</b></span>
│   │   ├── <span style="color: #5555FF; "><b>data_handlers</b></span>
│   │   └── <span style="color: #5555FF; "><b>managers</b></span>
│   ├── <span style="color: #5555FF; "><b>promoBank</b></span>
│   ├── <span style="color: #5555FF; "><b>__pycache__</b></span>
│   └── <span style="color: #5555FF; "><b>situacaoBeneficio</b></span>
├── <span style="color: #5555FF; "><b>start</b></span>
├── <span style="color: #5555FF; "><b>venv</b></span>
│   ├── <span style="color: #5555FF; "><b>bin</b></span>
│   ├── <span style="color: #5555FF; "><b>include</b></span>
│   ├── <span style="color: #5555FF; "><b>lib</b></span>
│   │   └── <span style="color: #5555FF; "><b>python3.7</b></span>
│   │       └── <span style="color: #5555FF; "><b>site-packages</b></span>
│   └── <span style="color: #5555FF; "><b>lib64</b></span> -&gt; <span style="color: #5555FF; "><b>lib</b></span>
</pre>