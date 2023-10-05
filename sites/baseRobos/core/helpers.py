import base64
import os
import sys
import glob
from datetime import datetime as dt
from time import sleep
import datetime
import ssl, smtplib


def enviar_email_gmail_uconecte(de: str, para: str, msg: str):
    port = 465
    context = ssl.create_default_context()    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("notifica4@uconecte.me", "marcelo2126")
        server.sendmail(de, para, msg)


def aguardar_n_segundos(segundos: int):
    for i in range(0, segundos+1, 5):
        print(f'\rAguardando {segundos} segundos: {(i/segundos)*100:.2f}% ', end="")
        sleep(5)

def apagar_arquivo(file_path):
    try:
        os.remove(file_path)
        print(f"Arquivo Removido!")
    except FileNotFoundError:
        print("Arquivo não existe")

def apagar_arquivos(dir_path):
    try:
        files = os.listdir(dir_path)
        for file in files:
            os.remove(dir_path + "\\" + file)
            print(f"Arquivo {file} Removido!")
    except FileNotFoundError:
        print("Arquivos não existem")

def deleta_todos_arquivos(path):
    for file in os.listdir(str(path)):
        file_path = os.path.join(str(path), file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

def clear():
    return os.system("cls")


def identificar_erro_robo():
    if "win" in sys.platform:
        os.system("title ERRORROBO")
    else:
        print(f'\33]0;ERRO\a', end='', flush=True)


def definir_nome_robo(nome, nome_proc=None):
    if "win" in sys.platform:
        os.system(f'title Robô - {nome}')
    else:
        print(f'\33]0;{nome}\a', end='', flush=True)


def convert_file_base_64(path):
    file = open(path, 'rb')
    file_base_64 = base64.encodebytes(file.read())
    file.close()
    return file_base_64


def formatar_moeda(texto):
    texto = texto.replace("R$ ", "")
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    return float(texto)

def formatar_moeda2(texto):
    texto = texto.replace(',', '')

def formatar_porcentagem(texto):
    texto = texto.replace("%", "")
    texto = texto.replace(",", ".")
    return float(texto)


def formatar_data_banco(data):
    data = dt.strptime(data, '%m/%Y')
    return dt.strftime(data, '%Y-%m-01')

def formatar_data_banco_anomenor(data):
    data = dt.strptime(data, '%m/%y')
    return dt.strftime(data, '%Y-%m-01')

def formatar_cpf(cpf):
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])


def countdown(segundos, step=1, mensagem=''):
    pad_str = ' ' * len('%d' % step)
    for i in range(segundos, 0, -step):
        print('%s %d segundo(s) %s\r' % (mensagem, i, pad_str))
        sys.stdout.flush()
        sleep(step)


def esta_horario_comercial(hora_limite_manha: int=7, hora_limite_noite: int=19) -> bool:
    hora_atual = dt.now().hour
    mins_atual = dt.now().min

    print("Hora atual:", hora_atual)
    # se domingo
    if datetime.date(dt.now().year, dt.now().month, dt.now().day).weekday() == 6:
        return False

    if hora_limite_manha <= hora_atual < hora_limite_noite:
        print("Dentro do horário comercial.")
        return True

    return False


def verificar_horario_comercial(hora_limite_manha: int=7, hora_limite_noite: int=19) -> bool:
    while True:
        hora_atual = dt.now().hour
        mins_atual = dt.now().min

        print("Hora atual:", hora_atual)
        
        # se domingo
        permitir = True
        if datetime.date(dt.now().year, dt.now().month, dt.now().day).weekday() in [5,6]:
            permitir = False
            print('Final de semana não logar... Só no sábado logar até 18...')          
            if(hora_atual < 19 and datetime.date(dt.now().year, dt.now().month, dt.now().day).weekday() == 5):
                permitir = True

        if hora_limite_manha <= hora_atual < hora_limite_noite and permitir:
            print("Dentro do horário comercial.")
            return True

        print("Fora do horário comercial")
        print("Aguardando 3 minutos")
        sleep(180)

def executar_script_pop_up_deprecated(driver):
    try:
        driver.execute_script("""ChromePopup = function (url, arg, feature) {
                                var opFeature = feature.split(";");
                                var featuresArray = new Array();
                                for (var i = 0; i < opFeature.length - 1; i++) {
                                    var f = opFeature[i].split(":");
                                    featuresArray[f[0].toString().trim().toLowerCase()] = f[1].toString().trim();
                                }

                                var h = "200px", w = "400px", l = "100px",
                                t = "100px", r = "no", c = "yes", s = "no";
                                if (featuresArray["dialogheight"]) h = featuresArray["dialogheight"];
                                if (featuresArray["dialogwidth"]) w = featuresArray["dialogwidth"];
                                if (featuresArray["dialogleft"]) l = featuresArray["dialogleft"];
                                if (featuresArray["dialogtop"]) t = featuresArray["dialogtop"];
                                if (featuresArray["resizable"]) r = featuresArray["resizable"];
                                if (featuresArray["center"]) c = featuresArray["center"];
                                if (featuresArray["status"]) s = featuresArray["status"];
                                var modelFeature = "height = " + h + ",width = " + w + ",left=" + l + ",top=" + t + ",model=yes,alwaysRaised=yes,directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no" + ",resizable= " + r + ",celter=" + c + ",status=" + s;
                                var model = window.open(url, "", modelFeature, null);
                                model.dialogArguments = arg;
                                if (window.showModalDialog.refreshParent) {
                                    reloadPage(model);
                                }
                                return model;
                            }

                            window.showModalDialog = ChromePopup;
                        """)
    except JavascriptException:
        print("Modal Javascript não pôde ser aberto.")

def executar_script_pop_up(driver):
    try:
        driver.execute_script("""ChromePopup = function (url, arg, feature) {
                                var opFeature = feature.split(";");
                                var featuresArray = new Array();
                                for (var i = 0; i < opFeature.length - 1; i++) {
                                    var f = opFeature[i].split(":");
                                    featuresArray[f[0].toString().trim().toLowerCase()] = f[1].toString().trim();
                                }

                                var h = "200px", w = "400px", l = "100px",
                                t = "100px", r = "no", c = "yes", s = "no";
                                if (featuresArray["dialogheight"]) h = featuresArray["dialogheight"];
                                if (featuresArray["dialogwidth"]) w = featuresArray["dialogwidth"];
                                if (featuresArray["dialogleft"]) l = featuresArray["dialogleft"];
                                if (featuresArray["dialogtop"]) t = featuresArray["dialogtop"];
                                if (featuresArray["resizable"]) r = featuresArray["resizable"];
                                if (featuresArray["center"]) c = featuresArray["center"];
                                if (featuresArray["status"]) s = featuresArray["status"];
                                var modelFeature = "height = " + h + ",width = " + w + ",left=" + l + ",top=" + t + ",model=yes,alwaysRaised=yes,directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no" + ",resizable= " + r + ",celter=" + c + ",status=" + s;
                                var model = window.open(url, "", modelFeature);
                                model.dialogArguments = arg;
                                if (window.showModalDialog.refreshParent) {
                                    reloadPage(model);
                                }
                                return model;
                            }

                            window.showModalDialog = ChromePopup;
                        """)
    except JavascriptException:
        print("Modal Javascript não pôde ser aberto.")


def apagar_arquivos_pasta(path):
    files = glob.glob(path)
    for file in files:
        os.remove(file)

def apagar_um_arquivo(file):
    os.remove(file)