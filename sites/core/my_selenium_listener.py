from selenium.webdriver.support.events import AbstractEventListener
import re

class MyListener(AbstractEventListener):
    def __init__(self, url):
        self.url = url

    def before_navigate_to(self, url, driver):
        regex = re.compile("{}".format(self.url))
        url_encontrada = regex.search(url)

        if url_encontrada:
            print("Update página")
        print("Antes de abrir a url %s" % url)

    def after_navigate_to(self, url, driver):
        print("Depois de abrir a url %s" % url)

    def before_click(self, element, driver):
        print("Antes de clicar no elemento")

    def after_click(self, element, driver):
        print("Depois de clicar no elemento")

    def before_close(self, driver):
        print("Antes de fechar a pagina")

    def after_close(self, driver):
        print("Depois de fechar a pagina")

    def on_exception(self, exeception, driver):
        print("Ocorreu um erro")
