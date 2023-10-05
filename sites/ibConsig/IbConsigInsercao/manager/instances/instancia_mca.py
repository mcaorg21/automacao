import pdb,sys
#sys.path.append('../../../../../')
from dados.database.queries.query_dados_robos import query_login_pass_robo
from dados.helpers.condicionais_apis import minimo_n_contratos_fila
from sites.ibConsig.IbConsigInsercao.manager.insercao_refin_novo.insercao import InsercaoIbConsig
import PATHS
from sites.baseRobos.core.helpers import definir_nome_robo, aguardar_n_segundos
from datetime import datetime

def main():
    hoje = datetime.today().isoweekday()

    if(hoje == 1 or hoje == 3):
        usuario = "cristiano.1873"
    elif(hoje == 2 or hoje == 4):
        usuario = "carolina.1873"
    else:
        usuario = "carolina.1873"

    dados_login = query_login_pass_robo(1, usuario)
    login = dados_login['login']
    senha = dados_login['senha']


    config = {
        'usuario': login,
        'senha': senha,
        'chrome_user': PATHS.chrome_user("IbConsigInsercao"+usuario),
        'ordem': 'asc',
    }

    if not minimo_n_contratos_fila(n=3, nome_banco="itau"):
        aguardar_n_segundos(900)
        raise ConnectionAbortedError("N contratos < 15... abortando inicialização")

    run = InsercaoIbConsig(**config)
    run.data.instancia = "Terciaria"
    definir_nome_robo("Itau - Insercao Terciaria")

    run.main()


if __name__ == "__main__":
    main()
