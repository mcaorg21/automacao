from sites.elementos import Button, TextInput, Select
from sites.elementos.ContainerElements.TextContainer import TextContainer
from sites.ibConsig.libs.auto.forms.FormIdentificacao import FormIdentificacao

tOut = 2


def formIdentificacao(driver, contrato) -> FormIdentificacao:
    form = FormIdentificacao(
        driver, contrato,
        btnMenuExpandir=Button(driver, '//*[@id="menu_group_2"]', time_out=tOut),
        btnMenuExpandido=Button(driver, '//*[@id="slidingMenu"]/div/div[2]/a[4]', time_out=tOut),
        btnMenuExpandido2=Button(driver, '//*[@id="slidingMenu"]/div/div[2]/a[2]', time_out=tOut),
        inputEntidade=TextInput(driver, '//*[@id="identificacao-form:orgao:find:txt-value"]', time_out=tOut),
        selectServico=Select(driver, '//*[@id="identificacao-form:servico"]', time_out=tOut),
        inputCpf=TextInput(driver, '//*[@id="identificacao-form:cpf"]', time_out=tOut),
        inputMatricula=TextInput(driver, '//*[@id="identificacao-form:matricula"]', time_out=tOut),
        inputDataNascimento=TextInput(driver, '//*[@id="identificacao-form:dataDeNascimento"]', time_out=tOut),
        inputCaptcha=TextInput(driver, '//*[@id="identificacao-form:idCaptcha:txt-value"]', time_out=tOut),
        btnConfirmar=Button(driver, '//*[@id="identificacao-form:idCommandLink"]', time_out=tOut),
        divErro=TextContainer(driver, '//*[@id="global-msg"]/li', time_out=tOut),
        btnPropostaAndamento=Button(
            driver, '//*[@id="identificacao-form:modalDialog"]/div[2]/div[2]/a[1]', time_out=tOut)
    , time_out=tOut)
    return form
