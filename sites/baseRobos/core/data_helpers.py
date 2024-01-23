"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: main.py
| data: 22/10/2019
| autor: Gustavo Belleza

| funcionamento:
    Contem funções auxiliares a serem utilizadas no
    tratamento e armazenamento de dados.
"""
from datetime import datetime
from selenium.webdriver.common.by import By
import requests
from PIL import Image
from datetime import datetime as dt
from fuzzywuzzy import fuzz
from typing import Union
from requests import Response
from sites.baseRobos.core.DebugTools import DebugTools
dbg = DebugTools(debugging=False)


def is_number(string):
    try:
        float(string)
        return True
    except:
        return


def gen_log(exception, log_name, *exclusions):
    with open(log_name + '.log', 'a') as fObj:
        if exception not in exclusions:
            write = fObj.write(f"{str(datetime.now())}: {str(exception)}" + "\n")


def monthly_data_cleaner(file):
    curr_date = datetime.now()
    curr_month = int(str(curr_date).split('-')[1])
    with open(file, 'r+') as fObj:
        reader = fObj.readline()
        try:
            reg_date = reader.split()[0]
            reg_month = int(reg_date.split('-')[1])
        except IndexError:
            return None
        if curr_month != reg_month:
            print('!!!')
            open(file, 'w')
        fObj.close()


def get_select_options_values(loc_select, act, method=By.CSS_SELECTOR):
    options = act.retornar_opcoes_select(loc_select, method)
    opts_key_vals = {}
    for option in options:
        key = option.text
        if len(key) > 1:
            opts_key_vals[key] = option.get_attribute('value')
    return opts_key_vals


def strip_zero_left(string_number: str) -> str:
    qtd_zeros: int = string_number.count("0")
    if qtd_zeros:
        return string_number[qtd_zeros:]
    else:
        print("Não há zeros à esquerda no string.")
        return string_number


def date_time_to_list():
    """
    Retorna a data atual no formato [aaaa, mm, dd]
    :return: (list[int])
    """
    date_str = str(datetime.now())
    str_aaaa_mm_dd = date_str.split(" ")[0]
    date_list = [int(num_str) for num_str in str_aaaa_mm_dd.split("-")]
    return date_list


def make_request(method: str, url: str, params_data: dict = None, msg: str = '', json: bool = False) -> Union[Response, dict]:
    """
    :param method: (str) método da request.
    :param url: (str) url da API.
    :param params_data: (dict) params do GET ou data do POST/PUT.
    :param msg: (str) mensagem opcional para quando HTTP Status != 200.
    :param json: retorna <response> como um dicionário.]
    :return: se request bem sucedido (status_code = 200): (<class 'requests.models.Response'>) dados da request.
             se não (status_code != 200): (boolean) False.
    """
    from inspect import getframeinfo, stack
    result = ''
    if method.upper() == 'GET':
        result = requests.get(
            url,
            params=params_data
        )
    elif method.upper() == 'POST':
        result = requests.post(
            url,
            data=params_data
        )
    elif method.upper() == 'PUT':
        result = requests.put(
            url,
            data=params_data
        )
    else:
        result = "Métodos permitidos: GET, POST e PUT."

    if result.status_code != 200:
        print(f"HTTP Status: {result}. " + msg)
        raise ApiResponseException(
            result.status_code, result.content)
    else:
        print(f"HTTP Status: {result.status_code} - OK. " + msg)
        if json:
            return result.json()
        else:
            return result


class ApiResponseException(Exception):
    def __init__(self, status_code, msg):
        self.status_code = status_code
        self.message = msg
        self.exc = f"Status Code: {self.status_code}. Mensagem: {self.message}"

    def __repr__(self):
        return self.exc


def buscar_documentos_contrato(cod_con):
    url_api = f'https://app.emprestimofacil.com/api/v1/contratos/documentos?key=f689f1e12a0399fba803cb2365fc362f&contrato={cod_con}'

    request_contratos = make_request('GET', url_api,
                                     msg="Em <buscar_documentos_contrato>")

    return request_contratos.json()


def download(url, file_path):
    with open(file_path, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

        if file_path[-3:] == 'jpg' or file_path[-3:] == 'jpeg':
            im = Image.open(file_path)
            im.save(file_path, dpi=(1400, 1400))

def criar_arquivo(content, file_path):
    with open(file_path, "wb") as file:
        file.write(content)
        im = Image.open(file_path)
        im.save(file_path, dpi=(1400, 1400))
        #im = Image.open(file_path)
        #im.save(file_path, dpi=(1400, 1400))


def deep_in(sample_list, comparison_str):
    for item in sample_list:
        if item in comparison_str:
            return True
    return False


def deep_search(sample_list, comparison_str):
    for item in sample_list:
        if item in comparison_str:
            return item
    return False


def data_mais_recente_dia_mes_ano(data1, data2):
    """
    :type data1: str
    :type data2: str
    :param data1, data2: dd/mm/aaaa
    :rtype bool:
    """
    dia1, mes1, ano1 = data1.split("/")
    dia2, mes2, ano2 = data2.split("/")

    if int(ano1) > int(ano2):
        return data1
    elif int(ano2) > int(ano1):
        return data2
    elif int(mes1) > int(mes2):
        return data1
    elif int(mes2) > int(mes1):
        return data2
    elif int(dia1) > int(dia2):
        return data1
    else:
        return data2


def achar_data_mais_recente(datas):
    print(datas)
    mais_recente = datas[0]
    for data in datas:
        mais_recente = data_mais_recente_dia_mes_ano(mais_recente, data)

    return mais_recente


def formatar_moeda(texto):
    texto = texto.replace("R$ ", "")
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    return float(texto)

def formatar_moeda2(texto):
    texto = texto.replace(',', '')
    return texto

def formatar_porcentagem(texto):
    texto = texto.replace("%", "")
    texto = texto.replace(",", ".")
    return float(texto)


def formatar_data_banco(data):
    data = dt.strptime(data, '%m/%Y')
    return dt.strftime(data, '%Y-%m-01')

def formatar_data_banco_dados(data):
    data = dt.strptime(data, '%d/%m/%Y')
    return dt.strftime(data, '%Y-%m-%d')

def formatar_cpf(cpf):
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

def formatar_cpf_sem_caracteres(cpf):
    return cpf.replace('.','').replace('-','')


def similaridade(string1, string2):
    return fuzz.ratio(str(string1), str(string2))
