from selenium.webdriver import Chrome
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from time import sleep
from sites.baseRobos.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.selenium_actions import SeleniumActions
from sites.ibConsig.IbConsigInsercao.data.IbConsigData import IbConsigData
import re,pdb
from sites.baseRobos.core.captcha import TwoCaptcha
from sites.baseRobos.core.uconecte import Uconecte
from sites.baseRobos.core.data_helpers import (
    similaridade
)
from sites.ibConsig.IbConsigInsercao.data.registros_erros import (
    registro_erros_form_insercao
)
from sites.ibConsig.ItauConsultaRefin.data.collections import (
    registro_erros_forms_refin
)
from selenium.common.exceptions import (
    NoAlertPresentException, UnexpectedAlertPresentException,
    TimeoutException, NoSuchWindowException, NoSuchElementException
)
from datetime import datetime as dt
from sites.ibConsig.libs.exceptions.Exceptions import *
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List, Dict
deb = DebugTools(debugging=False)


def fechar_janelas_com_erro(driver: Chrome, default_frame=""):
    sleep(0.5)
    janelas = driver.window_handles
    if len(janelas) > 1:
        for n, janela in enumerate(janelas):
            sleep(0.3)
            if len(driver.window_handles) == 1:
                break
            if n == 0:
                continue
            try:
                sleep(0.3)
                driver.switch_to.window(janela)
                sleep(0.3)
                driver.close()
            except NoSuchWindowException:
                continue

    driver.switch_to.window(driver.window_handles[0])
    try:
        if default_frame:
            driver.switch_to.frame(driver.find_element_by_name(default_frame))
    except NoSuchElementException:
        print(f"Frame ({default_frame}) não foi encontrado")


def selecionar_opcao_modal_formulario(driver: Chrome):
    texto_modal = ""
    modal = driver.execute_script(
        """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').find('a:contains("Não")').length""")

    if (modal == 1):
        texto_modal = driver.execute_script(
            """return $('#identificacao-form\\\\:modalDialog.ui-overlay-visible').text()""")
        driver.execute_script(
            """$('#identificacao-form\\\\:modalDialog').find('a:contains("Sim")').click()""")
        sleep(5)

    return modal, texto_modal


def aguardar_loading(driver: Chrome, rec=0):
    loc = '//*[@id="waitDiv"]/center/img'
    act = SeleniumActions(driver, time_out=0.5)
    try:
        act.manusear_alerta()
        act.esta_presente_recursivo(loc, By.XPATH)
    except UnexpectedAlertPresentException:
        act.manusear_alerta()
        if rec > 10:
            return
        return aguardar_loading(driver, rec+1)


def filtrar_entidade(dados: dict, tipo_consulta_refinanciamento = True) -> str:

    entidade: str = ''

    if 'estadual' in dados:
        try:
            dados['sigla'] = dados['sigla_orgao'].upper()
        except:
            pass
        if dados['sigla'] == 'MT':
            entidade = '243'
        elif dados['sigla'] == "PR":
            entidade = '4'
        elif dados['sigla'] == "GO":
            entidade = '83'
        elif dados['sigla'] == "MG":
            try:
                if dados["codigoEntidade"] in ["63","69","2008", "2010"]:
                    entidade = "3"
                elif dados["codigoEntidade"] in ["80"]:
                    entidade = "2049"
                elif dados["codigoEntidade"] in ["65"]:
                    entidade = "2048"
            except:
                try:
                    if dados["orgao"] in ["63","69","2008", "2010"]:
                        entidade = "4193"
                    elif dados["orgao"] in ["80"]:
                        entidade = "2049"
                    elif dados["orgao"] in ["65"]:
                        entidade = "2048"
                except:
                    pass
        elif dados['sigla'] == "SP":
            try:
                if dados["codigoEntidade"] in ["66", "67"]:
                    entidade = "4193"
                elif dados["codigoEntidade"] in ["80", "81"]:
                    entidade = "4194"
                else:
                    entidade = "4195-1"
                    if(tipo_consulta_refinanciamento == True):
                        entidade = "4195"
            except:
                try:
                    if dados["orgao"] in ["66", "67"]:
                        entidade = "4193"
                    elif dados["orgao"] in ["80", "81"]:
                        entidade = "4194"
                    else:
                        entidade = "4195-1"
                        if(tipo_consulta_refinanciamento == True):
                            entidade = "4195"
                except:
                    pass
        elif dados['sigla'] == "RJ":
            entidade = "1"
            #raise ErroRetornarFila("Entidade não associada à loja.")

    elif 'federal' in dados:
        entidade = "164"
    elif 'marinha' in dados:
        entidade = "972"
    elif 'municipal' in dados:
        if(dados['cidade'] == "São Paulo"):
            entidade = "128"
        elif(dados['cidade'] == "Curitiba"):
            entidade = "3392"
        elif(dados['cidade'] == "Praia Grande"):
            entidade = "3710"
        elif(dados['cidade'] == "Piracicaba"):
            entidade = "2387"
        elif(dados['cidade'] == "Porto Velho"):
            entidade = "2573"
        elif(dados['cidade'] == "Recife"):
            entidade = "2542" 
        else:
            print('XXXXXXXXXXXXXXXXXXX ARQUIVO ibConsig/libs/auxiliares/ib_auxiliares.py XXXXXXXXXXX')
            print("XXXXXXXXXXXXXXXXXXX CLASSIFICAR CIDADE XXXXXXXXXXXXXXXXX" + str(dados['cidade'] ))
            sleep(180)
    elif 'inss' in dados:
        entidade = "1581"
    elif dados['fk_idPerfil'] == '7':
        entidade = "423"

    return entidade


