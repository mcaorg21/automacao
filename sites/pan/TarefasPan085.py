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
from sites.pan.auxiliares.sessao import login
from pathlib import Path
from sites.pan.configs.pan097 import configs
from time import sleep


PREFS = {
    "download.default_directory": str(Path(PATHS.project_path() + "/pan/anexos/")),
    'profile.default_content_setting_values.automatic_downloads': True,
    'download.prompt_for_download': False,
    'plugins.plugins_disabled': 'Chrome PDF Viewer'
}


class Main:
    id_robo: int = 13
    timer: int = 60
    id_banco: int = 68

    TITLE = 'Pan Todas Tarefas 097'
    PNAME = 'pan_id1'

    def __init__(self):
        self.chrome_user: str = PATHS.chrome_user('TarefasPan097')
        print(self.chrome_user)
        Manager().criar_pasta_usuario_chrome(self.chrome_user)
        self.driver_path: str = PATHS.driver_path()
        self.base_path: str = PATHS.project_path()

        opts = ('--ignore-ssl-errors', self.chrome_user, 'log-level=3',"--no-sandbox","--window-size=1150,600")
        exp_opt = {"prefs": PREFS}
        self.driver = Manager.driver_factory(*opts, **exp_opt)
        self.ocioso: int = 0

        self.caminho_base = PATHS.project_path()
        self.cookies_path = self.caminho_base+"\\pan\\cookies\\" + "usuario_097.pkl"
        self.cookies_path_json = self.caminho_base+"\\pan\\cookies\\" + "usuario_097.json"
        self.driver.delete_all_cookies()

    def main(self):
        definir_nome_robo(self.TITLE)

        login(self.driver, cpf_login=configs['login'], senha=configs['senha'])

        while True:
            definir_nome_robo(self.TITLE)
            #self.save_cookies(self.cookies_path)
            
            #PanInsercaoMan.iniciar_horario_comercial(self.driver, configs)
            #GerarContratos.iniciar_horario_comercial(self.driver, configs)
            #Pan.iniciar_horario_comercial(self.driver, configs)
            ConsultaRefin.get_standalone_instance(driver=self.driver, **configs).consultar_refins_e_potenciais()         
            
            # definir_nome_robo(self.TITLE)
            # self.ocioso += PanAnexoDocsMan.iniciar_horario_comercial(self.driver, configs)
            print("Aguardando 1 minuto para reiniciar as atividades")
            # print("Aguardando 5 minutos para reiniciar as atividades")
            # sleep(600)
            # if self.ocioso <= -5:
            #     print("Aguardando 5 minutos para reiniciar as atividades")
            #     self.driver.quit()
            #     sleep(600)
            #     return 0
            print('Aguardando 180s...')
            sleep(180)

    def save_cookies(self, cookies_path):
        pickle.dump(self.driver.get_cookies(), open(cookies_path, "wb"))
        print(self.driver.get_cookies())



if __name__ == '__main__':
    run = Main()
    run.main()
