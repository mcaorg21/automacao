"""
A classe <FormReenvioSMS> contém métodos que representam os
elementos do formulário de reenvio de SMS, bem como a ação a
ser executada com cada um desses elementos.
"""
import pdb
from sites.baseRobos.gui_auto import AutoGUI
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from time import sleep
from sites.baseRobos.core.data_helpers import similaridade
from ..auto.auxiliares import tratar_erros, ErroLoginAtualizar, tipo_beneficio


class FormINSSLogin(AutoGUI):
    def __init__(self, driver, perfil: dict):
        super().__init__(driver)
        self.cpf = perfil['cpf']
        self.senha = perfil['senhaAcesso']
        self.act.time_out = 5

    def deletar_cookies(self):
        print("Deletando coookies...")
        self.driver.delete_all_cookies()    

    def fechar_modal(self, recr=0):
        try:
            print("Fechando modal.")
            loc = '//*[@id="modal-tips"]/div/div/a/img'
            self.act.hover_e_clique(loc, self.by.XPATH)
        except:
            if recr >= 2:
                raise TimeoutException
            sleep(1)
            return self.fechar_modal(recr + 1)

    def botao_sair(self, recr=0):
        try:
            print("Clicando em 'Sair'.")
            loc = '//*[@id="root"]/div/div[3]/main/header/div/div/div[2]/span'
            self.act.hover_e_clique(loc, self.by.XPATH)
        except TimeoutException:
            if recr >= 2:
                raise TimeoutException
            sleep(1)
            return self.botao_entrar(recr + 1)

        print("Mudando o foco para o pop up de login")

    def botao_entrar(self, recr=0):
        try:
            print("Clicando em 'Entrar'.")
            loc = '//div/div/div/form/button[1]'
            self.act.hover_e_clique(loc, self.by.XPATH)
        except TimeoutException:
            if recr >= 2:
                raise TimeoutException
            sleep(1)
            return self.botao_entrar(recr + 1)

        print("Mudando o foco para o pop up de login")

    def preencher_cpf(self, recr=0):

        mensagem_erro = ""
        try:
            mensagem_erro = self.act.obter_texto('//*[@id="kc-error-message"]/p', self.by.XPATH)
        except:
            pass

        if("Cliente desativado" in mensagem_erro):
            
            self.act.clicar_elemento('//*[@id="kc-form-buttons"]/input', self.by.XPATH)
            sleep(3)
            self.act.clicar_elemento('/html/body/div/div/div[2]/div/div/div/input', self.by.XPATH)

        try:
            print("Preencher CPF.", self.cpf)
            loc = '#accountId'
            self.act.enviar_texto_intervalado(loc, self.cpf, clear=False, delay=0.07)
        except TimeoutException:
            if recr < 3:
                self.driver.refresh()
                sleep(3)
                self.preencher_cpf(recr + 1)
            else:
                return False

    def botao_avancar(self):
        print("Clicando no botão 'Avançar'.")
        try:
            self.act.clicar_elemento('//*[@id="login-button-panel"]/button',self.by.XPATH)
            return True
        except:
            try:
                self.act.clicar_elemento('//*[@id="modal-tips"]/div/div/button[1]',self.by.XPATH)
            except:
                try:
                    self.act.clicar_elemento('//*[@id="modal-tips"]/div/div/button',self.by.XPATH)
                except:
                    pass
        return False
        # loc = '//*[@id="login-button-panel"]/button'
        # self.act.hover_e_clique(loc, self.by.XPATH)

    def preencher_senha(self):
        print("Preenchendo senha", self.senha)
        loc = '#password'
        self.act.enviar_texto_intervalado(loc, self.senha, clear=False, delay=0.08)

    def clicar_botao_entrar_login(self):
        print("Clicando no botão para login - 'Entrar'")
        loc = '#submit-button'
        self.act.hover_e_clique(loc)

    def verficar_erro_validacao(self):
        locs_erros = ["//*[text()='Ativação de Conta']",
                      '//*[@id="accordion-panel-id"]/div[1]/p',
                      '//*[@id="confirmacao-contato"]']
        for loc in locs_erros:
            try:
                erro = self.act.obter_texto(loc, self.inferir(loc))
                print(erro)
                sleep(0.2)
                tratar_erros(erro)

            except TimeoutException:
                print("Mensagem de erro não foi aberta durante o login. timeout")
            except AttributeError:
                print("Mensagem de erro não foi aberta durante o login. attribute")
            except NoSuchWindowException:
                print("Mensagem de erro não foi aberta durante o login. nowindow")

    def resolver_RECAPTCHAv2(self) -> bool:
        print("Resolvendo ReCAPTCHA.v2")

        #RECAPTCHA_KEY = '6LeVYrUUAAAAAM7ZsAaZS5tpZOD6AwG8-1Nm6Iep'
        RECAPTCHA_KEY = '93b08d40-d46c-400a-ba07-6f91cda815b9'
        try:
            # self.act.obter_atributo('body > div:nth-child(11)', 'style')
            return self.act.hcaptcha(RECAPTCHA_KEY, 'onSubmit')
        except NoSuchWindowException:
            print("Captcha não precisou ser resolvido.")

        return True

    def verificar_janela_recuperar_conta(self):
        loc = '//div[3]/div[2]/h1'
        try:
            msg = self.act.obter_texto(loc, self.by.XPATH)

            print(msg)
            if "recuperação" in msg.lower():
                sleep(0.5)
                atualizar: dict = tratar_erros(self.act, msg)
                raise ErroLoginAtualizar(atualizar)
        except TimeoutException:
            print("Janela Recuperar Conta não foi aberta")

    def autorizar_uso_dados_inss(self):
        try:
            loc = '//*[@id="authorize-info"]/div[2]/button[2]'
            self.act.clicar_elemento(loc, self.by.XPATH)
        except TimeoutException:
            return
        except NoSuchWindowException:
            return
        print("Autorizando uso de dados pessoais.")

    def cancelar_atualizar_dados(self):
        try:
            loc = '//*[@id="root"]/div/div[3]/header/div/div/button[1]'
            self.act.clicar_elemento(loc, self.by.XPATH)
        except TimeoutException:
            return


