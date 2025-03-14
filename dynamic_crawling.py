from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from user_agents import parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


# 서비스 환경별 크롬 드라이버 설정
def driver():
    userAgent = generate_user_agent()
    user_agent = parse(userAgent)

    # 옵션 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.page_load_strategy = "normal"
    chrome_options.add_argument("--enable-automation")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--lang=ko_KR")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--mute-audio")

    # 크롬 드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(3)
    return driver
