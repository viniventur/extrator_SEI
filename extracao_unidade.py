import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import pyautogui
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
import time
from chrome import *


@st.cache_data
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

        return option_texts

    except Exception as e:

        st.error(f"Obtenção de unidades disponíveis no SEI falhou: {e}")

