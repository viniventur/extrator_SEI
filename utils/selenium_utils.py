import time
import streamlit as st
import os

from utils.config import is_local, modulos, voltar_inicio, data_hr_atual
from utils.chrome_config import chrome, update_download_directory


def excluir_driver():
    """Fecha o driver do Selenium se estiver aberto."""
    if 'driver' in st.session_state:
        try:
            st.session_state.driver.quit()
        except Exception as e:
            st.warning(f"Erro ao encerrar o driver: {e}")
        del st.session_state['driver']

def mudar_iframe(iframe):
    """Muda o frame no Selenium."""
    driver = st.session_state.driver

    if iframe == 'arvore':
        driver.switch_to.default_content()
        iframe_arvore = driver.find_element('name', "ifrArvore")
        driver.switch_to.frame(iframe_arvore)
    elif iframe == 'visualizacao':
        driver.switch_to.default_content()
        iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
        driver.switch_to.frame(iframe_visualizacao)
    elif iframe == 'default':
        driver.switch_to.default_content()

def sair():
    with st.spinner('Redirecionando...'):
        # excluir os arquivos remanscente de outras sessoes na pasta temporaria
        if 'diretorio_download' in st.session_state:
            for item in os.listdir(st.session_state.diretorio_download):
                item_path = os.path.join(st.session_state.diretorio_download, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)  # Remove arquivos
        excluir_driver()
        st.cache_resource.clear()
        st.cache_data.clear()
        st.session_state.clear()
        st.switch_page(modulos[0][1])


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