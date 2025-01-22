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
    elif st.session_state['reload_data'] == True:
        st.session_state['reload_data'] = False
        st.cache_data.clear()  # Limpa o cache da função
        st.rerun()
     

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

@st.dialog("Adicionar Usuários")
def add_user():

    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Insira os Dados:</h1>", unsafe_allow_html=True)
    
    acessos = ['USUARIO', 'ADMIN']

    df_add_users = pd.DataFrame(pd.DataFrame({
                                                "CPF": ["Insira o CPF"],  # Exemplo de CPF formatado
                                                "ACESSO": ['USUARIO']             # Indicando se é admin ou não
                                            })

                                )

    add_df = st.data_editor(df_add_users,
                            column_config={
                                        "ACESSO": st.column_config.SelectboxColumn(
                                        "ACESSO",
                                        width="medium",
                                        options=acessos,
                                        default='USUARIO',
                                        required=True
                                        ),
                                        "CPF": st.column_config.TextColumn(
                                            "CPF",
                                            max_chars=11,
                                            validate=r"^\d{11}$",
                                            default='Insira o CPF'
                                        ) 
                            },
                             hide_index=True,
                             use_container_width=True,
                             num_rows='dynamic'
                            )

    if st.button(':material/add: Adicionar Usuários', use_container_width=True):

        with st.spinner('Adicionando usuários...'):

            # ========================
            # TRATAMENTO DE DADOS
            # ========================

            # Tratamento dos default e Verificar se foi inserido algo
            add_df = add_df[add_df["CPF"] != "Insira o CPF"]

            if len(add_df) < 1:
                st.error('Insira dados para adicionar usuários.')
                return
            
            # Validação de CPF
            add_df["CPF_VALIDACAO"] = add_df["CPF"].apply(validacao_cpf)
            qnt_INVALIDOS = len(add_df.loc[add_df['CPF_VALIDACAO'] == False])
            if qnt_INVALIDOS > 0:
                st.error('Os dados contém CPFs inválidos:')
                st.dataframe(add_df.loc[add_df['CPF_VALIDACAO'] == False][['CPF', 'ACESSO']],
                            use_container_width=True,
                            hide_index=True
                            )
                return

            
            # Verificar Duplicidade entre si
            add_df['CONCAT_VERIFICACAO'] = add_df['CPF'] + add_df['ACESSO']
            if len(add_df) > 1 and not add_df[["CONCAT_VERIFICACAO"]].duplicated().any():
                st.error('CPF duplicados com acessos diferentes:')
                st.dataframe(add_df.drop_duplicates(subset=['CONCAT_VERIFICACAO'], keep=False)[['CPF', 'ACESSO']],
                            use_container_width=True,
                            hide_index=True
                            )              
                return

            # Verificar Duplicidade na base de dados
            elif add_df["CPF"].isin(df_usuarios["CPF"]).any():
                st.error("Os CPFs abaixo já constam na base!")
                st.dataframe(add_df.loc[add_df["CPF"].isin(df_usuarios["CPF"])][['CPF', 'ACESSO']],
                    use_container_width=True,
                    hide_index=True
                    )
                return     

            add_df = add_df.drop_duplicates(subset=['CONCAT_VERIFICACAO'])[['CPF', 'ACESSO']]

            # Adicionando
            df_adicionado = pd.concat([df_usuarios, add_df], axis=0, ignore_index=True)

            upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_adicionado, secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
            df_usuarios = df_usuarios_cpf()
            st.rerun()


@st.dialog("Alterar Usuários")
def edit_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Alterar Usuários</h1>", unsafe_allow_html=True)
    
    # escolher por cpf e editar a linha toda

@st.dialog("Excluir Usuários")
def excluir_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Excluir Usuários</h1>", unsafe_allow_html=True)
    
    # selecao por CPF


if __name__ == "__main__":
    main()
