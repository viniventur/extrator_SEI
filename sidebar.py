import streamlit as st
from utils.funcoes_auxiliares import *

def run_sidebar():

    if is_local():

        if st.session_state.pag == 'inicio':
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
            
                st.title(f'Olá, {nome_usuario}!')

                if st.button("Sair"):
                    voltar()


                st.sidebar.divider()
                # navegacao

                st.sidebar.page_link('Inicio.py',
                        label='Início',
                        icon=':material/home:')
                
                st.sidebar.page_link('pages/1_Andamento de processos.py',
                                     label='Andamento de Processos',
                                     icon=':material/explore:')
                
                # st.sidebar.page_link('pages/2_Contagem de documentos.py',
                #                      label='Contagem de documentos',
                #                      icon=':material/functions:')

                st.divider()

                st.text('Controladoria-Geral do Estado de Alagoas')

    else:

        with st.sidebar:

            logo_path_CGE_OGP = 'src/assets/Identidades visual/logo_CGE_OGP_transp.png'       
            st.image(logo_path_CGE_OGP)
        
            st.title('Olá, fulano!')

            if st.button("Sair"):
                voltar()


            st.sidebar.divider()
            # navegacao

            st.sidebar.page_link('Inicio.py', label='Início', icon=':material/home:')
            st.sidebar.page_link('pages/1_Andamento de processos.py', label='Andamento de Processos')





