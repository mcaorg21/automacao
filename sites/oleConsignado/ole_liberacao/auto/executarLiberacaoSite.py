from sites.baseRobos.gui_auto import AutoGUI
import pdb,time
from selenium.common.exceptions import TimeoutException

class ExecutarLiberacao(AutoGUI):
    def __init__(self, driver):
        super().__init__(driver)

    def executar_liberacao_propostas(self,ade):
        consulta = dict()

        self.act.enviar_texto("#NumeroProposta",ade)
        self.chrome_driver.execute_script("""document.querySelector("#FormaAtuacao").removeAttribute('name');""")
        self.chrome_driver.execute_script("""$("input:radio[name=%s]:first").attr('checked', true)""" % ('FormaAtuacao'))
        self.act.press_enter('#btnPesquisar')
        time.sleep(2)
        
        try:
            erro_div = self.act.obter_texto("#divMensagemErro")
        except:
            erro_div = ''

        print(erro_div)    
        
        count = 0

        while self.act.quantidade_elemento('#btnAprovar') == 0:
            print('Tentando procurar novamente')
            time.sleep(1)
            self.act.press_enter('#btnPesquisar')
            time.sleep(1)
            count += 1
            if(count == 5):
                consulta['retorno'] = 0
                consulta['mensagem'] = 'Erro na liberação'
                return consulta

        if self.act.quantidade_elemento('#btnAprovar')==1:
            self.act.clicar_elemento('#btnAprovar')
            time.sleep(1)
            
            if self.act.quantidade_elemento('#btnPopUpAprovarSim')==1:
                self.act.clicar_elemento('#btnPopUpAprovarSim')

                time.sleep(2)
                try:
                    erro_div = self.act.obter_texto("#divMensagemErro")
                except:
                    erro_div = ''

                if 'Erro ao confirmar aprovação da proposta' in erro_div:
                    consulta['retorno'] = 0
                    consulta['mensagem'] = self.act.obter_texto("#divMensagemErro")
                    return consulta
                    
                if self.act.quantidade_elemento("#btnOK")==1:
                    try:
                        self.act.clicar_elemento('#btnOK')
                    except TimeoutException:
                        self.chrome_driver.refresh()
                        raise Exception(
                            "Não foi possível clicar no botão de confirmação ['#btnOK'].\n"
                            "Pode ter havido mudança no seletor ou erro interno no sistema."
                        )

                    consulta['retorno'] = 2
                    consulta['mensagem'] = 'Liberação realizada com sucesso!'
                else:
                    consulta['retorno'] = 0
                    consulta['mensagem'] = 'Erro na liberação'

                return consulta

        
        
        
        



