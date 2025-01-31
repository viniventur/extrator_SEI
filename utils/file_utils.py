import os
from dotenv import load_dotenv, dotenv_values
import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
import base64
import time
import re
env = dotenv_values('.env')

def criar_pasta_os(diretorio_x, nome_pasta):
    """Cria uma pasta com o nome especificado dentro do diretório_x."""
    caminho_pasta = os.path.join(diretorio_x, nome_pasta)

    try:
        if not os.path.exists(diretorio_x):
            st.error(f"Erro: O diretório '{diretorio_x}' não existe.")
            return None

        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)

        return caminho_pasta
    except Exception as e:
        st.error(f"Erro ao criar a pasta: {str(e)}")
        return None
    