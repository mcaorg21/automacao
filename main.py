from os import system
from PyInquirer import prompt, Separator
import click,sys,pdb

def robo_cora_login():
    from sites.cora.login import IniciarLogin
    system("title Robô - Cora Logins")
    run = IniciarLogin()
    run.login()

def robo_cora_sincronizacao():
    from sites.cora.main import IniciarEmissaoConsulta
    system("title Robô - Cora Sincronizacao")
    run = IniciarEmissaoConsulta()
    run.sincronizacao()

def robo_crefisa_analise_contrato():
    from sites.crefisa.main_analise import Main
    system("title Robô - Crefisa Analise Contrato")
    run = Main()
    run.main()

def robo_crefisa():
    from sites.crefisa.main import Main
    system("title Robô - Crefisa Insercao")
    run = Main()
    run.main()

def robo_crefisa_sincronizacao():
    from sites.crefisa.main_sincronizacao import Main
    system("title Robô - Crefisa Sincronizacao")
    run = Main()
    run.main()
    
def robo_phtech():
    from sites.phtech.main import Main
    system("title Robô - Phtech Insercao")
    run = Main()
    run.main()

def robo_phtech_sincronizacao():
    from sites.phtech.main_sincronizacao import Main
    system("title Robô - Phtech Sincronizacao")
    run = Main()
    run.main()
    
def robo_facta_sincronizacao():
    from sites.facta.main_sincronizacao import Main
    system("title Robô - Facta Sincronizacao")
    run = Main()
    run.main()
    
def robo_facta_analise_contrato():
    from sites.facta.main_analise import Main
    system("title Robô - Facta Analise Contrato")
    run = Main()
    run.main()

def robo_facta():
    from sites.facta.main import Main
    system("title Robô - Facta Insercao")
    run = Main()
    run.main()
    
def robo_euro():
    from sites.euro17.main import Main
    system("title Robô - Euro Insercao")
    run = Main()
    run.main()
    
def robo_euro_sincronizacao():
    from sites.euro17.main_sincronizacao import Main
    system("title Robô - Euro Sincronizacao")
    run = Main()
    run.main()
    
def robo_euro_analise_contrato():
    
    import threading
    from sites.euro17.main_analise import Main
    
    teste_fila = input('Qual modo deseja? 1- Modo unico 2- Modo Server')
    
    threads = []

    if teste_fila == '1':
        
        final_contrato = input("Digite o número do contrato final: \n\n")

        for i in range(1):
            try:
                t = threading.Thread(target=Main(final_contrato).main)
                t.start()
                threads.append(t)
            except Exception as e:
                print(f"Erro ao iniciar thread {final_contrato}: {e}")
                pass
    
    else:

        threads = []

        range_opcao = input(
            'Qual range deseja? \n'
            'a - para 0 até 1 \n'
            'b - para 1 até 2 \n'
            'c - para 2 até 3\n\n'
            'd - para todos\n\n'
        )

        if range_opcao == 'a':
            intervalo = range(0, 1)
        elif range_opcao == 'b':
            intervalo = range(1, 2)
        elif range_opcao == 'c':
            intervalo = range(2, 3)
        else:
            intervalo = range(0, 10)

        for i in intervalo:
            try:
                t = threading.Thread(target=Main(i).main)
                t.start()
                threads.append(t)
            except Exception as e:
                print(f"Erro ao iniciar thread {i}: {e}")
                pass

        
        
    
    for t in threads:
        t.join()

    # system("title Robô - Euro Analise Contrato")
    # run = Main()
    # run.main()
    
# def robo_euro_sincronizacao_ajuda():
#     from sites.euro17.main_analise import Main
#     system("title Robô - Euro Sincronizacao 2")
#     run = Main()
#     run.main()

def robo_waw():
    from sites.whatsappwu.main import Main
    system("title Robô - Whatsapp Warmup")
    run = Main()
    run.main()

