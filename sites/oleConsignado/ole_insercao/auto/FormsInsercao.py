"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: FormsInsercao
| data: 2020-02-18
| autor: Gustavo Belleza

| funcionamento:
"""
# SuperClasse herdada por todas as outras classes que implementam automação da interface.
from sites.baseRobos.core.data_helpers import similaridade
from sites.baseRobos.gui_auto import AutoGUI

from sites.baseRobos.core.selenium_actions import SeleniumActions

# Exceptions nativas do Selenium
from selenium.common.exceptions import (
    TimeoutException, InvalidElementStateException
)
# Funções auxiliares
from sites.baseRobos.core.uconecte import Uconecte
from .auxiliares import (
    selecionar_prazo, validar_valor_renda,
    select_tipo_conta
)
# Função que retorna todas as mensagens de erro já documentadas no site.
from .auxiliares import (
    verificar_erros
)
# stdlib
from time import sleep
from random import randint,randrange
import re, pdb


class AbaDadosSimulacao(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver: object = chrome_driver
        self.uconecte: object = Uconecte()

        self.t_max: float = 2
        self.t_min: float = 1
        self.t_sleep = 0.5

        self.atualizacoes: dict = {}
        self.act.time_out = 2

    @property
    def tabela_produtos(self):
        loc_tabela = 'input#gridretorno-1'
        return not self.act.esta_presente(loc_tabela)

    def verificar_loading(self, interacoes=100, aguardar = False):
        sleep(3)
        try:
            while (self.act.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
                print('Aguardando Loading...' + str(interacoes))
                sleep(0.3)
                interacoes -= 1
        except:
            pass

        if(interacoes == 0):
            print('XXXXXXXXXXXXXXXXXXXX Loading sem solução... XXXXXXXXXXXXXXXXXXXX')
            return


    def preencher_campo_cpf(self, contrato):
        loc = '#CPF'
        self.act.hover_e_clique(loc, pause=0.1)
        self.act.enviar_caracteres(
            loc, contrato['cpf'],
            clear=False, delay=0.1
        )

    def pedir_in_100(self, contrato, rec = 0):
        self.loading()
        print('Selecionando IN100...')

        try:

            print('Preenchendo campos da IN100..')
            self.act.hover_e_clique('//*[@id="AutorizacaoConsulta"]', self.by.XPATH)
            sleep(0.5)
            self.act.enviar_texto_intervalado('//*[@id="Nome"]', contrato['nome'], self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.hover_e_clique('//*[@id="DDD"]', self.by.XPATH)
            self.act.press_backspace('#DDD')
            #self.act.enviar_texto_intervalado('//*[@id="DDD"]', contrato['dddCelular'], self.by.XPATH, delay=randint(10, 30) / 700)
            self.driver.execute_script(f""" $('#DDD').val('{contrato['dddCelular']}')""")
            self.act.enviar_texto('//*[@id="Telefone"]', contrato['celular'], self.by.XPATH)
            self.act.enviar_texto('//*[@id="Email"]', contrato['email'], self.by.XPATH)
            self.act.enviar_texto('//*[@id="CEPIN100"]', contrato['cep'], self.by.XPATH)
            self.loading()

            if(contrato['token'] == 0 or contrato['token'] == ''):
                try:
                    print('Enviando SMS..')
                    self.act.hover_e_clique('//*[@id="btnEnviarSms"]', self.by.XPATH)
                except:
                    print('Reenviando SMS..')
                    self.act.hover_e_clique('//*[@id="btnReenviarSms"]', self.by.XPATH)

                self.loading()

                try:
                    print('Clicando em OK..')
                    self.act.hover_e_clique('//*[@id="btnOKMensagemSucesso"]', self.by.XPATH)
                except:
                    pass

                texto_erro = ''
                try:
                    print('Verificando erros..')

                    texto_erro = self.act.obter_texto('//*[@id="divMensagemErro"]',self.by.XPATH)
                    rec += 1

                    if('obrigatório' in texto_erro.lower()):     
                        print('Preenchendo IN100 novamente...')   
                        self.act.hover_e_clique('//*[@id="AutorizacaoConsulta"]', self.by.XPATH)            
                        return self.pedir_in_100(contrato, rec)
                        if(rec >= 5):
                            return
                except:
                    texto_erro = ''
                    pass

                if(texto_erro == ''):
                    return False
            else:
                print('Preenchendo o token')
                sleep(2)
                try:
                    self.driver.execute_script(f""" document.getElementById("ChaveAcesso").removeAttribute("readonly"); """)
                    self.act.enviar_texto('//*[@id="ChaveAcesso"]',contrato['token'], self.by.XPATH)
                    sleep(2)
                    try:
                        texto = self.act.obter_texto('//*[@id="errChaveAcesso"]',self.by.XPATH)
                        if('Erro ao validar o campo Chave de Acesso' in  texto):
                            print('|Erro Token|')
                            contrato['token'] = 0;
                            self.act.hover_e_clique('//*[@id="AutorizacaoConsulta"]', self.by.XPATH)  
                            return self.pedir_in_100(contrato)
                    except:
                        print('|Token aceito|')
                        pdb.set_trace()
                        return True
                except:
                    contrato['token'] = 0;
                    self.act.hover_e_clique('//*[@id="AutorizacaoConsulta"]', self.by.XPATH)  
                    return self.pedir_in_100(contrato)

        except:
            print('IN100 não disponível para enviar...')
            pass

    def preencher_dados_banco_portabilidade(self, contrato, atualiza_saldo_devedor = False, valor_novo_saldo_devedor = 0):

        self.loading()
        
        if(atualiza_saldo_devedor):
            print('Preenchendo novamente saldo devedor...')
            valor_novo_saldo_devedor = str(valor_novo_saldo_devedor + float(contrato['dados_portabilidade']['saldoDevedorFinal']))
            self.act.enviar_texto_intervalado('//*[@id="SaldoDevedor"]',"{:.2f}".format(float(valor_novo_saldo_devedor)), self.by.XPATH, delay=randint(10, 30) / 700)
        else:
            print("Inserindo banco da portabilidade", contrato['dados_portabilidade']['numeroBanco'])
            loc_portabilidade = 'button[data-id="selectBanco"]'
            sleep(0.5)
            self.act.hover_e_clique(loc_portabilidade)

            loc_banco_portabilidade = '//*[@id="dadosContratoASerPortado"]/div[3]/div[2]/div[1]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_banco_portabilidade, contrato['dados_portabilidade']['numeroBanco'], self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_banco_portabilidade, self.by.XPATH)

            print('Preenchendo numero contrato...')
            self.act.enviar_texto_intervalado('//*[@id="NumeroContrato"]', contrato['dados_portabilidade']['numeroContrato'], self.by.XPATH, delay=randint(10, 30) / 700)

            print('Preenchendo total de parcelas do contrato...')
            self.act.enviar_texto_intervalado('//*[@id="QuantidadeTotalParcelas"]', contrato['dados_portabilidade']['parcelasTotais'], self.by.XPATH, delay=randint(10, 30) / 700)

            print('Preenchendo quantidade de parcelas a serem portadas...')
            parcelas_portadas = str(int(contrato['dados_portabilidade']['parcelasTotais']) - int(contrato['dados_portabilidade']['parcelasPagas']))
            self.act.enviar_texto_intervalado('//*[@id="QuantidadeParcelasPortadas"]', parcelas_portadas, self.by.XPATH, delay=randint(10, 30) / 700)

            print('Preenchendo valor da parcela')
            self.act.enviar_texto_intervalado('//*[@id="ValorParcelas"]',contrato['dados_portabilidade']['parcela'], self.by.XPATH, delay=randint(10, 30) / 700)

            print('Preenchendo saldo devedor...')
            self.act.enviar_texto_intervalado('//*[@id="SaldoDevedor"]',contrato['dados_portabilidade']['saldoDevedorFinal'], self.by.XPATH, delay=randint(10, 30) / 700)
            
            print('Escolhendo a tabela...')
            loc_tabela_portabilidade = 'button[data-id="selectProdutoPortComp"]'
            sleep(0.5)
            self.act.hover_e_clique(loc_tabela_portabilidade)

            loc_banco_portabilidade = '//*[@id="dadosSimulacao"]/div[3]/div[2]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_banco_portabilidade, '012641', self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_banco_portabilidade, self.by.XPATH)

        print('Simulando...')
        self.act.hover_e_clique('//*[@id="btnSimularPortabilidade"]', self.by.XPATH)
        self.loading()

    def parar_while_tentativas(self):
        print('Verificando se pode parar o while...')
        try:
            self.act.clicar_elemento('//*[@id="btnFecharPopUpCalculoRefin"]',self.by.XPATH)
            self.loading()
        except:
            pass

        rec = 0        
        try:
            parcela_resultado = float(self.act.obter_texto('//*[@id="GridSimulacao"]/div[2]/div/div/div/table/tbody/tr[1]/td[4]', self.by.XPATH).replace(',','.'))
            return True
        except:
            return False
            

    def comparar_resultado_parcela(self, contrato, recr, saldo_devedor_recalcular):
        print('Comparando resultado da parcela calculada...')
        try:
            self.act.clicar_elemento('//*[@id="btnFecharPopUpCalculoRefin"]',self.by.XPATH)
            self.loading()
        except:
            pass

        rec = 0        
        try:
            parcela_resultado = float(self.act.obter_texto('//*[@id="GridSimulacao"]/div[2]/div/div/div/table/tbody/tr[1]/td[4]', self.by.XPATH).replace(',','.'))
        except:
            parcela_resultado = float(self.act.obter_texto('//*[@id="GridSimulacao"]/div[2]/div/div/div/table/tbody/tr[1]/td[4]', self.by.XPATH).replace('.','').replace(',','.'))

        parcela_contrato = float(contrato['dados_portabilidade']['parcela'])

        if(parcela_resultado <= parcela_contrato):
            parcela_valor_emprestimo: dict = {}
            parcela_valor_emprestimo['valorContrato'] = self.act.obter_texto('//*[@id="dados-compPort-001"]/div/div[6]/p', self.by.XPATH)
            parcela_valor_emprestimo['valorParcela'] = self.act.obter_texto('//*[@id="GridSimulacao"]/div[2]/div/div/div/table/tbody/tr[1]/td[4]', self.by.XPATH)
            
            return parcela_valor_emprestimo

        else:
            if(recr > 100):
                return False

            # if(recr == 0):
            #     saldo_devedor_recalcular = contrato['dados_portabilidade']['saldoDevedorFinal']

            print('Recalculando parcela até que fique menor...')

            if(float(saldo_devedor_recalcular) > 10000):
                reduzir = 10
            else:
                reduzir = 1

            saldo_devedor_recalcular = str('{0:.2f}'.format(float(saldo_devedor_recalcular) - reduzir))

            try:
                self.act.clicar_elemento('//*[@id="btnFecharPopUpCalculoRefin"]',self.by.XPATH)
                self.loading()
            except:
                pass

            print('Preenchendo saldo devedor...')
            self.act.enviar_texto_intervalado('//*[@id="SaldoDevedor"]',saldo_devedor_recalcular, self.by.XPATH, delay=randint(10, 30) / 700)

            print('Simulando...')
            self.act.hover_e_clique('//*[@id="btnSimularPortabilidade"]', self.by.XPATH)
            self.loading()
            
            try:
                self.act.clicar_elemento('//*[@id="btnFecharPopUpCalculoRefin"]', self.by.XPATH)
                self.loading()
            except:
                pass

            return self.comparar_resultado_parcela(contrato, recr + 1, saldo_devedor_recalcular)
        

    def clicar_iniciar_operacao(self):
        loc = '#btnIniciarOperacao'
        self.act.hover_e_clique(loc, pause=0.1)

    def input_texto_data_nascimento(self, contrato: dict):
        loc_data_nasc = '#DataNascimento'
        try:
            print("Data de nascimento:", contrato['dataNascimento'])

            self.act.hover_e_clique(loc_data_nasc)

            self.act.enviar_texto_intervalado(
                loc_data_nasc, contrato['dataNascimento'],
                delay=randint(10, 30) / 700, clear=False)

            self.act.press_enter(loc_data_nasc)

        except TimeoutException:
            print("Data de nascimento já preenchida")
        except InvalidElementStateException:
            print("Data de nascimento já preenchida")

    def input_texto_convenio(self, codigo_convenio = "011398"):
        print("Código do convênio - ." + codigo_convenio)
        try:
            loc_convenio_select = 'button[data-id="CodigoConvenio"]'
            self.act.hover_e_clique(loc_convenio_select)

            loc_convenio_txt = '//*[@id="divSimulacao"]/div[1]/div[2]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_convenio_txt, codigo_convenio,
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_convenio_txt, self.by.XPATH)
        except TimeoutException:
            print("Campo já preenchido.")

    def select_especie_beneficio(self, contrato: dict):
        loc_esp_ben = 'button[data-id="CodigoEspecieBeneficio"]'
        sleep(0.5)
        try:
            print("Código espécie benefício:", contrato['especieBeneficio'])
            self.act.hover_e_clique(loc_esp_ben)

            loc_esp_ben_txt = '//*[@id="divBeneficio"]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_esp_ben_txt, contrato['especieBeneficio'],
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_esp_ben_txt, self.by.XPATH)
        except TimeoutException:
            print("Campo 'Espécie Benefício' ausente")
        except InvalidElementStateException:
            print("Campo 'Espécie Benefício' ausente")


    def select_sub_orgao(self, contrato: dict):
        loc_orgao = 'button[data-id="CodigoOrgao"]'
        sleep(0.5)
        try:
            print("Código Órgão:", contrato['dadosProfissionais']['codigoOrgao'])
            self.act.hover_e_clique(loc_orgao)

            loc_orgao_txt = '//*[@id="divSimulacao"]/div[5]/div[1]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_orgao_txt, contrato['dadosProfissionais']['codigoOrgao'],self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_orgao_txt, self.by.XPATH)
        except TimeoutException:
            print("Campo 'Órgão' ausente")
        except InvalidElementStateException:
            print("Campo 'Órgão' ausente")

    def select_operacao(self):
        try:
            print("Selecionando a operação: 2 - Empréstimo Consignado.")
            loc_operacao = 'button[data-id="CodigoOperacao"]'
            self.act.hover_e_clique(loc_operacao)

            loc_operacao_txt = '//*[@id="divSimulacao"]/div[1]/div[3]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_operacao_txt, "2",
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_operacao_txt, self.by.XPATH)
        except TimeoutException:
            print("Data de nascimento já preenchida")
        except InvalidElementStateException:
            print("Data de nascimento já preenchida")


    def select_tipo_operacao(self, tipo_operacao = '5'):
        try:
            try:
                self.act.clicar_elemento('//*[@id="btnOKMensagemSucesso"]', self.by.XPATH)
            except:
                pass
                
            if tipo_operacao == '5':
                print('Selecionando tipo de operação: 5 - Contrato Novo.')
            elif tipo_operacao == '3':
                print('Selecionando tipo de operação: 3 - Portabilidade.')

            loc_tipo_operacao = 'button[data-id="CodigoTipoOperacao"]'
            self.act.hover_e_clique(loc_tipo_operacao)
            #loc_tipo_operacao_txt = '//*[@id="divSimulacao"]/div[1]/div[4]/div/div/div/div/input'
            loc_tipo_operacao_txt = '/html/body/div[2]/main/div/div[2]/div/form/div[15]/div[2]/div[1]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_tipo_operacao_txt, tipo_operacao, self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_tipo_operacao_txt, self.by.XPATH)
        except TimeoutException:
            print("Data de nascimento já preenchida")
        except InvalidElementStateException:
            print("Data de nascimento já preenchida")

    def verifica_convenio_escolhido(self):
        if 'Sem resultados correspondentes' in self.act.obter_texto('//*[@id="divSimulacao"]/div[2]/div[1]/div/div/div/ul/li[2]', self.by.XPATH):
            print('Erro sistema... Reinciando...')
            return False
        return True


    def select_orgao(self, idOrgao):

        if(idOrgao == '63'):
            orgao_portal = '008525'

        print("Selecionando orgao.")
        loc_operacao = 'button[data-id="CodigoOrgao"]'
        self.act.hover_e_clique(loc_operacao)

        loc_operacao_txt = '//*[@id="divSimulacao"]/div[5]/div[1]/div/div/div/div/input'
        self.act.enviar_texto_intervalado(loc_operacao_txt, orgao_portal,self.by.XPATH, delay=randint(10, 30) / 700)
        self.act.press_enter(loc_operacao_txt, self.by.XPATH)

    def select_tabela_produto(self, id_tabela = "012890"):

        print("Selecionando a tabela do produto.")
        loc = '/html/body/div[2]/main/div/div[2]/div/form/div[17]/div[3]/div[2]/div[4]/div/div'
        sleep(0.5)
        self.act.clicar_elemento(loc, self.by.XPATH)

        loc = '/html/body/div[2]/main/div/div[2]/div/form/div[17]/div[3]/div[2]/div[4]/div/div/div/div/input'
        self.act.enviar_texto_intervalado(loc, id_tabela,self.by.XPATH, delay=randint(10, 30) / 700)
        self.act.press_enter(loc, self.by.XPATH)
        

    def input_radio_contratacao_digital(self):
        print("Tipo de contratação - Digital.")
        loc_radio = "radioDigital"
        if self.act.esta_presente(loc_radio):
            self.act.hover_e_clique(loc_radio)

    def informacao_margem(self):
        texto_margem = ''
        print("Verificando informação de margem.")
        loc_margem = '//*[@id="h2MensagemSucesso"]'
        margem = ''

        if self.act.esta_presente(loc_margem):
            texto_margem = self.act.obter_texto(loc_margem, self.by.XPATH)
            for i in texto_margem.split(): 
                if(self.isfloat(i.replace(',','.'))): 
                    margem = float(i.replace(',','.'))
                    break

            if 'POSSUI MARGEM DE EMPRÉSTIMO NEGATIVA' in texto_margem and margem < 0:
                return {'retorno':False, 'mensagem':'sem_margem', 'erro':texto_margem, 'margem': margem}
            else:
                return {'retorno' : True,'mensagem':'com_margem', 'erro':texto_margem, 'margem':margem}

    def isfloat(self, value):
      try:
        float(value)
        return True
      except ValueError:
        return False

    def campo_matricula(self, contrato:dict):
        print("Verificando checkbox da matrícula")
        loc_cb_matricula = 'button[data-id="CbxMatricula"]'
        loc_txt_cb_matricula = '//*[@id="divCbxMatricula"]/div/div/div/div/input'
        loc_matricula = "#Matricula"

        if self.act.esta_presente(loc_cb_matricula):
            try:
                print('a')
                self.act.hover_e_clique(loc_cb_matricula)
                self.act.enviar_texto_intervalado(
                    loc_txt_cb_matricula, contrato['matricula'],
                    metodo=self.by.XPATH, delay=randint(10, 30) / 700
                )
                self.act.press_enter(loc_txt_cb_matricula, self.by.XPATH)
            except TimeoutException:
                alt_txt_mat = '//*[@id="divCbxMatricula"]/div/div/div/div/input'
                print('a')
                self.act.enviar_texto_intervalado(
                    alt_txt_mat, contrato['matricula'],
                    metodo=self.by.XPATH, delay=randint(10, 30) / 700
                )
                self.act.press_enter(alt_txt_mat, self.by.XPATH)

        else:
            try:
                print('b')
                self.act.enviar_texto_intervalado(
                    loc_matricula, contrato['matricula'], delay=randint(10, 30) / 700)
            except TimeoutException:
                print("Campo matricula indisponivel.")
            except InvalidElementStateException:
                print("Campo já preenchido.")

    def input_texto_parcela(self, contrato: dict, recr=0):
        try:
            print(f"[{recr+1}]Parcela.", contrato['valorParcela'])

            if recr >= 10:
                raise Exception("Não foi possível preencher parcela")

            loc_parcela = "#ValorParcela"
            
            self.act.hover_e_clique(loc_parcela)
            #self.act.press_backspace(loc_parcela, 5)
            sleep(2)
            self.__verificar_formato_parcela(contrato)

            self.act.enviar_texto_intervalado(loc_parcela, contrato['valorParcela'], delay=0.4, clear=True)
            #self.act.press_TAB(loc_parcela)

            #if self.act.obter_valor(loc_parcela) != contrato['valorParcela']:
                #return self.input_texto_parcela(contrato, recr+1)

        except TimeoutException:
            return self.input_texto_parcela(contrato, recr + 1)

    def __verificar_formato_parcela(self, contrato: dict):
        # xx,xx => [xx, xx]
        casas_dec = len(contrato['valorParcela'].split(",")[1])

        if casas_dec < 2:
            contrato['valorParcela'] += "0"

    def input_selecionar_produto(self, produto, recr=0):
        """
        Clica no campo, habilitando o input de texto. Envia os
        caracteres. Pressiona ENTER disparando <onchange> event handler.
        """
        sleep(0.5)
        if recr > 4:
            raise Exception("")
        print("Selecionando produto")

        try:
            loc_btn = '//*[@id="divEmprestimo"]/div[4]/div[1]/div/div/button'
            loc_txt = '//*[@id="divEmprestimo"]/div[4]/div[1]/div/div/div/div/input'
            self.act.hover_e_clique(loc_btn, self.by.XPATH)
            self.act.enviar_texto_intervalado(loc_txt, produto, self.by.XPATH, delay=0.3)
            self.act.press_enter(loc_txt, self.by.XPATH)
        except TimeoutException:
            return self.input_selecionar_produto(produto, recr+1)

    def selecionar_qtd_parcelas(self, prazo: str) -> str:
        """
        Clica no campo, habilitando o input de texto. Envia os
        caracteres. Verifica se há opção disponível no select
        para aquele valor. Se não, chama recursivamente o metodo
        incrementando o prazo em 1. Se sim, pressiona ENTER disparando
        <onchange> event handler.
        """
        print("Selecionando quantidade de parcelas:", prazo)
        loc_btn = '//*[@id="divEmprestimo"]/div[4]/div[2]/div/div/button'
        loc_txt = '//*[@id="divEmprestimo"]/div[4]/div[2]/div/div/div/div/input'
        loc_sem_opcao = '//*[@id="divEmprestimo"]/div[4]/div[2]/div/div/div/ul/li[13]'

        sleep(2)

        self.act.hover_e_clique(loc_btn, self.by.XPATH)
        self.act.enviar_caracteres(loc_txt, prazo, metodo=self.by.XPATH, delay=0.09)
        
        # Há opção disponível no select?
        if self.act.esta_presente(loc_sem_opcao, self.by.XPATH):
            # Não -> repetir o método com prazo++
            self.act.hover_e_clique(loc_btn, self.by.XPATH)
            return self.selecionar_qtd_parcelas(str(int(prazo) + 1))
        else:
            # Sim -> pressionar ENTER
            self.act.press_enter(loc_txt, self.by.XPATH)
            return prazo

    def encontrar_linha_prazo_tabela(self, prazo_novo: str, contrato: dict, tipo_contrato: str) -> int:
        """
        Busca pela linha da tabela que contenha um prazo igual ao do
        contrato. Caso encontre, retorna o valor posicional da linha.
        Do contrário, retorna o valor 1, para que sejam utilizados
        os valores sugeridos pela primeira linha do sistema Olé.
        """
        loc_radios = '//*[@id="GridSimulacao"]/div/div/div/table/tbody/tr/td/label'
        qtd_produtos = self.act.quantidade_elemento(loc_radios, self.by.XPATH)

        for idx in range(1, qtd_produtos+1):
            loc_prazo = f'#idQteParcela-{idx}'
            prazo_site = self.act.obter_texto(loc_prazo)

            loc_nome_tabela = f'#idNomeProduto-{idx}'
            nome_tabela = self.act.obter_texto(loc_nome_tabela)

            print(f"Prazo site: {prazo_site} ? Prazo con: {prazo_novo}")
            
            if(tipo_contrato == 'NOVO MARGEM COMPLEMENTAR'):

                if prazo_site == prazo_novo and nome_tabela == '011596 - VD_INSS - 120 DIAS' and contrato['carenciaTabela'] == '120':
                    print(f"Prazo site: {prazo_site} == Prazo con: {prazo_novo}")
                    return idx
                    
                if prazo_site == prazo_novo and nome_tabela == '006007 - VD_INSS':
                    print(f"Prazo site: {prazo_site} == Prazo con: {prazo_novo}")
                    return idx

            else:

                if prazo_site == prazo_novo and nome_tabela == '011596 - VD_INSS - 120 DIAS' and contrato['carenciaTabela'] == '120':
                    print(f"Prazo site: {prazo_site} == Prazo con: {prazo_novo}")
                    return idx

                if prazo_site == prazo_novo and nome_tabela == '006007 - VD_INSS' and contrato['carenciaTabela'] != '120':
                    print(f"Prazo site: {prazo_site} == Prazo con: {prazo_novo}")
                    return idx
        # prazo do contrato não se aplica ao cliente, devido à idade.
        #   utilizar prazo e valor do contrato sugeridos pelo sistema.
        return 1

    def extrair_dados_prazo_valor_emprestimo(self, idx_prazo: int):
        prazo_valor_emprestimo: dict = {}

        loc_valor = f'#idValorSolicitado-{idx_prazo}'
        loc_prazo = f'#idQteParcela-{idx_prazo}'

        prazo_valor_emprestimo['valorContrato'] = self.act.obter_texto(loc_valor)
        prazo_valor_emprestimo['prazo'] = self.act.obter_texto(loc_prazo)
        print(prazo_valor_emprestimo)
        return prazo_valor_emprestimo

    def botao_calcular_emprestimo(self, rec=0):
        print("Clicando em 'Calcular Empréstimo --.'")
        loc_calcular = "#btnCalcularEmprestimo"
        self.act.hover_e_clique(loc_calcular)
        
        self.loading()
        loc_tabela = '//*[@id="GridSimulacao"]/div/div/div'

        if verificar_erros(self.act, self.by):
            return

        loc_valor = False
        try:
            loc_valor = self.act.esta_presente('//*[@id="h2MensagemSucesso"]')
            if loc_valor:
                self.act.hover_e_clique('#btnOKMensagemSucesso')
                return {'erro' : 'VALOR DA PARCELA NÃO PODE ULTRAPASSAR O VALOR LIMITE'}

        except:
            pass

        if not self.act.esta_presente(loc_tabela):
            if rec >= 2:
                return False
            sleep(3)
            if not self.act.esta_presente(loc_tabela):
                return self.botao_calcular_emprestimo(rec+1)

    def check_box_produto(self, idx):
        try:
            print("Selecionando produto relativo a 'Nova Proposta'")
            print(f'input#gridretorno-{idx}')
            self.act.forcar_preenchimento_cb(f'input#gridretorno-{idx}')
        except TimeoutException:
            print("Produto não encontrado.")

    def extrair_valor_prazo_proposta(self, contrato: dict) -> dict:
        print("Atualizando valor e prazo do contrato.")
        grid_opt = selecionar_prazo(contrato, self.sh)

        if not grid_opt:
            print('Prazo com valor nulo no contrato')
            self.uconecte.atualizar_contrato(
                contrato['codigoContrato'],
                {
                    'erro': r'O atributo obrigatório Número de Prestações não foi informado.',
                    'mensagem': 'Reprovado a Conferir',
                    'observacoes': 'Prazo com valor nulo no contrato.'
                }
            )
            raise Exception("Abortando inserção. Contrato atualizado: Reprovado a Conferir.")

        loc_val_solicitado = "#idValorSolicitado-" + grid_opt
        loc_prazo = '#idQteParcela-' + grid_opt

        self.atualizacoes['valorContrato'] = self.act.obter_texto(loc_val_solicitado)
        self.atualizacoes['prazo'] = self.act.obter_texto(loc_prazo)

        return self.atualizacoes

    def botao_prosseguir_proposta(self):
        print("Prosseguindo com proposta.")
        loc_prosseguir = "#btnProsseguirEmprestimo"
        self.act.hover_e_clique(loc_prosseguir)
    
    def botao_prosseguir_proposta_refin(self):
        print('Prosseguindo com a proposta')
        self.act.hover_e_clique('//*[@id="btnProsseguir"]', self.by.XPATH) 

    def botao_prosseguir_proposta_portabilidade(self):
        print("Prosseguindo com proposta.")
        try:
            loc_prosseguir = "#btnProsseguirEmprestimo"
            self.act.hover_e_clique(loc_prosseguir)
        except:
            loc_prosseguir = "#btnProsseguir"
            self.act.hover_e_clique(loc_prosseguir)
        self.loading()

    def clicar_voltar_botao_erro_inesperado(self):
        loc = '//*[@id="erro"]/div/div/div/button'
        try:
            self.act.hover_e_clique(loc, self.by.XPATH, pause=0.1)
            print("Erro inesperado -> clicando em voltar")
            return True
        except TimeoutException:
            return False
    
    def loading(self):
        while True:
            try:
                self.act.obter_texto('//*[@id="divLoading"]/div/div/center[1]/h1', self.by.XPATH)
            except:
                break
            sleep(1)

    def loading_finalizar(self):
        while True:
            try:
                self.act.obter_texto('//*[@id="divLoading"]/div/div/center[1]/h1', self.by.XPATH)
            except:
                break
            sleep(1)
    
    def extrair_dados_prazo_valor_refinanciamento(self, idx_prazo):
        prazo_valor_emprestimo: dict = {}
        loc_valor = f'#idValorLiberado-{idx_prazo}'
        loc_prazo = f'#idQteParcela-{idx_prazo}'
        prazo_valor_emprestimo['valorContrato'] = self.act.obter_texto(loc_valor).replace(' (atualizado)', '')
        prazo_valor_emprestimo['prazo'] = self.act.obter_texto(loc_prazo)
        return prazo_valor_emprestimo

    def escolher_parcela(self, contrato):
        parcela_ativa = True
        self.loading()
        try:
            sleep(3)
            self.act.clicar_elemento('//*[@id="btnOKMensagemSucesso"]', self.by.XPATH)
        except:
            pass

        try:
            quantidade_refinanciamentos = int(self.act.quantidade_elemento('.pmd-radio')) + 2
        except:
            quantidade_refinanciamentos = 0
        
        posicao_check = 1
        for i in range(1, quantidade_refinanciamentos, 2):
            try:
                valor = self.act.obter_texto(f'/html/body/div[2]/main/div/div[2]/div/form/div[17]/div[2]/div/div/div[2]/div/div/table/tbody/tr[{i}]/td[6]', self.by.XPATH) 
            except: 
                valor = 0  
                pass

            if contrato['valorParcela'] == valor:
                self.act.clicar_elemento(f'//*[@id="idCheckBox-{posicao_check}"]', self.by.XPATH)
                parcela_ativa = True
                break   
            else:
                parcela_ativa = False
                posicao_check += 1
                continue

            if(parcela_ativa == True):
                break

        return parcela_ativa
   
    def realizar_consulta_refinanciamento(self, contrato):

        self.loading()
        self.act.clicar_elemento('//*[@id="btnCalcularRefin"]', self.by.XPATH) # Calcular
        self.loading()

        try:
            mensagem_alerta = self.act.obter_texto('//*[@id="divMensagemErro"]', self.by.XPATH)    
            if('Selecione um ou mais contratos para Refinanciamento' in mensagem_alerta):
                parcela_ativa = self.escolher_parcela(contrato) 
                if(parcela_ativa == True):
                    self.act.clicar_elemento('//*[@id="btnCalcularRefin"]', self.by.XPATH) # Calcular 
                    self.loading()
        except:
            pass

        #Seleciona a tabela do orgao de acordo com o perfil 
        if('especieBeneficio' in contrato and contrato['especieBeneficio'] in ['87','88']):
            
            self.select_tabela_produto("012890")
            self.act.clicar_elemento('//*[@id="btnCalcularRefin"]', self.by.XPATH) # Calcular 
            self.loading()

        dados = ''

        try:            
            dados = self.extrair_dados_prazo_valor_refinanciamento(1)
        except:
            self.escolher_parcela(contrato)
            self.act.clicar_elemento('//*[@id="btnCalcularRefin"]', self.by.XPATH)
            self.loading()
            alerta = ""
            try:
                alerta = self.act.obter_texto('//*[@id="divRefin"]/div[4]/div[1]', self.by.XPATH)
                if "NÃO EXISTEM SIMULAÇÕES DE REFINANCIAMENTO DISPONÍVEIS" in alerta:
                    return {'retorno' : False ,'mensagem':'Refinanciamento não disponível'}

            except:
                dados = self.extrair_dados_prazo_valor_refinanciamento(1)
                pass

        self.loading()

        self.act.clicar_elemento('//*[@id="btnProsseguirEmprestimo"]', self.by.XPATH) # Prosseguir
        self.loading()
        try:            
            if 'atualizar valores' in self.act.obter_texto('//*[@id="popUpRefinText"]', self.by.XPATH):
                self.act.clicar_elemento('//*[@id="btnFecharPopUpCalculoRefin"]', self.by.XPATH)
                dados = self.extrair_dados_prazo_valor_refinanciamento(1)
                self.act.clicar_elemento('//*[@id="btnProsseguirEmprestimo"]', self.by.XPATH) # Prosseguir
                self.loading()
        except:
            pass

        return dados

class AbaDadosCliente(AutoGUI):
    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver: object = chrome_driver
        self.uconecte: object = Uconecte()

        self.t_max: float = 2
        self.t_min: float = 1
        self.t_sleep = 0.5
        self.act.time_out = 2

    def input_texto_cpf(self, contrato: dict):
        loc_cpf = "input#CPF"
        if not self.act.obter_atributo(loc_cpf, 'readonly'):
            self.act.hover_e_clique(loc_cpf)
            self.act.enviar_texto_intervalado(
                loc_cpf, contrato['cpf'], delay=randint(10, 30) / 200)

    def input_texto_nome(self, contrato: dict):
        loc_nome = "#Nome"
        # campo 'nome' disponível? se sim, preencher
        try:
            print("Nome:", contrato['nome'])
            self.act.enviar_texto_intervalado(
                loc_nome, contrato['nome'], delay=randint(10, 30) / 700)
        except InvalidElementStateException:
            print("Campo já preenchido")
        except TimeoutException:
            print("Campo indisponível")

    def input_texto_email(self,contrato,forcar_email_web_admin = False):
        loc_email = '#Email'
        print('Email...')

        if(forcar_email_web_admin):
            print('Digitando email web_admin')
            self.act.enviar_texto_intervalado(loc_email, contrato['email'], delay=0.2)
        else:      

            if self.act.obter_valor(loc_email) == '' or '@uconecte' in self.act.obter_valor(loc_email):
                if(contrato['email'] == 'emprestimo@uconecte.me'):
                    rand_email = str(randint(21, 89))
                    nome_cliente = contrato['nome'] 
                    nome_email = nome_cliente.split(" ")[0].upper()+'.'+nome_cliente.split(" ")[-1].upper()
                    servidores_email = ["gmail.com"]
                    self.act.enviar_texto_intervalado(loc_email, f'{nome_email}.{rand_email}@{servidores_email[0].upper()}', delay=randint(10, 30) / 700)

                else:
                    self.act.enviar_texto_intervalado(loc_email, contrato['email'], delay=0.2)

    def input_text_ddd_celular(self, contrato: dict):
        ddd, celular = contrato['dddCelular'], contrato['celular']
        loc_ddd, loc_cel = "#DDDTelefoneCelular", "#TelefoneCelular"

        print(f"Celular: ({ddd}) {celular}")

        self.act.hover_e_clique(loc_ddd)
        self.act.press_backspace(loc_ddd, loop=3, end=True)
        self.act.enviar_texto_intervalado(loc_ddd, ddd, delay=0.5, clear=False)

        self.act.hover_e_clique(loc_cel)
        self.act.enviar_texto_intervalado(loc_cel, celular, delay=0.3, clear=False)
        self.act.hover_e_clique(loc_cel)

    def input_texto_renda_bruta(self, contrato: dict):
        loc_renda = "#RendaBruta"
        loc_patrimonio = "#ValorPatrimonio"
        val_renda = self.act.obter_texto(loc_renda)
        print("Verificando renda bruta:", val_renda)
        if validar_valor_renda(val_renda):
            self.act.hover_e_clique(loc_renda)
            renda = '1045,00'
            if(contrato['renda']):
                renda = contrato['renda']

            self.act.enviar_texto_intervalado(loc_renda, renda, delay=randint(10, 30) / 700)
            self.act.enviar_texto_intervalado(loc_patrimonio, '0,00', delay=randint(10, 30) / 700)

    def input_texto_nome_mae(self, contrato: dict):
        print('Nome da mãe:', contrato['nomeMae'])
        loc_mae = '#NomeMae'
        self.act.hover_e_clique(loc_mae)
        self.act.enviar_texto_intervalado(
            loc_mae, contrato['nomeMae'], delay=randint(10, 30) / 700)

    def input_texto_rg(self, contrato: dict):
        print("Nº RG:", contrato['identidade'])
        loc_rg = "#NumeroRg"
        self.act.hover_e_clique(loc_rg)
        self.act.enviar_texto_intervalado(loc_rg, contrato['identidade'],
                                          delay=randint(6, 16) / 200)

    def input_radio_sms(self):
        print("Selecionar comunicação por SMS.")
        loc_com_sms = '#ComunicacaoSMSEmail'
        self.act.hover_e_clique(loc_com_sms)

    def input_texto_cep(self, contrato: dict):
        print("CEP do site != CEP do contrato? ", end='')
        loc_cep = "#CEP"
        val_cep = self.act.obter_texto(loc_cep)
        check_cep = re.sub(r'\D', '', val_cep) != contrato['cep']
        print(f'Site: {val_cep} != Contrato: {contrato["cep"]}: {check_cep}')

        val_cep = val_cep.replace(".", "").replace("-", "")

        if val_cep.strip() != contrato['cep']:
            print("Utilizando CEP do contrato.", contrato['cep'])
            self.act.hover_e_clique(loc_cep)
            self.act.enviar_texto_intervalado(loc_cep, contrato['cep'],
                                              delay=0.7, clear=False)  # blur
            self.act.hover_e_clique(loc_cep)

    def select_tipo_uf(self, contrato: dict):
        print("Verificando se campo TIPO UF está preenchido.")
        loc_tipo_uf = "button[data-id='TipoUF']"
        try:
            print("TIPO UF:", contrato['uf'])
            # Clicar no elemento e habilitar txt input
            self.act.hover_e_clique(loc_tipo_uf)

            if self.act.obter_atributo(loc_tipo_uf, 'title').lower() == 'selecione...':
                self.act.hover_e_clique(loc_tipo_uf)

            elif not self.act.obter_atributo(loc_tipo_uf, 'title').lower() == contrato['uf']:
                self.act.hover_e_clique(loc_tipo_uf)
                # Preencher input e pressionar ENTER
                loc_tipoUFtxt = ('//*[@id="form_Pagina"]/div[7]/div/div/div/'
                                 'div/div[1]/div[3]/div/div/div/div/input')
                self.act.enviar_texto_intervalado(loc_tipoUFtxt, contrato['uf'],
                                                  self.by.XPATH, delay=randint(10, 30) / 700)
                self.act.press_enter(loc_tipoUFtxt, self.by.XPATH)
            else:
                print("Tipo UF já foi preenchido")
        except TimeoutException:
            print("Campo tipo UF indisponível.")
        except InvalidElementStateException:
            print("Tipo UF já preenchido")

    def select_cidade(self, contrato: dict, recr: int = 0):
        loc_cidade = 'button[data-id="Cidade"]'
        print("Verificando se campo cidade está disponível.")
        try:
            # Clicar no elemento e habilitar txt input
            self.act.hover_e_clique(loc_cidade)
            # Preencher input e pressionar ENTER
            loc_cidade_txt = ('//*[@id="form_Pagina"]/div[7]/div/div/div/'
                              'div/div[1]/div[4]/div/div/div/div/input')
            self.act.enviar_texto_intervalado(loc_cidade_txt, contrato['cidade'],
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_cidade_txt, self.by.XPATH)

            sleep(1)

        except TimeoutException:
            print("Campo cidade já preenchido.")

            if recr > 2:
                return

            loc_selecione = ('//*[@id="form_Pagina"]/div[7]/div/div/div/div/'
                             'div[1]/div[4]/div/div/button/span[1]')
            if "Selecione..." in self.act.obter_texto(loc_selecione, self.by.XPATH):
                return self.select_cidade(contrato, recr+1)
        except InvalidElementStateException:
            print("Campo cidade já preenchido.")

            if recr > 2:
                return

            loc_selecione = ('//*[@id="form_Pagina"]/div[7]/div/div/div/div/'
                             'div[1]/div[4]/div/div/button/span[1]')
            if "Selecione..." in self.act.obter_texto(loc_selecione, self.by.XPATH):
                self.select_cidade(contrato, recr+1)

    def input_texto_ncasa(self, contrato: dict):
        try:
            print("Preenchendo Nº Casa:", contrato['numeroCasa'])
            loc_ncasa = "#Numero"

            self.act.hover_e_clique(loc_ncasa)
            self.act.enviar_texto_intervalado(loc_ncasa, contrato['numeroCasa'],
                                              delay=randint(10, 30) / 700)
            self.act.hover_e_clique(loc_ncasa)
        except TimeoutException:
            print("Campo já preenchido.")
        except InvalidElementStateException:
            print("Numero da casa já preenchido.")

    def select_tipo_logradouro(self):
        try:
            print("Preenchendo tipo logradouro: RUA")
            loc_tipo_logradouro = 'button[data-id="TipoLogradouro"]'
            # Clicar no elemento e habilitar txt input
            self.act.hover_e_clique(loc_tipo_logradouro)
            # Preencher input e pressionar ENTER
            loc_logradouro_txt = '//*[@id="divTipoDeLogradouro"]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_logradouro_txt, 'RUA',
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_logradouro_txt, self.by.XPATH)
        except TimeoutException:
            print("Campo já preenchido.")

        except InvalidElementStateException:
            print("Campo já preenchido")

    def input_texto_logradouro(self, contrato: dict):
        print("Preenchendo logradouro.")
        loc_logradouro = 'input#Logradouro'
        try:
            print("Preenchendo logradouro", contrato['logradouro'])
            self.act.hover_e_clique(loc_logradouro)
            self.act.enviar_texto_intervalado(
                loc_logradouro, contrato['logradouro'], delay=0.001
            )
        except TimeoutException:
            print("Campo já preenchido.")
        except InvalidElementStateException:
            print("Campo já preenchido")

    def input_texto_complemento(self, contrato: dict):
        print("Preenchendo complemento:", contrato['complemento'])
        loc_complemento = "#Complemento"
        try:
            self.act.hover_e_clique(loc_complemento)
            self.act.enviar_texto_intervalado(
                loc_complemento, contrato['complemento'],
                delay=randint(10, 30) / 700
            )
        except TimeoutException:
            print("Campo já preenchido.")
        except InvalidElementStateException:
            print("Campo já preenchido")

    def input_texto_bairro(self, contrato: dict):
        loc_bairro = '#Bairro'
        try:
            print("Preenchendo bairro:", contrato['bairro'])
            self.act.enviar_texto_intervalado(
                loc_bairro, contrato['bairro'].title(), delay=0.001)
            self.act.press_TAB(loc_bairro)
        except InvalidElementStateException:
            print("Campo já preenchido")
        except TimeoutException:
            print("Campo já preenchido.")
        sleep(self.t_sleep)
        print("Clicando prosseguir.")

    def botao_prosseguir(self):
        print("Clicando prosseguir.")
        loc_prosseguir = 'input#btnProsseguir'

        sleep(self.t_sleep)
        self.act.hover_e_clique(loc_prosseguir)

    def div_erro_cep(self):
        loc = '#divErroCep'
        loc_close = '//*[@id="divErroCep"]/button'
        try:
            txt = self.act.obter_texto(loc)
            print(txt.replace('×', '').replace('\n', '').strip())
            if txt == 'x':
                self.act.clicar_elemento(loc_close, self.by.XPATH)
            else:
                return txt.replace('×', '').replace('\n', '').strip()
        except TimeoutException:
            print("div ErroCep não foi aberto.")

    def div_erro_email(self):
        loc = '//*[@id="divErro"]/ul/li'        
        try:
            if('O e-mail informado é inválido' in self.act.obter_texto(loc, self.by.XPATH)):
                return True
        except TimeoutException:
            return False


class AbaDadosOperacao(AutoGUI):
    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver: object = chrome_driver
        self.uconecte: object = Uconecte()

        self.t_max: float = 2
        self.t_min: float = 1
        self.t_sleep = 0.5

        self.atualizacoes: dict = {}
        self.act.time_out = 2

    def input_texto_cpf_vendedor(self):
        print("Preenchendo CPF Vendedor.")

        try:
            loc_cpf_vend = "#CPFVendedor"
            self.act.hover_e_clique(loc_cpf_vend)
            self.act.enviar_texto_intervalado(
                loc_cpf_vend, "035.071.796-60",
                delay=randint(10, 30) / 700, clear=False)
        except InvalidElementStateException:
            print("Campo já preenchido")
        except TimeoutException:
            print("Campo já preenchido.")

    def input_texto_codigo_margem(self):
        print("Preenchendo Codigo Reserva de margem.")

        try:
            loc_cod_margem = "#CodigoReservaMargem"
            self.act.hover_e_clique(loc_cod_margem)
            self.act.enviar_texto_intervalado(
                loc_cod_margem, "1236544",
                delay=randint(10, 30) / 700, clear=False)
        except InvalidElementStateException:
            print("Campo já preenchido")
        except TimeoutException:
            print("Campo já preenchido.")

    def select_tipo_conta_corrente(self, contrato, rec=0):
        print("Selecionando tipo de conta corrente.", contrato['tipoConta'])
        try:
            tipo_conta = select_tipo_conta(contrato['tipoConta'])
            loc_tipo_conta = '//*[@id="tipoContaPanel"]/div/button'
            loc_option = f'//span[text()="{tipo_conta}"]'

            try:
                self.act.hover_e_clique(loc_tipo_conta, self.by.XPATH)
            except:
                loc_tipo_conta = '//*[@id="tipoContaPanel"]/div/div/button'
                sleep(2)
                self.act.hover_e_clique(loc_tipo_conta, self.by.XPATH)

            self.act.hover_e_clique(loc_option, self.by.XPATH)

            return 0
        except InvalidElementStateException:
            print("Campo já preenchido.")
        except TimeoutException:
            if rec > 4:
                raise TimeoutException
            return self.select_tipo_conta_corrente(contrato, rec+1)

    def input_texto_nbanco(self, contrato: dict):
        print("Preenchendo Nº do Banco.", contrato['numeroBanco'])
        loc_banco = 'button[data-id="NumeroBanco"]'
        try:
            try:
                # Clicar no elemento e habilitar txt input
                self.act.hover_e_clique(loc_banco)
                # Preencher input e pressionar ENTER
                loc_banco_txt = '//*[@id="dados-liberacao-001"]/div/div[2]/div/div/div/input'
                try:                    
                    #mudanca de input
                    self.act.enviar_texto_intervalado(loc_banco_txt, contrato['numeroBanco'],self.by.XPATH, delay=randint(10, 30) / 700)
                except:
                    loc_banco_txt = '//*[@id="dados-liberacao-001"]/div/div[2]/div/div/div/div/input'
                    self.act.enviar_texto_intervalado(loc_banco_txt, contrato['numeroBanco'],self.by.XPATH, delay=randint(10, 30) / 700)

                self.act.press_enter(loc_banco_txt, self.by.XPATH)
            except TimeoutException as e:
                print(e.stacktrace)
        except InvalidElementStateException:
            print("Campo já preenchido")

    def select_agencia(self, contrato:dict):
        print("Selecionando Agência")
        loc_agencia = ('//*[@id="select2-NumeroAgencia-container"]')
        try:
            try:
                # Clicar no elemento e habilitar txt input
                self.act.hover_e_clique(loc_agencia, self.by.XPATH)
                # Preencher input e pressionar ENTER
                loc_ag_txt = '/html/body/span/span/span[1]/input'
                self.act.enviar_texto_intervalado(
                    loc_ag_txt, contrato['agencia'],
                    self.by.XPATH, delay=randint(10, 30) / 700
                )
                sleep(0.5)
                self.act.press_enter(loc_ag_txt, self.by.XPATH)
                sleep(0.5)
                self.act.press_enter(loc_ag_txt, self.by.XPATH)
            except TimeoutException as e:
                print(e)
        except InvalidElementStateException as e:
            print("Campo já preenchido")

    def input_texto_dv_agencia(self, contrato: dict):
        try:
            print("DV agência.")
            loc_digi_ver = 'input#DigitoVerificadorAgencia'
            self.act.hover_e_clique(loc_digi_ver)
            self.act.enviar_texto_intervalado(loc_digi_ver, '0', delay=randint(10, 30) / 700)
        except InvalidElementStateException as e:
            print("Campo já preenchido")
        except TimeoutException as e:
            print("Campo indisponível")
        try:
            print("Numero da conta.")
            loc_n_conta = "#NumeroConta"
            self.act.hover_e_clique(loc_n_conta)
            self.act.enviar_texto_intervalado(
                loc_n_conta, contrato['numeroConta'],
                delay=randint(10, 30) / 700
            )
        except InvalidElementStateException as e:
            print("Campo já preenchido")
        except TimeoutException as e:
            print("Campo indisponível")

    def input_texto_dv_conta(self, contrato: dict):
        print("DV conta.")
        loc_dv_conta = '#DigitoVerificadorConta'
        self.act.hover_e_clique(loc_dv_conta)
        self.act.enviar_texto_intervalado(
            loc_dv_conta, contrato['digitoConta'],
            delay=randint(10, 30) / 700
        )

    def botao_prosseguir_aba_resumo(self):
        loc_btn_prosseguir = 'input#btnProsseguir'
        sleep(self.t_sleep)
        self.act.hover_e_clique(loc_btn_prosseguir)

    def aguardar_aba_dados_operacao(self) -> bool:
        curr_url = self.chrome_driver.current_url

        print("Aguardando abertura da aba 'Dados da Operação.")
        sleep(4)

        if 'DadosOperacao' in curr_url:
            return True
        else:
            return False


class AbaResumo(AutoGUI):

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver: object = chrome_driver
        self.uconecte: object = Uconecte()

        self.t_max: float = 2
        self.t_min: float = 1
        self.t_sleep = 0.5

        self.atualizacoes: dict = {}
        self.act.time_out = 2

    def botao_finalizar_emprestimo(self, recr: int=0) -> bool:
        try:
            print('Botão finalizar empréstimo')
            loc_finalizar = 'input#btnFinalizarEmprestimo'
            self.act.hover_e_clique(loc_finalizar)
            return True
        except TimeoutException:
            if recr > 20:
                raise Exception("Não foi possivel finalizar emprestimo")

            return self.botao_finalizar_emprestimo(recr+1)

    def botao_finalizar_portabilidade(self, recr: int=0):
        try:
            loc_proposta_finalizada = '//*[@id="modal-finalizar"]/div/div/div[1]/div/h2'
            try:
                finalizada = self.act.obter_texto(loc_proposta_finalizada, self.by.XPATH)
                if('PROPOSTA FINALIZADA' in finalizada):
                    print('Confirmacao de modal de proposta finalizada...')
                    return True
            except:
                print('Botão finalizar portabilidade...')
                loc_finalizar = '//*[@id="btnFinalizarPortabilidadeComComplemento"]'
                self.act.clicar_elemento(loc_finalizar, self.by.XPATH)

        except TimeoutException:
            if recr > 50:
                raise Exception("Não foi possivel finalizar refinanciamento")
            sleep(2)
            return self.botao_finalizar_portabilidade(recr+1)
        except:
            pass

    def botao_finalizar_refin(self, recr: int=0):
        try:
            loc_proposta_finalizada = '//*[@id="modal-finalizar"]/div/div/div[1]/div/h2'
            try:
                finalizada = self.act.obter_texto(loc_proposta_finalizada, self.by.XPATH)
                if('PROPOSTA FINALIZADA' in finalizada):
                    print('Confirmacao de modal de proposta finalizada...')
                    return True
            except:
                print('Botão finalizar refinanciamento...')
                loc_finalizar = '//*[@id="btnFinalizarRefin"]'
                self.act.clicar_elemento(loc_finalizar, self.by.XPATH)

        except TimeoutException:
            if recr > 50:
                raise Exception("Não foi possivel finalizar refinanciamento")
            sleep(2)
            return self.botao_finalizar_refin(recr+1)
        except:
            pass

    def botao_concluir_emprestimo(self, recr: int=0) -> bool:
        try:
            print('Botão concluir Empréstimo')
            loc_concluir = "#btnConcluirEmprestimo"
            self.act.hover_e_clique(loc_concluir)
            return True
        except TimeoutException:
            if recr > 20:
                return False

            return self.botao_concluir_emprestimo(recr+1)

    def modal_cancelar_cartao_com_permissao(self):
        try:
            sleep(self.t_sleep)
            loc_cartao = '#btnCancelarCartaoComPermissao'
            print('Botão Cancelar Cartão com permissão')
            self.act.hover_e_clique(loc_cartao)
            sleep(0.5)
            self.act.hover_e_clique(loc_cartao)

        except TimeoutException:
            print("Modal 'Contratar Cartão' não foi aberto.")

    def erro_pagina_503(self):
        loc_503 = '//*[@id="main-message"]/h1/span'
        if self.act.esta_presente(loc_503, self.by.XPATH):
            raise Exception("ERRO: HTTP STATUS 503")

    def final_insercao(self, recr: int=0):
        try:
            loc_finalizar = '//*[@id="modal-finalizar"]/div/div/div[1]'
            self.act.esta_presente(loc_finalizar, self.by.XPATH)
            return True
        except TimeoutException:
            if recr > 20:
                return False

            return self.final_insercao(recr+1)

        return 

    def loading(self):
        while True:
            try:
                self.act.obter_texto('//*[@id="divLoading"]/div/div/center[1]/h1', self.by.XPATH)
            except:
                break
            sleep(1)

    def loading_finalizar(self):
        while True:
            try:
                self.act.obter_texto('//*[@id="divLoading"]/div/div/center[1]/h1', self.by.XPATH)
            except:
                break
            sleep(1)

