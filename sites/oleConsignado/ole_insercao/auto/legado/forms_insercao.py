"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: pan_inserc_auto.py
| data: 2019-12-20
| autor: Gustavo Belleza
"""
from sites.baseRobos.gui_auto import AutoGUI
from sites.baseRobos.core.uconecte import Uconecte
from time import sleep
from selenium.common.exceptions import TimeoutException, InvalidElementStateException

import re
from sites.oleConsignado.ole_insercao.auto.auxiliares import (
    preencher_se_nao_disabled, dispensar_div_erro,
    verificar_modais, select_tipo_conta, selecionar_prazo,
    validar_valor_renda, tratar_mensagens_erro
)

from random import randint, randrange
import requests
from datetime import datetime as dt


class OleInsercao(AutoGUI):
    url_aba_identificacao = 'https://ola.oleconsignado.com.br/Identificacao'
    url_aba_simulacao = 'https://ola.oleconsignado.com.br/Simulacao/Index/?&'

    def __init__(self, chrome_driver):
        super().__init__(chrome_driver)
        self.chrome_driver: object = chrome_driver
        self.uconecte: object = Uconecte()

        self.t_max: float = 2
        self.t_min: float = 1
        self.t_sleep = 0.5

        self.atualizacoes: dict = {}
        self.max_time_out: float = 2
        self.min_time_out: float = 1.5
        self.inicio = ""
        self.fim = ""

    def aba_simulacao_dados_cliente(self, contrato: dict):
        """
        Preenche dos campos da Aba de Simulação relativos aos dados do cliente.
        """
        self.chrome_driver.get(self.url_aba_simulacao + contrato['cpf'])
        self.act.time_out = self.max_time_out
        sleep(randint(self.t_min, self.t_max))
        verificar_modais(self.act, self.by)

        print("Preenchendo aba de simulação")
        print("\tDados do Cliente")

        self.inicio = dt.now()

        self.__verificar_erros(contrato)

        # Campo Data de Nascimento - texto
        loc_data_nasc = '#DataNascimento'
        try:
            print("Data de nascimento:", contrato['dataNascimento'])
            self.act.hover_e_clique(loc_data_nasc)
            self.act.enviar_texto_intervalado(loc_data_nasc, contrato['dataNascimento'],
                                              delay=randint(10, 30) / 700, clear=False)
            self.act.press_enter(loc_data_nasc)
        except TimeoutException:
            print("Data de nascimento já preenchida")
        except InvalidElementStateException:
            print("Data de nascimento já preenchida")

        # Campo Codigo do Convênio - button -> text
        print("Código do convênio - INSS.")

        try:
            loc_convenio_select = 'button[data-id="CodigoConvenio"]'
            self.act.hover_e_clique(loc_convenio_select)  # ativa o <input type="text">

            loc_convenio_txt = '//*[@id="divSimulacao"]/div[1]/div[2]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_convenio_txt, "011398",
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_convenio_txt, self.by.XPATH)  # dispara event_handler onchange
        except TimeoutException:
            print("Campo já preenchido.")
        # verificar_modais(self.act, self.by)

        # Campo Especie Benefício
        loc_esp_ben = 'button[data-id="CodigoEspecieBeneficio"]'
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

        verificar_modais(self.act, self.by)

        try:
            # Campo Operação
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

        verificar_modais(self.act, self.by)
        try:
            # Campo Tipo de Operação.
            print('Selecionando tipo de operação: 5 - Contrato Novo.')
            loc_tipo_operacao = 'button[data-id="CodigoTipoOperacao"]'
            self.act.hover_e_clique(loc_tipo_operacao)

            loc_tipo_operacao_txt = '//*[@id="divSimulacao"]/div[1]/div[4]/div/div/div/div/input'
            self.act.enviar_texto_intervalado(loc_tipo_operacao_txt, "5",
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_tipo_operacao_txt, self.by.XPATH)
        except TimeoutException:
            print("Data de nascimento já preenchida")
        except InvalidElementStateException:
            print("Data de nascimento já preenchida")

        print("Tipo de contratação - Digital.")
        loc_radio = "radioDigital"
        if self.act.esta_presente(loc_radio):
            self.act.hover_e_clique(loc_radio)

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
                input(">> ")
            except InvalidElementStateException:
                print("Campo já preenchido.")
        # verificar_modais(self.act, self.by)

    def aba_simulacao_dados_proposta(self, contrato, tipo_contrato):
        """
            #
        """
        sleep(self.t_sleep)
        print("Parcela.", contrato['valorParcela'])

        loc_parcela = "#ValorParcela"
        self.act.hover_e_clique(loc_parcela)

        sleep(self.t_sleep)
        self.act.press_backspace(loc_parcela, 5)
        self.act.enviar_texto_intervalado(
            loc_parcela, contrato['valorParcela'], delay=0.4, clear=False)

        print("Clicando em 'Calcular Empréstimo.'")
        loc_calcular = "#btnCalcularEmprestimo"
        self.act.hover_e_clique(loc_calcular)

        if self.__verificar_erros(contrato):
            dispensar_div_erro(act=self.act,  loc_btn=loc_calcular)

        verificar_modais(self.act, self.by)

        loc_calcular = "#btnCalcularEmprestimo"
        self.act.hover_e_clique(loc_calcular)

        self.__verificar_erros(contrato)

        # Selecionar tipo de produto.
        try:
            self.act.time_out = 4
            print("Selecionando produto relativo a 'Nova Proposta'")
            self.act.forcar_preenchimento_cb('input#gridretorno-1')
        except TimeoutException:
            print("Produto não encontrado.")
            self.__verificar_erros(contrato)

        self.act.time_out = self.min_time_out

        # Atualizar valor e prazo do contrato de acordo com o cálculo realizado.
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

        verificar_modais(self.act, self.by)

        print("Prosseguindo com proposta.")
        sleep(randrange(self.t_min, self.t_max))

        loc_prosseguir = "#btnProsseguirEmprestimo"
        self.act.hover_e_clique(loc_prosseguir)

        self.__verificar_erros(contrato)

        return self.atualizacoes

    def aba_dados_cliente(self, contrato):
        """
            #
        """
        print("Aba Dados Cliente.")

        loc_cpf = "input#CPF"
        if not self.act.obter_atributo(loc_cpf, 'readonly'):
            self.act.hover_e_clique(loc_cpf)
            self.act.enviar_texto_intervalado(loc_cpf, contrato['cpf'], delay=randint(10, 30) / 200)

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

        verificar_modais(self.act, self.by)

        print('Email.')
        loc_email = '#Email'
        if(contrato['email'] == 'emprestimo@uconecte.me'):
            rand_email = str(randint(1, 7000000001))
            self.act.enviar_texto_intervalado(loc_email, f'{rand_email}@hotmail.com', delay=randint(10, 30) / 700)
        else:
            self.act.enviar_texto_intervalado(loc_email, contrato['email'], delay=randint(10, 30) / 700)
        ddd, celular = contrato['dddCelular'], contrato['celular']
        loc_ddd, loc_cel = "#DDDTelefoneCelular", "#TelefoneCelular"
        print(f"Celular: ({ddd}) {celular}")
        self.act.hover_e_clique(loc_ddd)
        self.act.press_backspace(loc_ddd, loop=3, end=True)
        self.act.enviar_texto_intervalado(loc_ddd, ddd, delay=0.5, clear=False)
        self.act.hover_e_clique(loc_cel)
        self.act.enviar_texto_intervalado(loc_cel, celular, delay=0.3, clear=False)
        self.act.hover_e_clique(loc_cel)

        loc_renda = "#RendaBruta"
        loc_patrimonio = "#ValorPatrimonio"
        val_renda = self.act.obter_texto(loc_renda)
        print("Verificando renda bruta:", val_renda)
        if validar_valor_renda(val_renda):
            self.act.hover_e_clique(loc_renda)
            self.act.enviar_texto_intervalado(loc_renda, '998,00', delay=randint(10, 30) / 700)
            self.act.enviar_texto_intervalado(loc_patrimonio, '0,00', delay=randint(10, 30) / 700)

        print('Nome da mãe:', contrato['nomeMae'])
        loc_mae = '#NomeMae'
        self.act.hover_e_clique(loc_mae)
        self.act.enviar_texto_intervalado(
            loc_mae, contrato['nomeMae'], delay=randint(10, 30) / 700)

        # verificar_modais(self.act, self.by)
        print("Nº RG:", contrato['identidade'])
        loc_rg = "#NumeroRg"
        self.act.hover_e_clique(loc_rg)
        self.act.enviar_texto_intervalado(loc_rg, contrato['identidade'],
                                          delay=randint(6, 16) / 200)

        print("Selecionar comunicação por SMS.")
        loc_com_sms = '#ComunicacaoSMSEmail'
        self.act.hover_e_clique(loc_com_sms)

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

        sleep(randint(self.t_min, self.t_max))
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

        loc_cidade = 'button[data-id="Cidade"]'
        print("Verificando se campo cidade está disponível.")
        try:
            print("Campo cidade disponível.")
            # Clicar no elemento e habilitar txt input
            self.act.hover_e_clique(loc_cidade)
            # Preencher input e pressionar ENTER
            loc_cidade_txt = ('//*[@id="form_Pagina"]/div[7]/div/div/div/'
                              'div/div[1]/div[4]/div/div/div/div/input')
            self.act.enviar_texto_intervalado(loc_cidade_txt, contrato['cidade'],
                                              self.by.XPATH, delay=randint(10, 30) / 700)
            self.act.press_enter(loc_cidade_txt, self.by.XPATH)
        except TimeoutException:
            print("Campo cidade já preenchido.")
        except InvalidElementStateException:
            print("Campo cidade já preenchido.")

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

        print("Verificando se campo 'tipo de logradouro' eastá disponível.")

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

        print("Preenchendo complemento:", contrato['complemento'])
        loc_complemento = "#Complemento"
        preencher_se_nao_disabled(loc_complemento, contrato['complemento'],
                                  self.act, delay=randint(10, 30) / 700)

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
        loc_prosseguir = 'input#btnProsseguir'

        sleep(self.t_sleep)
        self.act.hover_e_clique(loc_prosseguir)

        dispensar_div_erro(act=self.act, loc_btn=loc_prosseguir)

        self.__verificar_erros(contrato)
        self.act.time_out = 20

    def aba_dados_operacao(self, contrato):
        sleep(self.t_sleep)
        print("Aba Dados Operação.")
        print("Preenchendo CPF Vendedor.")

        try:
            loc_cpf_vend = "#CPFVendedor"
            self.act.hover_e_clique(loc_cpf_vend)
            self.act.time_out = self.min_time_out
            self.act.enviar_texto_intervalado(loc_cpf_vend, "035.071.796-60", delay=randint(10, 30) / 700, clear=False)
        except InvalidElementStateException:
            print("Campo já preenchido")
        except TimeoutException:
            print("Campo já preenchido.")

        print("Selecionando tipo de conta corrente.", contrato['tipoConta'])

        try:
            self.act.time_out = self.max_time_out
            tipo_conta = select_tipo_conta(contrato['tipoConta'])
            loc_tipo_conta = 'button[data-id="TipoConta"]'
            loc_option = f'//*[@id="tipoContaPanel"]/div/div/div/ul/li[{tipo_conta}]/a'
            self.act.hover_e_clique(loc_tipo_conta)
            self.act.hover_e_clique(loc_option, self.by.XPATH)
        except InvalidElementStateException:
            print("Campo já preenchido.")

        self.act.time_out = self.min_time_out

        print("Preenchendo Nº do Banco.", contrato['numeroBanco'])
        loc_banco = 'button[data-id="NumeroBanco"]'
        try:
            try:
                # Clicar no elemento e habilitar txt input
                self.act.hover_e_clique(loc_banco)
                # Preencher input e pressionar ENTER
                loc_banco_txt = '//*[@id="dados-liberacao-001"]/div/div[4]/div/div/div/div/input'
                self.act.enviar_texto_intervalado(loc_banco_txt, contrato['numeroBanco'],
                                                  self.by.XPATH, delay=randint(10, 30) / 700)
                self.act.press_enter(loc_banco_txt, self.by.XPATH)
            except TimeoutException as e:
                print(e.stacktrace)
        except InvalidElementStateException:
            print("Campo já preenchido")

        print("Selecionando Agência")
        loc_agencia = '//*[@id="dados-liberacao-001"]/div/div[5]/div/div[1]/div/span/span[1]/span'
        try:
            try:
                # Clicar no elemento e habilitar txt input
                self.act.hover_e_clique(loc_agencia, self.by.XPATH)
                # Preencher input e pressionar ENTER
                loc_ag_txt = '/html/body/span/span/span[1]/input'
                self.act.enviar_texto_intervalado(loc_ag_txt, contrato['agencia'], self.by.XPATH,
                                                  delay=randint(10, 30) / 700)
                sleep(0.5)
                self.act.press_enter(loc_ag_txt, self.by.XPATH)
                sleep(0.5)
                self.act.press_enter(loc_ag_txt, self.by.XPATH)
            except TimeoutException as e:
                print(e)
        except InvalidElementStateException as e:
            print("Campo já preenchido")

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
            self.act.enviar_texto_intervalado(loc_n_conta, contrato['numeroConta'], delay=randint(10, 30) / 700)
        except InvalidElementStateException as e:
            print("Campo já preenchido")
        except TimeoutException as e:
            print("Campo indisponível")

        print("DV conta.")
        loc_dv_conta = '#DigitoVerificadorConta'
        self.act.hover_e_clique(loc_dv_conta)
        self.act.enviar_texto_intervalado(loc_dv_conta, contrato['digitoConta'], delay=randint(10, 30) / 700)

        verificar_modais(self.act, self.by)

        loc_btn_prosseguir = 'input#btnProsseguir'
        sleep(self.t_sleep)

        self.act.hover_e_clique(loc_btn_prosseguir)
        self.__verificar_erros(contrato)

    def aba_resumo(self, contrato):
        print('Aba resumo.')
        print('Botão finalizar empréstimo')
        sleep(randint(self.t_min, self.t_max))
        loc_finalizar = 'input#btnFinalizarEmprestimo'
        self.act.hover_e_clique(loc_finalizar)

        sleep(self.t_sleep)
        self.act.time_out = self.max_time_out
        print('Botão concluir Empréstimo')
        loc_concluir = "#btnConcluirEmprestimo"
        self.act.hover_e_clique(loc_concluir)

        try:
            sleep(self.t_sleep)
            loc_cartao = '#btnCancelarCartaoComPermissao'
            print('Botão Cancelar Cartão com permissão')
            self.act.hover_e_clique(loc_cartao)
            sleep(0.5)
            self.act.hover_e_clique(loc_cartao)

        except TimeoutException:
            print("Modal 'Contratar Cartão' não foi aberto.")

        self.act.time_out = 3

        print("Atualizando inserção.")
        self.atualizacoes['mensagem'] = "Aguardando Gerar Contrato"

        self.__atualizar_contrato(contrato['codigoContrato'], self.atualizacoes)

        print('Proposta inserida!')
        sleep(self.t_sleep)
        self.chrome_driver.get('https://ola.oleconsignado.com.br/Identificacao')

        self.fim = dt.now()

        print(f"\nINÍCIO: {self.inicio}\nFIM: {self.fim}")

    @staticmethod
    def __atualizar_contrato(codigo_contrato, dados):
        request_atualizar_contrato = requests.put(
            'https://app.emprestimofacil.com/api/v1/contratos/%s?key=f689f1e12a0399fba803cb2365fc362f' % (
                codigo_contrato),
            data=dados)

        if request_atualizar_contrato.status_code == 200:
            print('contrato atualizado')
        else:
            print(request_atualizar_contrato.text)
            input("Aguardando interação... %s" % request_atualizar_contrato.status_code)

    def __verificar_erros(self, contrato: dict) -> bool:
        self.act.time_out = 0.5
        loc_texto = '//*[@id="divMensagemErro"]/ul/li'

        loc_texto2 = '//*[@id="divErro"]/ul/li'

        print("Verificando <div>Erro:</div> Forms insercao")
        texto_erro = ''
        try:
            texto_erro = self.act.obter_texto(loc_texto, self.by.XPATH)
            print("Erro identificado.")
            print(texto_erro)

        except TimeoutException:
            texto_erro = self.act.obter_texto(loc_texto2, self.by.XPATH)
            print("Erro identificado.")
            print(texto_erro)

        finally:
            self.act.time_out = self.max_time_out

            if texto_erro:
                if texto_erro in "Produto é obrigatório.":
                    input("> ")
                self.act.time_out = self.min_time_out
                tratar_mensagens_erro(texto_erro, contrato, self.uconecte)
            else:
                return False



