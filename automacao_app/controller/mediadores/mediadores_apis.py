from typing import Dict
from flask import Blueprint, request
from automacao_app import templates
from automacao_app.controller.helpers.TimePoints import TimePoints
from dados.helpers.Queue import (
    Queue, EmptyQueueAccessAttemptException)
from dados.APIGetSource import APIGetSource
import json,pdb


bp = Blueprint("routing", __name__, template_folder=templates)

fila_propostas = Queue()
fila_contratos_insercao = Queue()

refin_request_time = TimePoints()
insercao_request_time = TimePoints()

query_flag_insercao = {}
query_flag_refin = {}

queues_colicitacoes: Dict[str, Queue] = {}
queues_contratos: Dict[str, Queue] = {}

tfs_refin: Dict[str, TimePoints] = {}
tfs_insercao: Dict[str, TimePoints] = {}


@bp.route("/routing/solicitacoes-refin/<banco>")
def distribuir_filas_refin(banco: str):
    print(f"\n{banco.upper()} REFINANCIAMENTO", )

    proposta: dict = {}

    if not tfs_refin.get(banco, False):
        tfs_refin[banco] = TimePoints()
        tfs_refin[banco].set_time_point("request")
        query_flag_refin[banco] = "first"

    if not queues_colicitacoes.get(banco, False):
        queues_colicitacoes[banco] = Queue()

    if query_fila_refin_enabled(banco, query_flag_refin[banco]):
        print("REQUEST...")

        tfs_refin[banco].update_time_point("request")
        query_flag_refin[banco] = "null"

        queues_colicitacoes[banco] = Queue.from_list(APIGetSource(banco).solicitacoes_consulta_refinanciamento()['solicitacoes'])
        queues_colicitacoes[banco].extend_from_list(APIGetSource(banco).solicitacoes_consulta_crm()['pessoas'])
    
    try:
        if(banco == 'pan'):
            proposta = queues_colicitacoes[banco].get(True)
        else:
            proposta = queues_colicitacoes[banco].get()
    except EmptyQueueAccessAttemptException:
        return '[]'

    print("Instancia: ", request.args.get("instancia", "DEFAULT"))
    print("LENGHT", queues_colicitacoes[banco].length)
    #print("SOLICITACAO: ", proposta.get('idSolicitacao', "idPessoa"))

    return json.dumps(proposta)


@bp.route("/routing/contratos-insercao/<banco>")
def distribuir_filas_insercao(banco: str):
    print(f"\n{banco.upper()} INSERÇÃO", )
    contrato: dict = {}
    if not tfs_insercao.get(banco, False):
        tfs_insercao[banco] = TimePoints()
        tfs_insercao[banco].set_time_point("request")
        query_flag_insercao[banco] = "first"

    if not queues_contratos.get(banco, False):
        queues_contratos[banco] = Queue()

    if query_fila_insercao_enabled(banco, query_flag_insercao[banco]):
        print("REQUEST...")
        query_flag_insercao[banco] = "null"
        tfs_insercao[banco].update_time_point("request")
        queues_contratos[banco] = Queue.from_list(
            APIGetSource(banco).fila_contratos_inserir()['contratos'])

    try:
        contrato = queues_contratos[banco].get()
    except EmptyQueueAccessAttemptException:
        return '[]'

    print("Instancia: ", request.args.get("instancia"))
    print("LENGHT", queues_contratos[banco].length)
    print("CONTRATO: ", contrato['codigo_con'])

    return json.dumps(contrato)


def query_fila_insercao_enabled(banco: str, flag: str) -> bool:
    length_cond = queues_contratos[banco].length == 0
    time_cond = tfs_insercao[banco].elapsed_since("request") > 240
    print(f"LEN COND: {length_cond}. TIME COND: {time_cond}")
    print("FLAG", flag)

    if flag == "first":
        return True

    return length_cond and time_cond


def query_fila_refin_enabled(banco: str, flag: str) -> bool:
    length_cond = queues_colicitacoes[banco].length == 0
    time_cond = tfs_refin[banco].elapsed_since("request") > 180
    print(f"LEN COND: {length_cond}. TIME COND: {time_cond}")
    print("FLAG", flag)

    if flag == "first":
        return True

    return length_cond and time_cond
