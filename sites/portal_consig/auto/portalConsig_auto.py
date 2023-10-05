from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from sites.baseRobos.core import data_helpers as dh


class PortalConsigAuto(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.estado = None
        self.parar_se_exception = False
        self.modo_log = 'ambos'
        self.nome_log = 'portal_consig'

    def login_sistema(self, cpf, senha):
        """
        Resolve e insere os dados do captcha em seu devido campo. Insere os
        dados do usario nos campos 'CPF' e 'Senha'. Simula um clique no botão
        'Acessar'. Caso a inserçao do captcha esteja incorreta, esta função é
        chamada recursivamente até que o captcha seja inserido corretamente.
        """
        try:
            self.auto_process_log("Realizando o login no portal.", self.nome_log, self.modo_log)
            # Aba log admin
            loc_aba_log_admin = '//span[text()="Login Administrativo"]/..'  # XPATH
            self.act.clicar_elemento(loc_aba_log_admin, metodo=self.metodo.XPATH)

            # Captcha
            loc_captcha_img = 'img'
            loc_captcha_campo = 'input#captcha'
            id_captcha, captcha_resp = self.captcha.resolver_captcha(loc_captcha_img)
            self.act.enviar_texto(loc_captcha_campo, captcha_resp)
            self.captcha.mudar_status_captcha(id_captcha, '1')

            # Entrar senha
            loc_senha_input = 'input#password'
            self.act.enviar_texto(loc_senha_input, senha)

            # Entrar CPF
            loc_cpf_input = 'input[title="CPF"]'
            self.act.press_backspace(loc_cpf_input, loop=11, delay=0.05)
            self.act.enviar_texto(loc_cpf_input, cpf, clear=False)

            # Verficar se captcha foi resolvido corretamente de modo recursivo
            loc_erro = 'div#divEtapaError2'
            self.act.press_enter(loc_captcha_campo)

            try:
                self.act.retornar_elemento(loc_erro)
                self.auto_process_log("Erro ao escrever captcha.", self.nome_log, self.modo_log)
                self.login_sistema(cpf, senha)  # reiniciar login
            except:
                self.auto_process_log("Login realizado com sucesso", self.nome_log, self.modo_log)
            return True

        except Exception as e:
            self.auto_gui_error_log("Em <login_sistema>", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def selecao_perfil(self, estado):
        """
        Seleciona o perfil do servidor segundo seu estado no portal.
        As opções atuais são: São Paulo e Mato Grosso.
        :param estado: (str) pode assumir os valores 'SP' ou 'MT'.
        :return: void.
        """
        try:
            self.estado = estado
            print(f"\nSelecionando o perfil de {self.estado}")

            # Selecionar Perfil Servidor
            loc_botao_radio = ''
            if estado.lower() == 'sp':
                loc_botao_radio = 'input[value="radio8"]'
            elif estado.lower() == 'mt':
                loc_botao_radio = 'input[value="radio6"]'
            else:
                print("Selecione um estado válido: SP ou MT")

            # Selecionar Estado
            self.act.clicar_elemento(loc_botao_radio)

            # Acessar
            loc_botao_acessar = 'input.botaoAcessar'
            self.act.clicar_elemento(loc_botao_acessar)

            print(f"\nPerfil do estado de {self.estado} selecionado")

        except Exception as e:
            self.auto_gui_error_log("Em login_sistema", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def consultar_dados_servidor(self, cpf_servidor):
        try:
            # CONSULTA DADOS
            # Expandir menu 'consultar margem'
            self.auto_process_log("Iniciando consulta dos dados do servidor.",
                                  self.nome_log, self.modo_log)
            loc_expandir_menu = "//span[text()='Consulta de Margem']/.."
            self.act.clicar_elemento(loc_expandir_menu, metodo=By.XPATH)

            # Clicar no botao de consulta à margem
            loc_botao_consulta_margem = "a[href='/consignatario/pesquisarMargem']"
            self.act.clicar_elemento(loc_botao_consulta_margem)

            # Pesquisar a margem do servidor
            loc_cpf_input = 'input#cpfServidor'
            self.act.clicar_elemento(loc_cpf_input)
            self.act.enviar_texto_intervalado(loc_cpf_input, cpf_servidor,
                                              clear=False, delay=0.03)
            loc_botao_pesquisar = 'input[name="botaoPesquisar"]'
            self.act.clicar_elemento(loc_botao_pesquisar)

        except Exception as e:
            self.auto_gui_error_log("Em <consultar_dados_servidor>", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def scrape_dados_servidor(self, matricula=''):
        try:
            try:
                margem, status = 0, ''

                loc_resultados = '//span[text()="Resultado"]'
                quantidade_provs = self.act.quantidade_elemento(
                    loc_resultados, self.metodo.XPATH)

                if quantidade_provs == 1:
                    margem, status = self.__extrair_dados_servidor_um_provimento()
                    self.auto_process_log(f"Margem: {margem}. Status: {status}",
                                          self.nome_log, self.modo_log)
                    return margem, status
                else:
                    print("Selecionando provimento")
                    margem, status = self.__extrair_dados_servidor_varios_provimentos(matricula)
                    self.auto_process_log(f"Margem: {margem}. Status: {status}",
                                          self.nome_log, self.modo_log)
                    return margem, status

            except TimeoutException as excObj:
                loc_error_msg = 'span.feedbackerror'
                msg_erro = self.act.obter_texto(loc_error_msg)
                print(msg_erro)
                return None, msg_erro

        except Exception as e:
            self.auto_gui_error_log("Em <scrape_dados_servidort>", "erro")
            if self.parar_se_exception:
                raise Exception(e)

    def __extrair_dados_servidor_varios_provimentos(self, matricula=''):
        ordem_div_matricula = 0     # numero da seção das tabelas
        cnt = 0
        idx_tabela = 0              # número da linha no conjunto total das tabelas
        verificar_matricula = ""

        loc_matricula = '//div[text()="Identificação - "]'
        elementos_matricula = self.act.retornar_elementos(
            loc_matricula, self.metodo.XPATH
        )
        for cnt, elemento in enumerate(elementos_matricula):
            n_matricula = elemento.text.split(" - ")[1]
            print(matricula, n_matricula)

            if dh.similaridade(n_matricula, matricula) > 85:
                ordem_div_matricula = cnt
                verificar_matricula = "OK"
                break

        if verificar_matricula != "OK":
            print("ERRO: Matrícula não bate com a do portal")
            return None, "Matrícula não bate com a do portal"

        idx_tabela = 4 * ordem_div_matricula

        elementos_consigs = '//*[@id="linha"]/td[2]/span'
        lista_elementos = self.act.retornar_elementos(elementos_consigs,
                                                      self.metodo.XPATH)

        try:
            margem = lista_elementos[2 + idx_tabela].text
        except IndexError:
            idx_tabela -= idx_tabela
            margem = lista_elementos[2 + idx_tabela].text

        print("Margem", margem)

        return margem, "_localizado"

    def __extrair_dados_servidor_um_provimento(self):
        loc_erro_margem = '//span[text()="Não há margem disponível"]'
        if self.act.esta_presente(loc_erro_margem, self.metodo.XPATH, VERB=True):
            print("Não há margem disponivel.")
            return 0, "_localizado"

        loc_consig_fac = '//div[4]/div[2]/div/div/span/div/table/tbody/tr[1]/td[2]/span'
        margem = self.act.obter_texto(loc_consig_fac, self.metodo.XPATH)
        return margem, "_localizado"






