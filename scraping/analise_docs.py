import pandas as pd
import os
from openpyxl.utils import get_column_letter
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from scraping.extracao_unidade import *
from utils.funcoes_auxiliares import *

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import warnings
warnings.filterwarnings('ignore')
import time
from datetime import datetime
from io import BytesIO
import re


def raspagem_docs(processo, unidade):
    try:
        # Tempos para execução
        tempo_curto = 0.5
        tempo_medio = 1
        tempo_longo = 1.5

        driver = st.session_state.driver

        mudar_iframe('default')

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)

        # Busca dos processos
        time.sleep(tempo_medio)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(processo)
        time.sleep(tempo_curto)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(Keys.ENTER)
        time.sleep(tempo_curto)

        # =============================================
        # VERIFICANDO A EXISTENCIA OU ACESSO AO PROCESSO
        # =============================================

        status, mensagem = verificar_acesso_processo(processo)

        if not status:
            st.error(mensagem)
            return

        # =============================================
        # raspagem documentos
        # =============================================

        mudar_iframe('arvore')

        # Localizar todos os elementos de abertura de pastas e clicar
        elements = driver.find_elements(By.XPATH, "//*[contains(@id, 'ancjoinPASTA')]")

        # Iterar sobre os elementos encontrados e clicar em cada um
        for element in elements[:-1]:
            element.click()
            time.sleep(tempo_curto)
        
        document_elements = driver.find_elements(By.XPATH, "//span[starts-with(@id, 'span') and not(contains(@id, 'PASTA'))]")

        # Extrair os textos (nomes dos documentos)
        document_names = [element.text for element in document_elements if element.text]  # Ignora spans vazios
        document_names.pop(0)

        return document_names

    except Exception as e:
        st.error(f"Erro durante a obtenção dos documentos do processo: {e}")

