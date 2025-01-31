import streamlit as st
from utils import *


def run_sidebar():

    if st.session_state.pag == 'login':
        with st.sidebar:

            logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'       
            st.image(logo_path_CGE_OGP)

            st.title('Realize o login no SEI para navegar.')

            st.divider()

            st.text('Controladoria-Geral do Estado de Alagoas')
    else:

        if st.session_state.acesso == 'ADMIN':

            with st.sidebar:

                logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'       
                st.image(logo_path_CGE_OGP)
                nome_usuario = st.session_state.nome_usuario
            
                st.markdown(f'# <center> Olá, {nome_usuario}!', unsafe_allow_html=True)

                if st.button(":material/logout: Sair", help='Clique para deslogar', use_container_width=True):
                    sair()


                st.sidebar.divider()

                # NAVEGACAO

                for modulo in range(1,6): # MODULOS COMPLETOS
                
                    st.sidebar.page_link(modulos[modulo][1],
                            label=modulos[modulo][0],
                            icon=modulos[modulo][2])

                st.divider()

                st.text('Controladoria-Geral do Estado de Alagoas')
        else:

            with st.sidebar:

                logo_path_CGE_OGP = 'src/assets/Identidade visual/logo_CGE_OGP_transp.png'       
                st.image(logo_path_CGE_OGP)
                nome_usuario = st.session_state.nome_usuario
            
                st.markdown(f'# <center> Olá, {nome_usuario}!', unsafe_allow_html=True)

                if st.button(":material/logout: Sair", help='Clique para deslogar', use_container_width=True):
                    sair()


                st.sidebar.divider()

                # navegacao

                for modulo in range(1,5): # MODULOS SEM ADMIN
                
                    st.sidebar.page_link(modulos[modulo][1],
                            label=modulos[modulo][0],
                            icon=modulos[modulo][2])

                st.divider()

                st.text('Controladoria-Geral do Estado de Alagoas')








