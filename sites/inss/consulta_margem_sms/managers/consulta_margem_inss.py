##########################
## CONSULTA MARGEM INSS ##
##########################
# Superclasse Manager
from sites.baseRobos.manager import Manager

# Classe de requisição e processamento de dados
from sites.inss.consulta_margem_sms.data.dados_consulta_margem_inss import DadosConsultaINSS

# FUNÇÕES QUE EXECUTAM A INTERAÇÃO COM OS ELEMENTOS WEB
from sites.inss.consulta_margem_sms.auto.executar_consulta_margem import (
    executar_busca_dados_bancarios, executar_busca_dados_emprestimos,
    executar_busca_margem, realizar_login, realizar_logout
)

# Custom exception
from time import sleep
from sites.inss.consulta_margem_sms.auto.auxiliares import ErroDadosConsultaException, ErroLoginAtualizar,BeneficioCancelado,ErroLoading
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List
from sites.baseRobos.core.helpers import definir_nome_robo
dt = DebugTools(debugging=False)
import pdb


class ConsultaMargemInss(Manager):

    def __init__(self):
        super().__init__()
        self.chrome_user = self.PATHS.chrome_user("ConsultaINSS-3")
        self.set_options('--disable-blink-features=AutomationControlled','--ignore-ssl-errors','--profile-directory=Default','window-size=1400,800')
        #set headless
        #self.set_options("--headless")
        self.set_options(self.chrome_user)
        self.dados = DadosConsultaINSS()
        

    @staticmethod
    def main():
        while True:
            definir_nome_robo("Meu INSS - Consulta Dados")
            dados_meu_inss = ConsultaMargemInss().dados.get_perfis()
            try:               
                for perfil in dados_meu_inss:
                    meu_inss: ConsultaMargemInss = ConsultaMargemInss()
                    meu_inss.init_chrome_driver()
                    
                    meu_inss.executar_consultas_dados_margem(dados_perfil=perfil)
                    print("Fechando o driver...")
                    meu_inss.close_driver()
            except:                
                ConsultaMargemInss().close_driver()                
                print("Não há beneficios para consulta... Esperando 1200 segundos...");
                pass
            print('Aguardando reiniciar consulta...')
            sleep(500)

    def main_consulta_via_post(self, perfil):
        definir_nome_robo("Meu INSS - Consulta Dados")
        try:
            meu_inss: ConsultaMargemInss = ConsultaMargemInss()
            meu_inss.init_chrome_driver()
            if 'idContrato' in perfil:
                print('API COMPLETA')
                resultado = meu_inss.executar_consultas_dados_margem(dados_perfil=perfil, tipo_consulta='api_completa')
            else:
                resultado = meu_inss.executar_consultas_dados_margem(dados_perfil=perfil, tipo_consulta="api")
            # post
            print("Fechando o driver...")
            meu_inss.close_driver()
            return resultado
        except:
            print("Não há beneficios para consulta... Esperando 1200 segundos...")
        sleep(1200)


    def executar_consultas_dados_margem(self, dados_perfil: dict=None, tipo_consulta='banco_dados'):
        """
        Gerencia os métodos responsáveis pela execução da consulta dos dados
        dos perfis no 'Meu INSS'.
        Fluxo: 1. requisição da lista de perfis para consulta. 2. login utilizando
        os dados de um perfil específico - caso já esteja logado, faz o logout.
        3. consulta o nome completo, dados bancários e dados de emprestimos
        consignados do cliente. 4. Atualiza o contrato e o perfil no web admin -
        essa atualização pode ser positiva (inserindo os novos dados) ou negativa
        (sinalizando um erro na consulta). 5. Realiza o logout.
        """
        # buscar dados dos perfis de clientes a serem consultados
        a_consultar: List[dict] = []

        if dados_perfil is None:
            a_consultar = self.dados.get_perfis()
        else:
            a_consultar.append(dados_perfil)

        print("Atualizando status do robô.")
        self.dados.uconecte.atualizar_status_robo(17)

        if not a_consultar:
            return False

        for perfil in a_consultar:
            try:
                if(len(perfil['matricula']) == 9):
                    perfil['matricula'] = '0'+perfil['matricula']

                print("Consultando perfil:", perfil['idContrato'])
                # LOGIN
                status_login = self.login_perfil(perfil)
                if status_login == "ERRO_USUARIO":
                    continue

                # CONSULTA
                dados_consulta = self.consultar_dados_perfil(perfil)

                # ATUALIZAR CONTRATO
                if 'api' not in tipo_consulta:
                    self.atualizar_consulta(perfil, dados_consulta)

                # LOGOUT
                realizar_logout(self.chrome_driver)

            except ErroDadosConsultaException as e:
                self.atualizar_consulta(perfil, e.message)
            except ErroLoading as e:
                continue
            except BeneficioCancelado as e:
                dados_consulta = {}
                dados_consulta['retorno'] = 5
                dados_consulta['erro'] = "Benefício está cessado."
                self.dados.post_consulta_info_falha(perfil, dados_consulta)
                self.dados.atualiza_perfil_web_admin(perfil=perfil, retorno=dados_consulta['retorno'] ,observacao=dados_consulta['mensagem'])
                print(">> Dados Atualizados de Beneficio Cessado <<\n")
                continue
            except Exception as e:
                print(e)
            
            if 'api' in tipo_consulta:
                print("Bateu API")
                if tipo_consulta == 'api_completa':
                    return dados_consulta

    def login_perfil(self, perfil: dict) -> str:
        """
        Tenta realizar o login utilizando os dados do perfil.
        Caso já esteja logado, deslog e tenta logar novamente.
        Caso aconteça algum erro relativo ao perfil do cliente
        que impossibilite a consulta, ocorre a atualização do
        contrato e do perfil no webadmin reportando a falha.
        """
        try:
            #self.chrome_driver.refresh()

            login_necessario = realizar_login(perfil, self.chrome_driver)

            if not login_necessario:  # já existe um perfil logado
                realizar_logout(self.chrome_driver)
                realizar_login(perfil, self.chrome_driver)

            return "OK"

        except ErroLoginAtualizar as e:  # erros no cadastro do cliente
            print("ERRO: ", e.message)   # -> atualizar contrato
            self.dados.post_consulta_info_falha(perfil, e.message)
            self.dados.atualiza_perfil_web_admin(
                perfil=perfil, retorno=0, observacao=e.message)
            return "ERRO_USUARIO"

    def consultar_dados_perfil(self, perfil: dict) -> dict:
        """
        Implementa a consulta propriamente dita. Três dicionários de
        dados extraídos são retornados ao longo do processo para então
        serem reunidos em um uníco dicionário com todos os dados
        consultados bem como uma key 'retorno'. A key retorno orienta
        a atualização do contrato: retorno = 1 -> sucesso. retorno != 1
        erro.
        """
        dados_margem: dict = {}
        dados_banco: dict = {}
        dados_emprestimos: dict = {}
        dados_consulta: dict = {}

        sleep(3)
        # Extração dos dados do cliente no site do INSS
        dados_margem: dict = executar_busca_margem(self.chrome_driver, perfil)
        dados_banco: dict = executar_busca_dados_bancarios(self.chrome_driver)
        print('entrou 2....')
        dados_emprestimos: dict = executar_busca_dados_emprestimos(self.chrome_driver)

        # Deslogar para posteriormente logar com o perfil de outro cliente
        realizar_logout(self.chrome_driver)

        return {**dados_margem, **dados_banco, **dados_emprestimos}

    def atualizar_consulta(self, perfil: dict, dados_consulta: dict) -> bool:
        """
        Atualiza o contrato e o perfil do web admin com os dados consultados
        no 'Meu INSS'. O tipo atualização depende do tipo de retorno nos dados
        consultados. Se 1 => atualiza com sucesso os dados. Se != 1 => atualiza
        o contrato e o web admin com a tratativa de erro necessária.
        """
        if dados_consulta.get("retorno", None) == 1:  # retorno 1 = OK
            print("\n>> Atualizando dados com RETORNO 1 <<")
            dados_consulta['mensagem'] = "--Consulta realizada com sucesso! Funcao 8"
            self.dados.post_dados_consultados(dados_consulta, perfil)

            obs: str = "Margem de emprestimo consultada com sucesso!"

            self.dados.atualiza_perfil_web_admin(
                perfil=perfil, dados_consulta=dados_consulta,
                retorno=1, observacao=obs)

            return True

        elif dados_consulta.get("retorno", 1) != 1:  # retorno != 1 -> ERRO
            print(f"\n>> Atualizando dados com RETORNO {dados_consulta['retorno']} <<")
            print(dados_consulta)
            self.dados.post_consulta_info_falha(perfil, dados_consulta)
            self.dados.atualiza_perfil_web_admin(
                perfil=perfil, retorno=dados_consulta['retorno'],
                observacao=dados_consulta['erro'])
            print(">> Dados Atualizados <<\n")
            return False
        else:
            # Não há atualização indicada
            print("\n>> Ocorreu um erro durante a consulta. Dados não atualizados.<<\n")
            return False


if __name__ == "__main__":
    ConsultaMargemInss.main()