def validar_acesso_contrato(contrato: dict) -> bool:
    status_acesso = contrato.get('usuarioPreenchimento', None)
    data_acesso = contrato['_dataAtualizacao']

    print("Status Acesso:", status_acesso)
    print("Data Acesso:", data_acesso)

    if status_acesso is None:  # contrato ainda nao foi acessado
        return True

    ultima_atualizacao = segs_atualizacao(data_acesso)
    print(f"A última atualização do contrato foi há {ultima_atualizacao} segundos")
    if status_acesso == '16332' and (ultima_atualizacao < 30):
        return False
    else:  # permite acesso ao contrato
        return True


def segs_atualizacao(data_atualizacao: str) -> int:
    a, b = data_atualizacao.split(" ")
    h, m, s = b.split(":")
    ano, mes, dia = a.split("-")
    hora, minuto, segundo = int(h), int(m), int(s)

    if int(mes) < dt.now().month:
        return 100

    if int(dia) < dt.now().day:
        return 100

    if hora < dt.now().hour:
        return 100

    return ((dt.now().minute * 60) + dt.now().second) - ((minuto * 60) + segundo - 798)


def verifica_portabilidade_retencao(
        driver: Chrome, sh: SeleniumHelper, wait=1) -> bool:
    try:
        sleep(wait)
        driver.switch_to.window(driver.window_handles[1])
        sleep(wait)
        portabilidade_retencao = driver.execute_script(
            """var resultado = $('.TituloTabela').text().trim(); return resultado;""")
        sleep(wait)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        sh.trocar_frame('rightFrame')
        if portabilidade_retencao != '':
            return True
        else:
            return False
    except Exception:
        pass


