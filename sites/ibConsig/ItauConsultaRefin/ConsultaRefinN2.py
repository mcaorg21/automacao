from sites.ibConsig.ItauConsultaRefin.managers.IbConsultaRefin import IbConsultaRefin
from sites.ibConsig.ItauConsultaRefin.configs import cnf_refin_n2
from sites.baseRobos.core.helpers import definir_nome_robo


def main():
    ib_refin = IbConsultaRefin.retornar_instancia_login(**cnf_refin_n2.cnf)
    try:
        ib_refin.id_instacia = 2
        ib_refin.data.instancia = "LOGIN"
        definir_nome_robo(f"Itau - Consulta Refinanciamento Login")

        ib_refin.main()
    except Exception as e:
        print(e)
        ib_refin.driver.quit()


if __name__ == "__main__":
    main()
