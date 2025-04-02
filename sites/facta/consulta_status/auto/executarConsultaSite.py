from sites.baseRobos.gui_auto import AutoGUI


class ExecutarConsultaStatus(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)
        self.delay = 0.1
        self.pause = 1
        self.act.time_out = 5

    def extrair_dados_consulta(self,tipo_con):
        consulta = dict()

        loc_status_macro = "#statusMacro"
        consulta["statusPropostaBanco"] = self.act.obter_texto(loc_status_macro)

        loc_status_detalhado = "#statusDetalhado"
        consulta["observacaoDetalhadaBanco"] = self.act.obter_texto(loc_status_detalhado)

        loc_fase = '//*[text()="Fase:"]/../span'
        fase: str = self.act.obter_texto(loc_fase, self.by.XPATH)

        if consulta["statusPropostaBanco"] != 'PAGO VIA TED':
            if not consulta["observacaoDetalhadaBanco"]:
                consulta["observacaoDetalhadaBanco"] = fase    
        # if consulta["statusPropostaBanco"] != 'PAGO VIA TED':
        #     if not consulta["statusPropostaBanco"] and not consulta["observacaoDetalhadaBanco"]:
        #         obs_mais_fase = f'{consulta["observacaoDetalhadaBanco"]} - {fase}'
        #         consulta["observacaoDetalhadaBanco"] = obs_mais_fase

        #     if not consulta["observacaoDetalhadaBanco"]:
        #         consulta["observacaoDetalhadaBanco"] = fase

        #         if consulta["statusPropostaBanco"]:
        #             consulta["statusPropostaBanco"] = consulta["observacaoDetalhadaBanco"]

        if(tipo_con == 'NOVO SEM SEGURO'):
            loc_val_contrato = '//*[@id="panel-5"]/div[57]/p'
            if 'Valor liberado' not in self.act.obter_texto(loc_val_contrato, self.by.XPATH):
                loc_val_contrato = '//*[@id="panel-5"]/div[58]/p'
                print(self.act.obter_texto(loc_val_contrato, self.by.XPATH))
                consulta["valorContrato"] = self.act.obter_texto(loc_val_contrato, self.by.XPATH).replace("Valor liberado (R$):\n", '')
            else:
                consulta["valorContrato"] = self.act.obter_texto(loc_val_contrato, self.by.XPATH).replace("Valor liberado (R$):\n", '')

            loc_qt_parc = '//*[@id="panel-5"]/div[44]/p'
            if 'Quantidade de parcelas' not in self.act.obter_texto(loc_qt_parc, self.by.XPATH):
                loc_qt_parc = '//*[@id="panel-5"]/div[43]/p'
                print(self.act.obter_texto(loc_qt_parc, self.by.XPATH))
                consulta["prazoContrato"] = self.act.obter_texto(loc_qt_parc, self.by.XPATH).replace("Quantidade de parcelas:\n", '')
            else:
                consulta["prazoContrato"] = self.act.obter_texto(loc_qt_parc, self.by.XPATH).replace("Quantidade de parcelas:\n", '')

            #loc_val_parc = "//strong[text()='Valor da parcela (R$):']"
            loc_val_parc = '//*[@id="panel-5"]/div[45]/p'
            if 'Valor da parcela' not in self.act.obter_texto(loc_val_parc, self.by.XPATH):
                loc_val_contrato = '//*[@id="panel-5"]/div[44]/p'
                print(self.act.obter_texto(loc_val_contrato, self.by.XPATH))
                consulta["parcelaContrato"] = self.act.obter_texto(loc_val_contrato, self.by.XPATH).replace("Valor da parcela (R$):\n", '')
            else:
                consulta["parcelaContrato"] = self.act.obter_texto(loc_val_parc, self.by.XPATH).replace("Valor da parcela (R$):\n", '')

        print(consulta)

        return consulta

    def extrair_historico_modal(self):
        
        loc_btn_dropdown = 'button[data-id="dropdownObservacoes"]'
        self.act.clicar_elemento(loc_btn_dropdown)

        try:
            loc_historico = 'a[role="option"]'
            resultados = self.act.retornar_elementos(loc_historico)
        except:
            resultados = self.act.retornar_elementos('option')

        historico = ''

        for observacao in resultados:
            historico += '\n' + observacao.text
            historico += '\n'

        print(historico)
        return historico
