import os
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

# Função para detectar se está rodando localmente
def is_local():
    return "IS_LOCAL" in env


# Filtra apenas os numeros de processos e padroniza
import re

def num_processo(processo):
    padrao = r"E:\d{5}\.\d{10}/\d{4}"
    processo_sei_format = re.search(padrao, processo).group()
    return processo_sei_format