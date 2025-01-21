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

    # Centralizando as imagens lado a lado
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
            <img src="data:image/png;base64,{logo_base64_CGE_OGP}" style="margin-right: 0px; width: 550px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Configuração de Usuários e Acessos</h1>", unsafe_allow_html=True)

    if 'reload_data' not in st.session_state:
     st.session_state['reload_data'] = False

    cols = st.columns(3)
    
    with cols[0]:
        # botao de edicao da base de usuarios
        if st.button(':material/add: Adicionar', use_container_width=True):
            add_user()

    with cols[1]:
        # botao de edicao da base de usuarios
        if st.button(':material/edit: Alterar', use_container_width=True):
            edit_user()

    with cols[2]:
        # botao de edicao da base de usuarios
        if st.button(':material/delete: Excluir', use_container_width=True):
            excluir_user()


    if st.button(':material/refresh: Atualizar', use_container_width=True):
        st.session_state['reload_data'] = True
        st.cache_data.clear()  # Limpa o cache da função
        st.rerun()

    # Carregar os dados
    if st.session_state['reload_data']:
        df_usuarios = df_usuarios_cpf()  # Recarrega os dados
        st.session_state['reload_data'] = False
    else:
        df_usuarios = df_usuarios_cpf()  # Usa o cache, se não for recarregar

    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

# =================================================================
# PAGINAS DE DIALOGOS (MODAL) DE ADD, EDICAO E EXCLUSAO DE USUARIOS
# =================================================================

@st.dialog("Edição de Usuários")
def add_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Adicionar Usuários</h1>", unsafe_allow_html=True)
    
    # Input para o usuário
    cpf = st.text_input('CPF:')

    # tratar cpf

@st.dialog("Edição de Usuários")
def edit_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Alterar Usuários</h1>", unsafe_allow_html=True)
    
    # editar cpf ou acesso? 

    acesso = st.selectbox('Acesso', ['USUARIO', 'ADMIN']) #colocar no dataframe

@st.dialog("Edição de Usuários")
def excluir_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Excluir Usuários</h1>", unsafe_allow_html=True)
    
    # selecao por CPF



# @st.dialog("Edição de Usuários")
# def pag_edit():
    
#     # Input para o usuário
#     cpf = st.text_input('CPF:')

#     # TRATAR INPUT

#     # Input para a senha (caracteres ocultos)
#     acesso = st.selectbox('Acesso', ['USUARIO', 'ADMIN'])

#     # if st.button('Adicionar usuario'):

#     #     novo = {'CPF': str(cpf), 'ACESSO': acesso}

#     #     dados_usuarios.loc[len(dados_usuarios)] = novo

#     #     alterar_dados_usuario(dados_usuarios)


#     if st.button('UPAR'):
#         #upload_and_replace_file_drive('cpf_autorizados_extrator_sei2', df_mod, secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
#         st.session_state['reload_data'] = True




if __name__ == "__main__":
    main()

# exemplo de df

# data_df = pd.DataFrame(
#     {
#         "widgets": ["st.selectbox", "st.number_input", "st.text_area", "st.button"],
#     }
# )

# st.data_editor(
#     data_df,
#     column_config={
#         "widgets": st.column_config.Column(
#             "Streamlit Widgets",
#             help="Streamlit **widget** commands 🎈",
#             width="medium",
#             required=True,
#         )
#     },
#     hide_index=True,
#     num_rows="dynamic",
# )