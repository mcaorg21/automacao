from flask import Blueprint, request, render_template, abort, redirect, url_for, send_file
from datetime import date, datetime, timedelta
import json, pdb, io
import pandas as pd
from automacao_app import templates
from initializr import INITIALIZR_ROOT
from pathlib import Path

file = str(Path(f"{INITIALIZR_ROOT}/ativacao.json"))
labels_file = str(Path(f"{INITIALIZR_ROOT}/process_labels.json"))
cpj_config_file = str(Path(INITIALIZR_ROOT).parent / "sites/cpj-reembolso-bmg/config.json")
omni_config_file = str(Path(INITIALIZR_ROOT).parent / "sites/omni-pde-fsp-trc/config.json")
bloqueados_spf_file = str(Path(INITIALIZR_ROOT).parent / "cpj_api/bloqueados_id_spf.json")
pan_config_file = str(Path(INITIALIZR_ROOT).parent / "sites/cpj-reembolso-pan/config.json")
bp = Blueprint("ativacao", __name__, template_folder=templates)


def _load_cpj_config():
    with open(cpj_config_file) as f:
        return json.loads(f.read())


def _load_omni_config():
    with open(omni_config_file, encoding='utf-8') as f:
        return json.loads(f.read())


def _load_pan_config():
    with open(pan_config_file, encoding='utf-8') as f:
        return json.loads(f.read())


def _date_to_iso(date_str):
    """Converte dd/mm/yyyy para yyyy-mm-dd (formato do input date HTML)."""
    try:
        d, m, y = date_str.split("/")
        return f"{y}-{m}-{d}"
    except Exception:
        return ""


def _date_from_iso(date_str):
    """Converte yyyy-mm-dd para dd/mm/yyyy."""
    try:
        y, m, d = date_str.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return date_str


