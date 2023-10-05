#####################################################
## /sites/oleConsignado/robo_refin_anex_lib_sms.py ##
#####################################################
from pathlib import Path
from time import sleep
from typing import List
import sys,json,pickle,requests

from selenium.webdriver import Chrome

import PATHS
from dados.database.LoginDBDataSource import LoginDBDataSource
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.manager import Manager
from sites.oleConsignado.anexar_documentos.anexar_documentos import AnexarDocumentos
from sites.oleConsignado.config.paths_ole import PATH_ID_4,PATH_COOKIES_JSON
from sites.oleConsignado.libs.FormLogin import FormLogin
from sites.oleConsignado.ole_consulta_status.managers.consultaStatus import ConsultaStatusOle
from sites.oleConsignado.ole_liberacao.managers.ole_executa_liberacao import ExecutaLiberacaoOle
from sites.oleConsignado.reenvio_sms.managers.reenvio_sms import ReenvioSMS

PREFS = {
    "download.default_directory": str(Path(PATHS.project_path() + '/OleConsignado/anexos/')),
    'profile.default_content_setting_values.automatic_downloads': True,
    'download.prompt_for_download': False,
    "plugins.always_open_pdf_externally": True
}


class Main:
    id_banco: int = 123
    id_robo: int = 4
    TITLE = "Ole - Refin/Sincronizacao/Anexo/Liberacao/SMS"

    base_path: str = PATHS.project_path()
    cookies_path = PATH_ID_4
    cookies_path_json = PATH_COOKIES_JSON

    def __init__(self):
        self.chrome_user: str = PATHS.chrome_user('OleConsig')
        self.driver_path: str = PATHS.driver_path()

        Manager().criar_pasta_usuario_chrome(self.chrome_user)

        self.driver: Chrome = Manager.driver_factory(
            self.chrome_user, '--ignore-ssl-errors', "--log-level=3", w3c=False, prefs=PREFS)
        self.auth: LoginDBDataSource = LoginDBDataSource(4)

    def main(self):
        definir_nome_robo(self.TITLE)
        cli_args = check_args(sys.argv[1:])
        self.driver.get('https://ola.oleconsignado.com.br/Home')

        #self.auth.nome_usuario = cli_args.get("login")
        #self.auth.load_dados_login()

        if cli_args.get("cookies", False):
            input("\n\n Aguardando inserir cookies manualmente. "
                  "Aperte ENTER para seguir >>> \n\n")

        for i in range(480):
            self.manter_sessao_logada()
            self.main_loop()
            sleep(60)

        self.driver.quit()
        sleep(600)
        raise KeyboardInterrupt

    def main_loop(self):
        tarefas: List[object] = [ConsultaStatusOle,
                                 ExecutaLiberacaoOle]
        #ReenvioSMS #AnexarDocumentos
        try:
            for tarefa in tarefas:
                print(f"\nIniciando Tarefa {tarefa.__class__.__name__}")
                tarefa.iniciar_horario_comercial(self.driver)
                self.manter_sessao_logada()

        except Exception as e:
            print(e)

    def manter_sessao_logada(self):
        #if FormLogin.realizar_login(self.driver, self.auth.login, self.auth.senha):
        if FormLogin.realizar_login(self.driver, "MARCELOCALEWE", "Marcelo@21"):
            print("Não ira salvar cookies...")
            #SeleniumHelper(self.driver).save_cookies(self.cookies_path)
            #self.salva_cookies_escreve_json()

    def salva_cookies_escreve_json(self):
        self.selenium_helper = SeleniumHelper(self.driver).save_cookies(self.cookies_path)

        with open(self.cookies_path, 'rb') as fpkl, open(self.cookies_path_json, 'w') as fjson:
            data = pickle.load(fpkl)
            json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)
            
            
        file = open(self.cookies_path_json)
        cookies = json.load(file)
        dados = {
                    'id_robo' : self.id_robo,
                    'cookies_json': json.dumps(cookies)
                }

        req = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/portal_ola_ole/?key=f689f1e12a0399fba803cb2365fc362f", data=dados)
        if(req.status_code == 200):
            print('Cookies salvos com sucesso!')


def check_args(args_list: List[str]) -> dict:
    args_dict = {}
    for arg in args_list:
        if "-L=" in arg:
            print(arg)
            args_dict["login"] = arg.replace("-L=", "")

        if arg == "-c":
            args_dict["cookies"] = True

    return args_dict


if __name__ == '__main__':
    run = Main()
    run.main()
