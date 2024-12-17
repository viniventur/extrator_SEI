import streamlit as st
import re

def tratar_processos(input_text):
    # Passo 1: Remove espaços no início e no final
    linhas = input_text.strip().splitlines()

    # Passo 2: Elimina linhas vazias e espaços extras dentro das linhas
    linhas_tratadas = [re.sub(r'\s+', '', linha) for linha in linhas if linha.strip()]

    # Passo 4: Junta as linhas válidas em uma única string com quebras de linha
    resultado = "\n".join(linhas_tratadas)

    return resultado, len(linhas_tratadas), len(linhas_tratadas)

