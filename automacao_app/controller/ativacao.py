from flask import Blueprint, request, render_template,abort
import json,pdb
from automacao_app import templates
from initializr import INITIALIZR_ROOT
from pathlib import Path

file = str(Path(f"{INITIALIZR_ROOT}/ativacao.json"))
bp = Blueprint("ativacao", __name__, template_folder=templates)

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

            with open(file, mode="w") as fObj:
                fObj.write(json.dumps(activate))
                fObj.close()
                print(activate)

    return render_template("ativacao.html", procs=activate)
