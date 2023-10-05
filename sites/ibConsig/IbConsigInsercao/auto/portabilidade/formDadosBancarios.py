from selenium.webdriver import Chrome

from sites.elementos import Select, TextInput
from sites.ibConsig.libs.auto.forms.FormDadosBancarios import FormDadosBancarios
from sites.ibConsig.libs.dto.Contrato import Contrato

TO = 2


def formDadosBancarios(driver: Chrome, contrato: Contrato):

    form = FormDadosBancarios(
        contrato=contrato,
        selFormaCredito=Select(driver, '//*[@id="dadosBancarios.formaCredito"]', time_out=TO),
        bancoOp=Select(driver, '//*[@id="dadosBancarios.numeroOrdemPagamento"]', time_out=TO),
        iptCodigoBanco=TextInput(driver, '//*[@id="dadosBancarios.numeroBanco"]', time_out=TO),
        iptNoAgencia=TextInput(driver, '//*[@id="dadosBancarios.agencia"]', time_out=TO),
        iptDvAgencia=TextInput(driver, '//*[@id="dadosBancarios.agenciaDv"]', time_out=TO),
        selContaCredito=Select(driver, '//*[@id="dadosBancarios.finalidadeCredito"]', time_out=TO),
        iptNoConta=TextInput(driver, '//*[@id="dadosBancarios.conta"]', time_out=TO),
        iptDvConta=TextInput(driver, '//*[@id="dadosBancarios.contaDv"]', time_out=TO))
    return form
