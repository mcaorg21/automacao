# Como adicionar um novo card de robô em /ativacao

O painel `/ativacao` exibe cards para controlar cada robô (ligar/desligar).
O `Initializr` monitora o `ativacao.json` e sobe/derruba os subprocessos correspondentes.

---

## Arquivos envolvidos

| Arquivo | Função |
|---|---|
| `initializr/ativacao.json` | Estado atual de cada robô (`true`/`false`) |
| `initializr/process_labels.json` | Rótulo exibido no card |
| `initializr/processos_automacao/config/robos_main_paths.py` | Caminho do `main.py` do robô |
| `initializr/processos_automacao/classes_processos/ProcessoNomeRobo.py` | Classe que sobe o subprocesso |
| `initializr/processos_automacao/classes_processos/__init__.py` | Importa a nova classe |
| `initializr/processos_automacao/classes_processos/InstanciasProcessos.py` | Registra a instância no Initializr |
| `automacao_app/controller/ativacao.py` | Controla quais robôs aparecem no painel (`PROCESSOS_VISIVEIS`) |
| `automacao_app/static/template/ativacao.html` | Template HTML dos cards |

---

## Passo a passo

### 1. Definir a chave do robô

Escolha uma chave em **PascalCase** que identifique o robô. Ela será usada como identificador em todos os arquivos abaixo. Exemplo: `CpjReembolsoPan`.

---

### 2. Registrar no `ativacao.json`

Arquivo: `initializr/ativacao.json`

Adicione a chave com valor `false` (desativado por padrão):

```json
{
  "CpjReembolsoBmg": true,
  "OmniPdeFspTrc": false,
  "CpjReembolsoPan": false
}
```

---

### 3. Adicionar o label em `process_labels.json`

Arquivo: `initializr/process_labels.json`

Adicione o rótulo amigável exibido no card:

```json
{
  "CpjReembolsoBmg": "Banco BMG - Reembolso SPF - CPJ",
  "OmniPdeFspTrc": "Banco Omni - Cadastro Eventos - CPJ",
  "CpjReembolsoPan": "Banco PAN - Reembolso SPF - CPJ"
}
```

---

### 4. Registrar o caminho do script em `robos_main_paths.py`

Arquivo: `initializr/processos_automacao/config/robos_main_paths.py`

Adicione uma entrada no dict `main_paths` com o caminho relativo ao diretório `sites/`:

```python
main_paths: dict = {
    # ...
    "CpjReembolsoBmg": "/cpj-reembolso-bmg/main.py",
    "OmniPdeFspTrc": "/omni-pde-fsp-trc/main.py",

    # Novo robô
    "CpjReembolsoPan": "/cpj-reembolso-pan/main.py",
}
```

---

### 5. Criar a classe do processo

Crie o arquivo `initializr/processos_automacao/classes_processos/ProcessoCpjReembolsoPan.py`.

Para um robô simples (sem validação de config), copie o padrão do Omni:

```python
from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper
from initializr.processos_automacao.config.MainConfig import MainConfig
from time import sleep
from initializr.processos_automacao import STDWAIT


class CpjReembolsoPan(ProcessWrapper):
    def __init__(self):
        super().__init__(proc_name=self.__class__.__name__)
        self.__config: MainConfig = MainConfig()
        self.__config.load_process_path(self.proc_name)

    @property
    def main_config(self) -> MainConfig:
        return self.__config

    def run(self):
        process = self.__config.build_sub_process()
        self.cmd_proc = process
        self.set_py_sub_process(process)

        sleep(STDWAIT)
        self.all_procs = self.get_children_safe(process)
```

Se o robô precisar validar um `config.json` antes de subir (como o BMG), adicione um método `_config_valida()` e chame-o no início do `run()`. Veja `ProcessoCpjReembolsoBmg.py` como referência.

---

### 6. Importar a classe no `__init__.py`

Arquivo: `initializr/processos_automacao/classes_processos/__init__.py`

Adicione a importação ao final do arquivo:

```python
from initializr.processos_automacao.classes_processos.ProcessoCpjReembolsoBmg import CpjReembolsoBmg
from initializr.processos_automacao.classes_processos.ProcessoOmniPdeFspTrc import OmniPdeFspTrc

# Novo robô
from initializr.processos_automacao.classes_processos.ProcessoCpjReembolsoPan import CpjReembolsoPan
```

---

### 7. Adicionar a instância em `InstanciasProcessos.py`

Arquivo: `initializr/processos_automacao/classes_processos/InstanciasProcessos.py`

