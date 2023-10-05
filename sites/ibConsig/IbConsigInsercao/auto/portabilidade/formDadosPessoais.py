from sites.elementos import TextInput, Select
from sites.ibConsig.libs.auto.forms.FormsDadosPessoais import FormDadosPessoais
from sites.ibConsig.libs.dto.Contrato.Contrato import Contrato
from selenium.webdriver import Chrome


def formDadosPessoais(driver: Chrome, contrato: Contrato, tOut=1) -> FormDadosPessoais:
    return FormDadosPessoais(
        contrato=contrato,
        iptNome=TextInput(driver, '//*[@id="servidor.nome"]', time_out=tOut),
        selSexo=Select(driver, '//*[@id="servidor.sexo"]', time_out=tOut),
        selEstadoCivil=Select(driver, '//*[@id="servidor.estadoCivil"]', time_out=tOut),
        iptNomeConjuge=TextInput(driver, '//*[@id="servidor.nomeConjuge"]', time_out=tOut),
        iptNomeMae=TextInput(driver, '//*[@id="servidor.nomeMae"]', time_out=tOut),
        iptNomePai=TextInput(driver, '//*[@id="servidor.nomePai"]', time_out=tOut),
        iptCidadeNascimento=TextInput(driver, '//*[@id="servidor.cidadeNascimento"]', time_out=tOut),
        selUFNascimento=Select(driver, '//*[@id="servidor.ufNascimento"]', time_out=tOut),
        selNacionalidade=Select(driver, '//*[@id="servidor.nacionalidade"]', time_out=tOut),
        selTipoIdentidade=Select(driver, '//*[@id="servidor.identidade.tipo"]', time_out=tOut),
        iptNoIdentidade=TextInput(driver, '//*[@id="servidor.identidade.numero"]', time_out=tOut),
        selOrgaoEmissor=Select(driver, '//*[@id="servidor.identidade.emissor"]', time_out=tOut),
        selUFIdentidade=Select(driver, '//*[@id="servidor.identidade.uf"]', time_out=tOut),
        iptDataEmissao=TextInput(driver, '//*[@id="servidor.identidade.dataEmissao"]', time_out=tOut)
    )

