import os
from dotenv import load_dotenv, dotenv_values
import streamlit as st
from datetime import datetime
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

# Contagem de dias entre datas do sei

def cont_dias(data_x, data_y):
    """
    Calcula a diferença em dias entre duas datas.

    Parâmetros:
        data_x (str ou datetime): Primeira data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.
        data_y (str ou datetime): Segunda data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.

    Retorna:
        int: Diferença em dias entre as duas datas.
    """
    # Verificar e converter data_x, se necessário
    if isinstance(data_x, str):
        data_x = datetime.strptime(data_x, "%d/%m/%Y %H:%M")
    elif not isinstance(data_x, datetime):
        raise ValueError("data_x deve ser uma string ou um objeto datetime.")

    # Verificar e converter data_y, se necessário
    if isinstance(data_y, str):
        data_y = datetime.strptime(data_y, "%d/%m/%Y %H:%M")
    elif not isinstance(data_y, datetime):
        raise ValueError("data_y deve ser uma string ou um objeto datetime.")

    # Calcular a diferença em dias
    diferenca = (data_y - data_x).days

    return diferenca

