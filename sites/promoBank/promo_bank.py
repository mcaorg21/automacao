from selenium import webdriver

from selenium.webdriver.chrome.options import Options
import time
import requests
import re
import json
import datetime
import random
import pickle
import os, shutil,pdb
import pdb
import tkinter as tk

from sites.core.selenium_helper import SeleniumHelper
from sites.baseRobos.core.helpers import (
	formatar_moeda, formatar_porcentagem, formatar_data_banco,formatar_data_banco_anomenor,
	countdown, identificar_erro_robo, definir_nome_robo)
from sites.core.uconecte import Uconecte
from sites.core.selenium_actions import SeleniumActions
from sites.baseRobos.core.selenium_actions import SeleniumActions
import PATHS
from sites.baseRobos.data_handler import DataHandler
from selenium.webdriver.common.by import By
from multiprocessing.dummy import Pool

#testando adicionar comentarios

class PromoBank:

	id_fila_retencao = 32
	id_fila_inss= 10
	id_fila_reprovado_conferir = 33

	def __init__(self):
		#root = tk.Tk()
		#screen_width = root.winfo_screenwidth()
		#screen_height = root.winfo_screenheight()

		self.caminho_base = PATHS.project_path()
		self.chrome_user = PATHS.chrome_user(f"Promobank{random.randrange(2,12)}")
		#self.chrome_user = PATHS.chrome_user(f"Promobank12")
		self.driver_path = PATHS.driver_path()
		self.api_key = "f689f1e12a0399fba803cb2365fc362f"
		self.id_robo = 10
		self.log = DataHandler()
		self.mensagem_erro = ""

		self.cookies_path = self.caminho_base+"\\promoBank\\cookies\\" + "usuario_promobank.pkl"
		self.cookies_path_json = self.caminho_base+"\\promoBank\\cookies\\" + "usuario_promobank.json"

		options = Options()
		options.add_argument('--ignore-ssl-errors')
		options.add_argument('log-level=3')
		options.add_argument('--profile-directory=Default')
		#options.add_argument(f'--window-position={int(screen_width-screen_width/3)},0')
		options.add_argument(f'--window-size=1300,1000')

		options.add_argument(self.chrome_user)
		
		try:
			self.driver = webdriver.Chrome(
					executable_path=self.driver_path,
					chrome_options=options)
		except:
			options = Options()
			self.chrome_user = PATHS.chrome_user(f"Promobank{random.randrange(2,12)}")
			options.add_argument(self.chrome_user)
			options.add_argument('--ignore-ssl-errors')
			options.add_argument('log-level=3')
			options.add_argument('--profile-directory=Default')
			self.driver = webdriver.Chrome(
					#executable_path=self.driver_path,
					options=options)
		
		self.uconecte = Uconecte()
		self.selenium_helper = SeleniumHelper(self.driver)
		self.act = SeleniumActions(self.driver)
		self.contar_inicio = 0

	def main(self,retorno='N'):
		self.driver.get('https://www.promobank.online/sistema')
		
		#self.driver.delete_all_cookies()


		# o promobank esta bloqueando login direto entao comecaremos a usar os cookies gerados pelo login manual
		
		#retorno = 'C'
		if(retorno == 'C'):
			retorno = input('Precisamos dos cookies atuais do endereço https://docs.google.com/document/d/18tv5YAqU9nE4ntppsJH_amr2mV2vPAqSrq6_FRM14OU/edit. Digite C para continuar: ')

		if(retorno == 'C'):
			print('Iniciando função de consulta...')	
			#self.driver.get('https://promobank.com.br/')
			self.driver.get("https://promobank.online/")
			time.sleep(2)
			self.selecionar_aba_consulta()

			while True:
				definir_nome_robo('Consulta INSS')
				self.validar_horario()

				print("Processando Fila do INSS")
				self.processar_filas_uconecte('inss')
				time.sleep(5)

				print("Processando Fila de Retenção")
				self.processar_filas_uconecte('retencao')
				time.sleep(random.randrange(7,15))

				print("Processando Fila Reprovado a Conferir")
				self.processar_fila_reprovado_conferir()
				time.sleep(random.randrange(7,15))

		else:

			print('Consulta via robo iniciando...')

			self.contar_inicio += 1
			if(self.contar_inicio > 10):
				self.driver.quit()
				
			try:
				self.load_cookies_pasta()
			except:
				pass
			time.sleep(random.randrange(1,3))

			try:
				if self.act.quantidade_elemento('/html/body/div[1]/div/div/form[1]/button[1]', By.XPATH) == 1:
					self.act.clicar_elemento('/html/body/div[1]/div/div/form[1]/button[1]', By.XPATH)

				try:
					# try:				
					# 	self.act.clicar_elemento('/html/body/div[1]/div[4]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div[4]/a/span', By.XPATH)
					# except:
					# 	pass
					# time.sleep(2)
					
					# try:				
					# 	self.act.clicar_elemento('/html/body/div[1]/div[4]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div[4]/a/span', By.XPATH)
					# except:
					# 	pass
					# time.sleep(2)

					# try:
					# 	print('entra')
					# 	self.act.clicar_elemento('/html/body/div[1]/div[4]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div[4]/a/span', By.XPATH)
					# except:
					# 	pass

					time.sleep(1)
					
					#self.act.clicar_elemento('/html/body/section/div/div/div[3]/div/div[2]/button', By.XPATH)
					time.sleep(1)
				except:
					pass

			except:
				print('Sem erro de login')
				pass

			try:
				if self.selenium_helper.buscar_quantidade_elemento('.nav-search-input') == 0:
					while not self.login():
						print("Tentativa de Login...")	
			except:
				self.driver.get("https://www.promobank.online/")
				while not self.login():
						print("Tentativa de Login...")

			try:
				
				time.sleep(15)
				self.driver.find_element_by_css_selector('.containerSenha')
				try:
					loc_sair= '/html/body/div/div/div/form[1]/button[2]'
					self.act.clicar_elemento(loc_sair, By.XPATH)
					self.login()
				except:
					print('Resolvendo o captcha para continuar')
					time.sleep(random.randrange(10,20))
					# while(self.act.quantidade_elemento('/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[2]', By.XPATH) == 1):
					# 	print('Aguardando solucionar o captcha...')
					# 	time.sleep(1)
					#pdb.set_trace()
					time.sleep(180)
					self.selecionar_aba_consulta_tentativa()
			except:
				print('Logado')
				time.sleep(random.randrange(1,3))
				self.selecionar_aba_consulta()
				pass

			while True:
				try:
					definir_nome_robo('Fila Consulta simulaçãoINSS')
					self.validar_horario()
					print('Iniciando função de consulta...')
					
					self.selenium_helper.save_cookies(self.cookies_path)
					self.escreve_json(self.cookies_path)

					print("Processando Fila do INSS")
					self.processar_filas_uconecte('inss')
					time.sleep(random.randrange(2,4))

					print("Processando Fila de Retenção")
					self.processar_filas_uconecte('retencao')
					time.sleep(random.randrange(2,4))

					print("Processando Fila Reprovado a Conferir")
					self.processar_fila_reprovado_conferir()
					time.sleep(random.randrange(2,4))
					time.sleep(3)

					#self.selecionar_aba_consulta()
					print('Aguardando 90 segundos...')
					time.sleep(90)
				except Exception as e:
					self.driver.quit()
					PromoBank().main()
					#self.main()
					#self.main()
					# identificar_erro_robo()
					# raise Exception(str(e))

	def escreve_json(self,path):
		with open(self.cookies_path, 'rb') as fpkl, open(self.cookies_path_json, 'w') as fjson:
			data = pickle.load(fpkl)
			json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)
			
			
		file = open(self.cookies_path_json)
		cookies = json.load(file)
		dados = {
					'id_robo' : self.id_robo,
					'cookies_json': json.dumps(cookies)
				}
		
		req = requests.post("https://emprestimofacil.co/web_admin/api/v1/atualiza-dados/atualiza-cookies/promobank/?key={}".format(self.api_key), data=dados)

		for cookie in cookies:
			try:
				if('expiry' not in cookie):
					self.driver.add_cookie(cookie)
			except Exception as e:
				pass

	def load_cookies_pasta(self):
		self.driver.get('https://www.promobank.online/')
		self.driver.delete_all_cookies()
		file = open(self.cookies_path_json)
		cookies = json.load(file)

		for cookie in cookies:
			try:
				if('expiry' not in cookie):
					self.driver.add_cookie(cookie)
			except Exception as e:
				pass
		self.driver.get('https://www.promobank.online/sistema')

	def load_cookies_promobank_web_admin(self):
		
		url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/promobank/?key={}".format(self.api_key)
		cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

		self.driver.get('https://www.promobank.online/')
		self.driver.delete_all_cookies()

		for cookie in cookies:
			try:
				if('expiry' not in cookie):
					self.driver.add_cookie(cookie)
			except Exception as e:
				pass
		self.driver.get('https://www.promobank.online/sistema')
		self.selecionar_aba_consulta_api()

	def load_cookies_promobank_web_admin_api(self):
		self.driver.get('https://www.promobank.online/')
		
		url = "http://emprestimofacil.co/web_admin/api/v1/consulta/cookies/promobank/?key={}".format(self.api_key)
		cookies = self.selenium_helper.load_cookies_robo_web_admin(url, self.id_robo)

		self.driver.delete_all_cookies()

		for cookie in cookies:
			try:
				if('expiry' not in cookie):
					self.driver.add_cookie(cookie)
			except Exception as e:
				pass
		self.driver.get('https://www.promobank.online/sistema')
		self.selecionar_aba_consulta_api()

	def abre_chrome(self,fila_tipo = 'api'):
		self.driver.get('https://www.promobank.online/')
		self.driver.delete_all_cookies()
		try:
			self.escreve_json(self.cookies_path)
		except:
			self.main()
		if(fila_tipo == 'api'):
			self.driver.get('https://www.promobank.online/sistema')
			self.selecionar_aba_consulta_api()
		else:
			self.main()
		
	def main_api(self,solicitacao,fila):
		#self.driver.get('https://www.promobank.com.br/')
		#self.driver.delete_all_cookies()
		#self.escreve_json(self.cookies_path)
		#self.driver.get('https://promobank.com.br/sistema')
		#self.selecionar_aba_consulta_api()
		#self.load_cookies_promobank_web_admin_api()
		definir_nome_robo('POST Consulta INSS')
		self.matricula_consultar = solicitacao['matricula']
		retorno = self.consultar_matricula(solicitacao['matricula'],fila)
		retorno = json.dumps(retorno)

		dados = {
					"consultaBeneficio": retorno,
					"idPessoa": solicitacao['fk_idPessoa'],
					"idSolicitacao": solicitacao['idSolicitacao'],
					"idPerfilPessoa": solicitacao['fk_idPerfil_pessoa']
				}

		return dados	

	def cosulta_beneficio_cpf(self,cpf):
		definir_nome_robo('POST Consulta CPF Beneficio')
		#self.load_cookies_promobank_web_admin_api()
		retorno = self.consultar_cpf_matricula(cpf)
		retorno = json.dumps(retorno)	
		return retorno

	def fechar_driver(self):
		self.driver.quit()
		
	def validar_horario(self):
		data_hora = datetime.datetime.now()
		if (data_hora.hour > 22 or data_hora.hour < 6):
			countdown(10000, 1, "Aguardando horário comercial...")
			#data_hora = datetime.datetime.now()			
			#print("Aguardando horario comercial... Fora do horario " + data_hora.hour)
			#time.sleep(60)
			self.main()

	def validar_horario_api(self):
		data_hora = datetime.datetime.now()

		if (data_hora.hour > 22 or data_hora.hour < 6):
			return {'status':'fora_horario'}
		else:
			return {'status':'dentro_horario'}	

	def login(self):

		try:
			self.act.clicar_elemento('//*[@id="stm_gdpr_popup_accept"]',By.XPATH)
			time.sleep(2)
			self.act.clicar_elemento('//*[@id="sgpb-popup-dialog-main-div-wrapper"]/div/img', By.XPATH)
		except:
			pass

		try:
			self.driver.delete_all_cookies()	
			self.act.enviar_texto_intervalado('[name=emp_senha]', '3732')
			try:
				self.act.enviar_texto_intervalado('#loginUsuario', 'mca.consulta')	
			except:
				self.act.enviar_texto_intervalado('#inputUsuario', 'mca.consulta')
				pass

			try:
				self.act.enviar_texto_intervalado('#loginSenha', 'Tim_909176')
			except:
				self.act.enviar_texto_intervalado('#passField', 'Tim_909176')
				pass

		except Exception:

			self.main()
	
		#o botao submit nao esta funcionando daremos um enter
		time.sleep(random.randrange(1,7))
		#self.selenium_helper.press_enter('#submitButton')
		#time.sleep(random.randrange(7,15))
		try:
			self.selenium_helper.press_enter('#submitButton')
			time.sleep(5)
		except:
			pass

		try:
			segundos = int(self.act.obter_texto('//*[@id="msg"]', By.XPATH).split(':')[1])*60
			#pdb.set_trace()
			countdown(segundos, 3, "Aguardando desbloqueio de "+ str(segundos))

			time.sleep(30)
			self.main()
		except:
			pass

		print('Logado com sucesso!')
		return True

	def reiniciar_browser(self):
		data_hora = datetime.datetime.now()

		if (data_hora.hour > 9 and data_hora.hour < 20):
			self.driver.close()
			self.__init__()
			return self.main()

	def buscar_solicitacoes(self, tipo_consulta):
		request_solicitacoes = requests.get("https://app.emprestimofacil.com/api/v1/solicitacoes/{}?key={}".format(tipo_consulta, self.api_key))
		
		if (request_solicitacoes.status_code != 200):
			print(request_solicitacoes.text)
			input("Não foi possível buscar as solicitações")

		solicitacoes = request_solicitacoes.json()['solicitacoes']
		self.uconecte.atualizar_status_robo(self.id_robo)
		return solicitacoes

	def processar_filas_uconecte(self, tipo_consulta):
		"""
		raises Exception("Parâmetro tipo consulta inválido:", tipo_consulta)
		"""
		#pdb.set_trace()
		solicitacoes = self.buscar_solicitacoes(tipo_consulta)

		for solicitacao in solicitacoes:
			try:
				print("Trabalhando na solicitação {}".format(solicitacao['idSolicitacao']))

				# Iniciar o log de acordo com o tipo de consulta
				id_fila: int
				if 'inss' in tipo_consulta:
					id_fila = self.id_fila_inss
				elif 'retencao' in tipo_consulta:
					id_fila = self.id_fila_retencao
				else:
					raise Exception("Parâmetro tipo consulta inválido:", tipo_consulta)
				# self.log.api_iniciar_log_robo(
				# 	idRobo=id_fila,
				# 	idSolicitacao=solicitacao['idSolicitacao']
				# )

				retorno = self.consultar_matricula(solicitacao['matricula'])
				retorno = json.dumps(retorno)

				dados = {
					"consultaBeneficio": retorno,
					"idPessoa": solicitacao['fk_idPessoa'],
					"idSolicitacao": solicitacao['idSolicitacao'],
					"idPerfilPessoa": solicitacao['fk_idPerfil_pessoa']
				}
				print("Salvando consulta com os dados:", dados)
				
				request_consulta = requests.post("https://app.emprestimofacil.com/api/v1/consultas/inss", data=dados)

				print(request_consulta.status_code);
				
				if request_consulta.status_code != 200:
					print(request_consulta.text, request_consulta.status_code)
					input('Não foi possível salvar a consulta do INSS, verifique o LOG')
					continue

				if (solicitacao['fk_idCategoria'] == '1'):
					self.uconecte.calcular_financiamento(solicitacao)
				elif (solicitacao['fk_idCategoria'] == '2'):
					self.uconecte.calcular_financiamento_aumento_margem(solicitacao)
				elif (solicitacao['fk_idCategoria'] == '5'):
					self.uconecte.calcular_cartao_consignado(solicitacao)

				# self.log.api_registrar_log_robo(
				# 	log="Consulta realizada com sucesso.",
				# 	status=2
				# )
			except Exception as e:
				# self.log.api_registrar_log_robo(
				# 	log=f"ERRO: {e}",
				# 	status=0
				# )
				self.driver.quit()

	def selecionar_aba_consulta(self,modo='manual'):
		print("Recarregando a página!")
		try:
			if(self.selenium_helper.buscar_quantidade_elemento('.logoCRM')==0 and self.selenium_helper.buscar_quantidade_elemento('.panel-body')==0):
				self.main()
			else:
				self.driver.get('https://www.promobank.online/sistema')
		except Exception:
			#pdb.set_trace()
			self.driver.quit()
			PromoBank().main()
			self.main()

		# try:
		# 	self.driver.get("https://promobank.com.br/sistema/")
		# except Exception:
		# 	return self.selecionar_aba_consulta()
		time.sleep(3)

		try:	
			loc_consulta = '/html/body/div[4]/div[2]/div[1]/div/span[3]/div[1]'

			try:
				self.act.clicar_elemento(loc_consulta, By.XPATH)
			except:
				self.act.clicar_elemento('//*[@id="navbar-container"]/div[2]/ul/li[5]/a/i[2]', By.XPATH)
				self.act.clicar_elemento(loc_consulta, By.XPATH)
				pass
			#pdb.set_trace()
			loc_frame_consulta = '//iframe[@src="corpo.php?src=consulta/index.php"]'
			iframe_consulta = self.act.retornar_elemento(loc_frame_consulta, By.XPATH)

			self.driver.switch_to.frame(iframe_consulta)
		except Exception:
			time.sleep(random.randrange(60,120))
			return self.login()
	
	def selecionar_aba_consulta_api(self):

		try:
			loc_consulta = '//*[text()="Consulta"]'
			self.act.clicar_elemento(loc_consulta, By.XPATH)
		except:
			return {'retorno': 11, 'mensagem': 'Erro na consulta...'}

		loc_frame_consulta = '//iframe[@src="corpo.php?src=consulta/index.php"]'
		iframe_consulta = self.act.retornar_elemento(loc_frame_consulta, By.XPATH)

		self.driver.switch_to.frame(iframe_consulta)

	def selecionar_aba_consulta_tentativa(self):
		self.driver.get('https://www.promobank.online/sistema')
		time.sleep(5)
		loc_consulta = '//*[text()="Consulta"]'
		self.act.clicar_elemento(loc_consulta, By.XPATH)

		loc_frame_consulta = '//iframe[@src="corpo.php?src=consulta/index.php"]'
		iframe_consulta = self.act.retornar_elemento(loc_frame_consulta, By.XPATH)

		self.driver.switch_to.frame(iframe_consulta)

	def consultar_matricula(self, matricula, fila = 'comum'):
		try:
			self.selenium_helper.atribuir_valor_campo_driver('[name=value]', matricula)
			self.selenium_helper.clicar_elemento_driver('#buttonConsultarInss')

			while(self.act.quantidade_elemento('/html/body/div[2]/div[2]/div[2]/div[5]/img', By.XPATH) == 1):
				print('Aguardando loading...')
				time.sleep(1)

			time.sleep(1)
			#pdb.set_trace()

			try:
				self.selenium_helper.clicar_elemento_driver('.fancybox-close')
			except:
				pass

			try:
				text_pagina_expirou = self.selenium_helper.verificar_texto_campo_jquery('#DivRule')
				if('Esta página expirou' in text_pagina_expirou):
					print('Logando novamente e reiniciando a busca.')
					self.main()
			except:
				pass
		except:
			self.driver.quit()
			PromoBank().main()
			return {'retorno': 11, 'mensagem': 'Erro na consulta...'}

		self.aguardar_loading_botao()
		try:
			if (len(matricula.strip()) > 10 or len(matricula.strip()) == 0 or len(matricula.strip()) < 8):
				raise IncorrectInfoException(
					message="Número do benefício informado está incorreto. Ele deve ter 10 números. Benefício informado por você: {}".format(matricula)
				)
			
			self.tratar_erros_consulta()

			self.retorno = {"retorno": 1,"mensagem": '--Consulta realizada com sucesso! Funcao 7'}

			self.consultar_detalhamento()
			if(fila != 'reprovado_conferir'):
				self.extrair_refinanciamentos()
			self.extrair_dados_consulta()

			return self.retorno
		except BeneficioCancelado as e:
			return {'retorno': 2, 'mensagem': e.message}
		except InfoNotFoundException as e:
			return {'retorno': 3, 'mensagem': e.message}
		except IncorrectInfoException as e:
			return {'retorno': 4, 'mensagem': e.message}
		except SiteLimitePesquisa as e:
			self.driver.quit()
			PromoBank().main()
			return {'retorno': 11, 'mensagem': 'Erro na consulta...'}
		except ConsultErrorException as e:
			if(fila != 'api'):
				self.fechar_driver()
				#self.reabrir_tela_consulta()
			return {'retorno': 11, 'mensagem': e.message}
		except Exception as e:
			if(self.selenium_helper.buscar_quantidade_elemento('#buttonConsultarInss')==0):
				if(fila == 'api'):
					print('Erro consulta>>>>>>>>>>' + str(matricula))
					return {'retorno': 11, 'mensagem': 'Erro na consulta...'}
				else:
					self.main()
			else:
				if(fila == 'api'):
					print('Erro consulta>>>>>>>>>>' + str(matricula))
					return {'retorno': 11, 'mensagem': 'Erro na consulta...'}	
				else:
					print('Tratar')
					
					if('Informe uma Matrícula ou CPF válido' in self.mensagem_erro):
						self.mensagem_erro = ""
						return {'retorno': 11, 'mensagem': 'Erro na consulta possivel beneficio novo...'}
					#self.driver.quit()
					
					#self.reabrir_tela_consulta()


			#self.reiniciar_browser()

	def consultar_cpf_matricula(self, cpf):

		try:
			self.selenium_helper.atribuir_valor_campo_driver('[name=value]', cpf)
			self.selenium_helper.clicar_elemento_driver('#buttonConsultarInss')
			time.sleep(2)
		except:
			return {'retorno': 11, 'mensagem': 'Erro na consulta...'}

		self.aguardar_loading_botao()

		try:
			matriculas_array_final = []
			matriculas = SeleniumActions(self.driver).retornar_opcoes_select('#mudarMatricula > div > div > select')

			if(matriculas):
				for matricula in matriculas: 
					array_matricula = matricula.text.split('/')
					numero_beneficio = array_matricula[0].replace('NB','').replace(' ','').replace('.','').replace('-','')
					especie_beneficio = array_matricula[1].split(' ')[2]
					consignavel = self.verifica_se_consignavel(int(especie_beneficio))
					matriculas_array_final.append([numero_beneficio,especie_beneficio,consignavel])

				return {
					"retorno": 'success',
					"mensagem": 'Benefícios encontrados.',
					"nome_beneficiario": self.selenium_helper.verificar_valor_campo_driver('[name=con_nome]'),
					"matriculas_array_final": json.dumps(matriculas_array_final)
				}	

			else:
				return {
					"retorno": 'alert',
					"mensagem": 'Sem beneficios vinculados ao CPF.',
					"nome_beneficiario":'',
					"matriculas_array_final": ''
				}	

		except:
			return {
				"retorno": 'alert',
				"mensagem": 'Sem beneficios vinculados ao CPF.',
				"nome_beneficiario":'',
				"matriculas_array_final": ''
			}

	def consultar_detalhamento(self):    
		seletor_detalhamento_atualizado = 'div.direita.fa.fa-check'
		detalhamento_atualizado = self.selenium_helper.buscar_quantidade_elemento(seletor_detalhamento_atualizado)

		if(detalhamento_atualizado == 1):
			return

		#seletor_detalhamento = '.verHiscred .fa-check:visible'
		#detalhamento = self.selenium_helper.buscar_quantidade_elemento(seletor_detalhamento)
		fechar_detalhamento = self.selenium_helper.buscar_quantidade_elemento(".fancybox-close")
		
		if fechar_detalhamento == 0:
			tentativas = 0

			self.selenium_helper.clicar_elemento_driver(".verHiscred")
			#while self.selenium_helper.buscar_quantidade_elemento(seletor_detalhamento) == 0:

			try:
				self.act.clicar_elemento('//*[@id="swal2-html-container"]/div/div/div[2]/a[1]', By.XPATH)	
			except:
				pass

			while fechar_detalhamento == 0:
				if tentativas > 15:
					print("Detalhamento possivelmente atualizado")
					return
					raise ConsultErrorException(
						message="Não foi possível concluir a busca, detalhamento indisponível!")

				time.sleep(2)
				tentativas += 1
				print(f"Aguardando Loading Detalhamento...{tentativas}")
				fechar_detalhamento = self.selenium_helper.buscar_quantidade_elemento(".fancybox-close")

			self.selenium_helper.clicar_elemento_driver(".fancybox-close")

	def extrair_dados_consulta(self):
		
		try:	
			credito_total = formatar_moeda(
				self.selenium_helper.verificar_valor_campo_driver('[name=con_valor_beneficio]')
			)
		except:
			print('Cookies vencidos...')
			mensagem = self.selenium_helper.verificar_texto_campo_jquery(".alert-danger span:visible")
			#pdb.set_trace()
			if mensagem == '':
				self.driver.delete_all_cookies()
				self.driver.quit()
				PromoBank().main()

		credito_total_liquido = formatar_moeda(
			self.selenium_helper.verificar_valor_campo_driver('[name=con_liquido]')
		)
		margem_disponivel = formatar_moeda(self.selenium_helper.verificar_valor_campo_driver('[name=con_margem_disponivel]'))
		
		if self.selenium_helper.buscar_quantidade_elemento('[name=parcela_rmc]') == 1:
			margem_disponivel_cartao = formatar_moeda(self.selenium_helper.verificar_valor_campo_driver('[name=parcela_rmc]'))
		else:
			try:
				margens = self.driver.execute_script("""return $('span:contains(\"Margem Disponível\")')""")
				margem_disponivel_cartao = formatar_moeda(margens[1].find_element_by_css_selector('input').get_attribute('value'))
			except:	
				margem_disponivel_cartao = 0

		cpf = self.selenium_helper.verificar_valor_campo_driver('[name=con_cpf]')
		especie_beneficio = self.selenium_helper.verificar_valor_campo_driver('[name=con_esp_beneficio]')

		data_nascimento = self.selenium_helper.verificar_valor_campo_driver(
			'[name=con_datanascimento]')
		data_nascimento = data_nascimento.split(' ')[0]
		data_nascimento = datetime.datetime.strptime(data_nascimento, r'%d/%m/%Y').strftime(r'%Y-%m-%d')

		banco = self.selenium_helper.verificar_valor_campo_driver(
			'[name=con_banco]')
		agencia = self.selenium_helper.verificar_valor_campo_driver(
			'[name=con_agencia]')
		tipo_conta = self.selenium_helper.verificar_valor_campo_driver(
			'[name=con_meio_pagamento]')
		conta = self.selenium_helper.verificar_valor_campo_driver(
			'[name=con_conta]')
		dib = self.selenium_helper.verificar_valor_campo_driver('[name=con_DIB]')
		
		if(dib!=''):
			dib = datetime.datetime.strptime(dib, r'%d/%m/%Y').strftime(r'%Y-%m-%d')

		uf = self.selenium_helper.verificar_valor_campo_driver('[name=con_uf]')

		if conta != '':
			digito_conta = conta[-1]
		else:
			digito_conta = 0
		
		competencia_detalhamento = self.selenium_helper.verificar_valor_campo_driver('#competenciaDetalhamento').split('/') 
		
		# - NO AUMENTO TROCAR OS 2 RESULTADOS NOS 2 IFS DE PARCELA AUMENTO

		array = ['87','88']
		porcentagem_aumento = 0.0475
		porcentagem_aumento_salario = 0.0475
		porcentagem_margem = 0.35

		if especie_beneficio in array:
			porcentagem_margem = 0.30

		if('ADQUIRIR' in competencia_detalhamento[0]): 
			
			try:
				credito_liquido = formatar_moeda(self.selenium_helper.verificar_valor_campo_driver('[name=con_liquido]'))
				parcela_aumento = credito_total_liquido * porcentagem_aumento * porcentagem_margem
			except:
				parcela_aumento = (credito_total * porcentagem_margem) - self.debito_total 			

			self.retorno.update({
				'retorno':1,
				'especieBeneficio': especie_beneficio,
				'cpf': cpf,
				'dataNascimento': data_nascimento,
				'banco': banco,
				'agencia': agencia,
				'tipoConta': tipo_conta,
				'conta': conta,
				'digitoConta': digito_conta,
				'creditoTotal': credito_total,
				'margemDisponivel': margem_disponivel,
				'margemDisponivelCartao': margem_disponivel_cartao,
				'dib':dib,
				'uf': uf,
				'parcelaAumento': parcela_aumento,
				'margemDisponivelReal': margem_disponivel,
			})
		else:
			try:
				ano_competencia = int(competencia_detalhamento[1])
				mes_competencia = int(competencia_detalhamento[0])
			except:
				ano_competencia = 2023
				mes_competencia = 12
				pass

			parcela_aumento = 0
			
			try:
				credito_liquido = formatar_moeda(self.selenium_helper.verificar_valor_campo_driver('[name=con_liquido]'))
				if(ano_competencia == 2025 and mes_competencia <= 3):
					#parcela_aumento = margem_disponivel
					if(credito_total <= 1413):
						parcela_aumento = credito_total_liquido * porcentagem_aumento * porcentagem_margem
						#credito_total = credito_total * (1+porcentagem_aumento)
					else:
						parcela_aumento = credito_total_liquido * porcentagem_aumento_salario * porcentagem_margem
						#credito_total = credito_total * (1+porcentagem_aumento_salario)

				elif(ano_competencia == 2024 and mes_competencia <= 12):
					if(credito_total <= 1412):
						parcela_aumento = credito_total_liquido * porcentagem_aumento * porcentagem_margem
						credito_total = credito_total * (1+porcentagem_aumento)
					else:
						parcela_aumento = credito_total_liquido * porcentagem_aumento_salario * porcentagem_margem
						credito_total = credito_total * (1+porcentagem_aumento_salario)

			except:
				if (ano_competencia == 2024 and mes_competencia <= 12):
					if(credito_total <= 1412):
						parcela_aumento = credito_total * porcentagem_aumento * porcentagem_margem
						credito_total = credito_total * (1+porcentagem_aumento)
					else:
						parcela_aumento = credito_total * porcentagem_aumento_salario * porcentagem_margem
						credito_total = credito_total * (1+porcentagem_aumento_salario)

				elif(ano_competencia == 2025 and mes_competencia <= 3):
					#parcela_aumento = margem_disponivel 
					if(credito_total <= 1413):
						parcela_aumento = credito_total * porcentagem_aumento * porcentagem_margem
						#credito_total = credito_total * (1+porcentagem_aumento)
					else:
						parcela_aumento = credito_total * porcentagem_aumento_salario * porcentagem_margem
						#credito_total = credito_total * (1+porcentagem_aumento_salario)


			dados = {
				'especieBeneficio': especie_beneficio,
				'cpf': cpf,
				'dataNascimento': data_nascimento,
				'banco': banco,
				'agencia': agencia,
				'tipoConta': tipo_conta,
				'conta': conta,
				'digitoConta': digito_conta,
				'creditoTotal': credito_total,
				'margemDisponivel': margem_disponivel,
				'margemDisponivelCartao': margem_disponivel_cartao,
				'dib':dib,
				'uf': uf,
				'parcelaAumento': parcela_aumento,
				'margemDisponivelReal': margem_disponivel,
			}
			
			self.retorno.update(dados)

	def extrair_refinanciamentos(self):
		refinanciamentos = []
		self.debito_total = 0

		#antigo
		#linhas_refinanciamento = self.driver.find_elements_by_css_selector('.gridContratos tbody tr')
		linhas_refinanciamento = self.driver.find_element(By.ID,'gridContratos').find_elements(By.TAG_NAME, "tr")
		
		try:
			for linha_refinanciamento in linhas_refinanciamento:
				
				#antigo
				#colunas = linha_refinanciamento.find_elements_by_css_selector('td')
				
				colunas = linha_refinanciamento.text.split('\n')
				
				if len(colunas) != 13:
					continue

				#tipo_contrato = colunas[0].get_attribute("innerHTML").strip()
				#tipo_contrato += colunas[1].get_attribute("innerHTML").strip()

				#if 'EMPRÉSTIMO CONSIGNADO' in tipo_contrato or 'PARCELA OCULTA' in tipo_contrato:
					
				banco = colunas[0]

				banco = re.split(r"\-", banco)

				numero_banco = banco[0].strip()
				nome_banco = banco[1].strip()
				
				data_inicio = formatar_data_banco_anomenor(colunas[2])
				data_fim= formatar_data_banco_anomenor(colunas[3])

				valor_total = formatar_moeda(colunas[4])
				saldo_devedor = formatar_moeda(colunas[5])

				valor_parcela = formatar_moeda(colunas[6])
				taxa_juros = formatar_porcentagem(colunas[7])
				
				parcelas_pag = colunas[8]
				parcelas_pagas = parcelas_pag.split('/')[0]
				prazo = int(colunas[9]) + int(parcelas_pagas)
				numero_contrato = colunas[10]

				refinanciamentos.append({
						'nomeBanco': nome_banco,
						'numeroBanco': numero_banco,
						'parcela': valor_parcela,
						'parcelasTotais': prazo,
						'parcelasPagas': parcelas_pagas,
						'taxaJurosFina': taxa_juros,
						'dataInicioContrato': data_inicio,
						'dataFimContrato': data_fim,
						'statusContrato': '',
						'parcelaEstimadaFinal': '',
						'valorPresenteInicial': valor_total,
						'saldoDevedorFinal': saldo_devedor,
						'numeroContrato': numero_contrato
					})

				print(refinanciamentos)
				
				print('----------------------')

				self.debito_total += valor_parcela
		except:
			pass

		self.retorno.update({
			'arrayParcelasRefin': refinanciamentos,
			'numeroEmprestimos': len(refinanciamentos)
		})

		#pdb.set_trace()

	def tratar_erros_consulta(self):
		mensagem_erro = self.selenium_helper.verificar_texto_campo_jquery(".alert-danger span:visible")
		self.mensagem_erro = mensagem_erro.strip()
		if mensagem_erro == "":
			try:
				#1751342260 exemplo
				time.sleep(2)
				if "DETECTADO UMA CONTRIBUIÇÃO SINDICAL" in self.selenium_helper.verificar_texto_campo_jquery(".alert-warning"):
					print("Detectada contribuicao sindical... Clicando na guia Contratos...")
					loc_consulta = '//*[@id="myTab4"]/li[1]'
					self.act.clicar_elemento(loc_consulta, By.XPATH)
					time.sleep(3)
					mensagem_erro = ""

			except:
				pass
		
		# if mensagem_erro == '':
		# 	try:
		# 		mensagem_erro = self.selenium_helper.verificar_texto_campo_jquery(".alert-danger").strip()
		# 	except:
		# 		pass
		
		if mensagem_erro == "":
			return


		print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<MENSAGEM ERRO >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print(mensagem_erro)
		print(self.matricula_consultar)

		erros_regex = [
			{
				'erro': r"NÃO ENCONTRADO MATRÍCULA PARA O CPF INFORMADO",
				'InfoNotFound': True
			}, {
				'erro': r"Informe uma Matrícula ou CPF válido",
				'IncorrectInfo': True
			}, {
				'erro': r"NÚMERO DA MATRICULA INSS NÃO ENCONTRADO",
				'InfoNotFound': True
			}, {
				'erro': r"NÚMERO DA MATRICULA INCORRETA",
				'IncorrectInfo': True
			}, {
				'erro': r"Não foi possível processar sua solicitação, tente novamente",
				'ConsultError': True
			}, {
				'erro': r"Por favor tente novamente dentro de alguns instantes",
				'ConsultError': True
			}, {
				'erro': r"CLIENTE NÃO ELEGÍVEL PARA EMPRÉSTIMO",
				'BeneficioCancelado': True
			},{
				'erro': r"Informe uma MatrÃ­cula ou CPF vÃ¡lido",
				'IncorrectInfo': True
			},{
				'erro': r"Limite de consulta diária atingido, aguarde alguns minutos e tente novamente.",
				'SiteLimitePesquisa': True
			},{
				'erro': r"Limite",
				'SiteLimitePesquisa': True
			},{
				'erro': r"Não foi possível retornar a informação",
				'ConsultError': True
			}

		]

		for erro_regex in erros_regex:
			regex = re.compile(erro_regex['erro'])
			erro_encontrado = regex.search(mensagem_erro)

			if not erro_encontrado:
				continue

			self.fechar_mensagem_erro()

			if 'InfoNotFound' in erro_regex:
				raise InfoNotFoundException(message="O Benefício não foi encontrado.")
			elif 'IncorrectInfo' in erro_regex:
				raise IncorrectInfoException(message="Número do benefício informado está incorreto.")
			elif 'BeneficioCancelado' in erro_regex:
				raise BeneficioCancelado(message="Benefício não pode realizar empréstimo.")
			elif 'SiteLimitePesquisa' in erro_regex:
				raise SiteLimitePesquisa(message="Site com limite de pesquisa. Aguardando pra reinciar...")
			elif 'ConsultError' in erro_regex:
				print("Não foi possível concluir a pesquisa, aguardando 60 segundos...")
				time.sleep(60)
				raise ConsultErrorException(message="Não foi possível concluir a busca, sistema fora do ar!")
			elif r'Seu acesso ao sistema de consulta foi ativado' in erro_regex:
				print("Não foi possível concluir a pesquisa, reiniciando a pesquisa, aguardando 60 segundos...")
				time.sleep(60)
				self.main()

		print("Erro, {}. Deseja continuar? r/p (reprovar/pular)".format(mensagem_erro))
		time.sleep(300)
		self.driver.quit()
		PromoBank().main()

	def fechar_mensagem_erro(self):
		style = self.selenium_helper.verificar_atributo_campo_jquery('#error', 'style')
		style = style.replace('display: inline;', 'display: none;')
		self.selenium_helper.atribuir_valor_atributo_jquery('#error', 'style', style)

	def aguardar_loading_botao(self):
		while self.selenium_helper.buscar_quantidade_elemento('.buttonConsultar .loadmask') >= 1:
			print("Aguardando Loading...")
			time.sleep(2)
	
	def reabrir_tela_consulta(self):
		try:
			self.driver.refresh()
		except Exception:
			return self.reabrir_tela_consulta()
		
		time.sleep(5)
		self.selecionar_aba_consulta()

	def processar_fila_reprovado_conferir(self):
		request_contratos = requests.get("https://emprestimofacil.co/web_admin/api/v1/contratos/reprovado-conferir/consulta-margem/?key=f689f1e12a0399fba803cb2365fc362f")

		try:
			if (request_contratos.status_code != 200):
				print("Erro na consulta de reprovado a conferir")
				raise Exception("Erro na consulta de reprovado a conferir")

			if (request_contratos.json()[0]['retorno'] != 1):
				print("Nenhum contrato para inserir")
				raise Exception("Nenhum contrato para inserir")
		except Exception as e:
			print(e)

		contratos = request_contratos.json()[1:]

		self.uconecte.atualizar_status_robo(self.id_robo)

		for contrato in contratos:
			try:
				# self.log.api_iniciar_log_robo(
				# 	idRobo=self.id_fila_reprovado_conferir,
				# 	idContrato=contrato['codigo_con']
				# )
				beneficio = contrato['matricula']

				if (len(beneficio) == 11 and beneficio[0] == '0'):
					beneficio = beneficio[1:]

				if(beneficio[0] == '0'):
					beneficio = beneficio[1:]

				print('Consultando contrato %s - beneficio: %s' % (contrato['codigo_con'],beneficio))
				retorno = self.consultar_matricula(beneficio,'reprovado_conferir')

				if 'margemDisponivel' not in retorno:
					retorno['retorno'] = 0
					retorno['margemDisponivel'] = ''

				dados = {
					"key": "f689f1e12a0399fba803cb2365fc362f",
					"retorno": retorno['retorno'],
					"mensagem": retorno['mensagem'],
					"codigoCon": contrato['codigo_con'],
					"margemDisponivel": retorno['margemDisponivel'],
					"margemDisponivelReal": retorno['margemDisponivelReal']
				}
				
				pool = Pool(10)
				pool.apply_async(requests.post("https://emprestimofacil.co/web_admin/api/v1/contratos/reprovado-conferir/atualiza-margem/", data=dados))

				if (request_contratos.status_code == 200):
					print('Contrato reprovado a conferir atualizado:'+contrato['codigo_con'])

				self.log.api_registrar_log_robo(
					log=f"Consulta finalizada com retorno: {retorno['retorno']}",
					status=2
				)
			except Exception as e:
				self.log.api_registrar_log_robo(
					log=f"ERRO: {e}",
					status=0
				)

	def verifica_se_consignavel(self,especie_beneficio):
	    switcher = {
	        1:'PENSAO PO MORTE DE TRABALHADOR RURAL',
			2:'PENSAO POR MORTE ACIDENTARIA-TRAB.RURAL',
			3:'PENSAO POR MORTE DE EMPREGADOR RURAL',
			4:'APOSENTADORIA POR INVALIDEZ-TRAB.RURAL',
			5:'APOSENT. INVALIDEZ ACIDENTARIA-TRAB.RUR.',
			6:'APOSENT INVALIDEZ EMPREGADOR RURAL',
			7:'APOSENTADORIA POR VELHICE-TRAB.RURAL',
			8:'APOSENT.PO RIDADE-EMPREGADOR RURAL',
			11:'RENDA MENSAL VITALÍCIA POR INVALIDEZ DO TRAB. RURAL (LEI No 6.179/74)',
			12:'AMPARO PREVIDENC. IDADE TRABALHADOR RURAL',
			19:'PENSAO DE ESTUDANTE(LEI7.004/82)',
			20:'PENSAO POR MORTEDE EX-DIPLOMATA',
			21:'PENSAO POR MORTE PREVIDENCIARIA',
			22:'PENSAO POR MORTE ESTATUTARIA',
			23:'PENSAO POR MORTE DE EX-COMBATENTE',
			24:'PENSAO ESPECIAL ATOINSTITUCIONAL',
			26:'PENSAO POR MORTE ESPECIAL',
			27:'PENSAO MORTE SERVIDOR PUBLICO FEDERAL',
			28:'PENSAO POR MORTE REGIME GERAL',
			29:'PENSAO POR MORTE EX-COMBATENTE MARITIMO',
			30:'RENDA MENSAL VITALÍCIA POR INVALIDEZ (LEI No 6.179/74)',
			32:'APOSENTADORIA INVALIDEZ PREVIDENCIARIA',
			33:'APOSENTADORIA INVALIDEZ AERONAUTA',
			34:'APOSENT .INVAL. EX-COMBATENTE MARITIMO',
			37:'APOSENTADORIA EXTRA NUMERARIO CAPIN',
			38:'APOSENT. EXTRANUM. FUNCIONARIO PUBLICO',
			40:'RENDA MENSAL VITALÍCIA POR IDADE',
			41:'APOSENTADORIA POR IDADE',
			42:'APOSENTADORIA POR TEMPO DE CONTRIBUIÇÃO',
			43:'APOSENT.POR TEMPO SERVICOEX-COMBATENTE',
			44:'APOSENTADORIA ESPECIAL DE AERONAUTA',
			45:'APOSENT. TEMPO SERVICO JORNALISTA',
			46:'APOSENTADORIA ESPECIAL',
			49:'APOSENTADORIA ORDINARIA',
			51:'APOSENT INVALIDEZ EXTINTO PLANO BASICO',
			52:'APOSENT. IDADE EXTINTO PLANO BASICO',
			54:'PENSAO ESPECIAL VITALICIA-LEI9793/99',
			55:'PENSAO POR MORTEEXTINTO PLANO BASICO',
			56:'PENSAO VITALICIA SINDROME TALIDOMIDA',
			57:'APOSENT.TEMPO DE SERVICO DE PROFESSOR',
			58:'APOSENTADORIA DE ANISTIADOS',
			59:'PENSAO POR MORTE DE ANISTIADOS',
			60:'PENSAO ESPECIALPORTADORDESIDA',
			72:'APOSENT. TEMPO SERVICO-LEI D GUERRA',
			78:'APOSENTADORIA IDADE-LEI DE GUERRA',
			81:'APOSENTADORIA COMPULSORIA EX-SASSE',
			82:'APOSENTADORIA TEMPO DE SERVICO EX-SASSE',
			83:'APOSENTADORIA POR INVALIDEZ EX-SASSE',
			84:'PENSAO PO MORTE EX-SASSE',
			87:'AMPARO ASSISTENCIAL AO DEFICIENTE',
			88:'AMPARO ASSISTENCIAL AO IDOSO',
			89:'PENSAO ESP.VITIMAS HEMODIALISE-CARUARU',
			92:'APOSENT.INVALIDEZ ACIDENTE TRABALHO',
			93:'PENSAOPORMORTE ACIDENTE DO TRABALHO',
			96:'PENSÃO ESPECIAL PARA AS PESSOAS ATINGIDAS PELA HANSENÍASE'
	    }
	    return switcher.get(especie_beneficio, "Não consignável")

class InfoNotFoundException(Exception):
	def __init__(self, message):
		super().__init__()
		self.message = message


class IncorrectInfoException(Exception):
	def __init__(self, message):
		super().__init__()
		self.message = message


class ConsultErrorException(Exception):
	def __init__(self, message):
		super().__init__()
		self.message = message


class BeneficioCancelado(Exception):
	def __init__(self, message):
		super().__init__()
		self.message = message

class SiteLimitePesquisa(Exception):
	def __init__(self, message):
		super().__init__()
		self.message = message


if __name__ == "__main__":
	run = PromoBank()
	run.main()
