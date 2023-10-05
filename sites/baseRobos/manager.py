"""
| projeto: automacao-python
| arquivo: manager.py
| data: 21/11/2019
| autor: Gustavo Belleza

Contém atributos e métodos que permitem gerenciar as tarefas de automação. Aqui
são definidos os caminhos para o chromedriver.exe, as Options para a sessão do
driver bem como a inicialização da classe ChromeDriver.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import traceback
from sites.baseRobos.core.data_helpers import gen_log
import PATHS
from sites.baseRobos.core.helpers import aguardar_n_segundos, definir_nome_robo

import time


class Manager(object):
    """
    atributos de classe:
    PATH_VM = caminho para o chromedriver a ser utilizado na máquina virtual to projeto
    path_pc = caminho a ser utilizado em um computador com OS Windows.

    atributos de instância:
    self.options = instância da classe Options, do selenium.webdriver
    self._driver = atributo privado, uma instância do chromedriver
    self.cookies = caminho para salvar e carregar cookies
    self.path = o caminho a ser aplicado ao webdriver

    métodos:
    chrome_driver = getter self.driver
    chrome_driver = setter self.driver
    init_chrome_driver = inicializa o chromedriver
    set_options = estabelece as opções da sessão do driver.
    atualizar_pagina = atualiza a pagina a cada X segundos.
    """

    CHROME_DRIVER = PATHS.driver_path()

    contratos_consultados: dict = {}

    def __init__(self):
        self.options = Options()
        self._driver: webdriver.Chrome = None
        self.caminho_base = PATHS.project_path()
        self.parar_se_exception = True
        self.cookies = self.caminho_base + 'cookies.pkl'
        self.PATHS = PATHS
        self.__log_path = self.PATHS.project_path()

    @classmethod
    def driver_factory(cls, *options, **kwargs) -> webdriver.Chrome:
        man = Manager()
        man.set_options(*options)
        man.set_experimental_opts(**kwargs)
        man.init_chrome_driver()

        return man.driver

    @property
    def driver(self):
        if not self._driver:
            raise Exception(
                "Driver não inicializado. Inicie o Driver utilizando método: "
                "Manager.init_chrome_driver")
        return self._driver

    @property
    def chrome_driver(self):
        return self._driver

    @chrome_driver.setter
    def chrome_driver(self, driver):
        self._driver = driver

    @property
    def cookies_path(self):
        return self.cookies

    @cookies_path.setter
    def cookies_path(self, path):
        self.cookies = path

    @property
    def log_path(self):
        return self.__log_path

    @log_path.setter
    def log_path(self, path):
        self.__log_path += path

    def close_driver(self):
        print(f"Fechando todas janelas do driver e limpando os cookies.")
        try:
            self.driver.delete_all_cookies()
            self.driver.quit()
        except Exception as e:
            print("Em <Manager.close_driver>:", e)

    def deleta_cookies(self):
        print(f"Deletando cookies.")
        self.driver.delete_all_cookies()    

    def init_chrome_driver(self, import_driver: webdriver.Chrome = False):
        """
        Inicializa o chrome_driver e o atribui à ivar self._driver.
        O padrão é que o objeto webdriver seja inicializado dentro
        da própria classe por este método. No entanto, um outro
        webdriver pode ser passado como argumento para o parametro
        'import_driver', caso, por exemplo, se queira compartilhar
        uma sessão webdriver com outros robôs.
        """
        if not import_driver:

            self._driver: webdriver.Chrome = webdriver.Chrome(
                executable_path=self.CHROME_DRIVER,
                options=self.options
            )
        else:
            self._driver = import_driver

    def set_experimental_opts(self, **kwargs):
        if not kwargs:
            return

        for key, val in kwargs.items():
            self.options.add_experimental_option(key, val)

    def set_options(self, *arguments):
        """
        Adiciona os argumentos passados no parâmetro 'arguments'
        às 'options' do webdriver.
        """
        for arg in arguments:
            if not arg:
                continue
            self.options.add_argument(arg)

    @classmethod
    def consultar_todos_contratos_registrados(cls):
        print(f"Contratos registrados: {cls.contratos_consultados}")

    @classmethod
    def deletar_registro_contrato(cls, codigo_con):
        registro = cls.contratos_consultados.pop(codigo_con, None)
        if registro is not None:
            print(f"Contrato {codigo_con} excluido do registro")
        elif registro is None:
            print(f"Contrato {codigo_con} não constava no registro.")

    @classmethod
    def adicionar_contrato_trabalhado(cls, codigo_con: str) -> bool:
        contrato_registrado = cls.contratos_consultados.get(codigo_con, False)
        if not contrato_registrado:
            cls.contratos_consultados[codigo_con] = 0
            print(f"Contrato {codigo_con} adicionado ao registro")
            return True
        elif contrato_registrado:
            print(f"Contrato {contrato_registrado} já registrado")
            return False

    @classmethod
    def consultar_contrato_registrado(cls, codigo_con) -> int:
        registrado = cls.contratos_consultados.get(codigo_con, False)
        if registrado:
            print(f"Contrato {codigo_con} já foi consultado {registrado} vezes")
            return cls.contratos_consultados[codigo_con]
        else:
            print("Contrato ainda não foi consultado")
            return -1

    @classmethod
    def registrar_consulta_contrato(cls, codigo_con: str) -> bool:
        registrado = cls.contratos_consultados.get(codigo_con, False)
        if registrado:
            cls.contratos_consultados[codigo_con] += 1
            return True
        else:
            print(f"O contrato {codigo_con} ainda não foi registrado.")
            return False

    @staticmethod
    def criar_pasta_usuario_chrome(path: str):
        import os
        try:
            dir_path = path.replace("--user-data-dir=", "")
            print("Criando pasta:", dir_path)
            os.makedirs(dir_path)
        except OSError:
            print("Pasta do usuário chrome não precisou ser criada, pois já existe.")

    def manager_error_log(self, message):
        print("Registrando log", self.log_path)
        gen_log(message, f'{self.log_path}')
        return traceback.print_exc(file=open(f'{self.log_path}.log', 'a'))

    @staticmethod
    def manager_process_log(message, filename, modo):
        if modo == 'print' or modo == 'ambos':
            print(message)
        if modo == 'log' or modo == 'ambos':
            gen_log(message, filename)

    def atualizar_pagina(self, segs, freq_output):
        print(f"Aguardando {segs} segundos...")
        for i in range(0, segs+1, freq_output):
            print(f"{i} ", end="")
            time.sleep(freq_output)
        self._driver.refresh()
        print("\n...\n")
