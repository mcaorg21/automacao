from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import time
import requests
import re,pdb

import pdfkit
import base64


from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.uconecte import Uconecte
from sites.core.helpers import identificar_erro_robo
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.baseRobos.data_handler import DataHandler
import PATHS
from selenium.webdriver import Chrome
from sites.baseRobos.core.decorators import ApenasHorarioComercial, AguardarHorarioComercial
from sites.baseRobos.core.Exceptions import ForaHorarioComercialError

from selenium.webdriver.common.by import By


HORARIO_COMERCIAL = 8, 20


class OleConsignado:

    id_fila_gerar = 23

    def __init__(self, driver: Chrome=False):
        self.caminho_base = PATHS.project_path()
        self.caminho_anexos: Path = Path(self.caminho_base, 'oleConsignado', 'anexos')
        self.atualizacoes = {}
        self.codigo_contrato = ""
        self.id_robo = 4
        self.id_banco = 123
        self.api_key = "f689f1e12a0399fba803cb2365fc362f"
        self.driver = driver
        self.path_wkhtmltopdf = PATHS.WKHTML2PDF_BIN
        self.config = pdfkit.configuration(wkhtmltopdf=self.path_wkhtmltopdf)
        self.selenium = SeleniumHelper(self.driver)
        self.uconecte = Uconecte(id_banco=self.id_banco)
        self.act = SeleniumActions(self.driver)
        self.contrato =False
        self.log = DataHandler()

    @classmethod
    @AguardarHorarioComercial(*HORARIO_COMERCIAL)
    def iniciar_horario_comercial(cls, driver: Chrome):
        run = OleConsignado(driver)
        try:
            run.gerar_contratos()
        except ForaHorarioComercialError as e:
            print(e.msg)
            run.driver.quit()

        return run

    # def login_sistema(self):
    #     self.driver.get('https://ola.oleconsignado.com.br/')

    #     self.driver.execute_script("""$('#Login').val('CCASTROLEWE')""")
    #     self.driver.execute_script("""$('#Senha').val('marcelo31')""")

    #     time.sleep(5)
    #     self.selenium.clicar_elemento("#botaoAcessar")

    #     time.sleep(5)
    #     if self.driver.execute_script("return $('.alert-danger\\:visible').length") == 1:
    #         self.login_sistema()

    def buscar_contratos_gerar(self):
        request_contratos_a_gerar = requests.get(
            'https://uconecte.me/api/v1/contratos/status/gerar?key={}&consulta=gerar&banco=ole'.format(
                self.api_key))

        if request_contratos_a_gerar.status_code != 200:
            input('Olé Consignado Error - Não foi possível buscar os contratos')

        contratos = request_contratos_a_gerar.json()['contratos']

        if len(contratos) == 0:
            print('Nenhum contrato na fila gerar contrato! Trocando de fila...')
            return []

        return contratos

    def atualizar_contrato(self, codigo_contrato, dados):
        request_atualizar_contrato = requests.put(
            'https://uconecte.me/api/v1/contratos/%s?key=f689f1e12a0399fba803cb2365fc362f' % (
                codigo_contrato),
            data=dados)
        
        if request_atualizar_contrato.status_code == 200:
            print('contrato atualizado')
        else:
            print(request_atualizar_contrato.text)
            print('Contrato nao atualizado linha 109 ole_consignado')

    @ApenasHorarioComercial(*HORARIO_COMERCIAL)
    def gerar_contratos(self):
        print('Trabalhando na fila de geração de contratos')
        contratos = self.buscar_contratos_gerar()

        for cnt, contrato in enumerate(contratos, 1):
            print(f"[{cnt}]Fila Gerar Contratos")
            self.contrato = contrato
            self.log.api_iniciar_log_robo(
                idRobo=self.id_fila_gerar,
                idContrato=self.contrato['codigo_con']
            )
            definir_nome_robo('Ole Insercao Gerar')
            try:
                if(self.preencher_pagina_consulta()):
                    self.comparar_dados_contrato()
                    time.sleep(2)
                    pdf_base_64 = self.baixar_pdf_contrato()

                    self.envia_pdf_contrato(pdf_base_64)

                    self.log.api_registrar_log_robo(
                        log="Contrato gerado com sucesso.",
                        status=2
                    )
                else:
                    print('Contrato não gerado...')
                    continue
            except Exception as e:
                print(e)
                self.log.api_registrar_log_robo(
                    log=f"ERRO: {e}",
                    status=0
                )
                identificar_erro_robo()

    def preencher_pagina_consulta(self):
        time.sleep(5)
        self.driver.get('https://ola.oleconsignado.com.br/ConsultaDeProposta/Index')
        print("Trabalhando no contrato %s" % (self.contrato['codigo_con']))

        # if(self.contrato['ade'] and self.contrato['ade'] != 0):
        #     if(self.contrato['tipo'] == 'REFINANCIAMENTO'):
        #         url = f"https://ola.oleconsignado.com.br/RefinPropostaDetalhe/Index/870931428/CONSULTA/"
        #     else:
        #         url = f"https://ola.oleconsignado.com.br/EmprestimoPropostaDetalhe/Index/{self.contrato['ade']}/CONSULTA/"  

        #     self.driver.get(url)
        # else:
        self.selenium.atribuir_valor_campo_jquery("#CPF", self.contrato['cpf_cli'])
        self.selenium.clicar_elemento('#btnPesquisar')
        
        time.sleep(5)
        try:
            alerta = self.act.obter_texto('//*[@id="divMensagemErro"]/ul/li', By.XPATH)
            if 'Nenhuma proposta encontrada' in alerta:
                self.atualizar_contrato(self.contrato['codigo_con'], {'mensagem': 'Erro ao procurar contrato',
                                                                        'erro': "Verificar se contrato foi inserido",
                                                                        'observacao': "Não encontrou contrato pra gerar no sistema. Verificar manualmente"})
            return False
        except:
            pass

        self.verificar_loading()

        return True

        

    def comparar_dados_contrato(self):
        links_contratos = self.driver.find_elements_by_css_selector('#tabelaDePropostas tbody tr a')
        links = list(map(lambda proposta: proposta.get_attribute('href'), links_contratos))
        
        rec = 0
        rec_port = 0
        for link in links:
            rec_port += 1
            try:
                self.driver.get(link)
            except:
                continue

            if(self.contrato['tipo'] == 'REFINANCIAMENTO DA PORTABILIDADE'):
                self.contrato['ade'] = self.selenium.verificar_texto_campo_jquery('p:contains("Número da Proposta")').split('Número')[2]
                self.contrato['ade'] = re.sub(r'\D', '', self.contrato['ade'])
            else:
                self.contrato['ade'] = self.selenium.verificar_texto_campo_jquery('p:contains("Número da Proposta")')
                self.contrato['ade'] = re.sub(r'\D', '', self.contrato['ade'])

            if self.contrato['ade'] == "":
                continue
                #raise ErrorOleException(message="ADE não foi gerada, esperando a próxima interação")

            if(self.contrato['tipo'] == 'PORTABILIDADE' or self.contrato['tipo'] == 'REFINANCIAMENTO DA PORTABILIDADE'):
                valor_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("Valor Liberado ao Cliente (R$):")')
                texto_tipo = 1

                if(valor_encontrado == ''):
                    texto_tipo = 2
                    valor_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("Valor liberado ao cliente(R$):")')   

                if(valor_encontrado == ''):
                    continue

                if texto_tipo == 1:
                    self.valor_proposta_ole = float(valor_encontrado.replace('Valor Liberado ao Cliente (R$): ','').strip().replace('.','').replace(',','.'))
                else:
                    self.valor_proposta_ole = float(valor_encontrado.replace('Valor liberado ao cliente(R$): ','').strip().replace('.','').replace(',','.'))

                valor_proposta_wa = float(self.contrato['valor_con'].replace('.','').replace(',','.'))
                produto = self.selenium.verificar_texto_campo_jquery('p:contains("Produto")')

                if(self.contrato['tipo'] == 'PORTABILIDADE'):
                    valor_total = self.selenium.verificar_texto_campo_jquery('p:contains("Valor Retido (R$):")')
                    self.valor_proposta_ole = float(valor_total.replace('Valor Retido (R$): ','').strip().replace('.','').replace(',','.'))
                    if self.valor_proposta_ole == valor_proposta_wa:
                        return True
                
                if 'PORTABILIDADE' in produto:
                    if self.valor_proposta_ole == valor_proposta_wa:
                        return True

                if(len(links) == rec_port):
                    raise ErrorOleException('ADE não encontrada')
                else:
                    continue


            else:
                cpf_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("Número CPF:")')
                valor_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("Valor liberado (R$):")')
                try:
                    self.valor_proposta_ole = float(valor_encontrado.replace('Valor liberado (R$): ','').strip().replace('.','').replace(',','.'))
                except:
                    self.valor_proposta_ole = ''
                    pass

                if(self.contrato['tipo'] == 'REFINANCIAMENTO' and self.valor_proposta_ole  == ''):
                    valor_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("Valor liberado ao cliente(R$):")')
                    self.valor_proposta_ole = float(valor_encontrado.replace('Valor liberado ao cliente(R$):','').strip().replace('.','').replace(',','.'))
                
                if(cpf_encontrado == ''):
                    cpf_encontrado = self.selenium.verificar_texto_campo_jquery('p:contains("CPF do Beneficiário:")')

                valor_proposta_wa = float(self.contrato['valor_con'].replace('.','').replace(',','.'))                
                
                if(self.valor_proposta_ole == ''):
                    continue

                if self.valor_proposta_ole  < valor_proposta_wa*0.90:
                    rec += 1
                    if(len(links) == rec):
                        raise ErrorOleException('ADE não encontrada')
                    else:
                        continue
                
                if cpf_encontrado.find(self.contrato['cpf_cli'][0:3]) == -1:
                    continue

            return True

        raise ErrorOleException('ADE não encontrada')

    def baixar_pdf_contrato(self):

        #link_imprimir = self.criar_link_elemento('#Imprimir')
        #self.driver.get(link_imprimir)
        options = {"enable-local-file-access": None, "load-media-error-handling":"ignore" , "load-error-handling":"ignore"}
        #codigo_pagina = self.driver.page_source.replace('file:///lib/jquery/jquery.js','')
        #try:
            #pdf = pdfkit.from_string(codigo_pagina, False, configuration=self.config,options=options)
        #except:
        pageSource = self.driver.execute_script("return document.body.innerText")
        pdf = pdfkit.from_string(pageSource, False, configuration=self.config,options=options)
        #pdf = pdfkit.from_string(self.driver.page_source, False, configuration=self.config,options=options)
        #pageSource = self.driver.execute_script("return document.body.innerText")
        #pdf = pdfkit.from_string(pageSource, False, configuration=self.config,options=options)
        
        return base64.b64encode(pdf)

    def envia_pdf_contrato(self, pdf_base_64):
        dados_pdf = {
            'key': 'f689f1e12a0399fba803cb2365fc362f',
            'ade': self.contrato['ade'],
            'codigoCliente': self.contrato['codigo_cli'],
            'codigoContrato': self.contrato['codigo_con'],
            'base64': pdf_base_64,
            'valor' : self.valor_proposta_ole,
            'banco': 'ole'
        }

        request_gerar_contrato = requests.post("https://uconecte.me/api/v1/contratos/gerar",data=dados_pdf)

        if request_gerar_contrato.status_code != 200:
            print(request_gerar_contrato.json())
            input('Não foi possível gerar o Contrato')

        #self.fechar_pagina_imprimir()

        print('Contrato %s Gerado com sucesso!' % (self.contrato['ade']))

    def fechar_pagina_imprimir(self):
        if float(self.driver.capabilities['version'][:2]) < 77.0:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.execute_script("""document.querySelector(\"print-preview-app\").shadowRoot.querySelector(\"print-preview-sidebar\").shadowRoot.querySelector(\"print-preview-header\").shadowRoot.querySelector(\"paper-button.cancel-button\").click();""")
            self.driver.switch_to.window(self.driver.window_handles[0])

    def limpar_mensagem_erro(self, erros):
        return list(map(lambda erro: re.sub(r'\s{2,}', ' ', erro), erros))

    def verificar_erros(self, acao = ''):
        time.sleep(1)
        if self.selenium.buscar_quantidade_elemento('#divMensagemErro\\:visible') == 1:
            erros = self.montar_mensagem_erro('#divMensagemErro li')
        elif self.selenium.buscar_quantidade_elemento('#divErro\\:visible') == 1:
            erros = self.montar_mensagem_erro('#divErro li')
        elif self.selenium.buscar_quantidade_elemento('.alert-dismissible\\:visible') and 'Margem' not in self.selenium.verificar_texto_campo_jquery('#divMensagemAlerta'):
            erros = self.montar_mensagem_erro('.alert-dismissible')
        elif self.selenium.buscar_quantidade_elemento(".generic-error\\:visible") == 1:

            print("Sistema do banco indisponível! Esperando para tentar novamente...")
            if(acao == 'gerar_contrato'):
                self.driver.delete_all_cookies()
                self.driver.get('https://ola.oleconsignado.com.br/')
            time.sleep(30)
            raise ErrorOleException(message="Sistema do banco indisponível!")
  
        try:
            self.tratar_mensagens_erro(erros)
        except NameError:
            return

    def verificar_loading(self, interacoes=35, aguardar = False, pular_erro_portabilidade = False):
        while (self.selenium.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
            print('Aguardando Loading...' + str(interacoes))
            time.sleep(2)
            interacoes -= 1

        if(aguardar != True and pular_erro_portabilidade == False):
            self.verificar_erros('gerar_contrato')

    def verificar_loading_anexos(self, interacoes=35):
        time.sleep(3)

        while (self.selenium.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
            print('Aguardando Loading...')
            time.sleep(2)
            interacoes -= 1

            if (interacoes == 0):
                raise ErrorOleException(message="Sistema do banco indisponível!")

        self.verificar_erros('gerar_contrato')

    def tratar_mensagens_erro(self, erros):
        erros = self.limpar_mensagem_erro(erros)

        for erro in erros:
            print(erro)

        if not self.contrato:
            self.contrato = dict()
            self.contrato['data_dep_con'] = '01/01/2020'

        erros_identificados = [
            {
                "erro": "Nenhuma proposta encontrada para o intervalo de 0 mês. Período: {} à {}.".format(
                    self.contrato['data_dep_con'],
                    self.acrescenta_7_dias(self.contrato['data_dep_con'])),
                "mensagem": "Sem possibilidade de baixar contrato"
            }, {
                'erro': "Nenhuma proposta encontrada para o(s) filtro(s) informado(s).",
                'mensagem': "Sem possibilidade de anexar"
            }, {
                'erro': "O telefone celular informado já está associado a outro CPF. Favor entrar em contato com o "
                        "parceiro Olé para solicitar alteração.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "O telefone celular informado já está associado a outro CPF.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "Não existe produto para as condições informadas.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "Cliente possui contrato com inadimplência.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "CPF não aprovado.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "Valor solicitado é maior do que o permitido para a Idade do Financiado.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': 'Cliente não atende à regra interna deste benefício.',
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': 'CPF possui restrição.',
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': "Ocorreu um erro inesperado, tente novamente mais tarde.",
                'mensagem': "ErrorOleException"
            }, {
                'erro': "Número da agência é obrigatório.",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na identificação da agência."
            }, {
                'erro': "Agência selecionada não é permitida para Forma de Pagamento .",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na identificação da agência."
            }, {
                'erro': "Telefone celular informado não é um tipo de telefone celular válido.",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na inserção do telefone celular"
            }, {
                'erro': 'Saldo devedor mais valor solicitado excede o valor de RISCO MÁXIMO.',
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema ao calcular a simulação"
            }, {
                'erro': 'A extensão do documento é inválida.',
                'mensagem': "Anexo no formato invalido"
            }, {
                'erro': 'O tamanho total dos arquivos excedeu o limite máximo de 10MB.',
                'mensagem': "Arquivo acima de 10 MB"
            }, {
                'erro': 'A extensão do(s) arquivo(s) é inválida para o produto.',
                'mensagem': "Anexo no formato invalido"
            }, {
                'erro': 'Benefício inativado pelo órgão. Em caso de dúvidas, gentileza verificar junto ao INSS.',
                'mensagem': "Reprovado a Conferir",
                'observacao': "Benefício cessado"
            }, {
                'erro': r"CEP na lista restritiva.",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': r"Valor da taxa está fora dos limites do parâmetro.",
                'mensagem': "Reprovado a Conferir"
            },{
                'erro': r"Valor da taxa está fora dos limites do parâmetro.",
                'mensagem': "Reprovado a Conferir",
                'textoMensagem': "Banco não disponibilizou uma taxa de portabilidade que viabilizasse a operação."
            },{
                'erro': r"CPF não encontrado na Dataprev. Verifique o número informado e tente novamente",
                'mensagem': "Reprovado a Conferir"
            }
        ]

        erros_regex = [
            {
                'erro': r"Este convenio não poderá ser utilizado, pois o cliente possuirá \d{2} anos no vencimento da operação",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': r"Este convenio não poderá ser utilizado, pois o cliente possui \d{2} anos",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': r"Cidade é obrigatório",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na inserção do endereço, conferir o CEP informado!"
            }, {
                'erro': r"Endereço\(s\) inexistente\(s\) para o CEP informado.",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na inserção do endereço, conferir o CEP informado!"
            }, {
                'erro': r"Data de nascimento divergente da Receita Federal",
                'mensagem': "Reprovado a Conferir"
            }, {
                'erro': r"Dados cadastrais consultados. Beneficiário não poderá ser atendido pois não possui margem consignável disponível para empréstimo.",
                'mensagem': "Reprovado a Conferir",
                'observacao': "Margem Insuficiente"
            }, {
                'erro': r"O telefone precisa estar no formato",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema na inserção do telefone celular"
            }, {
                'erro': r"O valor solicitado, somando outras operações existentes, excede o RISCO MÁXIMO. Refaça a simulacão para enquadrar a operação dentro da regra.",
                'mensagem': "Conferir dados do contrato",
                'observacao': "Problema no cálculo de parcelas"
            }, {
                'erro': r'Service Unavailable',
                'mensagem': 'ErrorOleException'
            }, {
                'erro': r"Para prosseguir, a Data de Liberação informada deve ser igual à \d{2}\/\d{2}\/\d{4}",
                'mensagem': 'ErrorOleException'
            }, {
                'erro': r"Não foi possivel consultar parcelas do Produto.",
                'mensagem': 'ErrorOleException'
            }, {
                'erro': r"O telefone celular informado já está associado a outro CPF.",
                'mensagem': "Aguardando Autorização",
                'textoMensagem': "O telefone informado por você já está registrado para outro cpf. Informe outro telefone celular.",
                'pedidoDocumentacao': 3,
                'interacaoHumana': 1
            }, {
                'erro': r"Data emissão RG não pode ser maior que a data atual.",
                'mensagem': "Aguardando Autorização",
                'textoMensagem': "Confirme por favor a data de emissão completa do seu RG.",
                'pedidoDocumentacao': 3,
                'interacaoHumana': 1
            },{
                'erro': r'Valor financiado não pode ser menor que o valor mínimo cadastrada no produto. valor mínimo: \d{3}',
                'mensagem': 'Valor mínimo financiado não atingido'
            },{
                'erro': r'Nenhuma proposta encontrada para o intervalo de 1 mês. Período: \d{2}\/\d{2}\/\d{4} à \d{2}\/\d{2}\/\d{4}.',
                'mensagem': "Contrato não gerado"
            },{
                'erro': r'Nenhuma proposta encontrada para o intervalo de 1 mês. Período: \d{2}\/\d{2}\/\d{4} à \d{2}\/\d{2}\/\d{4}.',
                'mensagem': "Contrato não gerado"
            },{
                'erro': r'você perderá todos os seus dados',
                'mensagem': "Continuar"
            },{
                'erro': r"CPF não encontrado na Dataprev. Verifique o número informado e tente novamente",
                'mensagem': "Reprovado a Conferir"
            }
        ]

        for erro_identificado in erros_identificados:
            try:
                erros.index(erro_identificado['erro'])
                if (erro_identificado['mensagem'] == "Sem possibilidade de anexar"):
                    raise ErrorOleException("SEM POSSIBILIDADE DE ANEXAR AINDA")

                if (erro_identificado['mensagem'] == "Anexo no formato invalido"):
                    raise ErrorOleException("ANEXOS COM FORMATO INVALIDO")

                if (erro_identificado['mensagem'] == "ErrorOleException"):
                    raise ErrorOleException("Pular inserção!")
                pdb.set_trace()

                self.atualizar_contrato(self.codigo_contrato, erro_identificado)
                raise ErrorOleException(
                    "Executei a ação vinculada à mensagem")
            except (ValueError):
                pass

        for erro_regex in erros_regex:
            regex = re.compile(erro_regex['erro'])
            erro_encontrado = [erro for erro in erros for match in [regex.search(erro)] if match]

            if erro_regex['mensagem'] == "Continuar":
                return

            if not erro_encontrado:
                continue

            if erro_regex['mensagem'] == "ErrorOleException":
                raise ErrorOleException("Pular inserção!")

            erro_regex['erro'] = erro_encontrado
            self.atualizar_contrato(self.codigo_contrato, erro_regex)

            raise ErrorOleException(
                "Executei a ação vinculada à mensagem")

        self.mensagem_erro_nao_encontrada(erros)

    def mensagem_erro_nao_encontrada(self, erros):
        confirmar = input(
            "Erro, %s. Deseja continuar? r/p (reprovar/pular)" % (erros))

        if (confirmar == "r"):
            mensagem = input("Mensagem: ")
            self.atualizar_contrato(self.codigo_contrato, {
                'mensagem': mensagem,
                'erros': ", ".join(erros)
            })
        elif (confirmar == "p"):
            raise Exception("Não inserir esse contrato!")

    def select_agencia(self, valor):
        selet_agencia = self.driver.find_element(By.CSS_SELECTOR,".select2")
        actions_agencia = ActionChains(self.driver)
        actions_agencia.click(selet_agencia)
        actions_agencia.send_keys(valor)
        actions_agencia.pause(5)
        actions_agencia.send_keys(Keys.ENTER)
        actions_agencia.perform()

    def select_tipo_conta(self, valor):
        if (valor == "Conta-corrente"):
            tipo_conta = "CONTA_CORRENTE_INDIVIDUAL"
        elif (valor == "Conta-poupança"):
            tipo_conta = "CONTA_POUPANCA_INDIVIDUAL"
        elif (valor == "Conta-corrente Conjunta"):
            tipo_conta = "CONTA_CORRENTE_CONJUNTA"
        elif (valor == "Conta-poupança Conjunta"):
            tipo_conta = "CONTA_POUPANCA_CONJUNTA"
        elif (valor == "Conta salário"):
            tipo_conta = "CONTA_SALARIO"
        elif (valor == "Conta investimento"):
            tipo_conta = "CONTA_INVESTIMENTO"
        self.selenium.atribuir_valor_campo_jquery("#TipoConta", tipo_conta, change=True)

    def montar_mensagem_erro(self, selector):
        return self.driver.execute_script("""
            let erros = [];
            $('%s').each(function(index, item) {
                erros.push($(item).text());
            });

            return erros""" % (selector))

    def criar_link_elemento(self, seletor):
        return "https://ola.oleconsignado.com.br%s" % (
            self.selenium.verificar_atributo_campo_jquery(seletor, 'href'))

    def clicar_elemento_radio_button(self, seletor):
        self.driver.execute_script(
            """$("input:radio[name=%s]:first").attr('checked', true)""" % (seletor))

    @staticmethod
    def acrescenta_7_dias(data):
        dia = int(data[:2])
        mes = int(data[3:5])
        ano = int(data[6:10])

        dia += 7

        if dia > 31:
            mes += 1
            dia -= 31
            if mes > 12:
                ano += 1
                mes -= 12

        if len(str(dia)) == 1 and len(str(mes)) == 1:
            data_nova = '0' + str(dia) + "/" + '0' + str(mes) + "/" + str(ano)
        elif len(str(dia)) == 1 and not len(str(mes)) == 1:
            data_nova = '0' + str(dia) + "/" + str(mes) + "/" + str(ano)
        elif not len(str(dia)) == 1 and len(str(mes)) == 1:
            data_nova = str(dia) + "/" + '0' + str(mes) + "/" + str(ano)
        else:
            data_nova = str(dia) + "/" + str(mes) + "/" + str(ano)

        return data_nova


class ErrorOleException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
