from sites.elementos import TextInput, Select
from sites.ibConsig.libs.auto.forms.FormDadosIniciais import FormDadosIniciais
from sites.ibConsig.libs.dto.Contrato import Contrato
from selenium.webdriver import Chrome

TO = 2


def formDadosIniciais(contrato: Contrato, driver: Chrome) -> FormDadosIniciais:
    form: FormDadosIniciais = FormDadosIniciais(
        contrato=contrato,
        iptDataNasc=TextInput(driver, '//*[@id="servidor.dataNascimento"]', time_out=TO),
        iptDataFator=TextInput(driver, '//*[@id="ade.dataFator"]', time_out=TO),
        iptCodigoLoja=TextInput(driver, '//*[@id="ade.loja"]', time_out=TO),
        iptDataRenda=TextInput(driver, '//*[@id="registro.dataRenda"]', time_out=TO),
        iptValorRenda=TextInput(driver, '//*[@id="registro.renda"]', time_out=TO),
        selectUFBeneficio=Select(driver, '//*[@id="ade.ufContaBeneficio"]', time_out=TO),
        iptTipoBeneficio=TextInput(driver, '//*[@id="registro.codTipoBeneficio"]', time_out=TO),
        selectGrauInstrucao=Select(driver, '//*[@id="servidor.grauInstrucao"]', time_out=TO))

    return form
