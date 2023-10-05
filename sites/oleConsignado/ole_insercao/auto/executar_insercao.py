"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: executar_insercao
| data: 2020-02-04
| autor: Gustavo Belleza

    Utiliza as classes representantes dos formulários para
implementar a automação do processo de inserção. Cada função
executa a automação de apenas um formulário (ou seção lógica
de um formulário). Para tanto, cada função instancia apenas
uma classe.
    Funções principais:
    1. preencher_formulario_identificacao. 2. preencher_dados_proposta_insercao.
    3. preencher_dados_pessoais. 4. preencher_dados_bancarios.
    5. finalizar_insercao.
"""
# Classes dos formularios.
from .FormsInsercao import (
    AbaDadosSimulacao, AbaDadosCliente,
    AbaDadosOperacao, AbaResumo
)
# Funções auxiliares.
from .auxiliares import (verificar_modais, verificar_erros, tratar_mensagens_erro)

import pdb

from time import sleep

def preencher_dados_simulacao(driver: object, contrato: dict, tipo_contrato: str, tentativa = 0) -> dict:
    form = AbaDadosSimulacao(driver)

    #INSS
    codigo_convenio = '011398'
    federal_estadual = False
    produto = "012574"
    prazo = 84

    if contrato['dadosProfissionais']['perfil'] == '2' or 'Servidor Federal' in contrato['dadosProfissionais']['perfil']:
        #SIAPE
        codigo_convenio = '013579'
        federal_estadual = True
        produto = "006017"
        prazo = 96
    elif contrato['dadosProfissionais']['perfil'] == '1':
        #SP ESTADO
        if(contrato['dadosProfissionais']['idEstado']) == '25':
            codigo_convenio = '014583'
            federal_estadual = True
            produto = "008045"
            prazo = 96


    form.verificar_loading()
    erro = verificar_erros(form.act, form.by)
    if erro:
        tratar_mensagens_erro(erro, contrato, form.uconecte)

    print("Preenchendo aba de simulação")
    
    if tipo_contrato == 'REFINANCIAMENTO':
        # try:
        #     form.select_orgao(contrato['dadosProfissionais']['orgao'])
        #     form.escolher_parcela(contrato)
        # except:

        # in100 = form.pedir_in_100(contrato)

        # if in100 == False:
        #     atualizacoes = {}
        #     print('Pedindo token...')
        #     atualizacoes['retorno'] = False
        #     atualizacoes['autorizar_token'] = True
        #     return atualizacoes
        form.verificar_loading()
        try:
            retorno_consulta_margem = form.informacao_margem()
            if 'retorno' in retorno_consulta_margem and retorno_consulta_margem['retorno'] == False:
                return retorno_consulta_margem
        except:
            pass

        form.verificar_loading()
        parcela_ativa = form.escolher_parcela(contrato)

        if(parcela_ativa == False):
            atualizacoes = {}
            atualizacoes['retorno'] = False
            return atualizacoes

        try:
            form.select_especie_beneficio(contrato)
            parcela_ativa = form.escolher_parcela(contrato)
        except:
            pass

        atualizacoes = form.realizar_consulta_refinanciamento(contrato)

        print(atualizacoes)

        verificar_modais(form.act, form.by)
    elif tipo_contrato == 'PORTABILIDADE':
        try:
            form.input_texto_data_nascimento(contrato)  
        except:
            pass
        verificar_modais(form.act, form.by)
        form.input_texto_convenio()    
        form.verificar_loading()

        verificar_modais(form.act, form.by)
        form.select_operacao()
        verificar_modais(form.act, form.by)
        form.select_tipo_operacao('3')

        try:
            if not form.verifica_convenio_escolhido():
                atualizacoes = {}
                print('Pulando inserção.... Falha no sistema...')
                atualizacoes['retorno'] = False
                atualizacoes['pular'] = True
                return atualizacoes
        except:
            pass

        # in100 = form.pedir_in_100(contrato)

        # if in100 == False:
        #     atualizacoes = {}
        #     print('Pedindo token...')
        #     atualizacoes['retorno'] = False
        #     atualizacoes['autorizar_token'] = True
        #     return atualizacoes

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        try:
            retorno_consulta_margem = form.informacao_margem()
            if retorno_consulta_margem['retorno'] == False:
                return retorno_consulta_margem
        except:
            pass

        form.campo_matricula(contrato)
        verificar_modais(form.act, form.by)

        try:
            retorno_consulta_margem = form.informacao_margem()
            if retorno_consulta_margem['retorno'] == False:
                return retorno_consulta_margem
        except:
            pass

        form.select_especie_beneficio(contrato)
        form.select_especie_beneficio(contrato)

        try:
            form.preencher_dados_banco_portabilidade(contrato)
        except:
            tentativa += 1
            if(tentativa <= 10):
                print('Tentativa' + str(tentativa))
                try:
                    form.input_texto_data_nascimento(contrato)  
                except:
                    pass
                return preencher_dados_simulacao(driver,contrato,tipo_contrato,tentativa)

        verificar_modais(form.act, form.by)

        erro = verificar_erros(form.act, form.by)

        recr_saldo_primeiro = 0
        diminui_novo_saldo_devedor = 0
        saldo_devedor_novo = 0

        while 'A Taxa da Portabilidade está fora dos valores parametrizados' in erro or 'Não foi possível simular comissionamento do complemento de portabilidade com os dados informados' in erro:
            print('Tentando atualizar calculo...')
            diminui_novo_saldo_devedor -= 150 
            form.preencher_dados_banco_portabilidade(contrato, True, diminui_novo_saldo_devedor)
            erro = verificar_erros(form.act, form.by)
            recr_saldo_primeiro += 1            
            saldo_devedor_novo = float(contrato['dados_portabilidade']['saldoDevedorFinal']) + diminui_novo_saldo_devedor      
            if(recr_saldo_primeiro == 200 or saldo_devedor_novo >= 1.25 * float(contrato['dados_portabilidade']['valorPresenteInicial']) ):
                print('Desistência do calculo...')
                erro = 'Valor da taxa está fora dos limites do parâmetro' 
                break

            if(form.parar_while_tentativas() == True):
                print('Parando o while...')
                break

        recr_saldo_segundo = 0
        soma_novo_saldo_devedor = 0

        while 'Valor da taxa está fora dos limites do parâmetro' in erro:
            print('Tentando atualizar calculo...')
            soma_novo_saldo_devedor += 50
            if(saldo_devedor_novo > 0):
                contrato['dados_portabilidade']['saldoDevedorFinal'] = str(saldo_devedor_novo)
            form.preencher_dados_banco_portabilidade(contrato, True, soma_novo_saldo_devedor)
            erro = verificar_erros(form.act, form.by)
            recr_saldo_segundo += 1            
            saldo_devedor_novo = float(contrato['dados_portabilidade']['saldoDevedorFinal']) + soma_novo_saldo_devedor      
            if(recr_saldo_segundo == 200 or saldo_devedor_novo >= 1.25 * float(contrato['dados_portabilidade']['valorPresenteInicial']) ):
                print('Desistência do calculo...')
                erro = 'Valor da taxa está fora dos limites do parâmetro' 
                break

            if(form.parar_while_tentativas() == True):
                print('Parando o while...')
                break

        if(recr_saldo_primeiro > 0 or recr_saldo_segundo > 0 and saldo_devedor_novo > 0):
            contrato['dados_portabilidade']['saldoDevedorFinal'] = str(float(contrato['dados_portabilidade']['saldoDevedorFinal']) + soma_novo_saldo_devedor + diminui_novo_saldo_devedor)
            print('Novo saldo devedor: ' + contrato['dados_portabilidade']['saldoDevedorFinal'] )

        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        atualizacoes = form.comparar_resultado_parcela(contrato,0,contrato['dados_portabilidade']['saldoDevedorFinal'])
        atualizacoes['valorSaldoDevedorPortabilidade'] = contrato['dados_portabilidade']['saldoDevedorFinal']

        if(atualizacoes == False):
            raise Exception("Não foi possível ajustar a parcela...")

        print(atualizacoes)

        verificar_modais(form.act, form.by)
        form.botao_prosseguir_proposta_portabilidade()
 
    else:        

        verificar_modais(form.act, form.by)

        form.input_texto_data_nascimento(contrato)

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        form.input_texto_convenio(codigo_convenio)
        form.verificar_loading()

        verificar_modais(form.act, form.by)

        
        if federal_estadual:            
            form.select_sub_orgao(contrato)
        else:
            form.select_especie_beneficio(contrato)

        form.verificar_loading()

        verificar_modais(form.act, form.by)

        form.select_operacao()
        form.select_tipo_operacao()

        try:
            if not form.verifica_convenio_escolhido():
                atualizacoes = {}
                print('Pulando inserção.... Falha no sistema...')
                atualizacoes['retorno'] = False
                atualizacoes['pular'] = True
                return atualizacoes
        except:
            pass

        if not federal_estadual:
            in100 = form.pedir_in_100(contrato)
            in100 = True
            if in100 == False:
                atualizacoes = {}
                print('Pedindo token...')
                atualizacoes['retorno'] = False
                atualizacoes['autorizar_token'] = True
                return atualizacoes

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        if tipo_contrato == 'NOVO SEM SEGURO' and not federal_estadual:
            try:
                retorno_consulta_margem = form.informacao_margem()

                if retorno_consulta_margem['retorno'] == False:
                    return retorno_consulta_margem

                if(retorno_consulta_margem['margem'] < 8):
                    retorno_consulta_margem['retorno'] = False
                    return retorno_consulta_margem

                if(retorno_consulta_margem['margem'] < float(contrato['valorParcela'].replace(',','.'))):
                    contrato['valorParcela'] = retorno_consulta_margem['margem'].replace('.',',')
                    atualizacoes['valorParcela'] = retorno_consulta_margem['margem']

            except:
                pass

        form.input_radio_contratacao_digital()
        verificar_modais(form.act, form.by)

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        form.campo_matricula(contrato)
        form.verificar_loading()

        verificar_modais(form.act, form.by)
        form.verificar_loading()
        form.input_texto_parcela(contrato) # Erro acontece aq
        verificar_modais(form.act, form.by)

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        erro = form.botao_calcular_emprestimo()

        try:
            if 'erro' in erro:
                tratar_mensagens_erro(erro['erro'], contrato, form.uconecte)
        except:
            pass

        if not erro:
            form.input_texto_parcela(contrato) # Erro acontece aq
            form.botao_calcular_emprestimo()
            verificar_modais(form.act, form.by)

        verificar_modais(form.act, form.by)

        erro = verificar_erros(form.act, form.by)

        if "Ocorreu" in erro:
            print("ERRO", erro)
            form.botao_calcular_emprestimo()
        elif erro:
            print("ERRO", erro)
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        verificar_modais(form.act, form.by)

        # Selecionar produto 006007 - VD_INSS
        form.input_selecionar_produto(produto)

        # Selecionar opção de faixa de prazo de acordo com aquele presente no contrato.
        prazo_atualizado = form.selecionar_qtd_parcelas(contrato['prazo'])
        form.verificar_loading()

        # Só é necessário calcular o empréstimo novamente se prazo < convenio proposta
        if int(contrato['prazo']) < prazo:
            form.botao_calcular_emprestimo()
            form.verificar_loading()

            erro = verificar_erros(form.act, form.by)            
            tratar_mensagens_erro(erro, contrato, form.uconecte)

            if "Ocorreu" in erro:
                print("ERRO", erro)
                form.botao_calcular_emprestimo()

            if erro:
                print("ERRO", erro)
                tratar_mensagens_erro(erro, contrato, form.uconecte)

        # Buscar a linha da tabela cujo prazo se enquadra ao prazo do contrato
        #   caso não haja, utilizar o prazo sugerido pelo site
        idx_tabela: int = form.encontrar_linha_prazo_tabela(prazo_atualizado,contrato,tipo_contrato)
        
        # Atualizar prazo e valor do empréstimo no contrato
        atualizacoes: dict = form.extrair_dados_prazo_valor_emprestimo(idx_tabela)
        print(atualizacoes)
        # Selecionar checkbox da linha com os dados atualizados
        form.check_box_produto(idx_tabela)
        verificar_modais(form.act, form.by)
        form.botao_prosseguir_proposta()
        verificar_modais(form.act, form.by)

        erro = verificar_erros(form.act, form.by)
        
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

    return atualizacoes

def preencher_dados_In100(driver: object, contrato: dict, tipo_contrato: str, tentativa = 0) -> dict:
    atualizacoes = True

    form = AbaDadosSimulacao(driver)

    form.verificar_loading()
    erro = verificar_erros(form.act, form.by)
    if erro:
        tratar_mensagens_erro(erro, contrato, form.uconecte)

    print("Preenchendo aba de simulação")
    
    if tipo_contrato == 'REFINANCIAMENTO':
        # try:
        #     form.select_orgao(contrato['dadosProfissionais']['orgao'])
        #     form.escolher_parcela(contrato)
        # except:

        in100 = form.pedir_in_100(contrato)

        if in100 == False:
            atualizacoes = {}
            print('Pedindo token...')
            atualizacoes['retorno'] = False
            atualizacoes['autorizar_token'] = True
            return atualizacoes

    elif tipo_contrato == 'PORTABILIDADE':
        try:
            form.input_texto_data_nascimento(contrato)  
        except:
            pass
        verificar_modais(form.act, form.by)
        form.input_texto_convenio()    
        form.verificar_loading()

        verificar_modais(form.act, form.by)
        form.select_operacao()
        verificar_modais(form.act, form.by)
        form.select_tipo_operacao('3')

        try:
            if not form.verifica_convenio_escolhido():
                atualizacoes = {}
                print('Pulando consulta.... Falha no sistema...')
                atualizacoes['retorno'] = False
                atualizacoes['pular'] = True
                return atualizacoes
        except:
            pass

        in100 = form.pedir_in_100(contrato)

        if in100 == False:
            atualizacoes = {}
            print('Pedindo token...')
            atualizacoes['retorno'] = False
            atualizacoes['autorizar_token'] = True
            return atualizacoes

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)
 
    else:        

        verificar_modais(form.act, form.by)

        form.input_texto_data_nascimento(contrato)

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

        form.input_texto_convenio()
        form.verificar_loading()

        verificar_modais(form.act, form.by)

        form.select_especie_beneficio(contrato)
        form.verificar_loading()

        verificar_modais(form.act, form.by)

        form.select_operacao()
        form.select_tipo_operacao()

        try:
            if not form.verifica_convenio_escolhido():
                atualizacoes = {}
                print('Pulando inserção.... Falha no sistema...')
                atualizacoes['retorno'] = False
                atualizacoes['pular'] = True
                return atualizacoes
        except:
            pass

        in100 = form.pedir_in_100(contrato)

        if in100 == False:
            atualizacoes = {}
            print('Pedindo token...')
            atualizacoes['retorno'] = False
            atualizacoes['autorizar_token'] = True
            return atualizacoes

        erro = verificar_erros(form.act, form.by)
        if erro:
            tratar_mensagens_erro(erro, contrato, form.uconecte)

    retorno_consulta_margem = form.informacao_margem()

    if erro:
        tratar_mensagens_erro(erro, contrato, form.uconecte)
        return '0'
        
    if 'retorno' in retorno_consulta_margem:
        return retorno_consulta_margem

    return atualizacoes

def preeencher_dados_cliente(driver: object, contrato: dict):
    form = AbaDadosCliente(driver)
    print("Aba Dados Cliente.")
    form.input_texto_cpf(contrato)
    form.input_texto_nome(contrato)

    verificar_modais(form.act, form.by)

    forcar_email = True
    if(contrato['email'] == 'emprestimo@uconecte.me'):
        forcar_email = False


    form.input_texto_email(contrato,forcar_email)
    form.input_text_ddd_celular(contrato)
    form.input_texto_renda_bruta(contrato)
    form.input_texto_nome_mae(contrato)
    form.input_texto_rg(contrato)
    form.input_radio_sms()

    # TODO: VERIFICAR ERROS ESPORÁDICOS NO PREENCHIMENTO DO CEP
    #   É PROVÁVEL QUE O PREENCHIMENTO ESTEJA OCORRENDO ANTES DO FIM
    #   DO 'LOADING'.

    form.input_texto_cep(contrato)

    form.select_tipo_uf(contrato)

    erro = form.div_erro_cep()
    if erro:
        tratar_mensagens_erro(erro, contrato, form.uconecte)

    form.select_cidade(contrato)
    form.input_texto_ncasa(contrato)
    form.select_tipo_logradouro()
    form.input_texto_logradouro(contrato)
    form.input_texto_complemento(contrato)
    form.input_texto_bairro(contrato)
    form.botao_prosseguir()

    verificar_modais(form.act, form.by)

    erro_email = form.div_erro_email()
    if erro_email:
        form.input_texto_email(contrato,True)
        form.botao_prosseguir()

def preencher_dados_operacao(driver: object, contrato: dict):
    print("Aba Dados Operação.")
    form = AbaDadosOperacao(driver)

    itr: int = 0
    while not form.aguardar_aba_dados_operacao():
        itr += 1
        erro = verificar_erros(form.act, form.by)
        if itr >= 5:
            raise Exception("Não foi possível abrir aba 'Dados da Operação'")
        elif erro:
            print('Tratando o erro ----- Preencher dados da operação')
            tratar_mensagens_erro(erro, contrato, form.uconecte)
            break

    form.input_texto_cpf_vendedor()
    
    try:
        form.input_texto_codigo_margem()
    except:
        pass

    form.select_tipo_conta_corrente(contrato)
    form.input_texto_nbanco(contrato)
    form.select_agencia(contrato)
    form.input_texto_dv_agencia(contrato)
    form.input_texto_dv_conta(contrato)

    verificar_modais(form.act, form.by)

    form.botao_prosseguir_aba_resumo()

    erro = verificar_erros(form.act, form.by)
    if erro:
        tratar_mensagens_erro(erro, contrato, form.uconecte)

def confirmar_aba_resumo(driver: object, tipo_contrato=None) -> bool:
    import time
 
    try:
        form = AbaResumo(driver)
        if tipo_contrato == 'REFINANCIAMENTO':
            time.sleep(0.5)
            form.botao_finalizar_refin()
            time.sleep(0.5)
            form.botao_finalizar_refin()
            time.sleep(0.5)
            form.botao_finalizar_refin()
            time.sleep(1)
        elif tipo_contrato == 'PORTABILIDADE':
            time.sleep(1)
            form.botao_finalizar_portabilidade()
            time.sleep(1)
            form.botao_finalizar_portabilidade()
            time.sleep(1)
            form.botao_finalizar_portabilidade()
            time.sleep(1)
        else:
            time.sleep(0.5)
            form.botao_finalizar_emprestimo()
            time.sleep(0.5)
            form.botao_concluir_emprestimo()
            time.sleep(0.5)
            form.modal_cancelar_cartao_com_permissao()
            time.sleep(1)

        form.erro_pagina_503()

        if form.final_insercao() == False:
            print('Não inseriu contrato porque não chegou no final da inserção...')
            raise Exception("Não foi possível inserir contrato...")

        return True

    except Exception as e:
        print(e.args)

        return False