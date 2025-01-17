from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

def obter_dados_usuarios():
    # conexao com a base de usuarios no google sheets
    conn = st.connection('gsheets', type=GSheetsConnection)
    data = conn.read(spreadsheet='cpf_autorizados_extrator_sei', worksheet='autorizacao_cpf')
    data['CPF'] = data['CPF'].apply(lambda x: f"{int(x):011d}")
    return data

def alterar_dados_usuario(dados):
    conn = st.connection('gsheets', type=GSheetsConnection)
    conn.update(spreadsheet='cpf_autorizados_extrator_sei', worksheet='autorizacao_cpf', data=dados)