class FormsINSSDadosCLiente(AutoGUI):
    """
    Possui métodos que extraem as informações relativas à margem do cliente
    e as armazenam na variável __dados_margem.
    :ivar __dados_margem: um dicionário que deverá conter os seguintes pares
    chave: valor:
    {
        nomeCompleto: nome completo do cliente,
        margemDisponivel: margem consignável do cliente,
        margemDisponivelCartao: margem do cartão magnético,
        creditoTotal: base de cálculo para o empréstimo
    }
    """

    def __init__(self, driver):
        super().__init__(driver, wait_timeout=20)
        self.delay = 0.1
        self.pause = 1
        self.act.time_out = 3
        self.matricula_site: str = ''
        self.qtd_beneficios_presentes: int = 0
        self.__dados_margem: dict = {}

    @property
    def dados_margem(self):
        return self.__dados_margem

    @dados_margem.setter
    def dados_margem(self, args: dict):
        self.__dados_margem = args

    def extrair_nome_completo(self):
        print("Extraindo nome completo: ", end='')
        loc = '//div[2]/div[1]/div[2]/div[1]/div/h2'
        nome = self.act.obter_texto(loc, self.by.XPATH)
        print(nome)
        self.__dados_margem['nomeCompleto'] = nome

    def quantidade_beneficios_do_perfil(self) -> int:
        loc = '//*[contains(text(), "Situação")]'
        qtd = self.act.quantidade_elemento(loc, self.by.XPATH, not_0=True)

        return qtd

    def ha_beneficios_ativos(self):
        loc = '//small[contains(text(), "ATIVO")]'
        ativos = self.act.quantidade_elemento(loc, self.by.XPATH)

        print("Beneficios ativos:", ativos)

        return ativos

    def beneficio_ativo(self, idx: int):
        if self.qtd_beneficios_presentes == 1:
            loc = f'//ul/a/ul/li[1]/div[1]/div/p/small[2]'
        else:
            loc = f'//ul/a[{idx + 1}]/ul/li[1]/div[1]/div/p/small[2]'
        situacao = self.act.obter_texto(loc, self.by.XPATH)

        print(situacao)

        if 'cessado' in situacao.lower():
            return False
        elif 'ativo' in situacao.lower():
            return True

    def extrair_tipo_beneficio(self):
        loc = '//*[@id="root"]/div/div[3]/main/div/div[3]/div[1]/div[1]/div[2]/p'

        txt = self.act.obter_texto(loc, self.by.XPATH)
        print("Tipo benefício:", txt)
        cod_beneficio = tipo_beneficio(txt)
        print("Códgio do benefício:", cod_beneficio)
        self.__dados_margem['especieBeneficio'] = cod_beneficio

    def extrair_txt_matriculas(self, idx: int):
        print("Extraindo texto matrícula: ", end='')
        if self.qtd_beneficios_presentes == 1:
            loc = f'//ul/a/ul/li[1]/div[1]/div/span'
        else:
            loc = f'//ul/a[{idx}]/ul/li[1]/div[1]/div/span'

        matrc = self.act.obter_texto(loc, self.by.XPATH)
        matrc = matrc.replace('.', '').replace('-', '')
        #
        # if matrc[0] == '0':
        #     matrc = matrc[1:]
        print("IDX", idx)
        print(matrc)
        self.matricula_site = matrc

    def selecionar_matricula_beneficios(self, matricula_solicit: str, idx: int) -> bool:
        print("Selecionando o benefício correspondente à matrícula.")
        print(f"Site: {self.matricula_site}. Solicitação: {matricula_solicit}")
        if self.qtd_beneficios_presentes == 1:
            loc = f'//ul/a/ul/li/div[1]/div'
        else:
            loc = f'//div/div[2]/ul/a[{idx}]/ul/li[1]/div[1]/div'

        if similaridade(self.matricula_site, matricula_solicit) > 90:
            print(matricula_solicit, self.matricula_site)
            self.act.hover_e_clique(loc, self.by.XPATH)
            return True
        return False

    def extrair_situacao_beneficio(self, rec = 0):
        print("Extraindo situação do benefício: ", end='')
        loc = '//*[@id="root"]/div/div[3]/main/div/div[2]/div[1]/div[2]/div[1]/div/h2'
        loc2 = '//*[@id="root"]/div/div[3]/main/div/div[3]/div[1]/div[1]/div[2]/div[1]/div/h2'
          
        aviso = ''
        loc_aviso = ''
        
        try:
            loc_aviso = '//*[@id="root"]/div/div[3]/main/div/div[3]/label[1]'
            aviso = self.act.obter_texto(loc_aviso, self.by.XPATH)
            if('Ocorreu um erro ao buscar seus dados.' in aviso):
                rec += 1
                if(rec == 15):
                    return False
                self.act.hover_e_clique('//*[@id="root"]/div/div[3]/main/div/div[3]/button/span', self.by.XPATH)
                while self.act.esta_presente_recursivo('//*[@id="root"]/div/div[3]/main/div/div[3]/div/div/div') == True : 
                    print('Aguardando Loading...')
                return self.extrair_situacao_beneficio(rec)
        except:
            pass

        try:
            loc_aviso = '//*[@id="root"]/div/div[3]/main/div/div[3]/div[1]/label[1]'
            aviso = self.act.obter_texto(loc_aviso, self.by.XPATH)
            if('Ocorreu um erro na sua requisição. Tente novamente mais tarde.' in aviso):
                print('Erro no site...')
                return False
        except:
            pass

        try:
            situacao = self.act.obter_texto(loc2, self.by.XPATH)
        except:
            try:
                situacao = self.act.obter_texto(loc, self.by.XPATH)
            except:
                situacao = 'ATIVO'

        print('Situacao: '+situacao)
        return situacao.strip()

    def extrair_margem_emprestimo(self):
        print("Extraindo margem consignável para empréstimo: ", end='')
        loc = '//div[2]/div[2]/div/div/div/div[1]/div/h2'
        margem_emp = self.act.obter_texto(loc, self.by.XPATH)
        margem_emp_f = margem_emp.replace(".", "").replace(",", ".").strip()
        print(margem_emp_f)
        self.__dados_margem['margemDisponivel'] = margem_emp_f.replace("R$", "").strip()

    def extrair_margem_cartao_mag(self):
        print("Extraindo margem consignável do cartao magnetico: ", end='')
        loc = '//div[2]/div[2]/div/ div/div/div[2]/div/h2'
        margem_crt = self.act.obter_texto(loc, self.by.XPATH)
        margem_crt_f = margem_crt.replace(".", "").replace(",", ".").strip()
        print(margem_crt_f)
        self.__dados_margem['margemDisponivelCartao'] = margem_crt_f.replace("R$", "").strip()

    def extrair_base_de_calculo(self):
        loc = '//div[2]/div[2]/div/div/div/div[3]/div/h2'
        bdc = self.act.obter_texto(loc, self.by.XPATH).replace("R$", "").strip()
        print("Base de cálculo:", bdc)
        self.__dados_margem['creditoTotal'] = bdc.replace(".", "").replace(",", ".").strip()

    def verificar_erros_dados(self) -> str:
        loc = '//*[@id="root"]/div/div[2]/main/div/main/div[2]/label[1]'
        try:
            erro = self.act.obter_texto(loc, self.by.XPATH)
            return erro
        except TimeoutException:
            return ""


