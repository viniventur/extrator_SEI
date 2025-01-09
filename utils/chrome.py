from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.funcoes_auxiliares import *

def chrome():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_extension(r'SEI Pro - Chrome Web Store 1.5.5.54.crx')

    if is_local():
        service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    return driver