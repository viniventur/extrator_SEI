import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import warnings
warnings.filterwarnings('ignore')
import time

from utils import *

def procs_unidade(unidade):

    try:
        if 'driver' not in st.session_state:
            st.error("Nenhuma sessão do SEI foi encontrada. Faça login novamente.")

        driver = st.session_state.driver  # Recupera o driver existente

        mudar_iframe('default')

        botao_voltar = driver.find_element(By.XPATH, '//*[@id="lnkControleProcessos"]').click

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)


        # Localizar a tabela de processos da unidade
        tabela = driver.find_element(By.XPATH, '//*[@id="tblProcessosRecebidos"]/tbody')


        # Capturar todos os links com a estrutura correspondente
        processos = tabela.find_elements(By.XPATH, './/td[3]/a')

        processos_list = [processo.text for processo in processos]  # Captura o texto de cada link
        
        return processos_list

    except Exception as e:

        st.error(f"Obtenção de processos na unidade: {e}")


