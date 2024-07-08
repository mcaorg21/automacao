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
from selenium.common.exceptions import *
from sites.baseRobos.core.data_helpers import make_request
from selenium.webdriver.remote.webelement import WebElement
from sites.baseRobos.core.selenium_helper import SeleniumHelper
import pdb


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
        self.message = ("\n> Elemento não pôde ser encontrado, tente:\n" +
                        "1. Aumentar o 'time_out', ou\n" +
                        "2. Verificar se o seletor está correto.")

    @property
    def time_out(self):
        return self.__time_out

    @time_out.setter
    def time_out(self, valor):
        self.__time_out = valor

    def clicar_elemento(self, seletor: str, metodo: object = By.CSS_SELECTOR):
        """
        Realiza um clique no elemento buscado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) selenium.webdriver.common.by.By.METODO.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.element_to_be_clickable((metodo, seletor)),
            message=self.message
        ).click()

    def enviar_texto(self, seletor: str, texto: str, metodo: object = By.CSS_SELECTOR, clear: bool = True):
        """
        Recebe o seletor do elemento e o metodo de busca.
        Por padrão, limpa o campo antes de enviar os caracteres.
        :param seletor: seletor do elemento web.
        :type seletor: str
        :param texto: texto a ser enviado para o campo.
        :type texto: str
        :param metodo: propriedade da classe selenium.webdriver.common.by.By.
        :type metodo: object
        :param clear: apaga o campo quando == True.
        :type clear: bool
        """
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        if clear:
            input_element.clear()
        input_element.send_keys(texto)

    def enviar_texto_intervalado(self, seletor: str, texto: str, metodo: object = By.CSS_SELECTOR, clear: bool = True,
                                 delay: float = 0.2):
        """
        Envia o texto para o campo inserindo um intervalo entre cada
        caractere.
        :param seletor: (str) seletor do elemento web.
        :param texto: (str) texto a ser enviado para o campo.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param clear: (bool) apaga o campo quando == True.
        :param delay: (float) intervalo entre cada caractere.
        """
        try:
            input_element = WebDriverWait(self.driver, self.__time_out).until(
                EC.visibility_of_element_located((metodo, seletor)),
                message=self.message
            )
            if clear:
                input_element.clear()

            for char in texto:
                sleep(delay)
                input_element.send_keys(char)

        except StaleElementReferenceException:
            input_element = WebDriverWait(self.driver, self.__time_out).until(
                EC.element_to_be_clickable((metodo, seletor)),
                message=self.message
            )
            if clear:
                input_element.clear()

            for char in texto:
                sleep(delay)
                input_element.send_keys(char)

    def enviar_texto_intervalado_uma_vez(self, seletor: str, texto: str, metodo: object = By.CSS_SELECTOR, clear: bool = True,
                                 delay: float = 0.2):
        """
        Envia o texto para o campo inserindo um intervalo entre cada
        caractere.
        :param seletor: (str) seletor do elemento web.
        :param texto: (str) texto a ser enviado para o campo.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param clear: (bool) apaga o campo quando == True.
        :param delay: (float) intervalo entre cada caractere.
        """
        try:
            input_element = WebDriverWait(self.driver, self.__time_out).until(
                EC.visibility_of_element_located((metodo, seletor)),
                message=self.message
            )
            if clear:
                input_element.clear()

            for char in texto:
                sleep(delay)
                input_element.send_keys(char)
                
        except StaleElementReferenceException:
            pass

    def buscar_quantidade_elemento(self, seletor):
        return self.driver.execute_script("""return $('%s').length""" % (seletor))

    def quantidade_elemento(self, seletor: str, metodo: object = By.CSS_SELECTOR, not_0=False) -> int:
        """
        Recebe o seletor do elemento e o metodo de busca. Retorna a
        quantidade de elementos encontrados na página, representados
        pelo seletor recebido.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (int) quantidade de elementos encontrados.
        """
        try:
            elements = WebDriverWait(self.driver, self.__time_out).until(
                lambda x: x.find_elements(metodo, seletor)
            )
            return len(elements)
        except TimeoutException:
            if not_0:
                raise TimeoutException
            return 0

    def obter_atributo(self, seletor: str, atributo: str, metodo: object = By.CSS_SELECTOR) -> str:
        """
        Recebe o seletor e o atributo do elemento e o metodo de busca.
        Retorna o atributo do elemento selecionado.
        :param seletor: (str) seletor do elemento web.
        :param atributo: (str) atributo desejado.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) atributo do elemento buscado.
        :rtype: str
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.get_attribute(atributo)

    def verificar_atributo(self, seletor, atributo, metodo=By.CSS_SELECTOR):
        """
        Recebe o seletor e o atributo do elemento e o metodo de busca.
        Retorna o atributo do elemento selecionado.
        :param seletor: (str) seletor do elemento web.
        :param atributo: (str) atributo desejado.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) atributo do elemento buscado.
        """
        try:
            elemento = WebDriverWait(self.driver, self.__time_out).until(
                EC.visibility_of_element_located((metodo, seletor)),
                message=self.message
            )
            elemento.get_attribute(atributo)
            return True
        except Exception as e:
            print(e)

    def obter_propriedade(self, seletor: str, propriedade: str, metodo: object = By.CSS_SELECTOR) -> str:
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

    def obter_texto(self, seletor: str, metodo: object = By.CSS_SELECTOR) -> str:
        """
        Recebe o seletor do elemento e o metodo de busca. Retorna o
        texto contido no elemento.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :return: (str) texto do elemento buscado.
        :rtype: str
        """
        elemento = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        return elemento.text

    def obter_valor(self, seletor: str, metodo: object = By.CSS_SELECTOR):
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

    def aplicar_valor_a_atributo(self, seletor: str, atributo: str, valor: str, metodo: object = By.CSS_SELECTOR):
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

    def select_drop_down(self, seletor, valor, metodo=By.CSS_SELECTOR, name=None):
        """
        Seleciona a opçao do menu dropdown de acordo com o valor em seu
        atributo <value>.
        :param seletor: (str) seletor do elemento web.
        :param valor: (str) valor da opçao a ser selecionada.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        select = Select(WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor))
        ))

        if name is not None:
            select.select_by_visible_text(valor)
        else:
            select.select_by_value(valor)

    def retornar_opcoes_select(self, seletor, metodo=None) -> WebElement:
        """
        Retorna uma lista com as opções do menu select representado pelo
        parâmetro <seletor>.
        :type seletor: str
        :param metodo: método de uma instância da classe selenium.webdriver.common.by.By.
        :type metodo: object
        :return:
        """
        select_by = ""
        if metodo is None:
            select_by = SeleniumActions.inferir_metodo_seletor(seletor)
            print("inferido ", select_by)
        else:
            select_by = metodo
            print("secolihdo ", select_by)

        return Select(WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((select_by, seletor))
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

    def press_shift_enter(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <ctrl A> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.SHIFT + Keys.RETURN)

    def press_ctrl_A(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <ctrl A> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.CONTROL+"A")

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

    def press_TAB(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <Enter> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.TAB)

    def press_UP(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <Enter> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.ARROW_UP)

    def press_DOWN(self, seletor, metodo=By.CSS_SELECTOR):
        """
        Pressiona a tecla <Enter> no elemento elecionado.
        :param seletor: (str) seletor do elemento web.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        """
        WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        ).send_keys(Keys.ARROW_DOWN)

    def press_backspace(self, seletor, loop=1, metodo=By.CSS_SELECTOR, delay=0.1, end=False):
        """
        Pressiona a tecla <Backspace> no elemento selecionado. Permite que a tecla seja pressionada
        um <loop> numero de vezes e de forma intervalada.
        :param seletor: (str) seletor do elemento web.
        :param loop: (int) vezes em que será pressionado o botao.
        :param metodo: (function) metodo da classe selenium.webdriver.common.by.By.
        :param delay: (float) intervalo entre cada inserçao.
        """
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.element_to_be_clickable((metodo, seletor)),
            message=self.message
        )
        if end:
            input_element.send_keys(Keys.END)
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
            return True
        except Exception as e:
            return False

    def trocar_frame_referencia(self, referencia, metodo=By.ID):
        """
        Alterna o controle para o frame selecionado de acordo com sua referencia,
        que pode ser o nome ou id do frame desejado.
        :type referencia: str
        :param referencia: nome ou id do frame.
        :type metodo: object
        :param metodo: selenium.webdriver.common.by.By
        """

        if referencia.lower() == 'default':
            self.driver.switch_to.default_content()
            return True
            
        try:
            frame = WebDriverWait(self.driver, self.__time_out).until(
                EC.visibility_of_element_located((metodo, referencia)),
                message=self.message
            )
            if referencia.lower() == 'default':
                self.driver.switch_to.default_content()
                return True

            self.driver.switch_to.frame(frame)
            return True
        except Exception as e:

            print("Frame Inexistente", end=' ')
            return False

    def manusear_alerta(self, acao='rejeitar'):
        """
        Aceita ou rejeita um alerta apresentado pelo navegador.
        Por padrao, rejeita o alerta.
        :param acao: (str) 'rejeitar' para fechar alerta, 'aceitar'
                    para aceitar alerta.
        """
        try:
            if self.verificar_existencia_alerta():
                if acao == 'rejeitar':
                    Alert(self.driver).dismiss()
                elif acao == 'aceitar':
                    Alert(self.driver).accept()
                else:
                    print("Entrar apenas com 'rejeitar' ou 'aceitar'.")
            else:
                print("Alerta não encontrado.")
        except Exception as e:
            print("Alerta não encontrado." + str(e))

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

    def retornar_elemento(self, seletor: str, metodo: str = By.CSS_SELECTOR) -> WebElement:
        """Retorna o elemento web representado pelo respectivo seletor"""
        return WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor))
        )

    def retornar_elementos(self, seletor: str, metodo: str = By.CSS_SELECTOR) -> list:
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

    def verificar_existencia_alerta(self, rtype='bool'):
        """
        Verifica se um alerta foi apresentado pelo navegador.
        :param rtype: Pode assumir dois valores: <bool> ou <text>. Se <bool>,
                    determina que a função retorne True, caso o alerta seja
                    encontrado. Se <text>, retorna o texto do alerta.
        :return:
        """
        try:
            if rtype == 'bool':
                WebDriverWait(self.driver, self.time_out).until(
                    EC.alert_is_present())
                return True
            elif rtype == 'text':
                text = self.obter_texto_alerta()
                return text
        except Exception:
            return False

    def retornar_janela_principal(self):
        try:
            sleep(0.2)
            self.driver.switch_to.window(self.driver.window_handles[0])
            sleep(0.2)
        except NoSuchWindowException:
            return

    def trocar_janela(self, idx_janela=1, numero_janelas=2, verb=False):
        """
        Aguarda até que uma nova janela seja aberta. Por isso, é necessário entrar com o
        número de janelas esperado. Desta forma, caso se espera que uma janela seja aberta
        além da principal, o parâmetro <numero_janelas> deve ser 2 e o parametro <ordem_janelas>
        deve ser 1 (índice do segundo elemento da lista de window_handles).
        :param ordem_janela: (int) o número da janela a ser selecionada nas window_handles.
        :param numero_janelas: (int) o número esperado de janelas abertas.
        :param verb: (bool) se True, escreve os parâmetros: Nº janelas abertas e  Ordem janela selecionada.
        """
        if verb:
            print(
                f"Nº janelas abertas: {len(self.driver.window_handles)}. "
                f"Index janela selecionada: {idx_janela}"
            )
        try:
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(numero_janelas))
            self.driver.switch_to.window(self.driver.window_handles[idx_janela])
        except NoSuchWindowException:
            return "Janela não encontrada"
        except TimeoutException:
            return "Janela não encontrada"
        except IndexError:
            return "Janela não encontrada"

    def fechar_janela(self, ordem_janela=-1):
        """
        Por padrão fecha a última janela.
        :param ordem_janela: (int) posição ordinal da janela em ordem de abertura.
                            [0 = principal, 1 = 1ª a ser aberta,..., n = nª a ser aberta];
        """
        self.driver.switch_to.window(self.driver.window_handles[ordem_janela])
        self.driver.close()

    def verificar_n_janelas(self, n_esperado):
        """
        Verificar se o número de janelas foi alterado.
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

    def anexar_documento(self, abs_file_path, seletor_escolher_arquivo, seletor_submit="",
                         metodo_by=By.CSS_SELECTOR):
        """
        :param abs_file_path: (str) caminho absoluto do arquivo
        :param seletor_escolher_arquivo: (str) seletor do botão para escolha do arquivo.
        :param seletor_submit: (str) seletor do botao de confirmação da escolha.
        :param metodo_by: (<class selenium.webdriver.common.by>.metodo) padrão = By.CSS_SELECTOR.
        """
        self.enviar_texto(seletor_escolher_arquivo, abs_file_path, metodo=metodo_by)
        if seletor_submit:
            self.clicar_elemento(seletor_submit, metodo=metodo_by)

    def esta_presente(self, seletor, metodo=None, VERB=False):
        """ Verifica se um determinado elemento está presente no DOM. """
        if metodo is None:
            metodo = SeleniumActions.inferir_metodo_seletor(seletor)
            print("inferido ", metodo)

        try:
            self.retornar_elemento(seletor, metodo)
            if VERB:
                print("Elemento encontrado.")
            return True
        except Exception:
            if VERB:
                print("Elemento ausente.")
            return False

    def verificar_campos_vazios(self, seletores_campos, metodo=By.CSS_SELECTOR, t=1, t_max=5):
        """
        Verifica se algum dos campos de texto está vazio. Caso esteja, retorna o seletor de cada
        campo, caso contrário, retorna False.
        :type seletores_campos: list or tuple
        :type metodo: object
        :param metodo: selenium.webdriver.common.by.By
        :type t: int
        :param t_max: quantidade máxima de recursões permitidas em
                decorrência de erros por StaleElement.
        :type t_max: int
        """
        lista_campos_vazios = []
        try:
            for seletor in seletores_campos:
                if self.obter_valor(seletor, metodo) == "":
                    lista_campos_vazios.append(seletor)

            if lista_campos_vazios:
                return lista_campos_vazios
            else:
                return False
        except StaleElementReferenceException:
            if t > t_max:
                self.verificar_campos_vazios(seletores_campos, metodo, t + 1, t_max)

    def preencher_varios_campos(self, lista_tuplas_seletor_valor, metodo=By.CSS_SELECTOR):
        """
        Recebe uma <list> de <tuples>, com cada tupla contendo um par (seletor, valor).
        :type lista_tuplas_seletor_valor: list
        :param lista_tuplas_seletor_valor: lista de tuplas (seletor, valor)
        :type metodo: object
        :param metodo: selenium.webdriver.common.by.By
        """
        for seletor, valor in lista_tuplas_seletor_valor:
            sleep(0.2)
            self.enviar_texto(seletor, valor, metodo)

    def abrir_nova_aba(self, url='about:blank'):
        """
        Abre uma nova aba redirecionada à url escolhida. Por padrão,
        redireciona para about:blank.
        :param url:
        :return: None
        """
        self.driver.execute_script(f"window.open(arguments[0]);", url)

    def esperar_alert_retornar_texto(self):
        """
        Retorna o texto de um alerta utilizando Wait.until
        :return: None
        """
        try:
            WebDriverWait(self.driver, self.time_out).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            return alert.text
        except TimeoutException as e:
            print(e)

    def aguardar_diponibilidade_elemento(self, seletor, metodo, max_segs=3):
        # TODO: ESTA FUNÇÃO DEVE SER REVISADA COM A POSSIBILIDADE DE SE RETIRAR O
        #   LAÇO FOR E UTILIZAR WAIT(...).UNTIL(EC)
        """
        Aguarda a disponibilidade de um elemento web por um tempo de
        <max_segs> segundos ou até que o elemento esteja disponível.
        :param seletor:
        :param metodo:
        :param max_segs:
        :return:
        """
        elemento = self.retornar_elemento(seletor, metodo)
        print(f"Aguardando disponibilidade do elemento...",
              end='')
        for i in range(1, max_segs + 1):
            try:
                if EC.staleness_of(elemento):
                    elemento.click()
                    print("\r", end="")
                    return True

            except Exception as e:
                print(f"\rErro: {i}", end="")

            print(f"\r> {i}s", end=' ')
            if i == max_segs:
                print("\r", end="")
                return False

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

    def clicar_preencher_campo(self, seletor, texto, metodo=By.CSS_SELECTOR, clear=True):
        """
          :param seletor: seletor do elemento web.
          :type seletor: str
          :param texto: texto a ser enviado para o campo.
          :type texto: str
          :param metodo: propriedade da classe selenium.webdriver.common.by.By.
          :type metodo: object
          :param clear: apaga o campo quando == True.
          :type clear: bool
          """
        self.clicar_elemento(seletor, metodo)
        self.enviar_texto(seletor, texto, metodo, clear)

    def forcar_clique_stale_element(self, localizador, metodo=By.CSS_SELECTOR, t_max=5, t=1, pause=0.5):
        # TODO: refatorar para futuramente substituir parâmetros opcionais por **kwargs
        """
        Força o clique em elementos que estejam temporariamente indisponíves para
        interação. Pode substituir a utilização de funções JQuery/JS para lidar com
        event handlers como 'onblur', 'onfocus' e 'onchange'.
        :param pause:
        :type localizador: str
        :type metodo: object
        :param t_max: número máximo de recursões
        :type t_max: int
        :type t: int
        :return: None
        """
        self.aguardar_diponibilidade_elemento(localizador, metodo, max_segs=1)
        try:
            self.hover_e_clique(localizador, metodo, pause=pause)
        except StaleElementReferenceException as e:
            if t >= t_max:
                self.forcar_clique_stale_element(localizador, metodo, t_max=5, t=t + 1)
        except TimeoutException as e:
            if t >= t_max:
                self.forcar_clique_stale_element(localizador, metodo, t_max=5, t=t + 1)

    def forcar_preenchimento_cb(self, seletor, metodo=By.CSS_SELECTOR, rec=1, max_recs=5):
        """
        Verifica se o check_box ou radio button foi selecionado com sucesso.
        Caso não tenha sido selecionado, a função é chamada recursivamente até
        que o campo tenha sido selecionado com sucesso.
        :type seletor: str
        :type metodo: str
        :param rec: numero da atual recursão
        :param max_recs: número máximo de recursões
        :rtype: bool
        """
        try:
            selected = self.retornar_elemento(seletor, metodo).is_selected()
            print('\rProduto selecionado?', selected, end='')
            if not selected and rec < max_recs:  # tentar preencher novamente
                self.hover_e_clique(seletor, metodo, pause=1)
                return self.forcar_preenchimento_cb(seletor, metodo, rec=rec + 1)
            elif rec > 5:  # maximo de recursões alcançado, erro.
                raise Exception("Máximo de recursões alcançado.")
            else:  # campo preenchido com sucesso.
                print(" Preenchido.")
                return True
        except StaleElementReferenceException:
            return self.forcar_preenchimento_cb(seletor, metodo, rec + 1, max_recs)

    def preencher_enquanto_vazio(self, seletor, texto, metodo=By.CSS_SELECTOR, rec=1, max_recs=5):
        """
        Tenta preencher um campo até que ele seja preenchido com sucesso ou até que se alcance
        o número máximo de recursões.
        :type seletor: str
        :type metodo: str
        :param rec: numero da atual recursão
        :param max_recs: número máximo de recursões
        """
        try:
            self.aplicar_valor_a_atributo(seletor, 'value', texto, metodo)
            if rec > max_recs:
                return False
            if self.obter_valor(seletor, metodo) != texto:
                return self.preencher_enquanto_vazio(seletor, texto, metodo, rec + 1)
        except StaleElementReferenceException:
            return self.preencher_enquanto_vazio(seletor, texto, metodo, rec + 1)

    def trigger_event_handler(self, seletor, metodo, *event_handlers):
        if not event_handlers:
            return False

        elemento = self.retornar_elemento(seletor, metodo)
        print(elemento.text, '<')
        for handler in event_handlers:
            if 'onchange' in handler:
                self.driver.execute_script("arguments[0].onchange()", elemento)
            if 'onfocus' in handler:
                self.driver.execute_script("arguments[0].onfocus()", elemento)
            if 'onclick' in handler:
                self.driver.execute_script("arguments[0].onclick()", elemento)
            if 'onblur' in handler:
                self.driver.execute_script("arguments[0].onblur()", elemento)

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
        print("Id Captcha: ", resultado.json()['request'])

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

        self.driver.execute_script(
            f'document.getElementById("g-recaptcha-response").innerHTML = "{solucao.json()["request"]}"')

        if callback != '':
            #$('.button-submit').click()
            self.driver.execute_script(f'{callback}();')
            self.driver.execute_script("""$('.button-submit').click()""")

    def hcaptcha(self, data_sitekey, callback=''):
        """
           :param data_sitekey: Key do reCaptcha do site
           :param callback: Nome da função callback
           """
        in_data = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "method": "hcaptcha",
            "sitekey": data_sitekey,
            "pageurl": self.driver.current_url,
            "json": 1
        }
        resultado = make_request("GET", "https://2captcha.com/in.php",
                                 params_data=in_data, msg="Em <reCaptcha_v2>")

        print("Id Captcha: ", resultado.json()['request'])

        sleep(20)
        out_data = {
            "key": "6c2a0fc387a4d92fae18d23ca833130f",
            "action": "get",
            "id": resultado.json()["request"],
            "json": 1
        }
        solucao = make_request("GET", "https://2captcha.com/res.php",
                               params_data=out_data, msg="Em <hCaptcha_v2>")

        while solucao.json()['request'] == "CAPCHA_NOT_READY":
            solucao = make_request("GET", "https://2captcha.com/res.php",
                                   params_data=out_data, msg="Em <hCaptcha_v2>")
            sleep(5)

        if solucao.json()['request'] == "ERROR_CAPTCHA_UNSOLVABLE":
            print('XXXXXX Reiniciando a consulta... CAptcha não pode ser resolvido XXXXXX')
            return False    

        print('Resultado:' + solucao.json()['request'])

        id_recaptcha = self.driver.execute_script("""return $('textarea')[0].id""").split('-')[-1]

        #self.driver.execute_script( f'document.getElementById("g-recaptcha-response-{id_recaptcha}").innerHTML = "{solucao.json()["request"]}"')

        self.driver.execute_script(f'document.getElementById("h-captcha-response-{id_recaptcha}").innerHTML = "{solucao.json()["request"]}"')

        if callback != '':
            self.driver.execute_script(f'{callback}();')
            return True


    def esta_presente_recursivo(self, loc_elemento, metodo=By.CSS_SELECTOR, rec=1, max_rec=100):
        if rec >= max_rec:
            raise Exception(f"Máximo de recursões [{rec}] atingido.")

        if self.esta_presente(loc_elemento, metodo) and rec < max_rec:
            print("\rLoading \\", end="")
            sleep(1)
            print(f"\rLoading |", end="")
            sleep(1)
            print(f"\rLoading /", end="")
            sleep(1)
            print(f"\rLoading -", end="")
            sleep(1)
            print("\rLoading \\", end="")
            sleep(1)
            print(f"\rLoading |", end="")
            sleep(1)
            print(f"\rLoading -", end="")
            sleep(1)

            return self.esta_presente_recursivo(loc_elemento, metodo, rec + 1)
        else:
            print("\r", end='')
            return False

    def nao_esta_presente_recursivo(self, loc_elemento, metodo=By.CSS_SELECTOR, rec=1, max_rec=10):
        if not self.esta_presente(loc_elemento, metodo) and rec < max_rec:
            print("\rLoading \\", end="")
            sleep(0.3)
            print(f"\rLoading |", end="")
            sleep(0.3)
            print(f"\rLoading /", end="")
            sleep(0.3)
            print(f"\rLoading -", end="")
            sleep(0.3)
            print("\rLoading \\", end="")
            sleep(0.3)
            print(f"\rLoading |", end="")
            sleep(0.3)
            print(f"\rLoading -", end="")
            sleep(0.3)

            return self.nao_esta_presente_recursivo(loc_elemento, metodo, rec + 1)
        elif rec > max_rec:
            return False
        else:
            print("Elemento encontrado.")
            return True

    def teste(self, seletor, texto, metodo, t=1, t_max=5):
        try:
            a = ActionChains(self.driver)
            elemento = self.retornar_elemento(seletor, metodo)
            a.move_to_element(elemento).click(elemento).pause(2).send_keys(texto).pause(2).release(
                elemento)
        except StaleElementReferenceException as e:
            if t >= t_max:
                self.forcar_clique_stale_element(seletor, metodo, t_max=5, t=t + 1)
                print()
        except TimeoutException as e:
            if t >= t_max:
                self.forcar_clique_stale_element(seletor, metodo, t_max=5, t=t + 1)
                print()

    def press_down(self, seletor, metodo, loop=1):
        input_element = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        for _ in range(loop):
            input_element.send_keys(Keys.BACKSPACE)

    def enviar_caracteres(self, seletor: str, texto: str, **kwargs):
        """
        Envia os caracteres de um string para o campo de texto do espectivo
        seletor passado como parâmetro.
        :param seletor: (str) seletor do elemento web.
        :param texto: (str) texto a ser enviado para o campo.
        :type kwargs:
        :param kwargs:

        """
        metodo: str = kwargs.get('metodo', By.CSS_SELECTOR)
        clear: bool = kwargs.get('clear', True)
        delay: float = kwargs.get('delay', 0.02)
        change: bool = kwargs.get('change', False)

        input_element: object = WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, seletor)),
            message=self.message
        )
        if clear:
            input_element.clear()

        for char in texto:
            sleep(delay)
            input_element.send_keys(char)

        if change:
            self.driver.execute_script(
                "arguments[0].onchange()",
                self.retornar_elemento(seletor, metodo)
            )

    def fechar_alertas_recursivamente(self):
        i = 0
        while self.verificar_existencia_alerta() and i < 5:
            print("Alerta presente")
            sleep(0.5)
            alert = self.driver.switch_to.alert
            sleep(0.5)
            alert.dismiss()

    def check_box_is_checked(self, loc: str, metodo: str = By.CSS_SELECTOR):
        checkbox: WebElement = self.retornar_elemento(loc, metodo)
        return checkbox.is_selected()

    def check_box_is_enabled(self, loc: str, metodo: str = By.CSS_SELECTOR):
        checkbox: WebElement = self.retornar_elemento(loc, metodo)
        return checkbox.is_enabled()

    def obter_texto_opcao_selecionada(self, loc: str, metodo: str=By.CSS_SELECTOR) -> str:
        opt = Select(WebDriverWait(self.driver, self.__time_out).until(
            EC.visibility_of_element_located((metodo, loc))
        )).first_selected_option

        return opt.text

    @staticmethod
    def inferir_metodo_seletor(seletor: str) -> str:
        import re

        if re.match(r"/{2}\w+|/{2}\*", seletor):
            return By.XPATH
        elif re.match(r"\w+\[|\*\[|#\w+|\.\w+|\[\w+", seletor):
            return By.CSS_SELECTOR
