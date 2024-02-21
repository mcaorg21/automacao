
def filtrar_bancos_nome(nome_banco: str) -> str:
    bancos = {
        "itau": "itau-consignado",
        "bradesco": "bradesco-promotora",
        "ole": "ole",
        "bmg": "bmg",
        "pan": "pan",
        "novo-saque": "novo-saque",
        "crefisa": "crefisa"

    }
    return bancos.get(nome_banco.lower())


def filtrar_bancos_id(nome_banco: str) -> int:
    bancos = {
        "itau": 1,
        "bradesco": 2,
        "ole": 123,
        "pan": 68,
        "novo-saque": 285,
        "crefisa": 93
    }
    return bancos.get(nome_banco)