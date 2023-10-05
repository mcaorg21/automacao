from sites.elementos import TextInput, CheckBox
from sites.ibConsig.libs.auto.forms.FormDadosEndereço import FormDadosEndereco
from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato
from selenium.webdriver import Chrome


def formDadosEndereco(driver: Chrome, contrato: Contrato, tOut=2) -> FormDadosEndereco:
    return FormDadosEndereco(
        contrato=contrato,
        iptCep=TextInput(driver, '//*[@id="endereco.cep"]', time_out=tOut),
        cBoxSemNumero=CheckBox(driver, '//*[@id="logradouroSemNumeroCheck"]', time_out=tOut),
        iptNumero=TextInput(driver, '//*[@id="endereco.numero"]', time_out=tOut),
        iptLogradouro=TextInput(driver, '//*[@id="endereco.logradouro"]', time_out=tOut),
        iptLogradouro2=TextInput(driver, '//*[@id="endereco.logradouro2"]', time_out=tOut),
        iptBairro=TextInput(driver, '//*[@id="endereco.bairro"]', time_out=tOut),
        iptBairro2=TextInput(driver, '//*[@id="endereco.bairro2"]', time_out=tOut),
        iptComplemento=TextInput(driver, '//*[@id="endereco.complemento"]', time_out=tOut),
        iptDddTel=TextInput(driver, '//*[@id="endereco.telefone.ddd"]', time_out=tOut),
        iptNoTel=TextInput(driver, '//*[@id="endereco.telefone.numero"]', time_out=tOut),
        iptDddCel=TextInput(driver, '//*[@id="endereco.telefoneCelular1.ddd"]', time_out=tOut),
        iptNoCel=TextInput(driver, '//*[@id="endereco.telefoneCelular1.numero"]', time_out=tOut)
    )
