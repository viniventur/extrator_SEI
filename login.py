import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from chrome import *

from selenium.webdriver.support.ui import Select

import warnings
warnings.filterwarnings('ignore')
import time
from chrome import *


@st.cache_data
def lista_orgaos_login():

    try:
        driver = chrome()
        driver.get(env['SITE_SEI'])

        select_element = driver.find_element('xpath', '//*[@id="selOrgao"]')

        # Cria um objeto Select para manipular a lista suspensa
        select = Select(select_element)

        # Captura todas as opções da lista
        options = select.options

        # Captura todas as opções e seus textos
        option_texts = [option.text for option in select.options]
        
        driver.quit()

        return option_texts
        
    except Exception as e:

        st.error(f"Obtenção de órgãos disponíveis no SEI falhou: {e}")

def login_sei(usuario_sei, senha_sei, orgao_sei):

    print('Carregando...')

    try:

        driver = chrome()

        if 'driver' not in st.session_state:
            st.session_state.driver = driver

        with st.spinner('Entrando no SEI...'):

            
            # tempos para execucao
            tempo_curto = 0.5
            tempo_medio = 1
            tempo_longo = 1.5

            # Abrindo o SEI
            #driver = webdriver.Chrome()
            driver.get(env['SITE_SEI'])

            print('Obtendo informacoes...')

            driver.find_element("xpath", '//*[@id="txtUsuario"]').send_keys(usuario_sei)
            time.sleep(tempo_curto)
            driver.find_element("xpath", '//*[@id="pwdSenha"]').send_keys(senha_sei)
            time.sleep(tempo_curto)
            driver.find_element("xpath", '//*[@id="selOrgao"]').send_keys(orgao_sei)
            driver.find_element("xpath", '//*[@id="sbmLogin"]').click()

        # Aguarda um pouco para possíveis popups ou respostas da página
            time.sleep(tempo_medio)

            try:
                alerta = driver.switch_to.alert
                #alerta = driver.switch_to.active_element
                texto = alerta.text
                st.error(alerta.text)
                alerta.accept()
                driver.quit()
            except:
                st.success('Acesso efetuado! Redirecionando, aguarde...')
                st.switch_page('pages/Extracao.py')              

    except Exception as e:

        st.error(f"Login falhou: {e}")
