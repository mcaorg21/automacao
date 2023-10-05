from sites.baseRobos.core.selenium_actions import SeleniumActions, By
from sites.baseRobos.core.data_helpers import similaridade
from sites.pan.pan_consulta_refin import registros_erros_refin
from selenium.common.exceptions import (
    NoAlertPresentException, UnexpectedAlertPresentException
)
from time import sleep
import re,pdb
from selenium.webdriver import Chrome


def aguardar_loading(act: SeleniumActions, by: By):
    loc_loading: str = '//*[@id="ctl00_Image2"]'
    act.esta_presente_recursivo(loc_loading, by.XPATH)

def aguardar_loading_card_ofertas(act: SeleniumActions, by: By):
    loc_loading: str = '//*[@id="div-loading"]'
    act.esta_presente_recursivo(loc_loading, by.XPATH)

def aguardar_loading_consultar(act: SeleniumActions, by: By):
    loc_loading: str = '/html/body/div[5]/div/div'
    act.esta_presente_recursivo(loc_loading, by.XPATH) 

def verificar_alertas(driver: Chrome, time_out = 1, tipo_form = 'formulario_comum'):

    act: SeleniumActions = SeleniumActions(driver, time_out=1)

    if(tipo_form == 'formulario_simulacao'):
        act.verificar_existencia_alerta()

    if act.verificar_existencia_alerta():
        texto_alerta: str = act.obter_texto_alerta()
        print("Alerta encontrado: ", texto_alerta)
        tratar_mensagens_sistema(act, texto_alerta)


def tratar_mensagens_sistema(act: object, texto: str) -> bool:
    print("Comparando textos de erro...")

    # Mensagens pré-definidas e respectivas tratativas
    mensagens: dict = registros_erros_refin()

    sleep(1)
    #pdb.set_trace()
    # Comparando a mensagem do alerta com as mensagens pré-definidas
    for infos in mensagens:
        comp_re: bool = bool(re.search(infos['texto'], texto))
        comp_in: bool = texto in infos['texto']
        comp_levs_dist: int = similaridade(texto, infos['texto']) >= 80
        print('-------------------------------------'),
        print(texto)
        print(comp_re)
        print(comp_in)
        print(comp_levs_dist)
        print('-------------------------------------')
        if comp_in or comp_re or comp_levs_dist:
            
            if 'InfoNotFound' in infos:
                act.manusear_alerta('aceitar')
                raise NotFoundResultException(texto)
            elif 'Restricao' in infos:
                act.manusear_alerta('aceitar')
                raise RestricaoException(texto)
            elif 'Preenchimento' in infos:
                raise PreenchimentoException(texto)
            elif 'MatriculaErrorPensionista' in infos:
                raise DadosIdentificacaoIncorretosException('005001', '803419')
            elif 'MatriculaErrorServidor' in infos:
                raise DadosIdentificacaoIncorretosException('005000', '801676')
            elif 'Continue' in infos:
                try:
                    act.manusear_alerta('aceitar')
                except UnexpectedAlertPresentException:
                    print("Alerta não foi aberto.")
                except NoAlertPresentException:
                    print("Alerta não foi aberto.")
                return True


class DadosIdentificacaoIncorretosException(Exception):
    def __init__(self, empregador, orgao):
        self.empregador_corrigido = empregador
        self.orgao_corrigido = orgao


class RestricaoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class NotFoundResultException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class PreenchimentoException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class PreenchimentoTabelaException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

