import pandas as pd
from openpyxl.utils import get_column_letter
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from chrome import *
from extracao_unidade import *
from tratamento_processos import *
from scrapping_processos import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pyautogui
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
import time
from io import BytesIO

def main():

    driver = st.session_state.driver
    st.set_page_config(page_title='Extrator de dados - SEI - OGP/CGE', page_icon='src/assets/Identidades visual/OGP/LOGO-OGP - icon.jpg', initial_sidebar_state="collapsed")

    # Aplicar CSS para esconder o sidebar
    hide_sidebar_style = """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)

    if st.button("Voltar ao Início"):
        driver.quit()
        st.switch_page('inicio.py')

    with st.container():
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
                <h1 style="font-size: 50px; margin: 0;">Extração dos Dados</h1>
            </div>
            """,
            unsafe_allow_html=True
        )



    # adicionar input para a unidade (lista de seleção)
    with st.spinner('Carregando unidades disponíveis no SEI...'):
        lista_unidades = lista_unidades_sei()
        unidade = st.selectbox('Selecione a Unidade', lista_unidades)

    lista_processos = st.text_area('Informe os Processos')
              
    if st.button("Buscar dados dos processos inseridos"):
        if lista_processos:
            with st.spinner('Buscando dados, aguarde...'):
                resultado, total_linhas, linhas_validas = tratar_processos(lista_processos)

                # Criação do DataFrame
                resultado = [linha.strip() for linha in resultado.splitlines() if linha.strip()]

                # 2. Cria o DataFrame
                df_processos = pd.DataFrame({"Processos": resultado})

                st.subheader("Tabela de Processos:")
                buscar_dados(df_processos)

                # Criando excel
                # Função para converter DataFrame em Excel
                def converter_para_excel(df_processos):
                    output = BytesIO()  # Cria um buffer de memória

                    # Gera o arquivo Excel
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_processos.to_excel(writer, index=False, sheet_name="Processos SEI - Unidades atuais")
                        
                        # Ajusta a largura das colunas
                        worksheet = writer.sheets["Processos SEI - Unidades atuais"]
                        for col_idx, column in enumerate(df_processos.columns, start=1):
                            # Calcula o tamanho máximo da coluna (inclui o cabeçalho e os dados)
                            max_length = max(
                                df_processos[column].astype(str).map(len).max(),  # Tamanho máximo dos valores da coluna
                                len(column)  # Tamanho do nome da coluna (cabeçalho)
                            ) + 2  # Adiciona margem para evitar corte
                            col_letter = get_column_letter(col_idx)  # Converte índice da coluna para letra
                            worksheet.column_dimensions[col_letter].width = max_length  # Ajusta a largura da coluna

                    output.seek(0)  # Move o cursor do buffer para o início
                    return output.getvalue()  # Retorna o conteúdo em bytes
                
                df_processos_xlsx = converter_para_excel(df_processos)

                st.download_button(
                    label="Clique aqui para baixar em excel",
                    data=df_processos_xlsx,
                    file_name="processos_sei_unidade_atual.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("Por favor, insira os números de processos para tratamento.")


if __name__ == "__main__":
    main()