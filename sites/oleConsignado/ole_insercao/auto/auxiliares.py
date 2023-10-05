from selenium.webdriver.common.by import By
from time import sleep
from sites.baseRobos.core.data_helpers import make_request, similaridade
from sites.oleConsignado.libs.elementos.Botoes import btn_ok_modal_sucesso, btn_ok_modal_dataprev, \
    btn_ok_modal_aguardar_dados
from sites.oleConsignado.ole_insercao.data.erros_data import dados_erros_regex, dados_erros_identificados
import re,pdb
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.selenium_actions import SeleniumActions

def preencher_se_nao_disabled(loc, val, act, by=By.CSS_SELECTOR, delay=0.1):
    """
    :type loc: str
    :type val: str
    :param act: SeleniumAction instance
    :type act: object
    :param by: selenium.webdriver.common.by.By object
    :type by: object
    :param delay: tempo entre caracteres
    :type delay: float
    :rtype: bool
    """
    if not act.obter_propriedade(loc, 'disabled', by):
        print("Elemento disponível.")
        act.enviar_texto_intervalado(loc, val, by, delay=delay)
        return True
    else:
        print("Elemento indisponível.")
        return False


def select_se_nao_disabled(loc, val, act, by=By.CSS_SELECTOR):
    """
    :type loc: str
    :type val: str
    :param act: SeleniumAction instance
    :type act: object
    :param by: selenium.webdriver.common.by.By object
    :type by: object
    :rtype: bool
    """
    if not act.obter_propriedade(loc, 'disabled', by):
        print("Elemento disponível.")
        act.select_drop_down(loc, val, by)
        return True
    else:
        print("Elemento indisponível.")
        return False


def select_tipo_conta(valor):
    tipo_conta = ''
    if valor == "Conta-corrente":
        tipo_conta = "Conta Corrente"
    elif valor == "Conta-poupança":
        tipo_conta = "Conta Poupança Individual"
    elif valor == "Conta-corrente Conjunta":
        tipo_conta = "Conta Corrente Conjunta"
    elif valor == "Conta-poupança Conjunta":
        tipo_conta = "Conta Poupança Conjunta"
    elif valor == "Conta salário":
        tipo_conta = "Conta Salário"
    elif valor == "Conta investimento":
        tipo_conta = "Conta Investimento"

    return tipo_conta


def selecionar_prazo(contrato, selenium, act=None):
    grid_option = "1"
    print(contrato['prazo'])
    if contrato['prazo'] is None:
        return False

    if int(contrato['prazo']) < 72:
        prazo = selenium.verificar_valor_campo_jquery(
            '#selectQteParcelas option:contains("%s")' % (contrato['prazo']))

        if prazo is None:
            novo_prazo = int(contrato['prazo']) + 1
            prazo = selenium.verificar_valor_campo_jquery(
                '#selectQteParcelas option:contains("%s")' % (novo_prazo))

        selenium.atribuir_valor_campo_jquery(
            "#selectQteParcelas", prazo, change=True)

        selenium.clicar_elemento("#btnCalcularEmprestimo")
        sleep(5)

        if selenium.verificar_texto_campo_jquery("#idQteParcela-1") == contrato['prazo']:
            grid_option = "1"
        elif selenium.verificar_texto_campo_jquery("#idQteParcela-2") == contrato['prazo']:
            grid_option = "2"
        else:
            grid_option = "3"

        selenium.clicar_elemento("#gridretorno-%s" % grid_option)
        sleep(5)

    return grid_option


def validar_valor_renda(valor_renda):
    if valor_renda == "":
        return True

    valor_renda = float(valor_renda.replace('.', '').replace(',', '.'))

    if valor_renda < 998.00:
        return True

    return False


def dispensar_div_erro(act: SeleniumActions, loc_btn: str = '', metodo: str = By.CSS_SELECTOR):
    print("Verificando <div>Erro:</div>")
    loc_x = 'button#closeDivMensagemErro'
    try:
        print("Dispensando <div> erro.")

        act.clicar_elemento(loc_x)
    except TimeoutException:
        print(loc_x + " não foi aberto.")

    if loc_btn:
        print(f"Clicando novamente no botão {loc_btn}")
        act.forcar_clique_stale_element(loc_btn, metodo)

