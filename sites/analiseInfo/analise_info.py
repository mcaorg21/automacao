from json_encoder import json

import time
import re
import pyautogui
import requests
import sys
import os
import datetime
import pdb

from tkinter import Tk

from sites.core import pyautogui_helper
from sites.core.uconecte import Uconecte

class AnaliseInfo():
	def __init__(self):
		self.caminho_base = os.getcwd().replace("\\", "/")
		self.imagens_path = self.caminho_base+"/sites/analiseInfo/imagens/%s"

		self.id_robo = 5
		self.tkinterface = Tk()
		self.width, self.height = pyautogui.size()
		self.config_imprimir = ((self.width/2), 0, self.width, (self.height/2))

		width_20_percent = self.width * 0.2
		self.config_area = ((width_20_percent), 0, (self.width - width_20_percent), (self.height/2))
		self.uconecte = Uconecte()

	def main(self):
		self.processar_fila_solicitacoes()

	def atualizar_pagina(self):
		pyautogui.click(800, 56)
		time.sleep(1)
		pyautogui.typewrite("https://app.analise.info/#/home")
		pyautogui.press(['enter'])
		time.sleep(40)
	
	def open_site(self, url):
		btn_aba_analise_info = pyautogui_helper.find_elements_on_screen(
			files=[self.imagens_path % ('04_aba.png'), self.imagens_path % ('05_aba.png')],
			click=True,
			search=True,
			search_wait=3,
			limit=5
		)
		
		if btn_aba_analise_info:
			return

		btn_nova_aba = self.find_element_on_screen([self.imagens_path % ('01_new_tab.png'), self.imagens_path % ('02_new_tab.png')])

		if (btn_nova_aba == False):
			print('this is the end')

		pyautogui.click(btn_nova_aba.x, btn_nova_aba.y)

		time.sleep(1)
		pyautogui.typewrite(url)
		
		time.sleep(2)
		pyautogui.press(['enter'])
		
	def login_sistema(self):
		time.sleep(5)

		btn_login = self.find_element_on_screen([self.imagens_path % ('btn_login.png')])

		if (btn_login != False):
			pyautogui.click(btn_login.x, btn_login.y)
					
		time.sleep(5)
		print('Logado no sistema')

	def ir_para_beneficio(self, beneficio):
		pyautogui.click(100, 100)
		pyautogui.hotkey('del')
		pyautogui.hotkey('ctrl', 'a')

		pyautogui.typewrite(beneficio, interval=0.02)
		time.sleep(1)

		pyautogui.press('enter')
		time.sleep(3)

	def tratar_mensagens_sistema(self, beneficio):
		self.click_center_of_screen()
		text_screen = self.copy_text_screen()
		time.sleep(3)
		
		while (re.compile(r'Buscando\.{3}').search(text_screen) is not None):
			print('Selecionando o texto')
			text_screen = self.copy_text_screen()
			time.sleep(2)

		if (re.compile(r'Limite de consultas diarias atingida').search(text_screen) is not None):
			self.tkinterface.withdraw()
			email = {
				'titulo': 'Limite de consultas alcançado',
				'tituloInterno': 'Trocar conta do AnaliseInfo',
				'mensagem': 'Altere a conta de usuário que está vinculada no AnaliseInfo'
			}

			self.enviar_email(dados_email=email)
			input('Aguardando troca de usuário... Ao realizar a troca pressione "ENTER"')
			return self.consultar_beneficio(beneficio)

		if (re.compile(r'Desculpe, nada consta no banco de dados').search(text_screen) is not None):
			raise InfoNotFoundException(message="Nada consta no banco de dados!")

		if (re.compile(r'CPF não encontrado').search(text_screen) is not None):
			raise InfoNotFoundException(message="O Benefício não foi encontrado.")

		if (re.compile(r'O número informado não é um NB ou CPF válido.').search(text_screen) is not None):
			raise IncorrectInfoException(message="Número do benefício informado está incorreto. Número informado por você: "+beneficio)

		if (re.compile(r'O número informado é válido como NB e CPF').search(text_screen) is not None):
			raise InfoNotFoundException(message="O número informado é válido como NB e CPF.")

		if (re.compile(r'Tente novamente mais tarde').search(text_screen) is not None):
			time.sleep(10)
			return self.consultar_beneficio(beneficio)	
	
	def consultar_beneficio(self, beneficio):
		if (type(beneficio) != 'str'):
			beneficio = str(beneficio)

		if (len(beneficio) > 10 or len(beneficio) == 0):
			return {'retorno': 4, 'mensagem': 'Número do benefício informado está incorreto. Ele deve ter 10 números. Benefício informado por você: '+beneficio}

		self.ir_para_beneficio(beneficio)
		self.find_element_on_screen(files=[self.imagens_path % ('btn_nb_01.png')], click=True)

		try:
			print("Tratando mensagens do sistema")
			self.tratar_mensagens_sistema(beneficio)
			
			print("Montando retorno do HTML")
			retorno = self.buscar_dados_html()

			self.find_element_on_screen(files=[self.imagens_path % ('btn_fechar_abas.png')], click=True)

			return retorno
		except InfoNotFoundException as e:
			return {'retorno': 3, 'mensagem': e.message}
		except IncorrectInfoException as e:
			return {'retorno': 4, 'mensagem': e.message}
		except ConsultErrorException as e:
			return {'retorno': 11, 'mensagem': e.message}
		except Exception as e:
			print(e)
			self.atualizar_pagina()
			time.sleep(5)
			return self.consultar_beneficio(beneficio)

	def find_element_on_screen(self, files, region=False, click=False):
		for file in files:
			try:
				if (region):
					element = pyautogui.locateOnScreen(file, region=region, grayscale=True, confidence=0.9)
				else:
					element = pyautogui.locateOnScreen(file, grayscale=True, confidence=0.9)

				element = pyautogui.center(element)

				if (click):
					pyautogui.click(element.x,element.y)

				return element
			except Exception as e:
				print(e)
				print(file)

		return False

	def click_center_of_screen(self):
		pyautogui.moveTo((self.width/2), (self.height/3))
		pyautogui.click()
		time.sleep(1)

	def copy_text_screen(self, pdf=False):
		time.sleep(1)
		pyautogui.hotkey('ctrl', 'a')
		time.sleep(1)
		pyautogui.moveTo((self.width/2), (self.height/3))
		pyautogui.click(button='right')
		pyautogui.press('down')

		if (pdf):
			pyautogui.press('down')

		pyautogui.press('enter')
		
		try:
			result = self.tkinterface.selection_get(selection = "CLIPBOARD")
			self.tkinterface.withdraw()
		except Exception as e:
			print(e)
			return self.copy_text_screen(pdf)
		
		if (result == ''):
			return self.copy_text_screen(pdf)
		
		return result

	def buscar_dados_pdf(self):
		quantidade_buscas = 0
		btn_imprimir = self.find_element_on_screen([self.imagens_path % ('btn_imprimir_02.png'), self.imagens_path % ('btn_imprimir_01.png')], self.config_imprimir)
		while (btn_imprimir == False):
			btn_imprimir = self.find_element_on_screen([self.imagens_path % ('btn_imprimir_02.png'), self.imagens_path % ('btn_imprimir_01.png')], self.config_imprimir)
			print('Buscando confirmação visual do imprimir')
			quantidade_buscas+=1
			if (quantidade_buscas > 15):
				raise ConsultErrorException(message="Não foi possível concluir a pesquisa")

		pyautogui.click(btn_imprimir.x, btn_imprimir.y)

		quantidade_buscas = 0
		area_vazia = self.find_element_on_screen([self.imagens_path % ('area_vazia_pdf.png'), self.imagens_path % ('area_vazia_pdf_01.png')], self.config_area)
		while (area_vazia == False):
			area_vazia = self.find_element_on_screen([self.imagens_path % ('area_vazia_pdf.png'), self.imagens_path % ('area_vazia_pdf_01.png')], self.config_area)
			print('Buscando confirmação visual da área vazia')
			quantidade_buscas+=1
			if (quantidade_buscas > 15):
				raise ConsultErrorException(message="Não foi possível concluir a pesquisa")

		pyautogui.moveTo(area_vazia.x, area_vazia.y)
		pyautogui.click()

		text = self.copy_text_screen(pdf=True)
		retorno = self.montar_retorno_consulta(text)
		return retorno

	def montar_retorno_consulta(self, text):
		lines = text.splitlines()

		retorno = {'arrayParcelasRefin': []}

		refinanciamentos = False

		i = 0
		while (i < len(lines)):
			if (len(re.compile(r'Espécie').findall(lines[i])) > 0):
				retorno['especieBeneficio'] = re.sub(r'\D', '', lines[i])

			elif (len(re.compile(r'CPF').findall(lines[i]))):
				retorno['cpf'] = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\-\d{1,2})', lines[i]).group(1)

			elif (len(re.compile(r'Nascimento').findall(lines[i]))):
				retorno['dataNascimento'] = lines[i].replace('Nascimento: ', '')

			elif (len(re.compile(r'Banco: ').findall(lines[i]))):
				retorno['banco'] = lines[i].replace('Banco: ', '')

			elif (len(re.compile(r'Agência: ').findall(lines[i]))):
				retorno['agencia'] = re.sub(r'\D', '', lines[i].replace('Agência: ', ''))

			elif (len(re.compile(r'Meio Pagamento: ').findall(lines[i]))):
				retorno['tipoConta'] = lines[i].replace('Meio Pagamento: ', '')

			elif (len(re.compile(r'Conta Corrente: ').findall(lines[i]))):
				retorno['conta'] = re.sub(r'\D', '', lines[i])
				if (len(retorno['conta']) > 0):
					retorno['digitoConta'] = retorno['conta'][-1]
					retorno['conta'] = retorno['conta'][:-1]

			elif (len(re.compile(r'Histórico de contratos atualizado').findall(lines[i])) > 0):
				refinanciamentos = True
			
			elif (len(re.compile(r'MR BASE DE CÁLCULO DA MARGEM CONSIGNÁVEL').findall(lines[i])) > 0):
				margens = lines[i+1].replace('R$ ', '').split(' ')
				retorno['creditoTotal'] = self.converter_moeda(margens[1])
				retorno['margemDisponivel'] = self.converter_moeda(margens[2])
				retorno['margemDisponivelCartao'] = self.converter_moeda(margens[3])

			elif (re.compile(r'Cartão RMC').search(lines[i]) is not None or re.compile(r'Desconto\(s\) do Cartão').search(lines[i]) is not None or re.compile(r'Não possui contratos ativos').search(lines[i])):
				refinanciamentos = False

			if (refinanciamentos and re.compile(r'Histórico de contratos atualizado').search(lines[i]) is None and re.compile(r'Contrato Banco Tipo').search(lines[i]) is None):
				try:
					refinanciamento = {
						'nomeBanco': re.search(r'( \d{1,3}.+) Empréstimo', lines[i]).group(1).strip(),
						'parcelasTotais': re.search(r'(\d{1,2} Meses)', lines[i]).group(1).replace(' Meses', ''),
						'dataInicioContrato': '',
						'dataInicioDesconto': '',
						'statusContrato': '',
						'taxaJurosFina': '',
						'parcelaEstimadaFinal': ''
					}
				except AttributeError:
					continue

				linha_completa = lines[i].replace(refinanciamento['nomeBanco'], '').replace('R$ ', '').replace(' Meses', '')
				refin_split = linha_completa.split(' ')
				refinanciamento['valorPresenteInicial'] = self.converter_moeda(refin_split[-6])
				refinanciamento['numeroBanco'] = re.sub(r'\D', '', refinanciamento['nomeBanco'])
				refinanciamento['parcela'] = self.converter_moeda(refin_split[-3])
				refinanciamento['parcelasPagas'] = refin_split[-2] # Penúltima coluna
				refinanciamento['saldoDevedorFinal'] = self.converter_moeda(refin_split[-1]) # Última coluna

				retorno['arrayParcelasRefin'].append(refinanciamento)

			i+=1

		if ('cpf' not in retorno or 'especieBeneficio' not in retorno):
			return {'retorno': 3, 'mensagem': 'Não possui informações pessoais do cliente na consulta'}

		if ('creditoTotal' not in retorno):
			return {'retorno': 3, 'mensagem': 'Não possui informações de margem do cliente'}

		retorno['retorno'] = 1
		retorno['mensagem'] = '--Consulta realizada com sucesso! Funcao 6'
		retorno['numeroEmprestimos'] = len(retorno['arrayParcelasRefin'])
		
		return retorno

	def buscar_dados_html(self):
		retorno = {'arrayParcelasRefin': []}
		retorno = self.extrair_informacoes_dados_pessoais(retorno)
		retorno = self.extrair_informacoes_contratos(retorno)
		
		retorno['retorno'] = 1
		retorno['mensagem'] = '--Consulta realizada com sucesso! Funcao 6'
		retorno['numeroEmprestimos'] = len(retorno['arrayParcelasRefin'])
		return retorno

	def extrair_informacoes_dados_pessoais(self, retorno):
		self.click_center_of_screen()
		text = self.copy_text_screen()
		lines = text.splitlines()
		extracao = False
		dados_bancarios = False

		for index, line in enumerate(lines):
			if re.compile(r'Simulações').search(line) is not None: extracao = True
			if re.compile(r'Dados Bancários').search(line) is not None: dados_bancarios = True
			if extracao == False: continue

			try: 
				next_line = lines[index+1]
			except Exception: 
				pass

			if (re.compile(r'Espécie').search(line) is not None):
				retorno['especieBeneficio'] = re.sub(r'\D', '', next_line)

				if (retorno['especieBeneficio'] == ''):
					retorno['especieIntegra'] = next_line

			elif (re.compile(r'CPF').search(line) is not None):
				try:
					retorno['cpf'] = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\-\d{1,2})', next_line).group(1)
				except AttributeError:
					raise InfoNotFoundException(message="Não possui informações pessoais do cliente na consulta")

			elif (re.compile(r'Nascimento\t').search(line) is not None):
				retorno['dataNascimento'] = next_line

			elif (dados_bancarios and re.compile(r'ID Banco').search(line) is not None):
				retorno['banco'] = next_line

			elif (dados_bancarios and re.compile(r'ID Ag\. Banco').search(line) is not None):
				retorno['agencia'] = re.sub(r'\D', '', next_line)

			elif (dados_bancarios and re.compile(r'Meio Pagamento').search(line) is not None):
				retorno['tipoConta'] = next_line

			elif (dados_bancarios and re.compile(r'Conta Corrente').search(line) is not None):
				retorno['conta'] = re.sub(r'\D', '', next_line)
				if (len(retorno['conta']) > 0):
					retorno['digitoConta'] = retorno['conta'][-1]
					retorno['conta'] = retorno['conta'][:-1]

		if ('especieIntegra' in retorno):
			save_json(data=retorno, file=self.caminho_base + '/sites/analiseInfo/data.json')
			retorno.pop('especieIntegra')

		if ('cpf' not in retorno or 'especieBeneficio' not in retorno):
			raise InfoNotFoundException(message="Não possui informações pessoais do cliente na consulta")

		if (retorno['especieBeneficio'] == ''):
			raise InfoNotFoundException(message="Não possui informações pessoais do cliente na consulta")

		return retorno

	def extrair_informacoes_contratos(self, retorno):
		self.find_element_on_screen(files=[self.imagens_path % ('01_aba_dados_contrato.png'), self.imagens_path % ('02_aba_dados_contrato.png')], click=True)
		time.sleep(2)
		self.click_center_of_screen()
		text = self.copy_text_screen()
		lines = text.splitlines()

		extracao = False
		refinanciamentos = False

		for index, line in enumerate(lines):
			if re.compile(r'Simulações').search(line) is not None: extracao = True
			if extracao == False: continue
			if re.compile(r'Histórico de contratos atualizado').search(line) is not None: refinanciamentos = True
			
			if (line == 'MR'):
				retorno['creditoTotal'] = self.converter_moeda(lines[index+3].replace('R$ ', ''))
				retorno['margemDisponivel'] = self.converter_moeda(lines[index+5].replace('R$ ', ''))
				if (lines[index+8] == "---"):
					retorno['margemDisponivelCartao'] = 0.00
				else:
					retorno['margemDisponivelCartao'] = self.converter_moeda(lines[index+7].replace('R$ ', ''))

			elif (re.compile(r'Cartão RMC').search(line) is not None or re.compile(r'Desconto\(s\) do Cartão').search(line) is not None or re.compile(r'Não possui contratos ativos').search(line)):
				refinanciamentos = False

			if (refinanciamentos):
				try:
					refinanciamento = {
						'nomeBanco': re.search(r'(\t\d{1,3}.+)\tEMPRÉSTIMO', line).group(1).strip(),
						'parcelasTotais': re.search(r'(\d{1,2} Meses)', line).group(1).replace(' Meses', ''),
						'dataInicioContrato': '',
						'dataInicioDesconto': '',
						'statusContrato': '',
						'taxaJurosFina': '',
						'parcelaEstimadaFinal': ''
					}
				except AttributeError:
					continue

				linha_completa = line.replace(refinanciamento['nomeBanco'], '').replace('R$ ', '').replace(' Meses', '')
				refin_split = linha_completa.split('\t')

				refinanciamento['numeroBanco'] = re.sub(r'\D', '', refinanciamento['nomeBanco'])
				refinanciamento['valorPresenteInicial'] = self.converter_moeda(refin_split[-7])
				refinanciamento['parcela'] = self.converter_moeda(refin_split[-4])
				refinanciamento['parcelasPagas'] = refin_split[-3]
				refinanciamento['saldoDevedorFinal'] = self.converter_moeda(refin_split[-2])

				retorno['arrayParcelasRefin'].append(refinanciamento)

		if ('creditoTotal' not in retorno):
			raise InfoNotFoundException(message='Não possui informações de margem do cliente')

		return retorno

	def escolher_fila(self, tipo_consulta):
		data_hora = datetime.datetime.now()
		print('Nenhuma proposta na fila %s' % (tipo_consulta))

		self.atualizar_pagina()
		time.sleep(5)

		novo_tipo_consulta = ''

		if (tipo_consulta == 'inss'):
			novo_tipo_consulta = 'retencao'
		elif (tipo_consulta == 'retencao' and (data_hora.weekday() >= 0 and data_hora.weekday() < 5) and (data_hora.hour > 8 and data_hora.hour < 19)):
			novo_tipo_consulta = 'reprovado_conferir'
			
		if (novo_tipo_consulta == ''):
			novo_tipo_consulta = 'inss'

		print('Processando fila %s' % (novo_tipo_consulta))
		return novo_tipo_consulta

	def processar_fila_solicitacoes(self, tipo_consulta='inss'):
		request_solicitacoes = requests.get(
			"https://uconecte.me/api/v1/solicitacoes/%s?key=f689f1e12a0399fba803cb2365fc362f" % (tipo_consulta))
		
		if (request_solicitacoes.status_code != 200):
			return (json.dumps({"tipo": "alert", "mensagem": request_solicitacoes.json()['mensagem']}))

		solicitacoes = request_solicitacoes.json()['solicitacoes']
		self.uconecte.atualizar_status_robo(self.id_robo)

		if (len(solicitacoes) == 0):
			novo_tipo_consulta = self.escolher_fila(tipo_consulta)
			
			if (novo_tipo_consulta == 'reprovado_conferir'):
				return self.processar_fila_reprovado_conferir()
			
			return self.processar_fila_solicitacoes(novo_tipo_consulta)

		self.open_site("https://app.analise.info/")
		self.login_sistema()

		for solicitacao in solicitacoes:
			retorno = self.consultar_beneficio(solicitacao['matricula'])

			if (type(retorno) != 'str'):
				retorno = json.dumps(retorno)

			dados = {
				"consultaBeneficio": retorno, 
				"idPessoa": solicitacao['fk_idPessoa'],
				"idSolicitacao": solicitacao['idSolicitacao'], 
				"idPerfilPessoa": solicitacao['fk_idPerfil_pessoa']
			}

			# Atualização da solicitação
			request_consulta = requests.post(
				"https://uconecte.me/api/v1/consultas/inss", data=dados)

			if (request_consulta.status_code != 201):
				solicitacao['filename'] = "consultaAnaliseInfo"
				requests.post(
					"https://uconecte.me/api/v1/logs?key=f689f1e12a0399fba803cb2365fc362f", data=solicitacao)
				input('Erro na consulta - Confira o LOG')
			else:
				if (solicitacao['fk_idCategoria'] == '1'):
					dados_calcular = {
						'area': 'darlene',
						'idSolicitacao': solicitacao['idSolicitacao'],
						'idPerfilPessoa': solicitacao['fk_idPerfil_pessoa'],
						'idProdutoWebAdmin': 3,
						'idCategoria': solicitacao['fk_idCategoria'],
						'idadePessoa': solicitacao['idadePessoa'],
						'idPessoa': solicitacao['fk_idPessoa'],
						'cidade': solicitacao['fk_idCidade'],
						'estado': solicitacao['fk_idEstado'],
						'valor': solicitacao['valorSelecionado'],
						'parcelas': solicitacao['parcelaSelecionada'],
						'subOrgao': solicitacao['con_idOrgao'],
						'margem': solicitacao['margem']
					}
					request_calcular = requests.post(
						"https://uconecte.me/api/calcular/emprestimo_novo", data=dados_calcular)
					print(request_calcular.text)
				elif (solicitacao['fk_idCategoria'] == '5'):
					dados_calcular = {
						'idSolicitacao': solicitacao['idSolicitacao'],
						'idPerfilPessoa': solicitacao['fk_idPerfil_pessoa'],
						'idCategoria': solicitacao['fk_idCategoria'],
						'idadePessoa': solicitacao['idadePessoa'],
						'idPessoa': solicitacao['fk_idPessoa']
					}
					request_calcular = requests.post(
						"https://uconecte.me/api/calcular/cartao_consignado", data=dados_calcular)
					print(request_calcular.text)

		return self.processar_fila_solicitacoes()

	def processar_fila_reprovado_conferir(self):
		request_contratos = requests.get(
			"https://emprestimofacil.co/web_admin/api/v1/contratos/reprovado-conferir/consulta-margem/?key=f689f1e12a0399fba803cb2365fc362f")

		try:
			if (request_contratos.status_code != 200):
				print("Erro na consulta de reprovado a conferir")
				raise Exception("Erro na consulta de reprovado a conferir")

			if (request_contratos.json()[0]['retorno'] != 1):
				print("Nenhum contrato para inserir")
				raise Exception("Nenhum contrato para inserir")
		except Exception:
			return self.processar_fila_solicitacoes('inss')
			
		contratos = request_contratos.json()[1:]
		self.open_site("https://app.analise.info/")
		self.uconecte.atualizar_status_robo(self.id_robo)

		for contrato in contratos:
			beneficio = contrato['matricula']
			
			if (len(beneficio) == 11 and beneficio[0] == '0'):
				beneficio = beneficio[1:]

			print('Consultando beneficio: %s' % (beneficio))
			retorno = self.consultar_beneficio(beneficio)

			# Atualização dos dados do contrato
			if (retorno['retorno'] == 3):
				retorno['margemDisponivel'] = ''
			
			dados = {
				"key": "f689f1e12a0399fba803cb2365fc362f",
				"retorno": retorno['retorno'], 
				"mensagem": retorno['mensagem'], 
				"codigoCon": contrato['codigo_con'], 
				"margemDisponivel": retorno['margemDisponivel']
			}
			
			requests.post(
				"https://emprestimofacil.co/web_admin/api/v1/contratos/reprovado-conferir/atualiza-margem/", data=dados)

			if (request_contratos.status_code == 200):
				print('Contrato reprovado a conferir atualizado:'+contrato['codigo_con'])

		return self.processar_fila_solicitacoes('inss')

	def converter_moeda(self, texto):
		return float(texto.replace('.', '').replace(',', '.'))

	def enviar_email(self, dados_email):
		request_email = requests.post('https://uconecte.me/api/v1/logs/email?key=f689f1e12a0399fba803cb2365fc362f', data=dados_email)
		print(request_email.text)

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

def save_json(data, file="data.json"):
	with open(file) as dataJson:
		info = json.load(dataJson)

	info.append(data)
	with open(file, mode='w') as f:
		f.write(json.dumps(info, indent=2))
