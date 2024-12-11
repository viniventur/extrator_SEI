import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pyautogui
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
import time

# tempos para execucao
tempo_curto = 0.5
tempo_medio = 1
tempo_longo = 1.5

print('Carregando...')

try:

    while True:

        caminho_arquivo = input('Insira o caminho para o arquivo (.xlsx): ')

        if os.path.isfile(caminho_arquivo):

            if caminho_arquivo.endswith(".xlsx"):

                # Nome arquivo novo

                caminho_arquivo = caminho_arquivo.replace(r'\\', "/")
                base_name = os.path.basename(caminho_arquivo)  # Nome do arquivo com extensão
                sheet_name = base_name.split('.')[0]  # Nome da planilha (antes do .xlsx)

                # Construir a nova string
                caminho_novo_arquivo = caminho_arquivo.replace(".xlsx", f"_preenchido.xlsx")

                chrome_options = Options()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-dev-shm-usage')

                driver = webdriver.Chrome(options=chrome_options)

                # Abrindo o SEI
                #driver = webdriver.Chrome()
                driver.get(env['SITE_SEI'])

                print('Obtendo informacoes...')


                # Login e seleção da unidade

                usuario_sei = env['CPF_SEI']
                senha_sei = env['SENHA_SEI']

                driver.find_element("xpath", '//*[@id="txtUsuario"]').send_keys(usuario_sei)
                time.sleep(tempo_curto)
                driver.find_element("xpath", '//*[@id="pwdSenha"]').send_keys(senha_sei)
                time.sleep(tempo_curto)
                driver.find_element("xpath", '//*[@id="selOrgao"]').send_keys('CGE')
                driver.find_element("xpath", '//*[@id="sbmLogin"]').click()


                # Looping de raspagem

                df = pd.read_excel(caminho_arquivo)

                for processo in df['Processo Mãe']:

                    time.sleep(tempo_medio)
                    driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(processo)
                    time.sleep(tempo_curto)
                    driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(Keys.ENTER)
                    time.sleep(tempo_curto)

                    # Alternar para o iframe 'ifrArvore'
                    iframe_arvore = driver.find_element('name', "ifrArvore")
                    driver.switch_to.frame(iframe_arvore)

                    driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span').click() # consultar andamento

                    time.sleep(tempo_curto)    
                    # Alternar para o iframe 'ifrVisualizacao'
                    driver.switch_to.default_content()
                    iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
                    driver.switch_to.frame(iframe_visualizacao)
                    
                    time.sleep(tempo_medio)
                    # Extrai os dados da primeira linha da tabela
                    data_hora = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[1]').text  # Coluna 1: Data/Horário
                    unidade = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[2]').text    # Coluna 2: Unidade
                    usuario = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[3]').text    # Coluna 3: Usuário
                    descricao = driver.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[4]').text  # Coluna 4: Descrição

                    # Cria um dicionário para organizar os dados extraídos
                    dados = {
                        "Data Horário": data_hora,
                        "Unidade Atual": unidade,
                        "Usuário CPF": usuario,
                        "Descrição": descricao
                    }

                    # Atualiza o DataFrame de forma mais eficiente
                    df.loc[df['Processo Mãe'] == processo, ['Data Horário', 'Unidade Atual', 'Usuário CPF', 'Descrição']] = [
                        dados["Data Horário"], dados["Unidade Atual"], dados["Usuário CPF"], dados["Descrição"]
                    ]

                    # Voltar ao contexto principal
                    driver.switch_to.default_content()

                df.to_excel(caminho_novo_arquivo, index=False)


                driver.quit()

                print('CONCLUIDO! Confira a pasta do arquivo fornecido.')

            else:
                
                print("Erro: O arquivo informado não é .xlsx")
            break
        else:
            print(f"O arquivo '{caminho_arquivo}' não existe. Tente novamente")

except Exception as e:
    print(' ') 
    print('Erro na obtenção dos dados:')
    print(' ')
    print(e)


