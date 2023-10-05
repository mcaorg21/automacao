from typing import List

import sys
import requests
import base64
import os
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions
from selenium.webdriver.common.by import By
import PATHS
from pathlib import Path
from selenium.common.exceptions import UnexpectedAlertPresentException
from sites.baseRobos.data_handler import DataHandler
from sites.pan.auxiliares.sessao import verificar_sessao_login, login, HORARIO_COMERCIAL
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver import Chrome
from sites.pan.pan_insercao.auto.pan_inserc_formulários import (tratar_mensagens_sistema)


class GerarContratos:

    id_fila_gerar = 29

    def __init__(self, driver, **kwargs):
        self.base_path = Path(PATHS.project_path())
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"
        self.contrato = {}
        self.driver = driver
        self.act = SeleniumActions(self.driver)
        self.selenium = SeleniumHelper(self.driver)
        self.log: DataHandler = DataHandler()
        self.n_contratos = 0
        self.n_contratos_maximo = 10
        self.cpf = kwargs.get("login", "")
        self.senha = kwargs.get("senha", "")
        self.parceiro = kwargs.get("parceiro", "")
        self.aguardar_sessao = False

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome, configs: dict):
        run = GerarContratos(driver, **configs)
        try:
            return run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        try:
            # verifica se existe um PDF na pasta quando o programa inicia. Caso sim, o remove.
            os.remove(str(self.base_path/"inss"/"extrato"/"-emprestimos-consignados.pdf"))
        except FileNotFoundError:
            pass

        self.menu_contratos()
        print('Trabalhando na fila de geração de contratos')
        contratos = self.buscar_contratos_gerar()
        if not contratos:
            return -1

        self.n_contratos = 0
        for contrato in contratos:
            print(contrato)
            
            if self.n_contratos == self.n_contratos_maximo:
                return 1
            self.n_contratos += 1
            
            self.log.api_iniciar_log_robo(
                 idContrato=contrato["codigo_con"],
                 idRobo=self.id_fila_gerar
             )
            print(f"CONTRATO Nº{self.n_contratos} DE {self.n_contratos_maximo}")
            self.contrato = contrato
            print(f'Trabalhando no contrato {self.contrato["codigo_con"]}')
            try:
                tratar_mensagens_sistema(self.act,self.act.obter_texto_alerta(),contrato)
            except:
                pass
            self.driver.get('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')

            try:
                tratar_mensagens_sistema(self.act,self.act.obter_texto_alerta(),contrato)
                sleep(2)
            except:
                pass
            print('Clicando no menu')
            self.act.hover_e_clique('//*[@id="navbar-collapse-funcao"]/ul/li[2]/a',By.XPATH)
            sleep(2)
            print('Clicando novamente no menu')
            self.act.hover_e_clique('//*[@id="navbar-collapse-funcao"]/ul/li[2]/a',By.XPATH)
            print('Escolhendo a esteira de contratos...')
            self.act.hover_e_clique('//*[@id="WFP2010_PWTCNPROP"]',By.XPATH)


            if(contrato['ade']):
                # passar número proposta
                try:
                    self.act.enviar_texto('//*[@id="ctl00_Cph_AprCons_txtPesquisa_CAMPO"]', contrato['ade'], metodo=By.XPATH)
                except:
                    continue
                # pesquisar
                self.act.clicar_elemento('//*[@id="btnPesquisar_txt"]',metodo=By.XPATH)

                self.aguardar_loading()

                try:
                    teste_vazio = self.act.obter_texto('//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr/td', metodo=By.XPATH)
                    if teste_vazio == 'Não há dados para a visualização.':
                        continue
                except TimeoutException:
                    pass


                self.aguardar_loading()

                situacao = ''
                try:
                    situacao = self.act.obter_texto('//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr[2]/td[3]/a', metodo=By.XPATH)
                except:
                    pass

                if situacao == 'CAN':
                    self.url = 'contrato cancelado'
                    self.envia_pdf_contrato()
                    self.driver.get('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')  
                    continue
                
                # atividade
                print('Clicando em atividade...')
                try:
                    atividade = self.act.obter_texto('//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr[2]/td[4]/a', metodo=By.XPATH)                  
                    self.aguardar_loading()
                except:
                    continue
                    
                if atividade == 'Negociacao em andamento':
                    self.act.clicar_elemento('//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr[2]/td[4]/a', metodo=By.XPATH)
                    self.aguardar_loading()
                    self.act.clicar_elemento('//*[@id="btnConcluirNegociacao"]', metodo=By.XPATH)
                    self.aguardar_loading()                    
                    self.act.trocar_frame_referencia('framePopUp', metodo=By.ID)
                    self.act.clicar_elemento('//*[@id="radioFormalizadorSim"]', metodo=By.XPATH)
                    self.act.clicar_elemento('//*[@id="btnConfirmar"]', metodo=By.XPATH)

                elif atividade == 'Aguarda Retorno Inss':
                    self.url = 'contrato assinado'
                    self.envia_pdf_contrato()
                    self.driver.get('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')  
                    continue

                else:
                    try:                 
                        self.act.clicar_elemento('//*[@id="ctl00_Cph_AprCons_grdConsulta"]/tbody/tr[2]/td[4]/a', metodo=By.XPATH)
                        print('Aguardando primeira abertura...')
                        self.aguardar_loading()
                    except:
                        continue

                while self.act.esta_presente('ctl00_Cph_FrameExterno',By.ID) == False: 
                    print('Aguardando frame...')

                while self.act.trocar_frame_referencia('ctl00_Cph_FrameExterno', metodo=By.ID) == False:
                    print('Tentando trocar frame')

                while self.act.esta_presente('SIGNATURE',By.ID) == False: 
                    print('Aguardando abertura final modal...')

                try:
                    sleep(2)
                    self.act.clicar_elemento('//*[@id="SIGNATURE"]', metodo=By.XPATH)
                    sleep(5)
                    elemento = self.driver.find_element_by_xpath('/html/body/platform-root/platform-operator-entry-container/div[2]/div/div/platform-operator-dashboard-container/div/div[2]/div[2]/platform-link-container/platform-link-ui/div/div/div/div[2]/div/pan-mahoe-card/platform-link-action/div/platform-link-action-copy/div/div[2]/pan-mahoe-text-field/div[2]/input')
                    self.url = elemento.get_attribute('value')
                    #pdf_base_64_CCB = self.baixar_pdf('CCB', tipo_doc)
                    #pdf_base_64_CET = self.baixar_pdf('CET', tipo_doc)
                    self.envia_pdf_contrato()
                    self.driver.get('https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')
                except:
                    continue

        #return 0

    def preencher_info_consulta(self, tipo_doc='pre_imp', rec=0):
        """
        Preenche o formulário de consulta de documentação respectivo ao link
        'Documentação Pré-impresso'. Caso não haja opções de documentação
        neste link, o navegador é redirecionado para o link de 'Documentação
        Impresso', para preenchimento do formulário.
        :var tipo_sel: trecho dos seletores dos campos do formulário que diferencia
            o tipo de consulta ('Pré-Impresso' ou 'Impresso').
        :param tipo_doc: tipo de documento a que se refere o formulário a ser preenchido.
        :return: tipo_doc: o tipo de formulário que acabou de ser preenchido.
        """
        # Verifica se o tipo de documentação digital é 'Pré-Impresso' ou 'Impresso'
        tipo_sel = self.__filtrar_seletor_tipo_doc(tipo_doc)
        # Preencher número da proposta
        loc_n_proposta = f"#ctl00_Cph_UcDocumentacao{tipo_sel}_jnlPanel1_ctl00_txtNumeroProposta_CAMPO"
        self.act.enviar_texto(loc_n_proposta, self.contrato['ade'])
        self.act.press_TAB(loc_n_proposta)
        sleep(1)

        if self.act.verificar_existencia_alerta():
            texto = self.act.obter_texto_alerta()
            self.act.manusear_alerta('aceitar')
            if "localizada" in texto:
                raise PropostaNaoEncontradaException(texto, self.contrato["codigo_con"])

        if self.act.obter_valor(loc_n_proposta) == "":
            self.act.enviar_texto(loc_n_proposta, self.contrato['ade'])

        # Clicar no menu select de tipo de documentação, dando a ele foco.
        loc_cb_doc = f"#ctl00_Cph_UcDocumentacao{tipo_sel}_jnlPanel1_ctl00_cboTipoDocumentacao_CAMPO"
        self.act.clicar_elemento(loc_cb_doc)
        if self.act.verificar_existencia_alerta():
            texto = self.act.obter_texto_alerta()
            self.act.manusear_alerta('aceitar')
            if "localizada" in texto:
                raise PropostaNaoEncontradaException(texto, self.contrato["codigo_con"])

        # Verificar se há tipos de documentos disponíves
        loc_select_tipo_doc = (f'//*[@id="ctl00_Cph_UcDocumentacao{tipo_sel}_jnlPanel1_'
                               'ctl00_cboTipoDocumentacao_CAMPO"]')

        self.act.clicar_elemento(loc_select_tipo_doc, By.XPATH)
        self.act.manusear_alerta('aceitar')

        if not self.documentos_presentes(loc_select_tipo_doc):
            # Caso não haja propostas no 'pré-impresso' redirecionar para 'impresso'.
            print("Redirecionando para consulta de 'Documentação Impresso.")
            self.driver.get(
                'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Relatorios/Documentacao/UI.DocumentacaoDigital.aspx')

            if rec > 1:
                raise PropostaNaoEncontradaException('Proposta não disponível para geração.', self.contrato["codigo_con"])
            sleep(2)
            return self.preencher_info_consulta(tipo_doc='imp', rec=rec+1)

        self.aguardar_loading()

        return tipo_doc

    def documentos_presentes(self, loc_select_tipo_doc):
        opts_docs: List[WebElement] = self.act.retornar_opcoes_select(loc_select_tipo_doc, By.XPATH)
        txt_opts = [opt.text for opt in opts_docs]
        for txt_opt in txt_opts:
            if "CET" in txt_opt or "CCB" in txt_opt:
                return True

        return False

    @staticmethod
    def __filtrar_seletor_tipo_doc(tipo_doc):
        """
        Recebe um str relativo ao tipo de documento ao qual o formulário de
        Documentação Digital se refere e retorna o trecho do str que diferencia os
        seletores dos campos dos formulários 'Pré-Impresso' e 'Impresso'.
        :param tipo_doc: string indicador do tipo de formulário que será preenchido.
        :return: trecho de str que diferencia os seletores dos dois tipos de fomulário.
        """
        if tipo_doc == 'pre_imp':
            print("Preenchendo campos de 'Documentação Pré-Impresso.")
            return 'PreImp'

        elif tipo_doc == 'imp':
            return ''

    def buscar_contratos_gerar(self):
        request_contratos_a_gerar = requests.get(
            f'https://uconecte.me/api/v1/contratos/status/gerar?key={self.api_key}&consulta=gerar&banco=pan')

        if request_contratos_a_gerar.status_code != 200:
            input('Pan Error - Não foi possível buscar os contratos')

        contratos = request_contratos_a_gerar.json()['contratos']

        if len(contratos) == 0:
            print('Nenhum contrato na fila gerar contrato! Trocando de fila...')
            return []

        return contratos

    def menu_contratos(self):
        self.driver.get(
            'https://panconsig.pansolucoes.com.br/WebAutorizador/MenuWeb/Relatorios/Documentacao/UI.DocumentacaoDigital.aspx')

    def atualizar_erros(self, texto):
        dados = {
            "mensagem": "Contrato não gerado",
            "observacao" : "Gerar manualmente"
                  }                         
        request_gerar_contrato = requests.put("https://uconecte.me/dev/api/v1/contratos/"+self.contrato['codigo_con']+"?key=f689f1e12a0399fba803cb2365fc362f",
                                               data=dados)

        if request_gerar_contrato.status_code != 200:
            print(request_gerar_contrato.json())
            print('Não foi possível gerar o contrato')

        print(f'Contrato {self.contrato["ade"]} atualizado com erro.')

    def envia_pdf_contrato(self, pdf_base_64_CCB='', pdf_base_64_CET=''):
        print('Gerando contrato...')
        dados_pdf = {
            'key': 'f689f1e12a0399fba803cb2365fc362f',
            'ade': self.contrato['ade'],
            'codigoCliente': self.contrato['codigo_cli'],
            'codigoContrato': self.contrato['codigo_con'],
            'base64': pdf_base_64_CCB,
            'CETbase64': pdf_base_64_CET,
            'banco': 'pan',
            'linkAssinaturaDigital': self.url
        }
        print(self.url)
        request_gerar_contrato = requests.post("https://uconecte.me/api/v1/contratos/gerar",
                                               data=dados_pdf)
        if request_gerar_contrato.status_code != 200:
            print(request_gerar_contrato.json())
            input('Não foi possível gerar o contrato')

        print(f'Contrato {self.contrato["ade"]} gerado com sucesso!')
        self.log.api_registrar_log_robo(
            log=f'Contrato {self.contrato["ade"]} gerado com sucesso!',
            status=2
        )

    def baixar_pdf(self, selector, tipo_doc='pre_imp'):
        tipo_sel = self.__filtrar_seletor_tipo_doc(tipo_doc)
        if selector == 'CCB':
            print('Fazendo o download da CBB...')
            self.selenium.atribuir_valor_campo_jquery(
                f"#ctl00_Cph_UcDocumentacao{tipo_sel}_jnlPanel1_ctl00_cboTipoDocumentacao_CAMPO",
                "279")
        else:
            print('Fazendo o download da CET...')
            self.selenium.atribuir_valor_campo_jquery(
                f"#ctl00_Cph_UcDocumentacao{tipo_sel}_jnlPanel1_ctl00_cboTipoDocumentacao_CAMPO",
                "282")

        btn_visualizar = "#btnVisualizar_txt"
        self.act.clicar_elemento(btn_visualizar)
        self.aguardar_loading()
        sleep(2)

        pdf = open(str(self.base_path/"pan"/"anexos"/"arquivoWFSIC.pdf"), 'rb')
        pdf_64 = base64.b64encode(pdf.read())
        pdf.close()
        os.remove(str(self.base_path/"pan"/"anexos"/"arquivoWFSIC.pdf"))

        return pdf_64

    def aguardar_loading(self):
        sleep(3)

        while self.selenium.buscar_quantidade_elemento('.updateprogress:visible') == 1:
            print('Aguardando o Loading...')
            sleep(2)