def _tempo_decorrido(iniciado_em_str):
    if not iniciado_em_str:
        return None
    try:
        iniciado = datetime.strptime(iniciado_em_str, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - iniciado
        total = int(delta.total_seconds())
        horas = total // 3600
        minutos = (total % 3600) // 60
        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"
    except Exception:
        return None

@bp.route('/codigo', methods=["GET", "POST"])
def salvar_codigo():
    codigo = request.args.get("codigo") or request.form.get("codigo")

    if not codigo:
        return "Código não informado", 400

    caminho_arquivo = "/home/gustavo/Desktop/automacao-python/sites/crefisa/libs/codigo.txt"

    try:
        with open(caminho_arquivo, "w") as f:
            f.write(codigo.strip())
        return "Código salvo com sucesso", 200
    except Exception as e:
        return f"Erro ao salvar: {str(e)}", 500
        

@bp.route('/consulta-portal-inss', methods=["GET", "POST"])
def ativacao_post():
    from sites.inss.consulta_margem_sms.managers.consulta_margem_inss import ConsultaMargemInss
    consultar = ConsultaMargemInss()
    perfil = request.json
    resultado = consultar.main_consulta_via_post(perfil)
    return resultado

@bp.route('/emitir-qrcode-acreditar', methods=["GET", "POST"])
def consulta_qrcode_acreditar():
    from sites.cora.main import IniciarEmissaoConsulta
    dados_emissao = request.json
    if not "key" in request.json:
        abort(403)
    if dados_emissao["key"] != "a6c4ab920274388cf66b736331e07907":
        return {"tipo":"alert","mensagem":"key inválida"}
    consultar = IniciarEmissaoConsulta()
    resultado = consultar.main(dados_emissao)
    resultado['tipo'] = "success"
    return resultado

@bp.route('/consulta_promobank', methods=['POST'])
def webhook():
    from flask import Flask, request, abort
    if request.method == 'POST':

        from sites.promoBank.promo_bank import PromoBank
        promobank = PromoBank()
        promobank.load_cookies_promobank_web_admin()

        valida_horario = promobank.validar_horario_api()
        if(valida_horario['status'] == 'fora_horario'):
            print('Fora do horário')
            abort(400)  
        solicitacao = request.json
        dados = promobank.main_api(solicitacao,'api')
        print(dados)
        #if(json.loads(dados['consultaBeneficio'])['retorno'] == 11 or ('retorno' in dados and dados['retorno'] == 11)):post
            #promobank.load_cookies_promobank_web_admin()
        promobank.fechar_driver()
        return dados
    else:
        abort(400)

@bp.route('/abre_promobank', methods=['GET'])
def webhook2():
    if request.method == 'GET':
        dados = promobank.main()
        return 200
    else:
        abort(400)

@bp.route('/consulta_cpf', methods=['GET'])
def webhook3():
    from flask import Flask, request, abort
    if request.method == 'GET': 
        from sites.promoBank.promo_bank import PromoBank

        promobank = PromoBank()
        promobank.load_cookies_promobank_web_admin()

        valida_horario = promobank.validar_horario_api()
        cpf = request.args['cpf']
        if(valida_horario['status'] == 'fora_horario'):
            print('Fora do horário')
            abort(400)  
        if not cpf:
            print('Cpf não enviado.')
            abort(404)
        retorno = promobank.cosulta_beneficio_cpf(cpf)
        promobank.fechar_driver()
        return retorno
    else:
        promobank.fechar_driver()
        abort(400)    

PROCESSOS_VISIVEIS = ["CpjReembolsoBmg", "OmniPdeFspTrc", "CpjReembolsoPan"]

@bp.route("/ativacao", methods=["GET", "POST"])
def ativacao():
    print(templates)
    activate: dict = {}

    with open(file) as fObj:
        activate = json.loads(fObj.read())
        fObj.close()

    if request.method == "POST":
        if "buscar" in request.form:
            busca_activate: dict = {}
            for key, val in activate.items():
                if request.form["buscar"].lower() in key.lower():
                    busca_activate[key] = val
            activate = busca_activate
        else:
            for key, val in request.form.items():
                status = None
                if val == "Ativar":
                    activate[key] = True
                elif val == "Desativar":
                    activate[key] = False
                    if key == "CpjReembolsoBmg":
                        config_atual = _load_cpj_config()
                        config_atual["numero_recibo"] = ""
                        config_atual["iniciado_em"] = ""
                        with open(cpj_config_file, mode="w") as f:
                            f.write(json.dumps(config_atual, ensure_ascii=False, indent=4))
                    if key == "CpjReembolsoPan":
                        config_atual = _load_pan_config()
                        config_atual["numero_recibo"] = ""
                        config_atual["iniciado_em"] = ""
                        with open(pan_config_file, mode="w", encoding='utf-8') as f:
                            f.write(json.dumps(config_atual, ensure_ascii=False, indent=4))

            with open(file, mode="w") as fObj:
                fObj.write(json.dumps(activate))
                fObj.close()
                print(activate)

    procs = {k: v for k, v in activate.items() if k in PROCESSOS_VISIVEIS}

    today = date.today().isoformat()
    cpj_config = _load_cpj_config()
    cpj_config["data_inicial_iso"] = _date_to_iso(cpj_config.get("data_inicial", "")) or today
    cpj_config["data_final_iso"] = _date_to_iso(cpj_config.get("data_final", "")) or today
    cpj_config["tempo_decorrido"] = _tempo_decorrido(cpj_config.get("iniciado_em", ""))
    try:
        with open(bloqueados_spf_file) as f:
            bloqueados_data = json.loads(f.read())
        cpj_config["bloqueados_spf"] = bloqueados_data.get("bloqueados", [])
    except Exception:
        cpj_config["bloqueados_spf"] = []

    with open(labels_file) as f:
        labels = json.loads(f.read())

    omni_config = _load_omni_config()
    omni_config["data_final_display"] = today
    try:
        prox = datetime.strptime(omni_config["proxima_execucao"], "%Y-%m-%dT%H:%M:%S")
        omni_config["proxima_execucao_fmt"] = prox.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        omni_config["proxima_execucao_fmt"] = None

    pan_config = _load_pan_config()
    pan_config["data_inicial_iso"] = pan_config.get("data_inicial", today)
    pan_config["data_final_iso"] = pan_config.get("data_final", today)
    pan_config["tempo_decorrido"] = _tempo_decorrido(pan_config.get("iniciado_em", ""))

    dash_mode = request.args.get("dash") == "1"
    return render_template("ativacao.html", procs=procs, cpj_config=cpj_config, omni_config=omni_config, pan_config=pan_config, labels=labels, dash_mode=dash_mode)


@bp.route("/ativacao/bloqueados-spf", methods=["POST"])
def adicionar_bloqueado_spf():
    id_spf = request.form.get("id_spf", "").strip()
    if id_spf:
        try:
            with open(bloqueados_spf_file) as f:
                data = json.loads(f.read())
            if id_spf not in data["bloqueados"]:
                data["bloqueados"].append(id_spf)
                with open(bloqueados_spf_file, mode="w") as f:
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            pass
    return redirect(url_for("ativacao.ativacao"))


@bp.route("/ativacao/bloqueados-spf/remover", methods=["POST"])
def remover_bloqueado_spf():
    id_spf = request.form.get("id_spf", "").strip()
    if id_spf:
        try:
            with open(bloqueados_spf_file) as f:
                data = json.loads(f.read())
            if id_spf in data["bloqueados"]:
                data["bloqueados"].remove(id_spf)
                with open(bloqueados_spf_file, mode="w") as f:
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            pass
    return redirect(url_for("ativacao.ativacao"))


def _json_to_excel_bytes(json_path: str) -> io.BytesIO:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf


@bp.route("/ativacao/omni-download/erros")
def omni_download_erros():
    erros_path = str(Path(INITIALIZR_ROOT).parent / "sites/omni-pde-fsp-trc/erros_registro_despesa.json")
    buf = _json_to_excel_bytes(erros_path)
    return send_file(buf, as_attachment=True,
                     download_name="erros_registro_despesa.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.route("/ativacao/omni-download/pastas-sem-contrato")
def omni_download_pastas():
    pastas_path = str(Path(INITIALIZR_ROOT).parent / "sites/omni-pde-fsp-trc/pastas_sem_contrato.json")
    buf = _json_to_excel_bytes(pastas_path)
    return send_file(buf, as_attachment=True,
                     download_name="pastas_sem_contrato.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.route("/ativacao/pan-config", methods=["POST"])
def salvar_pan_config():
    numero_recibo = request.form.get("numero_recibo", "")
    data_inicial = request.form.get("data_inicial", "")
    data_final = request.form.get("data_final", "")

    config_atual = _load_pan_config()

    if numero_recibo and numero_recibo != config_atual.get("numero_recibo", ""):
        iniciado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif not numero_recibo:
        iniciado_em = ""
    else:
        iniciado_em = config_atual.get("iniciado_em", "")

    config_atual.update({
        "numero_recibo": numero_recibo,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "iniciado_em": iniciado_em,
    })
    with open(pan_config_file, mode="w", encoding='utf-8') as f:
        f.write(json.dumps(config_atual, ensure_ascii=False, indent=4))

    return redirect(url_for("ativacao.ativacao"))


@bp.route("/ativacao/omni-executar-agora", methods=["POST"])
def omni_executar_agora():
    try:
        config_atual = _load_omni_config()
        config_atual["proxima_execucao"] = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
        with open(omni_config_file, mode="w", encoding='utf-8') as f:
            f.write(json.dumps(config_atual, ensure_ascii=False, indent=2))
    except Exception:
        pass
    return redirect(url_for("ativacao.ativacao"))


@bp.route("/ativacao/omni-config", methods=["POST"])
def salvar_omni_config():
    data_inicial = request.form.get("data_inicial", "")
    data_final = request.form.get("data_final", "")

    config_atual = _load_omni_config()
    config_atual.update({
        "data_inicial": data_inicial,
        "data_final": data_final,
    })
    with open(omni_config_file, mode="w", encoding='utf-8') as f:
        f.write(json.dumps(config_atual, ensure_ascii=False, indent=2))

    return redirect(url_for("ativacao.ativacao"))


@bp.route("/ativacao/cpj-config", methods=["POST"])
def salvar_cpj_config():
    numero_recibo = request.form.get("numero_recibo", "")
    data_inicial = _date_from_iso(request.form.get("data_inicial", ""))
    data_final = _date_from_iso(request.form.get("data_final", ""))

    config_atual = _load_cpj_config()

    if numero_recibo and numero_recibo != config_atual.get("numero_recibo", ""):
        iniciado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif not numero_recibo:
        iniciado_em = ""
    else:
        iniciado_em = config_atual.get("iniciado_em", "")

    config_atual.update({
        "numero_recibo": numero_recibo,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "iniciado_em": iniciado_em,
    })
    with open(cpj_config_file, mode="w") as f:
        f.write(json.dumps(config_atual, ensure_ascii=False, indent=4))

    return redirect(url_for("ativacao.ativacao"))
