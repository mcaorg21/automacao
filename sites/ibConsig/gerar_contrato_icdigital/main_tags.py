from automacao.extrair_tags import Extrair_tags
from sites.baseRobos.core.helpers import definir_nome_robo

class Extrair_Tags_ICcdigital():
    def __init__(self):
        definir_nome_robo(f"Itau - Extrair Tags Itau ICcDigital")
        self.tags = Extrair_tags()


    def iniciar_robos(self):
        self.tags.iniciar()

x = Extrair_Tags_ICcdigital().iniciar_robos()