def aceitar_pendencia(driver: Chrome, sh: SeleniumHelper=None):
    sh = SeleniumHelper(driver)
    if len(driver.window_handles) > 1:
        try:
            driver.switch_to.window(driver.window_handles[1])
            sleep(1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            sh.trocar_frame('rightFrame')
        except IndexError:
            print("Janela de pendência não localizada.")


def tratar_erros_formulario_identificacao(driver: Chrome, **kwargs):
    """
    Definem tratativas para possíveis erros no preenchimento do formulário de
    identificação. Esses erros são apresentados em um <div> logo acima do formulário.
    """
    from sites.ibConsig.IbConsigInsercao.data.registros_erros import registro_erros_form_identificacao

    codigo_con: str = kwargs.get('codigo_con')
    id_captcha: int = kwargs.get('id_captcha', None)
    mensagem_erro: str = kwargs.get('msg_erro', None)

    captcha: TwoCaptcha = TwoCaptcha(driver)
    uconecte: Uconecte = Uconecte()

    # Verifica a existência de uma mensagem de erro.
    sleep(1)
    if not mensagem_erro:
        try:
            mensagem_erro = driver.execute_script(
                "return $('.error_message\\:visible').text()")
            mensagem_erro = mensagem_erro.strip()
        except Exception as e:
            return 0
    else:
        print("Erro encontrado: {}".format(mensagem_erro))

    # Tratativas para erros já documentados.
    mensagens = registro_erros_form_identificacao()

    for mensagem in mensagens:
        regex = re.compile(mensagem['texto'])
        mensagem_encontrada = regex.search(mensagem_erro)

        if not mensagem_encontrada:
            continue

        if 'aprovar' in mensagem:
            print('Captcha Aprovado')
            captcha.mudar_status_captcha(id_captcha, '1')
        else:
            print('Captcha Recusado')
            captcha.mudar_status_captcha(id_captcha, '2')

        if 'preenchimento' in mensagem:
            raise PreenchimentoException(
                message='Não foi possível passar do formulário de identificação')

        if 'atualizar' in mensagem:
            uconecte.atualizar_contrato(codigo_con, {
                'erro': mensagem_erro,
                'mensagem': mensagem['mensagem']
            })
            raise ErroRetornarFila(mensagem_erro)


def tratar_erros_formulario_insercao(driver: Chrome, codigo_contrato: str, **kwargs):
    """
    Definem tratativas para possíveis erros no preenchimento do formulário de
    inserção. Esses erros são apresentados em alertas ao longo e no fim do formulário
    de inserção.
    """
    msg_erro: str = kwargs.get('msg_erro', "")
    vals_atualizados: dict = kwargs.get('vals_atualizados', "")
    act: SeleniumActions = SeleniumActions(driver)

    alert_text: str = ""
    alert: Alert = Alert(driver)

    if not msg_erro:  # se mensagem de erro não tiver sido entraada como
        try:  # parâmetro, buscar texto no alerta
            sleep(1)
            alert_text = act.obter_texto_alerta()
            print(alert.text)
        except NoAlertPresentException:
            print("Alerta não encontrado")
            return ''
    else:
        alert_text = msg_erro

    print("Dados Alert:", alert_text)

    # Retorna um dict com a trtativas de erros
    erros_regex: List[Dict[str]] = registro_erros_form_insercao(
        alert_text=alert_text,
        vals_ideais=vals_atualizados
    )

    # Compara as mensagens de erro documentadas com o texto do alerta aberto.
    for erro_regex in erros_regex:
        regex = re.compile(erro_regex['erro'])
        erro_encontrado1 = regex.search(alert_text)
        erro_encontrado2 = regex.search(f"Erro encontrado: {alert_text}")

        if 'Número de prestações inválido' in erro_regex['erro']:
            porcentagem = 99
        else:
            porcentagem = 90
        similar = similaridade(erro_regex['erro'], alert_text) > porcentagem

        if not erro_encontrado1 and not erro_encontrado2 and not similar:
            continue

        if 'atualizar' in erro_regex:
            print('Atualizei o contrato %s' % codigo_contrato)
            erro_regex['erro'] = alert_text
            IbConsigData().atualizar_contrato(
                codigo_contrato=codigo_contrato,
                **erro_regex,
            )
            act.manusear_alerta('aceitar')
            raise ErroRetornarFila(erro_regex['erro'])

        if 'aceitar' in erro_regex:
            print('Aceitei o alert')
            act.manusear_alerta('aceitar')
            if 'retornar' in erro_regex:
                raise ErroRetornarFila(erro_regex)
            else:
                return 1

        if 'dados_bancarios' in erro_regex:
            print('Reinserção dos dados bancários')
            act.manusear_alerta('aceitar')
            raise DadosBancariosException(message="Reinserir dados bancários")

        elif 'preenchimento_exception' in erro_regex:
            print('Reinserindo dados pessoais')
            act.manusear_alerta('aceitar')
            raise PreenchimentoException(message="Reinserir dados pessoais")

        elif 'atualizar_valor' in erro_regex:
            print('Reinserindo valor maior')
            act.manusear_alerta('aceitar')
            raise TaxaSuperiorException(message="Reinserir dados valor")

        if 'pular' in erro_regex:
            act.manusear_alerta('aceitar')
            raise Exception("Pular inserção!")

        if 'confirmar' in erro_regex:
            act.manusear_alerta('aceitar')
            print("Confirmando inserção...")
            loc_confirmar = '#confirmar'
            act.clicar_elemento(loc_confirmar)
            sleep(3)
            return

        if "ErroDadosProposta" in erro_regex:
            act.manusear_alerta()
            raise ErroDadosProposta(erro_regex['erro'])

    act.manusear_alerta()
    raise ErroRetornarFila(alert_text)


def tratar_erros_formulario_refinanciamento(act: SeleniumActions, captcha: TwoCaptcha, id_captcha: int):
    from sites.ibConsig.ItauConsultaRefin.data.collections import registro_erros_form_identificacao_refin
    mensagem_erro: str
    try:
        loc_erro = '//*[@id="global-msg"]/li'
        sleep(2)
        mensagem_erro: str = act.obter_texto(loc_erro, By.XPATH)
        mensagem_erro = mensagem_erro.strip()
        print("Erro:", mensagem_erro)
    except TimeoutException:
        print("Preenchido sem erros")
        return False

    if not mensagem_erro:
        return

    mensagens = registro_erros_form_identificacao_refin()

    for mensagem in mensagens:
        regex = re.compile(mensagem['texto'])
        erro_encontrado = regex.search(mensagem_erro)

        if not erro_encontrado:
            continue

        if 'aprovar' in mensagem:
            print("Captcha Aprovado")
            captcha.mudar_status_captcha(id_captcha, '1')
        else:
            print("[CR] Catpcha Recusado")
            captcha.mudar_status_captcha(id_captcha, '2')
            raise CaptchaRecusadoException("Captcha recusado")
        if 'preencher' in mensagem:
            raise CaptchaRecusadoException("Captcha Recusado")

        if 'finalizar' in mensagem or 'localizar' in mensagem or 'localizado' in mensagem:
            raise NotFoundResultException(mensagem_erro)


def tratar_alerts_refinanciamento(driver: Chrome, act: SeleniumActions, texto_alerta: str = False):
    import re
    if not texto_alerta:
        try:
            alert = driver.switch_to.alert
            texto_alerta = alert.text

        except Exception:
            return

    print("Mensagem encontrada: {}".format(texto_alerta))

    mensagens = registro_erros_forms_refin()
    for mensagem in mensagens:
        if 'Sistema temporariamente indisponível' in texto_alerta:
            driver.get('https://www.ibconsigweb.com.br/Index.do?method=prepare')
            raise Exception(texto_alerta)

        regex = re.compile(mensagem['texto'])
        alerta_encontrado = regex.search(texto_alerta)

        if not alerta_encontrado:
            continue
        try:
            act.manusear_alerta('aceitar')
        except UnexpectedAlertPresentException:
            act.manusear_alerta('aceitar')

        act.fechar_alertas_recursivamente()
        print("depois tentar fechar 3", mensagem)
        if 'selecionar' in mensagem:
            raise PularCheckboxException(
                "Não foi possível consultar o refinanciamento")

        if 'restricao' in mensagem:
            print(mensagem)
            act.fechar_alertas_recursivamente()
            raise RestricaoException(mensagem)

        if 'localizar' in mensagem:
            raise NotFoundResultException(mensagem)

        if 'clicar' in mensagem:
            return

        if 'pular' in mensagem:
            raise Exception(mensagem)

        if 'return' in mensagem:
            return

        sleep(60)
        raise Exception(mensagem)


def comparar_taxas_de_origem(taxas_option: str, taxa_contrato: float, margem_erro = 0, tipo = 'entre_ou_taxa_maior') -> bool:
    import re
    taxas_str: List[str] = re.findall(r"\d+,\d+", taxas_option)

    if not taxas_str:
        taxas_str: List[str] = re.findall(r"\d+.\d+", taxas_option)
        if not taxas_str:
            return False

    taxas_flt: List[float] = [float(x.replace(",", ".")) for x in taxas_str]

    taxas_flt.sort()

    if len(taxas_flt) == 2:
        if(tipo == 'entre_taxas'):
            if('DIG Inss/Refin Port-Min2000-Tx 1,80-1,70' in taxas_option and taxa_contrato > taxas_flt[1]):
                return True
            return taxas_flt[0] <= taxa_contrato + margem_erro <= taxas_flt[1]
        else:            
            if(taxa_contrato + margem_erro >= taxas_flt[1]):
                return True
            else:
                return taxas_flt[0] <= taxa_contrato + margem_erro <= taxas_flt[1]
    elif len(taxas_flt) == 1:
        return taxas_flt[0] <= taxa_contrato + margem_erro


def comparar_valores_contrato(valores_options: str, valor_contrato: float) -> bool:
    import re

    valores_str: List[str] = re.findall(r"\d+\.\d+", valores_options)

    # TODO: refatorar
    if 730 < valor_contrato < 1200:
        valor_contrato = 1200
        print(f"Valor do contrato ({valor_contrato}) 'arredondado' para 1000.00")
    elif valor_contrato < 450:
        valor_contrato = 450
        print(f"Valor do contrato ({valor_contrato}) 'arredondado' para 450.00")

    if not valores_str:
        valores_str: List[str] = re.findall(r"\d{3,10}", valores_options)

    if not valores_str:
        return False

    valores_flt: List[float] = [float(x.replace(".", "")) for x in valores_str]
    print(f"Valor Contrato: {valor_contrato}. Valor(es) Tabela: {valores_flt}")
    valores_originais = valores_flt 

    if len(valores_flt) == 3:
        return valores_flt[0] <= round(valor_contrato) <= valores_flt[1]

    if len(valores_flt) == 2:
        if(valores_originais[0] > valores_originais[1]):
            return valores_flt[0] <= round(valor_contrato)

    valores_flt.sort()

    if len(valores_flt) == 2:

        if(valores_originais[0] > valores_originais[1]):
            return valores_flt[0] <= round(valor_contrato)
        else:
            return valores_flt[0] <= round(valor_contrato) <= valores_flt[1]

    elif len(valores_flt) == 1:
        if(valores_flt[0] == 1200 and round(valor_contrato) > 3000):
            return False
        return valores_flt[0] <= round(valor_contrato)


