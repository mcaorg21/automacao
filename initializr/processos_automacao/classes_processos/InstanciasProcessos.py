# Imports de Processos
from typing import Dict

from initializr.processos_automacao.classes_processos import *
from initializr.processos_automacao.config.ProcessWrapper import ProcessWrapper

INSTANCIAS: Dict[str, ProcessWrapper] = {
    #Cora Sincroniza
    'CoraLogin': CoraLogin(),

    # Pan 078
    'rodar_pan078': rodar_pan078(),
    
    # FGTS SAFRA
    'Insercao-Safra2': Safra_Insercao_2(),
    'Insercao-Safra': Safra_Insercao(),
    'Fgts_Safra': Fgts_Safra(),
    # Daycoval
    #'Proposta_Daycoval': Proposta_Daycoval(),
    #'Daycoval_Simulacao': Daycoval_Simulacao(),
    # Clone robos refin
    'Ole_Insercao_Gerar_Contrato_Nova_Loja': Ole_Insercao_Gerar_Contrato_Nova_Loja(),

    'Ole_Refin_Anex_Sms_Nova_Loja': Ole_Refin_Anex_Sms_Nova_Loja(),

    #"OleConsigInssCem":OleConsigInssCem(),
    
    # Receita Federal
    'consulta_receita_federal': Consulta_CPF_Receita(),
    # Tse
    'consulta_de_cpfs': ConsultaCPFJusticaFederal(),
    # Pan
    #'pan_tarefas': TarefasPan(),
    #'pan_refin064': PanConsultaRefin064(),
    #'pan_refin035': PanConsultaRefin035(),

    # MeuINSS
    'meu_inss': ConsultaDadosMeuINSS(),

    # PortalConsig
    'portal_consig_sp': PortalConsigSP(),

    # Itau
    'Extrair_Tags_ICcdigital': Extrair_Tags_ICcdigital(),
    'Itau_Sincronizacao_ICdigital': Itau_Sincronizacao_ICdigital(),
    'itau_gerar_contrato': ItauGerarContrato(),
    'itau_insercao': ItauInsercao(),
    'itau_refin_n2': ItauConsultaRefinN2(),
    'itau_insercao_mca': ItauInsercaoMca(),
    'itau_insercao_carol': ItauInsercaoCarolina(),
    'itau_refin': ItauConsultaRefin(),
    'itau_consulta_status': ItauConsultaStatus(),
    #'Itau_Anexa_Doc_Ajusta_Restricao_Margem': Itau_Anexa_Doc_Ajusta_Restricao_Margem(),

    # BMG
    'bmg': BMG(),

    # Bradesco
    'bradesco_sinc_refin': BradescoSincRefin(),

    # GoogleAnalytics
    'google_analytics': GoogleAnalytics(),
    # Marinha
    #'consulta_margem_marinnha': ConsultaMargemMarinha(),

    # Ole
    #'Ole_Portal_Orienta': Ole_Portal_Orienta(),
    #'ole_refin_anex_lib_sms': OleRefinAnexLibSMS.run_with_cli_args("-L=MARCELOCALEWE"),
    #'ole_sinc_insercao': OleSincInsercao(),
    'ole_consulta_refin': OleConsultaRefin(),
    'promobank': Promobank(),
    #'rodar_flask': Rodar_Flask(),

    #Novo Saque
    'NovoSaque': NovoSaque(),

    #Cora Sincroniza
    'Cora': Cora()

}

