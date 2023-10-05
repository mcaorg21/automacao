"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: innss
| data: 2020-02-13
| autor: Gustavo Belleza
//*[@id="root"]/div/div[3]/div/div/label[1]
| funcionamento:
"""
from sites.inss.consulta_margem_sms.auto.FormsINSSConsultaMargem import (
    FormINSSDadosBanco, FormINSSDadosEmprestimos,
    FormINSSLogin, FormsINSSDadosCLiente, FormINSSLogout
)
from ..auto.auxiliares import tratar_erros, verificar_erros
from selenium.common.exceptions import TimeoutException
from time import sleep
from sites.baseRobos.core.DebugTools import DebugTools
from sites.inss.consulta_margem_sms.auto.auxiliares import ErroDadosConsultaException, ErroLoading, BeneficioCancelado
dt = DebugTools(debugging=False)

import pdb

urls = {
    'LOGIN': 'https://meu.inss.gov.br/#/login',
    #'CONSIGNADO': ('https://meu.inss.gov.br/central/#/login?redirectUrl=/emprestimo-consignado'),
    'CONSIGNADO': ('https://meu.inss.gov.br/#/emprestimo-consignado'),
    'CONSIGNADO_NOVO': ('https://meu.inss.gov.br/central/#'
                   '/login?redirectUrl=/eco'),
    'CENTRAL': 'https://meu.inss.gov.br/central/#/',
    'DADOS_CADASTRO': 'https://meu.inss.gov.br/central/#/dados-cadastrais',
    'URL_BENEFICIO_DIRETA': 'https://meu.inss.gov.br/central/#/meus-beneficios/'
}


def realizar_login(perfil: dict, driver: object) -> bool:
    """
    """
    try:
        form = FormINSSLogin(driver, perfil)

        form.chrome_driver.get(urls['LOGIN'])
        form.act.trocar_janela(0, 1)

        form.deletar_cookies()

        form.botao_sair()

        

        form.botao_entrar()

        # Alterar foco para janela de login

        form.act.trocar_janela(1, 2)

        url = driver.current_url

        driver.close()

        

        driver.switch_to.window(driver.window_handles[0])

        driver.execute_script("""window.open("","_blank");""")

        driver.switch_to.window(driver.window_handles[1])

        driver.get(url)


        form.preencher_cpf()

        # try:
        #     form.fechar_modal()
        # except:
        #     pass

        if(form.botao_avancar()):
            #form.verficar_erro_validacao()

            # Se necessário verificar a conta: erro -> atualizar contrato
            #form.verificar_janela_recuperar_conta()
            pdb.set_trace()
            try:
                form.preencher_senha()
            except:
                pass

            #desligado por causa do hcapctha
            #form.clicar_botao_entrar_login()
            form.resolver_RECAPTCHAv2()

            #if form.resolver_RECAPTCHAv2() == False:
            #    raise ErroDadosConsultaException('Erro ao resolver o captcha...')

            # Verificar se houve erro na validação do login
            form.verficar_erro_validacao()
            form.autorizar_uso_dados_inss()

            sleep(0.5)
            form.act.trocar_janela(0, 1)
            tratar_erros(verificar_erros(form.act, form.by))

            return True
        else:
            return False

    except TimeoutException:
        print("Usuario Já está logado.")
        return False


def executar_busca_margem(driver: object, perfil: dict, rec=0) -> dict:
    """
    Busca dados pessoais do cliente e dados relativos à margem.
    Retorna os dados extraídos do site.
    :return:  {
        nomeCompleto: nome completo do cliente,
        margemDisponivel: margem consignável do cliente,
        margemDisponivelCartao: margem do cartão magnético,
        creditoTotal: base de cálculo para o empréstimo
    }
    """
    form = FormsINSSDadosCLiente(driver)
    dt.debugger()

    loc_loading = '//*[@id="root"]/div/div[2]/main/div/div[2]/div/i'
    form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

    # PAGINA DO BENEFICIO
    form.chrome_driver.get(urls['CONSIGNADO_NOVO'] + '/' + perfil['matricula'])
    sleep(1)
    form.chrome_driver.get(urls['CONSIGNADO'] + '/' + perfil['matricula'])

    # => Página de Empréstimos Consignados
    #form.chrome_driver.get(urls['CONSIGNADO'])

    erro_inicial = tratar_erros(verificar_erros(form.act, form.by), perfil)
    
    if(erro_inicial and erro_inicial['erro']['erro'] and 'Ocorreu um erro ao buscar seus dados' in erro_inicial['erro']['erro']): 
        for i in range(0,4):
            try: 
                print('Tentando novamente...')
                form.act.clicar_elemento('//*[@id="root"]/div/div[3]/main/div/div[2]/button',form.by.XPATH)
            except:
                print('Não achou o botão...')
                sleep(3)
                pass


    # Iterar por todas opções de benefícios do cliente. Clicar apenas naquela
    #   marcada como 'Ativo' e com a mesma matricula que a do contrato.
    #form.qtd_beneficios_presentes = form.quantidade_beneficios_do_perfil()

    # if not form.ha_beneficios_ativos():
    #     raise ErroDadosConsultaException({'retorno': 5, 'erro': "Não há benefícios ativos"})

    # selecionado: bool = False
    # for idx in range(form.qtd_beneficios_presentes):
    #     if not form.beneficio_ativo(idx):
    #         continue

    #     form.extrair_txt_matriculas(idx+1)
    #     selecionado = form.selecionar_matricula_beneficios(perfil['matricula'], idx+1)
    #     if selecionado:  # => página do benefício selecionado
    #         break

    # if not selecionado:
    #     raise ErroDadosConsultaException({'retorno': 5, 'erro': "Não há benefícios ativos"})

    loc_loading = '//*[@id="root"]/div/div[2]/main/div/div[2]/div/i'
    form.act.esta_presente_recursivo(loc_loading, form.by.XPATH)

    situacao = form.extrair_situacao_beneficio()

    if not situacao:
        raise ErroLoading('Pagina nao carregada')

    if 'CESSADO' in situacao:
        raise BeneficioCancelado('Beneficio Cessado')


    erro = verificar_erros(form.act, form.by)
    if erro:
        tratar_erros(verificar_erros(form.act, form.by))

    try:
        form.extrair_tipo_beneficio()
    except TimeoutException:
        pass

    # Extrair dados margem
    try:
        form.extrair_margem_emprestimo()
        form.extrair_margem_cartao_mag()
    except TimeoutException:
        raise ErroLoading('Pagina nao carregada')
        # raise ErroDadosConsultaException(
        #     {"erro": "Margem indisponivel no site.", "retorno": 4})
    print("Resultado busca margem", form.dados_margem)

    return form.dados_margem


def executar_busca_dados_bancarios(drive: object) -> dict:
    """
    Busca e retorna os dados bancarios do cliente extraídos do site.
    :return: {
        "banco": número e nome do banco,
        "agencia": nº agencia,
        "conta": nº conta,
        "digitoConta": dv conta,
        "tipoConta": tipo da conta para liberação do empréstimo.
    }
    """
    
    form = FormINSSDadosBanco(drive)
    form.extrair_codigo_nome_banco()
    form.extrair_agencia()
    form.extrair_nconta_e_dv()
    form.extrair_tipo_conta()

    print("Resultado busca banco", form.dados_bancarios)

    return form.dados_bancarios


def executar_busca_dados_emprestimos(driver: object) -> dict:
    """
    Extrai os dados de cada empréstimo listado na página. Clica, abre a aba
    relativa ao empréstimo e retira os dados bancários e dados específicos
    do financiamento.
    :return:
    {
        retorno: 1  # sucesso,
        arrayConsultaRefin: list de dicts com dados dos empréstimos,
        arrayParcelasRefin: list com valores das parcelas dos empréstimos,
        valorEmprestimos: valor total dos empréstimos
    }
    """
    form = FormINSSDadosEmprestimos(driver)

    n_emprestimos: int = form.quantidade_emprestimos()

    # Cada iteração representa a aba de um empréstimo e seus dados.
    for idx in range(n_emprestimos):
        try:
            form.selecionar_emprestimo(idx)
        except:
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
            continue
        
        form.extrair_status_contrato(idx)        
        if(form.dados_do_emprestimo['statusContrato'] == 'Ativo'):
            form.extrair_n_banco(idx)
            #dt.debugger()
            form.extrair_valor_presente_inicial(idx)
            form.extrair_valor_parcela(idx)
            form.extrair_data_inicio_desconto(idx)
            form.calcular_parcelas_pagas()
            form.extrair_parcelas_totais(idx)

            print(form.dados_do_emprestimo)
            form.atualizar_lista_emprestimos()

    resultado =  {'retorno': 1,
                'arrayConsultaRefin': form.lista_emprestimos,
                'arrayParcelasRefin': form.lista_parcelas,
                'valorEmprestimos': form.calcular_valor_emprestimos(),
                'numeroEmprestimos': len(form.lista_emprestimos)}

    return resultado


def realizar_logout(driver: object):
    form = FormINSSLogout(driver)
    form.chrome_driver.get(urls['CENTRAL'])
    try:
        form.clicar_botao_logout()
    except TimeoutException:
        print("Não foi necessário realizar logout.")
