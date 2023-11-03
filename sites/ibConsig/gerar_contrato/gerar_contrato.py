import sys
sys.path.append('../')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os,pdb
import time
import requests
import pikepdf
import re
from sites.core.helpers import countdown
from datetime import datetime
from sites.core.captcha import TwoCaptcha
from sites.core.selenium_helper import SeleniumHelper
from sites.core.selenium_actions import SeleniumActions

from sites.ibConsig.cookies import COOKIES_GERAR_CONTRATO
from sites.ibConsig.libs.auxiliares.ib_consig import HORARIO_COMERCIAL
from sites.core.uconecte import Uconecte
from sites.baseRobos.core.helpers import convert_file_base_64, apagar_arquivos, aguardar_n_segundos
from sites.baseRobos.core.helpers import (
    identificar_erro_robo, definir_nome_robo)
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, InvalidElementStateException
)
from sites.baseRobos.manager import Manager
import PATHS
from sites.baseRobos.data_handler import DataHandler
from sites.baseRobos.core.DebugTools import DebugTools
from sites.baseRobos.core.decorators import AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from pathlib import Path
from sites.ibConsig.libs.exceptions.Exceptions import SessaoExpiradaError
from sites.ibConsig.libs.auxiliares.ib_consig import IbConsig
from sites.ibConsig.gerarContrato.GerarContratos import ItauGerarContratos
dbg: DebugTools = DebugTools(debugging=False)
import shutil

def cookies_gerar_contrato():
    return GerarContratoIbConsig.cookies_path


