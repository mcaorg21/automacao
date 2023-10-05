from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, sys, time, requests
import re
import datetime
from sites.core.selenium_helper import SeleniumHelper
from PATHS import chrome_user, project_path, driver_path
from pathlib import Path


class GoogleAnalyticsConsultaUserExplorer():
	def __init__(self):
		self.caminho_base = project_path()
		self.json_path = str(Path(self.caminho_base+'/google/analytics/json_consulta/'))
		self.default_file_name = os.path.join(self.json_path, 'user-report-export.json')
		self.driver = self.iniciar_google_chrome()
		self.usuario = "servidor@emprestimofacil.com"
		self.senha = "marcelo2126"
		self.url_login = 'https://analytics.google.com/analytics/web'
		self.url_clientId_analytics = 'https://analytics.google.com/analytics/web/?authuser=0#/report/visitors-user-activity/a153875w188443p32375572/_u.date00=%s&_u.date01=%s&_r.userId=%s&_r.userListReportId=visitors-legacy-user-id/'
		self.selenium_helper = SeleniumHelper(self.driver)

	def iniciar_google_chrome(self):
		options = Options()
		options.add_argument('--ignore-ssl-errors')
		options.add_argument("--window-size=800,600")
		options.add_argument(chrome_user("GoogleAnalytics"))

		#options.add_argument('--user-data-dir=C:/Users/marcelo/AppData/Local/Google/Chrome/GoogleAnalytics')
		#options.add_argument('--user-data-dir=C:/Users/lucas.s/AppData/Local/Google/Chrome/GoogleAnalytics')

		prefs = {
			"download.default_directory": self.json_path,
			'profile.default_content_setting_values.automatic_downloads': True,
			'download.prompt_for_download': False
		}

		options.add_experimental_option('prefs', prefs)

		return webdriver.Chrome(
			executable_path=driver_path(), chrome_options=options)

	def main(self):
		self.driver.get(self.url_login)
		self.login_sistema()
		contratos_a_atualizar = self.busca_contratos_finalizados()
		
		count = 0
		for contrato in contratos_a_atualizar[1:]:
			self.driver.get(self.url_clientId_analytics % (contrato['dataFinalizadoAnalytics'],contrato['dataFinalizadoAnalytics'],contrato['clientIdAnalytics']))
			
			if count == 0: 
				segundos_a_esperar = 20
			else:
				segundos_a_esperar = 7

			self.countdown(segundos_a_esperar,1,'Aguardando...')
			self.selenium_helper.trocar_frame('galaxy')

			self.driver.execute_script(""" var script = document.createElement('script');script.type = 'text/javascript'; script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js';	document.head.appendChild(script); """)
			self.countdown(segundos_a_esperar,5,'Aguardando...')
			try:
				usuario_nao_encontrado = self.driver.execute_script(""" var resultado = $('.C_USER_ACTIVITY_PROFILE_DELETION_IN_PROGRESS_CONTAINER').text(); return resultado;""")
			except:
				pass
			id_analytics_tela = self.driver.execute_script("""var resultado = $('._GAZeb').text(); return resultado;""")

			if(id_analytics_tela == contrato['clientIdAnalytics']):
				if(usuario_nao_encontrado):
					dados_analytics = {
						'key': 'f689f1e12a0399fba803cb2365fc362f',
						'codigoCon': contrato['codigoCon'],
						'ade': contrato['ade'],
						'dataFinalizadoDateTime':contrato['dataFinalizadoDateTime'], 
						'banco':contrato['nomeBanco'],
						'tipoContrato':contrato['tipoContrato'], 
						'subProduto':contrato['0']['valor_com'],
						'orgao':contrato['1']['valor_com'],
						'conversaoRegistradaUconecte':contrato['conversao'], 
						'clientIdAnalytics':contrato['clientIdAnalytics'], 
						'IdAnalyticsBigQuery':'000000000', 
						'ultimaVisualizacao':'1983-01-18', 
						'dispositivo':'NA',
						'plataformaDoDispositivo':'NA',
						'dataAquisicao':'1983-01-18',
						'canal':'NA',
						'origemMidia':'NA',
						'campanha':'NA',
						'sessoesTotaisLTV':'0',
						'sessoesFecharContrato':'0',
						'duracaoSessoesTotaisLTV':'0',
						'duracaoSessoesFecharContrato':'0'
					}
				else:
					texto_detalhes_analytics_cliente = self.driver.execute_script("""var resultado = []; $('.C_USER_ACTIVITY_PROFILE_SCORECARD_CONTENT_TEXT').each(function(str){resultado.push($(this).text())});return resultado;""")
					texto_detalhes_analytics_cliente_sessao = self.driver.execute_script("""var resultado = []; $('._GAsr').each(function(str){resultado.push($(this).text())});return resultado;""")
					
					texto =''
					array_dados_sessoes = []
					for texto in texto_detalhes_analytics_cliente_sessao[0].split('Sessões'):
						if(texto != "" and "\t" not in texto):
							array_dados_sessoes.append(re.sub("[^0-9]","",texto))
						
					for texto in texto_detalhes_analytics_cliente_sessao[1].split('sessão'):
						if(texto != "" and "\t" not in texto):
							texto = re.sub("[^0-9:]","",texto)
							if(texto!=""):
								segundos = self.converte_hora_string_segundos(texto)
								array_dados_sessoes.append(int(segundos))

					dados_analytics = {
						'key': 'f689f1e12a0399fba803cb2365fc362f',
						'codigoCon': contrato['codigoCon'],
						'ade': contrato['ade'],
						'dataFinalizadoDateTime':contrato['dataFinalizadoDateTime'], 
						'banco':contrato['nomeBanco'],
						'tipoContrato':contrato['tipoContrato'], 
						'subProduto':contrato['0']['valor_com'],
						'orgao':contrato['1']['valor_com'],
						'conversaoRegistradaUconecte':contrato['conversao'], 
						'clientIdAnalytics':contrato['clientIdAnalytics'], 
						'IdAnalyticsBigQuery':texto_detalhes_analytics_cliente[0], 
						'ultimaVisualizacao':self.converte_data_string_data(texto_detalhes_analytics_cliente[1]), 
						'dispositivo':texto_detalhes_analytics_cliente[2],
						'plataformaDoDispositivo':texto_detalhes_analytics_cliente[3],
						'dataAquisicao':self.converte_data_string_data(texto_detalhes_analytics_cliente[4]),
						'canal':texto_detalhes_analytics_cliente[5],
						'origemMidia':texto_detalhes_analytics_cliente[6],
						'campanha':texto_detalhes_analytics_cliente[7],
						'sessoesTotaisLTV':array_dados_sessoes[0],
						'sessoesFecharContrato':array_dados_sessoes[1],
						'duracaoSessoesTotaisLTV':array_dados_sessoes[2],
						'duracaoSessoesFecharContrato':array_dados_sessoes[3]
					}
					
				self.atualiza_contrato_web_admin(contrato['codigoCon'],dados_analytics)
				count += 1
			else:
				self.countdown(10,10,'Erro no carregamento da tela...Passando para próximo contrato...')

		if(count == 0):		
			self.countdown(7200,7200,'Sem sincronização! Aguardando...')
		else:
			self.countdown(10,10,'Terminada sincronização de %s contratos...' % (count))
		self.main()

	def login_sistema(self):
		try:
			campo_login = self.driver.find_element_by_css_selector(
				"input[name='identifier']")
			campo_login.clear()
			campo_login.send_keys(self.usuario)
			self.clicar_elemento_js('identifierNext')	
			self.countdown(7,7,'parado...')
			password = self.driver.find_element_by_css_selector(
				"input[name='password']")
			password.clear()
			password.send_keys(self.senha)
			self.clicar_elemento_js('passwordNext')
			self.countdown(6000,10,'parado...')
			return True
		except Exception as e:
			return False

	def busca_contratos_finalizados(self):
		request_contratos_a_atualizar = requests.get(
			'https://emprestimofacil.co/web_admin/api/v1/contratos/finalizados/analytics-todos-bancos/?key=f689f1e12a0399fba803cb2365fc362f')

		if (request_contratos_a_atualizar.status_code != 200):
			input('Itaú Consignado Consignado Error - Não foi possível buscar os contratos')

		return request_contratos_a_atualizar.json()

	def busca_dados_proposta(self,ade,codigo_con):
		self.countdown(2,2,'Buscando proposta...')
		try:
			self.driver.execute_script("""$('[title="Situação do contrato"]').click()""")	
		except Exception:
			print('Página ainda não carregou, tentando novamente..')
			self.busca_dados_proposta(ade,codigo_con)

		detalhes_proposta = self.busca_status_contrato_tela()
		if(detalhes_proposta[0] == 'Cancelada' or detalhes_proposta[0] == 'Rejeitada' or detalhes_proposta[0] == 'Solicitada'):
			status_proposta = detalhes_proposta[0]
			observacao_detalhada = '%s - %s -  %s %s %s %s' % (detalhes_proposta[1],detalhes_proposta[2],
																detalhes_proposta[3],detalhes_proposta[4],
																	detalhes_proposta[5],detalhes_proposta[-1])
		else:
			status_proposta = detalhes_proposta[0]+' - '+detalhes_proposta[1]	
			observacao_detalhada = '%s %s' % (detalhes_proposta[3],detalhes_proposta[-1])
		
		dados = {
					"key": "f689f1e12a0399fba803cb2365fc362f",
					"statusPropostaBanco": status_proposta, 
					"observacaoDetalhadaBanco": observacao_detalhada,
					"codigoCon": codigo_con,
					"ade": ade
				}
		return dados	

	def atualiza_contrato_web_admin(self,codigo_con,dados):
		request_dados_contrato = requests.post(
			"https://emprestimofacil.co/web_admin/api/v1/atualiza-tabela-google-analytics/", data=dados)
		
		if (request_dados_contrato.status_code != 200):
			input('Google Error - Não foi possível atualizar no request' (codigo_con))
		else:
			print('Contrato %s atualizado com sucesso!' % (codigo_con))

	def clicar_elemento_js(self, seletor):

		self.driver.execute_script("""document.getElementById('%s').click()""" % (seletor))

	def clicar_elemento_jquery(self, seletor):

		self.driver.execute_script("""$('%s').click();""" % (seletor))

	def converte_data_string_data(self,data_analytics):

		array_data = data_analytics.split(' ')
		try:
			ano = array_data[2]
			dia = array_data[1].replace(',','')
			mes = self.trocar_string_mes_numero(array_data[0].replace('.','')) 
			return '%s-%s-%s' % (ano,mes,dia)
		except:
			return '1983-01-18' 

	def trocar_string_mes_numero(self,mes):
		switcher = {
			"jan":'01',
			"fev":'02',
			"mar":'03',
			"abr":'04',
			"mai":'05',
			"jun":'06',
			"jul":'07',
			"ago":'08',
			"set":'09',
			"out":'10',
			"nov":'11',
			"dez":'12'
		}
		mes_analytics = switcher.get(mes, "invalido")
		if(mes_analytics == 'invalido'):
			self.countdown(600000,600000,mes+'Nao achado na funcao mes')
		return mes_analytics

	def converte_hora_string_segundos(self,hora_minuto_segundos_string):
		if(hora_minuto_segundos_string[0]==':'):
			hora_minuto_segundos_string = hora_minuto_segundos_string[1:]
		hora_minuto_segundo = hora_minuto_segundos_string.split(':')
		hora = int(hora_minuto_segundo[0])
		if(hora < 24):
			x = time.strptime(hora_minuto_segundos_string,'%H:%M:%S')
			return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
		else:
			hora_segundos = int(hora)*3600
			minutos_segundos = int(hora_minuto_segundo[1])*60
			segundos = int(hora_minuto_segundo[2])
			segundos_totais = hora_segundos + minutos_segundos + segundos
			return segundos_totais

	def countdown(self,t,step=1,msg=''): 
	    pad_str = ' ' * len('%d' % step)
	    for i in range(t, 0, -step):
	       	print ('%s %d segundo(s) %s\r' % (msg, i, pad_str))
	        sys.stdout.flush()
	        time.sleep(step)

	        
if __name__ == "__main__":
	run = GoogleAnalyticsConsultaUserExplorer()
	run.main()
