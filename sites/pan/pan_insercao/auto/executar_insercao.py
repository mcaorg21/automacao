"""
    Utiliza as classes representantes dos formulários para
implementar a automação do processo de inserção. Cada função
executa a automação de apenas um formulário (ou seção lógica
de um formulário). Para tanto, cada função instancia apenas
uma classe.
    Funções principais:
    1. preencher_formulario_identificacao. 2. preencher_dados_proposta_insercao.
    3. preencher_dados_pessoais. 4. preencher_dados_bancarios.
    5. finalizar_insercao.
"""
# Classes dos formularios.
from sites.pan.pan_insercao.auto.pan_inserc_formulários import (
    PanFormIdentificacao, PanFormInsercaoDadosProposta,
    PanFormInsercaoDadosPessoais, PanFormInsercaoDadosBancarios,
    PanFormFinalizarInsercao
)
from sites.pan.pan_insercao.auto.assinatura_digital_forms import (
    PanFormAssinaturaDigital
)

from sites.pan.pan_consulta_refin.auto.FormsConsultaRefin import (
    FormIdentificacao
)

from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import (
    ConsultaRefin
)

# Funções auxiliares.
from sites.pan.pan_insercao.auto.pan_inserc_formulários import (
    verificar_alertas, filtrar_tipo_conta, tratar_mensagens_sistema)

# Exceptions nativas do selenium
from selenium.common.exceptions import (
    UnexpectedAlertPresentException, TimeoutException,
    JavascriptException, WebDriverException
)

from sites.pan.pan_insercao.auto.pan_inserc_formulários import AtualizarException

from selenium.webdriver import Chrome
# stdlib
from time import sleep
from sites.baseRobos.core.DebugTools import DebugTools


def preencher_formulario_identificacao(driver: Chrome, contrato: dict):

    form: PanFormIdentificacao = PanFormIdentificacao(driver)
    try:
        # breakpoint()

        form.selectPromotora()

        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

        form.select_empegador()

        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.select_orgao(contrato)
        try:
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        except UnexpectedAlertPresentException as e:
            tratar_mensagens_sistema(form.act, e.alert_text, contrato)

        form.campo_cpf(contrato)
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH, max_rec=10)
        try:
            form.modal_selecionar_matricula_cadastro(acao="fechar")
        except JavascriptException:
            print("Modal não foi aberto")
        except TimeoutException:
            print("Modal não foi aberto")
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH,max_rec=10)
        form.campo_data_nascimento(contrato)
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.campos_ddd_telefone(contrato)
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.campo_matricula(contrato)
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.botao_consulta()
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

        verificar_alertas(form.act, contrato)

        print('Tentando modal card Dataprev')
        form.descartarCardDataPrev()
        
        if form.existeCardPendente():
            form.descartarCardPendente()
            form.confirmarDescartarPendencia()
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
            if(form.existeAvisoCardCancelado()):
                form.confirmarDescartarPendencia()

            form.botao_consulta()
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

        print('Loading para ver se tem oferta disponivel...')
        loc_loading: str = '//*[@id="div-loading"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        
        try:
            print('Verificando se possui oferta disponivel....')
            if not form.oferta_disponivel():
                return 'Nenhuma oferta disponível'
        except:
            print('Possui oferta disponivel')
            pass

        
        print('Tentando modal card Dataprev')
        form.descartarCardDataPrev()

        try:
            form.ofertarMargemLivre()
        except:
            AtualizarException('Não apareceu disponível a contratação do card de nova oferta.')

        try:
            loc_loading: str = '//*[@id="ctl00_Image2"]'
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        except UnexpectedAlertPresentException as e:
            tratar_mensagens_sistema(form.act, e.alert_text, contrato)

        verificar_alertas(form.act, contrato)
    except UnexpectedAlertPresentException as e:
        tratar_mensagens_sistema(form.act, str(e.alert_text), contrato)