class GerarContratoIbConsig(IbConsig):

    PNAME = "ib_id2"
    TITLE = 'Download contrato IbConsig'

    id_fila_liberar = 25
    id_fila_gerar_contrato = 2

    caminho_base = PATHS.project_path()
    cookies_path = COOKIES_GERAR_CONTRATO

    def __init__(self):
        super().__init__("saulo.1873", "t#909182", cookies_path=self.cookies_path)
        #super().__init__("cristiano.1873","t#909182", cookies_path=self.cookies_path)
        #super().__init__("mca1873","t#909182", cookies_path=self.cookies_path)
        
        # try:
        #     shutil.rmtree(self.caminho_base+'/chrome_user_dir/IbConsigGerarContrato')
        # except:
        #     pass
        self.chrome_user = PATHS.chrome_user('IbConsigGerarContrato')
        self.driver_path = PATHS.driver_path()


        self.contratos_pdf_path = str(Path(self.caminho_base+'/ibConsig/anexos/contratos'))
        self.pdfs_orientacoes_path = str(Path(self.caminho_base+'/ibConsig/anexos/unificados'))

        self.default_file_name = os.path.join(
            self.contratos_pdf_path, 'geraTermoAdesao.pdf')

        self.driver = self.iniciar_google_chrome()

        self.id_robo = 2

        self.uconecte = Uconecte()
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.captcha.captcha_path = ""
        self.selenium_helper = SeleniumHelper(self.driver)
        self.act = SeleniumActions(self.driver)
        self.contratos_vazio = False
        self.propostas_vazia = False
        self.log = DataHandler()

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls):
        run = GerarContratoIbConsig()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def iniciar_google_chrome(self):
        options = Options()
        #options.add_argument('--profile-directory=Default')
        options.add_argument('--ignore-ssl-errors')
        try:
            #pdb.set_trace()
            pasta = self.chrome_user.split('=')[1]
            shutil.rmtree(pasta)
        except:
            pass
        Manager.criar_pasta_usuario_chrome(self.chrome_user)
        options.add_argument(self.chrome_user)

        if not os.path.exists(self.contratos_pdf_path):
            os.mkdir(self.contratos_pdf_path)
        
        prefs = {
            "download.default_directory": self.contratos_pdf_path,
            'profile.default_content_setting_values.automatic_downloads': True,
            'download.prompt_for_download': False,
            'plugins.plugins_disabled': 'Chrome PDF Viewer',
            "plugins.always_open_pdf_externally": True
        }

        options.add_experimental_option('prefs', prefs)

        return webdriver.Chrome(
            #executable_path=self.driver_path,
            options=options)

    def main(self):
        self.driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
        try:
            definir_nome_robo('Itau - Gerar Contrato/Liberar Propostas')
            t = 0

            while not self.login_sistema():
                self.act.manusear_alerta('aceitar')
                t += 1
                if t > 5:
                    print(f"Foram realizadas {t} tentativas. Aguardando para recomeçar")
                    self.driver.quit()
                    aguardar_n_segundos(180)
                    raise SessaoExpiradaError

            self.selenium_helper.save_cookies(self.cookies_path)

            while True:
                if not IbConsig.esta_logado(self.driver):
                    raise SessaoExpiradaError

                print('Iniciando geração de contratos...')
                novo_gerar_contrato = ItauGerarContratos(self.driver)
                novo_gerar_contrato.selecionarContratosParaDownload()

                print("Iniciando liberação de propostas...")
                self.menu_liberar_proposta()
                self.liberar_proposta()

                print("Fila finalizada! Aguardando 60 segundos antes de iniciar novamente...")
                time.sleep(60)
                self.driver.refresh()

        except Exception as e:
            print(e)
            identificar_erro_robo()

    def menu_liberar_proposta(self):
        self.driver.get("https://www.ibconsigweb.com.br/liberacaoinconsistencias/resultadoLiberacaoInconsistencias.jsf")

    def liberar_proposta(self):
        try:
            self.liberar_proposta_272_274()
            #self.liberar_proposta_6_105()
            self.liberar_proposta_280()
            self.liberar_proposta_282()
            self.liberar_proposta_162()            
        except Exception as e:
            print(e)
            time.sleep(2)
            self.driver.refresh()

    def liberar_proposta_280(self, rec=0):
        try:
            print("Liberando consistências 280..")

            self.desmarcar_checkboxes()

            checked_280 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:10").checked""")
            if not checked_280:
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:10")

            self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                                                        "a.button.exibirCarregamento")

            if not self.tratar_erros():
                print("Nenhum registro encontrado para as consistências 280!")
                return

            while True:
                try:
                    try:
                        self.act.clicar_elemento("#j_idt207\\:0\\:modalDialogButton")
                    except TimeoutException:
                        self.act.clicar_elemento("#j_idt208\\:0\\:modalDialogButton")

                    time.sleep(1)
                    self.selenium_helper.atribuir_valor_campo_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")
                    self.selenium_helper.clicar_elemento_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")
                except TimeoutException:
                    break
        except StaleElementReferenceException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)
        except InvalidElementStateException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)

        print("Consistência 280 liberada!")
        return 0

    def liberar_proposta_282(self, rec=0):
        try:
            print("Liberando consistências 282..")

            self.desmarcar_checkboxes()

            checked_282 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:12").checked""")
            if not checked_282:
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:12")

            self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                                                        "a.button.exibirCarregamento")

            if not self.tratar_erros():
                print("Nenhum registro encontrado para as consistências 282!")
                return

            while True:
                try:
                    try:
                        self.act.clicar_elemento("#j_idt207\\:0\\:modalDialogButton")
                    except TimeoutException:
                        self.act.clicar_elemento("#j_idt208\\:0\\:modalDialogButton")

                    time.sleep(1)
                    self.selenium_helper.atribuir_valor_campo_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")
                    self.selenium_helper.clicar_elemento_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")
                except TimeoutException:
                    break
        except StaleElementReferenceException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)
        except InvalidElementStateException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)

        print("Consistência 282 liberada!")
        return 0

    def liberar_proposta_272_274(self, rec=0):
        try:
            print("Liberando consistências 272 e 274...")

            self.desmarcar_checkboxes()

            checked_272 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:8").checked""")
            if not checked_272:
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:8")

            checked_274 = self.driver.execute_script(
                """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:9").checked""")
            if not checked_274:
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:9")

            # checked_264 = self.driver.execute_script(
            #     """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:18").checked""")
            # if not checked_264:
            #     self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:18")

            self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                                                        "a.button.exibirCarregamento")

            if not self.tratar_erros():
                print("Nenhum registro encontrado para as consistências 272 e 274!")
                return

            while True:
                try:
                    try:
                        self.act.clicar_elemento("#j_idt207\\:0\\:modalDialogButton")
                    except TimeoutException:
                        self.act.clicar_elemento("#j_idt208\\:0\\:modalDialogButton")

                    time.sleep(1)
                    self.selenium_helper.atribuir_valor_campo_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")
                    self.selenium_helper.clicar_elemento_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")
                except TimeoutException:
                    break
        except StaleElementReferenceException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)
        except InvalidElementStateException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_272_274(rec+1)

        print("Consistência 272 e 274 liberadas!")
        return 0

    def liberar_proposta_6_105(self, rec=0):
        print("Liberando consistências 6 e 105...")
        try:
            self.desmarcar_checkboxes()

            checked_105 = self.driver.execute_script(
                """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:2").checked""")
            if not checked_105:
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:2")

            self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                                                        "a.button.exibirCarregamento")

            if not self.tratar_erros():
                print("Nenhum registro encontrado para as consistências 105!")
                return

            while True:
                try:
                    try:
                        self.act.clicar_elemento(f"#j_idt206 > table > tbody > tr.row1 > td:nth-child(15) > table > tbody > tr > td:nth-child(1)")
                    except:
                        self.act.clicar_elemento(f"#j_idt207 > table > tbody > tr.row1 > td:nth-child(15) > table > tbody > tr > td:nth-child(1)")

                    time.sleep(1)
                    self.selenium_helper.atribuir_valor_campo_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")
                    self.selenium_helper.clicar_elemento_driver(
                        "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")

                except TimeoutException:
                    break
        except StaleElementReferenceException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_6_105(rec+1)
        except InvalidElementStateException:
            if rec > 4:
                raise StaleElementReferenceException
            return self.liberar_proposta_6_105(rec+1)

        print("Consistência 6 e 105 liberadas!")
        return 0

    def liberar_proposta_162(self):
        print("Liberando consistências 162 e 180...")

        propostas = self.busca_propostas_liberar()
        self.desmarcar_checkboxes()

        for proposta in propostas[1:]:
            self.log.api_iniciar_log_robo(
                idRobo=self.id_fila_liberar,
                idContrato=proposta[2]
            )
            try:
                print(f"Liberando proposta {proposta[2]}")

                self.liberar_proposta_159(proposta)

                # if 'REFINANCIAMENTO' in proposta[3] or 'PORTABILIDADE' in proposta[3] :
                #     checked_180 = self.driver.execute_script(
                #         """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:5").checked""")
                #     if not checked_180:
                #         self.desmarcar_checkboxes()
                #         time.sleep(0.5)
                #         self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:5")
                # else:
                #     checked_162 = self.driver.execute_script(
                #         """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:4").checked""")
                #     if not checked_162:
                #         self.desmarcar_checkboxes()
                #         time.sleep(0.5)
                #         self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:4")

                # self.selenium_helper.atribuir_valor_campo_driver("#filter-form > table > tbody > tr:nth-child(8) > "
                #                                                  "td.value > input", proposta[1])

                # self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                #                                             "a.button.exibirCarregamento")

                # if not self.tratar_erros():
                #     self.atualiza_contrato_web_admin_erro(proposta[2])
                #     self.log.api_registrar_log_robo(
                #         log=self.selenium_helper.verificar_texto_campo_driver("#global-msg > li"),
                #         status=2
                #     )
                #     continue

                # index = self.match_ade(proposta[0])

                # self.selenium_helper.clicar_elemento_driver(f"#j_idt207\\:{str(index - 1)}\\:modalDialogButton")
                # self.selenium_helper.clicar_elemento_driver(f"#j_idt208\\:{str(index - 1)}\\:modalDialogButton")

                # time.sleep(1)
                # self.selenium_helper.atribuir_valor_campo_driver(
                #     "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")

                # self.selenium_helper.clicar_elemento_driver(
                #     "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")

                # self.atualiza_contrato_web_admin(proposta[2])
                # print(f"Proposta {proposta[2]} liberada!")
                # self.log.api_registrar_log_robo(
                #     log=f"Proposta {proposta[2]} liberada!",
                #     status=2
                # )
            except ErrorADE:
                print('Nao ha nada a liberar...')
                continue
                # self.atualiza_contrato_web_admin_erro(proposta[2])
                # print(f"Não foi possível encontrar a ADE {proposta[0]}, a proposta já foi liberada!")
                # self.log.api_registrar_log_robo(
                #     log=f"Não foi possível encontrar a ADE {proposta[0]},"
                #         f" a proposta já foi liberada!",
                #     status=2
                # )
            except Exception as e:
                dbg.exception(e)
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {str(e)}",
                    status=0
                )

    def liberar_proposta_159(self, proposta):
        print('Liberando a 159...')

        try:
            checked_159 = self.driver.execute_script(
                        """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:2").checked""")

            if not checked_159:
                self.desmarcar_checkboxes()
                time.sleep(0.5)
                self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:2")

            self.selenium_helper.atribuir_valor_campo_driver("#filter-form > table > tbody > tr:nth-child(8) > "
                                                                 "td.value > input", proposta[1])

            self.selenium_helper.clicar_elemento_driver("#filter-form > div.formulario-buttons > "
                                                            "a.button.exibirCarregamento")
            if not self.tratar_erros():
                self.atualiza_contrato_web_admin_erro(proposta[2])
                self.log.api_registrar_log_robo(
                        log=self.selenium_helper.verificar_texto_campo_driver("#global-msg > li"),
                        status=2
                    )
                return

            index = self.match_ade(proposta[0])

            self.selenium_helper.clicar_elemento_driver(f"#j_idt207\\:{str(index - 1)}\\:modalDialogButton")
            self.selenium_helper.clicar_elemento_driver(f"#j_idt208\\:{str(index - 1)}\\:modalDialogButton")

            time.sleep(1)
            self.selenium_helper.atribuir_valor_campo_driver(
                    "#modalDialog > div.ui-dialog-content.ui-widget-content > textarea", "Proposta liberada.")

            self.selenium_helper.clicar_elemento_driver(
                    "#modalDialog > div.ui-dialog-content.ui-widget-content > div > a:nth-child(1)")

            self.atualiza_contrato_web_admin(proposta[2])

            print(f"Proposta {proposta[2]} liberada 159!")
            
            self.log.api_registrar_log_robo(
                    log=f"Proposta {proposta[2]} liberada 159!",
                    status=2
                )
        except ErrorADE:
            print('Nao ha nada a liberar...')
            self.atualiza_contrato_web_admin_erro(proposta[2])
            print(f"Não foi possível encontrar a ADE {proposta[0]}, a proposta já foi liberada!")
            self.log.api_registrar_log_robo(
                    log=f"Não foi possível encontrar a ADE {proposta[0]},"
                        f" a proposta já foi liberada!",
                    status=2
                )

    def desmarcar_checkboxes(self):
        #pdb.set_trace()
        # checked_105 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:2").checked""")
        # if checked_105:
        #     self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:2")

        checked_159 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:2").checked""")
        if checked_159:
            self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:2")

        # checked_162 = self.driver.execute_script(
        #     """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:4").checked""")
        # if checked_162:
        #     self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:4")

        # checked_180 = self.driver.execute_script(
        #     """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:5").checked""")
        # if checked_180:
        #     self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:5")

        checked_272 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:8").checked""")
        if checked_272:
            self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:8")

        checked_274 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:9").checked""")
        if checked_274:
            self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:9")

        checked_280 = self.driver.execute_script("""return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:10").checked""")
        if checked_280:
            self.selenium_helper.clicar_elemento_driver("#filter-form\\:tipoInconsistencias\\:10")

    def match_ade(self, ade):
        
        try:
            qtd_rows = self.driver.execute_script(
                """return document.querySelector("#j_idt206 > table > tbody").rows.length""")
        except:
            qtd_rows = self.driver.execute_script(
                """return document.querySelector("#j_idt207 > table > tbody").rows.length""")

        for index in range(1, qtd_rows + 1):
            try:
                if self.selenium_helper.verificar_texto_campo_driver(
                        f"#j_idt206 > table > tbody > tr:nth-child({index}) > td:nth-child(1)") == ade:
                    return index
            except NoSuchElementException:
                if self.selenium_helper.verificar_texto_campo_driver(
                        f"#j_idt207 > table > tbody > tr:nth-child({index}) > td:nth-child(1)") == ade:
                    return index

        raise ErrorADE(message="Não foi possível encontrar a ADE.")

    def gerar_contratos(self):
        print("Apagando arquivos em:", self.contratos_pdf_path)
        apagar_arquivos(self.contratos_pdf_path)
        contratos = self.buscar_contratos_gerar()

        for contrato in contratos:

            self.log.api_iniciar_log_robo(
                idRobo=self.id_fila_gerar_contrato,
                idContrato=contrato['codigo_con']
            )
            try:
                print("Trabalhando no contrato %s" % (contrato['ade']))

                self.baixar_pdf_contrato(contrato['ade'])
                self.unificar_pdf(contrato)
                self.envia_pdf_contrato(contrato)

                self.log.api_registrar_log_robo(
                    log=f"Contrato enviado com sucesso.",
                    status=2
                )
            except FileNotFoundError as e:
                print(e)
                print("PDF nao pode ser baixado.")
                self.log.api_registrar_log_robo(
                    log=f"ERRO: PDF nao pode ser baixado.",
                    status=0
                )
            except Exception as e:
                dbg.exception(e)
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )

    def deletar_pdf_contrato_default(self):
        while os.path.exists(self.default_file_name):
            print('Apagando arquivo...')
            os.remove(self.default_file_name)
            time.sleep(2)

    def baixar_pdf_contrato(self, ade):
        self.driver.get(f'https://www.ibconsigweb.com.br/geraTermoAdesao.login?method=report&numeroAde={ade}')

        self.act.manusear_alerta()

        cnt: int = 0
        while not os.path.exists(self.default_file_name) and cnt < 16:
            print('Esperando o download do arquivo...')
            time.sleep(2)
            cnt += 1

        print('Arquivo baixado...')

        new_file_name = os.path.join(self.contratos_pdf_path, f"{ade}.pdf")
        os.rename(self.default_file_name, new_file_name)

        while not os.path.exists(new_file_name):
            print('Esperando renomear o arquivo...')
            time.sleep(2)

    def unificar_pdf(self, contrato):
        contrato_unificado = pikepdf.Pdf.new()

        contrato_path = os.path.join(
            self.contratos_pdf_path, "%s.pdf" % (contrato['ade']))
        condicoes_path = os.path.join(
            self.pdfs_orientacoes_path, "condicoes.pdf"
        )
        condicoes_pdf = pikepdf.Pdf.open(condicoes_path)
        contrato_pdf = pikepdf.Pdf.open(contrato_path)

        orientacoes_path = os.path.join(
            self.pdfs_orientacoes_path, "orientacao_assinatura_digital.pdf"
        )

        orientacoes_pdf = pikepdf.Pdf.open(orientacoes_path)

        contrato_unificado.pages.extend(orientacoes_pdf.pages)
        contrato_unificado.pages.extend(contrato_pdf.pages)
        contrato_unificado.pages.extend(condicoes_pdf.pages)
        contrato_unificado.save(contrato_path)

    def envia_pdf_contrato(self, contrato):
        contrato_path = os.path.join(
            self.contratos_pdf_path, "%s.pdf" % (contrato['ade']))
        contrato_base_64 = convert_file_base_64(contrato_path)

        dados_pdf = {
            'key': 'f689f1e12a0399fba803cb2365fc362f',
            'ade': contrato['ade'],
            'codigoCliente': contrato['codigo_cli'],
            'codigoContrato': contrato['codigo_con'],
            'base64': contrato_base_64,
            'banco': 'itau'
        }
        request_gerar_contrato = requests.post("https://uconecte.me/api/v1/contratos/gerar", data=dados_pdf)
        print(request_gerar_contrato.content)
        if request_gerar_contrato.status_code != 200:
            print(request_gerar_contrato.json())
            input('Não foi possível gerar o Contrato')

        os.remove(contrato_path)

    def busca_propostas_liberar(self):
        request_propostas_liberar = requests.get("https://emprestimofacil.co/web_admin/api/v1/contratos/a-liberar"
                                                 "/banco-itau-consignado/?key=f689f1e12a0399fba803cb2365fc362f")

        if request_propostas_liberar.status_code != 200:
            input("IBConsig Error - Não foi possível buscar as propostas para liberação!")

        propostas = request_propostas_liberar.json()

        if len(propostas) == 1:
            print("Nenhuma proposta 162 e 180 para liberação!")
            self.propostas_vazia = True
            return []

        return propostas

    def buscar_contratos_gerar(self):
        request_contratos_a_gerar = requests.get('https://uconecte.me/api/v1/contratos/status/gerar?key'
                                                 '=f689f1e12a0399fba803cb2365fc362f&consulta=gerar&banco=itau')
        print(request_contratos_a_gerar.content)
        if request_contratos_a_gerar.status_code != 200:
            input('IBConsig Error - Não foi possível buscar os contratos para geração!')

        contratos = request_contratos_a_gerar.json()['contratos']
        print(contratos)
        if len(contratos) == 0:
            print('Nenhum contrato para geração, trocando de fila...')
            self.contratos_vazio = True
            return []

        return contratos

    def aguardar(self):
        print("Filas vazias! Aguardando novas propostas e contratos...")
        time.sleep(180)
        self.driver.refresh()

        self.contratos_vazio = False
        self.propostas_vazia = False

    @staticmethod
    def atualiza_contrato_web_admin_erro(codigo_contrato):
        dados = {
            "liberarProposta": 0,
            "codigoCon": codigo_contrato,
        }

        request_dados_contrato = requests.post("http://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-itau"
                                               "-consignado/liberacao-proposta/?key=f689f1e12a0399fba803cb2365fc362f",
                                               data=dados)

        if request_dados_contrato.status_code != 200:
            print(f"Status code; {request_dados_contrato.status_code}")
            input("Problema ao atualizar o status da proposta no webadmin, favor verificar o que ocorreu!")

    @staticmethod
    def atualiza_contrato_web_admin(codigo_contrato):
        dados = {
            "liberarProposta": 2,
            "codigoCon": codigo_contrato,
        }

        request_dados_contrato = requests.post("http://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-itau"
                                               "-consignado/liberacao-proposta/?key=f689f1e12a0399fba803cb2365fc362f",
                                               data=dados)

        if request_dados_contrato.status_code != 200:
            print(f"Status code; {request_dados_contrato.status_code}")
            input("Problema ao atualizar o status da proposta no webadmin, favor verificar o que ocorreu!")

    def tratar_erros(self):
        if self.selenium_helper.buscar_quantidade_elemento('#global-msg > li') > 0:
            mensagem_erro = self.selenium_helper.verificar_texto_campo_driver("#global-msg > li")
        else:
            return True

        print(f"Mensagem de erro: {mensagem_erro}")

        if mensagem_erro == "":
            return True

        erros_regex = [
            {
                'erro': r"Nenhum registro encontrado.",
                'NoRegister': True
            }
        ]

        for erro_regex in erros_regex:
            regex = re.compile(erro_regex['erro'])
            erro_encontrado = regex.search(mensagem_erro)

            if not erro_encontrado:
                continue

            if 'NoRegister' in erro_regex:
                return False

        input("Mensagem não encontrada...")

    def verifica_horario_comercial(self):
        data_hora = datetime.now()
        if data_hora.hour > 20:
            print('Fora do horário comercial... Inciando o processo para próxima manhã (7:00)...')
            self.driver.close()
            countdown(36000, 3600, 'Aguardando...')
            self.__init__()
            self.main()


class ErrorADE(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


if __name__ == '__main__':
    GerarContratoIbConsig.iniciar_horario_comercial()

