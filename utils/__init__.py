from utils.config import (is_local, modulos, voltar_inicio, data_hr_atual)
from utils.chrome_config import chrome, update_download_directory
from utils.conn_gdriver import (
    get_drive_service,
    list_login_files,
    download_file_from_drive_id,
    criar_pasta,
    upload_csv,
    download_file_by_name,
    df_usuarios_cpf,
    df_historico_acesso,
    recarregar_usuarios,
    upload_and_replace_file_drive
)
from utils.conn_gsheets import obter_dados_usuarios, alterar_dados_usuario
from utils.file_utils import criar_pasta_os
from utils.login import lista_orgaos_login, login_sei
from utils.selenium_utils import excluir_driver, mudar_iframe, sair, verificar_acesso_processo
from utils.tipos_docs import tipos_documentos
from utils.validacao_dados import (
    num_processo_sei,
    tratar_processos_input,
    extrair_nome_sei,
    get_image_as_base64,
    validacao_cpf,
    converter_para_excel,
    cont_dias,
    tratamento_verif_users
)

import streamlit as st
secrets = st.secrets