import pandas as pd
import os
import streamlit as st
from utils.conn_gsheets import *
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

st.set_page_config(page_title='Extrator de dados do SEI - OGP/CGE', page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png')

if 'driver' not in st.session_state:
    st.error('Erro, Google Chrome não respondeu, redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page(modulos[0][1])

if st.session_state.acesso != 'ADMIN':
    st.error('Acesso restrito! Redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page(modulos[0][1])


# Config Layout (condicional de local ou online)

if is_local():
    
    # Aplicar CSS para esconder o sidebar
    hide_style = """
    """
else:

    # Aplicar CSS para esconder o sidebar
    hide_style = """
        <style>
        #MainMenu {visibility: hidden}
        header {visibility: hidden}
        </style>
    """

st.markdown(hide_style, unsafe_allow_html=True)

def main():

    st.session_state.pag = 'ADMIN'   

    run_sidebar()

    logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'
    logo_base64_CGE_OGP = get_image_as_base64(logo_path_CGE_OGP)

    with st.container():
        # Centralizando as imagens lado a lado
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
                <img src="data:image/png;base64,{logo_base64_CGE_OGP}" style="margin-right: 0px; width: 550px;">
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.container():

        st.markdown(f'''
                 
                 <div style="display: flex; justify-content: center; align-items: center; height: 70px; text-align: bottom;">
                <h1 style="font-size: 35px; margin: 0;">Extrator de Dados do SEI</h1>
                 </div>        
                 
                 ''',
                unsafe_allow_html=True)
        
    with st.container():

        st.markdown(f'''
                 
                 <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
                <h1 style="font-size: 30px; margin: 0;">Configuração de Acessos</h1>
                 </div>        
                 
                 ''',
                unsafe_allow_html=True)
    
        dados_usuarios = obter_dados_usuarios()

    st.dataframe(dados_usuarios)

    if st.button('atualizar'): 

        st.cache_data.clear()
        st.rerun()

    # Input para o usuário
    cpf = st.text_input('CPF:')

    # TRATAR INPUT

    # Input para a senha (caracteres ocultos)
    acesso = st.selectbox('Acesso', ['USUARIO', 'ADMIN'])

    if st.button('Adicionar usuario'):

        novo = {'CPF': str(cpf), 'ACESSO': acesso}

        dados_usuarios.loc[len(dados_usuarios)] = novo

        alterar_dados_usuario(dados_usuarios)

        st.cache_data.clear()
        st.rerun()


if __name__ == "__main__":
    main()