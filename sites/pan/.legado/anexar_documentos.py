import requests
import os
from PIL import Image
from time import sleep
from sites.core.selenium_helper import SeleniumHelper
from sites.core.selenium_actions import SeleniumActions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from pathlib import Path


class AnexarDocumentos:

    path_serv = Path().cwd() / "sites"
    path_pc = Path("C:\\Users\\gustavo\\Documents\\automacao-python\\sites\\")

    def __init__(self, driver):
        self.driver = driver
        self.act = SeleniumActions(self.driver, time_out=1)
        self.selenium = SeleniumHelper(self.driver)
        self.api_key = 'f689f1e12a0399fba803cb2365fc362f'
        self.caminho_anexos = str(self.path_serv/'pan'/'anexos/')
        self.deleta_todos_arquivos()

    def main(self):
        print('Trabalhando na fila de anexação de documentos...')
        contratos = self.buscar_contratos()
        self.menu_anexar()

        for contrato in contratos:
            print(f'Trabalhando no contrato {contrato["codigoCon"]}...')
            try:
                self.pesquisa_contrato(contrato['ade'])
            except ErrorValidacao:
                self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                 "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE")
                self.menu_anexar()
                continue
            except ErrorReprovada:
                self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                 "REP - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE")
                self.menu_anexar()
                continue
            except ErrorAprovada:
                print('Arquivos anexados com sucesso!')
                self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'], 'DOCUMENTOS ANEXADOS NO BANCO')
                self.menu_anexar()
                continue

            arquivos = self.buscar_documentos(contrato['ade'])
            path_files = []
            print('Downloading arquivos...')

            for url_arquivo in arquivos['arquivos']:
                nome_arquivo = url_arquivo.split('?')[0].split('/')[-2] + '_' + url_arquivo.split('?')[0].split('/')[-1]
                url_arquivo = r'%s' % url_arquivo

                self.download(url_arquivo, self.caminho_anexos + nome_arquivo)
                path_files.append(self.caminho_anexos + nome_arquivo)

            print('Anexando arquivos...')
            try:
                try:
                    self.upload_doc_identificacao_novo(path_files, self.tipo_documento(path_files))
                except ErrorValidacao:
                    self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                     "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE")
                    self.menu_anexar()
                    continue
                except TimeoutException:
                    icon = self.driver.execute_script(
                        """return document.querySelector("body > platform-root > platform-operator-entry-container > div.iframe.iframe--active > div > div.entry__container > platform-operator-dashboard-container > div > div.dashboard__stepper > platform-ui-steps > div > div.checklist-steps__stepper > ul > li.ui-stepper__step.ui-stepper__step--done > div.ui-stepper__step__timeline > div.ui-stepper__step__timeline__item > img").alt""")

                    if "concluído" in icon:
                        print("Documento de indentificação já enviado! -> 2")
                        try:
                            self.act.clicar_elemento("#Pular_SIG_Opt > button > span")
                        except TimeoutException:
                            pass
                        self.aguardar_modal()
            except WebDriverException:
                campo = self.act.obter_texto("body > app-core-root > div > div > div > div > "
                                             "app-dashboard-container > div > div > div:nth-child(1) > "
                                             "app-identity-document > div > app-list-item > div > "
                                             "div.list-item__content.list-item__content--right > div")
                if 'Enviar' not in campo:
                    print("Documento de identificação já enviado! -> 3")
                else:
                    try:
                        self.upload_doc_identificacao_antigo(path_files, self.tipo_documento(path_files))
                    except ErrorValidacao:
                        self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                         "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE")
                        self.menu_anexar()
                        continue

            except ErrorValidacao:
                self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                 "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE")
                self.menu_anexar()
                continue

            try:
                try:
                    self.upload_contra_cheque_novo(path_files, self.verifica_contra_cheque(path_files))
                except TimeoutException:
                    icon = self.driver.execute_script(
                        """return document.querySelector("body > platform-root > platform-operator-entry-container > div.iframe.iframe--active > div > div.entry__container > platform-operator-dashboard-container > div > div.dashboard__info > platform-test > platform-ui-overview > div > div.content__container > div > div.overview__cards > div:nth-child(2) > platform-ui-card > div > div.card__content.card__content--list > div > div > div > img").alt""")

                    if 'feito' in icon:
                        print("Contra-cheque já anexado!")
            except WebDriverException:
                try:
                    campo = self.act.obter_texto(
                        "body > app-core-root > div > div > div > div > app-dashboard-container "
                        "> div > div.dashboard__list > div:nth-child(3) > "
                        "app-additional-documents > div > app-list-item > div > "
                        "div.list-item__content.list-item__content--right > div")

                    if "Enviar" not in campo:
                        print("Contra-cheque já anexeado!")
                    else:
                        try:
                            self.upload_contra_cheque_antigo(path_files, self.verifica_contra_cheque(path_files))
                        except ErrorValidacao:
                            self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'],
                                                             "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR "
                                                             "MANUALMENTE")
                            self.menu_anexar()
                            continue

                except TimeoutException:
                    pass

            sleep(1)
            try:
                self.act.clicar_elemento("#Continuar_Overview > button > span")
            except TimeoutException:
                pass

            try:
                self.act.clicar_elemento("#Concluir_Overview > button > span")  # Retorna para o menu principal do modal
            except TimeoutException:
                try:
                    self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-dashboard-container > "
                                             "app-footer > div > div > div.footer__content.footer__content--right > "
                                             "pan-button:nth-child(2) > button > span")
                except TimeoutException:
                    pass

                self.alterar_frame()
                for i in range(0, 3):
                    try:
                        self.act.clicar_elemento(f"#mat-dialog-{str(i)} > app-prompt > div > mat-dialog-actions > "
                                                 f"button:nth-child(2)")
                        break
                    except TimeoutException:
                        continue

            while self.driver.current_url.find('NrProposta') != -1:
                sleep(2)

            print('Arquivos anexados com sucesso!')
            self.atualiza_contrato_web_admin(contrato['ade'], contrato['codigoCon'], 'DOCUMENTOS ANEXADOS NO BANCO')

    def pesquisa_contrato(self, ade):
        loc_nr_proposta = "#ctl00_Cph_AprCons_txtPesquisa_CAMPO"
        self.act.enviar_texto(loc_nr_proposta, ade)

        loc_btn_psq = "#btnPesquisar_txt"
        self.act.clicar_elemento(loc_btn_psq)
        self.aguardar_loading()

        loc_situacao = "#ctl00_Cph_AprCons_grdConsulta > tbody > tr.normal > td:nth-child(3) > a"
        situacao = self.act.obter_texto(loc_situacao)

        if 'REP' in situacao:
            print("Proposta reprovada!")
            raise ErrorReprovada(message='Proposta reprovada!')
        elif 'CAN' in situacao:
            raise ErrorValidacao(message="Error CAN - Não é possível anexar.")

        loc_btn_status = "#ctl00_Cph_AprCons_grdConsulta > tbody > tr.normal > td:nth-child(6) > a"
        texto = self.act.obter_texto(loc_btn_status)

        if 'Aprovado' in texto:
            raise ErrorAprovada(message="Proposta já está aprovada.")

        self.act.clicar_elemento(loc_btn_status)
        self.aguardar_modal()

    def menu_anexar(self):
        self.driver.get("https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI"
                        ".AprovacaoConsultaAnd.aspx")

    def buscar_contratos(self):
        request_contratos = requests.get(
            f'https://emprestimofacil.co/web_admin/api/v1/contratos/enviar-documentos-banco/banco-pan/'
            f'?key={self.api_key}')

        if request_contratos.status_code != 200:
            input('Banco Pan Error - Não foi possível buscar os contratos')

        contratos_anexar = request_contratos.json()

        try:
            if contratos_anexar['retorno'] == 0:
                print('Nenhum documento para anexar no momento! Trocando de fila...')
                return []
        except TypeError:
            pass

        return contratos_anexar

    def buscar_documentos(self, ade):
        request_contratos = requests.get(
            f'https://uconecte.me/api/v1/contratos/documentos?ade={ade}&key={self.api_key}')

        if request_contratos.status_code != 200:
            input('Banco Pan Error - Não foi possível buscar os documentos')

        return request_contratos.json()

    def upload_doc_identificacao_antigo(self, path_files, selector):
        self.aguardar_modal()
        self.alterar_frame()

        self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-dashboard-container > div > div "
                                 "> div:nth-child(1) > app-identity-document > div > app-list-item > div > "
                                 "div.list-item__content.list-item__content--right > div")

        if selector == 1:  # Seleciona a opção de enviar o RG
            self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-document-ref-container > div "
                                     "> app-document-container > app-identity-container > div > div > "
                                     "pan-radio-option:nth-child(1) > div > label")

        elif selector == 2:  # Seleciona a opção de enviar a CNH
            self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-document-ref-container > div "
                                     "> app-document-container > app-identity-container > div > div > "
                                     "pan-radio-option:nth-child(2) > div > label")
        elif selector == 3:  # Seleciona a opção de enviar OUTROS
            self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-document-ref-container > div "
                                     "> app-document-container > app-identity-container > div > div > "
                                     "pan-radio-option:nth-child(3) > div > label")

        # Avança para próxima janela do modal
        self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-document-ref-container > "
                                 "app-footer > div > div > div.footer__content.footer__content--right > pan-button")

        self.driver.find_element_by_css_selector("#file-upload-0").send_keys(path_files[0])  # Envia a frente do ID
        sleep(1)

        self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-document-ref-container > "
                                 "app-footer > div > div > div.footer__content.footer__content--right > "
                                 "pan-button:nth-child(2) > button > span")
        self.aguardar_analise_doc(1, True)

        try:
            if selector == 1 or selector == 2:
                # Envia o verso do ID no campo do RG e CNH
                texto = self.act.obter_texto("body > app-core-root > div > div > div > div > "
                                             "app-document-ref-container > div > app-document-container > "
                                             "app-upload-container > div > div > div:nth-child(2) > app-file-upload > "
                                             "div > div > label > app-upload-status > div > "
                                             "div.upload-status__content > p")

                if 'Arraste os documentos' in texto:
                    self.driver.find_element_by_css_selector(f'#file-upload-3').send_keys(path_files[1])

                    sleep(1)
                    self.act.clicar_elemento("body > app-core-root > div > div > div > div > "
                                             "app-document-ref-container > app-footer > div > div > "
                                             "div.footer__content.footer__content--right > pan-button:nth-child(2) > "
                                             "button > span")  # Confirma o envio do ID
                    self.aguardar_analise_doc(2, True)
                else:
                    self.act.clicar_elemento("#Continuar_DOC_Dash")
                    print("Frente enviada no local do verso, não é possível inserir a documentação.")
                    raise ErrorValidacao(message="Frente enviada no lugar do verso.")
            else:
                # Envia o verso do ID no campo OUTROS
                self.driver.find_element_by_css_selector('#file-upload-1').send_keys(path_files[1])

            self.act.clicar_elemento("body > app-core-root > div > div > div > div > app-dashboard-container > "
                                     "app-footer > div > div > div.footer__content.footer__content--right > "
                                     "pan-button:nth-child(2) > button > span")
            self.alterar_frame()
            for i in range(0, 3):
                try:
                    self.act.clicar_elemento(f"#mat-dialog-{str(i)} > app-prompt > div > mat-dialog-actions > "
                                             f"button:nth-child(2)")
                except TimeoutException:
                    continue

        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

    def upload_doc_identificacao_novo(self, path_files, selector):
        self.aguardar_modal()
        self.alterar_frame()
        try:
            self.act.clicar_elemento("#Overview_DOC_IDENTITY")
            self.aguardar_modal()
        except TimeoutException:
            pass

        if selector == 1:  # Seleciona a opção de enviar o RG
            self.act.clicar_elemento("#\\35 cf80c52ef3ab41984f2e47f > label")

        elif selector == 2:  # Seleciona a opção de enviar a CNH
            self.act.clicar_elemento("#\\35 cf80c65ef3ab41984f2e480 > label")
        elif selector == 3:  # Seleciona a opção de enviar OUTROS
            self.act.clicar_elemento("#\\35 cf80c73ef3ab41984f2e482 > label")

        self.act.clicar_elemento("#Continuar_DOC > button > span")  # Avança para próxima janela do modal

        self.driver.find_element_by_css_selector("#file-upload-0").send_keys(path_files[0])  # Envia a frente do ID
        sleep(1)

        self.act.clicar_elemento("#Continuar_Preview_DOC > button > span")
        self.aguardar_analise_doc(1, False)

        try:
            if selector == 1 or selector == 2:
                # Envia o verso do ID no campo do RG e CNH
                try:
                    texto = self.act.obter_texto("body > platform-root > platform-operator-entry-container > "
                                                 "div.iframe.iframe--active > div > div.entry__container > "
                                                 "platform-operator-dashboard-container > div > div.dashboard__info > "
                                                 "platform-doc-container > platform-doc-dash-container > "
                                                 "platform-doc-ui-dash > div > div.content__container > div > div > "
                                                 "div > div:nth-child(2) > platform-ui-file-upload > div > div > div "
                                                 "> platform-ui-file-upload-status > div > "
                                                 "div.file-upload-status__content > p")
                except TimeoutException:
                    texto = self.act.obter_texto("body > platform-root > platform-operator-entry-container > "
                                                 "div.iframe.iframe--active > div > div.entry__container > "
                                                 "platform-operator-dashboard-container > div > div.dashboard__info > "
                                                 "platform-doc-container > platform-doc-dash-container > "
                                                 "platform-doc-ui-dash > div > div.content__container > div > div > "
                                                 "div > div:nth-child(2) > platform-ui-file-upload > div > div > "
                                                 "label > div > platform-ui-file-upload-status > div > "
                                                 "div.file-upload-status__content > p")

                if 'Envie uma foto do documento' in texto:
                    for element in ['3', '5']:
                        try:
                            self.driver.find_element_by_css_selector(f'#file-upload-{element}').send_keys(path_files[1])
                            break
                        except TimeoutException:
                            continue

                    sleep(1)
                    self.act.clicar_elemento("#Continuar_Preview_DOC > button > span")  # Confirma o envio do ID
                    self.aguardar_analise_doc(2, False)
                else:
                    # Envia a frente do ID
                    for element in range(1, 12):
                        try:
                            self.driver.find_element_by_css_selector(f'#file-upload-{element}').send_keys(path_files[1])
                            sleep(2)
                            break
                        except NoSuchElementException:
                            continue
                        except TimeoutException:
                            continue

                    self.act.clicar_elemento("#Continuar_Preview_DOC > button > span")
                    self.aguardar_analise_doc(1, False)
                    self.act.clicar_elemento("#Continuar_DOC_Dash")
            else:
                # Envia o verso do ID no campo OUTROS
                self.driver.find_element_by_css_selector('#file-upload-1').send_keys(path_files[1])

            self.act.clicar_elemento("#Continuar_DOC_Dash > button > span")

        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

        self.aguardar_modal()
        # self.act.clicar_elemento("#Pular_SIG_Opt > button > span")

    def upload_contra_cheque_antigo(self, path_files, selector):
        if selector != -1:  # GARANTE QUE O CONTRA_CHEQUE EXISTE CONTRA_CHEQUE NOS DOC
            self.alterar_frame()
            self.act.clicar_elemento(
                'body > app-core-root > div > div > div > div > app-dashboard-container > div > div '
                '> div:nth-child(3) > app-additional-documents > div > app-list-item > div > '
                'div.list-item__content.list-item__content--left > div')
            sleep(1)
            index = ''

            for i in range(10):
                try:
                    texto = self.act.obter_texto(
                        'body > app-core-root > div > div > div > div > app-document-ref-container > '
                        'div > app-document-container > app-additional-container > div > div > '
                        'app-file-upload > div > div > label > app-upload-status > div > '
                        'div.upload-status__content > div > h3')

                    if 'Contra' in texto:
                        index = str(i)
                        break
                except TimeoutException:
                    continue

            for i in ['0', '1', '2', '3']:
                try:
                    self.driver.find_element_by_css_selector(f"#file-upload-{i}").send_keys(path_files[selector])
                except NoSuchElementException:
                    continue

            texto = self.act.obter_texto("body > app-core-root > div > div > div > div > app-document-ref-container > "
                                         "div > app-document-container > app-additional-container > div > div > "
                                         "app-file-upload.ng-untouched.ng-dirty.ng-valid > div > div > label > "
                                         "app-upload-status > div > div.upload-status__content > p")

            while 'Arraste os documentos ou clique para enviar' in texto:
                sleep(1)
                texto = self.act.obter_texto("body > app-core-root > div > div > div > div > "
                                             "app-document-ref-container > div > app-document-container > "
                                             "app-additional-container > div > div > "
                                             "app-file-upload.ng-untouched.ng-dirty.ng-valid > div > div > label > "
                                             "app-upload-status > div > div.upload-status__content > p")

            self.alterar_frame()
            self.act.clicar_elemento(
                'body > app-core-root > div > div > div > div > app-document-ref-container > app-footer > div > div > '
                'div.footer__content.footer__content--right > pan-button > button > span')

            self.aguardar_modal()

    def upload_contra_cheque_novo(self, path_files, selector):
        if selector != -1:  # GARANTE QUE EXISTE CONTRA_CHEQUE NOS DOC
            try:
                self.act.clicar_elemento("#Overview_DOC_OTHER")
                self.aguardar_modal()
            except TimeoutException:
                pass
            index = ''

            for i in ['0', '1', '2', '3']:
                try:
                    contra_cheque = self.act.obter_texto(f"body > platform-root > platform-operator-entry-container > "
                                                         f"div.iframe.iframe--active > div > div.entry__container > "
                                                         f"platform-operator-dashboard-container > div > "
                                                         f"div.dashboard__info > platform-doc-other-container > "
                                                         f"platform-doc-other-list-container > "
                                                         f"platform-doc-other-ui-list > div > div.content__container > "
                                                         f"div > div > div > div:nth-child({i}) > "
                                                         f"platform-ui-file-upload > div > div > div > "
                                                         f"platform-ui-file-upload-status > div > "
                                                         f"div.file-upload-status__content > div > h3")
                    if 'Contra' in contra_cheque:
                        index = i
                        break

                except TimeoutException:
                    try:
                        contra_cheque = self.act.obter_texto(
                            f"body > platform-root > platform-operator-entry-container > "
                            f"div.iframe.iframe--active > div > div.entry__container > "
                            f"platform-operator-dashboard-container > div > "
                            f"div.dashboard__info > platform-doc-other-container > "
                            f"platform-doc-other-list-container > "
                            f"platform-doc-other-ui-list > div > div.content__container > "
                            f"div > div > div > div:nth-child({i}) > "
                            f"platform-ui-file-upload > div > div > label > div > "
                            f"platform-ui-file-upload-status > div > "
                            f"div.file-upload-status__content > div > h3")
                        if 'Contra' in contra_cheque:
                            index = i
                            break
                    except TimeoutException:
                        pass

            try:
                texto = self.act.obter_texto(f"body > platform-root > platform-operator-entry-container > "
                                             f"div.iframe.iframe--active > div > div.entry__container > "
                                             f"platform-operator-dashboard-container > div > div.dashboard__info > "
                                             f"platform-doc-other-container > platform-doc-other-list-container > "
                                             f"platform-doc-other-ui-list > div > div.content__container > div > div "
                                             f"> div > div:nth-child({index}) > platform-ui-file-upload > div > div > "
                                             f"div > platform-ui-file-upload-status > div > "
                                             f"div.file-upload-status__content > p")
            except TimeoutException:
                texto = self.act.obter_texto(f"body > platform-root > platform-operator-entry-container > "
                                             f"div.iframe.iframe--active > div > div.entry__container > "
                                             f"platform-operator-dashboard-container > div > div.dashboard__info > "
                                             f"platform-doc-other-container > platform-doc-other-list-container > "
                                             f"platform-doc-other-ui-list > div > div.content__container > div > div > "
                                             f"div > div:nth-child({index}) > platform-ui-file-upload > div > div > "
                                             f"label > div > platform-ui-file-upload-status > div > "
                                             f"div.file-upload-status__content > p")

            if 'enviado' in texto:
                print("Contra Cheque já enviado!")
                self.act.clicar_elemento("#Pular_Outros > button > span")
                self.aguardar_modal()

                try:
                    self.act.clicar_elemento("#Pular_SIG_Opt > button > span")
                    self.aguardar_modal()
                except TimeoutException:
                    pass

                return

            for i in ['0', '2']:
                try:
                    self.driver.find_element_by_css_selector(f"#file-upload-{i}").send_keys(path_files[selector])
                    break
                except NoSuchElementException:
                    continue

            sleep(1)
            self.act.clicar_elemento("#Continuar_Preview_Other > button > span")

            texto = self.act.obter_texto(f"body > platform-root > platform-operator-entry-container > "
                                         f"div.iframe.iframe--active > div > div.entry__container > "
                                         f"platform-operator-dashboard-container > div > div.dashboard__info > "
                                         f"platform-doc-other-container > platform-doc-other-list-container > "
                                         f"platform-doc-other-ui-list > div > div.content__container > div > div > div "
                                         f"> div:nth-child({index}) > platform-ui-file-upload > div > div > div > "
                                         f"platform-ui-file-upload-status > div > div.file-upload-status__content > p")

            while 'sucesso' not in texto:
                sleep(2)
                texto = self.act.obter_texto(f"body > platform-root > platform-operator-entry-container > "
                                             f"div.iframe.iframe--active > div > div.entry__container > "
                                             f"platform-operator-dashboard-container > div > div.dashboard__info > "
                                             f"platform-doc-other-container > platform-doc-other-list-container > "
                                             f"platform-doc-other-ui-list > div > div.content__container > div > div > "
                                             f"div "
                                             f"> div:nth-child({index}) > platform-ui-file-upload > div > div > div > "
                                             f"platform-ui-file-upload-status > div > div.file-upload-status__content "
                                             f"> p")

            self.act.clicar_elemento("#Pular_Outros > button > span")
            self.aguardar_modal()

            try:
                self.act.clicar_elemento("#Pular_SIG_Opt > button > span")
                self.aguardar_modal()
            except TimeoutException:
                pass

    def alterar_frame(self):
        self.act.trocar_frame_seletor("#ctl00_Cph_FrameExterno")

    def aguardar_modal(self):
        self.alterar_frame()
        sleep(2)

        try:
            not_found = self.act.retornar_elemento("body > app-core-root > div > div > div > div > app-not-found > "
                                                   "div > h2")

            if "Não encontramos sua proposta" in not_found.text:
                print('Erro na validação do documento!')
                raise ErrorValidacao('Erro na validacação do documento!')
        except TimeoutException:
            pass

        try:
            self.act.retornar_elemento("body > app-core-root > div > div > div > div > app-dashboard-container > div "
                                       "> div > div:nth-child(1) > app-identity-document > div > app-list-item > div")
        except TimeoutException:
            try:
                self.act.retornar_elemento("#DOC_IDENTITY")
            except TimeoutException:
                print('Aguardando abertura do modal...')
                self.aguardar_modal()

    def aguardar_analise_doc(self, selector, selector_tipo):
        sleep(2)
        if selector_tipo:
            var = self.driver.execute_script(
                """return document.querySelector("#_hjRemoteVarsFrame").getAttribute('aria-hidden')""")

            if var is not None:
                if selector == 1:
                    print('Aguardando validação da frente do documento...')
                    sleep(2)
                    self.aguardar_analise_doc(selector, True)
                elif selector == 2:
                    print('Aguardando validação do verso do documento...')
                    sleep(2)
                    self.aguardar_analise_doc(selector, True)

                sleep(2)

            try:
                if self.act.quantidade_elemento("body > app-core-root > div > div > div > div > "
                                                "app-document-ref-container > div > app-document-container > "
                                                "app-upload-error-container > div > h2") > 0:
                    print('Erro na validação do documento!')
                    raise ErrorValidacao('Erro na validacação do documento!')
            except TimeoutException:
                pass

        elif not selector_tipo:
            while True:
                try:
                    self.act.retornar_elemento("body > platform-root > "
                                               "platform-operator-entry-container > "
                                               "div.iframe.iframe--active > div > platform-ui-loader > "
                                               "div.load-picto > div > div > "
                                               "div.cubo__face.cubo__face--back")

                    if selector == 1:
                        print('Aguardando validação da frente do documento...')
                        sleep(2)
                        self.aguardar_analise_doc(selector, False)
                    elif selector == 2:
                        print('Aguardando validação do verso do documento...')
                        sleep(2)
                        self.aguardar_analise_doc(selector, False)

                    sleep(2)
                except TimeoutException:
                    try:
                        if self.act.quantidade_elemento(
                                "body > app-core-root > div > div > div > div > app-document-ref-container > div > "
                                "app-document-container > app-upload-error-container > div > h2") > 0:
                            print('Erro na validação do documento!')
                            raise ErrorValidacao('Erro na validacação do documento!')
                    except TimeoutException:
                        break

    @staticmethod
    def download(url, file_path):
        with open(file_path, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

            if file_path[-3:] == 'jpg' or file_path[-3:] == 'jpeg':
                im = Image.open(file_path)
                im.save(file_path, dpi=(1400, 1400))

    @staticmethod
    def tipo_documento(path_files):
        if path_files[0].find('RG') != -1:
            return 1
        elif path_files[0].find('CNH') != -1:
            return 2
        else:
            return 3

    @staticmethod
    def verifica_contra_cheque(path_files):
        for index in range(0, len(path_files)):
            if path_files[index].find('CONTRA_CHEQUE') != -1:
                return index

        return -1

    def deleta_todos_arquivos(self):
        try:
            os.mkdir(self.caminho_anexos)
            print("Criando pasta anexos em:")
            print(self.caminho_anexos)
        except OSError:
            print("Pasta anexos já existe.")

        for file in os.listdir(self.caminho_anexos):
            file_path = os.path.join(self.caminho_anexos, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    @staticmethod
    def atualiza_contrato_web_admin(ade, codigo_contrato, status):
        print(f"Finalizando consulta do contrado {codigo_contrato}!")
        dados = {
            "key": "f689f1e12a0399fba803cb2365fc362f",
            "statusPropostaBanco": status,
            "observacaoDetalhadaBanco": '',
            "codigoCon": codigo_contrato,
            "ade": ade
        }

        request_dados_contrato = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-pan"
                                               "/contratos/", data=dados)

        if request_dados_contrato.status_code != 200:
            input("Erro ao atualizar contrato no web admin")

    def aguardar_loading(self):
        sleep(4)

        while self.selenium.buscar_quantidade_elemento('.updateprogress:visible') == 1:
            print('Aguardando o Loading...')
            sleep(2)


class ErrorValidacao(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ErrorReprovada(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ErrorAprovada(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
