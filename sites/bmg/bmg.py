import sys
sys.path.append('../')

import re,pdb, shutil
import requests

from time import sleep
from datetime import datetime
from selenium import webdriver
from sites.core.helpers import countdown
from sites.core.uconecte import Uconecte
from sites.core.captcha import TwoCaptcha
from selenium.webdriver.chrome.options import Options
from sites.core.selenium_actions import SeleniumActions
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.helpers import definir_nome_robo, identificar_erro_robo
from sites.baseRobos.data_handler import DataHandler
from PATHS import chrome_user, driver_path
from sites.bmg.BMGDados import BMGDados
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver.common.by import By
from dados.database.queries.query_dados_robos import query_login_pass_robo

HORARIO_COMERCIAL = 7, 20


class BMG:
    def __init__(self):
        try:
            #pdb.set_trace()
            pasta = chrome_user('bmg').split('=')[1]
            shutil.rmtree(pasta)
        except:
            pass
            
        options = Options()
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(chrome_user('bmg'))
        options.add_argument('headless')
        self.driver = webdriver.Chrome(
            #executable_path=driver_path(),
            options=options
        )

        self.uconecte = Uconecte()
        self.act = SeleniumActions(self.driver, time_out=2)
        self.captcha = TwoCaptcha(self.driver, manual=False)
        self.user = "carolina.1873"
        self.password = "t#909164"
        self.ultima_atualizacao = datetime.now()
        self.id_robo = 18
        self.timer = 600
        self.log = DataHandler()
        self.dados = BMGDados()

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls):
        run = BMG()
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    def main(self):
        self.driver.get("https://www.bmgconsig.com.br/")

        print("Realizando login...")
        self.login()
        print("Login realizado com sucesso!")
        self.menu_consistencias()
        self.uconecte.atualizar_status_robo(self.id_robo)

        while True:
            try:
                if self.verificar_login():
                    self.login()
                definir_nome_robo('BMG - Liberação de Consistências')
                self.menu_consistencias()
                #self.consistencias_sem_ade()
                self.consistencias_com_ade()
                print("Aguardando 5 minutos antes de liberar novamente...")
                sleep(150)
                self.driver.refresh()
                self.verificar_tempo_execucao()
                sleep(150)
                try:
                    self.tratar_erros()
                except NoRegister:
                    pass
            except Exception as e:
                identificar_erro_robo()
                raise Exception(str(e))

    def verificar_login(self):
        try:
            loc_user = "#usuario"
            self.act.quantidade_elemento(loc_user)
            return True
        except TimeoutException:
            return False

    def desmarcar_checkboxes(self):
        
        checkbox_162 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:11").checked""")
        if checkbox_162:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:11")

        checkbox_180 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:13").checked""")
        if checkbox_180:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:13")

        checkbox_181 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:14").checked""")
        if checkbox_181:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:14")

        checkbox_184 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:15").checked""")
        if checkbox_184:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:15")

        checkbox_322 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:56").checked""")
        if checkbox_322:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:56")

        checkbox_340 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:70").checked""")
        if checkbox_340:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:71")

        checkbox_341 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:71").checked""")
        if checkbox_341:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:72")

        checkbox_342 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:72").checked""")
        if checkbox_342:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:73")

    def consistencias_com_ade(self):
        print("Liberando consistencias com ADE...")
        consistencias = self.dados.buscar_propostas_liberar()

        for consistencia in consistencias[1:]:
            self.consistencias_sem_ade()
            self.menu_consistencias()
            try:
                self.log.api_iniciar_log_robo(
                    idRobo=self.id_robo,
                    idContrato=consistencia[2]
                )
                print(f"Liberando proposta {consistencia[2]}")

                consistencias = ["162"]
                self.marcar_consistencias_liberar(consistencias)

                # checked_162 = self.driver.execute_script(
                #     """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:11").checked""")

                # if not checked_162:
                #     self.desmarcar_checkboxes()
                #     sleep(0.5)
                #     self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:11")

                self.act.enviar_texto("#filter-form > table > tbody > tr:nth-child(2) > td.value > input", consistencia[0])
                #self.act.clicar_elemento("#filter-form > div.formulario-buttons > a.button.exibirCarregamento")

                loc_captcha_img = '#filter-form\\:idCaptcha\\:j_idt201'
                loc_campo_catpcha = '#filter-form\\:idCaptcha\\:txt-value'
                id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)

                self.act.trocar_frame_referencia(loc_campo_catpcha)
                self.act.enviar_texto(loc_campo_catpcha, res_captcha)
                sleep(0.5)

                self.act.clicar_elemento('/html/body/div[2]/form[1]/div[2]/div/table/tbody/tr[2]/td/a[1]', By.XPATH)

                try:
                    self.tratar_erros()
                except NoRegister:
                    self.atualiza_contrato_web_admin_erro(consistencia[2])
                    self.log.api_registrar_log_robo(
                        log=f"Proposta {consistencia[2]} não encontrada!",
                        status=2
                    )
                    print(f"Proposta {consistencia[2]} não encontrada!")
                    continue

                try:
                    self.act.clicar_elemento('#j_idt246\\:0\\:j_idt292') 
                    #self.act.clicar_elemento("#j_idt222\\:0\\:j_idt268")
                except:
                    self.act.clicar_elemento('//*[@id="j_idt245:0:j_idt291"]', By.XPATH) 
                    #self.act.clicar_elemento("#j_idt227\\:0\\:modalDialogButton")
                # finally:
                #     self.act.clicar_elemento("#j_idt228\\:0\\:modalDialogButton")

                sleep(1)
                self.act.enviar_texto("#justificativa", "Proposta liberada.")

                self.act.clicar_elemento(
                    "#modalDialog > div.ui-dialog-footer.ui-widget-content > span > a:nth-child(1)")

                self.atualiza_contrato_web_admin(consistencia[2])
                self.act.press_backspace(
                    "#filter-form > table > tbody > tr:nth-child(2) > td.value > input")

                print(f"Proposta {consistencia[2]} liberada!")
                self.log.api_registrar_log_robo(
                    log=f"Proposta {consistencia[2]} liberada!",
                    status=2
                )
            except Exception as e:
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {str(e)}",
                    status=0
                )

    def consistencias_sem_ade(self):
        print("Liberando consistências que não precisam de ADE...")

        self.log.api_iniciar_log_robo(
            idRobo=self.id_robo,
            idContrato="000000"
        )

        consistencias = ["180","181","184","322","340","341","342"]
        self.marcar_consistencias_liberar(consistencias)
        #self.desmarcar_checkboxes()
        #self.marcar_checkboxes_sem_ade()

        loc_captcha_img = '#filter-form\\:idCaptcha\\:j_idt201'
        loc_campo_catpcha = '#filter-form\\:idCaptcha\\:txt-value'
        id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)

        self.act.trocar_frame_referencia(loc_campo_catpcha)
        self.act.enviar_texto(loc_campo_catpcha, res_captcha)
        sleep(0.5)

        self.act.clicar_elemento('/html/body/div[2]/form[1]/div[2]/div/table/tbody/tr[2]/td/a[1]', By.XPATH)

        try:
            self.tratar_erros()
        except NoRegister:
            print("Nenhuma proposta sem ADE para liberação!")
            return

        while True:
            try:
                try:
                    self.act.clicar_elemento("#j_idt246\\:0\\:modalDialogButton")
                except:
                    try:
                        self.act.clicar_elemento("#j_idt228\\:0\\:modalDialogButton")
                    except TimeoutException:
                        self.act.clicar_elemento("#j_idt227\\:0\\:modalDialogButton")
                sleep(1)
                self.act.enviar_texto("#justificativa", "Proposta liberada.")
                self.act.clicar_elemento("#modalDialog > div.ui-dialog-footer.ui-widget-content > span > a:nth-child(1)")
            except TimeoutException:
                break

        print("Consistências sem ADE liberadas!")
        self.log.api_registrar_log_robo(
            log="Consistências sem ADE liberadas!",
            status=2
        )

    def marcar_checkboxes_sem_ade(self):
        checkbox_180 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:13").checked""")
        if not checkbox_180:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:13")

        checkbox_181 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:14").checked""")
        if not checkbox_181:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:14")

        checkbox_184 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:15").checked""")
        if not checkbox_184:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:15")

        checkbox_322 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:56").checked""")
        if not checkbox_322:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:56")

        checkbox_340 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:70").checked""")
        if not checkbox_340:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:71")

        checkbox_341 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:71").checked""")
        if not checkbox_341:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:72")

        checkbox_342 = self.driver.execute_script(
            """return document.querySelector("#filter-form\\\\:tipoInconsistencias\\\\:72").checked""")
        if not checkbox_342:
            self.act.clicar_elemento("#filter-form\\:tipoInconsistencias\\:73")

    def marcar_consistencias_liberar(self,consistencias):

        for consistencia in consistencias:
            try:
                print(f"Liberando consistencia - {consistencia}")
                self.act.clicar_elemento("#filter-form\\:consistencias > a > label")
                self.act.enviar_texto("#filter-form\\:consistencias_panel > div.ui-widget-header.ui-corner-all.ui-selectcheckboxmenu-header.ui-helper-clearfix > div.ui-selectcheckboxmenu-filter-container > input",f"{consistencia}")
                self.act.clicar_elemento('//*[@id="filter-form:consistencias_panel"]/div[1]/div[1]/div',By.XPATH)
                self.act.clicar_elemento("#filter-form\\:consistencias > a > label")      
            except:
                pass

    def menu_consistencias(self):
        self.driver.get("https://www.bmgconsig.com.br/liberacaoinconsistencias/resultadoLiberacaoInconsistencias.jsf")

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def login(self):
        try:
            loc_user = "#usuario"
            self.act.trocar_frame_referencia(loc_user)
            self.act.enviar_texto(loc_user, self.user)
            sleep(0.5)
        except TimeoutException:
            print("Usuário já logado!")
            return

        loc_password = "#j_password"
        dados_login = query_login_pass_robo(318, self.user)

        self.act.enviar_texto(loc_password, dados_login['senha'])
        sleep(0.5)

        self.act.trocar_frame_seletor("#f-login > div.form-group.text-center > iframe")

        loc_captcha_img = "body > img"
        loc_campo_catpcha = "#captcha"
        id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)

        self.act.trocar_frame_referencia(loc_campo_catpcha)
        self.act.enviar_texto(loc_campo_catpcha, res_captcha)
        sleep(0.5)

        self.act.clicar_elemento("#bt-login")

        self.tratar_erros()

    def complete_captcha(self):
        self.act.trocar_frame_seletor("#f-login > div.form-group.text-center > iframe")

        loc_captcha_img = "body > img"
        loc_campo_catpcha = "#captcha"
        id_captcha, res_captcha = self.captcha.resolver_captcha(loc_captcha_img)

        self.act.trocar_frame_referencia(loc_campo_catpcha)
        self.act.enviar_texto(loc_campo_catpcha, res_captcha)

    def tratar_erros(self):
        alert = self.act.obter_texto_alerta()
        try:
            mensagem = self.act.obter_texto("#msg-error")
        except TimeoutException:
            try:
                mensagem = self.act.obter_texto("#global-msg > li")
            except TimeoutException:
                return

        alerts_regex = [
            {
                'erro': r'Informe o usuário',
                'CaptchaError': True
            }
        ]

        erro_regex = [
            {
                'erro': r"A palavra de verificação está inválida.",
                'CaptchaError': True
            }, {
                'erro': r"Nenhum registro encontrado.",
                "SemINFO": True
            }, {
                'erro': r"A imagem de autenticação expirou. Por favor, tente novamente.",
                "CaptchaError": True
            }, {
                'erro': r"Foi detectada uma possível tentativa de acesso simultâneo e, por questão de segurança, "
                        r"sua sessão foi encerrada. Nova tentativa de acesso ao sistema será permitida em {0}.",
                'aguardar': True
            }
        ]

        try:
            for alert_regex in alerts_regex:
                regex = re.compile(alert_regex['erro'])
                alert_encontrado = regex.search(alert)

                if not alert_encontrado:
                    continue

                if 'CaptchaError' in alert_regex:
                    print("Captcha Inválido!")
                    self.login()
        except TypeError:
            pass

        for mensagem_regex in erro_regex:
            regex = re.compile(mensagem_regex['erro'])
            mensagem_encontrada = regex.search(mensagem)

            if not mensagem_encontrada:
                continue

            if 'CaptchaError' in mensagem_regex:
                print("Captcha Inválido!")
                self.login()
            elif "SemINFO" in mensagem_regex:
                raise NoRegister(message="Nenhum registro encontrado para essas consistêcias.")
            elif "aguardar" in mensagem_regex:
                print("Tentativa de login simultâneo, aguardando 13 minutos antes de logar novamente...")
                sleep(780)
                self.main()
            else:
                return

    @staticmethod
    def atualiza_contrato_web_admin_erro(codigo_contrato):
        dados = {
            "liberarProposta": 0,
            "codigoCon": codigo_contrato,
        }

        request_dados_contrato = requests.post("http://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-bmg"
                                               "/liberacao-proposta/?key=f689f1e12a0399fba803cb2365fc362f",
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

        request_dados_contrato = requests.post("http://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-bmg"
                                               "/liberacao-proposta/?key=f689f1e12a0399fba803cb2365fc362f",
                                               data=dados)

        if request_dados_contrato.status_code != 200:
            print(f"Status code; {request_dados_contrato.status_code}")
            input("Problema ao atualizar o status da proposta no webadmin, favor verificar o que ocorreu!")

    def verifica_horario_comercial(self):
        data_hora = datetime.now()
        if data_hora.hour > 20:
            print('Fora do horário comercial... Inciando o processo para próxima manhã (7:00)...')
            self.driver.close()
            countdown(36000, 3600, 'Aguardando...')
            self.__init__()
            self.main()

    def verificar_tempo_execucao(self):
        time_between_updates = (datetime.now() - self.ultima_atualizacao).seconds
        print(f"\nTempo entre atualizações: {time_between_updates}")
        print(f"Timer: {self.timer} segundos")

        if time_between_updates < 60:
            wait_time = self.timer - time_between_updates
            print(f"Esperando {wait_time} segundos antes de recomeçar a fila!")

            if wait_time > 0:
                sleep(wait_time)

        self.ultima_atualizacao = datetime.now()
        self.uconecte.atualizar_status_robo(self.id_robo)


class NoRegister(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


if __name__ == "__main__":
    BMG.iniciar_horario_comercial()
