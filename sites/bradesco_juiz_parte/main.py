# -*- coding: utf-8 -*-
import sys
import os
import re
import json
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import shutil
import tempfile
import subprocess
import requests
import openpyxl
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from normalizar_processos import extrair_processos, normalizar_cnj, PLANILHA

DIR          = os.path.dirname(os.path.abspath(__file__))
URL_BASE     = "https://www.jusbrasil.com.br"
URL_CONSULTA = "https://www.jusbrasil.com.br/consulta-processual/"
COOKIES_FILES = [
    os.path.join(DIR, f"cookies_jusbrasil_conta_{i}.json") for i in range(1, 11)
]
# inclui os arquivos que existirem no disco
COOKIES_FILES = [f for f in COOKIES_FILES if os.path.exists(f)]
# fallback: arquivo original se nenhuma conta numerada existir
if not COOKIES_FILES:
    COOKIES_FILES = [os.path.join(DIR, "cookies_jusbrasil.json")]
RESULTADO_FILE = os.path.join(DIR, "resultados.json")
WEBHOOK_URL  = "https://n8n-diascosta.up.railway.app/webhook/dados-fc3149c1-ad4f-4572-a1ea-9d8d548d18e3-capa"

XPATH_CAMPO_BUSCA = (
    "/html/body/div[1]/main/section[1]/div/div[2]/div/form"
    "/div/div/div[1]/span/input"
)

LIMITE_TESTE    = 3050
API_2CAPTCHA    = "8154898064787da1d36d5c7062417bde"
XPATH_CF_IFRAME = "//iframe[@title='Widget contendo um desafio de segurança da Cloudflare']"

RESULTADO_ASC  = os.path.join(DIR, "resultados_asc.json")
RESULTADO_ASC2 = os.path.join(DIR, "resultados_asc2.json")
RESULTADO_DESC2= os.path.join(DIR, "resultados_desc2.json")
RESULTADO_DESC = os.path.join(DIR, "resultados_desc.json")
DONE_ASC       = os.path.join(DIR, "asc.done")
DONE_ASC2      = os.path.join(DIR, "asc2.done")
DONE_DESC2     = os.path.join(DIR, "desc2.done")
DONE_DESC      = os.path.join(DIR, "desc.done")

_MODO_CFG = {
    "asc":   {"resultado": RESULTADO_ASC,  "done": DONE_ASC,  "direcao": "asc",  "start_pct": 0},
    "asc2":  {"resultado": RESULTADO_ASC2, "done": DONE_ASC2, "direcao": "asc",  "start_pct": 25},
    "desc2": {"resultado": RESULTADO_DESC2,"done": DONE_DESC2,"direcao": "desc", "start_pct": 25},
    "desc":  {"resultado": RESULTADO_DESC, "done": DONE_DESC, "direcao": "desc", "start_pct": 0},
}
ALL_RESULTADOS = [RESULTADO_ASC, RESULTADO_ASC2, RESULTADO_DESC2, RESULTADO_DESC]
ALL_DONES      = [DONE_ASC, DONE_ASC2, DONE_DESC2, DONE_DESC]

_CAMPOS_IGNORADOS_F1 = {"hostOnly", "session", "storeId", "id", "sameSite"}
_SAME_SITE_MAP_F1 = {
    "no_restriction": "None",
    "lax":            "Lax",
    "strict":         "Strict",
    "unspecified":    None,
}
_CAMPOS_IGNORADOS_F2 = {"partitioned", "hostOnly", "session", "storeId", "id", "sameSite"}
_SAME_SITE_MAP_F2 = {
    "no_restriction": "None",
    "lax":            "Lax",
    "strict":         "Strict",
    "none":           "None",
    "unspecified":    None,
}


