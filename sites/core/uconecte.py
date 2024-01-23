import requests

class Uconecte():
	def __init__(self, id_banco=False):
		self.url = "https://app.emprestimofacil.com/api/v1/{}"
		self.api_key = "f689f1e12a0399fba803cb2365fc362f"
		self.id_banco = id_banco

	def atualizar_status_robo(self, id_robo):
		url_status = self.url.format("robos/status/{}?key={}".format(id_robo, self.api_key))
		request_status_robo = requests.get(url_status)

		if request_status_robo.status_code != 200:
			print("Não foi possível salvar o status do robô. Verifique o que aconteceu!")

		print("Status do robô atualizado com sucesso!")

	def inserir_historico_solicitacao(self, id_solicitacao, mensagem):
		historico = {
			"mensagem": mensagem
		}

		request_inserir_historico = requests.post(
			self.url.format("solicitacoes/{}/historico?key={}".format(
				id_solicitacao, self.api_key)),
			data=historico
		)
		
		if request_inserir_historico.status_code != 200:
			print(request_inserir_historico.text)
			input("Não foi possível inserir o histórico. Verifique o que aconteceu!")

	def inserir_bloqueio_pessoa(self, id_pessoa):
		bloqueio = {
			"idBanco": self.id_banco
		}

		request_inserir_bloqueio = requests.post(
			self.url.format("pessoas/{}/bloqueio?key={}".format(
				id_pessoa, self.api_key
			)),
			data=bloqueio
		)

		if request_inserir_bloqueio.status_code != 201:
			print(request_inserir_bloqueio.text)
			input("Não foi possível inserir um novo bloqueio. Verifique o que aconteceu!")

	def inserir_consulta_inss(self, dados_consulta):
		request_consulta = requests.post(
                    self.url.format("consultas/inss"), data=dados_consulta)

		if (request_consulta.status_code != 201):
			print(request_consulta.text)
			input('Erro na consulta - Confira o LOG')
			raise Exception("Não foi possível salvar a consulta do INSS")

	def inserir_consulta(self, dados_consulta, slug):
		request_consulta = requests.post(
			self.url.format(f"consultas/{slug}"), data=dados_consulta)

		if request_consulta.status_code != 201:
			print(request_consulta.text)
			input('Erro na consulta - Confira o LOG')
			raise Exception(f"Não foi possível salvar a consulta do {slug}")

	def calcular_financiamento(self, solicitacao, status_solicit=False):
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
			'margem': solicitacao['margem'],
			'retorno': None,
			'mensagem': None
		}
		if status_solicit:
			dados_calcular['retorno'] = solicitacao['retorno']
			dados_calcular['mensagem'] = solicitacao['mensagem']

		request_calcular = requests.post("https://app.emprestimofacil.com/api/calcular/emprestimo_novo", data=dados_calcular)
		print(request_calcular.text)
	
	def calcular_financiamento_aumento_margem(self, solicitacao, status_solicit=False):
		dados_calcular = {
			'area': 'darlene',
			'idSolicitacao': solicitacao['idSolicitacao'],
			'idPerfilPessoa': solicitacao['fk_idPerfil_pessoa'],
			'idProdutoWebAdmin': 5,
			'idCategoria': solicitacao['fk_idCategoria'],
			'idadePessoa': solicitacao['idadePessoa'],
			'idPessoa': solicitacao['fk_idPessoa'],
			'cidade': solicitacao['fk_idCidade'],
			'estado': solicitacao['fk_idEstado'],
			'valor': solicitacao['valorSelecionado'],
			'parcelas': solicitacao['parcelaSelecionada'],
			'subOrgao': solicitacao['con_idOrgao'],
			'margem': solicitacao['margem'],
			'retorno': None,
			'mensagem': None
		}
		if status_solicit:
			dados_calcular['retorno'] = solicitacao['retorno']
			dados_calcular['mensagem'] = solicitacao['mensagem']

		request_calcular = requests.post("https://app.emprestimofacil.com/api/calcular/aumento_inss", data=dados_calcular)
		print(request_calcular.text)

	def calcular_cartao_consignado(self, solicitacao, status_solicit=False):
		dados_calcular = {
			'area': 'darlene',
			'idSolicitacao': solicitacao['idSolicitacao'],
			'idPerfilPessoa': solicitacao['fk_idPerfil_pessoa'],
			'idCategoria': solicitacao['fk_idCategoria'],
			'idadePessoa': solicitacao['idadePessoa'],
			'idPessoa': solicitacao['fk_idPessoa']
		}

		if status_solicit:
			dados_calcular['retorno'] = solicitacao['retorno']
			dados_calcular['mensagem'] = solicitacao['mensagem']

		request_calcular = requests.post("https://app.emprestimofacil.com/api/calcular/cartao_consignado", data=dados_calcular)
		print(request_calcular.text)

	# Realiza o calculo de todos os refinanciamentos de uma solicitação
	def calcular_refinanciamento(self, refinanciamentos, solicitacao):
		if len(refinanciamentos) > 0:
			for refinanciamento in refinanciamentos:
				dados_calcular = {
					'tipoOferta': 2,
					'solicitacao': solicitacao['idSolicitacao'],
					'usuarioNegociacao': 16332,
					'banco': self.id_banco,
					'valor': refinanciamento['valorLiberado'],
					'saldoDevedor': refinanciamento['saldoDevedor'],
					'prazo': refinanciamento['prazo'],
					'parcela': refinanciamento['valorParcela']
				}

				request_calcular_refinanciamento = requests.post(
					"https://app.emprestimofacil.com/api/calcular/refinanciamento", data=dados_calcular)

				if request_calcular_refinanciamento.status_code != 200:
					print(request_calcular_refinanciamento.text)
					input(
						'Não foi possível calcular o refinanciamento. Verifique o que aconteceu!')
		else:
			dados_calcular = {
				'solicitacao': solicitacao['idSolicitacao'],
			}

			request_calcular_refinanciamento = requests.post("https://app.emprestimofacil.com/api/calcular/finalizar_solicitacao", data=dados_calcular)
			print(request_calcular_refinanciamento.text)
			if request_calcular_refinanciamento.status_code != 200:
				print(request_calcular_refinanciamento.text)
				input('Não foi possível calcular o refinanciamento. Verifique o que aconteceu!')


	def atualizar_contrato(self, codigo_contrato, dados):
		request_put_contrato = requests.put(
			self.url.format("contratos/{}?key={}".format(codigo_contrato, self.api_key)), data=dados
		)

		if (request_put_contrato.status_code == 200):
			print('Contrato %s atualizado!' % (codigo_contrato))
		else:
			print('Erro: %s na atualização do contrato %s , provavelmente deverá realizar nova tratativa no arquivo controllers/api/v1/Contratos.php' %
			      (request_put_contrato.text, codigo_contrato))
			input("Verifique o que aconteceu!")

	def buscar_informacoes_contrato(self, codigo_contrato, return_campos=False, return_contrato=False):
		request_dados_contrato = requests.get(
			self.url.format("contratos/{}/informacoes?key={}".format(codigo_contrato, self.api_key))
		)

		if (request_dados_contrato.status_code != 200):
			self.atualizar_contrato(
				codigo_contrato, {
					'mensagem': 'Dados não encontrados'
				}
			)

			print("Resposta: {}; Código: {}".format(request_dados_contrato.text, request_dados_contrato.status_code))
			raise Exception("Não foi possível buscar os dados do contrato")

		campos = request_dados_contrato.json()['campos']
		dados_contrato = request_dados_contrato.json()['dadosContrato']

		if return_campos:
			return campos
		elif return_contrato:
			return dados_contrato
		else:
			return campos, dados_contrato

	def inserir_ofertas_crm(self, consulta, pessoa):
		if len(consulta['refinanciamentos']) > 0:
			consulta['banco'] = self.id_banco
			consulta['pessoa'] = pessoa['idPessoa']
			consulta['perfilPessoa'] = pessoa['idPerfil_pessoa']
			consulta['tipoOferta'] = 2
			consulta['retorno'] = 1

			request_inserir_oferta = requests.post(
				"https://app.emprestimofacil.com/api/v1/ofertas/crm?key={}".format(self.api_key), json=consulta)

			if request_inserir_oferta.status_code != 200:
				print(request_inserir_oferta.text)
				input('Não foi possível salvar uma nova oferta. Verifique o que aconteceu!')
		else:
			self.finalizar_consulta_crm(pessoa, 3)

	def finalizar_consulta_crm(self, pessoa, retorno):
		dados_oferta = {
			'banco': self.id_banco,
			'pessoa': pessoa['idPessoa'],
			'perfilPessoa': pessoa['idPerfil_pessoa'],
			'retorno': retorno
		}

		request_finalizar_oferta = requests.post(
			"https://app.emprestimofacil.com/api/v1/ofertas/crm?key={}".format(self.api_key), data=dados_oferta)

		if request_finalizar_oferta.status_code != 200:
			print(request_finalizar_oferta.text)
			input('Não foi possível salvar uma nova oferta. Verifique o que aconteceu!')

	
