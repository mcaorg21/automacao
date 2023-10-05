"""
A classe <FormReenvioSMS> contém métodos que representam os
elementos do formulário de reenvio de SMS, bem como a ação a
ser executada com cada um desses elementos.
"""
from sites.baseRobos.gui_auto import AutoGUI
from selenium.common.exceptions import TimeoutException
from time import sleep
import pdb


class FormReenvioSMS(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.delay = 0.1
        self.pause = 1
        self.act.time_out = 3

    def campo_ade(self, ade: str):
        """ Clicar e preencher o campo 'Múmero da Proposta' """
        print("Campo ADE", ade)
        loc_cpf = 'input#NumeroProposta'
        self.act.hover_e_clique(loc_cpf, pause=0.3)
        self.act.enviar_caracteres(loc_cpf, ade, delay=0.02, clear=False)

    def botao_pesquisar(self):
        """ Clicar no botão 'Pesquisar' """
        print("Botão pesquisar.")
        loc_pesquisar = 'input#btnPesquisarBiometriaFacial'
        self.act.hover_e_clique(loc_pesquisar, pause=0.3)

    def botao_editar(self):
        """ Clicar no botão 'Editar' """
        print("Botão editar.")
        loc_status = '//*[@id="tabelaDePropostas"]/tbody/tr/td[7]' 
        msg_status: str = self.act.obter_texto(loc_status, self.by.XPATH)        

        if "Concluído" in msg_status:
            return True
        else:
            try:
                loc_editar = '//*[@id="tabelaDePropostas"]/tbody/tr/td[8]/img'
                self.act.hover_e_clique(loc_editar, metodo=self.by.XPATH, pause=0.3)
            except:
                loc_editar = '//*[@id="tabelaDePropostas"]/tbody/tr/td[9]/img'
                self.act.hover_e_clique(loc_editar, metodo=self.by.XPATH, pause=0.3)
            return False

    def link_enviar_sms(self):
        """
        Clicar no ícone amarelo na coluna 'EDITAR / REENVIAR 1º SMS',
        parar abrir modal de envio de SMS
        """
        print("Link enviar SMS")
        loc_envio = '//*[@id="tablePropostas"]/table/tbody/tr/td[6]/div/a'
        self.act.hover_e_clique(loc_envio, metodo=self.by.XPATH, pause=0.3)

    def campo_ddd(self, ddd: str):
        """ Preencher campo 'DDD' """
        print("DDD:", ddd)
        loc_ddd = 'input#alterarDdd'
        self.act.hover_e_clique(loc_ddd)
        self.act.press_backspace(loc_ddd, 3, delay=0.02, end=True)
        self.act.enviar_caracteres(loc_ddd, ddd, delay=0.08, clear=False)

    def campo_celular(self, celular: str):
        """ Preencher campo 'Telefone' """
        print("Celular:", celular)
        loc_celular = 'input#alterarTelefone'
        self.act.hover_e_clique(loc_celular)
        self.act.press_backspace(loc_celular, 10, delay=0.02, end=True)
        self.act.enviar_caracteres(loc_celular, celular, delay=0.08, clear=False)

    def botao_salvar_e_enviar(self):
        """ Clicar no botão 'Salvar' """
        print("Botão Salvar")
        loc_salvar = 'button#btnConfirmarBiometriaFacial'
        self.act.hover_e_clique(loc_salvar, pause=0.3)

    def aguardar_loading(self):
        loc_loading = '//*[@id="divLoading"]'
        self.act.esta_presente_recursivo(loc_loading, self.by.XPATH)

    def retornar_msg_div_erro_modal(self):
        #try:       
        loc_div = '/html/body/div[6]/div[2]/div/div/div/div/div/div/div/div[3]/div'
        msg_erro: str = self.act.obter_texto(loc_div, self.by.XPATH)            
        return msg_erro
        #except TimeoutException:
            #return ""

    def retornar_msg_div_erro_modal_primeiro(self):
        try:
            loc_msg_modal = '//*[@id="alertaErrosBiometriaFacial"]/ul/li'
            msg_erro: str = self.act.obter_texto(loc_msg_modal, self.by.XPATH)
            return msg_erro
        except:
            pass

    def verificar_modal_sucesso(self) -> bool:
        """
        Verificar se o modal 'Sucesso' foi aberto, indicando a
        confirmação do envio do SMS. Retorna True caso tenha
        sido aberto, do contrário, False.
        """
        sleep(2)
        try:
            loc_btn_sucesso = '//*[@id="btnSucessoOK"]'
            self.act.hover_e_clique(loc_btn_sucesso, self.by.XPATH)
            print("Confirmação do envio: OK!")
            return True

        except TimeoutException:
            print("Confirmação do envio: ERRO!")
            return False

    def retornar_msg_div_erro(self) -> str:
        """
        Verifica se alguma mensagem de erro foi apresentada. Caso sim
        retorna a mensagem. Caso não, retorna uma string vazia.
        """
        try:
            print("Verificando erro na pesquisa...")
            loc_div = '//*[@id="divMensagemErro"]/ul/li'
            msg_erro: str = self.act.obter_texto(loc_div, self.by.XPATH)
            return msg_erro
        except TimeoutException:
            return ""

