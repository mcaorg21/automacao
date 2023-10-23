import requests, time, os
from PATHS import project_path
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By


import pdb

class Captcha:
	def __init__(self, driver, manual=False, prioridade=0, timeout=90): 
		self.driver = driver
		self.api_key = "CD7TQHQSV7QPCTQI34"
		self.prioridade = prioridade
		self.timeout = timeout
		self.captcha_path = os.getcwd().replace("\\", "/")+"/sites/core/captchas/"
		self.manual = manual

	def enviar_novo_captcha(self, filename):
		files = {"file-upload-01": open(filename, 'rb')}
		values = {
			'apikey': self.api_key, 
			'action': 'usercaptchaupload', 
			'source': 'pythonapi', 
			'prio': self.prioridade, 
			'maxtimeout': self.timeout
		}
		request_novo = requests.post("https://www.9kw.eu/index.cgi", files=files, data=values)
		
		if (request_novo.status_code == 200):
			return request_novo.text

	def resultado_captcha(self, id_captcha):
		request_consulta = requests.get("https://www.9kw.eu/index.cgi?apikey=%s&id=%s&action=usercaptchacorrectdata" % (self.api_key, id_captcha)) 

		if (request_consulta.status_code == 200):
			return request_consulta.text

	def resolver_captcha(self, seletor_captcha, filename='1.jpg'):
		if (self.manual == True):
			catpcha_resposta = input("Qual é o captcha? ")
			return 1, catpcha_resposta

		screenshot = self.driver.find_element(By.CSS_SELECTOR,seletor_captcha).screenshot_as_png
		image = Image.open(BytesIO(screenshot))
		image.save(self.captcha_path+filename, 'PNG', optimize=True, quality=95)
		time.sleep(2)

		id_captcha = self.enviar_novo_captcha(self.captcha_path+filename)
		print("Id captcha: " + id_captcha)

		catpcha_resposta = self.resultado_captcha(id_captcha)
		while (catpcha_resposta == ''):
			try:
				print('Esperando captcha 2...')
				catpcha_resposta = self.resultado_captcha(id_captcha)
				time.sleep(5)
			except Exception as e:
				print("Erro na resposta do captcha!")
				print(e)
				time.sleep(5)

		return id_captcha, catpcha_resposta

	# status 1 = Correto
	# status 2 = Incorreto
	def mudar_status_captcha(self, id_captcha, status):
		if self.manual == True: return ''

		request_status = requests.get("https://www.9kw.eu/index.cgi?apikey=CD7TQHQSV7QPCTQI34&id="+id_captcha+"&action=usercaptchacorrectback&correct="+status) 
		if (request_status.status_code == 200):
			return request_status.text


