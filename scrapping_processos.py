import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from chrome import *
from extracao_unidade import *
from tratamento_processos import *

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

def buscar_dados(processos):

    # tempos para execucao
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5

    driver = st.session_state.driver

    for processo in processos['Processos']:

        time.sleep(tempo_medio)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(processo)
        time.sleep(tempo_curto)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(Keys.ENTER)
        time.sleep(tempo_curto)

        # Alternar para o iframe 'ifrArvore'
        iframe_arvore = driver.find_element('name', "ifrArvore")
        driver.switch_to.frame(iframe_arvore)

        driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span').click() # consultar andamento

        time.sleep(tempo_curto)    
        # Alternar para o iframe 'ifrVisualizacao'
        driver.switch_to.default_content()
        iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
        driver.switch_to.frame(iframe_visualizacao)
        
        time.sleep(tempo_medio)
        # Extrai os dados da primeira linha da tabela
        data_hora = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[1]').text  # Coluna 1: Data/Horário
        unidade = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[2]').text    # Coluna 2: Unidade
        usuario_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[3]/a')
        usuario_cpf = usuario_elemento.text    # Coluna 3: Usuário CPF
        usuario = usuario_elemento.get_attribute("alt") # coluna 4: Usuário
        descricao = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[4]').text  # Coluna 5: Descrição

        # Cria um dicionário para organizar os dados extraídos
        dados = {
            "Data Horário": data_hora,
            "Unidade Atual": unidade,
            "Usuário CPF": usuario_cpf,
            "Usuário": usuario,
            "Descrição": descricao
        }

        # Atualiza o DataFrame de forma mais eficiente
        processos.loc[processos['Processos'] == processo, ['Data Horário', 'Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição']] = [
            dados["Data Horário"], dados["Unidade Atual"], dados["Usuário CPF"], dados["Usuário"], dados["Descrição"]
        ]

        # Voltar ao contexto principal
        driver.switch_to.default_content()

    return st.dataframe(processos, hide_index=True)