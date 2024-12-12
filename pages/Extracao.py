import streamlit as st

st.set_page_config(layout="wide", page_title='Extrator de dados - SEI - OGP/CGE', page_icon='src/assets/Identidades visual/OGP/LOGO-OGP - icon.jpg', initial_sidebar_state="collapsed")

# Aplicar CSS para esconder o sidebar
hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

if st.button("Voltar"):
    #driver.quit()
    st.switch_page('inicio.py')


st.write('''
            ## Extração dos Dados
            ''')


'''

# adicionar input para a unidade (lista de seleção)
unidade = st.selectbox('Selecione a Unidade', lista_unidades)
'''