def preencher_dados_proposta_insercao(driver: Chrome, contrato: dict, tipo_contrato: str):
    form: PanFormInsercaoDadosProposta = PanFormInsercaoDadosProposta(driver)

    verificar_alertas(form.act, contrato)
    sleep(2)  

    print("\n> Preenchendo formulário de inserçao...")
    verificar_alertas(form.act, contrato)

    # Preencher Renda - Geralmente vem preenchida pelo sistema.
    form.campo_renda(contrato)
    sleep(3)

    verificar_alertas(form.act, contrato)
    
    # Preencher Valor Solcitação
    #form.campo_valor_solicitacao(contrato)

    # Preencher Valor da Parcela
    form.campo_valor_parcela(contrato)

    #Preenche o prazo
    form.selecionar_campo_prazo(contrato)

    verificar_alertas(form.act, contrato)

    # Simular Financiamento - Tabela
    form.botao_calcular_financiamento()

    verificar_alertas(form.act, contrato)
    # Selecionar Check Box - Tipo de Benefício
    loc_loading: str = '//*[@id="ctl00_Image2"]'
    form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

    selec_tabela: str = form.filtrar_tipo_contrato(contrato['tabela'], tipo_contrato, contrato)
    
    if selec_tabela is None:
        selec_tabela: str = form.filtrar_tipo_contrato_forcado(contrato['tabela'], tipo_contrato, contrato)

    form.checkbox_tabela_beneficio(selec_tabela, contrato)

    loc_loading: str = '//*[@id="ctl00_Image2"]'
    form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
    verificar_alertas(form.act, contrato)

    form.retirar_seguro()
    loc_loading2: str = '//*[@id="ctl00_UpdPrs"]'
    form.act.esta_presente_recursivo(loc_loading2, form.by.XPATH)
    verificar_alertas(form.act, contrato)

    form.recalcular()
    form.act.esta_presente_recursivo(loc_loading2, form.by.XPATH)
    verificar_alertas(form.act, contrato)

    novo_valor = form.atualiza_valor()

    # Selecionar Check Box - Tipo de Benefício
    #selec_tabela: str = form.filtrar_tipo_contrato(contrato['tabela'], tipo_contrato, contrato)
    #form.checkbox_tabela_beneficio(selec_tabela, contrato)

    return form.tabela_selecionada,novo_valor


def preencher_dados_pessoais(driver: Chrome, contrato: dict):
    form: PanFormInsercaoDadosPessoais = PanFormInsercaoDadosPessoais(driver)
    verificar_alertas(form.act, contrato)

    print("Preenchendo dados pessoais.")
    form.campo_nome(contrato)

    form.campo_estado_civil()

    form.campo_rg(contrato)

    try:
        form.campo_cep(contrato)
    except UnexpectedAlertPresentException as e:
        print(e.alert_text)
        tratar_mensagens_sistema(form.act, e.alert_text, contrato)

    # aguarda enquanto a págine carrega os dados do formulário.
    try:
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
    except UnexpectedAlertPresentException as e:
        tratar_mensagens_sistema(form.act, e.alert_text, contrato)

    form.campo_endereco(contrato)

    form.campo_n_casa(contrato)

    form.campo_complemento(contrato)

    form.campo_bairro(contrato)

    form.campo_nome_mae(contrato)

    form.campo_email(contrato)

    form.campo_cpf_insercao(contrato)


