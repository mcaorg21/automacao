import pdb,sys
#sys.path.append('../../../../../')
from sites.ibConsig.IbConsigInsercao.manager.insercao_refin_novo.insercao import InsercaoIbConsig
from dados.database.queries.query_dados_robos import query_login_pass_robo
import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.helpers import aguardar_n_segundos
from dados.helpers.condicionais_apis import minimo_n_contratos_fila
from datetime import datetime

def main():
    hoje = datetime.today().isoweekday()

    if(hoje == 1 or hoje == 3):
        usuario = "mca1873"
    elif(hoje == 2 or hoje == 4):
        usuario = "cristiano.1873"
    else:
        usuario = "mca1873"

    dados_login = query_login_pass_robo(1, usuario)
    login = dados_login['login']
    senha = dados_login['senha']


    config = {
        'usuario': login,
        'senha': senha,
        'chrome_user': PATHS.chrome_user("IbConsigInsercao"+usuario),
        'ordem': 'asc',
    }

    if not minimo_n_contratos_fila(n=10, nome_banco="itau"):
        aguardar_n_segundos(900)
        raise ConnectionAbortedError

    run = InsercaoIbConsig(**config)
    run.data.instancia = "Secundaria"
    definir_nome_robo("Itau - Insercao Secundaria")
    run.main()

if __name__ == "__main__":
    main()
