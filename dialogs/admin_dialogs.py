import pandas as pd
import plotly.express as px
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values

secrets = st.secrets

from sidebar import *

import warnings
import base64
import time
import locale


@st.dialog("Adicionar Usuários", width='large')
def add_user():
    st.markdown("<h1 style='text-align: center; font-size: 20px;'>Insira os Dados:</h1>", unsafe_allow_html=True)
    acessos = ['USUARIO', 'ADMIN']

    lista_orgaos = lista_orgaos_login()
    lista_orgaos.pop(0)
    lista_orgaos.insert(0, "Selecione o Orgão")

    # cpf_selecionado = st.selectbox("Selecione o CPF do usuário para alterar:", df_usuarios_select, placeholder='Selecione um CPF')

    df_add_users = pd.DataFrame({"CPF": ["Insira o CPF"], "APELIDO": ['Insira um Apelido'], "ORGAO": ["Selecione o Orgão"], "ACESSO": ['USUARIO']})
    add_df = st.data_editor(
        df_add_users,
        column_config={
            "ACESSO": st.column_config.SelectboxColumn(
                "ACESSO", width="medium", options=acessos, default='USUARIO', required=True
            ),
            "CPF": st.column_config.TextColumn(
                "CPF", max_chars=11, validate=r"^\d{11}$", default='Insira o CPF'
            ),
            "APELIDO": st.column_config.TextColumn(
                "APELIDO", validate=r"^[A-Za-z]*$", default='Insira um Apelido'
            ),
            "ORGAO": st.column_config.SelectboxColumn(
                "ORGAO", width="medium", options=lista_orgaos, default='Selecione o Orgão', required=True
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
                add_df = tratamento_verif_users(add_df, df_usuarios) # tratamento e verificacoes
                if add_df is None:
                    return
                
                add_df['ULTIMO_ACESSO'] = "NAO_ACESSOU"

                df_adicionado = pd.concat([df_usuarios, add_df], axis=0, ignore_index=True)
                upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_adicionado, folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
                st.success("Usuários adicionados com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f'Erro ao atualizar dados: {e}')

############################################

@st.dialog("Alterar Usuários", width='large')
def edit_user():

    lista_orgaos = lista_orgaos_login()
    lista_orgaos.pop(0)
    lista_orgaos.insert(0, "Selecione o Orgão")

    df_usuarios = df_usuarios_cpf()
    df_usuarios_select = df_usuarios['CPF'].tolist()
    df_usuarios_select.insert(0, " ")
    cpf_selecionado = st.selectbox("Selecione o CPF do usuário para alterar:", df_usuarios_select, placeholder='Selecione um CPF')

    if cpf_selecionado != " ":

        st.markdown("<h1 style='text-align: center; font-size: 20px;'>Altere os Dados:</h1>", unsafe_allow_html=True)

        df_cpf_select = df_usuarios.loc[df_usuarios['CPF'] == cpf_selecionado].drop(columns='ULTIMO_ACESSO') # df do cpf selecionado

        acessos = ['USUARIO', 'ADMIN']

        edit_df = st.data_editor(
            df_cpf_select,
            column_config={
                "ACESSO": st.column_config.SelectboxColumn(
                    "ACESSO", width="medium", options=acessos, default='USUARIO', required=True
                ),
                "CPF": st.column_config.TextColumn(
                    "CPF", max_chars=11, validate=r"^\d{11}$", default='Insira o CPF'
                ),
                "APELIDO": st.column_config.TextColumn(
                    "APELIDO", validate=r"^[A-Za-z]*$", default='Insira um Apelido'
                ),
                "ORGAO": st.column_config.SelectboxColumn(
                    "ORGAO", width="medium", options=lista_orgaos, default='Selecione o Orgão', required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows='fixed'
        ) # df edicao

        if st.button(':material/edit: Editar Usuários', use_container_width=True):

            with st.spinner('Editando usuário...'):
                try:
                    df_usuarios = df_usuarios_cpf()

                    # Verificar se não houve alteração
                    if df_cpf_select[['CPF', 'APELIDO', 'ORGAO', 'ACESSO']].equals(edit_df[['CPF', 'APELIDO', 'ORGAO', 'ACESSO']]):
                        st.error('Não há alterações.') 
                        return
                    
                    # verificar se o cpf foi alterado
                    if cpf_selecionado != edit_df['CPF'].values:

                        edit_df = tratamento_verif_users(edit_df, df_usuarios) # tratamento e verificacoes
                        if edit_df is None:
                            return
                    else: # Verificacoes sem alteracao no CPF
                        # Verificar se o orgao foi inserido
                        orgao_teste_df = edit_df[edit_df["ORGAO"] != "Selecione o Orgão"]
                        if len(orgao_teste_df) < 1:
                            st.error('Usuários sem órgão informado:')
                            st.dataframe(
                                edit_df.loc[edit_df["ORGAO"] == "Selecione o Orgão", ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
                                use_container_width=True,
                                hide_index=True
                            )
                            return None

                        # Verifica usuarios sem apelidos
                        orgao_teste_df = edit_df[(edit_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                                                 (edit_df["APELIDO"].str.strip() == "") | 
                                                 (edit_df["APELIDO"] == " ")]
                        if len(orgao_teste_df) > 0 :
                            st.error('Usuários sem apelidos informado:')
                            st.dataframe(
                                edit_df.loc[(edit_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                                            (edit_df["APELIDO"].str.strip() == "") | 
                                            (edit_df["APELIDO"] == " "),
                                            ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
                                use_container_width=True,
                                hide_index=True
                            )
                            return None
                                            
                    # Modificando o df original
                    df_usuarios = df_usuarios_cpf()
                    df_usuarios.loc[df_usuarios['CPF'] == cpf_selecionado, ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']] = edit_df[['CPF', 'APELIDO', 'ORGAO', 'ACESSO']].values

                    upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_usuarios, folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
                    st.success("Usuário editado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f'Erro ao editar os dados: {e}')

############################################

@st.dialog("Excluir Usuários", width='large')
def excluir_user():
    
    df_usuarios = df_usuarios_cpf()
    df_usuarios_select = df_usuarios['CPF'].tolist()
    df_usuarios_select.insert(0, " ")
    cpf_selecionado = st.selectbox("Selecione o CPF do usuário para excluir:", df_usuarios_select, placeholder='Selecione um CPF')

    if cpf_selecionado != " ":

        st.write('Confira os dados a serem excluídos:')

        df_cpf_select = df_usuarios.loc[df_usuarios['CPF'] == cpf_selecionado] # df do cpf selecionado

        st.dataframe(df_cpf_select,
                        use_container_width=True,
                        hide_index=True
                    )

        if st.button(':material/delete: Excluir Usuários', use_container_width=True):

            with st.spinner('Excluindo usuário...'):
                try:
                    df_usuarios = df_usuarios_cpf()
                    
                    # Modificando o df original
                    df_usuarios = df_usuarios.loc[df_usuarios['CPF'] != cpf_selecionado]

                    upload_and_replace_file_drive('cpf_autorizados_extrator_sei', df_usuarios, folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID'])
                    st.success("Usuário editado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f'Erro ao excluir os dados: {e}')