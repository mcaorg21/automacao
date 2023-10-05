"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: analise_docs_auto
| data: 2019-11-14
| autor: Gustavo Belleza
| funcionamento:
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from sites.baseRobos.core.data_helpers import download,criar_arquivo
from sites.baseRobos.gui_auto import AutoGUI
from selenium.common.exceptions import TimeoutException
from pathlib import Path
from typing import List
from sites.baseRobos.core.DebugTools import DebugTools
from PATHS import project_path
import time

dbg = DebugTools(debugging=False)


class AnaliseDocsAuto(AutoGUI):

    def __init__(self, driver):
        super().__init__(driver)
        self.parar_se_exception = True
        self.path = str(Path(project_path() + "/ibConsig/anexos/"))
        self.path_form_completa = str(Path(self.path + '/formalizacao_completa.pdf'))
        self.path_docs = str(Path(self.path + '/docs.pdf'))

    def extrair_dados_tabelas(self):
        import re
        print("Buscando codigo de acesso no 'IbConsigWeb'")

        loc = '//*[@id="registro"]/tbody/tr/td[5]'
        codigo_con: str = self.act.obter_texto(loc, self.by.XPATH)

        r_codigo_con = r"{}".format(codigo_con)

        print("Utilizando codigo do contrato:", r_codigo_con)

        loc_link_contrato = '//*[@id="registro"]/tbody/tr/td[1]/table/tbody/tr/td/a'
        self.act.clicar_elemento(loc_link_contrato, By.XPATH)

        loc_tabela_correncias = '/html/body/form/table[6]/tbody/tr'
        linhas_ocorr: List[WebElement] = self.act.retornar_elementos(
            loc_tabela_correncias, self.metodo.XPATH)

        loc_tabela_historico = '/html/body/form/table[10]/tbody/tr'
        linhas_hist: List[WebElement] = self.act.retornar_elementos(
            loc_tabela_historico, self.metodo.XPATH)

        linhas_hist_filt: List[WebElement] = []
        try:
            linhas_hist_filt: List[WebElement] = [
                lin for lin in linhas_hist if re.search(r_codigo_con, lin.text)]
        except Exception as e:
            dbg.warning(e)

        print(linhas_hist_filt, linhas_ocorr)

        return linhas_ocorr, linhas_hist_filt

    def acessar_portal(self, codigo_acesso):

        print("Entrando no portal...\n")

        loc_codigo_acesso_input = 'input#codigoAcesso'
        self.act.enviar_texto(loc_codigo_acesso_input, codigo_acesso)

        loc_botao_acessar = 'button#btnAcessar'
        self.act.clicar_elemento(loc_botao_acessar)

    def anexar_documentos(self, documentos):
        self.act.time_out = 8
        print("Anexando documentos\n")
        dbg.debugger()
        try:
            download(documentos, self.path_form_completa)
        except:
            print('Salvando arquivo...')

        self.act.anexar_documento(self.path_form_completa, 'input#flContratoCCB')
        self.act.anexar_documento(self.path_docs, f'input#flDocumentoIdentificacao')
        self.act.anexar_documento(self.path_docs, f'input#arquivoSelfie')

        loc_botao_enviar = 'button#btnEnviar'
        self.act.clicar_elemento(loc_botao_enviar)

        loc_protocolo = 'div.modal-body'  # ou xpath '//*[@id="Modal1573652325671"]/div[2]'
        mensagem_protocolo = self.act.obter_texto(loc_protocolo)

        numero_protocolo = mensagem_protocolo.split(" Protocolo ")[1]
        numero_protocolo = numero_protocolo.replace(".", "")

        print(f"Arquivos anexados com sucesso. Proocolo nº: {numero_protocolo}")
        return numero_protocolo

    def anexar_documentos_portabilidade(self, documento, path_completo, id_campo, tipo='css'):
        self.act.time_out = 8
        print("Downloading e anexando documento\n")
        try:
            criar_arquivo(documento, path_completo)
            print('criou arquivo com sucesso')
        except:
            print('Salvando arquivo...')
        if tipo == 'css':
            self.act.anexar_documento(path_completo, id_campo)
        elif tipo == 'xpath':
            self.act.anexar_documento(path_completo, id_campo, metodo_by=By.XPATH)
    # def anexar_documentos(self, documentos):
    #     self.act.time_out = 8
    #     print("Anexando documentos\n")
    #     dbg.debugger()
    #     try:
    #         download(documentos, self.path_form_completa)
    #     except:
    #         print('Salvando arquivo...')

    #     self.act.anexar_documento(self.path_form_completa, 'input#flContratoCCB')
    #     self.act.anexar_documento(self.path_docs, f'input#flDocumentoIdentificacao')

    #     loc_botao_enviar = 'button#btnEnviar'
    #     self.act.clicar_elemento(loc_botao_enviar)

    #     loc_protocolo = 'div.modal-body'  # ou xpath '//*[@id="Modal1573652325671"]/div[2]'
    #     mensagem_protocolo = self.act.obter_texto(loc_protocolo)

    #     numero_protocolo = mensagem_protocolo.split(" Protocolo ")[1]
    #     numero_protocolo = numero_protocolo.replace(".", "")

    #     print(f"Arquivos anexados com sucesso. Proocolo nº: {numero_protocolo}")
    #     return numero_protocolo

    def verificar_erros_acesso_portal(self):
        time.sleep(2)
        try:
            loc_msg_erro = '.danger'
            erro = self.act.obter_texto(loc_msg_erro)
            erro = erro.strip().replace("\n", "")
            print("ERRO:", erro)
            return erro
        except TimeoutException:
            return ''

    def esperar_mensagem(self,mensagem, selector, time):
        while mensagem not in self.act.obter_texto(selector):
            print('Aguardando envio...{time} segundos')
            time.sleep(time)