_INTERCEPT_SCRIPT = """
const i = setInterval(() => {
    if (window.turnstile) {
        clearInterval(i);
        window.turnstile.render = (a, b) => {
            window._cf_params = {
                type:       "TurnstileTaskProxyless",
                websiteKey: b.sitekey,
                websiteURL: window.location.href,
                data:       b.cData,
                pagedata:   b.chlPageData,
                action:     b.action,
                userAgent:  navigator.userAgent
            };
            window.tsCallback = b.callback;
            return 'foo';
        };
    }
}, 10);
"""


def clicar_vamos_la(driver) -> bool:
    for m in range(10, 51):
        try:
            btn_vamos = driver.find_element(By.XPATH, f"/html/body/div[{m}]/div[2]/div/div[2]/div/button")
            if "vamos" in btn_vamos.text.lower():
                print(f"  [VAMOS LA] encontrado em div[{m}], clicando...")
                driver.execute_script("arguments[0].click();", btn_vamos)
                time.sleep(2)
                return True
        except Exception:
            continue
    return False


def clicar_agora_nao(driver) -> bool:
    for n in range(10, 51):
        try:
            btn = driver.find_element(By.XPATH, f"/html/body/div[{n}]/div[2]/div/form/div[3]/div/button[2]")
            if "agora" in btn.text.lower():
                print(f"  [AGORA NAO] encontrado em div[{n}], clicando...")
                btn.click()
                time.sleep(2)
                import pdb; pdb.set_trace()
                clicar_vamos_la(driver)
                return True
        except Exception:
            continue
    return False


def resolver_turnstile(driver: uc.Chrome) -> bool:
    # Injeta interceptor antes do carregamento da pagina
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                               {"source": _INTERCEPT_SCRIPT})
    except Exception as e:
        print(f"  [2CAPTCHA] erro ao injetar CDP: {e}")
        return False

    # Recarrega para o interceptor capturar o turnstile.render
    driver.refresh()

    # Aguarda captura dos params (max 10s)
    params = None
    for _ in range(20):
        time.sleep(0.5)
        params = driver.execute_script("return window._cf_params || null;")
        if params:
            break

    if not params:
        print("  [2CAPTCHA] turnstile.render nao capturado apos refresh")
        return False

    sitekey    = params.get("websiteKey")
    user_agent = params.get("userAgent", "")
    print(f"  [2CAPTCHA] params capturados | sitekey={sitekey} | action={params.get('action')}")

    if not sitekey:
        print("  [2CAPTCHA] sitekey nao encontrado nos params")
        return False

    task = {
        "type":       "TurnstileTaskProxyless",
        "websiteURL": params.get("websiteURL"),
        "websiteKey": sitekey,
    }
    if params.get("action"):
        task["action"] = params["action"]
    if params.get("data"):
        task["data"] = params["data"]
    if params.get("pagedata"):
        task["pagedata"] = params["pagedata"]
    if user_agent:
        task["userAgent"] = user_agent

    # Cria task na 2captcha
    try:
        r = requests.post("https://api.2captcha.com/createTask",
                          json={"clientKey": API_2CAPTCHA, "task": task},
                          timeout=30)
        data = r.json()
    except Exception as e:
        print(f"  [2CAPTCHA] erro ao criar task: {e}")
        return False

    if data.get("errorId") != 0:
        print(f"  [2CAPTCHA] erro API: {data}")
        return False

    task_id = data["taskId"]
    print(f"  [2CAPTCHA] task {task_id} criada, aguardando resolucao...")

    # Polling (max 150s)
    for _ in range(30):
        time.sleep(5)
        try:
            r = requests.post("https://api.2captcha.com/getTaskResult",
                              json={"clientKey": API_2CAPTCHA, "taskId": task_id},
                              timeout=30)
            data = r.json()
        except Exception:
            continue

        if data.get("status") == "ready":
            token = data["solution"]["token"]
            print(f"  [2CAPTCHA] token recebido, chamando tsCallback...")
            driver.execute_script("window.tsCallback(arguments[0]);", token)
            time.sleep(3)
            clicar_agora_nao(driver)
            return True

        if data.get("errorId") != 0:
            print(f"  [2CAPTCHA] erro na resolucao: {data}")
            return False

    print("  [2CAPTCHA] timeout aguardando solucao")
    return False


