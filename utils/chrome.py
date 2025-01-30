from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.funcoes_auxiliares import *
import streamlit as st
import tempfile
import json


def chrome():

    # if para inicializacao - se nao tiver usuario definido, rodar sem pasta download
    if 'usuario_sei' not in st.session_state:
        st.session_state.diretorio_download = '.'
    else:
        # Criacao da pasta temporaria para downloads apenas para o usuario
        pasta_nome = f"{st.session_state.usuario_sei}_temporaria"

        # diretorio if local ou nuvem:
        if is_local():
            # verifica se ja existe e apaga
            diretorio = r'C:\Users\vinicius.ventura\OneDrive\CGE\extrator_SEI\testes_download'
            caminho_pasta = os.path.join(diretorio, pasta_nome)
            if os.path.exists(caminho_pasta):
                st.session_state.diretorio_download = caminho_pasta
                # excluir os arquivos remanscente de outras sessoes
                for item in os.listdir(st.session_state.diretorio_download):
                    item_path = os.path.join(st.session_state.diretorio_download, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)  # Remove arquivos
            else:
                # cria a pasta
                criar_pasta(diretorio, pasta_nome)
                st.session_state.diretorio_download = caminho_pasta
        else:
            # verifica se ja existe e apaga
            diretorio = '/tmp/'
            caminho_pasta = os.path.join(diretorio, pasta_nome)
            if os.path.exists(caminho_pasta):
                st.session_state.diretorio_download = caminho_pasta
            else:
                # cria a pasta
                criar_pasta(diretorio, pasta_nome)
                st.session_state.diretorio_download = caminho_pasta

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--kiosk-printing')  # Imprime diretamente sem exibir a janela
    settings_save_pdf = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    chrome_prefs = {
        "printing.print_preview_sticky_settings.appState": json.dumps(settings_save_pdf),
        "savefile.default_directory": st.session_state.diretorio_download,  # Define o local onde o PDF será salvo
        "download.default_directory": st.session_state.diretorio_download,  # Define o local onde o PDF será salvo - downloads pdfviewer
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    if is_local():
        service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def update_download_directory(new_dir):
    """Atualiza o diretório de download usando Chrome DevTools Protocol (CDP)."""
    if 'driver' in st.session_state:
        st.session_state.driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": new_dir
            }
        )
        st.session_state.temp_dir = new_dir
        st.success(f"Diretório de download atualizado para: {new_dir}")
    else:
        st.error('Driver não encontrado.')