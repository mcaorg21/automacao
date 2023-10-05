def minimo_n_contratos_fila(n: int, nome_banco: str) -> bool:
    from dados.APIGetSource import APIGetSource
    fila_contratos = APIGetSource(nome_banco).fila_contratos_inserir()['contratos']
    print(len(fila_contratos))
    return len(fila_contratos) > n
