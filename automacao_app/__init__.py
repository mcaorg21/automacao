
from flask import Flask
import os,sys
#sys.path.append('../')
from pathlib import Path

templates = str(Path(os.path.dirname(os.path.abspath(__file__)) + "/static/template/"))
static = str(Path(os.path.dirname(os.path.abspath(__file__)) + "/static/"))


def create_app() -> Flask:
    print(templates)
    app = Flask(__name__, template_folder=templates, static_folder=static)
    app.config['SECRET_KEY'] = os.urandom(10)

    from automacao_app.controller import ativacao
    app.register_blueprint(ativacao.bp)

    from automacao_app.controller.mediadores import mediadores_apis
    app.register_blueprint(mediadores_apis.bp)

    from automacao_app.controller import log_display_controller
    app.register_blueprint(log_display_controller.bp)

    return app