def robo_novo_saque():
    from sites.novosaque.main import Main
    system("title Robô - Novo Saque")
    run = Main()
    run.main()

def robo_pan_078():
    from sites.pan.TarefasPan078 import rodar_pan078
    system("title Robô Pan 078")
    TarefasPan078().rodar_pan078()
    #rodar = rodar_pan078()
    #rodar.run()


def ligar_flask():
    from sites.webhook.consultas.run_index import Rodar_Flask
    system("title Rodar Flask")
    rodar = Rodar_Flask()
    rodar.main()

def robo_insercao_safra_2():
    from sites.safra.insercao2 import Insercao_2
    system("title Robô - Insercao Safra 2")
    insercao_safra = Insercao_2()
    insercao_safra.main()

def robo_insercao_safra():
    from sites.safra.insercao import Consulta_Safra
    system("title Robô - Insercao Safra")
    insercao_safra = Consulta_Safra()
    insercao_safra.main()

def robo_fgts_safra():
    from sites.safra.main import Consulta_Safra_Sinc
    system("title Robô - FGTS Safra")
    fgts_safra = Consulta_Safra_Sinc()
    fgts_safra.main()

def robo_proposta_daycoval():
    from sites.daycoval.main_propostas import Proposta_Daycoval
    system("title Robô - Proposta Daycoval")
    proposta_daycoval = Proposta_Daycoval()
    proposta_daycoval.main()

def robo_ole_portal_orienta():
    from sites.oleConsignado.olePortalOrienta import Ole_Portal_Orienta
    system('title Robô - Ole Portal Orienta')
    ole_portal = Ole_Portal_Orienta()
    ole_portal.logar()

def robo_daycoval_simulacao():
    from sites.daycoval.main_simulacao import Daycoval_Simulacao
    system('title Robô - Simulacao Daycoval')
    simulacao_daycoval = Daycoval_Simulacao()
    simulacao_daycoval.main()

def robo_ole_consulta_in100():
    from sites.oleConsignado.robo_in100 import Main
    system("title Robô - Ole IN100")
    Main().main()

def robo_refin_anex_lib_sms_nova_loja_ole():
    from sites.oleConsignado.robo_refin_anex_lib_sms_2 import Main
    system("title Robô - Ole Refin Anex Lib SMS Nova Loja")
    anexar_sms_2 = Main()
    anexar_sms_2.main()

def robo_ole_refin_insercao_contrato_nova_loja_ole():
    from sites.oleConsignado.robo_insercao_gerar_contrato_2 import Main
    system("title Robô - Ole Refin Insercao e Gerar Contrato Nova Loja")
    insercao_contrato_2 = Main()
    insercao_contrato_2.main()

def robo_extrair_tags_iccdigital():
    from sites.ibConsig.gerar_contrato_icdigital.main_tags import Extrair_Tags_ICcdigital
    extrair_tags_icdigital = Extrair_Tags_ICcdigital()
    extrair_tags_icdigital.iniciar_robos()


def robo_sincronizacao_icdigital():
    from sites.ibConsig.gerar_contrato_icdigital.main import Anexar_Arquivos_IccDigital 
    system("title Robô - Sincronizador Itau ICDigital")
    icc_digital_contratos = Anexar_Arquivos_IccDigital()
    icc_digital_contratos.iniciar_anexar()

def robo_consulta_cpf_receita():
    from sites.busca_cpf.consulta_situacao import Consulta_Receita
    consulta_receita = Consulta_Receita()
    consulta_receita.consulta_site()

def robo_consulta_cpf_tse():
    from sites.busca_cpf.consulta_cpf_tse import Consulta_Cpf
    consulta_cpf = Consulta_Cpf()
    consulta_cpf.consultar()

