import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from utils.funcoes_auxiliares import *
from utils.conn_gdriver import *
from scraping.extracao_unidade import *

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import warnings
warnings.filterwarnings('ignore')
import time

@st.cache_data(show_spinner=False)
def lista_orgaos_login():

    try:
        driver = chrome()

        driver.get(env['SITE_SEI'] if is_local() else st.secrets['SITE_SEI'])

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

def login_sei(df_usuarios, usuario_sei, senha_sei, orgao_sei):

    #st.write('Carregando...')

    try:

        driver = chrome()

        st.session_state.driver = driver

        # Verificando acesso do usuario
        with st.spinner('Verificando acesso...'):

            # Verifica se o usuario tem acesso
            if usuario_sei in df_usuarios['CPF'].values:
                if len(df_usuarios.loc[df_usuarios['CPF'] == usuario_sei]['ACESSO'].unique()) > 1: # Verifica se o usuario tem acessos conflitantes
                    st.error('Usuário contém mais de um acesso registrado! Contacte um administrador.')
                    return
                else:
                    st.session_state.acesso = df_usuarios.loc[df_usuarios['CPF'] == usuario_sei]['ACESSO'].unique()
                    pass
            else:
                st.error('O usuário não tem acesso.')
                return

        with st.spinner('Entrando no SEI...'):
            
            # tempos para execucao
            tempo_curto = 0.5
            tempo_medio = 1
            tempo_longo = 1.5

            # Abrindo o SEI
            #driver = webdriver.Chrome()
            driver.get(env['SITE_SEI'] if is_local() else st.secrets['SITE_SEI'])

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
                # Pegar o nome completo do usuário
                nome_elemento = driver.find_element(By.XPATH, '//*[@id="lnkUsuarioSistema"]') # Pegar o nome completo do usuário
                nome = nome_elemento.get_attribute("title")
                nome = nome.split()[0]
                st.session_state.nome_usuario = nome

                # Atualizacao ultimo acesso
                df_usuarios.loc[df_usuarios['CPF'] == usuario_sei, 'ULTIMO_ACESSO'] = st.session_state.data_atualizacao_users
                upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_usuarios, folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])

                # Base de logs de acesso
                

                # Redirecionamento
                st.success(f'Olá, {nome}! Acesso efetuado! Redirecionando, aguarde...')
                lista_unidades_sei()
                time.sleep(2)
                st.switch_page(modulos[1][1])              

    except Exception as e:

        st.error(f"Login falhou: {e}")
