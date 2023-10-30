from typing import Callable, List, Dict

from PATHS import chrome_user
from dados.helpers.fileHandlers.FileHandler import FileHandler
from dados.helpers.fileHandlers.PdfHandler import PdfHandler
from sites.baseRobos.manager import Manager
from sites.ibConsig.gerarContrato.data.APIsItauGerarContrato import APIsItauGerarContrato
from sites.ibConsig.gerarContrato.data.InfosContrato import InfosContrato
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig
from selenium.webdriver import Chrome
from sites.ibConsig.gerarContrato.configs.uri import (
    PATH_CONDICOES, PATH_ORIENTACOES, URL_LOGIN,
    DEFAULT_FILE, URL_DOWNLOAD, PATH_CONTRATOS
)
from sites.ibConsig.gerarContrato.configs.driverOptions import PREFS
from sites.ibConsig.gerarContrato.tests import mock

from sites.baseRobos.core.helpers import deleta_todos_arquivos

import pdb
import PATHS
from pathlib import Path

class ItauGerarContratos(Manager):

    #def __init__(self, driver: Chrome, login: str, senha: str):
    def __init__(self, driver: Chrome):
        super().__init__()
        self.init_chrome_driver(import_driver=driver)

        #self.login = login
        #self.senha = senha

        self.api = APIsItauGerarContrato()

        self.orientacoesPdf: FileHandler = FileHandler(PATH_ORIENTACOES)
        self.condicoesPdf: FileHandler = FileHandler(PATH_CONDICOES)

        # self.realizarLogin: Callable = IbConsig.login_fact(
        #     usuario=self.login, senha=self.senha, driver=self.driver)

    def aguardarLogin(self):
        cnt = 0
        while not self.realizarLogin():
            self.driver.get(URL_LOGIN)
            if IbConsig.esta_logado(self.driver):
                break
            cnt += 1
            print(f"[{cnt}] Tentando realizar login...")

        print("Login realizado com sucesso!")

    def selecionarContratosParaDownload(self):
        print("Buscando contratos para download")
        #mock.contratos
        listContratos: List[Dict[str, str]] = self.api.buscar_contratos_gerar()

        if not listContratos:
            return

        for contrato in listContratos:
            infosContrato: InfosContrato = InfosContrato(**contrato)

            self.api.iniciarLogGerarContrato(infosContrato.codigo)

            print('Deletando arquivos da pasta...')
            deleta_todos_arquivos(str(Path(PATHS.project_path())) + "/ibConsig/anexos/contratos")

            pdfHandler: PdfHandler = PdfHandler()
            if infosContrato.novoContrato or infosContrato.refinanciamento or infosContrato.aumento_margem or infosContrato.refinanciamento_margem:
                # if(contrato['assDigital'] == '1' and not infosContrato.aumento_margem):
                #     print('Anexando orientações para contratos')
                #     pdfHandler.addPdfToQueue(self.orientacoesPdf)
                pdf = self.baixarContrato(infosContrato.ade)
                if pdf == False:
                    print('Pulando contrato por erro no sistema...')
                    return
                    continue
                pdfHandler.addPdfToQueue(pdf)
                #pdfHandler.addPdfToQueue(self.condicoesPdf)
                ade_gerar = infosContrato.ade
            elif infosContrato.portabilidade:
                #if('INSS' not in infosContrato.orgao):                    
                #    pdfHandler.addPdfToQueue(self.orientacoesPdf)
                #pdfHandler.addPdfToQueue(self.baixarContrato(infosContrato.ade))
                ade_refin_portabilidade = str(int(infosContrato.ade_refin_portabilidade))
                pdf = self.baixarContrato(ade_refin_portabilidade)
                if pdf == False:
                    print('Pulando contrato por erro no sistema...')
                    return
                    continue
                pdfHandler.addPdfToQueue(pdf)
                #retirado para o banco nao ler como retencao portabilidade
                #pdfHandler.addPdfToQueue(self.condicoesPdf)
                ade_gerar = ade_refin_portabilidade
            else:
                pdf = self.baixarContrato(infosContrato.ade)
                if pdf == False:
                    print('Pulando contrato por erro no sistema...')
                    return
                    continue
                pdfHandler.addPdfToQueue(pdf)
                pdfHandler.addPdfToQueue(self.condicoesPdf)
                ade_gerar = infosContrato.ade

            unificadoPdf = pdfHandler.mergePdfsFromQueue(
                output_path=f"{PATH_CONTRATOS}/{ade_gerar}.pdf")

            print(f"Enviando Contrato: {unificadoPdf}")
            
            self.api.enviarPdfContrato(infosContrato, pdfUnificado=unificadoPdf)

            unificadoPdf.remove()

    def baixarContrato(self, ade: str) -> FileHandler:
        print("Realizando Download do Contrato")
        srcDownload = URL_DOWNLOAD + ade
        contratoPdf = FileHandler(path=DEFAULT_FILE, src=srcDownload)

        if contratoPdf.downloadFromWebDriver(self.driver) == False:
            return False
        
        if not contratoPdf.exists:
            raise Exception("Contrato não pôde ser baixado!")

        print("Contrato baixado com sucesso. Renomeando contrato...")

        contratoPdf.rename(f"{ade}.pdf")

        return contratoPdf


if __name__ == "__main__":

    #driver = Manager.driver_factory(chrome_user("ItauGerarContrato"), prefs=PREFS)
    #Manager.criar_pasta_usuario_chrome(chrome_user("ItauGerarContrato"))

    #gerar = ItauGerarContratos(driver=driver, login="saulo.1873p", senha="Marcelo@39")
    #gerar.aguardarLogin()
    gerar.selecionarContratosParaDownload()
