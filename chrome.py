from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def chrome():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=chrome_options, service=Service(executable_path='./chromedriver.exe'))
    return driver