def robo_google_analytics_consulta_user_explorer():
    from sites.google.analytics.google_analytics_consulta_user_explorer_atualiza_dados import \
        GoogleAnalyticsConsultaUserExplorer
    system("title Robô - Consulta User Explorer Analytics")
    google_analytics_consulta_user_explorer_atualiza_dados = GoogleAnalyticsConsultaUserExplorer()
    google_analytics_consulta_user_explorer_atualiza_dados.main()


def robo_ib_consig_consulta_status():
    from sites.ibConsig.ib_consig_consulta_status.ib_consig_consulta_status import IbConsigGetStatus
    system("title Robô - Atualiza Status Proposta IbConsig")
    ib_consig_status = IbConsigGetStatus()
    ib_consig_status.main()


def robo_ole_portal_orienta_consulta_status():
    from sites.oleOrientaStatusProposta.ole_portal_orienta_consulta_status import OlePortalOrientaGetStatus
    system("title Robô - Atualiza Status Proposta Ole Portal Orienta")
    ole_portal_orienta_consulta_status = OlePortalOrientaGetStatus()
    ole_portal_orienta_consulta_status.main()


def robo_ib_consig():
    from sites.ibConsig.IbConsigInsercao.manager.insercao_refin_novo.insercao import InsercaoIbConsig
    system("title Robô - Inserir IbConsig")
    ib_consig_insercao = InsercaoIbConsig()
    ib_consig_insercao.main()

def robo_ib_consig_portabilidade():
    from sites.ibConsig.IbConsigInsercao.manager.portabilidade.insercao_portabilidade import InsercaoIbConsigPortabilidade
    system("title Robô - Inserir IbConsig Portabilidade")
    ib_consig_insercao_portabilidade = InsercaoIbConsigPortabilidade()
    ib_consig_insercao_portabilidade.main()


def robo_ib_consig_consulta_refinanciamento():
    from sites.ibConsig.ItauConsultaRefin.managers.IbConsultaRefin import IbConsultaRefin
    system("title Robô - Consulta Refinanciamento IbConsig")
    IbConsultaRefin().main()


def robo_ib_consig_consulta_refinanciamento_n2():
    from sites.ibConsig.ItauConsultaRefin.ConsultaRefinN2 import main
    system("title Robô - Consulta Refinanciamento IbConsig N2")
    main()


def robo_cetelem_consulta_refinanciamento():
    from sites.cetelem.cetelem import Cetelem
    system("title Robô - Consulta Refinanciamento Cetelem")
    cetelem_refinanciamento = Cetelem()
    cetelem_refinanciamento.main()


def robo_bradesco_consulta_refinanciamento():
    from sites.bradesco.bradesco import Bradesco
    system("title Robô - Consulta Refinanciamento Bradesco")
    bradesco_refinanciamento = Bradesco()
    bradesco_refinanciamento.main()

def robo_ib_consig_gerar_contrato():
    from sites.ibConsig.gerar_contrato.gerar_contrato import GerarContratoIbConsig
    system("title Robô - Download contrato IbConsig")
    ib_consig_gerar_contrato = GerarContratoIbConsig()
    ib_consig_gerar_contrato.main()


def robo_promo_bank_consulta_inss():
    from sites.promoBank.promo_bank import PromoBank
    system("title Robô - Consulta INSS")
    promo_bank = PromoBank()
    promo_bank.main()


def robo_fila_inss_reprovado_conferir():
    from sites.multiBr.multi_br import MultiBr
    system("title Robô - Fila INSS Reprovado Conferir por Margem")
    fila_inss_reprovado_conferir = MultiBr()
    fila_inss_reprovado_conferir.main()


def robo_marinha_consulta_margem():
    from sites.marinha.main import Main
    system("title Robô - Consulta Margem Marinha")
    Main.run()


def robo_analise_docs():
    from sites.ibConsig.ib_analise_de_fraude.main import Main
    system("title Robô - Ib Analise de Fraude")
    analise_docs = Main()
    analise_docs.main()
    #analise_docs.__init__()