def preencher_dados_bancarios(driver: Chrome, contrato: dict):
    print("Preenchendo dados bancários.")
    form: PanFormInsercaoDadosBancarios = PanFormInsercaoDadosBancarios(driver)
    tipo_conta: str = filtrar_tipo_conta(contrato['tipoConta'])
    try:
        if not tipo_conta:
            print("Ordem de pagto.")
            try:
                form.selecionar_ordem_de_pagto(contrato)
            except WebDriverException as e:
                if "cannot locate option" in str(e.msg).lower():
                    tratar_mensagens_sistema(
                        act=form.act,
                        texto='Cannot locate option with value',
                        contrato=contrato
                    )

        else:
            loc_loading: str = '//*[@id="ctl00_Image2"]'

            form.select_tipo_conta(tipo_conta)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
            form.campo_beneficio(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

            form.select_uf_beneficio(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

            form.campo_n_banco(contrato)
            verificar_alertas(form.act, contrato)

            form.campo_agencia(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
            verificar_alertas(form.act, contrato)

            form.digito_agencia(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

            form.n_conta_corrente(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

            form.dv_conta_corrente(contrato)
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

    except UnexpectedAlertPresentException as e:
        if form.act.verificar_existencia_alerta():
            print('Tratando alerta...', e.alert_text)
            text_alerta: str = form.act.obter_texto_alerta()
            tratar_mensagens_sistema(form.act, text_alerta, contrato)


def finalizar_insercao(driver: Chrome, contrato: dict) -> str:
    form: PanFormFinalizarInsercao = PanFormFinalizarInsercao(driver)
    print("Finalizando inserçao.")
    try:
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        try:
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        except UnexpectedAlertPresentException as e:
            tratar_mensagens_sistema(form.act, e.alert_text, contrato)

        form.act.time_out = 2
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        verificar_alertas(form.act, contrato)
        try:
            form.campo_cpf_operador()
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        except:
            print('Nao precisou preencher campo')
            pass

        n_ade = ""
        rec = 0
        while n_ade == '':
            print('Tentando encontrar ADE')
            form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
            try:
                form.campo_cpf_operador()
                form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
            except:
                print('Nao precisou preencher campo')
                pass

            n_ade = finalizar_insercao_segunda(driver, contrato)
            rec += 1

            print('Nova tentativa de pegar ADE: ' + str(rec))
            if(rec == 5):
                return 'Insercao falha'

        return n_ade

    except UnexpectedAlertPresentException as e:
        print('Tratando alerta...', e.alert_text)
        text_alerta: str = form.act.obter_texto_alerta()
        tratar_mensagens_sistema(form.act, text_alerta, contrato)


def finalizar_insercao_segunda(driver, contrato):
    form: PanFormFinalizarInsercao = PanFormFinalizarInsercao(driver)
    print("Finalizando inserçao.")
    n_ade = ""


    try:
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.botao_salvar_proposta()
    except:
        pass

    try:
        loc_loading: str = '//*[@id="ctl00_Image2"]'
        form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)
        form.aprovar_proposta()
    except:
        pass
    
    try:
        sleep(2)
        n_ade: str = form.extrair_ade()
    except:
        pass

    try:
        form.confirmar_formalizacao_digital_tela()
    except:
        pass

    try:
        form.concluir_negociacao()
    except:
        pass  

    msg_alerta = verificar_alertas(form.act, contrato)

    if(msg_alerta == 'preencher_cpf'):
        form.apagar_cpf_operador()

    if not n_ade:
        sleep(10)
        print("Extraindo a ade da tabela")
        try:
            n_ade: str = form.extrair_ade_tabela()
        except:
            pass

        if not n_ade:
            try:
                n_ade: str = form.extrair_ade_frame()
            except:
                pass

    return n_ade


def realizar_assinatura_digital(driver: Chrome, n_ade: str, recr=1) -> str:
    # raises ApplicationErrorException
    form: PanFormAssinaturaDigital = PanFormAssinaturaDigital(driver)

    link_assinatura: str = ''
    try:
        driver.get('https://panconsig.pansolucoes.com.br/WebAutorizador/'
                   'MenuWeb/Esteira/AprovacaoConsulta/UI.AprovacaoConsultaAnd.aspx')
        sleep(4)

        form.input_texto_pesquisar_proposta(n_ade)
        form.botao_pesquisar_proposta()
        form.selecionar_proposta_assinatura()

        loc_frame = '//*[@id="ctl00_Cph_FrameExterno"]'
        form.act.trocar_frame_seletor(loc_frame, form.by.XPATH)
        form.act.time_out = 10

        form.botao_pular_envio_docs()
        form.act.time_out = 5

        form.selecionar_assinatura_via_link()
        form.confirmar_assinatura_via_link()
        form.preencher_nome_vendedor()
        form.preencher_nome_empresa()
        link_assinatura = form.obter_link_assinatura_digital()
        form.confirmar_envio_de_link()
        form.concluir_assinatura_digital()

        return link_assinatura

    except TimeoutException:
        form.act.time_out = 7
        if form.verificar_erro_tentar_novamente() and recr < 2:
            return realizar_assinatura_digital(driver, n_ade, recr+1)
        raise ApplicationErrorException(str(form.__module__))


class ApplicationErrorException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = f"Erro na aplicação. {msg}"

    def __repr__(self):
        return self.msg

