import os
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

# Função para detectar se está rodando localmente
def is_local():
    return "IS_LOCAL" in env


# Filtra apenas os numeros de processos e padroniza
import re

def num_processo_sei(processo):
    padrao = r"E:\d{5}\.\d{10}/\d{4}"
    processo_sei_format = re.search(padrao, processo).group()
    return processo_sei_format

def tratar_processos_input(input_text):
    # Passo 1: Remove espaços no início e no final
    linhas = input_text.strip().splitlines()

    # Passo 2: Elimina linhas vazias e espaços extras dentro das linhas
    linhas_tratadas = [re.sub(r'\s+', '', linha) for linha in linhas if linha.strip()]

    # Passo 4: Junta as linhas válidas em uma única string com quebras de linha
    resultado = "\n".join(linhas_tratadas)

    return resultado, len(linhas_tratadas), len(linhas_tratadas)