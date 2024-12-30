from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

# Configurar o Selenium e o ChromeDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Para executar em modo headless, sem abrir o navegador
service = Service('chromedriver.exe')  # Atualize o caminho para o ChromeDriver
chrome_options.add_experimental_option('detach', True)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Abrir o site
    driver.get(env['SITE_SEI'])  # Substitua pela URL do sistema que você está acessando


    driver.find_element("xpath", '//*[@id="txtUsuario"]').send_keys(env['CPF_SEI'])
  
    driver.find_element("xpath", '//*[@id="pwdSenha"]').send_keys(env['SENHA_SEI'])
    driver.find_element("xpath", '//*[@id="selOrgao"]').send_keys('ORGAO')
    driver.find_element("xpath", '//*[@id="sbmLogin"]').click()
    # Esperar a página carregar completamente (ajuste se necessário)
    driver.implicitly_wait(10)


    driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys('PROCESSOX')
    driver.find_element("xpath", '//*[@id="txtPesquisaRapida"]').send_keys(Keys.ENTER)

    # Alternar para o iframe 'ifrVisualizacao'
    driver.switch_to.default_content()
    iframe_visualizacao = driver.find_element('name', "ifrVisualizacao")
    driver.switch_to.frame(iframe_visualizacao)
    driver.find_element("xpath", '//*[@id="divArvoreAcoes"]/a[18]/img').click()
    # Localizar os elementos com o texto "Formulário Contratação Direta PGE"
   # Localizar a tabela com o ID "tblDocumentos"
    tabela = driver.find_element(By.ID, "tblDocumentos")

    # Localizar as células na tabela que contêm o texto "Formulário Contratação Direta"
    celulas = tabela.find_elements(By.XPATH, ".//td[contains(text(), 'Formulário Utilização da Ata de Registro de Preço')]")


    # Contar os elementos encontrados
    quantidade = len(celulas)
    print(f"Número de formulários encontrados: {quantidade}")

finally:
    # Fechar o navegador
    driver.quit()