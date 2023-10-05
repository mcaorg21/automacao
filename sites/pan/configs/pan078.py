"""
Configs: ordem reversa, caso o login caia, aguarda 20 minutos, filtro: apenas ímpares.
Consulta apenas os 10 primeiros itens da lista.
"""
from typing import Dict

from dados.database.queries.query_dados_robos import query_login_pass_robo

login: Dict[str, str] = query_login_pass_robo(31, '07823888688')

configs: dict = {
    **login,
    "verificar_sessao": True,
    "ordem_inversa": False,
    "nome_robo": "PanConsultaRefin078"
}
