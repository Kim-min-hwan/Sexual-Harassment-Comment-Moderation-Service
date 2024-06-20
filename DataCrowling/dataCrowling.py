import os
from glob import glob
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as CromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
import re

def remove_emojis(text):
    # 이모티콘 패턴 정의
    emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # 스마일 이모티콘
                            u"\U0001F300-\U0001F5FF"  # 기호 및 이모티콘
                            u"\U0001F680-\U0001F6FF"  # 기타 이모티콘
                            u"\U0001F1E0-\U0001F1FF"  # 국기 이모티콘
                            u"\U00002702-\U000027B0"  # 다양한 이모티콘
                            u"\U000024C2-\U0001F251"
                            "]+", flags=re.UNICODE)
    # 이모티콘 제거
    return emoji_pattern.sub(r'', text)


def crawl_youtube_comments(url):
    driver = webdriver.Chrome(service=CromeService(ChromeDriverManager().install()))

    driver.get(url)
    time.sleep(5)  # 페이지가 로딩될 때까지 잠시 대기

    # 영상 제목 가져오기
    video_title = driver.title.split(' - YouTube')[0]

    # 유튜브 Shorts 처리
    if 'shorts' in url:
        button = driver.find_element(By.XPATH, '//*[@id="comments-button"]/ytd-button-renderer/yt-button-shape/label/button')
        driver.execute_script("arguments[0].click();", button)


    # 스크롤 내리기(끝까지)
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)  # 페이지 로딩 대기
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    '''
    # 대댓글 열기
    elements = driver.find_elements(By.CSS_SELECTOR, '#more-replies')
    for element in elements:
        driver.execute_script("arguments[0].click();", element)
    while True:
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#more-replies'))).click()
            time.sleep(3)
        except:
            break
    '''

    # 댓글 요소들 찾기
    comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
    authors = driver.find_elements(By.XPATH, '//*[@id="author-text"]')


    # 한국어 댓글만 추출
    korean_comments = []
    for i in range(len(comments)):
        if comments[i].text != "" and re.search('[ㄱ-ㅎㅏ-ㅣ가-힣]', comments[i].text):  # 한글이 포함되어 있는지 확인
            korean_comments.append([video_title, comments[i].text])

    driver.quit()

    return video_title, korean_comments

def read_urls(url):
    driver = webdriver.Chrome(service=CromeService(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(5)  # 페이지 로딩 대기
    video_links = driver.find_elements(By.CSS_SELECTOR, 'a.ytd-playlist-video-renderer')

    youtube_urls = []
    for link in video_links:
        href = link.get_attribute('href')
        if href:
            youtube_urls.append(href)

    driver.quit()
    return youtube_urls

def save_to_csv(comments, output_file, i):
    output_file = f"normal_comment_files/youtube_comments{i}.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'comment'])
        for comment in comments:
            # 댓글 전처리(줄바꿈, ", ' 제거)
            comment[1] = comment[1].replace('"', '').replace("'", '')
            comment[1] = re.sub(r'[\r\n]+', ' ', comment[1])
            writer.writerow(comment)

if __name__ == "__main__":
    os.chdir("C:/Users/minhw/Desktop/4-1/소캡디/성희롱댓글/code/Data_Crowling")
    # youtube_url = input("Input url: ")
    playlist_url = "https://www.youtube.com/playlist?list=PLjL7wW_CRkrYg0Ni7PMB_yJqewjTvpgt1"

    youtube_urls = read_urls(playlist_url)

    i = len(os.listdir("normal_comment_files/"))
    for j, link in enumerate(youtube_urls):
        video_title, comments = crawl_youtube_comments(link)

        save_to_csv(comments, f'{video_title}.csv', i)
        print(f"Done ({j} / {len(youtube_urls)})", video_title, i)
        i += 1