def _converter_cookie(raw: dict) -> dict:
    cookie = {}

    if "expirationDate" in raw:
        # Formato 1: EditThisCookie
        for k, v in raw.items():
            if k in _CAMPOS_IGNORADOS_F1:
                continue
            if k == "expirationDate":
                cookie["expiry"] = int(v)
            else:
                cookie[k] = v
        ss = _SAME_SITE_MAP_F1.get(raw.get("sameSite", "unspecified"))
        if ss:
            cookie["sameSite"] = ss
    else:
        # Formato 2: Cookie-Editor (expires em milissegundos, sameSite padrao)
        # ignora cookies sem dominio valido
        domain = raw.get("domain")
        if not domain:
            return {}
        cookie["domain"] = domain if domain.startswith(".") else "." + domain

        for k, v in raw.items():
            if k in _CAMPOS_IGNORADOS_F2 or k == "domain":
                continue
            if k == "expires":
                if v:
                    cookie["expiry"] = int(float(v) / 1000)
            else:
                cookie[k] = v

        ss = _SAME_SITE_MAP_F2.get(raw.get("sameSite", "").lower())
        if ss:
            cookie["sameSite"] = ss
        else:
            cookie.pop("sameSite", None)

    return cookie


def carregar_cookies(driver: uc.Chrome, path: str) -> int:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Corrige \\" → \" gerado por algumas extensoes de exportacao de cookies
    content = content.replace('\\\\"', '\\"')
    cookies_raw = json.loads(content)
    injetados = 0
    for raw in cookies_raw:
        convertido = {}
        try:
            convertido = _converter_cookie(raw)
            if not convertido:
                continue
            driver.add_cookie(convertido)
            injetados += 1
        except Exception as e:
            msg = f"[COOKIE ERRO] {raw.get('name')} | convertido: {convertido} | erro: {e}\n"
            print(msg, end="")
            log_path = os.path.join(DIR, "cookie_erros.log")
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(msg)
    return injetados


def reiniciar_com_watchdog(driver: uc.Chrome, profile_dir: str, modo: str = "asc", conta_idx: int = 0):
    print("  [WATCHDOG] Encerrando driver...")
    destruir_driver(driver, profile_dir)

    import random
    nova_conta = random.choice([i for i in range(len(COOKIES_FILES)) if i != conta_idx] or [conta_idx])
    script = (
        f"import time, subprocess; "
        f"print('Watchdog: aguardando 60s para reiniciar...'); "
        f"time.sleep(60); "
        f"print('Watchdog: reiniciando main.py...'); "
        f"subprocess.Popen([r'{sys.executable}', r'{os.path.abspath(__file__)}', '--modo', '{modo}', '--conta', '{nova_conta}'])"
    )
    subprocess.Popen(
        [sys.executable, "-c", script],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print("  [WATCHDOG] Watchdog ativo. Encerrando processo atual em 10s...")
    time.sleep(10)
    sys.exit(0)


def criar_driver() -> tuple[uc.Chrome, str]:
    profile_dir = tempfile.mkdtemp(prefix="jb_chrome_")
    opts = uc.ChromeOptions()
    opts.add_argument("--window-size=1000,680")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    driver = uc.Chrome(options=opts, use_subprocess=True)
    return driver, profile_dir


def _carregar_json(path: str) -> list:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def destruir_driver(driver: uc.Chrome, profile_dir: str):
    try:
        driver.delete_all_cookies()
    except Exception:
        pass
    try:
        driver.quit()
    except Exception:
        pass
    time.sleep(1)
    try:
        shutil.rmtree(profile_dir, ignore_errors=True)
        print(f"  Perfil removido: {profile_dir}")
    except Exception as e:
        print(f"  [AVISO] nao removeu perfil: {e}")


def pesquisar_processo(driver: uc.Chrome, numero_cnj: str, timeout: int = 15) -> bool:
    try:
        driver.get(URL_CONSULTA)
        campo = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, XPATH_CAMPO_BUSCA))
        )
        campo.clear()
        campo.send_keys(numero_cnj)
        campo.send_keys(Keys.RETURN)
        return True
    except TimeoutException:
        print(f"  [TIMEOUT] Campo de busca nao encontrado: {numero_cnj}")
        return False
    except Exception as e:
        print(f"  [ERRO] {numero_cnj}: {e}")
        return False