Adicione uma entrada no dict `INSTANCIAS`. A **chave deve ser exatamente igual** à chave usada em `ativacao.json`:

```python
INSTANCIAS: Dict[str, ProcessWrapper] = {
    # ...
    "CpjReembolsoBmg": CpjReembolsoBmg(),
    "OmniPdeFspTrc": OmniPdeFspTrc(),

    # Novo robô
    "CpjReembolsoPan": CpjReembolsoPan(),
}
```

---

### 8. Adicionar à lista `PROCESSOS_VISIVEIS` no controller

Arquivo: `automacao_app/controller/ativacao.py`, linha 153

Essa lista controla quais robôs aparecem no painel. Adicione a nova chave:

```python
PROCESSOS_VISIVEIS = ["CpjReembolsoBmg", "OmniPdeFspTrc", "CpjReembolsoPan"]
```

> Robôs que existem no `ativacao.json` mas **não** estão em `PROCESSOS_VISIVEIS` ficam ocultos no painel (mas o Initializr ainda os controla normalmente).

---

### 9. (Opcional) Adicionar modal de configurações

Se o robô precisar de um painel de configuração (como BMG e Omni), siga os sub-passos abaixo.

#### 9a. Botão no card — `ativacao.html`

Dentro do bloco `{% for key, val in procs.items() %}`, adicione o bloco condicional para o novo robô (após o toggle de ativar/desativar):

```html
{% if key == "CpjReembolsoPan" %}
    <hr class="cpj-divider">
    <button class="config-toggle" type="button" onclick="openModal('modal-pan')">
        &#9881; Configurações
    </button>
{% endif %}
```

#### 9b. HTML do modal — `ativacao.html`

Antes do `<script>` final, adicione o modal:

```html
<!-- Modal PAN -->
<div class="modal-overlay" id="modal-pan" onclick="closeOnOverlay(event, 'modal-pan')">
    <div class="modal-box">
        <div class="modal-header">
            <span class="modal-title">&#9881; Banco PAN — Configurações</span>
            <button class="modal-close" type="button" onclick="closeModal('modal-pan')">&#10005;</button>
        </div>
        <hr class="cpj-divider">
        <form method="post" action="{{ url_for('ativacao.salvar_pan_config') }}"
              style="display:flex;flex-direction:column;gap:12px;">
            <!-- Campos de configuração aqui -->
            <button type="submit" class="btn-save">Salvar</button>
        </form>
    </div>
</div>
```

#### 9c. Rota de configuração — `ativacao.py`

```python
@bp.route("/ativacao/pan-config", methods=["POST"])
def salvar_pan_config():
    campo = request.form.get("campo", "")

    pan_config_file = str(Path(INITIALIZR_ROOT).parent / "sites/cpj-reembolso-pan/config.json")
    with open(pan_config_file, encoding='utf-8') as f:
        config_atual = json.loads(f.read())

    config_atual.update({"campo": campo})

    with open(pan_config_file, mode="w", encoding='utf-8') as f:
        f.write(json.dumps(config_atual, ensure_ascii=False, indent=4))

    return redirect(url_for("ativacao.ativacao"))
```

#### 9d. Passar o config para o template — `ativacao.py`

Na função `ativacao()`, carregue o config e passe ao `render_template`:

```python
pan_config_file = str(Path(INITIALIZR_ROOT).parent / "sites/cpj-reembolso-pan/config.json")
with open(pan_config_file, encoding='utf-8') as f:
    pan_config = json.loads(f.read())

return render_template(
    "ativacao.html",
    procs=procs,
    cpj_config=cpj_config,
    omni_config=omni_config,
    pan_config=pan_config,
    labels=labels
)
```

---

## Resumo rápido (card simples, sem modal)

```
1. initializr/ativacao.json                          → "NomeRobo": false
2. initializr/process_labels.json                    → "NomeRobo": "Nome Legível"
3. initializr/processos_automacao/config/
       robos_main_paths.py                           → "NomeRobo": "/pasta/main.py"
4. initializr/processos_automacao/classes_processos/
       ProcessoNomeRobo.py                           → criar classe herdando ProcessWrapper
5. initializr/processos_automacao/classes_processos/
       __init__.py                                   → importar a nova classe
6. initializr/processos_automacao/classes_processos/
       InstanciasProcessos.py                        → "NomeRobo": NomeRobo()
7. automacao_app/controller/ativacao.py              → adicionar "NomeRobo" em PROCESSOS_VISIVEIS
```

Pronto — o card aparece no painel e o Initializr já controla o processo automaticamente.


#automacao #instrucoes #adicionar-robo-automacao 