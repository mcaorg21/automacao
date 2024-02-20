from typing import Dict

from dados.database.db_conf.connection import conect_db


def query_login_pass_robo(id_robo: int, login: str) -> Dict[str, str]:
    db = conect_db()
    cur = db.cursor()

    cur.execute(
        "SELECT login,senha,link FROM tbl_repositorio_adm"
        f" WHERE fk_idRobo IN ({id_robo}) AND login LIKE '%{login}%'")
    res = cur.fetchone()

    print("Dados login:", res)

    return res


