##################################
####### /sites/pan/main.py #######
##################################


import PATHS
import pickle
from sites.pan.pan_gerar_contratos.gerar_contratos import GerarContratos
from sites.pan.pan_consulta_status.consulta_status_pan import Pan
from sites.pan.pan_anexo_docs.manager.anexo_docs import PanAnexoDocsMan
# Imports Classes Robôs
from sites.pan.pan_insercao.manager.pan_inserc_man import PanInsercaoMan
from sites.baseRobos.manager import Manager
from sites.baseRobos.core.helpers import definir_nome_robo, aguardar_n_segundos
from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import ConsultaRefin
from pathlib import Path
from sites.pan.configs.pan064 import configs
from sites.pan.auxiliares.sessao import login
from time import sleep

PREFS = {
    "download.default_directory": str(Path(PATHS.project_path() + "/pan/anexos/")),
    'profile.default_content_setting_values.automatic_downloads': True,
    'download.prompt_for_download': False,
    'plugins.plugins_disabled': 'Chrome PDF Viewer'
}
ID_BANCO: int = 68


class TarefasPan064:

    timer: int = 60
    TITLE = 'Pan Todas Tarefas 064 Cookies'

    def __init__(self):
        self.chrome_user: str = PATHS.chrome_user('Pancred064Cookies')
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        self.driver_path: str = PATHS.driver_path()
        self.base_path: str = PATHS.project_path()

        opts = ('--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,1080")
        exp_opt = {"prefs": PREFS}
        self.driver = Manager.driver_factory(*opts, **exp_opt)
        self.ocioso: int = 0
        self.caminho_base = PATHS.project_path()
        self.cookies_path = self.caminho_base+"\\pan\\cookies\\" + "usuario_064.pkl"

    def main(self):
        definir_nome_robo(self.TITLE)

        while True:
            definir_nome_robo(self.TITLE)
            self.driver.get("https://panconsig.pansolucoes.com.br/WebAutorizador/Login/AC.UI.LOGIN.aspx")
            self.load_cookies(self.cookies_path)
            self.driver.get("https://panconsig.pansolucoes.com.br/WebAutorizador/Cadastro/CardOferta")
            PanInsercaoMan.iniciar_horario_comercial(self.driver, configs)
            #GerarContratos.iniciar_horario_comercial(self.driver, configs)
            #Pan.iniciar_horario_comercial(self.driver, configs)
            #ConsultaRefin.get_standalone_instance(driver=self.driver, **configs).consultar_refins_e_potenciais()    
            
            # self.ocioso += PanAnexoDocsMan.iniciar_horario_comercial(self.driver, configs)
            print("Aguardando 1 minuto para reiniciar as atividades")
            # sleep(600)
            # if self.ocioso <= -5:
            #     print("Aguardando 10 minutos para reiniciar as atividades")
            #     self.driver.quit()
            #     sleep(600)
            #     return 0
            #sleep(60)

    def load_cookies(self, cookies_path, delete=False):
        if delete:
            self.driver.delete_all_cookies()
        for cookie in pickle.load(open(cookies_path, "rb")):
            self.driver.add_cookie(cookie)


if __name__ == '__main__':
    run = TarefasPan064()
    run.main()
