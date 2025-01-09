import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.login import *
from utils.chrome import *
from utils.funcoes_auxiliares import *
from teste import *
import warnings
warnings.filterwarnings('ignore')
import base64
import time

st.set_page_config(page_title='Extrator de dados do SEI - OGP/CGE', page_icon='src/assets/Identidades visual/OGP/LOGO-OGP - icon.jpg', initial_sidebar_state="collapsed")

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
        #MainMenu {visibility: hidden}
        header {visibility: hidden}
        </style>
    """

st.markdown(hide_style, unsafe_allow_html=True)

def main():

    # Criar um contêiner fixo no topo da página
    header = st.container()

    def get_image_as_base64(file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    logo_path_CGE = 'src/assets/Identidades visual/Logo CGE Governo/LOGO GOV-branco.png'
    logo_path_OGP = 'src/assets/Identidades visual/OGP/APRESENTAÇÃO_LOGO_-_OBSERVATÓRIO_DA_GESTÃO_PÚBLICA_BRANCO_TRANSP.png'
    logo_base64_CGE = get_image_as_base64(logo_path_CGE)
    logo_base64_OGP = get_image_as_base64(logo_path_OGP)

    with st.container():
        # Centralizando as imagens lado a lado
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
                <img src="data:image/png;base64,{logo_base64_CGE}" style="margin-right: 0px; width: 300px;">
                <img src="data:image/png;base64,{logo_base64_OGP}" style="width: 250px;">
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.container():
        # Centralizando o texto no meio da tela
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 60px; text-align: center;">
                <h1 style="font-size: 35px; margin: 0;">Extrator de Dados do SEI - {teste()}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

### Olá! Bem vindo extrator de dados do SEI

    with st.container():

        st.write('''
                 
                 ##### 

                 Obs.: Os dados de logins fornecidos não são armazenados, servindo apenas para o sistema logar no SEI e carregar as informações.                 
                 
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
    if st.button("Acessar"):
        if orgao == lista_orgaos[0]:
            st.error(f"Informe o órgão.")
        else:
            login_sei(usuario, senha, orgao)
        
if __name__ == "__main__":
    main()