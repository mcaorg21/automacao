
from dados.database.queries.query_dados_robos import query_login_pass_robo

dados_login = query_login_pass_robo(27, '03507179660')


configs: dict = {
    "login": dados_login['login'],
    "senha": dados_login['senha'],
    "verificar_sessao": False,
    "ordem_inversa": False,
    "parceiros": "003442",
    "nome_robo": "PanConsultaRefin035",
    "headless": "--headless"
}
