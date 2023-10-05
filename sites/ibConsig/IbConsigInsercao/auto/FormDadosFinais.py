from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from time import sleep
from selenium.common.exceptions import (
    TimeoutException, JavascriptException,
    NoSuchWindowException
)
from pathlib import Path
from sites.baseRobos.core.selenium_actions import SeleniumActions
from PATHS import project_path
from selenium.webdriver.common.by import By
from sites.baseRobos.core.helpers import apagar_arquivo
import pdb

class DadosFinais(AutoGUI):
    def __init__(self, driver: Chrome, dados: dict):
        super().__init__(driver)
        self.__nome_vendedor = dados.get('nomeVendedor', None)
        self.__forma_envio = dados.get('formaEnvio', None)
        self.__entidade = dados.get('entidade', None)
        self.idPessoa = dados.get('idPessoa', None)
        self.erro_aplicacao: str = ""
        self.erro_aplicacao: str = ""
        self.ade: str = ""
        self.act.time_out = 0.2
        self.__estadual = dados.get("estadual")
        self.grau_instrucao_sistema: str  = dados.get('grauInstrucaoWa', None)
        self.grau_instrucao_cliente: str = dados.get('grauInstrucao', None)
        self.tabela_digital_sistema: str = dados.get('tabelaDigital', None)
        self.termo_in100_path = str(Path(project_path()+'/ibConsig/anexos/termo_in100/termo_in100_'+ self.idPessoa +'.jpg'))
        self.__prazo_contrato = dados.get('prazoContrato', None)

    @property
    def necessario_anexar_contracheque(self):
        return '1581' not in self.__entidade

    @property
    def estadual(self):
        return self.__estadual

    @property
    def grau_instrucao_wa(self):
        return self.grau_instrucao_sistema

    @property
    def grau_instrucao_uconecte(self):
        return self.grau_instrucao_cliente

    @property
    def tabela_digital(self):
        return self.tabela_digital_sistema

    def selecionar_if_nao(self):
        loc = '//*[@id="fluxoIn100Table"]/tbody/tr[2]/td[2]/input[1]'
        print("Selecionando IFN = Não")
        self.act.clicar_elemento(loc, self.by.XPATH)

    def selecionar_if_sim(self):
        loc = '//*[@id="fluxoIn100Table"]/tbody/tr[2]/td[2]/input[2]'
        print("Selecionando IFN = Sim")
        self.act.clicar_elemento(loc, self.by.XPATH)

    def selecionar_rogado_nao(self):
        print("Selecionando Rogado = Não")
        loc = 'input[name=rogado]'
        if not self.act.check_box_is_checked(loc):
            sleep(1)
            self.sh.clicar_elemento_driver(loc)

    def selecionar_rogado_sim(self):
        print("Selecionando Rogado = Sim")
        loc = '/html/body/form/table[11]/tbody/tr[2]/td[2]/input[2]'
        self.driver.find_element_by_xpath(loc).click()

    def preencher_nome_vendedor(self):
        print("Preenchendo nome do vendedor")
        self.sh.atribuir_valor_campo_jquery(
            '#ade\\\\.agente\\\\.nome', self.__nome_vendedor)

    def preencher_prazo_contrato(self, rec=0):
        print("Preenchendo prazo do contrato...", self.__prazo_contrato)
        loc_prazo = '//*[@id="ade.quantidadePrestacoes"]'
        self.act.enviar_texto_intervalado(
                loc_prazo, self.__prazo_contrato,
                self.by.XPATH, delay=0.02
            )
        sleep(2)
        self.act.press_TAB(loc_prazo, self.by.XPATH)

    def preencher_forma_envio(self):
        print("Preenchendo forma de envio:", self.__forma_envio)
        self.sh.atribuir_valor_campo_jquery(
            '#ade\\\\.codigoFormaEnvioTermo', self.__forma_envio)

    def anexar_contracheque(self):
        print(f"Tentando anexar contracheque...")
        # Selecionar tipo documento = contracheque.
        loc_select_contracheque = '//*[@id="contraCheque.tipoAnexo[0]"]'
        self.act.select_drop_down(loc_select_contracheque, '1', self.by.XPATH)
        sleep(3)

        # Fazer upload do documento.
        loc_upload_contracheque = '//*[@id="contraCheque.file[0]"]'
        anexo_path = str(Path(project_path()+'/ibConsig/anexos/contracheque.pdf'))
        self.act.anexar_documento(
            anexo_path, loc_upload_contracheque, metodo_by=self.by.XPATH)

    def anexar_termo_in100(self):
        print(f"Tentando anexar termo da IN100...")
        # Selecionar tipo documento = in 100.
        loc_select_in100 = '//*[@id="contraCheque.tipoAnexo[0]"]'
        self.act.select_drop_down(loc_select_in100, '18', self.by.XPATH)
        sleep(3)

        # Fazer upload do documento.
        loc_upload_in100 = '//*[@id="contraCheque.file[0]"]'        
        self.act.anexar_documento(self.termo_in100_path, loc_upload_in100, metodo_by=self.by.XPATH)

    def apagar_arquivo_in100(self):
        apagar_arquivo(self.termo_in100_path)

    def anexar_contracheque_servidor_mt(self):
        print(f"Tentando anexar contracheque...MT")
        # Selecionar tipo documento = contracheque.
        loc_select_contracheque = '//*[@id="contraCheque.tipoAnexo[0]"]'
        self.act.select_drop_down(loc_select_contracheque, '10', self.by.XPATH)
        sleep(3)

        # Fazer upload do documento.
        loc_upload_contracheque = '//*[@id="contraCheque.file[0]"]'
        anexo_path = str(Path(project_path()+'/ibConsig/anexos/contracheque.pdf'))
        self.act.anexar_documento(
            anexo_path, loc_upload_contracheque, metodo_by=self.by.XPATH)

    def anexar_contracheque_servidor_sp(self):
        print(f"Tentando anexar contracheque... SP")
        # Selecionar tipo documento = contracheque.
        loc_select_contracheque = '//*[@id="contraCheque.tipoAnexo[0]"]'
        self.act.select_drop_down(loc_select_contracheque, '1', self.by.XPATH)
        sleep(3)

        # Fazer upload do documento.
        loc_upload_contracheque = '//*[@id="contraCheque.file[0]"]'
        anexo_path = str(Path(project_path()+'/ibConsig/anexos/contracheque.pdf'))
        self.act.anexar_documento(
            anexo_path, loc_upload_contracheque, metodo_by=self.by.XPATH)

    def clicar_confirmar(self):
        print("Confirmando inserção...")
        loc_confirmar = "#confirmar"
        self.act.clicar_elemento(loc_confirmar)

    def buscar_ade(self, rec=0):
        print("Buscando ADE REFIN DA PORTABILIDADE" + str(rec))
        self.sh.trocar_frame("rightFrame")
        try:
            self.ade_refin_portabilidade = self.chrome_driver.execute_script(
                "return $('#label_numeroAde').text()")
            if self.ade_refin_portabilidade:
                print("ADE REFIN DA PORTABILIDADE:", self.ade_refin_portabilidade)
                return 1
            raise TimeoutException
        except TimeoutException:
            if rec > 50:
                print("Não foi possível encontrar ADE REFIN PORTABILIDADE")
                return 0
            sleep(1)
            return self.buscar_ade(rec+1)

    def buscar_ade_portabilidade(self, rec=0):
        print("Buscando ADE PORTABILIDADE: " + str(rec))
        self.sh.trocar_frame("rightFrame")
        try:
            self.ade = self.chrome_driver.execute_script(
                "return $('#label_numeroAdeVinculada').text()")
            if self.ade:
                print("ADE:", self.ade)
                return 1
            raise TimeoutException
        except TimeoutException:
            if rec > 50:
                print("Não foi possível encontrar ADE")
                return 0
            sleep(1)
            return self.buscar_ade_portabilidade(rec+1)

    def buscar_ade_final(self, rec=0):
        print("Buscando ADE FINAL: " + str(rec))
        self.sh.trocar_frame("rightFrame")
        try:
            self.ade = self.chrome_driver.execute_script(
                "return $('#label_numeroAde').text()")
            if self.ade :
                print("ADE:", self.ade)
                return 1
            raise TimeoutException
        except TimeoutException:
            if rec > 50:
                print("Não foi possível encontrar ADE REFIN PORTABILIDADE")
                return 0
            sleep(1)
            return self.buscar_ade_final(rec+1)

    def verificar_erro_ib_consig(self):
        self.erro_aplicacao = self.chrome_driver.execute_script(
            "return trim($('.erro').text())")

    @staticmethod
    def executar_script_pop_up(driver: Chrome):
        try:
            driver.execute_script("""ChromePopup = function (url, arg, feature) {
                                var opFeature = feature.split(";");
                                var featuresArray = new Array();
                                for (var i = 0; i < opFeature.length - 1; i++) {
                                    var f = opFeature[i].split(":");
                                    featuresArray[f[0].toString().trim().toLowerCase()] = f[1].toString().trim();
                                }

                                var h = "200px", w = "400px", l = "100px",
                                t = "100px", r = "no", c = "yes", s = "no";
                                if (featuresArray["dialogheight"]) h = featuresArray["dialogheight"];
                                if (featuresArray["dialogwidth"]) w = featuresArray["dialogwidth"];
                                if (featuresArray["dialogleft"]) l = featuresArray["dialogleft"];
                                if (featuresArray["dialogtop"]) t = featuresArray["dialogtop"];
                                if (featuresArray["resizable"]) r = featuresArray["resizable"];
                                if (featuresArray["center"]) c = featuresArray["center"];
                                if (featuresArray["status"]) s = featuresArray["status"];
                                var modelFeature = "height = " + h + ",width = " + w + ",left=" + l + ",top=" + t + ",model=yes,alwaysRaised=yes,directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no" + ",resizable= " + r + ",celter=" + c + ",status=" + s;
                                var model = window.open(url, "", modelFeature);
                                model.dialogArguments = arg;
                                if (window.showModalDialog.refreshParent) {
                                    reloadPage(model);
                                }
                                return model;
                            }

                            window.showModalDialog = ChromePopup;
                        """)
        except JavascriptException:
            print("Modal Javascript não pôde ser aberto.")

    @staticmethod
    def abrir_confirmar_janelas_finais(driver: Chrome, **kwargs):
        abrir_janela: str = kwargs.get('script_abrir_janela', None)
        confirmar: str = kwargs.get('script_confirmar', None)
        wait: float = kwargs.get('wait', 1)
        try:
            if abrir_janela is not None:
                driver.execute_script(abrir_janela)
            sleep(wait)

            driver.switch_to.window(driver.window_handles[1])
            sleep(wait)

            driver.execute_script(confirmar)
            sleep(wait)

            driver.switch_to.window(driver.window_handles[0])
            sleep(wait)

        except JavascriptException:
            print("Pop up anexar arquivos não foi aberto.")
        except NoSuchWindowException:
            print("Nova janela não foi encontrada.")
            driver.switch_to.window(driver.window_handles[0])
        except IndexError:
            print("Nova janela não foi encontrada.")

    @staticmethod
    def janela_confirmar_insercao(driver: Chrome, act: SeleniumActions, wait: float = 1.0):
        try:
            sleep(wait)
            driver.switch_to.window(driver.window_handles[1])

            loc_modal = '/html/body/table/tbody/tr/td[1]/a'
            act.clicar_elemento(loc_modal, By.XPATH)

            driver.switch_to.window(driver.window_handles[0])
            sleep(wait)

        except NoSuchWindowException:
            print("Nova janela não foi encontrada.")
            sleep(wait)
        except IndexError:
            print("Nova janela não foi encontrada.")
        except TimeoutException:
            print("Não foi possível localizar o botão para fechar modal.")
            sleep(wait)

        act.trocar_janela(0, 1)

