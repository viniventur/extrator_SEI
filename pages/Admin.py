import pandas as pd
import os
import streamlit as st
from utils.conn_gsheets import *
from dotenv import load_dotenv, dotenv_values
from utils.login import *
from utils.chrome import *
from utils.funcoes_auxiliares import *
from sidebar import *
from utils.conn_gdriver import *
import warnings
import base64
import time

# Configurações Gerais
warnings.filterwarnings('ignore')
env = dotenv_values('.env')

st.set_page_config(page_title='Extrator de dados do SEI - OGP/CGE', 
                   page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png')

# Verificação Inicial
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

# Config Layout (local ou online)
hide_style = """ """
if not is_local():
    hide_style = """
    <style>
    #MainMenu {visibility: hidden}
    header {visibility: hidden}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# Tratamento e verificacoes de dados de acesso
def tratamento_verif_users(add_df):
    add_df = add_df[add_df["CPF"] != "Insira o CPF"]

    if len(add_df) < 1:
        st.error('Insira dados para adicionar usuários.')
        return None

    # Validação de CPF
    add_df["CPF_VALIDACAO"] = add_df["CPF"].apply(validacao_cpf)
    if any(~add_df["CPF_VALIDACAO"]):
        st.error('Os dados contêm CPFs inválidos:')
        st.dataframe(
            add_df.loc[~add_df["CPF_VALIDACAO"], ['CPF', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verifica duplicados com acessos diferentes
    duplicados_diferentes = add_df.groupby('CPF')['ACESSO'].nunique()
    cpf_diferentes = duplicados_diferentes[duplicados_diferentes > 1].index
    if not cpf_diferentes.empty:
        st.error('CPF duplicados com acessos diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes)][['CPF', 'ACESSO']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verificar duplicidade na base de dados
    df_usuarios = df_usuarios_cpf()
    if add_df["CPF"].isin(df_usuarios["CPF"]).any():
        st.error("Os CPFs abaixo já constam na base.")
        st.dataframe(
            add_df.loc[add_df["CPF"].isin(df_usuarios["CPF"])][['CPF', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None

    return add_df.drop_duplicates(subset=['CPF'])[['CPF', 'ACESSO']]

# Funções Principais
def main():
    st.session_state.pag = 'ADMIN'

    run_sidebar()
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

    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Configuração de Usuários e Acessos</h1>", unsafe_allow_html=True)

    if 'reload_data' not in st.session_state:
        st.session_state['reload_data'] = False

    cols = st.columns(3)
    with cols[0]:
        if st.button(':material/add: Adicionar', use_container_width=True):
            add_user()

    with cols[1]:
        if st.button(':material/edit: Alterar', use_container_width=True):
            edit_user()

    with cols[2]:
        if st.button(':material/delete: Excluir', use_container_width=True):
            excluir_user()

    if st.button(':material/refresh: Atualizar', use_container_width=True):
        st.session_state['reload_data'] = True
        st.cache_data.clear()
        st.rerun()

    if st.session_state['reload_data']:
        df_usuarios = df_usuarios_cpf()
        st.session_state['reload_data'] = False
    else:
        df_usuarios = df_usuarios_cpf()

    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

@st.dialog("Adicionar Usuários")
def add_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Insira os Dados:</h1>", unsafe_allow_html=True)
    acessos = ['USUARIO', 'ADMIN']

    df_add_users = pd.DataFrame({"CPF": ["Insira o CPF"], "ACESSO": ['USUARIO']})
    add_df = st.data_editor(
        df_add_users,
        column_config={
            "ACESSO": st.column_config.SelectboxColumn(
                "ACESSO", width="medium", options=acessos, default='USUARIO', required=True
            ),
            "CPF": st.column_config.TextColumn(
                "CPF", max_chars=11, validate=r"^\d{11}$", default='Insira o CPF'
            )
        },
        hide_index=True,
        use_container_width=True,
        num_rows='dynamic'
    )

    if st.button(':material/add: Adicionar Usuários', use_container_width=True):
        with st.spinner('Adicionando usuários...'):
            try:
                df_usuarios = df_usuarios_cpf()
                add_df = tratamento_verif_users(add_df) # tratamento e verificacoes
                if add_df is None:
                    return

                df_adicionado = pd.concat([df_usuarios, add_df], axis=0, ignore_index=True)
                upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_adicionado, folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
                st.success("Usuários adicionados com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f'Erro ao atualizar dados: {e}')

@st.dialog("Alterar Usuários")
def edit_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Alterar Usuários</h1>", unsafe_allow_html=True)
    # Implementação futura

@st.dialog("Excluir Usuários")
def excluir_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Excluir Usuários</h1>", unsafe_allow_html=True)
    # Implementação futura

if __name__ == "__main__":
    main()
