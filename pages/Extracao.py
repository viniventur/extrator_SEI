import pandas as pd
import streamlit as st
from dotenv import dotenv_values
env = dotenv_values('.env')

from chrome import *
from extracao_unidade import *
from tratamento_processos import *
from scrapping_processos import *
from login import *

import warnings
warnings.filterwarnings('ignore')

def excluir_driver():
    if 'driver' in st.session_state:
        try:
            st.session_state.driver.quit()
        except Exception as e:
            st.warning(f"Erro ao encerrar o driver: {e}")
        del st.session_state['driver']

def voltar():
    with st.spinner('Redirecionando...'):
        excluir_driver()
        st.cache_resource.clear()
        st.switch_page('inicio.py')

if 'driver' not in st.session_state:
    st.error('Erro, Google Chrome não respondeu, redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page('inicio.py')

def main():
    st.set_page_config(page_title='Extrator de dados - SEI - OGP/CGE', page_icon='src/assets/Identidades visual/OGP/LOGO-OGP - icon.jpg', initial_sidebar_state="collapsed")

    # Aplicar CSS para esconder o sidebar
    hide_style = """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        #MainMenu {visibility: hidden}
        header {visibility: hidden}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

    # Inicializar a flag auxiliar para limpar o input
    if "limpar_input" not in st.session_state:
        st.session_state.limpar_input = False

    # Se a flag for True, limpa o input e reseta a flag
    if st.session_state.limpar_input:
        default_value = ""  # Define o valor padrão
        st.session_state.limpar_input = False  # Reseta a flag
    else:
        default_value = st.session_state.get("processos_input", "")

    # Layout
    if st.button("Voltar ao Início"):
        voltar()

    st.markdown("<h1 style='text-align: center;'>Extração dos Dados</h1>", unsafe_allow_html=True)

    # Lista de seleção
    lista_unidades = lista_unidades_sei()
    unidade = st.selectbox('Selecione a Unidade', lista_unidades)

    # Text area
    lista_processos = st.text_area('Informe os Processos', value=default_value, key="processos_input")

    # Dividindo os botões em duas colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        buscar = st.button("Buscar dados dos processos inseridos")

    with col2:
        limpar = st.button("Limpar")

    # Lógica do botão "Limpar"
    if limpar:
        st.session_state.limpar_input = True  # Ativa a flag para limpar
        st.rerun()  # Recarrega a interface

    # Lógica do botão "Buscar"
    if buscar:
        if lista_processos:
            with st.spinner('Buscando dados, aguarde...'):
                resultado, total_linhas, linhas_validas = tratar_processos(lista_processos)

                # Criação do DataFrame
                resultado = [linha.strip() for linha in resultado.splitlines() if linha.strip()]
                df_processos = pd.DataFrame({"Processos": resultado})

                # Output
                with st.container():
                    st.subheader("Tabela de Processos:")
                    buscar_dados(df_processos)
        else:
            st.error("Por favor, insira os números de processos para tratamento.")

if __name__ == "__main__":
    main()