def robo_consulta_margem_sp():
    from sites.portal_consig.main import Main
    system("title Robô - Consulta Margem SP")
    portal_sp = Main()
    portal_sp.main()


def robo_bmg_liberacao():
    from sites.bmg.bmg import BMG
    system("title Robô - Liberacao BMG")
    bmg = BMG()
    bmg.main()


def robo_consulta_margem_inss():
    from sites.inss.consulta_margem_sms.managers.consulta_margem_inss import ConsultaMargemInss
    system("title Robô - Consulta Margem INSS")
    ConsultaMargemInss.main()


def robo_refin_anex_lib_sms():
    from sites.oleConsignado.robo_refin_anex_lib_sms import Main
    system("title Robô - Ole Refin Sincronizacao Anexo Liberacao SMS")
    run = Main()
    run.main()

def robo_refin_2():
    from sites.oleConsignado.ole_consulta_refinanciamento.consulta_refinanciamento import ConsultaRefinanciamento
    system("title Robô - Ole Refin 2")
    run = ConsultaRefinanciamento()
    run.main()


def robo_sinc_insercao():
    from sites.oleConsignado.robo_insercao_gerar_contrato import Main
    system("title Robô - Ole Insercao Gerar")
    run = Main()
    run.main()

def robo_pan_78():
    from sites.pan.TarefasPan078 import TarefasPan078
    system("title Robô - Pan Todas Tarefa 078")
    run = TarefasPan078()
    run.rodar_pan078()

def robo_pan_todas_tarefas():
    from sites.pan.TarefasPan085 import Main
    system("title Robô - Pan Todas Tarefas")
    run = Main()
    run.main()

def robo_pan_85_cookies():
    from sites.pan.TarefasPan085Cookies import TarefasPan085
    system("title Robô - PanConsulta 085 Cookies")
    run = TarefasPan085()
    run.main()


def robo_pan_consulta_refinanciamento064():
    from sites.pan.TarefasPan064 import TarefasPan064
    system("title Robô - PanConsulta 064")
    run = TarefasPan064()
    run.main()

def robo_pan_64_cookies():
    from sites.pan.TarefasPan064Cookies import TarefasPan064
    system("title Robô - PanConsulta 064 Cookies")
    run = TarefasPan064()
    run.main()


def robo_pan_consulta_refinanciamento035():
    from sites.pan.ConsultaRefinPan035 import main
    system("title Robô - PanConsultaRefin035")
    main()


def itau_insercao_auto_init():
    from sites.listerners.itau_insercao_auto_init import main
    system("title Robô - Itau Insercao Listener")
    main()

def robo_cpj_reembolso_bmg():
    import subprocess
    system("title Robô - CPJ Reembolso BMG")

    numero_recibo = input("Digite o número do recibo: ")
    data_inicial = input("Digite a data inicial (dd/mm/yyyy): ")
    data_final = input("Digite a data final (dd/mm/yyyy): ")

    script_path = r'C:\www\automacao\sites\cpj-reembolso-bmg\main.py'
    subprocess.run(['python', script_path, numero_recibo, data_inicial, data_final])


