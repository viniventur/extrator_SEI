import pandas as pd
import streamlit as st
import shutil
import os
from path import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from st_pages import add_page_title, get_nav_from_toml, _get_pages_from_config
from dotenv import dotenv_values
env = dotenv_values('.env')

from utils import *

from scraping.analise_docs import *
from scraping.extracao_unidade import *
from scraping.scrapping_processos import *
from sidebar import *

import base64
from docling.document_converter import DocumentConverter

import warnings
warnings.filterwarnings('ignore')

if 'driver' not in st.session_state:
    st.error('Erro, Google Chrome não respondeu, redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page(modulos[0][1])

# Define o estado inicial para "docs_carregados" (se a lista foi carregada)
if "docs_carregados" not in st.session_state:
    st.session_state["docs_carregados"] = False  # Inicialmente, não carregado

# Função para buscar documentos
def botao_docs():
    st.session_state["docs_verificacao"] = True
    st.session_state["docs_carregados"] = False

# resetar botoes
def reset_botao_docs():
    st.session_state["docs_verificacao"] = False
    st.session_state["docs_carregados"] = False

st.set_page_config(page_title='Extrator de dados - SEI - OGP/CGE', page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png', layout='wide')

if is_local():
    
    # Aplicar CSS para esconder o sidebar
    hide_style = """
    """
else:

    # Aplicar CSS para esconder o sidebar
    hide_style = """
        <style>
        #MainMenu {visibility: hidden}
        header {visibility: hidden}
        </style>
    """

st.markdown(hide_style, unsafe_allow_html=True)

# Função principal
def main():

    # Tempos para execução
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5

    if st.session_state.pag != 'analise_doc':
        reset_botao_docs()

    st.session_state.pag = 'analise_doc'

    run_sidebar()
    
    # Inicializar a flag auxiliar para limpar o input
    if "limpar_input" not in st.session_state:
        st.session_state.limpar_input = False

    # Se a flag for True, limpa o input e reseta a flag
    if st.session_state.limpar_input:
        default_value = ""  # Define o valor padrão
        st.session_state.limpar_input = False  # Reseta a flag
    else:
        default_value = st.session_state.get("processo_input", "")

    # Exibir cabeçalho e logotipo
    logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'
    logo_base64_CGE_OGP = get_image_as_base64(logo_path_CGE_OGP)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
            <img src="data:image/png;base64,{logo_base64_CGE_OGP}" style="margin-right: 0px; width: 550px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align: center;'>Análise de Documentos</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🚧 EM CONSTRUÇÃO</h1>", unsafe_allow_html=True)

    # Dividindo os botões em duas colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(":material/logout: Sair", key='sair', help='Clique para deslogar', use_container_width=True):
            sair()
    with col2:
        if st.button(":material/keyboard_return: Voltar ao Início", key='inicio', help='Clique para ir ao início', use_container_width=True):
            voltar_inicio()

    # Lista de seleção
    try:
        lista_unidades = st.session_state.unidades_usuario
    except Exception as e:
        st.error(f'Erro ao obter as unidades disponíveis! Realize Login novamente.')
        sair()

    unidade = st.selectbox('Selecione a Unidade', lista_unidades)

    # Text area
    processo = st.text_input('Informe o Processo', value=default_value, key="processo_input", on_change=reset_botao_docs)

    # Define o estado inicial para o botão de busca e a verificacao docs
    if "docs_verificacao" not in st.session_state:
        st.session_state["docs_verificacao"] = False

    # Dividindo os botões em duas colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        buscar = st.button(":material/search: Buscar documentos disponíveis", on_click=botao_docs)

    with col2:
        limpar = st.button(":material/delete_forever: Limpar")

    # Lógica do botão "Limpar"
    if limpar:
        st.session_state.limpar_input = True  # Ativa a flag para limpar
        st.session_state["docs_carregados"] = False
        st.session_state["docs_verificacao"] = False
        st.rerun()  # Recarrega a interface para limpar

    # Se a busca foi realizada e `docs_verificacao` está ativo
    if st.session_state["docs_verificacao"]:
        if not processo:
            st.error('Por favor, insira os números de processos para análise.')
            return

        # Executa a busca novamente ao clicar no botão
        if not st.session_state["docs_carregados"]:
            with st.spinner("Buscando documentos disponíveis..."):
                try:
                    st.session_state["docs_dict"] = raspagem_docs(processo, unidade)
                    st.session_state["docs"] = st.session_state["docs_dict"].keys()
                    st.session_state["docs_carregados"] = True
                except Exception as e:
                    return  # Interrompe a execução
                
        # Renderizar multiselect com a lista carregada
        documentos_selecionados = st.multiselect(
            'Selecione os Tipos de Documentos',
            list(st.session_state["docs_dict"].keys())[1:],  # Usa os documentos carregados no estado
            max_selections=5,
            placeholder="Tipos de documentos"
        )

        st.write("Documentos selecionados:", documentos_selecionados)

        if st.button(':material/quick_reference_all: Analisar documentos selecionados'):

            if not documentos_selecionados:
                st.error('Selecione documentos para analisar.')

            # =============================================
            # BAIXANDO OS ARQUIVOS
            # =============================================

            with st.spinner('Baixando os arquivos...'):

                with TemporaryDirectory() as temp_dir:

                    st.session_state.temp_dir = temp_dir
                    st.write(st.session_state.temp_dir)

                    # baixar documentos em um PDF único
                    baixar_docs_analise(documentos_selecionados, st.session_state.temp_dir)

                    time.sleep(10)

                    st.write(st.session_state.diretorio_download)
                    st.write(os.listdir(temp_dir))
                    # Verificar se a quantidade de arquivos na pasta é igual à quantidade de documentos selecionados
                    arquivos_na_pasta = [f for f in os.listdir(Path(temp_dir))]
                    st.write(f"Arquivos na pasta: {len(arquivos_na_pasta)}")

                    # =============================================
                    # PROCESSO DE LEITURA - DOCLING
                    # =============================================

                    with st.spinner('Lendo os arquivos...'):

                        try:

                            for arquivo in arquivos_na_pasta:
                                pdf_path = os.path.join(st.session_state.temp_dir, arquivo)
                                st.write(pdf_path)

                                # Ler os arquivos - docling
                                st.write(carregar_docs(pdf_path))
                                st.write(carregar_docs(pdf_path)[0])
                        except Exception as e:
                            st.error(f'Erro ao ler arquivos: {e}')

                    # =============================================
                    # PROCESSAMENTO COM IA
                    # =============================================



if __name__ == "__main__":
    main()