class FormINSSDadosBanco(AutoGUI):
    """
        Possui métodos que extraem as informações relativas aos dados bancários
        do cliente e as armazenam na variável __dados_bancarios.
        :ivar __dados_bancarios: um dicionário que deverá conter os seguintes pares
        chave: valor:
        {
            "banco": número e nome do banco,
            "agencia": nº agencia,
            "conta": nº conta,
            "digitoConta": dv conta,
            "tipoConta": tipo da conta para liberação do empréstimo.
        }
        """

    def __init__(self, driver):
        super().__init__(driver)
        self.__dados_bancarios: dict = {
            "banco": '',
            "agencia": '',
            "conta": '',
            "digitoConta": '',
            "tipoConta": ''
        }

    @property
    def dados_bancarios(self) -> dict:
        return self.__dados_bancarios

    @dados_bancarios.setter
    def dados_bancarios(self, value):
        self.__dados_bancarios = value

    def extrair_codigo_nome_banco(self):
        #
        loc = '/html/body/div[2]/div/div[3]/main/div/div[3]/div[1]/div[2]/div[2]/p'
        self.__dados_bancarios['banco'] = self.act.obter_texto(loc, self.by.XPATH)

    def extrair_agencia(self):
        #
        loc = '/html/body/div[2]/div/div[3]/main/div/div[3]/div[1]/div[2]/div[2]/div/div[2]/div/h2'
        ag = self.act.obter_texto(loc, self.by.XPATH)
        self.__dados_bancarios['agencia'] = ag

    def extrair_nconta_e_dv(self):
        #
        
        loc = '/html/body/div[2]/div/div[3]/main/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div/h2'
        cc: str = self.act.obter_texto(loc, self.by.XPATH)

        if not cc:
            n_conta, dv = '', ''
        else:
            n_conta, dv = cc[0:-1], cc[-1:]

        self.__dados_bancarios['conta'] = n_conta
        self.__dados_bancarios['digitoConta'] = dv

    def extrair_tipo_conta(self):
        loc = '/html/body/div[2]/div/div[3]/main/div/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/h2'
        tc: str = self.act.obter_texto(loc, self.by.XPATH)
        self.__dados_bancarios['tipoConta'] = tc


