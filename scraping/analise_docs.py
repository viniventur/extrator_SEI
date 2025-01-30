import pandas as pd
import os
import tempfile
from openpyxl.utils import get_column_letter
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from scraping.extracao_unidade import *
from utils.funcoes_auxiliares import *

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import warnings
warnings.filterwarnings('ignore')
import time
from datetime import datetime
from io import BytesIO
from docling.document_converter import DocumentConverter
import re


def raspagem_docs(processo, unidade):
    try:
        # Tempos para execução
        tempo_curto = 0.5
        tempo_medio = 1
        tempo_longo = 1.5

        driver = st.session_state.driver

        mudar_iframe('default')

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)

        # Busca dos processos
        time.sleep(tempo_medio)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(processo)
        time.sleep(tempo_curto)
        driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(Keys.ENTER)
        time.sleep(tempo_curto)

        # =============================================
        # VERIFICANDO A EXISTENCIA OU ACESSO AO PROCESSO
        # =============================================

        status, mensagem = verificar_acesso_processo(processo)

        if not status:
            st.error(mensagem)
            return

        # =============================================
        # raspagem documentos
        # =============================================

        mudar_iframe('arvore')

        # Localizar todos os elementos de abertura de pastas e clicar
        elements = driver.find_elements(By.XPATH, "//*[contains(@id, 'ancjoinPASTA')]")

        # Iterar sobre os elementos encontrados e clicar em cada um
        for element in elements[:-1]:
            element.click()
            time.sleep(tempo_curto)

            # Aguarda o desaparecimento do elemento com ID que começa com "spanAGUARDE"
            try:
                WebDriverWait(driver, 30).until(
                    EC.invisibility_of_element((By.XPATH, "//*[starts-with(@id, 'spanAGUARDE')]"))
                )
            except:
                st.error("O SEI não respondeu a tempo. Tente novamente.")
                
        document_elements = driver.find_elements(By.XPATH, "//span[starts-with(@id, 'span') and not(contains(@id, 'PASTA'))]")

        # Criar um dicionário com o texto (nome do documento) como chave e o elemento como valor
        documents_dict = {
            element.text: element
            for element in document_elements if element.text  # Ignora spans vazios
        }

        # Remove a primeira entrada do dicionário (se necessário)
        if documents_dict:
            first_key = next(iter(documents_dict))  # Obtém a primeira chave
            del documents_dict[first_key] # deletar o num de processo

        return documents_dict

    except Exception as e:
        st.error(f"Erro durante a obtenção dos documentos do processo: {e}")

def baixar_docs_analise(doc_elemento, temp_dir):

    update_download_directory(temp_dir)

    driver = st.session_state.driver

    # Selecionar o documento
    mudar_iframe('arvore')
    doc_elemento.click()

    # Clicar para imprimir
    mudar_iframe('visualizacao')

    try:
        try:
            # Verifica se o primeiro elemento existe
            st.write('teste1')
            elemento_imprimir = driver.find_element(By.XPATH, '//img[@alt="Imprimir Web"]')
            time.sleep(5)
            elemento_imprimir.click()
            st.write('teste2')
            # Baixar o documento se nao for anexo
            try:
                st.write('teste4')
                time.sleep(3)
                # pegar arquivo no download de PDFs imprimidos
                if not os.path.exists(st.session_state.diretorio_download):
                    st.error(f"Erro: O diretório '{st.session_state.diretorio_download}' não existe.")
                    return

                # Pegando o primeiro arquivo do diretório
                arquivos = [f for f in os.listdir(st.session_state.diretorio_download)]

                if not arquivos:
                    print("Nenhum arquivo encontrado na pasta.")
                    return None
                
                st.write(f'arquivos: {arquivos}')
                st.write('teste')

                # Encontrar o arquivo baixado
                arquivo_escolhido = os.path.join(st.session_state.diretorio_download, arquivos[0])
                st.write(f"Arquivo encontrado: {arquivo_escolhido}")
                st.write(os.path.isfile(arquivo_escolhido))

                # Abrir o arquivo e baixar (necessita apenas abrir)
                driver.get(arquivo_escolhido)


                # Excluir o arquivo na pasta temporaria do diretorio
                os.remove(arquivo_escolhido)  # Remove arquivos
            except Exception as e:
                st.error(f'Erro ao baixar documento (documento SEI): {e}')
                
        except NoSuchElementException:
            try:
                # Caso o primeiro elemento não exista, verifica o segundo
                elemento_informacao = driver.find_element(By.XPATH, '//*[@id="divInformacao"]/a')
                
                # Verifica se o texto do elemento contém "aqui"
                if "aqui" in elemento_informacao.text.lower():  # Ignora case sensitivity
                    elemento_informacao.click()

                else:
                    st.error("Erro ao baixar documento (anexo).")
                    return
            except NoSuchElementException:
                # Caso nenhum dos elementos seja encontrado
                st.error("Erro ao baixar documento.")


    except Exception as e:
        st.error(f'Erro ao baixar documento (aba): {e}')


def pdf_to_mrkd(pdf_path):

    # Ler os arquivos
    source = pdf_path 
    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown()