class PropostaNaoEncontradaException(Exception):
    def __init__(self, txt, proposta):
        super().__init__()
        self.msg = f"{txt}: {proposta}"

    def __repr__(self):
        return self.msg



#try:
            #    if not verificar_sessao_login(self.driver, aguardar=self.aguardar_sessao):
            #        login(self.driver, self.cpf, self.senha)
            #        self.aguardar_sessao = True
            #    self.menu_contratos()
            #    tipo_doc = self.preencher_info_consulta('imp')
            #    pdf_base_64_CCB = self.baixar_pdf('CCB', tipo_doc)
            #    pdf_base_64_CET = self.baixar_pdf('CET', tipo_doc)
            #    self.envia_pdf_contrato(pdf_base_64_CCB, pdf_base_64_CET)
            #    sleep(2)
            #    self.menu_contratos()

            #except PropostaNaoEncontradaException as e:
            #    print(e)
            #    self.atualizar_erros(e.msg)

            #except UnexpectedAlertPresentException as e:
            #    # self.log.api_registrar_log_robo(log=e.alert_text, status=0)

            #    if 'formalização não disponível' in e.alert_text:
            #        self.atualizar_erros(e.alert_text)
            #    self.act.manusear_alerta()
            #    continue
            #except Exception as e:
            #    # self.log.api_registrar_log_robo(log=e, status=0)
            #    self.atualizar_erros(e.alert_text)
            #    continue
