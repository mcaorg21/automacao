import pdb, sys
sys.path.append('../../')
#sys.path.append('../')
from sites.baseRobos.core.data_helpers import similaridade
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from sites.core.selenium_actions import SeleniumActions
from time import sleep


class Automacao():
    def __init__(self, driver):
        self.act = SeleniumActions(driver)
        pass

    
    def loading(self):
        while True:
            try:
                self.act.obter_texto('/html/body/div[1]/div[23]/div/div/div', By.XPATH)
            except:
                break        
    
    
    def lidar_beneficiarios(self, dados):
        if len(dados['beneficiarios']) >= 1:
            for i in range(1, len(dados['beneficiarios']) + 1):
                self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[4]/div/div/nav/div/button', By.XPATH)
                self.act.enviar_texto('//*[@id="app"]/div[8]/div/div/div[2]/div/div[1]/div/div/div[1]/div/input', dados['beneficiarios'][f'beneficiario_{i}']['nome'], By.XPATH)
                self.act.clicar_elemento('//*[@id="app"]/div[8]/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]', By.XPATH)
                qtd_div = self.act.quantidade_elemento('//*[@id="app"]/div[9]/div/div/div', By.XPATH)
                if  dados['beneficiarios'][f'beneficiario_{i}']['parentesco'] == 'Mae':
                     dados['beneficiarios'][f'beneficiario_{i}']['parentesco'] = 'Mãe'
                for j in range(1, qtd_div + 1):
                    if self.act.obter_texto(f'//*[@id="app"]/div[9]/div/div/div[{j}]/a/div/div', By.XPATH) == dados['beneficiarios'][f'beneficiario_{i}']['parentesco']:
                        self.act.clicar_elemento(f'//*[@id="app"]/div[9]/div/div/div[{j}]/a/div/div', By.XPATH)
                        break
                self.act.enviar_texto('//*[@id="app"]/div[8]/div/div/div[2]/div/div[5]/div/div[2]/div[1]/div/input',  dados['beneficiarios'][f'beneficiario_{i}']['repasse'], By.XPATH)
                self.act.clicar_elemento('//*[@id="app"]/div[8]/div/div/div[3]/button[2]', By.XPATH)
        else:
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[3]/form/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]', By.XPATH)

            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]', By.XPATH)


    def pagamento_seguro(self, nome, dados_pagamento):
        if dados_pagamento['tipo'] == 'cartao':
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[1]/div/div/div[2]/a', By.XPATH)
            sleep(5)
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div/div/div/div[1]/div/input', dados_pagamento['dados']['numero'], By.XPATH)
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[2]/div/div/div/div[1]/div/input', dados_pagamento['dados']['nomeCartao'], By.XPATH)
            try:
                status = self.act.obter_texto('/html/body/div[2]/div/div/div[1]/div[1]/p', By.XPATH)
            except:
                status = None
            if status:
                return status
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/div[1]', By.XPATH)
            for i in range(7, 13):
                if self.act.obter_texto(f'//*[@id="app"]/div[6]/div/div/div[{i}]/a/div/div', By.XPATH) == dados_pagamento['dados']['mesValidade']:
                        self.act.clicar_elemento(f'//*[@id="app"]/div[6]/div/div/div[{i}]/a/div/div', By.XPATH)
                        break
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div[1]/div[1]/div[1]', By.XPATH)
            for i in range(1, 11):
                if self.act.obter_texto(f'//*[@id="app"]/div[5]/div/div/div[{i}]/a/div/div', By.XPATH) == dados_pagamento['dados']['anoValidade'][2:]:
                    self.act.clicar_elemento(f'//*[@id="app"]/div[5]/div/div/div[{i}]/a/div/div', By.XPATH)
                    break
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[3]/div[3]/div/div/div[1]/div/input', dados_pagamento['dados']['cvv'], By.XPATH)
            pdb.set_trace()
            print(similaridade(dados_pagamento['dados']['nomeCartao'], nome))
            if similaridade(dados_pagamento['dados']['nomeCartao'], nome) >= 70:
                self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[2]/div/div/div/div[1]/div/div[1]', By.XPATH)
            else:
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[2]/div/form/div[1]/div/div/div[1]/div/input', 'CPF', By.XPATH)
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[2]/div/form/div[2]/div/div/div[1]/div/input', dados_pagamento['dados']['nomeCartao'], By.XPATH)

        else:   
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[1]/div/div/div[4]/a', By.XPATH)
            switch_bancos = {
                "001" : '1',
                "033" : '2',
                "104" : '3',
                "237" : '4',
                "341" : '5'
            }
            dados_pagamento['dados']['numeroBanco'] = '001'
            dados_pagamento['dados']['agencia'] = '8549'
            dados_pagamento['dados']['numeroConta'] = '2122'
            dados_pagamento['dados']['digitoConta'] = '5'
            id_banco = switch_bancos[dados_pagamento['dados']['numeroBanco']]
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[3]/form/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]', By.XPATH)
            self.act.clicar_elemento(f'//*[@id="app"]/div[4]/div/div/div[{id_banco}]/a/div/div', By.XPATH)
            pdb.set_trace()
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[3]/form/div/div/div[2]/div[1]/div/div/div[1]/div/input', dados_pagamento['dados']['agencia'] + str(dados_pagamento['dados']['digitoAgencia']), By.XPATH)
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[3]/form/div/div/div[2]/div[3]/div/div/div[1]/div/input', dados_pagamento['dados']['numeroConta'] + dados_pagamento['dados']['digitoConta'], By.XPATH)
            # Validade
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[1]/div[2]/div/div[3]/form/div/div/div[3]/div/div/div/div[1]/div[1]/div[1]', By.XPATH)
            self.act.clicar_elemento('//*[@id="app"]/div[4]/div/div/div[1]/a/div/div', By.XPATH)
            # Proponente que paga
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[2]/div/div/div/div[1]/div/div[1]', By.XPATH)
        
        
