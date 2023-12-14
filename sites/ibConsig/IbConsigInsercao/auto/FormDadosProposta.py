from threading import Thread

from sites.baseRobos.gui_auto import AutoGUI
from selenium.webdriver import Chrome
from time import sleep
from selenium.common.exceptions import (
    TimeoutException, JavascriptException,
)

from sites.elementos import TextInput, Select
from sites.ibConsig.ItauConsultaRefin.data.DadosConsultaRefin import DadosConsultaRefin
from sites.baseRobos.core.DebugTools import DebugTools
from typing import List, Callable
from selenium.webdriver.remote.webelement import WebElement
from sites.ibConsig.libs.exceptions.Exceptions import NotFoundResultException, ParcelaNaoEncontradaException, DadoIndisponivelException,PreenchimentoTabelaException
from sites.ibConsig.libs.auxiliares.ib_auxiliares import (
    comparar_valores_contrato, comparar_taxas_de_origem)

import pdb,time

deb = DebugTools(debugging=False)


class DadosProposta(AutoGUI):

    def __init__(self, driver: Chrome, dados: dict, dadosObj=None):
        super().__init__(driver, wait_timeout=1)
        try:
            self.__val_contrato = float(dados.get('valorContrato', 0.0))
        except:
            self.__val_contrato = float(dados.get('valorContrato', 0.0).replace(',','.'))    
        self.federal = dados.get('federal', False)
        self.inss = dados.get('inss', False)
        self.estadual = dados.get('estadual', False)
        self.inss = dados.get('inss', False)
        self.__val_parcela = dados.get('valorParcela', None)
        self.__prazo_contrato = dados.get('prazoContrato', None)
        self.valor_liberado_maximo = ""
        self.__valores_atualizados: dict = {}
        self.__tipo: str = dados.get('tipo', '')
        self.consulta_refinanciamento = False
        self.__val_liberado_refin = ""
        self.__saldo_devedor_refin = ""
        self.__infos_extras: dict = dados.get("informacoesExtras", {})
        self.__carenciaTabela: str = self.__infos_extras.get("carenciaTabela")
        self.__tipo_beneficio: str = dados.get("tipoBeneficio")
        self.tabela_selecionada: str = ""
        self.wait = 0.3
        self.dadosObj: DadosConsultaRefin = dadosObj
        self.simular = False
        self.portabilidade = False
        self.taxa_juros_tabela = dados.get('taxaJurosTabela', None)
        self.grau_instrucao_sistema: str  = dados.get('grauInstrucaoWa', None)
        self.grau_instrucao_cliente: str = dados.get('grauInstrucao', None)
        self.tabela_digital_sistema: str = dados.get('tabelaDigital', None)
        #self.especie_beneficio: str = dados.get('especieBeneficio', None)
        self.taxa_basica_juros = "1,8"

    @property
    def prazo_refin(self):
        if not self.refinanciamento:
            raise Exception(
                "A proposta não foi marcada como "
                "Inserção/Consulta de REFINANCIAMENTO")

        return self.__prazo_contrato

    @property
    def val_contrato_atualizado(self):
        return str(self.__valores_atualizados['prazo_contrato'])

    @property
    def prazo_contrato_atualizado(self):
        return self.__prazo_contrato

    @property
    def valores_prazos_ib_consig(self):
        return self.__valores_atualizados

    @property
    def nova_proposta(self):
        return "novo" in self.__tipo.lower()

    @property
    def refinanciamento(self):
        return ("refinanciamento" in self.__tipo.lower() or
                self.consulta_refinanciamento)

    @property
    def saldo_devedor(self):
        return self.__saldo_devedor_refin

    @property
    def valor_contrato(self):
        return self.__val_contrato

    @property
    def valor_liberado(self):
        return self.__val_liberado_refin

    @property
    def valor_parcela(self):
        return self.__val_parcela

    @valor_parcela.setter
    def valor_parcela(self, valor):
        self.__val_parcela = valor

    @property
    def possui_carencia(self):
        print("Possui carência? ", self.__carenciaTabela != 0)
        if(self.__carenciaTabela == '0'):
            return False

        if(self.__carenciaTabela != 0):
            return True
        else:
            return False

    @property
    def grau_instrucao_wa(self):
        return self.grau_instrucao_sistema

    @property
    def grau_instrucao_uconecte(self):
        return self.grau_instrucao_cliente

    @property
    def tabela_digital(self):
        return self.tabela_digital_sistema

    @property
    def taxa_juros(self):
        return self.taxa_juros_tabela

    @property
    def tipo_beneficio(self):
        print("Tipo beneficio: ", self.__tipo_beneficio)
        return self.__tipo_beneficio

    @property
    # def especie_beneficio(self):
    #     print("Especie do beneficio: ", self.especie_beneficio)
    #     return self.especie_beneficio

    def selecionar_carencia_adicional(self):
        '//*[@id="ade.carenciaAdicional"]'
        select = Select(self.driver, '//*[@id="ade.carenciaAdicional"]', time_out=2)
        select.carregar_elemento()
        self.carencia = str(self.__carenciaTabela)
        # if(self.carencia == '120'):
        #     self.carencia = '90'
        select.selecionar_opcao(self.carencia)

        sleep(3)
        self.act.manusear_alerta('aceitar')

    def selecionar_tabela_carencia(self,tabela_digital= True, nova_formalizazao_in100 = False, valor_minimo_contrato_carencia = 1500, valor_primeira_faixa_carencia_maximo = 1499):
        self.nova_formalizazao_in100 = nova_formalizazao_in100
        loc: str = ""
        
        if self.inss:
            #if self.__carenciaTabela and self.__val_contrato >= valor_minimo_contrato_carencia:
            #    self.selecionar_carencia_adicional()
            loc = '[id="ade.codigoCarencia"]'  # tabela RGPS
        elif self.federal:
            loc = '[id="ade.codigoTabelaEspecial"]'  # tabela estatutários

        print("TipoTabela:", loc)
        
        if(self.__carenciaTabela and self.__carenciaTabela != 0 and self.__carenciaTabela != '0' and self.__val_contrato >= valor_minimo_contrato_carencia):
            if(self.__val_contrato <= valor_primeira_faixa_carencia_maximo):
                string_tabela = "DIG Inss/Novo R$ 730 a R$ 1499 - Car "+str(self.__carenciaTabela)+")" 
            else:
                string_tabela = r"Car "+str(self.__carenciaTabela)+'-Tx 2,14' 

            print('Procurar tabela:' + string_tabela)

            if(tabela_digital == False):
                opt_tabela: WebElement = self.__opcao_tabela_nova_proposta_sem_digital(loc, filt=lambda taxa: "DIG" not in taxa and string_tabela in taxa and self.taxa_basica_juros in taxa)
            else:
                if(self.__val_contrato <= valor_primeira_faixa_carencia_maximo):
                    opt_tabela: WebElement = self.__opcao_tabela_nova_proposta(loc, filt=lambda taxa: "DIG" in taxa and "Car" in taxa)
                else:
                    opt_tabela: WebElement = self.__opcao_tabela_nova_proposta(loc, filt=lambda taxa: "DIG" in taxa and "Car" in taxa and self.taxa_basica_juros  in taxa)

            if not opt_tabela:
                raise PreenchimentoTabelaException("Não há tabela disponível para carência 120 dias. Com valor de" + str(self.__val_contrato))

        else:
            if(tabela_digital):
                if(self.__tipo_beneficio == "87" or self.__tipo_beneficio == "88"):
                    opt_tabela: WebElement = self.__opcao_tabela_nova_proposta(loc, filt=lambda taxa: "DIG" in taxa and "Loas" in taxa and 'Car' not in taxa and self.taxa_basica_juros  in taxa)
                else:  
                    #pdb.set_trace()
                    if(self.__tipo_beneficio != ""):
                        opt_tabela: WebElement = self.__opcao_tabela_nova_proposta(loc, filt=lambda taxa: "DIG" in taxa and 'Car' not in taxa and self.taxa_basica_juros  in taxa)
                    else:
                        opt_tabela: WebElement = self.__opcao_tabela_nova_proposta(loc, filt=lambda taxa: "DIG" in taxa and 'Car' not in taxa and self.taxa_basica_juros  in taxa)
            else:
                opt_tabela: WebElement = self.__opcao_tabela_nova_proposta_sem_digital(loc, filt=lambda taxa: "DIG" not in taxa and self.taxa_basica_juros in taxa)
        
        self.act.select_drop_down(loc, opt_tabela.get_attribute("value"))

        sleep(0.3)
        self.tabela_selecionada = self.act.obter_texto_opcao_selecionada(loc)
        print("Tabela:", self.tabela_selecionada)

    def extrair_prazo_formulario(self):
        loc = '[id="ade.quantidadePrestacoes"]'
        self.__prazo_contrato = self.act.obter_valor(loc)
        print("Prazo:", self.__prazo_contrato)

    def preencher_margem_se_vazia(self):
        try:
            txt_ipt: TextInput = TextInput(
                driver=self.chrome_driver, seletor='//*[@id="margem.valor"]')
            txt_ipt.carregar_elemento()
            if txt_ipt.disabled() or txt_ipt.has_hidden_type():
                return
            txt_ipt.enviar_caracteres(self.__val_parcela, delay=0.05)
            txt_ipt.press_TAB()
        except TimeoutException:
            print("Campo margem já preenchido")

    def selecionar_taxa_refinanciamento(self, filtro: Callable = lambda taxa: not ("DIG" in taxa)):
        print("Selecionando taxa de refinanciamento")
        taxa_origem = self.extrair_taxa_origem()
        loc_tabela = '[id="ade.codigoCarencia"]'  # tabela RGPS
        print("Taxa de origem:", taxa_origem)

        if not self.act.esta_presente(loc_tabela):
            loc_tabela = '[id="ade.codigoTabelaEspecial"]'  # tabela estatutários

        opt_tabela: WebElement = self.__opcao_tabela_refin(
            loc_tabela, taxa_origem, filt=filtro)
        self.act.select_drop_down(loc_tabela, opt_tabela.get_attribute("value"))

        print("Tabela selecionada:", opt_tabela.text)
        self.tabela_selecionada = opt_tabela.text

    def apagar_campo_valor_solicitado(self):
        print("Apagando campo valor solicitado.")
        loc_val = '//*[@id="ade.valorEmprestimo"]'

        self.act.hover_e_clique(loc_val, self.by.XPATH)
        self.act.press_backspace(
            loc_val, 10, self.by.XPATH, delay=0.01
        )

    def extrair_valor_parcela(self, rec=0):
        """ Específico para consulta de Refinanciamento """
        print("Extraindo valor parcela para consulta:", end='')
        # loc = '//*[@id="label_ade.valorPrestacao"]'
        try:
            sleep(1)
            self.act.manusear_alerta('aceitar')
            loc = '//*[@id="ade.valorPrestacao"]'
            valor = self.act.obter_valor(loc, self.by.XPATH)
            if not valor:
                raise ParcelaNaoEncontradaException

            self.__val_parcela = valor
        except TimeoutException:
            loc = '//*[@id="label_ade.valorPrestacao"]'
            self.__val_parcela = self.act.obter_texto(loc, self.by.XPATH)
        print(self.__val_parcela)

        sleep(0.5)
        if rec > 5:
            raise ParcelaNaoEncontradaException

        if not self.__val_parcela:
            return self.extrair_valor_parcela(rec + 1)

    def extrair_saldo_devedor(self):
        """ Específico para consulta de Refinanciamento """
        print("Extraindo saldo devedor:", end='')
        loc = '//*[@id="label_refinanciamento.valorSaldoDevedor"]'
        self.__saldo_devedor_refin = self.act.obter_texto(loc, self.by.XPATH)

        print(self.__saldo_devedor_refin)

    def extrair_valor_liberado(self, rec=0):
        """ Específico para consulta de Refinanciamento """
        sleep(0.5)
        try:
            print("Extraindo valor liberado:", end='')
            loc = '//*[@id="label_refinanciamento.valorAdicionalComIof"]'
            self.__val_liberado_refin = self.act.obter_texto(loc, self.by.XPATH)
        except TimeoutException:
            if rec >= 5:
                raise TimeoutException
            return self.extrair_valor_liberado(rec + 1)
        print(self.__val_liberado_refin)

    def preencher_valor_parcela(self):
        sleep(self.wait)
        print("Preenchendo valor da parcela...", self.__val_parcela)

        #ajuste para sair na tabela acima de 680 reais
        if("complementar" in self.__tipo.lower()):
            parcela_float = float(self.__val_parcela.replace(',','.')) 
            if(parcela_float >= 16.30 and parcela_float < 16.40):
                self.__val_parcela = '16,40'   
        try:
            loc_parcela = '//*[@id="ade.valorPrestacao"]'
            self.act.hover_e_clique(loc_parcela, self.by.XPATH)
            self.act.press_backspace(
                loc_parcela, loop=10, delay=0.01,
                end=True, metodo=self.by.XPATH
            )
            self.act.enviar_texto_intervalado(
                loc_parcela, self.__val_parcela,
                self.by.XPATH, delay=0.05
            )
            sleep(self.wait)
            self.act.press_TAB(loc_parcela, self.by.XPATH)
        except TimeoutException:
            print("Campo valor das prestações ja preenchido.")

    def thread_extrair_valores_pop_up(self):
        thread_extrair_valores_pop_up = Thread(target=self.extrair_valores_emprestimo)
        thread_extrair_valores_pop_up.start()
        for i in range(60):
            sleep(1)
            print(f"\rAguardando consultar tabela: {i}", end="")
            if not thread_extrair_valores_pop_up.is_alive():
                break
        if thread_extrair_valores_pop_up.is_alive():
            self.chrome_driver.quit()
            raise KeyboardInterrupt(
                "Pop-up de simulaçao não pôde ser consultado "
                "ou fechado, provavelmente por interferência de um alerta")

    def extrair_valores_emprestimo(self):
        
        # Abrir janela simulação
        print("Extraindo valor do empréstimo segundo a tabela do sistema IbConsig")
        loc_btn_simular = '//*[@id="simulacao"]/a'
        self.act.hover_e_clique(loc_btn_simular, self.by.XPATH)

        while self.act.verificar_n_janelas(2) == False:
            print('Numero de janela ainda errado')
            self.act.hover_e_clique(loc_btn_simular, self.by.XPATH)

        self.act.trocar_janela(idx_janela=-1, verb=True)      

        if self.nova_proposta:
            # valor para comparação com valor do contrato
            val_ib: dict = self.__extrair_valor_segundo_prazo(self.__prazo_contrato)

            # valores relativos a parcelas máximas segundo parametrização de algumas entidades

            if not val_ib:
                val_ib.update(self.__extrair_valor_segundo_prazo("48"))
                val_ib.update(self.__extrair_valor_segundo_prazo("60"))

                self.__valores_atualizados = {
                    "prazo_contrato": float(val_ib[self.__prazo_contrato].replace(",", ".")),
                    "48x": val_ib['48'],
                    "60x": val_ib['60'],
                }
            else:
                self.__valores_atualizados = {
                    "prazo_contrato": float(val_ib[self.__prazo_contrato].replace(",", ".")),
                }


        elif self.portabilidade:
            val_ib: dict = self.__extrair_valor_segundo_prazo(self.__prazo_contrato)
            self.__valores_atualizados = {
                "prazo_contrato": float(val_ib[self.__prazo_contrato].replace(",", ".")),
            }
        elif self.refinanciamento:  # REFATORAR ?
            prazo_valor: dict = self.__extrair_valor_segundo_prazo(prazo="maximo")
            self.__valores_atualizados = {
                "prazo_contrato": prazo_valor['valor_maximo']
            }
            self.__prazo_contrato = prazo_valor['prazo_maximo']
            
        # Fechar janela
        self.chrome_driver.close()
        self.chrome_driver.switch_to.window(self.chrome_driver.window_handles[0])
        self.sh.trocar_frame("rightFrame")

    def preencher_campo_val_emprestimo(self):
        print(f"Preenchendo utilizando o valor: {self.val_contrato_atualizado}")
        loc_val = '//*[@id="ade.valorEmprestimo"]'
        format_val = str(self.val_contrato_atualizado).replace('.', ',')
        self.act.enviar_texto_intervalado(
            loc_val, format_val, self.by.XPATH, delay=0.02)
        #sleep(self.wait)
        self.act.press_TAB(loc_val, self.by.XPATH)

    def preencher_campo_novo_val_emprestimo(self,valor):
        print(f"Preenchendo utilizando o valor: {valor}")
        loc_val = '//*[@id="ade.valorEmprestimo"]'
        self.act.enviar_texto_intervalado(
            loc_val, valor, self.by.XPATH, delay=0.02)
        #sleep(self.wait)
        self.act.press_TAB(valor, self.by.XPATH)    

    def recalcular_valor_liberado(self, wait=0.5):
        print("Recalculando valor liberado.")
        loc = "#ade\\\\.valorEmprestimo"
        script = f"recalculaValorLiberado($('{loc}'), getEmprestimoFlex())"
        try:
            sleep(wait)
            self.chrome_driver.execute_script(script)
            sleep(wait)
        except JavascriptException:
            print("Não foi possível executar script: ", script)

    def preencher_prazo_contrato(self, rec=0):
        print("Preenchendo prazo do contrato...", self.__prazo_contrato)
        loc_prazo = '//*[@id="ade.quantidadePrestacoes"]'
        try:
            self.act.enviar_texto_intervalado(
                loc_prazo, self.__prazo_contrato,
                self.by.XPATH, delay=0.02
            )
            sleep(self.wait)
            self.act.press_TAB(loc_prazo, self.by.XPATH)
        except TimeoutException:
            if rec >= 5:
                raise TimeoutException("DadosProposta.preencher_prazo_contrato")
            return self.preencher_prazo_contrato(rec + 1)

    def extrair_valor_maximo_liberado(self):
        print("Extraindo valor liberado máximo...", end='')
        loc_val_max = '//*[@id="label_refinanciamento.valorAdicionalComIof"]'
        self.valor_liberado_maximo = self.act.obter_texto(
            seletor=loc_val_max, metodo=self.by.XPATH
        )
        print(self.valor_liberado_maximo)

    def executar_calculo_comissao(self, wait=0.5):
        script = "calculoPercentualComissaoAjax()"
        self.chrome_driver.execute_script(script)
        #sleep(wait)

    def executar_caculo_valores_refinanciamento(self):
        self.chrome_driver.execute_script("""
            buscaValorCapitalSegurado();
            buscaCoeficienteAndExpansaoIofAjax();
            calculoPercentualComissaoAjax();
        """)

    def __extrair_valor_segundo_prazo(self, prazo: str = "maximo") -> dict:
        print("Buscando pelo valor respectivo ao prazo:", prazo)

        val_encontrado: str = ""
        prazo_encontrado: str = ""
        for idx in range(2, 12):
            try:
                loc_prazos = f'//*[@id="tableSimulacaoIdeal"]/tbody/tr[{idx}]/td[1]'
                loc_valor = f'//*[@id="tableSimulacaoIdeal"]/tbody/tr[{idx}]/td[2]'
                loc_status = f'//*[@id="tableSimulacaoIdeal"]/tbody/tr[{idx}]/td[3]/input'

                prazo_tab = self.act.obter_texto(loc_prazos, self.by.XPATH)
                val_ib: str = self.act.obter_texto(loc_valor, self.by.XPATH)

                if prazo != "maximo" and prazo_tab == prazo:
                    print(f"Prazo: {prazo_tab}. Valor: {val_ib}")
                    return {prazo: val_ib}

                elif prazo == "maximo":
                    try:
                        status = self.act.obter_atributo(loc_status, "src", self.by.XPATH)
                    except TimeoutException:
                        continue
                    print(status)

                    print(f"Prazo: {prazo_tab}. Valor: {val_ib}")
                    val_encontrado = val_ib
                    prazo_encontrado = prazo_tab

            except TimeoutException:
                continue

        if not val_encontrado or not prazo_encontrado:
            self.act.fechar_janela(1)
            self.act.trocar_janela(0, 1)
            raise DadoIndisponivelException(nome="Valor simulação", valor=f"prazo={prazo}")
        return {
            'valor_maximo': val_encontrado,
            'prazo_maximo': prazo_encontrado
        }

    def extrair_taxa_origem(self) -> float:
        # Obter Taxa de Juros do Cotrato de Origem
        loc_tx_origem = '//*[@id="label_refinanciamento.taxaContratoOrigem"]'
        tx_origem = self.act.obter_texto(loc_tx_origem, self.by.XPATH)
        return float(tx_origem.replace(',', '.'))

    def selecionarTabelaDiretaPortabilidade(self,opcaoValor, nome):
        self.tabelaDisponivel.carregar_elemento()
        self.tabelaDisponivel.selecionar_opcao(opcaoValor)
        self.__tabelaCarencia = nome
        self.__dados.incluirDadoAdicional(
            "tabelaBanco", self.__tabelaCarencia)

    def __opcao_tabela_refin(
            self, loc_tabela: str, taxa: float, filt: Callable = lambda x: 1, insercao_contrato = False, rec = 0) -> WebElement:
        """
        Seleciona a opção correta na tabela de carência de acordo com a taxa de origem do contrato.
        Pode ser utilizado também um filtro para filtrar a oppção, também, segundo o texto da opçao
        da tabela.
        :param loc_tabela: localizador do elemento da tabela
        :param filt: função aplicada para filtrar as opções segundo o texto contigo nos elementos.
        :return: elemento web relativo à opção selecionada
        :raises: NotFoundResultException
        """
        print("Encontrando tabela segundo taxa de origem.")
        taxas_opts: List[WebElement] = self.act.retornar_opcoes_select(loc_tabela)
        taxas_encontradas = []
        for taxa_opt in taxas_opts:
            # filtro: expressão lambda a ser aplicada para filtrar o tipo de taxa na tabela
            if(self.__carenciaTabela == 0):
                if 'Car' in taxa_opt.text:
                    continue

            if not filt(taxa_opt.text):
                continue
            print(taxa_opt.text)
            if(insercao_contrato):
                tipo = 'entre_taxas'
            else:
                tipo = 'entre_ou_taxa_maior'    
            
            if comparar_taxas_de_origem(taxa_opt.text, taxa, insercao_contrato):
                print("Taxa selecionada:", taxa_opt.text)
                taxas_encontradas.append(taxa_opt)
                #return taxa_opt

        for taxa_encontrada in taxas_encontradas:
            if('Origem maior' in taxa_encontrada.text or 'Refin 1' in taxa_encontrada.text):
                return taxa_encontrada

        if(taxas_encontradas):
            return taxas_encontradas[0]
        else:
            rec += 1
            if(rec < 8):
                taxa = taxa + 0.1
                return self.__opcao_tabela_refin(loc_tabela, taxa, filt , False, rec)  
            else:
                raise DadoIndisponivelException(nome="Taxa", valor=str(taxa))

    def __opcao_tabela_nova_proposta(self, loc_tabela: str, filt: Callable = lambda x: 1) -> WebElement:
        """
        Seleciona a opção correta na tabela de carência de acordo com a taxa de origem do contrato.
        Pode ser utilizado também um filtro para filtrar a oppção, também, segundo o texto da opçao
        da tabela.
        :param loc_tabela: localizador do elemento da tabela
        :param filt: função aplicada para filtrar as opções segundo o texto contigo nos elementos.
        :return: elemento web relativo à opção selecionada
        :raises: NotFoundResultException
        """
        print("Encontrando opção da tabela de carência segundo valor do contrato.")
        valores_opts: List[WebElement] = self.act.retornar_opcoes_select(loc_tabela)

        array_tabelas_menor_1200 = ['1194','2108']
        array_tabelas_maior_1200 = ['1948','4533']

        for valor_opt in valores_opts:
 
            if(self.__carenciaTabela == 0):
                if 'Car' in valor_opt.text:
                    continue

                # if '1,8' in valor_opt.text:
                #     continue

            if self._DadosProposta__tipo_beneficio != '87'and self._DadosProposta__tipo_beneficio != '88':
                if '87' in valor_opt.text or '88' in valor_opt.text  or 'loas' in valor_opt.text.lower():
                    print(self.__tipo_beneficio)
                    print('É tabela do tipo beneficio 87 e 88 e vai pular...')
                    continue

            #pdb.set_trace()

            if "DIG" in valor_opt.text:
                # filtro: expressão lambda a ser aplicada para filtrar o tipo de taxa na tabela
                if not filt(valor_opt.text):
                    continue

                if(valor_opt.get_attribute("value") == '2503' and self.nova_formalizazao_in100 == False):
                    continue

                if(valor_opt.get_attribute("value") in array_tabelas_menor_1200 and self.__val_contrato >= 2400):
                    continue

                if(valor_opt.get_attribute("value") == '1323' and self.__val_contrato >= 3000):
                    continue

                # if(valor_opt.get_attribute("value") == '2108' and self.__val_contrato >= 2000):
                #     continue

                print('---------Verificando tabela de valores--------')
                print(valor_opt.text)
                print('----------------------------------------------')
                print(comparar_valores_contrato(valor_opt.text, self.__val_contrato))
                print('----------------------------------------------')
                
                if comparar_valores_contrato(valor_opt.text, self.__val_contrato):
                    print("Valor selecionado:", valor_opt.text)
                    return valor_opt

        raise DadoIndisponivelException(nome="Valor Emprestimo", valor=str(self.__val_contrato))

    def __opcao_tabela_nova_proposta_sem_digital(self, loc_tabela: str, filt: Callable = lambda x: 1) -> WebElement:
        """
        Seleciona a opção correta na tabela de carência de acordo com a taxa de origem do contrato.
        Pode ser utilizado também um filtro para filtrar a oppção, também, segundo o texto da opçao
        da tabela.
        :param loc_tabela: localizador do elemento da tabela
        :param filt: função aplicada para filtrar as opções segundo o texto contigo nos elementos.
        :return: elemento web relativo à opção selecionada
        :raises: NotFoundResultException
        """
        print("Encontrando opção da tabela de carência segundo valor do contrato.")
        valores_opts: List[WebElement] = self.act.retornar_opcoes_select(loc_tabela)

        for valor_opt in valores_opts:

            if(self.__carenciaTabela == 0):
                if 'Car' in valor_opt.text:
                    continue

            if not "DIG" in valor_opt.text:
                # filtro: expressão lambda a ser aplicada para filtrar o tipo de taxa na tabela
                if not filt(valor_opt.text):
                    continue

                if comparar_valores_contrato(valor_opt.text, self.__val_contrato):
                    print("Valor selecionado:", valor_opt.text)
                    return valor_opt

        raise DadoIndisponivelException(nome="Valor Emprestimo", valor=str(self.__val_contrato))