def salvar_resultado(resultados: list, path: str = RESULTADO_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)


def iniciar_driver(conta_idx: int = 0) -> tuple[uc.Chrome, str]:
    cookies_file = COOKIES_FILES[conta_idx % len(COOKIES_FILES)]
    driver, profile_dir = criar_driver()
    print(f"Abrindo jusbrasil.com.br para injetar cookies ({os.path.basename(cookies_file)})...")
    driver.get(URL_BASE)
    time.sleep(2)
    injetados = carregar_cookies(driver, cookies_file)
    print(f"Cookies injetados: {injetados}\n")
    print("Navegando para /consulta-processual/ ...")
    driver.get(URL_CONSULTA)
    time.sleep(2)
    return driver, profile_dir


def trocar_conta(driver: uc.Chrome, conta_idx: int) -> int:
    """Troca para uma conta aleatoria diferente da atual sem reiniciar o driver."""
    import random
    opcoes = [i for i in range(len(COOKIES_FILES)) if i != conta_idx]
    proximo = random.choice(opcoes) if opcoes else conta_idx
    cookies_file = COOKIES_FILES[proximo]
    print(f"  [CONTA] Trocando para conta {proximo}: {os.path.basename(cookies_file)}")
    driver.delete_all_cookies()
    driver.get(URL_BASE)
    time.sleep(2)
    carregar_cookies(driver, cookies_file)
    driver.get(URL_CONSULTA)
    time.sleep(2)
    return proximo


def atualizar_planilha_estoque(caminho: str = PLANILHA):
    print("Atualizando estoque.xlsx com os resultados (colunas Y e Z)...")
    resultados = _carregar_json(RESULTADO_FILE)

    por_cnj = {}
    for r in resultados:
        cnj_norm = normalizar_cnj(r["cnj"])
        if cnj_norm:
            por_cnj[re.sub(r"\D", "", cnj_norm)] = (r["col_Y"], r["col_Z"])

    wb = openpyxl.load_workbook(caminho)
    ws = wb.active

    atualizados = 0
    for row in ws.iter_rows(min_row=2):
        raw = row[1].value  # coluna B
        if raw is None:
            continue
        cnj_norm = normalizar_cnj(raw)
        if not cnj_norm:
            continue
        digits = re.sub(r"\D", "", cnj_norm)
        if digits in por_cnj:
            col_y, col_z = por_cnj[digits]
            row[24].value = col_y  # coluna Y
            row[25].value = col_z  # coluna Z
            atualizados += 1

    wb.save(caminho)
    print(f"Estoque atualizado: {atualizados} linhas preenchidas em Y/Z.")


