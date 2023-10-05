"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: selenium_actions.py
| data: 20/10/2019
| autor: Gustavo Belleza

| funcionamento:
  Contem açoes comumente utilizadas na automação utilizando Selenium Webdriver.
"""
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core.data_helpers import make_request


class SeleniumActions:
    """
    > Metodos:
      * o metodo de busca por elementos web é, por padrao, By.CSS_SELECTOR. Isso
      pode ser alterado utilizando-se algum dos metodos da classe By, do modulo
      <selenium.webdriver.common.by> *
      - @property
        time_out(self)
      - @time_out.setter
        time_out(self, valor)
      - clicar_elemento(self, seletor, metodo=By.CSS_SELECTOR)
      - enviar_texto(self, seletor, texto, metodo=By.CSS_SELECTOR, clear=True)
      - enviar_texto_intervalado(self, seletor, texto, metodo=By.CSS_SELECTOR, clear=True, delay=0.5)
      - quantidade_elemento(self, seletor, metodo=By.CSS_SELECTOR)
      - obter_atributo(self, seletor, atributo, metodo=By.CSS_SELECTOR)
      - obter_propriedade(self, seletor, propriedade, metodo=By.CSS_SELECTOR)
      - obter_texto(self, seletor, metodo=By.CSS_SELECTOR)
      - obter_valor(self, seletor, metodo=By.CSS_SELECTOR)
      - aplicar_valor_a_atributo(self, seletor, atributo, valor, metodo=By.CSS_SELECTOR)
      - obter_link(self, seletor)
      - select_drop_down(self, seletor, valor, metodo=By.CSS_SELECTOR)
      - retornar_opcoes_select(self, seletor, valor, metodo=By.CSS_SELECTOR)
      - press_enter(self, seletor, metodo=By.CSS_SELECTOR)
      - trocar_frame_seletor(self, seletor, metodo=By.CSS_SELECTOR)
      - trocar_frame_referencia(self, referencia)
      - manusear_alerta(self, acao='rejeitar')
      - entrar_texto_alerta(self, texto)
      - obter_texto_alerta(self)
      - hover_menu_dropdown(self, seletor, metodo=By.CSS_SELECTOR)
      - verificar_existencia_alerta()
      - trocar_janela(self, ordem_janela=1, numero_janelas=2, verb=False)

    > Atributos:
      - self.driver: (class) selenium.webdriver.WebDriver.
      - self.wait: (class) selenium.webdriver.support.wait.WebDriverWait.
      - self.message: (str) menssagem quando a busca pelo elemento web
        ultrapassa o time_out.
    """

    def __init__(self, driver, time_out=4):
        self.driver = driver
        self.__time_out = time_out
        self.message = ("\n> Elemento não pôde ser encotrado, tente:\n" +
                        "1. Aumentar o 'time_out', ou\n" +
                        "2. Veirificar se o seletor está correto.")

    @property
    def time_out(self):
        return self.__time_out

    @time_out.setter
    def time_out(self, valor):
        self.__time_out = valor

    def clicar_elemento(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Realiza um clique no elemento buscado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) selenium.webdriver.common.by.By.METODO.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.element_to_be_clickable((metodo, seletor)),
            message=self.message
        ).click()

    def enviar_texto(self, seletor, texto, metodo=By.CSS_SELECTOR, clear=True):
        """
        Recebe o seletor do elemento e o metodo de busca.
        Por padrão, limpa o campo antes de enviar os caracteres.
        :param seletor: (str) seletor do elemento web.
        :param texto: (str) texto a ser enviado para o campo.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param clear: (bool) apaga o campo quando == True.
        """
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        if clear:
            input_element.clear()
        input_element.send_keys(texto)

    def executar_acao_elemento(self, seletor, metodo=By.CSS_SELECTOR):
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )

        pdb.set_trace()

        input_element.send_keys(Keys.PAGE_DOWN)

    def enviar_texto_intervalado(self, seletor, texto, metodo=By.CSS_SELECTOR, clear=True, delay=0.2):
        """
        Envia o texto para o campo inserindo um intervalo entre cada
        caractere.
        :param seletor: (str) seletor do elemento web.
        :param texto: (str) texto a ser enviado para o campo.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param clear: (bool) apaga o campo quando == True.
        :param delay: (float) intervalo entre cada caractere.
        """
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        if clear:
            input_element.clear()

        for char in texto:
            sleep(delay)
            input_element.send_keys(char)

    def buscar_quantidade_elemento(self, seletor):
        return self.driver.execute_script("""return $('%s').length""" % (seletor))

    def quantidade_elemento(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor do elemento e o metodo de busca. Retorna a
        quantidade de elementos encontrados na página, representados
        pelo seletor recebido.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (int) quantidade de elementos encontrados.
        """
        elements = WebDriverWait(self.driver, self.__time_out).until(
            lambda x: x.find_elements(metodo, seletor)
        )
        return len(elements)

    def obter_atributo(self, seletor, atributo, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor e o atributo do elemento e o metodo de busca.
        Retorna o atributo do elemento selecionado.
        :param seletor: (str) seletor do elemento web.
        :param atributo: (str) atributo desejado.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) atributo do elemento buscado.
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.get_attribute(atributo)

    def obter_propriedade(self, seletor, propriedade, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor e a propriedade do elemento e o metodo de busca. Retorna a
        propriedade do elemento selecionado.
        :param seletor: (str) seletor do elemento web.
        :param propriedade: (str) atributo desejado.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) propriedade do elemento buscado.
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.get_property(propriedade)

    def obter_texto(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor do elemento e o metodo de busca. Retorna o
        texto contido no elemento.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) texto do elemento buscado.
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.text

    def obter_valor(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor do elemento e o metodo de busca. Retorna o
        atributo <value> contido no elemento.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) atributo <value> do elemento buscado.
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.get_attribute("value")

    def aplicar_valor_a_atributo(self, seletor, atributo, valor, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor do elemento, o atributo a ser modificado, o valor
        a ser aplicado e o metodo de busca. Aplica o valor ao atributo
        contido no elemento buscado.
        :param seletor: (str) seletor do elemento web.
        :param atributo: (str) atributo cujo valor sera modificado.
        :param valor: (str) valor a ser aplicado ao atributo.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        self.driver.execute_script(
            "arguments[0].setAttribute(arguments[1],arguments[2])",
            elemento, atributo, valor
        )

    def obter_link(self, seletor):
        """
        Retorna o link do elemento encontrado de acordo com o
        seletor escolhido.
        :param seletor: (str) seletor do elemento web.
        :return: (str) link.
        """
        return self.obter_atributo(seletor, 'href')

    def select_drop_down(self, seletor, valor, metodo=By.CSS_SELECTOR):
        """
        Seleciona a opçao do menu dropdown de acordo com o valor em seu
        atributo <value>.
        :param seletor: (str) seletor do elemento web.
        :param valor: (str) valor da opçao a ser selecionada.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        Select(WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor))
        )).select_by_value(valor)

    def retornar_opcoes_select(self, seletor, metodo=By.CSS_SELECTOR):
        return Select(WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor))
        )).options

    def press_enter(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <Enter> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.RETURN)

    def press_pagedown(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <Enter> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.PAGE_DOWN)

    def press_backspace(self, seletor, loop=1, metodo=By.CSS_SELECTOR, delay=0.1):
        """
        Pressiona a tecla <Backspace> no elemento elecionado. Permite que a tecla seja pressionada
        um <loop> numero de vezes e de forma intervalada.
        :param seletor: (str) seletor do elemento web.
        :param loop: (int) vezes em que será pressionado o botao.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param delay: (float) intervalo entre cada inserçao.
        """
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        for _ in range(loop):
            sleep(delay)
            input_element.send_keys(Keys.BACKSPACE)

    def trocar_frame_seletor(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Alterna o controle para o frame selecionado, após achar seu elemento
        correspondente.
        :param seletor: (str) seletor do elemento web correspondente ao frame.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        try:
            self.driver.switch_to.default_content()
            frame = WebDriverWait(self.driver, self.__time_out).until(
                EC.visibility_of_element_located((metodo, seletor)),
                message=self.message
            )
            self.driver.switch_to.frame(frame)
        except Exception as e:
            print(e)

    def trocar_frame_referencia(self, referencia):
        """
        Alterna o controle para o frame selecionado de acordo com sua referencia,
        que pode ser o nome ou id do frame desejado.
        :param referencia: (str) nome ou id do frame.
        """
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(referencia)
        except Exception as e:
            print(e)

    def manusear_alerta(self, acao='rejeitar'):
        """
        Aceita ou rejeita um alerta apresentado pelo navegador.
        Por padrao, rejeita o alerta.
        :param acao: (str) 'rejeitar' para fechar alerta, 'aceitar'
                    para aceitar alerta.
        """
        if self.verificar_existencia_alerta():
            if acao == 'rejeitar':
                Alert(self.driver).dismiss()
            elif acao == 'aceitar':
                Alert(self.driver).accept()
            else:
                print("Entrar apenas com 'rejeitar' ou 'aceitar'.")
        else:
            print("Alerta não encontrado.")

    def entrar_texto_alerta(self, texto):
        """
        Envia um texto para o campo de texto de uma caixa de alerta.
        :param texto: (str) texto a ser entrado no alerta.
        """
        if self.verificar_existencia_alerta():
            Alert(self.driver).send_keys(texto)
        else:
            print("Alerta não encontrado.")

    def obter_texto_alerta(self):
        """Retorna o texto constante na caixa de alerta."""
        if self.verificar_existencia_alerta():
            return Alert(self.driver).text

    def retornar_elemento(self, seletor, metodo=By.CSS_SELECTOR):
        """Retorna o elemento web representado pelo respectivo seletor"""
        return WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor))
        )

    def retornar_elementos(self, seletor, metodo=By.CSS_SELECTOR):
        """Retorna uma lista com os elementos representados pelo seletor inserido"""
        return WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_all_elements_located((metodo, seletor))
        )

    def hover_menu_dropdown(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Simula o 'passar do mouse' por um menu drop down, no intuito de
        expandir seu conteudo.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return:
        """
        menu = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        hover = ActionChains(self.driver).move_to_element(menu)
        hover.perform()


    def hover_e_clique(self, seletor: str, metodo: str = By.CSS_SELECTOR, pause: float = 0.5):
        """
        Simula o passar do mouse por cima de um elemento seguido de um clique.
        :type seletor: str
        :type metodo: object
        :param pause: tempo de duração da ação 'hover'.
        :type pause: float
        :return: None
        """
        botao = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        hover = ActionChains(self.driver).move_to_element(botao)
        hover.pause(pause).click().perform()

    def verificar_existencia_alerta(self):
        try:
            WebDriverWait(self.driver, self.time_out).until(
                EC.alert_is_present()
            )
            return True
        except:
            return False

    def trocar_janela(self, ordem_janela=1, numero_janelas=2, verb=False):
        """
        :param ordem_janela: (int) o número da janela a ser selecionada nas window_handles.
        :param numero_janelas: (int) o número esperado de janelas abertas.
        :param verb: (bool) se True, escreve os parâmetros: Nº janelas abertas e  Ordem janela selecionada.
        """
        if verb:
            print(f"Nº janelas abertas: {len(self.driver.window_handles)}. Ordem janela selecionada: {ordem_janela}")
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(numero_janelas))
        self.driver.switch_to.window(self.driver.window_handles[ordem_janela])

    def fechar_janela(self, ordem_janela=-1):
        """
        :param ordem_janela: (int) posição ordinal da janela em ordem de abertura.
                            [0 = principal, 1 = 1ª a ser aberta,..., n = nª a ser aberta];
        """
        self.driver.switch_to.window(self.driver.window_handles[ordem_janela])
        self.driver.close()

    def verificar_n_janelas(self, n_esperado):
        """
        :param n_esperado: (int) quantidade de janelas esperadas.
        :return: (bool) se n_esperado == n_real: True.
                        se não: False.
        """
        try:
            WebDriverWait(self.driver, self.time_out).until(
                EC.number_of_windows_to_be(n_esperado))
            return True
        except TimeoutException:
            return False

    def anexar_documento(self, abs_file_path, seletor_escolher_arquivo, seletor_submit='', metodo_by=By.CSS_SELECTOR):
        """
        :param abs_file_path: (str) caminho absoluto do arquivo
        :param seletor_escolher_arquivo: (str) seletor do botão para escolha do arquivo.
        :param seletor_submit: (str) seletor do botao de confirmação da escolha.
        :param metodo_by: (<class selenium.webdriver.common.by>.metodo) padrão = By.CSS_SELECTOR.
        """
        self.enviar_texto(seletor_escolher_arquivo, abs_file_path, metodo=metodo_by)
        if seletor_submit:
            self.clicar_elemento(seletor_submit, metodo=metodo_by)

    def reCaptcha(self, pointer, file):
        """
        Começo do post request
        """
        in_data = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "method": "base64",
            "body": file,
            "json": 1
        }
        id_captcha = make_request("POST", "https://2captcha.com/in.php", params_data=in_data)
        try:
            print(id_captcha.json()['request'])      
        except ValueError:
            print('Value Error')
            while ValueError:
                id_captcha = make_request("POST", "https://2captcha.com/in.php", params_data=in_data)
        """
        fim do post request
        """
        sleep(10)
        
        """
        começo do get request
        """
        payload = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "action": "get",
            "id": id_captcha.json()['request']
        }
        
        captcha_token = make_request("GET", "https://2captcha.com/res.php", params_data=payload).text
        while captcha_token == "CAPCHA_NOT_READY":
            captcha_token = make_request("GET", "https://2captcha.com/res.php", params_data=payload).text
       
        """
        fim do get request
        """
        captcha_token = captcha_token.replace('O', '', 1).replace('K', '', 1).replace('|', '', 1)
        return captcha_token
        
    
    def reCaptcha_v2(self, data_sitekey, callback=''):
        """
        :param data_sitekey: Key do reCaptcha do site
        :param callback: Nome da função callback
        """
        
        in_data = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "method": "userrecaptcha",
            "googlekey": data_sitekey,
            "pageurl": self.driver.current_url,
            "json": 1
        }
        resultado = make_request("GET", "https://2captcha.com/in.php",
                                 params_data=in_data, msg="Em <reCaptcha_v2>")
        try:
            print("Id Captcha: ", resultado.json()['request'])
        except ValueError:
            print('ValueError')
            resultado = make_request("GET", "https://2captcha.com/in.php",
                                 params_data=in_data, msg="Em <reCaptcha_v2>")
        sleep(20)
        out_data = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "action": "get",
            "id": resultado.json()["request"],
            "json": 1
        }
        solucao = make_request("GET", "https://2captcha.com/res.php",
                               params_data=out_data, msg="Em <reCaptcha_v2>")
        
        while solucao.json()['request'] == "CAPCHA_NOT_READY":
            solucao = make_request("GET", "https://2captcha.com/res.php",
                                   params_data=out_data, msg="Em <reCaptcha_v2>")
            sleep(5)
            
        try:
            self.driver.execute_script(
            f'document.getElementById("g-recaptcha-response-1").innerHTML = "{solucao.json()["request"]}"')
        except:
            pass
        self.driver.execute_script(
            f'document.getElementById("g-recaptcha-response").innerHTML = "{solucao.json()["request"]}"')

        if callback != '':
            self.driver.execute_script(f'{callback}();')

