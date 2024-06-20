import os
import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def remove_emojis(text):
    emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # 스마일 이모티콘
                            u"\U0001F300-\U0001F5FF"  # 기호 및 이모티콘
                            u"\U0001F680-\U0001F6FF"  # 기타 이모티콘
                            u"\U0001F1E0-\U0001F1FF"  # 국기 이모티콘
                            u"\U00002702-\U000027B0"  # 다양한 이모티콘
                            u"\U000024C2-\U0001F251"
                            "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_youtube_comments(url):
    print("check0")
    driver = get_driver()
    driver.get(url)
    print("check1")

    time.sleep(5)  # 페이지가 로딩될 때까지 잠시 대기

    # 영상 제목 가져오기
    video_title = driver.title.split(' - YouTube')[0]
    print("check2")

    # 스크롤 내리기(2번)
    for _ in range(2):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
    print("check3")

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

def save_to_csv(title, comments):
    output_file = "test.txt"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(['title', 'comment'])
        for i, comment in enumerate(comments):
            if comment != "" and re.search('[ㄱ-ㅎㅏ-ㅣ가-힣]', comment): # 한국어 댓글만 추출
                # 댓글 전처리(줄바꿈, ", ' 제거)
                comment = comment.replace('"', '').replace("'", '')
                comment = re.sub(r'[\r\n]+', ' ', comment)
                # 댓글 전처리(중국어 제거)
                pattern = re.compile(r'[\u4E00-\u9FFF]')
                comment = re.sub(pattern, '', comment)
            else:
                comment = "영어입니다"
            writer.writerow([title, comment])

if __name__ == "__main__":
    start_time = time.time()
    os.chdir("C:/Users/minhw/Desktop/4-1/소캡디/성희롱댓글/extension/Server")
    youtube_urls = [
        'https://www.youtube.com/watch?v=yLupcG_eFag',
        # 'https://www.youtube.com/watch?v=UrVdyn8yQfs',
        # 'https://www.youtube.com/watch?v=PDcXr7EMi_I',
        # 'https://www.youtube.com/watch?v=pUPI9tmnRSY',
        # 'https://www.youtube.com/watch?v=ISGJ_zrK-LQ',
        # 'https://www.youtube.com/watch?v=pgP3l3VfTJE',
        # 'https://www.youtube.com/watch?v=cqUB16IY3io',
        # 'https://www.youtube.com/watch?v=T9OVGWtIg8s',
        # 'https://www.youtube.com/watch?v=9cQOgdMjwWQ',
        # 'https://www.youtube.com/watch?v=pV_i9_Unf9E',
        # 'https://www.youtube.com/watch?v=fQlMmKKrXAs',
        # 'https://www.youtube.com/watch?v=zki1VPkzFVs',
        # 'https://www.youtube.com/watch?v=6JfRoXmf-8s',
        # 'https://www.youtube.com/watch?v=EtTwxtlRaBc',
        # 'https://www.youtube.com/watch?v=cmKuGxb23z0',
        # 'https://www.youtube.com/watch?v=cZnRHuoTj1s',
        # 'https://www.youtube.com/watch?v=SRxn70fYHlA',
        # 'https://www.youtube.com/watch?v=ie8KbXUd9OE',
        # 'https://www.youtube.com/watch?v=Up7oYIfvpFQ',
        # 'https://www.youtube.com/watch?v=UaXZa_OO-R0',
        # 'https://www.youtube.com/watch?v=OHIh429rt4A',
        # 'https://www.youtube.com/watch?v=oYbYOKRNgOU',
        # 'https://www.youtube.com/watch?v=FwPdj7QRykU',
        # 'https://www.youtube.com/watch?v=AeRq62UQdCA',
        # 'https://www.youtube.com/watch?v=QhsvuvEN6YI',
        # 'https://www.youtube.com/watch?v=Ap3E1c3Grko',
        # 'https://www.youtube.com/watch?v=WuHxbBRTi_0',
        # 'https://www.youtube.com/watch?v=Ujtjnh7WTRM',
    ]
    
    for i, youtube_url in enumerate(youtube_urls):
        video_title, comments = crawl_youtube_comments(youtube_url)
        save_to_csv(comments, f'{video_title}.csv', i)
        print("Done", video_title, i)
    print(f"{time.time() - start_time:.5f} sec")
