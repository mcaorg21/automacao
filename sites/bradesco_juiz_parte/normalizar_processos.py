import re
import openpyxl


PLANILHA = "estoque.xlsx"
COLUNA_PROCESSO = 2  # B = 2 (1-indexed)


def normalizar_cnj(raw: str) -> str | None:
    """
    Converte qualquer representação de número de processo de 20 dígitos
    para o formato CNJ: NNNNNNN-DD.AAAA.J.TT.OOOO
    """
    # Remove tudo que não for dígito
    digits = re.sub(r"\D", "", str(raw).strip())

    if not digits:
        return None

    # Garante 20 dígitos com padding de zeros à esquerda
    if len(digits) > 20:
        return None  # número inválido, mais de 20 dígitos

    digits = digits.zfill(20)

    n = digits[0:7]   # número de ordem
    d = digits[7:9]   # dígito verificador
    a = digits[9:13]  # ano
    j = digits[13]    # segmento da justiça
    t = digits[14:16] # tribunal
    o = digits[16:20] # origem

    return f"{n}-{d}.{a}.{j}.{t}.{o}"


def extrair_processos(caminho: str = PLANILHA) -> list[dict]:
    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    ws = wb.active

    resultados = []
    erros = 0

    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        raw = row[COLUNA_PROCESSO - 1]  # índice 0-based
        if raw is None:
            continue

        cnj = normalizar_cnj(raw)
        if cnj:
            resultados.append({"linha": i, "original": str(raw).strip(), "cnj": cnj})
        else:
            erros += 1
            print(f"  [ERRO] Linha {i}: valor inválido → {raw!r}")

    wb.close()
    return resultados, erros


if __name__ == "__main__":
    print(f"Lendo {PLANILHA}...")
    processos, erros = extrair_processos()

    print(f"\nTotal extraído : {len(processos)}")
    print(f"Erros/ignorados: {erros}")
    print("\n=== Amostra (primeiros 10) ===")
    for p in processos[:10]:
        print(f"  Linha {p['linha']:4d} | {p['original']}  ->  {p['cnj']}")

    print("\n=== Amostra (ultimos 5) ===")
    for p in processos[-5:]:
        print(f"  Linha {p['linha']:4d} | {p['original']}  ->  {p['cnj']}")
