import sys,pdb,json
import asyncio
from threading import Thread

#sys.path.append('../../../')

from flask import Flask, request, abort
app = Flask(__name__)

#from sites.promoBank.promo_bank import PromoBank
#promobank = PromoBank()
#promobank.load_cookies_promobank_web_admin()

@app.route('/consulta_promobank', methods=['POST'])
def webhook():
	from flask import Flask, request, abort
	if request.method == 'POST':

		from sites.promoBank.promo_bank_post import PromoBank
		promobank = PromoBank()
		#promobank.load_cookies_promobank_web_admin()

		valida_horario = promobank.validar_horario_api()
		if(valida_horario['status'] == 'fora_horario'):
			print('Fora do horário')
			abort(400)	
		solicitacao = request.json
		dados = promobank.main_api(solicitacao,'api')
		print(dados)
		#if(json.loads(dados['consultaBeneficio'])['retorno'] == 11 or ('retorno' in dados and dados['retorno'] == 11)):
			#promobank.load_cookies_promobank_web_admin()
		#promobank.fechar_driver()
		return dados
	else:
		abort(400)

@app.route('/abre_promobank', methods=['GET'])
def webhook2():
	if request.method == 'GET':
		dados = promobank.main()
		return 200
	else:
		abort(400)

@app.route('/consulta_cpf', methods=['GET'])
def webhook3():
	from flask import Flask, request, abort
	if request.method == 'GET':	

		from sites.promoBank.promo_bank_post import PromoBank
		promobank = PromoBank()
		#promobank.load_cookies_promobank_web_admin()

		valida_horario = promobank.validar_horario_api()
		cpf = request.args['cpf']
		if(valida_horario['status'] == 'fora_horario'):
			print('Fora do horário')
			abort(400)	
		if not cpf:
			print('Cpf não enviado.')
			abort(404)
		retorno = promobank.cosulta_beneficio_cpf(cpf)
		#promobank.fechar_driver()
		return retorno
	else:
		promobank.fechar_driver()
		abort(400)


if __name__ == '__main__':
	app.run(port='5050')