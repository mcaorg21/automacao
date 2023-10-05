import sys
sys.path.append('../../')
#sys.path.append('../')
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.safra.insercao import Consulta_Safra
from time import sleep


HORARIO_COMERCIAL = 7, 22


class Insercao_2():

    TITLE = "Safra - Insercao 2"

    def __init__(self):
        self.robo_insercao = Consulta_Safra()

    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        self.robo_insercao.main(url_get = True, title = "Safra - Insercao - Pendentes")

if __name__ == '__main__':
    robo = Insercao_2()
    while True:
	    robo.main()
	    sleep(60)
  