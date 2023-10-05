#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| file: /sites/novosaque/main.py

| projeto: automacao-python
| data: 2021-12-27
| autor: Marcelo Amancio
"""
import pdb,sys, shutil
from selenium.webdriver import Chrome

import PATHS

from sites.baseRobos.core.helpers import definir_nome_robo
from sites.cora.libs.FormLogin import FormLogin
from sites.cora.main import IniciarEmissaoConsulta

from time import sleep

class IniciarLogin():

    def __init__(self):  

        self.base_path: str = PATHS.project_path()        
        self.driver_path: str = PATHS.driver_path()
        self.path_arquivo = PATHS.project_path()+"\\cora\\pix_boleto\\"  
        self.user_driver_path: str = PATHS.project_path()+"/chrome_user_dir/CoraEmissoes_"  

    def login(self):

        definir_nome_robo("Cora - Logins")

        for user in range(4,12):
            print('Logando usuario: ' + str(user) + ' de 12')
            try:
                self.driver = IniciarEmissaoConsulta().inciar_chrome(Chrome, "multiplo", user)
                login = FormLogin.realizar_login(self.driver)
            except:
                shutil.rmtree(self.user_driver_path+str(user))
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Erro criar de pasta XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                self.driver = IniciarEmissaoConsulta().inciar_chrome(Chrome, "multiplo", user)
                login = FormLogin.realizar_login(self.driver)
                #continue
                pass
            self.driver.quit()

        print('Aguardando 3 minutos...')
        sleep(180)  
        self.login()         

if __name__ == '__main__':
    run = IniciarLogin()
    run.login()
