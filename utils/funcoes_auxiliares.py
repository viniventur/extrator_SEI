import os
from dotenv import load_dotenv, dotenv_values
import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
import base64
import time
env = dotenv_values('.env')


# modulos
@st.cache_data(show_spinner=False)
def modulos():
    '''
        Retorna um dicionário com informações sobre os módulos disponiveis no sistema.

        Estrutura:
        - Chave (int): Identificador do módulo.
        - Valor (list): [Nome do módulo (str), Caminho do arquivo (str), Emoji (str)] - .


        Exemplo de uso:
            modulos = modulos()
            print(modulos_dict[1])  # Retorna ['Início', 'pages/Inicio.py', ':material/home:']
            print(modulos[0][1]) # Retorna o endereço do primeiro modulo
    '''
    modulos = {
        0: ['Login', 'pag_login.py'],
        1: ['Início', 'pages/Inicio.py', ':material/home:'],
        2: ['Análise de Documentos', 'pages/Analise_de_documentos.py', ':material/quick_reference_all:'],
        3: ['Andamento de Processos', 'pages/Andamento_de_processos.py', ':material/explore:'],
        4: ['Contagem de Documentos', 'pages/Contagem_de_documentos.py', ':material/equal:'],
        5: ['Administração', 'pages/Admin.py', ':material/admin_panel_settings:']
    }
    return modulos

modulos = modulos()

# Função para detectar se está rodando localmente
def is_local(path='.'):
    """
    Verifica se há um arquivo ou diretório chamado '.env' em um caminho especificado.
    
    :param path: Caminho onde a verificação será realizada. Padrão é o diretório atual.
    :return: String indicando se '.env' é um arquivo, diretório ou não existe.
    """
    env_path = os.path.join(path, ".gitignore")
    
    if os.path.exists(env_path):
        if os.path.isfile(env_path):
            return True
    return False

def excluir_driver():
    if 'driver' in st.session_state:
        try:
            st.session_state.driver.quit()
        except Exception as e:
            st.warning(f"Erro ao encerrar o driver: {e}")
        del st.session_state['driver']

def sair():
    with st.spinner('Redirecionando...'):
        os.rmdir(st.session_state.temp_dir)
        excluir_driver()
        st.cache_resource.clear()
        st.cache_data.clear()
        st.session_state.clear()
        st.switch_page(modulos[0][1])

def voltar_inicio():
    with st.spinner('Redirecionando...'):
        st.switch_page(modulos[1][1])

# Filtra apenas os numeros de processos e padroniza
import re

def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def num_processo_sei(processo):
    padrao = r"E:\d{5}\.\d{10}/\d{4}"
    processo_sei_format = re.search(padrao, processo).group()
    return processo_sei_format

def tratar_processos_input(input_text):
    # Passo 1: Remove espaços no início e no final
    linhas = input_text.strip().splitlines()

    # Passo 2: Elimina linhas vazias e espaços extras dentro das linhas
    linhas_tratadas = [re.sub(r'\s+', '', linha) for linha in linhas if linha.strip()]

    # Passo 4: Junta as linhas válidas em uma única string com quebras de linha
    resultado = "\n".join(linhas_tratadas)

    return resultado, len(linhas_tratadas), len(linhas_tratadas)


# Contagem de dias entre datas do sei

def cont_dias(data_x, data_y):
    """
    Calcula a diferença em dias entre duas datas.

    Parâmetros:
        data_x (str ou datetime): Primeira data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.
        data_y (str ou datetime): Segunda data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.

    Retorna:
        int: Diferença em dias entre as duas datas.
    """
    # Verificar e converter data_x, se necessário
    if isinstance(data_x, str):
        data_x = datetime.strptime(data_x, "%d/%m/%Y %H:%M")
    elif not isinstance(data_x, datetime):
        raise ValueError("data_x deve ser uma string ou um objeto datetime.")

    # Verificar e converter data_y, se necessário
    if isinstance(data_y, str):
        data_y = datetime.strptime(data_y, "%d/%m/%Y %H:%M")
    elif not isinstance(data_y, datetime):
        raise ValueError("data_y deve ser uma string ou um objeto datetime.")

    # Calcular a diferença em dias
    diferenca = (data_y - data_x).days

    return diferenca

def converter_para_excel(df_processos, nome_aba):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_processos.to_excel(writer, index=False, sheet_name=nome_aba)
        worksheet = writer.sheets[nome_aba]
        for col_idx, column in enumerate(df_processos.columns, start=1):
            max_length = max(
                df_processos[column].astype(str).map(len).max(),
                len(column)
            ) + 2
            col_letter = get_column_letter(col_idx)
            worksheet.column_dimensions[col_letter].width = max_length
    output.seek(0)
    return output.getvalue()


def mudar_iframe(iframe):

    driver = st.session_state.driver

    if (iframe == 'arvore'):

        driver.switch_to.default_content()
        iframe_arvore = driver.find_element('name', "ifrArvore")
        driver.switch_to.frame(iframe_arvore)

    elif (iframe == 'visualizacao'):

        driver.switch_to.default_content()
        iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
        driver.switch_to.frame(iframe_visualizacao)
    
    elif (iframe == 'default'):
        driver.switch_to.default_content()


