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

def buscar_contagem_docs(unidade, processos):

    # Tempos para execução
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5

    driver = st.session_state.driver

    # Inicializa o indicador de progresso
    total_processos = len(processos)
    progresso = st.progress(0)  # Barra de progresso inicializada
    status_texto = st.empty()  # Espaço para exibir o texto de progresso
    cronometro_texto = st.empty()  # Espaço para o cronômetro

    # Calcula e exibe o tempo estimado
    tempo_medio_processo = 7 # segundos por processo
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
                processos.loc[processos['Processos'] == processo, 'Link do Processo'] = env['SITE_SEI'] if is_local() else st.secrets['SITE_SEI']
                continue   

            # =============================================
            # PROCESSO DE RASPAGEM
            # =============================================
            
        st.success('ok')

        return st.dataframe(processos)

            
        # # Alternar para o iframe 'ifrVisualizacao'
        # driver.switch_to.default_content()
        # iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
        # driver.switch_to.frame(iframe_visualizacao)
        # driver.find_element("xpath", '//*[@id="divArvoreAcoes"]/a[18]/img').click()
        # # Localizar os elementos com o texto "Formulário Contratação Direta PGE"
        # # Localizar a tabela com o ID "tblDocumentos"
        # tabela = driver.find_element(By.ID, "tblDocumentos")

        # # Localizar as células na tabela que contêm o texto "Formulário Contratação Direta"
        # celulas = tabela.find_elements(By.XPATH, ".//td[contains(text(), 'Formulário Utilização da Ata de Registro de Preço')]")


        # # Contar os elementos encontrados
        # quantidade = len(celulas)
        # print(f"Número de formulários encontrados: {quantidade}")

    except Exception as e:
        # Em caso de erro, exibe a mensagem e continua
        st.error(f"Erro durante o processamento: {e}")
        driver.switch_to.default_content()