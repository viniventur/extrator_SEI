from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.funcoes_auxiliares import *
import streamlit as st
import tempfile



def chrome():

    if 'temp_dir' not in st.session_state:
        st.session_state['temp_dir'] = tempfile.mkdtemp()


    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--kiosk-printing')  # Imprime diretamente sem exibir a janela

    if st.session_state.temp_dir:
        chrome_prefs = {
            "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":""}],"selectedDestinationId":"Save as PDF","version":2}',
            "savefile.default_directory": st.session_state.temp_dir,  # Define o local onde o PDF será salvo
            "download.default_directory": st.session_state.temp_dir,  # Define o local onde o PDF será salvo - downloads pdfviewer
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        }
    else:
        chrome_prefs = {
            "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":""}],"selectedDestinationId":"Save as PDF","version":2}',
            "savefile.default_directory": r"C:\Users\vinicius.ventura\OneDrive\CGE\extrator_SEI\testes_download",  # Define o local onde o PDF será salvo
            "download.default_directory": r"C:\Users\vinicius.ventura\OneDrive\CGE\extrator_SEI\testes_download",  # Define o local onde o PDF será salvo - downloads pdfviewer
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