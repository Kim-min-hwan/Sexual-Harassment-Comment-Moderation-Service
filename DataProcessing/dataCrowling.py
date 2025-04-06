import os
from glob import glob
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import csv
import re

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 브라우저를 띄우지 않고 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    driver_path = ChromeDriverManager().install()
    driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")

    driver = webdriver.Chrome(service=ChromeService(executable_path=driver_path), options=chrome_options)
    return driver

def crawl_youtube_comments(url):
    driver = get_driver()
    driver.get(url)

    time.sleep(5)

    # 영상 제목 가져오기
    video_title = driver.title.split(' - YouTube')[0]

    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, 500);") # 스크롤을 약간 내리지 않으면 댓글이 안보이는 문제 발생.
    time.sleep(3)

    cnt_scroll = 2 # 스크롤 횟수
    for _ in range(cnt_scroll):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
    
    
    # 댓글 찾기
    comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

    # 한국어로만 이루어진 댓글 추출 (초성 포함)
    korean_comments = []
    for i in range(len(comments)):
        if comments[i].text != "" and re.fullmatch(r"[ㄱ-ㅎㅏ-ㅣ가-힣0-9\s\W]+", comments[i].text): # 특수문자와 숫자 허용
            korean_comments.append(comments[i].text)

    driver.quit()

    return video_title, korean_comments

def save_to_csv(title, comments):
    output_file = "test.txt"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(["title", "comment"])
        
        # 전처리(줄바꿈, ", ' , 제거)
        for i, comment, in enumerate(comments):
            # 한국어로만 이루어진 댓글 추출 (초성 및 특수문자와 숫자 허용)
            if comment != "" and re.fullmatch(r"[ㄱ-ㅎㅏ-ㅣ가-힣0-9\s\W]+", comment): 
                comment = comment.replace('"', '').replace("'", '')
                comment = re.sub(r'[\r\n]+', ' ', comment)

                writer.writerow([title, comment])


if __name__ == "__main__":
    youtube_url ="[Youtube URL]"

    video_title, comments = crawl_youtube_comments(youtube_url)
    save_to_csv(video_title, comments)