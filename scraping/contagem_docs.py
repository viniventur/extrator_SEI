import pandas as pd
import os
from openpyxl.utils import get_column_letter
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from scraping.extracao_unidade import *
from utils.funcoes_auxiliares import *

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import warnings
warnings.filterwarnings('ignore')
import time
from datetime import datetime
from io import BytesIO
import re

def buscar_contagem_docs(unidade, processos, docs):

    # Tempos para execução
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5

    driver = st.session_state.driver

    # Inicializa o indicador de progresso - PROCESSO
    total_processos = len(processos)
    progresso = st.progress(0)  # Barra de progresso inicializada
    status_texto = st.empty()  # Espaço para exibir o texto de progresso

    cronometro_texto = st.empty()  # Espaço para o cronômetro

    # Calcula e exibe o tempo estimado
    tempo_medio_processo = 5 # segundos por processo
    tempo_estimado_total = total_processos * tempo_medio_processo
    minutos_estimados, segundos_estimados = divmod(tempo_estimado_total, 60)
    tempo_estimado_formatado = f"{int(minutos_estimados)}min {int(segundos_estimados)}s"
    st.write(f"Tempo estimado para concluir a busca: {tempo_estimado_formatado}")

    # Marca o início do processamento
    inicio = time.time()

    try:
        
        mudar_iframe('default')

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)
                    
        for i, processo in enumerate(processos['Processos'], start=1):

            # Atualiza o cronômetro
            tempo_decorrido = time.time() - inicio
            horas, resto = divmod(tempo_decorrido, 3600)
            minutos, segundos = divmod(resto, 60)
            tempo_formatado = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}"
            cronometro_texto.text(f"Tempo de execução: {tempo_formatado}")

            # Atualiza o texto e a barra de progresso
            progresso.progress(i / total_processos)
            status_texto.text(f"Buscando dados dos processos: {i} de {total_processos}.")

            mudar_iframe('default')

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
                processos.loc[processos['Processos'] == processo, processos.drop('Processos', axis=1).columns] = mensagem
                continue   

            # =============================================
            # PROCESSO DE RASPAGEM
            # =============================================

            mudar_iframe('visualizacao')
            driver.find_element("xpath", '//img[@alt="Gerar Arquivo PDF do Processo"]').click()
            tabela_documentos = driver.find_element(By.ID, "tblDocumentos")

            for doc in docs:

                # Localizar as células na tabela que contêm o texto "Formulário Contratação Direta"
                celulas = tabela_documentos.find_elements(By.XPATH, f".//td[contains(text(), '{doc}')]")

                # Contar os elementos encontrados
                quantidade = len(celulas)
                processos.loc[processos['Processos'] == processo, doc] = quantidade

    except Exception as e:
        # Em caso de erro, exibe a mensagem e continua
        st.error(f"Erro durante o processamento: {e}")
        driver.switch_to.default_content()

    # organizando para o display
    processos_display = processos.copy()

    # Exportando em excel
    df_processos_xlsx = converter_para_excel(processos, "Processos SEI - Unidades atuais")

    # Botão de download do Excel
    botao_download = st.download_button(
        label="Clique aqui para baixar em Excel",
        data=df_processos_xlsx,
        file_name="processos_sei_unidade_atual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    dataframe_final = st.dataframe(processos_display,
                                hide_index=True
                            )

    return dataframe_final
