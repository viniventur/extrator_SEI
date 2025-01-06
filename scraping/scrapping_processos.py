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


def converter_para_excel(df_processos):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_processos.to_excel(writer, index=False, sheet_name="Processos SEI - Unidades atuais")
        worksheet = writer.sheets["Processos SEI - Unidades atuais"]
        for col_idx, column in enumerate(df_processos.columns, start=1):
            max_length = max(
                df_processos[column].astype(str).map(len).max(),
                len(column)
            ) + 2
            col_letter = get_column_letter(col_idx)
            worksheet.column_dimensions[col_letter].width = max_length
    output.seek(0)
    return output.getvalue()

def buscar_dados_andamento(unidade, processos):
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
    tempo_estimado_total = total_processos * 4  # 6 segundos por processo
    minutos_estimados, segundos_estimados = divmod(tempo_estimado_total, 60)
    tempo_estimado_formatado = f"{int(minutos_estimados)}min {int(segundos_estimados)}s"
    st.write(f"Tempo estimado para concluir a busca: {tempo_estimado_formatado}")

    # Marca o início do processamento
    inicio = time.time()
    
    try:

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

            # Verificar se o processo não foi encontrado
            try:
                elemento_nao_encontrado = driver.find_element("xpath", '//*[@id="sbmPesquisar"]')
                if elemento_nao_encontrado.is_displayed():
                    processos.loc[processos['Processos'] == processo, ['Data Horário', 'Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição']] = [
                        "Processo Não Encontrado", "Processo Não Encontrado", "Processo Não Encontrado", "Processo Não Encontrado", "Processo Não Encontrado"
                    ]
                    continue
            except:
                pass  # Processo encontrado, continuar

            # Alternar para o iframe 'ifrArvore'
            try:
                iframe_arvore = driver.find_element('name', "ifrArvore")
                driver.switch_to.frame(iframe_arvore)
                driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span').click()  # Consultar andamento
            except:
                driver.switch_to.default_content()
                processos.loc[processos['Processos'] == processo, ['Data Horário', 'Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição']] = [
                    "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso"
                ]
                continue

            # Alternar para o iframe 'ifrVisualizacao'
            driver.switch_to.default_content()
            iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
            driver.switch_to.frame(iframe_visualizacao)
            
            time.sleep(tempo_medio)
            
            # Verificar se a unidade não tem acesso ao processo
            try:
                mensagem_sem_acesso = driver.find_element("xpath", '//*[@id="divMensagem"]/label')
                if mensagem_sem_acesso.is_displayed():
                    processos.loc[processos['Processos'] == processo, ['Data Horário', 'Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição']] = [
                        "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso", "Unidade Não Possui Acesso"
                    ]
                    driver.switch_to.default_content()
                    continue
            except:
                pass  # Unidade tem acesso, continuar

            # DADOS:
            processo_sei_format = num_processo_sei(driver.find_element(By.XPATH, '//*[@id="divInfraBarraLocalizacao"]').text) # coluna de Processo
            data_hora = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[1]').text  # Coluna de Data/Horário
            qnt_dias = cont_dias(data_hora, datetime.now())
            unidade_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[2]/a')
            unidade_abreviação = unidade_elemento.text # coluna de abrev unidade
            unidade_nome = unidade_elemento.get_attribute("title") # coluna de abrev unidade
            usuario_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[3]/a')
            usuario_cpf = usuario_elemento.text    # Coluna de Usuário CPF
            usuario = usuario_elemento.get_attribute("title") # Coluna de Usuário
            descricao = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[4]').text  # Coluna de Descrição

            # Atualiza os dados no DataFrame
            processos.loc[processos['Processos'] == processo, ['Processos', 'Data Horário', 'Qnt. Dias', 'Unidade Atual',
                                                                'Nome Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição'
                                                                ]] = [
                processo_sei_format, data_hora, qnt_dias, unidade_abreviação, unidade_nome, usuario_cpf, usuario, descricao
            ]

            # ordenando por dias de andamento:
            processos.sort_values(by='Qnt. Dias', ascending=True)

            # Voltar ao contexto principal
            driver.switch_to.default_content()

    except Exception as e:
        # Em caso de erro, exibe a mensagem e continua
        st.error(f"Erro durante o processamento: {e}")
        driver.switch_to.default_content()

    # Exportando em excel
    df_processos_xlsx = converter_para_excel(processos)

    # Botão de download do Excel
    botao_download = st.download_button(
        label="Clique aqui para baixar em Excel",
        data=df_processos_xlsx,
        file_name="processos_sei_unidade_atual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    dataframe_final = st.dataframe(processos, hide_index=True)

    return dataframe_final