@click.command()
@click.option('--site', 'site')
def main(site=False):
    if site is None:
        questions = [
            {
                'type': 'list',
                'name': 'robo',
                'message': 'Qual robô você deseja iniciar?',
                'choices': [
                    Separator(),
                    {
                        'name': 'rodar_pan078',
                        'value': 'robo_panP078'
                    },
                    Separator(),
                    {
                        'name': 'Insercao_Safra 2',
                        'value': 'robo_insercao_safra_2'
                    },
                    Separator(),
                    {
                        'name': 'Insercao_Safra',
                        'value': 'robo_insercao_safra'
                    },
                    Separator(),
                    {
                        'name': 'Fgts_Safra',
                        'value': 'robo_fgts_safra'
                    },
                    Separator(),
                    {
                        'name': 'Proposta_Daycoval',
                        'value': 'robo_proposta_daycoval'
                    },
                    Separator(),
                    {
                        'name': 'Ole_Portal_Orienta',
                        'value': 'robo_ole_portal_orienta'
                    },

                    Separator(),
                    {
                        'name': 'Simulacao Daycoval',
                        'value': 'robo_daycoval_simulacao'
                    },
                    
                    Separator(),
                    {
                        'name': 'Extrair Tags ICcdigital',
                        'value': 'robo_extrair_tags_iccdigital'
                    },

                    Separator(),
                    {
                        'name': 'Ole Refin Anex Sms Nova Loja',
                        'value': 'robo_refin_anex_lib_sms_nova_loja_ole'
                    },
                    {
                        'name': 'Ole Insercao e Gerar Nova Loja',
                        'value': 'robo_refin_insercao_contrato_nova_loja_ole'
                    },{
                        'name': 'Robo Ole Consulta IN100',
                        'value': 'robo_ole_consulta_in100'
                    },
                    Separator(),
                    {
                        'name': "Sincronizador Itau ICDigital",
                        'value': "robo_sincronizacao_icdigital"
                    },
                    Separator(),
                    {
                        'name': 'Consultar CPF Receita Federal',
                        'value': 'robo_consulta_cpf_receita'
                    },
                    Separator(),
                    {
                        'name': 'Consultar CPF Tse',
                        'value': 'robo_consulta_cpf_tse'
                    },
                    Separator(),
                    {
                        'name': 'Fila INSS Reprovado Conferir por Margem (Teste) - Multi Br',
                        'value': 'filaInssReprovadoConferir'
                    },
                    Separator(),
                    {
                        'name': 'Consulta de Margem Marinha',
                        'value': 'consultaMargemMarinha'
                    },
                    Separator(),
                    {
                        'name': 'Pan Todas Tarefas 085',
                        'value': 'robo_pan_todas_tarefas'
                    }, {
                        'name': 'Pan Todas Tarefas 085 Cookies',
                        'value': 'robo_pan_85_cookies'
                    } ,{
                        'name': 'Pan Todas Tarefas 064',
                        'value': 'robo_pan_consulta_refinanciamento064'
                    }, {
                        'name': 'Pan Todas Tarefas 064 Cookies',
                        'value': 'robo_pan_64_cookies'
                    },{
                        'name': 'Pan Todas Tarefas 078',
                        'value': 'robo_pan_78'
                    },
                    Separator(),
                    {
                        'name': 'Atualização Status Contrato - IbConsig',
                        'value': 'ibConsigConsultaStatus'
                    },
                    Separator(),
                    {
                        'name': 'Inserção - IbConsig',
                        'value': 'ibConsig'
                    },     
                    Separator(),
                    {
                        'name': 'Inserção - IbConsig Portabilidade',
                        'value': 'ibConsigPortabilidade'
                    },
                    Separator(),
                    {
                        'name': 'Consulta INSS',
                        'value': 'promoBank'
                    },
                    Separator(),
                    {
                        'name': 'Consulta Refinanciamentos - IbConsig',
                        'value': 'ibConsigRefinanciamento'
                    }, {
                        'name': 'Consulta Refinanciamentos [N2] - IbConsig',
                        'value': 'ibConsigRefinanciamentoN2'
                    }, {
                        'name': 'Consulta Refinanciamentos - Cetelem',
                        'value': 'cetelemRefinanciamento'
                    }, {
                        'name': 'Consulta Refinanciamentos,Atualização - Bradesco',
                        'value': 'bradescoRefinanciamento'
                    },
                    Separator(),
                    {
                        'name': 'Download Contrato - IbConsig',
                        'value': 'gerarIbConsig'
                    },
                    Separator(),
                    {
                        'name': 'User Explorer Atualização - Google',
                        'value': 'googleAnalyticsConsultaUserExplorer'
                    },
                    Separator(),
                    {
                        'name': 'Ib Analise de Fraude',
                        'value': 'ib_analise_de_fraude'
                    },
                    Separator(),
                    {
                        'name': 'Consulta Margem SP',
                        'value': 'portal_consig'
                    },
                    Separator(),
                    {
                        'name': 'Liberacao BMG',
                        'value': 'liberacao_bmg'
                    },
                    {
                        'name': 'CPJ Reembolso BMG',
                        'value': 'cpj_reembolso_bmg'
                    },
                    Separator(),
                    {
                        'name': 'Consulta Margem INSS',
                        'value': 'margem_inss'
                    },
                    Separator(),
                    {
                        'name': 'Ole Refin Sincronizacao Anexo Liberacao SMS',
                        'value': 'robo_refin_anex_lib_sms'
                    },
                    Separator(),
                    {
                        'name': 'Ole Refin 2',
                        'value': 'robo_refin_2'
                    },
                    Separator(),
                    {
                        'name': "Ole Insercao Gerar",
                        'value': 'robo_sinc_insercao'
                    }, 
                    Separator(),
                    {
                        'name': 'Itau Insercao Listener',
                        'value': 'itau_insercao_auto_init'
                    }, 
                    Separator(),
                    {
                        'name': 'Novo Saque',
                        'value': 'novo_saque'
                    }, 
                    Separator(),
                    {
                        'name': 'Cora Sincronizacao',
                        'value': 'cora_sincronizacao'
                    }, {
                        'name': 'Cora Login',
                        'value': 'cora_login'
                    },
                    Separator(),
                    {
                        'name': 'Crefisa Insercao',
                        'value': 'crefisa'
                    },
                    {
                        'name': 'Crefisa Analise Contrato',
                        'value': 'crefisa_analise'
                    },
                    {
                        'name': 'Crefisa Sincronizacao',
                        'value': 'crefisa_sinc'
                    },
                    Separator(),
                    {
                        'name': 'Whatsapp Warmup',
                        'value': 'whatsapp'
                    },
                    Separator(),
                    {
                        'name': 'Facta Insercao',
                        'value': 'facta'
                    },
                    {
                        'name': 'Facta Analise Contrato',
                        'value': 'facta_analise'
                    },
                    {
                        'name': 'Facta Sincronizacao',
                        'value': 'facta_sinc'
                    },
                    Separator(),
                    {
                        'name': 'Euro Insercao',
                        'value': 'euro'
                    },
                    {
                        'name': 'Euro Analise Contrato',
                        'value': 'euro_analise'
                    },
                    {
                        'name': 'Euro Sincronizacao',
                        'value': 'euro_sinc'
                    },
                    Separator(),
                    {
                        'name': 'PHTech Insercao',
                        'value': 'phtech'
                    },
                    {
                        'name': 'PHTech Sincronizacao',
                        'value': 'phtech_sinc'
                    },

                ]
            }
        ]
       
        answers = prompt(questions)
        site = answers['robo']


    if site == 'ibConsig':
        robo_ib_consig()
    if site == 'ibConsigPortabilidade':
        robo_ib_consig_portabilidade()
    elif site == 'ibConsigRefinanciamento':
        robo_ib_consig_consulta_refinanciamento()
    elif site == 'ibConsigRefinanciamentoN2':
        robo_ib_consig_consulta_refinanciamento_n2()
    elif site == 'cetelemRefinanciamento':
        robo_cetelem_consulta_refinanciamento()
    elif site == 'bradescoRefinanciamento':
        robo_bradesco_consulta_refinanciamento()
    elif site == 'ibConsigConsultaStatus':
        robo_ib_consig_consulta_status()
    elif site == 'promoBank':
        robo_promo_bank_consulta_inss()
    elif site == 'gerarIbConsig':
        robo_ib_consig_gerar_contrato()
    elif site == 'googleAnalyticsConsultaUserExplorer':
        robo_google_analytics_consulta_user_explorer()
    elif site == 'filaInssReprovadoConferir':
        robo_fila_inss_reprovado_conferir()
    elif site == 'consultaMargemMarinha':
        robo_marinha_consulta_margem()
    elif site == 'ib_analise_de_fraude':
        robo_analise_docs()
    elif site == 'portal_consig':
        robo_consulta_margem_sp()
    elif site == 'liberacao_bmg':
        robo_bmg_liberacao()
    elif site == 'cpj_reembolso_bmg':
        robo_cpj_reembolso_bmg()
    elif site == 'margem_inss':
        robo_consulta_margem_inss()
    elif site == 'robo_refin_anex_lib_sms':
        robo_refin_anex_lib_sms()
    elif site == 'robo_refin_2':
        robo_refin_2()
    elif site == "robo_sinc_insercao":
        robo_sinc_insercao()
    elif site == "robo_pan_todas_tarefas":
        robo_pan_todas_tarefas()
    elif site == "robo_pan_78":
        robo_pan_78()
    elif site == "robo_pan_consulta_refinanciamento064":
        robo_pan_consulta_refinanciamento064()
    elif site == "robo_pan_consulta_refinanciamento035":
        robo_pan_consulta_refinanciamento035()
    elif site == "itau_insercao_auto_init":
        itau_insercao_auto_init()
    elif site == 'robo_consulta_cpf_tse':
        robo_consulta_cpf_tse()
    elif site == 'robo_sincronizacao_icdigital':
        robo_sincronizacao_icdigital()
    elif site == 'robo_ole_consulta_in100':
        robo_ole_consulta_in100()
    elif site == 'robo_refin_anex_lib_sms_nova_loja_ole':
        robo_refin_anex_lib_sms_nova_loja_ole()
    elif site == 'robo_refin_insercao_contrato_nova_loja_ole':
        robo_ole_refin_insercao_contrato_nova_loja_ole()
    elif site == 'robo_extrair_tags_iccdigital':
        robo_extrair_tags_iccdigital()
    elif site == 'robo_daycoval_simulacao':
        robo_daycoval_simulacao()
    elif site == 'robo_proposta_daycoval':
        robo_proposta_daycoval()
    elif site == 'robo_ole_portal_orienta':
        robo_ole_portal_orienta()
    elif site == 'robo_pan_64_cookies':
        robo_pan_64_cookies()
    elif site == 'robo_pan_85_cookies':
        robo_pan_85_cookies()
    elif site == 'robo_fgts_safra':
        robo_fgts_safra()
    elif site == 'robo_insercao_safra':
        robo_insercao_safra()
    elif site == 'robo_insercao_safra_2':
        robo_insercao_safra_2()
    elif site == 'robo_consulta_cpf_receita':
        robo_consulta_cpf_receita()
    elif site == 'robo_pan_078':
        robo_pan_078()
    elif site == 'novo_saque':
        robo_novo_saque()
    elif site == 'cora_sincronizacao':
        robo_cora_sincronizacao()
    elif site == 'cora_login':
        robo_cora_login()
    elif site == 'crefisa':
        robo_crefisa()
    elif site == 'crefisa_analise':
        robo_crefisa_analise_contrato()
    elif site == 'crefisa_sinc':
        robo_crefisa_sincronizacao()
    elif site == 'facta':
        robo_facta()
    elif site == 'facta_analise':
        robo_facta_analise_contrato()
    elif site == 'facta_sinc':
        robo_facta_sincronizacao()
    elif site == 'euro':
        robo_euro()
    elif site == 'euro_sinc':
        robo_euro_sincronizacao()
    elif site == 'euro_analise':
        robo_euro_analise_contrato()
    elif site == 'phtech':
        robo_phtech()
    elif site == 'phtech_sinc':
        robo_phtech_sincronizacao()
    elif site == 'whatsapp':
        robo_waw()
    else:
        print("Não foi possível encontrar o robô desejado!")


if __name__ == "__main__":
    main()
