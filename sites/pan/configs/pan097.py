"""
Configs: ordem reversa, sem verificar sessao caso o login caia, fazendo login
novamente sem aguardar,, filtro: apenas pares. Consulta apenas os 10 primeiros
itens da lista.
"""
from typing import Dict

from dados.database.queries.query_dados_robos import query_login_pass_robo

login: Dict[str, str] = query_login_pass_robo(13, '09760596652')

configs: dict = {
    **login,
    "verificar_sessao": False,
    "ordem_inversa": True,
    "filtro": lambda x: int(x.get("idSolicitacao", x["idPessoa"])) % 2 != 0,
    "min_len": 10,
    "nome_robo": "PanConsultaRefin035"
}
