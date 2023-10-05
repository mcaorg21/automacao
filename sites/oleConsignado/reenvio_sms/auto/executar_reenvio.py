"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: executar_reenvio
| data: 2020-02-13
| autor: Gustavo Belleza

| funcionamento:
"""
from sites.oleConsignado.reenvio_sms.auto.form_reenvio_sms import FormReenvioSMS
from time import sleep
import pdb


def executar_reenvio_sms(contrato: dict, driver: object) -> int:
    """
    Instancia a classe FormReenvioSMS, cujos métodos representam uma
    ação em um elemento do formulário. Preenche o formulário, invocando
    cada um desses métodos. Caso um erro seja encontrado, retorna status 0.
    Caso o reenvio seja bem sucedido, retorna status 1.
    :return: status [0 ou 1]
    """
    form = FormReenvioSMS(driver)
    # Dados do formulário
    ade: str = contrato['ade']
    ddd: str = contrato['ddd']
    celular: str = contrato['celular']

    # Campos do formulário
    form.campo_ade(ade)
    form.botao_pesquisar()

    form.aguardar_loading()

    bota_editar = form.botao_editar()     

    if bota_editar:
        return 1

    print('Assinatura ainda não concluída')

    # se não há proposta para a ADE, retornar status 0
    msg_erro_div: str = form.retornar_msg_div_erro()
    if 'nenhuma proposta' in msg_erro_div.lower():
        return 0
    elif 'número da proposta inválido' in msg_erro_div.lower():
        return 0
    elif msg_erro_div != '':
        raise Exception(msg_erro_div)

    #form.link_enviar_sms()
    form.campo_ddd(ddd)
    form.campo_celular(celular)
    form.botao_salvar_e_enviar()
    
    sleep(1)
    form.aguardar_loading()

    try:
        msg_erro_modal_primeiro = form.retornar_msg_div_erro_modal_primeiro()
    except:
        pass

    if(msg_erro_modal_primeiro is not None):
        if 'associado a outro cpf' in msg_erro_modal_primeiro.lower():
            return 2
        elif 'já existe um dossiê ativo ou proposta paga' in msg_erro_modal_primeiro.lower():
            return 2
        elif 'falha ao enviar sms' in msg_erro_modal_primeiro.lower():
            return 2
        elif 'telefone informado não é do tipo celular.' in msg_erro_modal_primeiro.lower():
            return 2

    msg_erro_modal = form.retornar_msg_div_erro_modal()

    if 'o sms foi reenviado com sucesso!' in msg_erro_modal.lower():
        return 1
    else:
        return 2

    # elif msg_erro_modal != '':
    #     raise Exception(msg_erro_modal)
    
    # msg_erro_div: str = form.retornar_msg_div_erro()
    # if 'espere mais um pouco' in msg_erro_div:
    #     sleep(10)
    #     raise Exception("ERRO: " + msg_erro_div)

    # se SMS foi enviado com sucesso, retornar status 1
    # sucesso: bool = form.verificar_modal_sucesso()
    # if sucesso:
    #     return 1
    # else:
    #     raise Exception("Não foi possível enviar o SMS")
