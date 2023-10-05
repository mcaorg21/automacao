from time import sleep
from sites.baseRobos.gui_auto import AutoGUI
import pdb

def aguardar_load_cookies(driver: object, sh: object, act: object,  cks_path: str):
    from selenium.webdriver.common.by import By
    cnt = 0
    loc = '//*[@id="wrapper"]/section/div/div[1]/div/div/img'
    deslogado = act.esta_presente(loc, By.XPATH)
    while deslogado and cnt < 100:
        sh.load_cookies(cks_path)
        print("Aguardando cookies...")
        driver.refresh()
        sleep(5)
        cnt += 1
        deslogado = act.esta_presente(loc, By.XPATH)


def verificar_tempo_execucao(**kwargs):
    from datetime import datetime

    ultima_atualizacao = kwargs.get('ultima_atualizacao')
    timer = kwargs.get('timer')
    uconecte = kwargs.get('uconecte')
    id_robo = kwargs.get('id_robo')

    time_between_updates = (datetime.now() - ultima_atualizacao).seconds
    print("Tempo entre atualizações: {}".format(time_between_updates))
    print("Timer: {} segundos".format(timer))

    if time_between_updates < 60:
        wait_time = timer - time_between_updates
        print("Esperando {} segundos antes de recomeçar a fila!".format(wait_time))

        if wait_time > 0:
            sleep(wait_time)

        timer += 1
    else:
        timer -= 1

    uconecte.atualizar_status_robo(id_robo)

    return datetime.now()


def criar_pasta_usuario_chrome(user_path):
    import os
    try:
        os.makedirs(user_path)
    except OSError:
        print("Pasta o usuário chrome não precisou ser criada, pois já existe.")

def verificar_loading(act, interacoes=35, aguardar = False):
    while (act.buscar_quantidade_elemento('#divLoading\\:visible') == 1):
        print('Aguardando Loading...' + str(interacoes))
        sleep(2)
        interacoes -= 1

class GerenciarSessao(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.estado = 0

    @property
    def estado_atual(self):
        return self.estado

    def verificar_estado(self):
        loc = '//*[@id="wrapper"]/section/div/div[1]/div/div/img'
        deslogado = self.act.esta_presente(loc, self.by.XPATH)

        if deslogado:
            print("Usuário não está logado.")
            self.estado = 0
        else:
            print("Usuário está logado.")
            self.estado = 1
        self.resolver_estado()

    def resolver_estado(self):
        print("Resolvendo estado...")
        if self.estado == 0:
            print("Interrompendo processos...")
            raise ErroSessaoOle("Necessário carregar novos cookies")
        elif self.estado == 1:
            print("Seguindo execução das tarefas.")

    def aguardar_load_cookies(self, cks_path: str, max_cnt: int=50):
        from selenium.webdriver.common.by import By
        cnt = 0
        loc = '//*[@id="wrapper"]/section/div/div[1]/div/div/img'
        deslogado = self.act.esta_presente(loc, By.XPATH)
        while deslogado and cnt < max_cnt:
            self.sh.load_cookies(cks_path)
            print("Aguardando cookies...")
            self.chrome_driver.refresh()
            sleep(30)
            cnt += 1
            deslogado = self.act.esta_presente(loc, By.XPATH)

        if cnt > max_cnt:
            raise ErroSessaoOle("Tempo para carregar cookies excedido.")


class ErroSessaoOle(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
