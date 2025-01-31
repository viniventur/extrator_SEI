from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import toml
import streamlit as st
import pandas as pd

from utils.config import data_hr_atual

# Carregar configurações do arquivo TOML
#config = toml.load('config.toml')

# secrets em variavel
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
        scopes=['https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
                ]
    )

    return build('drive', 'v3', credentials=credentials)

service = get_drive_service()

def list_login_files():
    LOGIN_FOLDER_ID = secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID']  # Adicionar o ID da pasta de login no .env
    login_files = service.files().list(
        q=f"'{LOGIN_FOLDER_ID}' in parents and name contains '.csv'",
        fields="files(id, name)",
        orderBy='createdTime desc'
    ).execute().get('files', [])
    if not login_files:
        st.error('Nenhum arquivo de login encontrado na pasta do Google Drive.')
        return None
    return login_files  # Pegar o arquivo mais recente


# Função para baixar arquivos do Google Drive pelo ID
def download_file_from_drive_id(file_id):
    try:
        request = service.files().get_media(fileId=file_id)
        response = request.execute()
        return BytesIO(response)
    except Exception as e:
        st.error(f'Erro ao baixar pasta: {e}')

# Criar pastas
def criar_pasta(name, parent_id=None):
    """
    Cria uma pasta no Google Drive.
    
    Args:
        service: Instância autenticada da API do Google Drive.
        name (str): Nome da pasta a ser criada.
        parent_id (str): ID da pasta pai (opcional).

    Returns:
        str: ID da pasta criada.
    """

    try:

        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]

        service.files().create(body=folder_metadata, fields='id').execute()
    except Exception as e:
        st.error(f'Erro ao baixar pasta: {e}')

# Enviar arquivos
def upload_csv(file_name, file_content_df, parent_id=None):
    """
    Faz o upload de um arquivo CSV para o Google Drive.
    
    Args:
        service: Instância autenticada da API do Google Drive.
        file_path (str): Caminho completo do arquivo local.
        file_name (str): Nome que o arquivo terá no Google Drive.
        parent_id (str): ID da pasta onde o arquivo será armazenado (opcional).
    
    Returns:
        str: ID do arquivo enviado.
    """
    try:
        file_metadata = {
            'name': file_name,
            'mimeType': 'text/csv',
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

                # Converter o DataFrame para CSV
        csv_buffer = BytesIO()
        file_content_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)

        # Fazer o upload do novo arquivo
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

    except Exception as e:
        st.error(f'Erro ao criar arquivo: {e}')        


# Função para baixar arquivos do Google Drive pelo NOME
def download_file_by_name(file_name, folder_id=None):
    """
    Baixa um arquivo do Google Drive pelo nome.
    
    Args:
        file_name (str): Nome do arquivo a ser baixado.
        folder_id (str, opcional): ID da pasta para restringir a busca.
    
    Returns:
        BytesIO: O conteúdo do arquivo como um objeto BytesIO.
    """
    try:
        # Define o query para busca
        query = f"name = '{file_name}'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        # Busca o arquivo pelo nome
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        if not files:
            st.error(f"Arquivo '{file_name}' não encontrado.")
            return None
        
        # Pega o ID do primeiro arquivo encontrado
        file_id = files[0]['id']
        
        # Faz o download do arquivo
        request = service.files().get_media(fileId=file_id)
        response = request.execute()
        return BytesIO(response)
    
    except Exception as e:
        st.error(f'Erro: {e}')
        return None

# Dados de permissao e tipo de acesso
#@st.cache_data(show_spinner=False)
def df_usuarios_cpf():
    try:
        #df = pd.read_csv(download_file_from_drive_id(secrets['google_credentials']['AUTORIZACAO_CPF_ID']), dtype=str)
        df = pd.read_csv(download_file_by_name('cpf_autorizados_extrator_sei', folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID']), dtype=str)
        st.session_state.data_atualizacao_users  = data_hr_atual()
        return df
    except Exception as e:
        st.error(f'Erro ao obter dados de acesso: {e}')

# Dados de historico de acesso
def df_historico_acesso():
    try:
        #df = pd.read_csv(download_file_from_drive_id(secrets['google_credentials']['AUTORIZACAO_CPF_ID']), dtype=str)
        df = pd.read_csv(download_file_by_name('acessos_extrator_sei', folder_id=secrets['google_credentials']['AUTORIZACAO_CPF_FOLDER_ID']), dtype=str)
        st.session_state.data_atualizacao_hist_acesso  = data_hr_atual()
        return df
    except Exception as e:
        st.error(f'Erro ao obter histórico de acesso: {e}')

# recarregar df de usuarios
def recarregar_usuarios():
    # Carregar os dados
    if st.session_state['reload_data']:
        df_usuarios = df_usuarios_cpf()  # Recarrega os dados
        st.session_state['reload_data'] = False
    else:
        df_usuarios = df_usuarios_cpf()  # Usa o cache, se não for recarregar

# Upload de arquivos para o drive
def upload_and_replace_file_drive(file_name, file_content_df, folder_id):
    """
    Faz o upload de um arquivo para o Google Drive, substituindo o arquivo com o mesmo nome se existir.
    
    Args:
        file_name (str): Nome do arquivo a ser salvo no Google Drive.
        file_content_df (DataFrame): Conteúdo do arquivo a ser enviado (como DataFrame).
        folder_id (str): ID da pasta no Google Drive onde o arquivo será salvo.
    
    Returns:
        dict: Informações do arquivo salvo (ID e nome).
    """
    try:
        # Buscar por arquivos com o mesmo nome na pasta
        query = f"name = '{file_name}' and '{folder_id}' in parents"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        if files:
            # Se o arquivo existir, apagar o antigo
            file_id = files[0]['id']
            service.files().delete(fileId=file_id).execute()
        
        # Converter o DataFrame para CSV
        csv_buffer = BytesIO()
        file_content_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)

        # Metadados do novo arquivo
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # Fazer o upload do novo arquivo
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        return uploaded_file

    except Exception as e:
        st.error(f'Erro ao fazer upload: {e}')
        return None


