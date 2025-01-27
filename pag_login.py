import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.login import *
from utils.chrome import *
from utils.funcoes_auxiliares import *
from sidebar import *

import warnings
warnings.filterwarnings('ignore')
import base64
import time

st.set_page_config(page_title='Extrator de dados do SEI - OGP/CGE', page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png', initial_sidebar_state="collapsed")

# Config Layout (condicional de local ou online)

if is_local():
    
    # Aplicar CSS para esconder o sidebar
    hide_style = """
    """
else:

    # Aplicar CSS para esconder o sidebar
    hide_style = """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stBaseButton-headerNoPadding"] {
            display: none;
        }

        #MainMenu {visibility: hidden}
        header {visibility: hidden}
        </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

def main():

    st.session_state.pag = 'login'
    st.session_state.acesso = ''

    run_sidebar()

    # Criar um contêiner fixo no topo da página
    header = st.container()

    logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'
    logo_base64_CGE_OGP = get_image_as_base64(logo_path_CGE_OGP)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
            <img src="data:image/png;base64,{logo_base64_CGE_OGP}" style="margin-right: 0px; width: 550px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
            <h1 style="font-size: 35px; margin: 0;">Extrator de Dados do SEI</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

### Olá! Bem vindo extrator de dados do SEI

    with st.container():

        st.write(f'''
                 
                 :warning: As senhas fornecidas não são armazenadas, servindo apenas para o sistema logar no SEI e carregar as informações.                 
                 
                 ''')

    # Input para o usuário
    usuario = st.text_input('Usuário SEI:', placeholder="Digite seu usuário do SEI.")

    # Input para a senha (caracteres ocultos)
    senha = st.text_input('Senha SEI:', type='password', placeholder="Digite sua senha do SEI.")

    # Lista de orgaos login
    with st.spinner('Obtendo órgãos disponíveis no SEI...'):
        lista_orgaos = lista_orgaos_login()
        orgao = st.selectbox("Órgão:", lista_orgaos)

    # Login
    if st.button(":material/login: Acessar"):
        if orgao == lista_orgaos[0]:
            st.error(f"Informe o órgão.")
        else:
            df_usuarios = df_usuarios_cpf()
            historico_acesso = df_historico_acesso()
            login_sei(df_usuarios, historico_acesso, usuario, senha, orgao)
        
if __name__ == "__main__":
    main()