def verificar_acesso_processo(processo):
    """
    Verifica a existência ou acesso a um processo no sistema e atualiza o DataFrame 'processos'.

    Args:
        processo (str): Identificador do processo a ser verificado.
    Returns:
        bool: Retorna True se o acesso foi finalizado (não encontrado ou sem acesso), False caso contrário.
        mensagem: Mensagem de nao acesso
    """

    driver = st.session_state.driver

    # Tempos para execução
    tempo_curto = 0.5
    tempo_medio = 1
    tempo_longo = 1.5

    # =============================================
    # VERIFICANDO A EXISTÊNCIA OU ACESSO AO PROCESSO
    # =============================================

    # Verificar se o processo não foi encontrado
    try:
        mudar_iframe('arvore')
        elemento_nao_encontrado = driver.find_element("xpath", '//*[@id="sbmPesquisar"]')
        if elemento_nao_encontrado.is_displayed():
            valor_acesso = "Processo Não encontrado"
            return False, valor_acesso
    except:
        pass  # Processo encontrado, continuar

    # Alternar para o iframe 'arvore' e verificar acesso
    try:
        mudar_iframe('arvore')
        driver.find_element("xpath", '//*[@id="divConsultarAndamento"]/a/span')  # Consultar andamento
    except:
        driver.switch_to.default_content()
        valor_acesso = "Unidade Não Possui Acesso"
        return False, valor_acesso

    # Alternar para o iframe 'visualizacao'
    mudar_iframe('visualizacao')
    time.sleep(tempo_longo)

    # Verificar se a unidade não tem acesso ao processo
    try:
        mensagem_sem_acesso = driver.find_element("xpath", '//*[@id="divMensagem"]/label')
        if mensagem_sem_acesso.is_displayed():
            valor_acesso = "Unidade Não Possui Acesso"
            driver.switch_to.default_content()
            return False, valor_acesso
    except:
        pass  # Unidade tem acesso, continuar
    
    valor_acesso = 'Acesso liberado'

    return True, valor_acesso
  
def validacao_cpf(cpf):

    # Retira apenas os dígitos do CPF, ignorando os caracteres especiais
    numeros = [int(digito) for digito in cpf if digito.isdigit()]

    validacao1 = False
    validacao2 = False

    soma_produtos = sum(a*b for a, b in zip (numeros[0:9], range (10, 1, -1)))
    digito_esperado = (soma_produtos * 10 % 11) % 10
  
    if numeros[9] == digito_esperado:
        validacao1 = True

    soma_produtos1 = sum(a*b for a, b in zip(numeros [0:10], range (11, 1, -1)))
    digito_esperado1 = (soma_produtos1 *10 % 11) % 10

    if numeros[10] == digito_esperado1:
        validacao2 = True
        
    if  validacao1 == True and validacao2 == True:
        return True
    else:
        return False
    

def data_hr_atual():
    # Define o fuso horário GMT-3
    fuso_horario = pytz.timezone("America/Sao_Paulo")
    # Obtém a data e hora atual no fuso horário especificado
    now = datetime.now(fuso_horario)
    # Formata no estilo dd-mm-yyyy hh:mm
    data_hora_atual = now.strftime("%d/%m/%Y %H:%M")
    return data_hora_atual
    

# Tratamento e verificacoes de dados de acesso
def tratamento_verif_users(add_df, df_usuarios):

    add_df = add_df[add_df["CPF"] != "Insira o CPF"]

    if len(add_df) < 1:
        st.error('Insira ao menos 1 CPF para adicionar usuários.')
        return None
    
    # Verificar se o orgao foi inserido
    orgao_teste_df = add_df[add_df["ORGAO"] != "Selecione o Orgão"]
    if len(orgao_teste_df) < 1:
        st.error('Usuários sem órgão informado:')
        st.dataframe(
            add_df.loc[add_df["ORGAO"] == "Selecione o Orgão", ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verificar se um usuario possui dois registros com 2 orgaos diferentes
    duplicados_diferentes_orgao = add_df.groupby('CPF')['ORGAO'].nunique()
    cpf_diferentes = duplicados_diferentes_orgao[duplicados_diferentes_orgao > 1].index
    if not cpf_diferentes.empty:
        st.error('CPF duplicados com órgãos diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes)][['CPF', 'APELIDO', 'ORGAO', 'ACESSO']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None


    # Verifica usuarios sem apelidos
    orgao_teste_df = add_df[(add_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                                (add_df["APELIDO"].str.strip() == "") | 
                                (add_df["APELIDO"] == " ")]
    if len(orgao_teste_df) > 0 :
        st.error('Usuários sem apelidos informado:')
        st.dataframe(
            add_df.loc[(add_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                        (add_df["APELIDO"].str.strip() == "") | 
                        (add_df["APELIDO"] == " "),
                        ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None


    # Validação de CPF
    add_df["CPF_VALIDACAO"] = add_df["CPF"].apply(validacao_cpf)
    if any(~add_df["CPF_VALIDACAO"]):
        st.error('Os dados contêm CPFs inválidos:')
        st.dataframe(
            add_df.loc[~add_df["CPF_VALIDACAO"], ['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verifica duplicados com acessos diferentes
    duplicados_diferentes_cpf = add_df.groupby('CPF')['ACESSO'].nunique()
    cpf_diferentes = duplicados_diferentes_cpf[duplicados_diferentes_cpf > 1].index
    if not cpf_diferentes.empty:
        st.error('CPF duplicados com acessos diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes)][['CPF', 'APELIDO', 'ORGAO', 'ACESSO']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verificar duplicidade na base de dados
    if add_df["CPF"].isin(df_usuarios["CPF"]).any():
        st.error("Os CPFs abaixo já constam na base.")
        st.dataframe(
            add_df.loc[add_df["CPF"].isin(df_usuarios["CPF"])][['CPF', 'APELIDO', 'ORGAO', 'ACESSO']],
            use_container_width=True,
            hide_index=True
        )
        return None

    return add_df.drop_duplicates(subset=['CPF'])[['CPF', 'APELIDO', 'ORGAO', 'ACESSO']]


def extrair_nome_sei(string):
    # Divide a string na primeira ocorrência do parêntese
    nome = string.split('(')[0]
    # Remove espaços extras no início ou fim
    return nome.strip()






