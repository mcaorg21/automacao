"""
| #!/usr/bin/env python3
| #-*- coding: utf-8 -*-
| projeto: automacao-python
| arquivo: auxiliares
| data: 2020-03-11
| autor: Gustavo Belleza

| funcionamento:
"""


class StatusPropostaException(Exception):

    erro: str = ''

    def __init__(self, erro):
        self.erro = erro


