from selenium.webdriver.common.by import By

import os
import time
import requests
from PIL import Image
from pathlib import Path
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


from sites.oleConsignado.gerar_refin.ole_consignado import (OleConsignado, ErrorOleException)
from sites.oleConsignado.robos.auxiliares import GerenciarSessao
import PATHS
from sites.baseRobos.data_handler import DataHandler
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from selenium.webdriver import Chrome

HORARIO_COMERCIAL = 8, 20


class AnexarDocumentos(OleConsignado):

    id_robo = 20

    def __init__(self, driver: Chrome):
        super().__init__(driver)
        self.sessao = GerenciarSessao(self.driver)
        self.log = DataHandler()
        self.n_anexo = 1
        # atributo <caminho_anexos> herdado de <OleConsignado>

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = AnexarDocumentos(driver)
        try:
            run.main()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def main(self):
        contratos = self.buscar_contratos_enviar_documentos()
        self.contrato = {'data_dep_con': "12/12/2012"}  # variável 'inútil' que tem como função somente não dar pau no
        # erro regex pois a classe AnexarDocumentos precisa ter um self.contrato para não bugar na hora de dar .format
        # no erro.

        for ade, self.codigo_contrato, observacao in contratos:
            print(f"[{self.n_anexo}] Fila Anexar Documentos")
            self.log.api_iniciar_log_robo(
                idRobo=self.id_robo,
                idContrato=self.codigo_contrato
            )
            self.sessao.verificar_estado()
            self.sessao.resolver_estado()

            self.driver.get(
                'https://ola.oleconsignado.com.br/AtuacaoNaProposta/Index')
            time.sleep(4)
            print('Anexando arquivos do contrato: %s' % ade)

            self.selenium.atribuir_valor_campo_jquery('#NumeroProposta', ade)
            self.clicar_elemento_radio_button('FormaAtuacao')
            self.selenium.clicar_elemento('#btnPesquisar')

            try:
                self.verificar_loading()
            except ErrorOleException as e:
                self.atualiza_contrato_web_admin(ade, self.codigo_contrato, e.message)
                self.log.api_registrar_log_robo(log=e.message, status=2)
                self.deleta_todos_arquivos()

                continue
            except Exception as e:
                self.log.api_registrar_log_robo(log=f'Erro: {e}', status=0)
                self.sessao.verificar_estado()
                time.sleep(4)
                loc_error = '//strong[text()="Error"]'

                time.sleep(4)
                loc_error = '//strong[text()="Error"]'
                if self.act.esta_presente(loc_error, By.XPATH):
                    msg_erro = 'Pagina fora do ar.'
                    print(msg_erro + 'Pulando a inserção.')

                    self.log.api_registrar_log_robo(
                        log=f'Erro: Pagina fora do ar.', status=0)
                    self.driver.refresh()
                    raise ErrorOleException

                print(e)

            self.selenium.clicar_elemento('#Aprovar')
            self.verificar_loading()

            path_files = []
            arquivos_contrato = self.buscar_documentos_contrato(ade)
            print('Downloading e anexando arquivos...')

            #self.sessao.resolver_estado()

            for url_arquivo in arquivos_contrato['arquivos']:
                nome_arquivo = url_arquivo.split('?')[0].split('/')[-1]
                url_arquivo = r'%s' % url_arquivo
                if not 'SELFIE' in url_arquivo and not 'COMPROVANTE_ENDERECO' in url_arquivo and not 'SELFIE' in observacao: 
                    try:
                        self.download(url_arquivo, str(self.caminho_anexos / nome_arquivo))
                        time.sleep(5)
                        path_files.append(str(self.caminho_anexos / nome_arquivo))
                    except:
                        pass

                if 'SELFIE' in observacao:
                    try:
                        self.download(url_arquivo, str(self.caminho_anexos / nome_arquivo))
                        path_files.append(str(self.caminho_anexos / nome_arquivo))
                    except:
                        pass

            if(len(path_files) > 0):
                
                self.upload('file', "\n".join(path_files))
                self.selenium.clicar_elemento('#btnAprovar')
                
                try:
                    self.verificar_loading_anexos()
                except ErrorOleException as e:
                    self.log.api_registrar_log_robo(log=f"ERRO: {e.message}", status=0)

                    self.deleta_todos_arquivos()
                    continue

                except Exception as e:
                    self.sessao.verificar_estado()
                    time.sleep(4)
                    loc_error = '//strong[text()="Error"]'
                    self.log.api_registrar_log_robo(log=f"ERRO: {e}", status=0)

                    if self.act.esta_presente(loc_error, By.XPATH):
                        msg_erro = 'Pagina fora do ar.'
                        print(msg_erro + 'Pagina fora do ar.')
                        self.log.api_registrar_log_robo(log=f"ERRO: {e}", status=0)
                        self.driver.refresh()
                        self.main()
                    print(e)

                try:
                    self.selenium.clicar_elemento('#btnOk')
                    self.atualiza_contrato_web_admin(
                        ade, self.codigo_contrato, 'DOCUMENTOS ANEXADOS NO BANCO')
                    self.log.api_registrar_log_robo(log="Anexados com sucesso.", status=2)
                except:
                    pass


                self.deleta_todos_arquivos()
            else:
                self.atualiza_contrato_web_admin(
                        ade, self.codigo_contrato, 'NAO HA DOCUMENTOS NA PROPOSTA')
                continue


    def download(self, url, file_path):
        with open(file_path, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

            if (file_path[-3:] == 'jpg' or file_path[-3:] == 'jpeg'):
                im = Image.open(file_path)
                im.save(file_path, dpi=(1400, 1400))

    def upload(self, selector_id, file_path):
        self.driver.find_element(By.ID,selector_id).send_keys(file_path)

    def deleta_todos_arquivos(self):
        for file in os.listdir(str(self.caminho_anexos)):
            file_path = os.path.join(str(self.caminho_anexos), file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def buscar_contratos_enviar_documentos(self):
        request_contratos = requests.get(
            'https://emprestimofacil.co/web_admin/api/v1/contratos/enviar-documentos-banco/banco-ole/?key=f689f1e12a0399fba803cb2365fc362f')

        if (request_contratos.status_code != 200):
            input('Banco Olé Error - Não foi possível buscar os contratos')

        contratos_anexar = request_contratos.json()

        if (contratos_anexar[0]['retorno'] != 1):
            print('Nenhum documento para anexar no momento! Trocando de fila...')
            return []

        return contratos_anexar[1:]

    def buscar_documentos_contrato(self, ade):
        request_contratos = requests.get(
            'https://uconecte.me/api/v1/contratos/documentos?ade=%s&key=f689f1e12a0399fba803cb2365fc362f' % (ade))

        if (request_contratos.status_code != 200):
            input('Banco Olé Error - Não foi possível buscar os documentos')

        return request_contratos.json()

    def atualiza_contrato_web_admin(self, ade, codigo_contrato, observacao):
        print('Atualizando contrato')
        dados = {
            "key": "f689f1e12a0399fba803cb2365fc362f",
            "statusPropostaBanco": observacao,
            "observacaoDetalhadaBanco": 'OK',
            "codigoCon": codigo_contrato,
            "ade": ade
        }

        response = requests.post(
            "https://emprestimofacil.co/web_admin/api/v1/atualiza-status/banco-ole/contratos/", data=dados)

        if response.status_code == 200:
            print("Contrato atualizado com sucesso.")
        else:
            print("Não foi possível atualizar o contrato.")
            print(f"Status HTTP atualiza contrato: {response.status_code}")
