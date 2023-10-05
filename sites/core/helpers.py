import os
import base64
import sys
from time import sleep
from datetime import datetime as dt

def clear(): 
    return os.system("cls")

def identificar_erro_robo():
	os.system("title ERRORROBO")

def convert_file_base_64(path):
    file = open(path, 'rb')
    file_base_64 = base64.encodebytes(file.read())
    file.close()
    return file_base_64

def formatar_moeda(texto):
    texto = texto.replace("R$ ", "")
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    return float(texto)

def formatar_porcentagem(texto):
    texto = texto.replace("%", "")
    texto = texto.replace(",", ".")
    return float(texto)

def formatar_data_banco(data):
    data = dt.strptime(data, '%m/%Y')
    return dt.strftime(data, '%Y-%m-01')

def formatar_cpf(cpf):
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

def countdown(segundos, step=1, mensagem=''): 
    pad_str = ' ' * len('%d' % step)
    for i in range(segundos, 0, -step):
        print ('%s %d segundo(s) %s\r' % (mensagem, i, pad_str))
        sys.stdout.flush()
        sleep(step)