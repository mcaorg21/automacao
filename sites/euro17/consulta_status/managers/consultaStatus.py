import array
from selenium.webdriver import Chrome

from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.manager import Manager
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions

import os,time,pdb,re

from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError
from sites.baseRobos.core.data_helpers import formatar_cpf_sem_caracteres,formatar_moeda

from sites.euro17.consulta_status.data.dados_consulta_status import DadosConsultaStatus

from selenium.webdriver.common.by import By
from dados.database.queries.query_dados_robos import query_login_pass_robo

HORARIO_COMERCIAL = 7, 22


class ConsultaStatus(Manager):

    def __init__(self, driver: Chrome = False, forcar_consulta=False):
        super().__init__()

        self.urls = {
            "consulta": "https://capture.kapmug.com/dashboard",
            "esteira" : "https://analysis.kapmug.com/formalization",
        }
        
        self.set_options('--ignore-ssl-errors')
        self.init_chrome_driver(import_driver=driver)
        self.dados: DadosConsultaStatus = DadosConsultaStatus()
        self.sh = SeleniumHelper(self.chrome_driver)
        self.act = SeleniumActions(self.chrome_driver)
        self.atualiza = Uconecte()
        self.forcar_consulta = forcar_consulta

    @classmethod
    def iniciar_horario_comercial(cls, driver: Chrome, forcar_consulta=False):

        run = ConsultaStatus(driver, forcar_consulta=forcar_consulta)
        try:
            retorno = run.consultar_status_proposta()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return retorno

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def consultar_status_proposta(self):     

        #self.verificar_loading()       
        print('Inciando sincronização...')

        #testes = input('Teste? 1- sim / 2- não')
        testes = 0
        if testes == 0:
            contratos = self.dados.get_contratos_inserir('desc')

            # if self.forcar_consulta == False:
                
            #     if('contratos' in contratos and len(contratos['contratos']) > 20):
            #         print('>>>>> Mais de 10 contratos para inserir. Não irá sincronizar para ajudar na inserção.')
            #         return False
            
            status_a_consultar = self.dados.get_ades()[1:]
            
            if not status_a_consultar:
                print('Sem atualizações para realizar...')
                return True
        else:
            ade = input('Ade: ')
            codigo_con = input('Codigo: ')
            status_a_consultar = [[ade, '06947813557', codigo_con,'','','','2024-01-14']]

        for cnt, proposta in enumerate(status_a_consultar, 1):
            
            print(f"[{cnt}]Fila Consulta Status")
            self.chrome_driver.get(self.urls["consulta"])
            print("Consultando proposta:", proposta)

            ade = proposta[0]
            cod_con = proposta[2]
            self.dados_consulta = {}
            self.dados_consulta['ade'] = ade
            self.dados_consulta["codigoCon"] = cod_con

            print(self.dados_consulta) 

            self.act.enviar_texto('//*[@id="input_text_proposalOrFederalNumber"]', ade, By.XPATH)
            self.act.clicar_elemento('//*[@id="buscar"]', By.XPATH)
            self.verificar_loading()

            try:
                status_consulta = self.act.obter_texto('//div[@title="Proposta"]', By.XPATH).split('\n')[-1]

                if status_consulta == 'Prontas para Prosseguir':
                    if(self.act.quantidade_elemento("//button[contains(text(),'Observações')]", By.XPATH) == 1):
                        #pdb.set_trace()
                        self.act.clicar_elemento("//button[contains(text(),'Observações')]", By.XPATH)
                        time.sleep(1)
                        self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                        detalhes_status = self.act.obter_texto("/html/body/section/div[2]/div/div/section", By.XPATH).strip()
                        cabecalho = ' | '.join(detalhes_status.split('\n')[0:2])

                        self.dados_consulta['observacaoDetalhadaBanco'] = cabecalho + '\n\n' + detalhes_status.split('\n')[-2] + " | " + detalhes_status.split('\n')[-1] 

                        try:
                            texto_sub_status = self.act.obter_texto("/html/body/div/div/div[2]/div/div[2]/section/div/div", By.XPATH)
                        except:
                            texto_sub_status = ""
                            pass

                        if 'Alteração de Valores' in texto_sub_status or 'Recomendamos a Operação considerando as validações' in self.dados_consulta['observacaoDetalhadaBanco'] or 'Aprovado' in self.dados_consulta['observacaoDetalhadaBanco']:

                            print('>>>>> Atualizando valores de contrato pelo recomendado.')
                            
                            dados_atualizacao = {}
                            self.act.clicar_elemento("//button[contains(text(),'Fechar')]", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            
                            dados_atualizacao['mensagem'] = 'Atualizar Valor'
                            dados_atualizacao['valorContrato'] = "{:.2f}".format(formatar_moeda(self.act.obter_texto("/html/body/div/main/div[2]/div/section/div/div[2]/div[1]/p[2]", By.XPATH)))
                            dados_atualizacao['textoMensagem'] = 'Valores atualizados'
                            dados_atualizacao['valorParcela'] = self.act.obter_texto("/html/body/div/main/div[2]/div/section/div/div[2]/div[2]/p[2]", By.XPATH).split(' ')[1]
                            dados_atualizacao['prazo'] = self.act.obter_texto("/html/body/div/main/div[2]/div/section/div/div[2]/div[3]/p[2]", By.XPATH).split(' ')[0]
                            self.atualiza.atualizar_contrato(cod_con, dados_atualizacao)

                            self.act.clicar_elemento("//button[contains(text(),'CONTRATAR')]", By.XPATH)
                            self.verificar_loading()
                            
                            self.act.enviar_texto('//*[@id="input_text_proposalOrFederalNumber"]', ade, By.XPATH)
                            self.act.clicar_elemento('//*[@id="buscar"]', By.XPATH)
                            self.verificar_loading()
                            
                            print('>>>>> Reenviando link de assinatura Remota')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Nova Assinatura digital'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)

                    else:
                        self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                        self.verificar_loading()
                        
                        try:
                            texto_tela = self.act.obter_texto("//*[@id='root']/main/div[2]/div/section/div/form", By.XPATH)
                            
                            if('tire fotos ou anexe os documentos' in texto_tela.lower()):
                                print('----> TRATAR DOCUMENTOS.')
                                #documento = self.act.obter_texto('/html/body/div/main/div[2]/div/section/div/form/div[1]', By.XPATH)
                                #pdb.set_trace()
                                
                                self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                                self.dados_consulta['observacaoDetalhadaBanco'] = 'Enviar os seguintes documentos novamente: '
                                
                                if 'NOVO DOCUMENTO DE IDENTIFICAÇÃO' in texto_tela:
                                    self.dados_consulta['observacaoDetalhadaBanco'] += '|documento|'
                                
                                if 'EXTRATO BANCÁRIO' in texto_tela:
                                    self.dados_consulta['observacaoDetalhadaBanco'] += '|extrato|'
                                    
                                if 'ÚLTIMO CONTRACHEQUE' in texto_tela:
                                    self.dados_consulta['observacaoDetalhadaBanco'] += '|ultimocc|'
                                
                                if 'PENÚLTIMO CONTRACHEQUE' in texto_tela:
                                    self.dados_consulta['observacaoDetalhadaBanco'] += '|penultimocc|'
                                    
                                if 'COMPROVANTE DE RESIDÊNCIA' in texto_tela:
                                    self.dados_consulta['observacaoDetalhadaBanco'] += '|residencia|'
                                    
                                # else:
                                
                                # self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                                # self.dados_consulta['observacaoDetalhadaBanco'] = 'Enviar documentos pendentes pelo link.'
                        
                        except:
                            texto_tela = self.act.obter_texto("/html/body/div/main/div/section/div/h2", By.XPATH)
                            
                            if 'Formalização remota' in texto_tela:
                                self.chrome_driver.get(self.urls["esteira"])
                                self.act.enviar_texto('//*[@id="input_text_search"]', ade, By.XPATH)
                                self.verificar_loading()
                                if self.act.obter_texto('//div[@title="Situação da proposta"]/span', By.XPATH) == 'Em andamento':
                                    self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                                    self.dados_consulta['observacaoDetalhadaBanco'] = 'Assinatura digital'
                
                elif( status_consulta == 'Formalização Remota'):
                    print('>>>>> Formalização Remota')
                    try:
                        texto_sub_status = self.act.obter_texto("/html/body/div/div/div[2]/div/div[2]/section/div/div", By.XPATH)
                        if 'Formalização remota - cliente' in texto_sub_status:
                            print('>>>>> Reenviando link de assinatura Remota')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Nova Assinatura digital'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)
                            
                        elif 'Cliente Incluir Documentos' in texto_sub_status:
                            print('>>>>> Incluir Documentos')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Aguardando Envio Docs'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)
                            
                        elif 'Nova Prova-viva - Formalização' in texto_sub_status:
                            print('>>>>> Nova Prova-viva - Formalização')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Prova de vida'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)

                        elif 'Incluir selfie' in texto_sub_status:
                            print('>>>>> Selfie - Formalização')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Envio de Selfie'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)

                        elif 'Novo audio' in texto_sub_status:
                            print('>>>>> Novo audio - Formalização')
                            self.act.clicar_elemento("//button[contains(text(),'Continuar')]", By.XPATH)
                            self.verificar_loading()
                            self.act.clicar_elemento("//button[contains(text(),'Formalização')]", By.XPATH)
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = 'Envio de Audio'
                            self.dados_consulta['linkAssinaturaDigital'] = self.act.obter_texto("/html/body/div/main/div/section/div/div[2]/div[1]/span", By.XPATH)
                            self.act.clicar_elemento("//button[contains(text(),'FINALIZAR')]", By.XPATH)

                        
                        else:
                            print('>>>>> Classificando Status')
                            array_texto_status = texto_sub_status.split('\n')
                            etapa_index = array_texto_status.index('Etapa:')
                            if etapa_index + 1 < len(array_texto_status):
                                etapa_valor = array_texto_status[etapa_index + 1]
                            time.sleep(2)
                            self.dados_consulta["statusPropostaBanco"] = 'Classificar Pendente'
                            self.dados_consulta['observacaoDetalhadaBanco'] = etapa_valor
                            

                        
                    except:
                        texto_sub_status = ""
                        pass
                
                else:
                    self.dados_consulta["statusPropostaBanco"] = status_consulta
                    self.dados_consulta['observacaoDetalhadaBanco'] = ''
            
            except:
                
                self.driver.get(self.urls["esteira"])
                self.act.enviar_texto('//*[@id="input_text_search"]', ade, By.XPATH)
                self.verificar_loading()
                self.dados_consulta["statusPropostaBanco"] = self.act.obter_texto('//div[@title="Situação da proposta"]/span', By.XPATH)
                self.dados_consulta['observacaoDetalhadaBanco'] = ''

            self.dados.post_dados_consultados(self.dados_consulta)

        return True
    
    def verificar_loading(self, interacoes = 60):
        
        print('Verificando loading...')
        
        while (self.act.quantidade_elemento("/html/body/div/div/div[2]/section/div/section/div/div/div/div/div", By.XPATH) == 1):
            print('Aguardando Loading...')
            interacoes -= 1
            time.sleep(1)
            if(interacoes < 1):
                return False