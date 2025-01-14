import streamlit as st
from utils.funcoes_auxiliares import *


def run_sidebar():

    if st.session_state.pag == 'login':
        with st.sidebar:

            logo_path_CGE_OGP = 'src/assets/Identidades visual/logo_CGE_OGP_transp.png'       
            st.image(logo_path_CGE_OGP)

            st.title('Realize o login no SEI para navegar.')

            st.divider()

            st.text('Controladoria-Geral do Estado de Alagoas')
    else:
        with st.sidebar:

            logo_path_CGE_OGP = 'src/assets/Identidades visual/logo_CGE_OGP_transp.png'       
            st.image(logo_path_CGE_OGP)
            nome_usuario = st.session_state.nome_usuario
        
            st.markdown(f'# <center> Olá, {nome_usuario}!', unsafe_allow_html=True)

            if st.button(":material/logout: Sair", help='Clique para deslogar', use_container_width=True):
                sair()


            st.sidebar.divider()
            # navegacao

            st.sidebar.page_link(modulos[1][1],
                    label=modulos[1][0],
                    icon=modulos[1][2])
            
            
            st.sidebar.page_link(modulos[2][1],
                                    label=modulos[2][0],
                                    icon=modulos[2][2])
            
            st.sidebar.page_link(modulos[3][1],
                                  label=modulos[3][0],
                                  icon=modulos[3][2])

            st.divider()

            st.text('Controladoria-Geral do Estado de Alagoas')







