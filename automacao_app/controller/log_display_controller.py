from flask import Blueprint, request, render_template
import datetime as dt
import pygal

from typing import List

from automacao_app import templates, static
from dados.database.RoboLogDataSource import RoboLogDataSource
from dados.database.dao import RoboLogDAO
from initializr import INITIALIZR_ROOT
from pathlib import Path

file = str(Path(f"{INITIALIZR_ROOT}/ativacao.json"))
bp = Blueprint("log", __name__, template_folder=templates)


@bp.route("/log", methods=["GET", "POST"])
def log_display():
    from sites.baseRobos.configs.dados_robos import ID_ROBOS
    logs: List[RoboLogDAO] = []
    if request.method == "POST":
        print("DADOS:", request.form)
        print("DADOS:", request.data)
        log_data_source: RoboLogDataSource = RoboLogDataSource(1)

        logs = log_data_source.consultar_log(limite=10)
        print(logs)

    return render_template("log.html", logs=logs, robos=ID_ROBOS)


@bp.route("/stats")
def stats_display():
    hoje = dt.datetime.now().strftime("%Y/%m/%d")
    subtr_mes = hoje.split("/")

    mes_passado = f"{subtr_mes[0]}/{int(subtr_mes[1]) - 1}/{subtr_mes[2]}"

    erros = RoboLogDataSource(1).consultar_status(0, mes_passado, hoje)
    acertos = RoboLogDataSource(1).consultar_status(2, mes_passado, hoje)
    total = [x for x in map(lambda a, b: a + b, erros, acertos)]

    line_chart = pygal.Line()
    line_chart.title = "Erros vs Acertos"
    line_chart.add("Erros", erros)
    line_chart.add("Acertos", acertos)
    line_chart.add("Total", total)

    bar = pygal.Bar()
    bar.add("Erros", (sum(erros) / len(erros)))
    bar.add("Acertos", (sum(acertos) / len(acertos)))
    bar.add("Total", (sum(total) / len([x for x in total])))

    return render_template("stats.html", hist=line_chart.render_data_uri(), med=bar.render_data_uri())
