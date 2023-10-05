from sites.elementos import TextInput
from sites.ibConsig.libs.auto.forms.FormPortabilidade import FormPortabilidade

tOut = 2


def formPortabilidade(driver, contrato):
    form = FormPortabilidade(
        contrato=contrato,
        iptSaldoDevedor=TextInput(driver, '//*[@id="portabilidade.saldoDevedor"]', time_out=tOut),
        iptValorParcela=TextInput(driver, '//*[@id="portabilidade.valorParcela"]', time_out=tOut),
        iptQtdParcelas=TextInput(driver, '//*[@id="portabilidade.quantidadeParcela"]', time_out=tOut),
        iptQtdParcelasPagas=TextInput(driver, '//*[@id="portabilidade.quantidadeParcelaPagas"]', time_out=tOut),
        iptNoContrato=TextInput(driver, '//*[@id="trNumeroContratoPortabilidade"]/td[2]/input', time_out=tOut),
        iptUltimoVencimento=TextInput(
            driver, '//*[@id="portabilidade.dataPortabilidadeUltimaParcela"]', time_out=tOut),
        iptPrimeiroVencimento=TextInput(
            driver, '//*[@id="portabilidade.dataPortabilidadePrimeiroVencimento"]', time_out=tOut),
        iptCnpj=TextInput(driver, '//*[@id="portabilidade.numeroCNPJPortabilidade"]', time_out=tOut),
        iptCodigoBanco=TextInput(driver, '//*[@id="portabilidade.codBancoPortabilidade"]', time_out=tOut), time_out=tOut)
    return form
