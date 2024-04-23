import pdb

from selenium.webdriver import Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, InvalidElementStateException,TimeoutException
from time import sleep

from sites.baseRobos.core.DebugTools import DebugTools
from sites.baseRobos.core.decorators import AguardarHorarioComercial

from dados.APIDataSource import APIDataSource

HORARIO_COMERCIAL = 8, 20

dbg: DebugTools = DebugTools(debugging=False)

URL_LOGIN = (r"https://panconsig.pansolucoes.com.br/")


@AguardarHorarioComercial(*HORARIO_COMERCIAL)
def login(driver: Chrome, cpf_login: str, senha: str, parceiros="003442"):

    act: SeleniumActions = SeleniumActions(driver, time_out=10)

    try:
        driver.get(URL_LOGIN)
    except:
        sleep(30)
        driver.quit()


    logado = preencher_usuario(driver, act, cpf_login)

    if not logado:
        #driver.delete_all_cookies()
        driver.get(URL_LOGIN)
        logado = preencher_usuario(driver, act, cpf_login)
        #sleep(2)

        preencher_campo_parceiros(act, parceiros)
        #sleep(2)



        preencher_campo_senha(act, senha)
        #sleep(2)
        act.time_out = 0.5

        forcar_clique_entrar(act)

        print(act.obter_texto_alerta())

        sleep(2)
        print(act.obter_texto_alerta())
        act.manusear_alerta('aceitar')



def preencher_usuario(driver: Chrome, act: SeleniumActions, cpf_login: str, rec=0):
    sleep(2)
    if rec > 1500:
        raise InvalidElementStateException
    try:
        print("Usuário:", cpf_login)
        #loc_cpf = "#txtCPF_CAMPO"
        loc_cpf = "/html/body/login-page/main/div/div/div[3]/app-login-form/form/mahoe-input[1]/label/span[2]/input"
        #act.enviar_texto(loc_cpf, cpf_login, clear=True)
        #act.enviar_texto_intervalado(loc_cpf, cpf_login, clear=True, delay=0.5)
        act.enviar_texto_intervalado(loc_cpf, cpf_login, By.XPATH)
        #act.press_TAB(loc_cpf)
        #act.enviar_texto_intervalado(loc_cpf, cpf_login, clear=True)
        sleep(2)

        #act.press_enter(loc_cpf)
        #sleep(0)

        #act.press_TAB(loc_cpf)
        #sleep(0)

    except StaleElementReferenceException:
        return preencher_usuario(driver, act, cpf_login, rec+1)
    except InvalidElementStateException:
        return preencher_usuario(driver, act, cpf_login, rec+1)
    except TimeoutException:
        print("Verificando se usuário está logado...")
        if '?FISession' in driver.current_url:
            return True
        else:
            print('Site não abriu...Aguardando 2 minutos...')
            sleep(120)
            driver.get(URL_LOGIN)
            return preencher_usuario(driver, act, cpf_login, rec+1)
        

def preencher_campo_parceiros(act: SeleniumActions, parceiros: str, rec=0):
    sleep(2)
    if rec > 5:
        raise InvalidElementStateException
    try:
        try:
            act.clicar_elemento('//*[@id="onetrust-accept-btn-handler"]', By.XPATH)
        except:
            pass

        sleep(2)
        loc_par = '//*[@id="form-partner"]'
        #act.select_drop_down(loc_par, parceiros)
        act.clicar_elemento(loc_par, By.XPATH)

        for i in act.retornar_elementos('.combo-option'):
            if parceiros in i.text:
                sleep(1)
                act.clicar_elemento(i.get_attribute('id'), By.ID)

        #act.press_enter(loc_par)
        #act.press_TAB(loc_par)
        act.clicar_elemento('//*[@id="formulario"]/app-login-form/form/div[4]/div/mahoe-button', By.XPATH)
    except StaleElementReferenceException:
        return preencher_usuario(act, parceiros, rec+1)
    except InvalidElementStateException:
        return preencher_usuario(act, parceiros, rec+1)




def preencher_campo_senha(act: SeleniumActions, senha: str, rec=0):
    sleep(2)
    if rec > 5:
        raise InvalidElementStateException
    try:
        
        try:
            loc_entrar_primeiro = '//*[@id="formulario"]/app-login-form/form/div[2]/div/mahoe-button/button'
            act.press_enter(loc_entrar_primeiro, By.XPATH)
            sleep(10)
        except:
            pass
        print("Senha:", senha)

        if(act.quantidade_elemento('/html/body/login-page/app-leitura-qr-code-login/main/div[2]/div/qrcode/div/canvas', By.XPATH) == 1):
            print('FAZER BIOMETRIA - 90s...')
            payload = {"telefoneDDD": '31993448917', "area" : "autotarefa_robo" ,"mensagem": act.obter_texto('/html/body/login-page/app-leitura-qr-code-login/main/div[2]/a/span',By.XPATH) ,"key": "f9223937d6a342a75fa449a2e5bbd75b"}
            response = APIDataSource().post_request_v2('enviar-mensagem-whatsapp', payload)
            sleep(90)
            return preencher_usuario(act, senha, rec+1)

        #loc_senha = "#ESenha_CAMPO"
        loc_senha = "/html/body/login-page/main/div/div/div[3]/app-login-form/form/mahoe-input[2]/label/span[2]/input"
        #act.enviar_texto(loc_senha, senha, clear=False)
        act.enviar_texto_intervalado(loc_senha, senha, By.XPATH)
        loc_entrar = '//*[@id="formulario"]/app-login-form/form/div[4]/div[2]/mahoe-button/button'
        act.press_enter(loc_entrar, By.XPATH)
        #act.press_enter(loc_entrar)
        #act.press_TAB(loc_senha)
        
    except StaleElementReferenceException:
        return preencher_usuario(act, senha, rec+1)
    except InvalidElementStateException:
        return preencher_usuario(act, senha, rec+1)


def forcar_clique_entrar(act: SeleniumActions):
    while True:
        try:
            act.manusear_alerta('aceitar')
            loc_entrar = '//*[@id="lnkEntrar"]'
            act.forcar_clique_stale_element(loc_entrar, By.XPATH)
            act.manusear_alerta('aceitar')
            print(act.obter_texto_alerta())
        except Exception as e:
            return


def verificar_sessao_login(driver: Chrome, aguardar=False) -> bool:
    print("Verificando se usuário está logado...")
    if '/Login/AC.UI.LOGIN' in driver.current_url:
        if aguardar:
            print("Usuario deslogado. Aguardando:")
            aguardar_n_segundos(1200)

        return False
    else:
        return True


def aguardar_n_segundos(segundos: int):
    print(f"Aguardando {segundos} segundos.")
    for i in range(1, segundos+1):
        sleep(1)

        print(f'\rSegundos: {i} de {segundos}.', end="")
    print()


if __name__ == "__main__":
    print(__name__)

