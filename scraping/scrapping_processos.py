import pandas as pd
import os
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
import re


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

        mudar_iframe('default')

        driver.find_element("xpath", '//*[@id="selInfraUnidades"]').send_keys(unidade)

        colunas_sem_processo = ['Data Horário', 'Qnt. Dias', 'Status', 'Unidade Atual',
            'Nome Unidade Atual', 'Atribuição', 'Atribuição CPF', 'Descrição', 'Processo aberto nas unidades', 'Link do Processo'
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
                processos.loc[processos['Processos'] == processo, 'Link do Processo'] = env['SITE_SEI'] if is_local() else st.secrets['SITE_SEI']
                continue      

            # =============================================
            # PROCESSO DE RASPAGEM
            # =============================================

            # Raspagem de unidades em que o proc esta aberto
            mudar_iframe('visualizacao')
            time.sleep(tempo_curto)

            try:
                unidade_andamento = driver.find_element("xpath", '//*[@id="divInformacao"]').text
            except:
                time.sleep(tempo_longo)
                try:
                    unidade_andamento = driver.find_element("xpath", '//*[@id="divInformacao"]').text
                except Exception as e:
                    print(f"Erro persistente: {e}")
                    unidade_andamento = "Erro ao buscar dados de andamento do processo"

            try:
                if "Processo aberto nas unidades:" in unidade_andamento:
                    atribuicao_nome = 'Atribuído a várias pessoas em vários órgãos. Confira onde o processo está aberto'
                    atribuicao_cpf = 'Atribuído a várias pessoas em vários órgãos. Confira onde o processo está aberto'
                else:

                    if "(atribuído para" in unidade_andamento:
                        atribuicao_nome = driver.find_element('xpath', '//*[@id="divInformacao"]/a[2]').text
                        atribuicao_cpf = driver.find_element('xpath', '//*[@id="divInformacao"]/a[2]').get_attribute("title")
                    else:
                        atribuicao_nome = 'Não atribuído'
                        atribuicao_cpf = 'Não atribuído'
            except Exception as e:
                atribuicao_nome = 'Dado não obtido'
                atribuicao_cpf = 'Dado não obtido'


            # Link permanente do processo
            time.sleep(tempo_curto)
            mudar_iframe('default')
            link_isca = driver.find_element("xpath", '//*[@id="ifrArvore"]').get_attribute('src') # iframe da arvore
            id_procedimento = re.search(r"id_procedimento=(\d+)", link_isca).group(1)
            
            # juncao do id_procedimento com link modelo
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
            # usuario_elemento = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[3]/a')
            # usuario_cpf = usuario_elemento.text    # Coluna de Usuário CPF
            # usuario = usuario_elemento.get_attribute("title") # Coluna de Usuário
            descricao = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[4]').text  # Coluna de Descrição

            # Atualiza os dados no DataFrame
            processos.loc[processos['Processos'] == processo, colunas] = [
                processo_sei_format, data_hora, qnt_dias, conclusao, unidade_abreviação, unidade_nome, atribuicao_nome, atribuicao_cpf, descricao, unidade_andamento, link_proc
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
    df_processos_xlsx = converter_para_excel(processos, "Processos SEI - Unidades atuais")

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
                                   column_order=('Processos', 'Acessar Processo', 'Data Horário', 'Qnt. Dias', 'Status', 'Unidade Atual',
                                                 'Nome Unidade Atual', 'Atribuição', 'Atribuição CPF', 'Descrição',
                                                  'Processo aberto nas unidades', 'Link do Processo'
                                         ), 
                                     hide_index=True
                                   )

    return dataframe_final
