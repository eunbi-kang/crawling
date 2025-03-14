import sys
import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 🔥 sys.path 추가하여 crawling 경로에서 실행 가능하도록 설정
sys.path.append("..")

# 🔥 올바른 경로에서 driver 가져오기
from dynamic_crawling import driver

if __name__ == "__main__":
    url = "https://www.hollys.co.kr/store/korea/korStore2.do?a=2&b=3"
    browser = driver()  # ✅ driver() 함수 호출

    browser.get(url)import sys
import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 🔥 sys.path 추가하여 crawling 경로에서 실행 가능하도록 설정
sys.path.append("..")

# 🔥 올바른 경로에서 driver 가져오기
from dynamic_crawling import driver

if __name__ == "__main__":
    url = "https://www.hollys.co.kr/store/korea/korStore2.do?a=2&b=3"
    browser = driver()  # ✅ driver() 함수 호출

    browser.get(url)
    time.sleep(random.uniform(2, 4))

    # table = browser.find_element(By.XPATH, '''//*[@id="contents"]/div[2]/fieldset/fieldset/div[1]''')
    trs = BeautifulSoup(browser.page_source, 'html.parser').find_all("tr")

    page = 1;
    while True:


    browser.quit()  # ✅ 브라우저 닫기 추가 (안 닫으면 계속 실행됨)
