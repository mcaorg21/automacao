from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import ConsultaRefin
""" Ordem inversa Impar """

configs: dict = {
    "login": "06445557694",
    "senha": "Marcelo@38",
    "verificar_sessao": True,
    "ordem_inversa": True,
    "filtro": lambda x: int(x.get("idSolicitacao", x["idPessoa"])) % 2 == 0,
    "min_len": 10
}


def main():
    ConsultaRefin.get_standalone_instance(**configs).run()


if __name__ == "__main__":
    main()
