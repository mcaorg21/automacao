from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sites.elementos import Chrome
from sites.baseRobos.core.selenium_actions import SeleniumActions
from time import sleep,time

import pdb

class FormLogin:
    
    def __init__(self, driver: Chrome, usuario: str, senha: str):
        self.driver: Chrome = driver
        self.usuario: str = usuario
        self.senha: str = senha

    def acessar_site(self):
        print("Acessando site")
        time.sleep(10)
        if "Home" in self.driver.title:
            print('Já logado!')
            return True
        
        sleep(5)
        self.driver.get("https://web.kapmug.com/")
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder=' ']"))
        )
        
        return False

    def preencher_login(self):
        campos_input = self.driver.find_elements(By.XPATH, "//input[@placeholder=' ']")
        if len(campos_input) >= 1:
            print(f"Preenchendo usuário: {self.usuario}")
            campos_input[0].clear()
            campos_input[0].send_keys(self.usuario)
        else:
            raise Exception("Campo de usuário não encontrado")

    def preencher_senha(self):
        campos_input = self.driver.find_elements(By.XPATH, "//input[@placeholder=' ']")
        if len(campos_input) >= 2:
            print(f"Preenchendo senha")
            campos_input[1].clear()
            campos_input[1].send_keys(self.senha)
        else:
            raise Exception("Campo de senha não encontrado")

    def clicar_acessar(self):
        print("Clicando no botão de acesso")
        sleep(5)
        botao = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Acessar')]")
        botao.click()
        

    def aguardar_resultado_login(self) -> bool:
         # Aguardar resultado do login (máximo 30 segundos)
        tempo_inicio = time()
        tempo_limite = 30  # segundos
        
        while time() - tempo_inicio < tempo_limite:
            # Verificar se ainda está na tela de carregamento
            
            if "Carregando" in self.driver.title:
                print("Aguardando carregamento...")
                sleep(2)
                continue
                
            # Verificar se voltou para a tela de login (falha)
            if "Login" in self.driver.title:
                print("Falha no login: Redirecionado para a página de login")
                self.driver.quit()
                return False
                
            # Se chegou aqui, provavelmente o login foi bem-sucedido
            print("Login realizado com sucesso!")
            
            # Capturar URL atual após login
            url_atual = self.driver.current_url
            print(f"URL após login: {url_atual}")
            
            sleep(10)
            
            # Capturar título da página após login
            titulo_atual = self.driver.title
            print(f"Título da página após login: {titulo_atual}")
            
            if('Home' in titulo_atual):
                print("Login realizado com sucesso!")
                return True
            else:
                print("Login falhou, redirecionado para a página de login")
                return False

    @staticmethod
    def realizar_login(driver: Chrome, usuario: str, senha: str) -> bool:
        # Capturar título da página após login
        titulo_atual = driver.title
        print(f"Título da página após login: {titulo_atual}")
            
        if('Home | Kapmug' in titulo_atual):
            print("Login realizado com sucesso!")
            return True
        
        try:
            login_kapmug = FormLogin(driver, usuario, senha)
            logado = login_kapmug.acessar_site()
            if(logado):
                return True
            login_kapmug.preencher_login()
            login_kapmug.preencher_senha()
            login_kapmug.clicar_acessar()
            resultado = login_kapmug.aguardar_resultado_login()
            return resultado
        except Exception as e:
            print(f"Erro durante o login: {str(e)}")
            try:
                driver.quit()
            except:
                pass
            return False

