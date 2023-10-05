from dados.database.db_conf.connection import conect_db


class LoginDBDataSource:
    def __init__(self, id_robo: int, nome_usuario: str=""):
        self.db = conect_db()
        self.cur = self.db.cursor()
        self.nome_usuario = nome_usuario
        self.id_robo = id_robo
        self.__login = ""
        self.__senha = ""

    #@property
    def login(self):
    #    if not self.__login:
    #        raise EmptyDataAccessAttemptException(campo="login")
        return self.__login

    #@property
    def senha(self):
    #    if not self.__senha:
    #        raise EmptyDataAccessAttemptException(campo="senha")
        return self.__senha

    def load_dados_login(self):
        self.cur.execute(
            "SELECT login,senha FROM tbl_repositorio_adm"
            f" WHERE fk_idRobo IN ({self.id_robo}) AND login LIKE '%{self.nome_usuario}%'")
        res = self.cur.fetchone()

        self.__login = res["login"]
        self.__senha = res["senha"]

        print("Dados login:", res)

    def __repr__(self):
        return f"LoginDBDataSource(login:{self.__login}, senha: {self.__senha})"


class EmptyDataAccessAttemptException(Exception):
    def __init__(self, campo: str):
        super().__init__()
        self.msg = (f"Campo {campo} vazio. Se certifique de ter realizado carregado\n"
                    f"os dados por meio do metodo LoginDBDataSource.load_dados_login")

    def __repr__(self):
        return self.msg
