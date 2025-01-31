import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from selenium.webdriver.support.ui import Select

import warnings
warnings.filterwarnings('ignore')
import time

from utils import *

def lista_unidades_sei():

    try:
        if 'driver' not in st.session_state:
            st.error("Nenhuma sessão do SEI foi encontrada. Faça login novamente.")

        driver = st.session_state.driver  # Recupera o driver existente

        select_element = driver.find_element('xpath', '//*[@id="selInfraUnidades"]')

        # Cria um objeto Select para manipular a lista suspensa
        select = Select(select_element)

        # Captura todas as opções da lista
        options = select.options

        # Captura todas as opções e seus textos
        option_texts = [option.text for option in select.options]

        st.session_state.unidades_usuario = option_texts

    except Exception as e:

        st.error(f"Obtenção de unidades disponíveis no SEI falhou: {e}")

