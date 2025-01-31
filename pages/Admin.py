import pandas as pd
import plotly.express as px
import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values

from utils import *
from sidebar import *

import warnings
import base64
import time
import locale

from dialogs.admin_dialogs import *

# Configurações Gerais
warnings.filterwarnings('ignore')
env = dotenv_values('.env')

st.set_page_config(page_title='Extrator de dados do SEI - OGP/CGE', 
                   page_icon='src/assets/Identidade visual/OGP/logo-ogp-favicon.png',
                   layout='wide')

# Verificação Inicial
if 'driver' not in st.session_state:
    st.error('Erro, Google Chrome não respondeu, redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page(modulos[0][1])

if st.session_state.acesso != 'ADMIN':
    st.error('Acesso restrito! Redirecionando...')
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page(modulos[0][1])

# Config Layout (local ou online)
hide_style = """ """
if not is_local():
    hide_style = """
    <style>
    #MainMenu {visibility: hidden}
    header {visibility: hidden}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# Funções Principais
def main():

    st.session_state.pag = 'ADMIN'

    run_sidebar()
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

    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Configuração de Usuários e Acessos</h1>", unsafe_allow_html=True)

    if 'reload_data' not in st.session_state:
        st.session_state['reload_data'] = False

    cols = st.columns(3)
    with cols[0]:
        if st.button(':material/add: Adicionar', use_container_width=True):
            add_user()

    with cols[1]:
        if st.button(':material/edit: Alterar', use_container_width=True):
            edit_user()

    with cols[2]:
        if st.button(':material/delete: Excluir', use_container_width=True):
            excluir_user()

    if st.button(':material/refresh: Atualizar', use_container_width=True):
        st.session_state['reload_data'] = True
        st.cache_data.clear()
        st.rerun()

    if st.session_state['reload_data']:
        df_usuarios = df_usuarios_cpf()
        st.session_state['reload_data'] = False
    else:
        df_usuarios = df_usuarios_cpf()

    st.markdown(f"<h1 style='text-align: center; font-size: 20px;'>Última atualização: {st.session_state.data_atualizacao_users}</h1>", unsafe_allow_html=True)
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

    st.divider()
    
    st.markdown(f"<h1 style='text-align: center; font-size: 35px;'>Histórico de Acessos</h1>", unsafe_allow_html=True)

    # # Configurando o locale para português
    if is_local():
        locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")  # Para sistemas Windows
    else:
        locale.setlocale(locale.LC_ALL, "pt_BR")  # Para sistemas baseados em Unix/Linux

    historico_acesso = df_historico_acesso()
    # historico_acesso = pd.read_csv(r'tests\teste_HISTORICO.csv', dtype=str)
    # historico_acesso.drop(columns='Unnamed: 0', inplace=True)

    # =============================================
    # TRATAMENTO DOS DADOS
    # =============================================

    # Convertendo a coluna 'DATA_ACESSO' para datetime
    historico_acesso['DATA_ACESSO'] = pd.to_datetime(historico_acesso['DATA_ACESSO'], format='%d/%m/%Y %H:%M')

    # Criando a coluna de mês/ano como pd.Period (preserva ordem temporal)
    historico_acesso['MES_ANO'] = historico_acesso['DATA_ACESSO'].dt.to_period('M')

    # Extraindo os meses únicos para o slider
    meses_unicos = sorted(historico_acesso['MES_ANO'].unique())

    # Verificando se há mais de um mês disponível
    if len(meses_unicos) > 1:
        # Adicionando o slider para selecionar intervalo de meses
        mes_inicio, mes_fim = st.select_slider(
            "Selecione o intervalo de meses:",
            options=meses_unicos,
            value=(meses_unicos[0], meses_unicos[-1])  # Valores inicial e final padrão
        )
    else:
        # Caso haja apenas um mês, usar valores fixos e exibir mensagem
        mes_inicio = meses_unicos[0] if len(meses_unicos) == 1 else None
        mes_fim = mes_inicio  # Apenas um mês disponível
        st.warning("Apenas um mês disponível. Exibindo dados para o único mês.")

    # Filtrando os dados com base no intervalo selecionado
    if mes_inicio and mes_fim:
        historico_filtrado = historico_acesso[
            (historico_acesso['MES_ANO'] >= mes_inicio) &
            (historico_acesso['MES_ANO'] <= mes_fim)
        ]
    else:
        historico_filtrado = pd.DataFrame()  # Caso não haja meses disponíveis, DataFrame vazio

    # Verificação final
    if historico_filtrado.empty:
        st.error("Nenhum dado encontrado para o intervalo selecionado.")

    # Filtrando os dados com base no intervalo de meses
    historico_filtrado = historico_acesso[
        (historico_acesso['MES_ANO'] >= mes_inicio) &
        (historico_acesso['MES_ANO'] <= mes_fim)
    ]

    # =============================================
    # GRÁFICO DE BARRAS EMPILHADAS VERTICAIS (MENSAL)
    # =============================================

    # Contando acessos por órgão e mês
    df_contagem_empilhada = historico_filtrado.groupby(
        [historico_filtrado['MES_ANO'], 'ORGAO']
    ).size().reset_index()
    df_contagem_empilhada.columns = ['MES_ANO', 'ORGÃO', 'Número de Acessos']

    # Convertendo MES_ANO para string com nomes de meses em português para exibição
    df_contagem_empilhada['MES_ANO_LABEL'] = df_contagem_empilhada['MES_ANO'].dt.strftime('%B/%Y').str.capitalize()

    # Criando o gráfico de barras empilhadas
    graf_empilhado = px.bar(
        df_contagem_empilhada,
        x='MES_ANO_LABEL',  # Exibe o rótulo formatado
        y='Número de Acessos',
        color='ORGÃO',
        title='Acessos Empilhados por Órgão (Mensal)',
        labels={'MES_ANO_LABEL': 'Mês/Ano', 'Número de Acessos': 'Número de Acessos', 'ORGÃO': 'Órgão'},
        text_auto=True
    )

    # Ajustando a ordem cronológica dos meses com base no Period original
    graf_empilhado.update_xaxes(categoryorder='array', categoryarray=df_contagem_empilhada['MES_ANO'].sort_values().astype(str))

    graf_empilhado.update_layout(
        title_font_size=16,
        xaxis_title="Mês/Ano",
        yaxis_title="Número de Acessos",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        legend_title="Órgãos",
        barmode='stack',  # Define barras empilhadas
        template="plotly_white"
    )

    st.plotly_chart(graf_empilhado, use_container_width=True)

    # =============================================
    # GRÁFICO DE BARRAS HORIZONTAIS POR ÓRGÃO
    # =============================================

    # Contando os acessos por órgão
    orgaos_contagem = historico_filtrado['ORGAO'].value_counts().reset_index()
    orgaos_contagem.columns = ['ORGÃO', 'Número de Acessos']
    orgaos_contagem = orgaos_contagem.sort_values(by='Número de Acessos', ascending=True)

    graf_qnt_acessos = px.bar(
        orgaos_contagem,
        x='Número de Acessos',
        y='ORGÃO',
        orientation='h',
        title='Órgãos com Mais Acessos',
        text='Número de Acessos',
        color='Número de Acessos',
        color_continuous_scale='Blues'
    )

    graf_qnt_acessos.update_layout(
        xaxis_title="Número de Acessos",
        yaxis_title="Órgãos",
        title_font_size=16,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=False),
        template="plotly_white",
        coloraxis_showscale=False
    )

    # =============================================
    # GRÁFICO DE BARRAS HORIZONTAIS POR USUARIO
    # =============================================

    # Extraindo o primeiro nome da coluna NOME e concatenando com o órgão
    historico_acesso['USUARIO'] = historico_acesso['NOME_SEI'].str.split().str[0] + " (" + historico_acesso['ORGAO'] + ")"

    # Contando os acessos por usuário
    ranking_usuarios = historico_acesso['USUARIO'].value_counts().reset_index()
    ranking_usuarios.columns = ['USUÁRIO', 'Número de Acessos']


    # Criando o gráfico de ranking
    graf_ranking = px.bar(
        ranking_usuarios,
        x='Número de Acessos',
        y='USUÁRIO',
        orientation='h',
        title='Ranking de Acessos por Usuário',
        labels={'USUÁRIO': 'Usuário', 'Número de Acessos': 'Número de Acessos'},
        text='Número de Acessos',
        color='Número de Acessos',  # Para diferenciar com uma escala de cores
        color_continuous_scale='Blues'
    )

    # Customizando o layout do gráfico
    graf_ranking.update_layout(
        title_font_size=16,
        xaxis_title="Número de Acessos",
        yaxis_title="Usuários",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=False, categoryorder='total ascending'),  # Ordena pela quantidade de acessos
        template="plotly_white",
        coloraxis_showscale=False
    )

    col1, col2 = st.columns([0.8,1.2])

    with col1:
        st.plotly_chart(graf_qnt_acessos, use_container_width=True)

    with col2:
     st.plotly_chart(graf_ranking, use_container_width=True)


if __name__ == "__main__":
    main()