class TwoCaptcha:
	def __init__(self, driver, manual=False, timeout=90, calculo=False):
		self.driver = driver
		self.api_key = "6c2a0fc387a4d92fae18d23ca833130f"
		self.calculo = calculo
		self.captcha_path = project_path() + "/core/captchas/"
		self.captcha_img = ''

		self.manual = manual

	def resolver_captcha(self, seletor_captcha, filename='1.jpg'):
	
		if self.captcha_img:
			filename = self.captcha_img

		if self.manual == True:
			catpcha_resposta = input("Qual é o captcha? ")
			return 1, catpcha_resposta

		try:
			screenshot = self.driver.find_element(By.CSS_SELECTOR,seletor_captcha).screenshot_as_png
		except Exception as e:
			print("Não foi possível tirar o print do captcha")
			print(e)
			return self.resolver_captcha(seletor_captcha, filename)

		image = Image.open(BytesIO(screenshot))
		image.save(self.captcha_path+filename, 'PNG', optimize=True, quality=95)
		time.sleep(2)

		id_captcha = self.enviar_novo_captcha(self.captcha_path+filename)
		print("Id captcha: " + id_captcha)
		time.sleep(6)

		catpcha_resposta = self.resultado_captcha(id_captcha)
		return id_captcha, catpcha_resposta

	def resolver_captcha_screenshot(self, width, height, top, left, filename="1.jpg"):
		if (self.manual == True):
			catpcha_resposta = input("Qual é o captcha? ")
			return 1, catpcha_resposta

		self.driver.set_window_size(width, height)
		time.sleep(3)
		self.driver.execute_script("""window.scrollTo({ top: %s, left: %s });""" % (top, left))
		time.sleep(3)

		screenshot = self.driver.get_screenshot_as_png()
		image = Image.open(BytesIO(screenshot))
		image.save(self.captcha_path+filename, 'PNG', optimize=True, quality=95)
		time.sleep(2)
		self.driver.maximize_window()

		id_captcha = self.enviar_novo_captcha(self.captcha_path+filename)
		print("Id captcha: " + id_captcha)
		time.sleep(6)

		catpcha_resposta = self.resultado_captcha(id_captcha)
		return id_captcha, catpcha_resposta

	def resolver_captcha_inss_bradesco(self, seletor, filename="/TESTE.jpg"):
		if self.manual == True:
			catpcha_resposta = input("Qual é o captcha? ")
			return 1, catpcha_resposta
		imagem = self.driver.find_element_self.driver.find_element(By.CSS_SELECTOR,seletor))

		localizacao = imagem.location
		tamanho = imagem.size
		screenshot = self.driver.get_screenshot_as_png()
		print(localizacao, tamanho)
		image = Image.open(BytesIO(screenshot))
		left = localizacao['x']
		top = localizacao['y']
		right = localizacao['x'] + tamanho['width']
		bottom = localizacao['y'] + tamanho['height']

		image = image.crop((left, top, right, bottom))

		image.save(self.captcha_path + filename, 'PNG', optimize=True, quality=95)
		print(self.captcha_path+filename)
		id_captcha = self.enviar_novo_captcha(self.captcha_path+filename)
		print("Id captcha: " + id_captcha)
		time.sleep(6)

		catpcha_resposta = self.resultado_captcha(id_captcha)
		return id_captcha, catpcha_resposta

	def enviar_novo_captcha(self, filename):
		files = {
			"file": open(filename, 'rb')
		}
		
		values = {
			'key': self.api_key,
			'method': 'post',
			'regsense': 1,
			'json': 1
		}

		if self.calculo:
			values['regsense'] = 0
			values['calc'] = 1
			values['textinstructions'] = "E.g: captcha (4 + 4) answer = 8"

		request_novo_captcha = requests.post(
			"https://2captcha.com/in.php", files=files, data=values)

		if (request_novo_captcha.status_code == 200):
			return request_novo_captcha.json()['request']

	def resultado_captcha(self, id_captcha, tentativa=0):
		request_consulta = requests.get(
			"https://2captcha.com/res.php?key={}&action=get&id={}".format(self.api_key, id_captcha)
		)

		if request_consulta.status_code != 200:
			print('Erro na busca do captcha!')
			time.sleep(5)
			return self.resultado_captcha(id_captcha, (tentativa+1))

		if tentativa >= 20:
			return 'ERROR NO USER'

		captcha_resposta = request_consulta.text

		if 'CAPCHA_NOT_READY' in captcha_resposta:
			print("Esperando Captcha 2...")
			time.sleep(5)
			return self.resultado_captcha(id_captcha, (tentativa+1))

		if captcha_resposta == 'ERROR_CAPTCHA_UNSOLVABLE':
			return 'ERROR NO USER'

		return captcha_resposta.split('|')[1]

	# status 1 = Correto
	# status 2 = Incorreto
	def mudar_status_captcha(self, id_captcha, status):
		if self.manual == True:
			return ''

		if status == '1':
			tipo = "reportgood"
		elif status == '2':
			tipo = "reportbad"
			
		request_status = requests.get(
			"https://2captcha.com/res.php?key={}&action={}&id={}".format(self.api_key, tipo, id_captcha)
		)

		if (request_status.status_code == 200):
			return request_status.text
