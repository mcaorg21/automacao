from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

import time
import pickle

class SeleniumHelper():
    def __init__(self, driver):
        self.driver = driver

    def buscar_quantidade_elemento(self, seletor):
        return self.driver.execute_script("""return $('%s').length""" % (seletor))

    def buscar_quantidade_elemento_somente_tela(self, seletor):
        return self.driver.execute_script("""return $('%s:visible').size()""" % (seletor))

    def verificar_texto_campo_jquery(self, seletor):
        return self.driver.execute_script("""return $('%s').text()""" % (seletor))

    def verificar_valor_campo_jquery(self, seletor):
        return self.driver.execute_script("""return $('%s').val()""" % (seletor))

    def verificar_atributo_campo_jquery(self, seletor, atributo):
        return self.driver.execute_script("""return $('%s').attr('%s')""" % (seletor, atributo))

    def atribuir_valor_atributo_jquery(self, seletor, atributo, valor):
        self.driver.execute_script("""$('{}').attr('{}', '{}')""".format(seletor, atributo, valor))

    def verificar_propriedade_css(self, seletor, prop):
        return self.driver.execute_script("""return $('%s').prop('%s')""" % (seletor, prop))

    def criar_link_elemento(self, seletor):
        return self.verificar_atributo_campo_jquery(seletor, 'href')

    def clicar_elemento(self, seletor):
        self.driver.execute_script("""$('%s').click()""" % (seletor))

    def atribuir_valor_campo_jquery(self, seletor, valor, change=False, blur=False):
        self.driver.execute_script("""$('%s').val("%s")""" % (seletor, valor))

        if (change):
            self.change_campo_jquery(seletor)
        elif (blur):
            self.blur_campo_jquery(seletor)
    
    def change_campo_jquery(self, seletor):
	    self.driver.execute_script("""$('%s').trigger('change')""" % (seletor))

    def blur_campo_jquery(self, seletor):
	    self.driver.execute_script("""$('%s').trigger('blur')""" % (seletor))

    def verificar_valor_campo_driver(self, seletor):
        return self.driver.find_element(By.CSS_SELECTOR,seletor).get_attribute('value')

    def verificar_texto_campo_driver(self, seletor):
        return self.driver.find_element(By.CSS_SELECTOR,seletor).text

    def select_valor(self, seletor, valor):
        select = Select(self.driver.find_element(By.CSS_SELECTOR,seletor))
        select.select_by_value(valor)

    def atribuir_valor_campo_driver(self, seletor, valor):
        #field = self.driver.find_element(By.CSS_SELECTOR,seletor)
        self.driver.find_element(By.CSS_SELECTOR,seletor)
        field.clear()
        field.send_keys(valor)

    def press_enter(self, seletor):
        self.driver.find_element(By.CSS_SELECTOR,seletor).send_keys(Keys.RETURN)

    def atribuir_valor_campo_tab(self, valor, seletor=False, field=False):
        if field is False:
            field = self.driver.find_element(By.CSS_SELECTOR,seletor)

        action_chains = ActionChains(self.driver)
        action_chains.click(field)
        action_chains.send_keys(valor)
        action_chains.send_keys(Keys.TAB)
        action_chains.perform()

    def clicar_elemento_driver(self, seletor, scroll=True):
        try:
            elemento = self.driver.find_element(By.CSS_SELECTOR,seletor)

            action_chains = ActionChains(self.driver)
            action_chains.click(elemento).perform()
            time.sleep(1)
        except Exception:
            if scroll is False:
                return
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            self.clicar_elemento_driver(seletor, scroll=False)

    def selecionar_frame(self, seletor):
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(
                self.driver.find_element(By.CSS_SELECTOR,seletor))
        except Exception as e:
            print(e)

    def trocar_frame(self, frame_name,id=False):
        try:
            self.driver.switch_to.default_content()
            if(id):
                self.driver.switch_to.frame(self.driver.find_element(By.ID,frame_name))    
            else:
                self.driver.switch_to.frame(self.driver.find_element(By.NAME,frame_name))
        except Exception as e:
            print(e)

    def load_cookies(self, cookies_path, delete=False):
        if delete:
            self.driver.delete_all_cookies()
        for cookie in pickle.load(open(cookies_path, "rb")):
            self.driver.add_cookie(cookie)

    def save_cookies(self, cookies_path):
        pickle.dump(self.driver.get_cookies(), open(cookies_path, "wb"))
        print(self.driver.get_cookies())

    def load_cookies_robo_web_admin(self, url, id_robo):
        dados = {
                    'id_robo' : id_robo,
                }
        
        cookies = json.loads(requests.post(url, data=dados).text)
        return cookies

