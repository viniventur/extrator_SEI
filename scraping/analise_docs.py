import pandas as pd
import os
import tempfile
from openpyxl.utils import get_column_letter
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils import *
from scraping.extracao_unidade import *

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

        # # Remove a primeira entrada do dicionário (se necessário)
        # if documents_dict:
        #     proc_chave = next(iter(documents_dict))  # Obtém a primeira chave
        #     proc_element = documents_dict[proc_element]
        #     del documents_dict[proc_element] # deletar o num de processo

        return documents_dict

    except Exception as e:
        st.error(f"Erro durante a obtenção dos documentos do processo: {e}")


def baixar_docs_analise(docs_selecionados, temp_dir):

    # Tempos para execução
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5
                        
    update_download_directory(temp_dir)

    driver = st.session_state.driver
    driver.refresh() #voltar a pagina inicial do processo
    time.sleep(tempo_medio)
   
    # Clicar para imprimir
    mudar_iframe('visualizacao')

    # Esperar até que o botão "Gerar Arquivo PDF do Processo" esteja visível e clicável
    pdf_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//img[@alt="Gerar Arquivo PDF do Processo"]'))
    )
    pdf_button.click()

    # Esperar até que o checkbox "Selecionar Tudo" esteja presente na página
    checkbox_selecionar_tudo = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="imgInfraCheck"]'))
    )
    for _ in range(2):  # Melhorando a legibilidade do loop
        checkbox_selecionar_tudo.click()

    # Localizar a tabela de documentos
    tabela_xpath = '//*[@id="tblDocumentos"]/tbody/tr'
    
    # Encontrar todas as linhas da tabela
    linhas = driver.find_elements(By.XPATH, tabela_xpath)
    total_linhas = len(linhas)  # Obtém o número real de linhas

    st.write(f"Total de linhas encontradas: {total_linhas}")

    # Percorrer os documentos selecionados
    for doc in docs_selecionados:
        
        # Filtra apenas o número do documento
        match = re.search(r'\((\d+)\)$', doc)  # Agora garantindo que o número está no final da string
        if match:
            numero_doc = match.group(1)
            st.write(f"Procurando documento: {numero_doc}")
        else:
            st.error(f"Número de documento inválido em: {doc}")
            continue  # Pula para o próximo documento

        # Percorre a tabela, garantindo que não ultrapasse o número real de linhas
        for index in range(2, total_linhas + 1):  # Agora garantimos que os índices são válidos
            
            try:
                # Construindo dinamicamente o XPath da célula que contém o número SEI
                num_xpath = f'//*[@id="tblDocumentos"]/tbody/tr[{index}]/td[2]/a'
                elementos = driver.find_elements(By.XPATH, num_xpath)  # Retorna uma lista

                if not elementos:  # Se a lista estiver vazia, o elemento não existe
                    st.warning(f"Elemento {num_xpath} não encontrado, pulando para o próximo.")
                    continue  # Pula para o próximo índice

                numero_documento = elementos[0].text  # Pega o texto do primeiro elemento encontrado

                # Verifica se o número do documento corresponde ao que estamos buscando
                if numero_documento == numero_doc:
                    checkbox_xpath = f'//*[@id="chkInfraItem{index - 2}"]'  # Ajuste para alinhar com os checkboxes
                    checkbox = driver.find_element(By.XPATH, checkbox_xpath)
                    
                    # Verifica se o checkbox não está marcado antes de clicar
                    if not checkbox.is_selected():
                        checkbox.click()
                        st.success(f"Checkbox do documento {numero_documento} marcado.")
                    else:
                        st.info(f"Checkbox do documento {numero_documento} já estava marcado.")

            except Exception as e:
                st.error(f"Erro ao selecionar documento {numero_doc} na linha {index}: {e}")

    # Baixar
    try:
        driver.find_element('xpath', '//*[@id="divInfraBarraComandosSuperior"]/button[1]').click()
        mudar_iframe('default')
        WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, '//*[@id="spnInfraAviso"]'))
        )
        time.sleep(tempo_longo)
    except Exception as e:
        st.error(f"Erro baixar os documentos: {e}")


def pdf_to_mrkd(pdf_path):

    # Ler os arquivos
    source = pdf_path 
    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown()


