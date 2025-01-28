import pandas as pd
import streamlit as st
from st_pages import add_page_title, get_nav_from_toml, _get_pages_from_config
from dotenv import dotenv_values
env = dotenv_values('.env')

from utils.chrome import *
from utils.funcoes_auxiliares import *
from utils.login import *
from scraping.analise_docs import *
from scraping.extracao_unidade import *
from scraping.scrapping_processos import *
from sidebar import *
import base64

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

st.set_page_config(page_title='Extrator de dados - SEI - OGP/CGE', page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png')

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
                st.session_state["docs_dict"] = raspagem_docs(processo, unidade)
                st.session_state["docs"] = st.session_state["docs_dict"].keys()
                st.session_state["docs_carregados"] = True

        # Renderizar multiselect com a lista carregada
        documentos_selecionados = st.multiselect(
            'Selecione os Tipos de Documentos',
            st.session_state.get("docs", []),  # Usa os documentos carregados no estado
            max_selections=5,
            placeholder="Tipos de documentos"
        )

        st.write("Documentos selecionados:", documentos_selecionados)

        if st.button('Analisar documentos selecionados'):

            if not documentos_selecionados:
                st.error('Selecione documentos para analisar.')

            for doc in documentos_selecionados:
                st.write(doc)
                st.write(st.session_state["docs_dict"][doc])
                doc_elemento = st.session_state["docs_dict"][doc]
                baixar_docs_analise(doc_elemento)


            st.write(os.listdir(st.session_state.temp_dir))
            st.write(st.session_state.temp_dir)



    

        #st.write(docs)




    

        # if lista_processos:
        #     with st.spinner('Buscando dados, aguarde...'):
        #         resultado, total_linhas, linhas_validas = tratar_processos_input(lista_processos)

        #         # Criação do DataFrame
        #         resultado = [linha.strip() for linha in resultado.splitlines() if linha.strip()]
        #         df_processos = pd.DataFrame({"Processos": resultado})
        #         df_processos.drop_duplicates(subset="Processos", inplace=True)

        #         # Output
        #         with st.container():
        #             st.subheader("Tabela de Processos:")
        #             buscar_dados_andamento(unidade, df_processos)
        # else:
        #     st.error("Por favor, insira os números de processos para tratamento.")



if __name__ == "__main__":
    main()
