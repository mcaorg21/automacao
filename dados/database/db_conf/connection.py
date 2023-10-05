import pymysql
from dados.helpers import retrieve_data


def conect_db(database: str="consige5"):
    db = pymysql.connect(
        host=retrieve_data("DB_HOST"),
        user=retrieve_data("DB_USER"),
        db=database,
        password=retrieve_data("DB_PASS"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return db
