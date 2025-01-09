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


def mudar_iframe(iframe):

    driver = st.session_state.driver

    if (iframe == 'arvore'):

        driver.switch_to.default_content()
        iframe_arvore = driver.find_element('name', "ifrArvore")
        driver.switch_to.frame(iframe_arvore)

    elif (iframe == 'visualizacao'):

        driver.switch_to.default_content()
        iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
        driver.switch_to.frame(iframe_visualizacao)


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
    tempo_medio_processo = 7 # segundos por processo
    tempo_estimado_total = total_processos * tempo_medio_processo
    minutos_estimados, segundos_estimados = divmod(tempo_estimado_total, 60)
    tempo_estimado_formatado = f"{int(minutos_estimados)}min {int(segundos_estimados)}s"
    st.write(f"Tempo estimado para concluir a busca: {tempo_estimado_formatado}")

    # Marca o início do processamento
    inicio = time.time()
    
    try:

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)

        colunas_sem_processo = ['Data Horário', 'Qnt. Dias', 'Concluído', 'Unidade Atual',
            'Nome Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição', 'Processo aberto nas unidades', 'Link do Processo'
            ]

        colunas = ['Processos'] + colunas_sem_processo
        
        processos[colunas_sem_processo] = ''
        
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

            # Verificar se o processo não foi encontrado
            try:
                elemento_nao_encontrado = driver.find_element("xpath", '//*[@id="sbmPesquisar"]')
                if elemento_nao_encontrado.is_displayed():
                    processos.loc[processos['Processos'] == processo, colunas_sem_processo] = "Processo Não encontrado"
                    continue
            except:
                pass  # Processo encontrado, continuar

            # Alternar para o iframe 'ifrArvore'
            try:
                mudar_iframe('arvore')
                driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span')  # Consultar andamento
            except:
                driver.switch_to.default_content()
                processos.loc[processos['Processos'] == processo, colunas_sem_processo] = "Unidade Não Possui Acesso"
                continue

            # Alternar para o iframe 'ifrVisualizacao'
            mudar_iframe('visualizacao')
            time.sleep(tempo_longo)
            
            # Verificar se a unidade não tem acesso ao processo
            try:
                mensagem_sem_acesso = driver.find_element("xpath", '//*[@id="divMensagem"]/label')
                if mensagem_sem_acesso.is_displayed():
                    processos.loc[processos['Processos'] == processo, colunas_sem_processo] = "Unidade Não Possui Acesso"
                    driver.switch_to.default_content()
                    continue
            except:
                pass  # Unidade tem acesso, continuar

            # =============================================
            # PROCESSO DE RASPAGEM
            # =============================================

            # Raspagem de unidades em que o proc esta aberto
            mudar_iframe('visualizacao')
            time.sleep(tempo_longo)

            try:
                unidade_andamento = driver.find_element("xpath", '//*[@id="capaProcessoPro"]/div[1]/div[2]').text
            except:
                time.sleep(tempo_longo)
                try:
                    unidade_andamento = driver.find_element("xpath", '//*[@id="capaProcessoPro"]/div[1]/div[2]').text
                except Exception as e:
                    print(f"Erro persistente: {e}")
                    unidade_andamento = "Erro ao buscar unidade_andamento"

            
            # Link permanente do processo
            time.sleep(tempo_longo)
            id_procedimento = driver.find_element("xpath", '//*[@id="capaProcessoPro"]/div[3]/div[2]/a[2]').get_attribute('data-id_procedimento')
            link_proc = (env['LINK_PROC_MODELO'] if is_local() else st.secrets['LINK_PROC_MODELO']) + id_procedimento

            # Raspagem de documendo de encerramento de processo
            mudar_iframe('visualizacao')
            driver.find_element("xpath", '//img[@alt="Gerar Arquivo PDF do Processo"]').click()
            tabela_documentos = driver.find_element(By.ID, "tblDocumentos")

            # Localizar as células na tabela de documentos que contêm o texto "Termo de Encerramento do Processo"
            termos = len(tabela_documentos.find_elements(By.XPATH, ".//td[contains(text(), 'Termo de Encerramento do Processo')]"))
            
            if (termos > 0 and unidade_andamento == 'Processo não possui andamentos abertos.'):

                conclusao = 'Concluído'

            elif  (termos > 0 and unidade_andamento != 'Processo não possui andamentos abertos.'):

                conclusao = 'Possui termo de encerramento mas está aberto em unidades'

            elif (termos == 0 and unidade_andamento == 'Processo não possui andamentos abertos.'):

                conclusao = 'Não possui andamentos abertos mas não possui termo de encerramento'

            elif (termos == 0 and unidade_andamento != 'Processo não possui andamentos abertos.'):

                conclusao = 'Em andamento'

            else: 

                conclusao = 'Não foi possível concluir se o processo está encerrado'

            
            mudar_iframe('arvore')
            driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span').click()
            mudar_iframe('visualizacao')
            
            # DADOS DA TABELA DE ANDAMENTO:
            processo_sei_format = num_processo_sei(driver.find_element(By.XPATH, '//*[@id="divInfraBarraLocalizacao"]').text) # coluna de Processo
            data_hora = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[1]').text  # Coluna de Data/Horário
            qnt_dias = str(cont_dias(data_hora, datetime.now()))
            unidade_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[2]/a')
            unidade_abreviação = unidade_elemento.text # coluna de abrev unidade
            unidade_nome = unidade_elemento.get_attribute("title") # coluna de abrev unidade
            usuario_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[3]/a')
            usuario_cpf = usuario_elemento.text    # Coluna de Usuário CPF
            usuario = usuario_elemento.get_attribute("title") # Coluna de Usuário
            descricao = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[4]').text  # Coluna de Descrição

            # Atualiza os dados no DataFrame
            processos.loc[processos['Processos'] == processo, colunas] = [
                processo_sei_format, data_hora, qnt_dias, conclusao, unidade_abreviação, unidade_nome, usuario_cpf, usuario, descricao, unidade_andamento, link_proc
            ]

            # Voltar ao contexto principal
            driver.switch_to.default_content()

    except Exception as e:
        # Em caso de erro, exibe a mensagem e continua
        st.error(f"Erro durante o processamento: {e}")
        driver.switch_to.default_content()

    # ordenando as colunas
    processos = processos[colunas]

    # organizando para o display
    processos_display = processos.copy()
    processos_display['Acessar Processo'] = processos_display['Link do Processo']
  
    # Exportando em excel
    df_processos_xlsx = converter_para_excel(processos)

    # Botão de download do Excel
    botao_download = st.download_button(
        label="Clique aqui para baixar em Excel",
        data=df_processos_xlsx,
        file_name="processos_sei_unidade_atual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    dataframe_final = st.dataframe(processos_display,
                                   column_config={
                                       'Acessar Processo': st.column_config.LinkColumn(
                                           'Ir ao Processo',
                                            display_text="Acessar"
                                       )
                                   }, 
                                   column_order=('Processos', 'Acessar Processo', 'Data Horário', 'Qnt. Dias', 'Concluído', 'Unidade Atual',
                                                 'Nome Unidade Atual', 'Usuário CPF', 'Usuário', 'Descrição',
                                                  'Processo aberto nas unidades', 'Link do Processo'
                                         ), 
                                     hide_index=True
                                   )
    
    return dataframe_final