def finalizar_instancia(modo: str, driver: uc.Chrome, profile_dir: str):
    done_proprio = _MODO_CFG[modo]["done"]
    open(done_proprio, "w").close()
    print(f"  [{modo.upper()}] marcado como concluido.")

    destruir_driver(driver, profile_dir)

    if all(os.path.exists(d) for d in ALL_DONES):
        print("\nTodas as 4 instancias concluidas — iniciando merge...")
        vistos = {}
        for f in ALL_RESULTADOS:
            for r in _carregar_json(f):
                if r["cnj"] not in vistos:
                    vistos[r["cnj"]] = r
        merged = sorted(vistos.values(), key=lambda x: x["linha"])
        salvar_resultado(merged, RESULTADO_FILE)
        print(f"Merge concluido: {len(merged)} registros salvos em resultados.json")
        for d in ALL_DONES:
            try:
                os.remove(d)
            except Exception:
                pass
        atualizar_planilha_estoque()
    else:
        pendentes = [d for d in ALL_DONES if not os.path.exists(d)]
        print(f"  Aguardando {len(pendentes)} instancia(s) para fazer o merge.")

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["asc", "asc2", "desc2", "desc"], default=None,
                        help="asc/asc2: crescente | desc2/desc: decrescente | (omitir: lanca os 4)")
    parser.add_argument("--conta", type=int, default=0,
                        help="indice do arquivo de cookies a usar (0-based)")
    args = parser.parse_args()

    # Sem --modo: lanca as 4 instancias com cookies randomizados
    if args.modo is None:
        import random
        script  = os.path.abspath(__file__)
        indices = random.sample(range(len(COOKIES_FILES)), min(4, len(COOKIES_FILES)))
        # completa com indices aleatorios se tiver menos de 4 arquivos
        while len(indices) < 4:
            indices.append(random.randrange(len(COOKIES_FILES)))
        for m, conta in zip(["asc", "asc2", "desc2", "desc"], indices):
            print(f"Lancando instancia {m.upper()} com conta {conta} ({os.path.basename(COOKIES_FILES[conta])})...")
            subprocess.Popen(
                ["cmd", "/c", f"title JusBrasil-{m.upper()} && {sys.executable} {script} --modo {m} --conta {conta}"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            print("Aguardando 15s para evitar colisao no chromedriver...")
            time.sleep(15)
        return

    modo      = args.modo
    conta_idx = args.conta
    cfg       = _MODO_CFG[modo]

    resultado_file  = cfg["resultado"]
    outros_arquivos = [f for f in ALL_RESULTADOS if f != resultado_file]

    print(f"Modo: {modo.upper()} | conta: {conta_idx} ({os.path.basename(COOKIES_FILES[conta_idx % len(COOKIES_FILES)])}) | arquivo: {os.path.basename(resultado_file)}")

    print("Lendo processos da planilha...")
    processos, erros = extrair_processos()
    # Aplica direcao e start_pct
    if cfg["direcao"] == "desc":
        processos = list(reversed(processos))
    start = len(processos) * cfg["start_pct"] // 100
    processos = processos[start:]
    total = len(processos)
    print(f"Processando {total} registros a partir de {cfg['start_pct']}% | Erros leitura: {erros}")
    print(f"Primeiros CNJs desta instancia: {[p['cnj'] for p in processos[:3]]}")
    print(f"Ultimos  CNJs desta instancia: {[p['cnj'] for p in processos[-3:]]}\n")

    XPATH_BTN_DETALHES = "/html/body/div[1]/div[3]/div/main/section[1]/div[2]/div/div/div[2]/button"
    XPATH_MODAL_BTN    = "(//body/div)[last()]/div[2]/button"
    driver, profile_dir = iniciar_driver(conta_idx)

    while True:  # loop de restart apos Cloudflare
        # Recarrega resultados proprios + todos os outros para evitar repeticao
        resultados = _carregar_json(resultado_file)
        ja_processados = {r["cnj"] for r in resultados if r["col_Y"] not in ("erro",)}
        for f in outros_arquivos:
            ja_processados |= {r["cnj"] for r in _carregar_json(f) if r["col_Y"] not in ("erro",)}
        print(f"Retomando: {len(resultados)} proprios | {len(ja_processados)} total ja processados\n")

        reiniciar = False

        # Conjunto dos outros para detectar ponto de encontro
        ja_processados_outro = set()
        for f in outros_arquivos:
            ja_processados_outro |= {r["cnj"] for r in _carregar_json(f) if r["col_Y"] not in ("erro",)}

        for i, p in enumerate(processos, 1):
            cnj   = p["cnj"]
            linha = p["linha"]

            # Atualiza conjunto dos outros a cada 50 iteracoes
            if i % 50 == 0:
                ja_processados_outro = set()
                for f in outros_arquivos:
                    ja_processados_outro |= {r["cnj"] for r in _carregar_json(f) if r["col_Y"] not in ("erro",)}

            # Ponto de encontro: outra instancia ja processou este CNJ
            if cnj in ja_processados_outro:
                print(f"\n[PONTO DE ENCONTRO] {cnj} ja processado por outra instancia. Encerrando {modo.upper()}.")
                finalizar_instancia(modo, driver, profile_dir)

            if cnj in ja_processados:
                print(f"[{i:3d}/{total}] Linha {linha} | {cnj}  ja processado, pulando")
                continue

            print(f"[{i:3d}/{total}] Linha {linha} | {cnj}", end="  ", flush=True)

            ok = pesquisar_processo(driver, cnj)
            if not ok:
                registro = {"linha": linha, "cnj": cnj, "col_Y": "invalido", "col_Z": "invalido"}
                resultados.append(registro)
                salvar_resultado(resultados, resultado_file)
                print("ERRO navegacao")
                continue

            time.sleep(2)

            # Verifica numero invalido
            try:
                el = driver.find_element(By.XPATH, "/html/body/div[1]/main/section[1]/div/div[2]/div/form/div/p")
                if "Número inválido" in el.text:
                    registro = {"linha": linha, "cnj": cnj, "col_Y": "invalido", "col_Z": "invalido"}
                    resultados.append(registro)
                    salvar_resultado(resultados, resultado_file)
                    print("numero invalido")
                    continue
            except Exception:
                pass

            # Clica no botao de detalhes
            try:
                btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATH_BTN_DETALHES))
                )
                btn.click()
            except Exception as e:
                if "Sua conta excedeu o limite de uso" in driver.page_source:
                    print(f"  [LIMITE DE USO] conta {conta_idx} excedeu limite - trocando conta...")
                    conta_idx = trocar_conta(driver, conta_idx)
                    continue
                time.sleep(10)
                if "Volte mais tarde" in driver.page_source:
                    print(f"  [VOLTE MAIS TARDE] registro bloqueado, pulando...")
                    registro = {"linha": linha, "cnj": cnj, "col_Y": "bloqueado", "col_Z": "bloqueado"}
                    resultados.append(registro)
                    salvar_resultado(resultados, resultado_file)
                    driver.get(URL_CONSULTA)
                    time.sleep(2)
                    continue
                print(f"  [ERRO clique botao] {e} - verificando 'Agora nao' / 'Vamos la'...")
                clicar_vamos_la(driver)
                if clicar_agora_nao(driver):
                    continue
                clicar_vamos_la(driver)
                print(f"  [ERRO clique botao] tentando 2captcha...")
                resolvido = resolver_turnstile(driver)
                if resolvido:
                    clicar_vamos_la(driver)
                    if clicar_agora_nao(driver):
                        continue
                    clicar_vamos_la(driver)
                    if "Sua conta excedeu o limite de uso" in driver.page_source:
                        print(f"  [LIMITE DE USO] pos-captcha conta {conta_idx} excedeu limite - trocando conta...")
                        conta_idx = trocar_conta(driver, conta_idx)
                        continue
                    try:
                        # try:
                        btn = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, XPATH_BTN_DETALHES))
                        )
                        # except:
                        #     btn = WebDriverWait(driver, 15).until(
                        #         EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/main/section[1]/div[2]/div/div/div[2]/div[2]/button'))
                        #     )

                        driver.execute_script("arguments[0].click();", btn)
                    except Exception as e2:
                        if "Sua conta excedeu o limite de uso" in driver.page_source:
                            print(f"  [LIMITE DE USO] pos-captcha conta {conta_idx} excedeu limite - trocando conta...")
                            conta_idx = trocar_conta(driver, conta_idx)
                            continue
                        print(f"  [ERRO clique pos-captcha] {e2} - pdb...")
                        import pdb; pdb.set_trace()
                else:
                    print("  [2CAPTCHA] falhou - voltando para consulta e continuando...")
                    driver.get(URL_CONSULTA)
                    time.sleep(3)
                    continue

            # Aguarda modal
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, XPATH_MODAL_BTN))
                )
            except Exception as e:
                print(f"  [ERRO aguardar modal] {e}")
                driver.get(URL_CONSULTA)
                time.sleep(2)
                continue

            time.sleep(5)

            texto_modal = ""
            for tentativa in range(3):
                for n in range(10, 61):
                    xpath = f"/html/body/div[{n}]"
                    try:
                        texto = driver.find_element(By.XPATH, xpath).text.strip()
                        if texto and ("Valor da causa" in texto or "Assunto" in texto or "Envolvidos" in texto):
                            texto_modal = texto
                            print(f"  [MODAL] encontrado em div[{n}] (tentativa {tentativa+1})")
                            break
                    except Exception:
                        continue
                if texto_modal:
                    break
                print(f"  [MODAL] tentativa {tentativa+1} sem resultado, aguardando 3s...")
                time.sleep(3)

            if not texto_modal:
                bloqueado = False
                try:
                    btn_fechar = driver.find_element(By.XPATH, "/html/body/div[12]/div[2]/div[2]/div/button[1]")
                    if "fechar" in btn_fechar.text.lower():
                        bloqueado = True
                except Exception:
                    pass

                if bloqueado:
                    registro = {"linha": linha, "cnj": cnj, "col_Y": "bloqueado", "col_Z": "bloqueado"}
                    resultados.append(registro)
                    salvar_resultado(resultados, resultado_file)
                    print("bloqueado")
                    try:
                        btn_fechar.click()
                        time.sleep(1)
                    except Exception:
                        pass
                    driver.get(URL_CONSULTA)
                    time.sleep(2)
                    continue
                else:
                    print(f"  [TEXTO VAZIO] nenhum div[10..60] com conteudo valido")
                    import pdb; pdb.set_trace()

            try:
                resp  = requests.post(WEBHOOK_URL, json={"processo": cnj, "texto": texto_modal}, timeout=180)
                dados = resp.json()
            except Exception as e:
                
                try:
                    resp  = requests.post(WEBHOOK_URL, json={"processo": cnj, "texto": texto_modal}, timeout=600)
                    dados = resp.json()
                except Exception as e:

                    print(f"  [ERRO webhook] {e}")
                    import pdb; pdb.set_trace()
                    driver.get(URL_CONSULTA)
                    time.sleep(2)
                    continue

            nomes_juiz      = dados.get("nomes_juiz", "")
            nomes_advogados = dados.get("nomes_advogados", "")

            registro = {
                "linha": linha,
                "cnj":   cnj,
                "col_Y": nomes_juiz,
                "col_Z": nomes_advogados,
            }
            resultados.append(registro)
            salvar_resultado(resultados, resultado_file)

            print(f"OK | juiz: {nomes_juiz[:40]} | adv: {nomes_advogados[:40]}")

            # Fecha modal e volta para a busca
            try:
                driver.find_element(By.XPATH, XPATH_MODAL_BTN).click()
                time.sleep(1)
            except Exception:
                pass
            driver.get(URL_CONSULTA)
            time.sleep(2)

        if reiniciar:
            print("Driver reiniciado, retomando...\n")
            continue

        break

    print(f"\n=== Concluido === {len(resultados)} registros salvos em {os.path.basename(resultado_file)}")
    finalizar_instancia(modo, driver, profile_dir)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        log_path = os.path.join(DIR, "crash.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print(f"CRASH: {e}\nDetalhes em crash.log")
        input("Pressione ENTER para fechar...")

