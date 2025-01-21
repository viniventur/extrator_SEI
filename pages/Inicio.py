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

from utils.conn_gdriver import *


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

    st.session_state.pag = 'inicio'

    run_sidebar()

    # Criar um contêiner fixo no topo da página

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
                <h1 style="font-size: 30px; margin: 0;">Olá, {st.session_state.nome_usuario}! O que deseja acessar?</h1>
                 </div>        
                 
                 ''',
                unsafe_allow_html=True)
        
    # Filtrar os módulos a partir do índice 2   
    modulos_filtrados = {k: v for k, v in modulos.items() if int(k) >= 2} # filtrar modulos sem pagina de login e sem o pag de inicio

    n_cols = len(modulos_filtrados) if st.session_state.acesso == 'ADMIN' else len(modulos_filtrados)-1 # numero de coluna sem o administrador para usuarios sem acesso

    cols= st.columns(n_cols, gap='large', vertical_alignment='center')

    # Inicializar variável para armazenar o módulo clicado
    modulo_select = None

    for i, modulo in modulos_filtrados.items():
        with cols[i-2]:  # Posicionar o botão na coluna correspondente (-2 excluindo login e inicio)
            #st.write(modulo[0])
            if st.button(f'{modulo[2]} {modulo[0]}', use_container_width=True, key=f'botao-{modulo[0]}', help='Clique para mudar de página'):  # Nome do módulo como rótulo do botão
                modulo_select = modulo[1]

    if modulo_select:
        with st.spinner('Redirecionando...'):
            st.switch_page(modulo_select)
        
if __name__ == "__main__":
    main()