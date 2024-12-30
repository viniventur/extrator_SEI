import pandas as pd
import streamlit as st
from dotenv import dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from scraping.extracao_unidade import *
from utils.funcoes_auxiliares import *
from scraping.scrapping_processos import *
from login import *
import base64

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
        st.switch_page('Inicio.py')

if 'driver' not in st.session_state:
    st.error('Erro, Google Chrome não respondeu, redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page('Inicio.py')

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


def main():
    
    # Inicializar a flag auxiliar para limpar o input
    if "limpar_input" not in st.session_state:
        st.session_state.limpar_input = False

    # Se a flag for True, limpa o input e reseta a flag
    if st.session_state.limpar_input:
        default_value = ""  # Define o valor padrão
        st.session_state.limpar_input = False  # Reseta a flag
    else:
        default_value = st.session_state.get("processos_input", "")

    # Criar um contêiner fixo no topo da página
    header = st.container()

    def get_image_as_base64(file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    logo_path_CGE = 'src/assets/Identidades visual/Logo CGE Governo/LOGO GOV-branco.png'
    logo_path_OGP = 'src/assets/Identidades visual/OGP/APRESENTAÇÃO_LOGO_-_OBSERVATÓRIO_DA_GESTÃO_PÚBLICA_BRANCO_TRANSP.png'
    logo_base64_CGE = get_image_as_base64(logo_path_CGE)
    logo_base64_OGP = get_image_as_base64(logo_path_OGP)

    with st.container():
        # Centralizando as imagens lado a lado
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
                <img src="data:image/png;base64,{logo_base64_CGE}" style="margin-right: 0px; width: 300px;">
                <img src="data:image/png;base64,{logo_base64_OGP}" style="width: 250px;">
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.container():
        st.markdown("<h1 style='text-align: center;'>Extração dos Dados</h1>", unsafe_allow_html=True)

    # Layout
    if st.button("Voltar ao Início"):
        voltar()

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
                resultado, total_linhas, linhas_validas = tratar_processos_input(lista_processos)

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
