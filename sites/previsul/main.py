import pdb, sys, json
sys.path.append('../../')
#sys.path.append('../')
from sites.ibConsig.IbConsigInsercao.data.IbConsigData import IbConsigData
from sites.previsul.automacao.aut import Automacao
from sites.baseRobos.core.helpers import definir_nome_robo
from sites.baseRobos.core.helpers import formatar_moeda, convert_file_base_64, deleta_todos_arquivos
from dados.APIDataSource import APIDataSource
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from sites.core.selenium_actions import SeleniumActions
from time import sleep


class previsul:
    def __init__(self):
        self.driver = Chrome()
        self.driver.get('https://cota-mais-individual.previsul.com.br/individual?hash=Sm2zDMfMTt%2BEXV%2BxNdXLig%3D%3D&sistema=ACI_5323_COR')
        self.act = SeleniumActions(self.driver)
        

    def main(self):
        self.insercao()
        #self.sincronizacao()


    def sincronizacao(self):
        response = APIDataSource().get_request('previsul-sincronizacao').text
        pdb.set_trace()
        contratos = json.loads(response)
        for i in contratos[1:]:
            # Clicar em Minhas Propostas
            self.act.clicar_elemento('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[1]/div/div/div[6]/a', By.XPATH)
            # Realizar Busca por ID
            self.act.enviar_texto('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[2]/div/div[5]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/input', i[0], By.XPATH)
            # Pesquisar
            self.act.clicar_elemento('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[2]/div/div[5]/div/div[1]/div/div[5]/button', By.XPATH)
            status = self.act.obter_texto('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/table/tbody/tr[1]/td[5]/span/span', By.XPATH)
            pdb.set_trace()
            payload = {
                "ade" : i[0],
                "statusPropostaBanco": status,
                "codigoContrato": i[-1]
            }
            response = APIDataSource().post_request_v2('sincronizar-previsul', payload)


    def insercao(self):
        response = APIDataSource().get_request('previsul-insercao').text
        contratos = json.loads(response)
        todos_dados = contratos['contratos']
        self.data = IbConsigData()
        self.funcoes = Automacao(self.driver)
        for i in todos_dados:
            if i ['codigo_con'] == '472784':
                continue
            dados = APIDataSource().get_request('previsul-insercao-dados', edit=["ade", i['codigo_con']]).text
            print(dados)
            dados = json.loads(APIDataSource().get_request('previsul-insercao-dados', edit=["ade", i['codigo_con']]).text)['contrato']
            self.driver.get('https://cota-mais-individual.previsul.com.br/individual')
            # cpf
            self.act.enviar_texto('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[2]/div/div[1]/div/div/div/div/form/div/div/div[1]/div/div/div[1]/div/input', dados['cpf'], By.XPATH)
            # Pesquisar
            self.act.clicar_elemento('//*[@id="app"]/div[5]/main/div/div/div/div/div/div[2]/div/div[1]/div/div/div/div/form/div/div/div[2]/button', By.XPATH)
            sleep(5)
            # Nascimento
            self.act.enviar_texto('//*[@id="pnlTitular"]/div[2]/div/div/div[2]/div/div/div[1]/div/input', dados['dataNascimento'], By.XPATH)
            # Dados Celular
            campo_celular = self.driver.find_element_by_xpath('//*[@id="pnlTitular"]/div[2]/div/div/div[4]/div/div/div[1]/div/input')
            campo_celular.send_keys(Keys.CONTROL + "a") # BUG .clear() não apaga
            campo_celular.send_keys(Keys.DELETE)
            self.act.enviar_texto_intervalado('//*[@id="pnlTitular"]/div[2]/div/div/div[4]/div/div/div[1]/div/input', dados['dddCelular'] + dados['celular'], metodo=By.XPATH, clear=True, delay=0.5)
            # Mail
            if self.act.obter_atributo('//*[@id="pnlTitular"]/div[2]/div/div/div[5]/div/div/div[1]/div/input', 'value', By.XPATH) == '':
                self.act.enviar_texto('//*[@id="pnlTitular"]/div[2]/div/div/div[5]/div/div/div[1]/div/input', dados['email'], By.XPATH)
            # Atividade
            self.act.enviar_texto('//*[@id="pnlTitular"]/div[2]/div/div/div[3]/div/div/div[1]/div[1]/input', dados['outrosDadosPessoais']['profissao'], By.XPATH)
            atividade = self.driver.find_element_by_xpath('//*[@id="pnlTitular"]/div[2]/div/div/div[3]/div/div/div[1]/div[1]/input')
            atividade.send_keys(Keys.DOWN)
            sleep(1)
            atividade.send_keys(Keys.ENTER)
            self.act.clicar_elemento('//*[@id="pnlTitular"]/div[2]/div/div/div[6]/button', By.XPATH)
            switch = {
                "Acidentes Pessoais I": '1',
                "Acidentes Pessoais II": '2',
                "Acidentes Pessoais III": '3',
                "Acidentes Pessoais IV": '4',
                "Acidentes Pessoais V": '5'}
            id_plano = switch[dados['dadosOperacao']['plano']]
            # Plano de Acidentes
            self.funcoes.loading()
            try:
                status = self.act.obter_texto('//*[@id="app"]/div[2]/div/div/div[1]/span', By.XPATH)
                self.data.atualizar_contrato(dados['codigoContrato'], mensagem="Reprovado a Conferir", erro=status, observacao="Erro ao inserir a proposta")
                exit(0)
            except:
                pass
            self.act.clicar_elemento(f'/html/body/div[1]/div[22]/main/div/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/ul/li[2]/div[2]/div/div/div[{id_plano}]/div[1]/h1', By.XPATH)
            self.act.clicar_elemento(f'/html/body/div[1]/div[22]/main/div/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/ul/li[2]/div[2]/div/div/div[{id_plano}]', By.XPATH)
            self.funcoes.loading()
            pdb.set_trace()
            # Confirmar
            self.act.clicar_elemento('/html/body/div[1]/div[22]/main/div/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/ul/li[3]/div[2]/div/div/div/div/div[2]/p', By.XPATH)
            # Marcar
            self.funcoes.loading()
            try:
                status = self.act.obter_texto('//*[@id="app"]/div[2]/div/div/div[1]/span', By.XPATH)
                self.data.atualizar_contrato(dados['codigoContrato'], mensagem="Reprovado a Conferir", erro=status, observacao="Erro ao inserir a proposta")
                sys.exit()
            except:
                pass
            self.act.clicar_elemento('//*[@id="grdPremio"]/div/table/tbody/tr/td[1]/div/div/div[1]/div/div', By.XPATH)
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[1]/div/div/div[2]/div/div[2]/button', By.XPATH)
            switch_estado_civil = {
                "Casado (a)": 1,
                "Solteiro (a)": 2,
                "Viúvo (a)": 3,
                "Separado (a)": 4,
                "Desquitado (a)": 5,
                "União Estável": 6,
                "Outros": 7
            }
            self.funcoes.loading()
            # Estado Civil
            if dados['outrosDadosPessoais']['estadoCivil'] == 'Divorciado (a)':
                dados['outrosDadosPessoais']['estadoCivil'] = 'Separado (a)'
            div_estado_civil = switch_estado_civil[dados['outrosDadosPessoais']['estadoCivil']]
            sleep(7)
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[1]/div/div[2]/div[4]/div/div/div[1]/div[1]/div[1]', By.XPATH)
            sleep(1.5)
            self.act.clicar_elemento(f'//*[@id="app"]/div[16]/div/div/div[{div_estado_civil}]/a/div/div', By.XPATH)
            # Nome
            if self.act.obter_atributo('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[1]/div/div[2]/div[1]/div/div/div[1]/div/input', 'value', By.XPATH) == '':
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[1]/div/div[2]/div[1]/div/div/div[1]/div/input', dados['nome'], By.XPATH)
            # Sexo
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[1]/div/div[2]/div[3]/div/div/div[1]/div[1]/div[1]', By.XPATH)
            if dados['sexo'] == 'Feminino':
                self.act.clicar_elemento('//*[@id="app"]/div[17]/div/div/div[2]/a/div/div', By.XPATH)
            else:
                self.act.clicar_elemento('//*[@id="app"]/div[17]/div/div/div[1]/a/div/div', By.XPATH)
            pdb.set_trace()
            # cep
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[1]/div[1]/div/div/div[1]/div/input', dados['endereco']['cep'], By.XPATH)
            # Pesquisar cep
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[1]/div[2]/button', By.XPATH)
            sleep(6)
            # endereco
            if self.act.obter_atributo('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[1]/div/input', 'value', By.XPATH) == '':
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[1]/div/input', dados['endereco']['logradouro'], By.XPATH)
            # Complemento
            if self.act.obter_atributo('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[2]/div[3]/div/div/div[1]/div/input', 'value', By.XPATH) == '':
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[2]/div[3]/div/div/div[1]/div/input', dados['endereco']['complemento'], By.XPATH)
            # Numero
            self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div/input', dados['endereco']['numero'], By.XPATH)
            # Bairro
            if self.act.obter_atributo('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[3]/div[3]/div/div/div[1]/div/input', 'value', By.XPATH) == '':
                self.act.enviar_texto('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[1]/div/div[2]/div/div[3]/div[3]/div/div/div[1]/div/input', dados['endereco']['bairro'], By.XPATH)
            # avançar
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[2]/div/form/div[2]/div/div[2]/button', By.XPATH)
            self.funcoes.loading()
            # PERGUNTAS
            switch_perguntas = {
                "Sim": 1,
                "Não": 2,
            }
            # 1 Pergunta
            valor_div = 14
            lista = []
            for k in dados['declaracaoSaude']:
                lista.append(k)
            sleep(2)
            for i in range(2, 8):
                self.act.clicar_elemento(f'//*[@id="mainContainer"]/div/div/div[3]/div/form/div/div[{i}]/div/div/div[2]/div/div/div[1]/div[1]/div[1]', By.XPATH)
                try:
                    self.act.clicar_elemento(f'//*[@id="app"]/div[{valor_div}]/div/div/div[{switch_perguntas[dados["declaracaoSaude"][lista[i - 2]]]}]/a/div/div', By.XPATH)
                except:
                    pass
                valor_div -= 1
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[3]/div/form/div/div[8]/div/div[2]/button', By.XPATH)
            status = None
            try:
                status = self.act.obter_texto('//*[@id="app"]/div[2]/div/div/div[1]/span', By.XPATH)
                self.data.atualizar_contrato(dados['codigoContrato'], mensagem="Reprovado a Conferir", erro=status, observacao="Erro ao inserir a proposta")
                # Fechar
                self.act.clicar_elemento('//*[@id="app"]/div[2]/div/div/div[2]/button', By.XPATH)
                continue
            except:
                pass
            # Beneficiarios
            if dados['beneficiarios'] == 'sem_beneficiarios':
                self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]', By.XPATH)
            else:
                self.funcoes.lidar_beneficiarios(dados)
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[4]/div/div/div[3]/div/div[2]/button', By.XPATH)
            self.funcoes.loading()
            erro = self.funcoes.pagamento_seguro(dados['nome'], dados['formaDesconto'])
            if erro:
                payload = {
                    "codigoContrato": dados['codigoContrato'],
                    "statusPropostaBanco": erro
                }
                response = APIDataSource().post_request_v2('sincronizar-previsul', payload)
                self.act.clicar_elemento('//*[@id="biglogo"]', By.XPATH)
                self.act.clicar_elemento('//*[@id="app"]/div[2]/main/div/div/div/div/div/div/div[3]/button/div/span', By.XPATH)
                continue
            # Clica no botão de finalizar contrato
            self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[5]/div/div/div[3]/div[2]/div/button', By.XPATH)
            self.funcoes.loading()
            ade = None
            try:
                status = self.act.obter_texto('/html/body/div[2]/div/div/div[1]/div[1]/p', By.XPATH)
            except:
                pass
            if status:
                payload = {
                        "codigoContrato" : dados['codigoContrato'],
                        "statusPropostaBanco": status,
                    }
                response = APIDataSource().post_request_v2('sincronizar-previsul', payload)
            else:
                self.act.clicar_elemento('//*[@id="mainContainer"]/div/div/div[6]/div/div/div[2]/div/div[2]/button', By.XPATH)
                self.funcoes.loading()            
                ade = self.act.obter_texto('//*[@id="app"]/div[3]/div/div/div[3]/span', By.XPATH).split(' ')[-1]
                payload = {"codigoCliente": dados['codigoCliente'],"ade": ade,"codigoContrato": dados['codigoContrato'],"banco":"previsul-seguradora","key": "f689f1e12a0399fba803cb2365fc362f"}
                response = APIDataSource().post_request_v2('enviar-dados-previsul', payload)
            
            if ade:
                self.act.clicar_elemento('//*[@id="app"]/div[3]/div/div/div[4]/button', By.XPATH)
                continue
            self.act.clicar_elemento('//*[@id="biglogo"]', By.XPATH)
            self.act.clicar_elemento('//*[@id="app"]/div[2]/main/div/div/div/div/div/div/div[3]/button/div/span', By.XPATH)

if __name__ == '__main__':
    robo = previsul()
    robo.main()