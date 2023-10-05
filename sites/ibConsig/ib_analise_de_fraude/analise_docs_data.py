"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: analise_docs_data
| data: 2019-11-14
| autor: Gustavo Belleza

"""
import re
from typing import List, Union

from sites.baseRobos.data_handler import DataHandler
from sites.baseRobos.core.DebugTools import DebugTools
from dados.APIGetSource import APIGetSource

dbg = DebugTools(debugging=False)


class AnaliseDocsData(DataHandler):
    def __init__(self):
        super().__init__()
        self.data_source = APIGetSource("itau")
        self.api_keys = {
            'post_atualizar_status': 'f689f1e12a0399fba803cb2365fc362f'
        }
        self.api_urls = {
            'post_atualizar_status': ("https://www.emprestimofacil.co/web_admin/api/v1/" +
                                      "atualiza-status/banco-itau-consignado/contratos/")}
        self.parar_se_exception = True

    def get_request_documentos(self, contrato) -> dict:
        self.data_source.codigo_dados = contrato[0]  # ADE
        return self.data_source.docs_log_contrato(cpf=contrato[1])

    def get_request_documentos_portabilidade(self, contrato) -> dict:
        self.data_source.codigo_dados = contrato[0]  # ADE
        return self.data_source.docs_contrato_portabilidade(cpf=contrato[4])

    def obter_contratos_para_analise_documental(self) -> List[dict]:
        """ Buscar ADE e CPF de contratos que necessitam de checagem de documentos """
        fila_contratos = self.data_source.contratos_documentos_a_enviar()

        if fila_contratos[0]["mensagem"] == "Nada a atualizar.":
            print("Não há contratos na fila...")
            return []

        return fila_contratos

    def obter_contratos_para_anexar_ibconsig(self) -> List[dict]:
        """ Buscar ADE e CPF de contratos que necessitam de checagem de documentos """
        fila_contratos = self.data_source.contratos_documentos_a_enviar_ibconsig()

        if fila_contratos[0]["mensagem"] == "Nada a atualizar.":
            print("Não há contratos na fila...")
            return []

        return fila_contratos

    def filtrar_solicitacao_de_analise_mais_recente(self, datas_codigos):
        data_mais_recente = self.dh.achar_data_mais_recente(list(datas_codigos.keys()))
        return datas_codigos[data_mais_recente]

    def atualizar_status(self, contrato, mensagem):
        try:
            dbg.debugger()
            print("Atualizando status do contrato...")
            print(f"{mensagem}")

            dados = {'key': self.api_keys['post_atualizar_status'],
                     "codigoCon": contrato[2],
                     "ade": contrato[1],
                     "statusPropostaBanco": "Aguardando Análise do Banco",
                     "observacaoDetalhadaBanco": mensagem
                     }

            req_atualiza = self.dh.make_request(
                "POST",
                self.api_urls['post_atualizar_status'],
                params_data=dados,
                msg="Em <atualizar_status>"
            )
            print(req_atualiza.content)
        except Exception as e:
            print(e)
            self.data_handler_error_log("Em <atualizar_status>", "analise_docs")
            if self.parar_se_exception:
                raise Exception(e)

    def atualizar_status_portabilidade(self, contrato, mensagem):
        try:
            dbg.debugger()
            print("Atualizando status do contrato...")
            print(f"{mensagem}")

            dados = {'key': self.api_keys['post_atualizar_status'],
                     "codigoCon": contrato[1],
                     "ade": contrato[0],
                     "statusPropostaBanco": "Aguardando Análise do Banco",
                     "observacaoDetalhadaBanco": mensagem,
                     "ade_portabilidade":contrato[2],
                     "codigo_con_portabilidade":contrato[3]
                     }

            req_atualiza = self.dh.make_request(
                "POST",
                self.api_urls['post_atualizar_status'],
                params_data=dados,
                msg="Em <atualizar_status>"
            )
            print(req_atualiza.content)
        except Exception as e:
            print(e)
            self.data_handler_error_log("Em <atualizar_status>", "analise_docs")
            if self.parar_se_exception:
                raise Exception(e)
    
    def atualizar_status_In100(self, contrato, mensagem):
        try:
            dbg.debugger()
            print("Atualizando status do contrato...")
            print(f"{mensagem}")

            dados = {'key': self.api_keys['post_atualizar_status'],
                     "codigoCon": contrato[1],
                     "ade": contrato[0],
                     "statusPropostaBanco": "Aguardando Análise do Banco",
                     "observacaoDetalhadaBanco": mensagem,
                     }

            req_atualiza = self.dh.make_request(
                "POST",
                self.api_urls['post_atualizar_status'],
                params_data=dados,
                msg="Em <atualizar_status>"
            )
            print(req_atualiza.content)
        except Exception as e:
            print(e)
            self.data_handler_error_log("Em <atualizar_status>", "analise_docs")
            if self.parar_se_exception:
                raise Exception(e)

    def extrair_datas_codigos_tabela(self, elementos_linha, numero_col_data) -> dict:
        data_codigo_dicts = {}
        codigo = ""
        codigos = []
        for elemento in elementos_linha:
            if "www.analisedocumentos.com.br" in elemento.text:
                data = elemento.text.split(" ")[numero_col_data - 1]
                print('-' * 50)
                print(data)
                infos = elemento.text.split(" ")[-7:]
                print(" ".join(infos))

                mensagem = " ".join(infos)

                re_match = re.search(
                    r'[A-Za-z0-9]*([a-zA-Z]+[0-9]+|[0-9]+[a-zA-Z]+)',
                    mensagem)

                if re_match is not None:
                    codigo = re_match.group()

                if not codigo:
                    re_match = re.search(r"\d{8}", mensagem)
                    if re_match is None:
                        continue
                    else:
                        codigo = re_match.group()

                print("Código encontrado:", codigo)
                data_codigo_dicts[data] = codigo

        return data_codigo_dicts

    def filtrar_codigo(self, texto):
        texto = texto.lower()
        b = texto.split(':')
        c = " ".join(b).split("codigo")
        d = ""

        for item in c:
            if 'voxage' in item or '|' in item:
                d = item.split("|")

        e = ''

        for item in d:
            for char in item:
                if self.dh.is_number(char):
                    e = item.strip()
                    break
        print('Código:', e)
        return e

