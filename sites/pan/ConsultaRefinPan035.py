from sites.pan.pan_consulta_refin.manager.PanConsultaRefin import ConsultaRefin
from sites.pan.configs.pan035 import configs


def main():
    ConsultaRefin.get_standalone_instance(**configs).run()


if __name__ == "__main__":
    main()
