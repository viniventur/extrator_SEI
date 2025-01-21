from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import toml
import streamlit as st
import pandas as pd

# Carregar configurações do arquivo TOML
#config = toml.load('config.toml')
secrets = st.secrets

# Caminho para o arquivo de credenciais da conta de serviço
CREDENTIALS_FILE = json.loads(secrets['google_credentials']['CREDENTIALS_FILE'])


# ID da pasta do Google Drive onde estão os dados "dataset_despesas_detalhado"
AUTORIZACAO_CPF_FOLDER_ID = secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID']


# ID da pasta do Google Drive onde estão os dados "contratos"
# AUTORIZACAO_CPF_ID = secrets['CONTRATOS_FOLDER_ID']

# Função para autenticar e construir o serviço Google Drive API
def get_drive_service():
    # Carregar o JSON como um dicionário do .env
    credentials_info = json.loads(secrets['google_credentials']['CREDENTIALS_FILE'])

    # Usar from_service_account_info para passar o dicionário em vez de um arquivo
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    return build('drive', 'v3', credentials=credentials)


def list_login_files():
    g_service = get_drive_service()
    LOGIN_FOLDER_ID = secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID']  # Adicionar o ID da pasta de login no .env
    login_files = g_service.files().list(
        q=f"'{LOGIN_FOLDER_ID}' in parents and name contains '.csv'",
        fields="files(id, name)",
        orderBy='createdTime desc'
    ).execute().get('files', [])
    if not login_files:
        st.error('Nenhum arquivo de login encontrado na pasta do Google Drive.')
        return None
    return login_files  # Pegar o arquivo mais recente


# Função para baixar arquivos do Google Drive
def download_file_from_drive(file_id):
    try:
        g_service = get_drive_service()
        request = g_service.files().get_media(fileId=file_id)
        response = request.execute()
        return BytesIO(response)
    except Exception as e:
        st.error(f'Erro: {e}')

@st.cache_data(show_spinner=False)
def df_usuarios_cpf():
    try:
        df = pd.read_csv(download_file_from_drive(secrets['google_credentials']['AUTORIZACAO_CPF_ID']), dtype=str)
        return df
    except Exception as e:
        st.error(f'Erro ao obter acesso: {e}')


def upload_file_to_drive(file_name, file_content, folder_id):
    """
    Faz o upload de um arquivo para o Google Drive.
    
    Args:
        file_name (str): Nome do arquivo a ser salvo no Google Drive.
        file_content (BytesIO): Conteúdo do arquivo a ser enviado.
        folder_id (str): ID da pasta no Google Drive onde o arquivo será salvo.
    
    Returns:
        dict: Informações do arquivo salvo (ID e nome).
    """
    try:
        # Autenticar o serviço do Google Drive
        g_service = get_drive_service()

        # Metadados do arquivo
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # Realizar o upload
        media = MediaIoBaseUpload(file_content, mimetype='application/octet-stream') # testar depois com text/csv
        uploaded_file = g_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        return uploaded_file
    except Exception as e:
        st.error(f'Erro ao fazer upload: {e}')
        return None
    