class FormINSSDadosEmprestimos(AutoGUI):
    """
    Possui métodos que extraem as informações relativas aos empréstimos em
    cada banco.
    :ivar __dados_do_emprestimo: um dicionário que deverá conter os seguintes pares
    chave: valor:
    {
        "numeroBanco": número do banco que realizou empréstimo,
        "valorPresenteInicial": inicio do contrato,
        "parcela": valor das parcelas,
        "dataInicioDesconto": inicio da cobrança do contrato,
        "parcelasPagas": parcelas pagas até o momento,
        "parcelasTotais": quantidade total de parcelas,
        "statusContrato": ativo ou inativo
    }
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.dados_do_emprestimo: dict = {}
        self.lista_emprestimos: list = []
        self.lista_parcelas: list = []
        self.act.time_out = 2

    @property
    def dados_emprestimo_consultados(self):
        return self.dados_do_emprestimo.copy()

    def atualizar_lista_emprestimos(self):
        print("Atualizando lista de emprestimos:", self.dados_do_emprestimo)
        self.lista_emprestimos.append(self.dados_emprestimo_consultados)

    def quantidade_emprestimos(self) -> int:
        loc = '/html/body/div[2]/div/div[3]/main/div/div[3]/div[1]/div[3]/div[2]/div'
        qtd = self.act.quantidade_elemento(loc, self.by.XPATH)
        return qtd

    def selecionar_emprestimo(self, idx):
        loc = f'//*[@id="root"]/div/div[3]/main/div/div[3]/div[1]/div[3]/div[2]/div[{idx+1}]'
        self.act.hover_e_clique(loc, self.by.XPATH)


    def extrair_n_banco(self, idx: int):
        print("Extraindo número do banco: ", end='')
        loc = f'//div[2]/div[{idx + 1}]/div[2]/div/div/div/div/div/div[3]/div/h2'
        try:
            n_banco = self.act.obter_texto(loc, self.by.XPATH)
        except:
            self.selecionar_emprestimo(idx)
            print("Extraindo novamente número do banco: ", end='')
            loc = f'//div[2]/div[{idx}]/div[2]/div/div/div/div/div/div[3]/div/h2'
            n_banco = self.act.obter_texto(loc, self.by.XPATH)
            
        print(n_banco)

        self.dados_do_emprestimo['numeroBanco'] = n_banco.split("-")[0].strip()

    def extrair_valor_presente_inicial(self, idx: int):
        print("Extraindo valor inicial do empréstimo: ", end="")
        loc = (f'//div[2]/div[{idx + 1}]/div[2]/div/'
               f'div/div/div/div/div[9]/div/h2')
        vpi = self.act.obter_texto(loc, self.by.XPATH)
        vpi = vpi.replace("R$", "").replace(".", "").replace(",", ".").strip()
        print(vpi)

        self.dados_do_emprestimo['valorPresenteInicial'] = vpi

    def extrair_valor_parcela(self, idx: int):
        print("Extraindo valor parcela ", end="")
        loc = (f'//div[{idx + 1}]/div[2]/div/div/'
               f'div/div/div/div[8]/div/h2')
        val_parcela = self.act.obter_texto(loc, self.by.XPATH)
        val_parcela = val_parcela.replace("R$", "").replace(".", "").replace(",", ".").strip()
        print(val_parcela)

        self.dados_do_emprestimo['parcela'] = val_parcela
        self.lista_parcelas.append(val_parcela)

    def extrair_data_inicio_desconto(self, idx: int):
        print("Extraindo a data de início de desconto.", end='')
        loc = f'//div[{idx + 1}]/div[2]/div/div/div/div/div/div[4]/div/h2'
        did = self.act.obter_texto(loc, self.by.XPATH)
        print(did)
        self.dados_do_emprestimo['dataInicioDesconto'] = did

    def calcular_parcelas_pagas(self):
        print("Calcular as parcelas pagas: ", end='')
        pp = self.__calcula_parcelas_pagas(
            self.dados_do_emprestimo['dataInicioDesconto'])
        print(pp)
        self.dados_do_emprestimo['parcelasPagas'] = pp

    def extrair_parcelas_totais(self, idx: int):
        print("Extraindo parcelas totais do contrato: ", end="")
        loc = f'//div[{idx + 1}]/div[2]/div/div/div/div/div/div[7]/div/h2'
        parcelas_totais = self.act.obter_texto(loc, self.by.XPATH)
        print(parcelas_totais)
        self.dados_do_emprestimo['parcelasTotais'] = parcelas_totais

    def extrair_status_contrato(self, idx: int):
        print("Extraindo status do contrato: ", end='')
        loc = f'//div[{idx + 1}]/div[2]/div/div/div/div/div/div[2]/div/h2'
        status_contrato = self.act.obter_texto(loc, self.by.XPATH)
        self.dados_do_emprestimo['statusContrato'] = status_contrato

    def calcular_valor_emprestimos(self) -> str:
        soma: int = 0

        for parcela in self.lista_parcelas:
            soma += float(parcela)

        return str(round(soma, 2))

    @staticmethod
    def __calcula_parcelas_pagas(inicio: str) -> int:
        """
        Calcula a quantidade de parcelas pagas com base no mês
        de início da cobrança e no mês atual.
        :param inicio: data de início da cobrança, no modelo de DD/MM/AAAA.
        :return: valor inteiro da quantidade de parcelas pagas.
        """
        print(inicio)
        try:
            mes_inicio = int(inicio.split('/')[0])
            ano_inicio = int(inicio.split('/')[1])
        except:
            mes_inicio = int(inicio[4:6])
            ano_inicio = int(inicio[0:4])

        data = datetime.now()
        
        if data.year == ano_inicio:
            return data.month - mes_inicio
        else:
            return ((data.year - ano_inicio) * 12) + (data.month - mes_inicio)


class FormINSSLogout(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.act.time_out = 2

    def clicar_botao_logout(self):
        print('Realizando logout.')
        try:
            loc1 = '//div[contains(text(), "Sair")]'
            self.act.hover_e_clique(loc1, self.by.XPATH)
        except TimeoutException:
            loc2 = '//div[contains(text(), "Sair")]'
            self.act.hover_e_clique(loc2, self.by.XPATH)
