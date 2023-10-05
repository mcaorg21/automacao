"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: executar_anexo_docs
| data: 2020-03-11
| autor: Gustavo Belleza

| funcionamento:
"""

from .auxiliares import StatusPropostaException
from selenium.webdriver import Chrome
from .Anexar_docs_forms import PanDocumentosAnexo
from selenium.common.exceptions import TimeoutException


def pesquisar_proposta(driver: Chrome, dados: dict):
    """
    Realiza a pesquisa utizando o número da proposta (ADE) e verifica se
    há impedimentos ao anexo de docs. por meio do o STATUS, SITUAÇÃO e TIPO
    DE ASSINATURA. Caso não haja impedimentos, abre o modal de anexos.
    CAso haja, levanta uma exceção para que a proposta seja atualzida.
    :raises StatusPropostaException
    """
    from .Anexar_docs_forms import PanFormBuscarProposta

    form: PanFormBuscarProposta = PanFormBuscarProposta(driver, **dados)
    # Direcionar à consulta de propostas
    driver.get(form.url)

    # Pesquisar número da proposta
    form.input_texto_pesquisar_proposta()
    form.botao_pesquisar_proposta()

    # Verificar se há impedimentos para o anexo dos documentos
    form.extrair_situacao()
    form.extrair_tipo_assin()
    form.extrair_status_proposta()

    if 'REP' in form.situacao:
        raise StatusPropostaException(
            "PEN - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE"
        )
    elif 'CAN' in form.situacao:
        raise StatusPropostaException(
            "CAN - Não é possível anexar documentos."
        )
    elif 'REP' in form.situacao:
        raise StatusPropostaException(
            "REP - ERRO AO ANEXAR DOCUMENTOS NO BANCO ENVIAR MANUALMENTE"
        )
    if 'FÍSICO' in form.tipo_assn:
        raise StatusPropostaException('AnexoManual')

    if 'Aprovado' in form.status:
        raise StatusPropostaException(
            "PropostaAprovada - DOCUMENTOS ANEXADOS NO BANCO"
        )

    print("Proposta sem impedimentos para anexo de documentação")

    # Não há erros, abrir modal de anexos.
    form.clicar_iniciar_anexos()


def verificar_status_formalizacao(driver: Chrome):
    """
    No modal de escolha por anexar documentos, verifica se os
    documentos a serem anexados já foram marcados com anexados.
    Se sim, levanta uma exceção para que a proposta seja atualizada.
    Se não, seleciona a opção de seguir e anexar documentos.
    :raises StatusPropostaException
    """
    from .Anexar_docs_forms import PanFormStatusFormalizacao
    form: PanFormStatusFormalizacao = PanFormStatusFormalizacao(driver)

    try:
        status = form.verificar_status_docs_id()

        if status == 'anexado':
            raise StatusPropostaException(
                "DOCUMENTOS ANEXADOS NO BANCO"
            )
        form.clicar_botao_enviar()
    except TimeoutException:
        print("Tela de verificação de anexos não foi aberta.")


def download_documentos(driver: Chrome, docs_urls: list) -> PanDocumentosAnexo:
    """
    Seleciona na lista de URLs os documentos a serem baixados. Baixa os selecionados
    (Id e Contra-cheque) e retorna um objeto do tipo <PanDocumentosAnexo> que contém
    um dict com os caminhos dos documentos ('docIdFrente', 'docIdVerso','contraCheque')
    e o tipo de documento de identificação a ser inserido.
    """
    docs: PanDocumentosAnexo = PanDocumentosAnexo(driver, docs_urls)
    docs.selecionar_urls_docs()
    docs.download_doc_id_frente()
    docs.download_doc_id_verso()
    docs.download_contra_cheque()

    return docs


def anexar_documentos_cliente(driver: Chrome, docs: PanDocumentosAnexo, tipo: str):
    """
    Anexa os documentos relativos à proposta, de acordo com o parâmetro 'tipo', que
    pode se referir ao documento de identificação ou ao contra-cheque.
    :param driver: instância do Chromedriver.
    :param docs: intância da classe PanDocumentosAnexo na qual podem ser acessados os
    caminhos dos documentos no disco e o tipo de documento de identificação que será
    anexado.
    :param tipo: tipo de documento a ser inserido: identficiação ou contracheque.
    """
    from .Anexar_docs_forms import PanFormsAnexarDocs

    print("Anexando documentos:")

    form_id: PanFormsAnexarDocs = PanFormsAnexarDocs(
        driver, docs.paths_docs, docs.tipo_doc_id
    )

    loc_frame = '//*[@id="ctl00_Cph_FrameExterno"]'
    form_id.act.trocar_frame_seletor(loc_frame, form_id.by.XPATH)
    form_id.clicar_enviar_docs()

    if "contra_cheque" in tipo.lower():
        form_id.selecionar_anexar_contracheque()
        form_id.clicar_continuar_anexo_doc()
        form_id.enviar_anexo(n_campo=0, tipo='contraCheque')
    elif "identificacao" in tipo.lower():
        form_id.selecionar_anexar_id()
        form_id.clicar_continuar_anexo_doc()
        form_id.enviar_anexo(n_campo=0, tipo='docIdFrente')
        form_id.clicar_confirmar_anexo_doc()
        form_id.enviar_anexo(n_campo=1, tipo='docIdVerso')
        form_id.clicar_confirmar_anexo_doc()

        if not form_id.validar_anexos():
            form_id.enviar_anexo(n_campo=0, tipo='docIdFrente')
            form_id.clicar_confirmar_anexo_doc()
    else:
        raise Exception(
            f"Tipo {tipo} inválido. Usar 'identificacao' ou 'contrachque'"
        )

    form_id.clicar_continuar()