def verificar_modais(act: SeleniumActions, by: object):
    print("Verificando presença de modais")
    modal_sucesso = btn_ok_modal_sucesso(act.driver)
    modal_dataprev = btn_ok_modal_dataprev(act.driver)
    modal_aguardar_dados = btn_ok_modal_aguardar_dados(act.driver)

    if modal_sucesso is not None:
        print("Dispensar modal 'sucesso.'")
        modal_sucesso.hover_e_clique()

    elif modal_dataprev is not None:
        print("Dispensar modal 'dados verificados na DATAPREV.'")
        modal_dataprev.hover_e_clique()

    elif modal_aguardar_dados is not None:
        print("Dispensar modal 'aguardando dados do INSS'.")
        modal_aguardar_dados.hover_e_clique()
        sleep(7)
    else:
        print('Modais ausentes.')


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


def tratar_mensagens_erro(msg_erro: str, contrato: dict, uconecte: object):
    datas = {
        # 'inicial': contrato['data_dep_con'],
        # 'final': acrescenta_7_dias(contrato['data_dep_con'])
    }
    erros_site = dados_erros_identificados(datas)
    erros_regex = dados_erros_regex()

    print("Tratando o erro:-->", msg_erro)

    for erro_identificado in erros_site:
        try:
            print('----------------------------------------')
            print(erro_identificado)            
            print(msg_erro)
            print(similaridade(erro_identificado['erro'], msg_erro)) 
            print('----------------------------------------')

            if similaridade(erro_identificado['erro'], msg_erro) > 83:

                print(erro_identificado['mensagem'], msg_erro)
                
                if "Já existe um dossiê ativo ou proposta paga com aceite para este CPF vinculado ao celular" in msg_erro:
                    telefone_celular = msg_erro.split('celular')[1].strip().replace('.','').replace(' ','')                    
                    erro_identificado['textoMensagem'] = erro_identificado['textoMensagem'].replace('|CELULAR|',telefone_celular)         

                if erro_identificado['mensagem'] == "Sem possibilidade de anexar":
                    raise ErrorOleException("SEM POSSIBILIDADE DE ANEXAR AINDA")

                if erro_identificado['mensagem'] == "Anexo no formato invalido":
                    raise ErrorOleException("ANEXOS COM FORMATO INVALIDO")

                if erro_identificado['mensagem'] == "ErrorOleException":
                    raise ErrorOleException("Pular inserção!")

                if erro_identificado['mensagem'] == "Sem possibilidade de baixar contrato":
                    raise ErrorOleException("SEM POSSIBILIDADE DE BAIXAR CONTRATO")

                uconecte.atualizar_contrato(
                    contrato['codigoContrato'],
                    erro_identificado
                )

                raise ErrorOleException(
                    "Executei a ação vinculada à mensagem")
        except ValueError:
            pass

    for erro_regex in erros_regex:

        erro_data = erro_regex['erro'].replace("Erro encontrado: ", "")

        regex = re.compile(erro_data)

        if not regex.search(msg_erro) and not similaridade(erro_data, msg_erro) > 95:
            continue

        print(erro_data)
        if erro_regex['mensagem'] == "ErrorOleException":
            raise Exception("Pular inserção!")
        # erro_regex['erro'] = msg_erro

        print(erro_regex)

        uconecte.atualizar_contrato(
            contrato['codigoContrato'],
            erro_regex
        )
        
        raise ErrorOleException(
            "Executei a ação vinculada à mensagem")


def verificar_erros(act: object, by) -> str:
    loc_texto = '//*[@id="divMensagemErro"]/ul/li'
    loc_texto2 = '//*[@id="divErro"]/ul/li'

    print("Verificando <div>Erro:</div>")
    texto_erro = ''
    try:
        texto_erro = act.obter_texto(loc_texto, by.XPATH)
        print("Erro identificado.")
        print(texto_erro)

    except TimeoutException:
        texto_erro = act.obter_texto(loc_texto2, by.XPATH)
        print("Erro identificado.")
        print(texto_erro)

    finally:
        return texto_erro


class ErrorOleException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
