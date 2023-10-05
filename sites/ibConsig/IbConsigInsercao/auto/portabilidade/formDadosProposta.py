from sites.elementos import Select, TextInput, Button
from sites.elementos.ContainerElements.TextContainer import TextContainer
from sites.ibConsig.libs.dto.Contrato import Contrato
from sites.ibConsig.libs.auto.forms.FormDadosProposta import FormDadosProposta
from selenium.webdriver import Chrome


def formDadosProposta(contrato: Contrato, driver: Chrome):
    form: FormDadosProposta = FormDadosProposta(
        contrato=contrato, driver=driver,
        selectTabela=Select(driver, '[id="ade.codigoCarencia"]'),
        selectTabelaEspecial=Select(driver, '[id="ade.codigoTabelaEspecial"]'),
        iptValorSolicitado=TextInput(driver, '//*[@id="ade.valorEmprestimo"]'),
        valorPrestacao=TextInput(driver, '//*[@id="ade.valorPrestacao"]'),
        iptNumPrestacoes=TextInput(driver, '//*[@id="ade.quantidadePrestacoes"]'),
        valorLiberadoMaximo=TextContainer(driver, '//*[@id="label_refinanciamento.valorAdicionalComIof"]'),
        btnSimular=Button(driver, '//*[@id="simulacao"]/a'))

    print(form)

    return form
