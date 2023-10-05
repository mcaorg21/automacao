from login_dados.login import Dados
from automacao.gerar_contrato import IbConsig_gerar
from automacao.extrair_tags import Extrair_tags
import threading
from sites.baseRobos.core.helpers import definir_nome_robo
import sys
import pdb

class Itau_Sincronizacao_ICdigital():
    def __init__(self):
        self.ligar = False
        self.dados = Dados()
        self.anexar = IbConsig_gerar()
        


    def iniciar_robos(self):
        definir_nome_robo(f"Itau - Anexa Itau ICcDigital")
        self.anexar.login(self.dados.retornar_infos(), self.dados.retornar_infos2())
        self.anexar.iniciar()


x = Itau_Sincronizacao_ICdigital().iniciar_robos()



