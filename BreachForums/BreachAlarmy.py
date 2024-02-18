import os
import time
from slackAPI import SlackAPI
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

#option
chrome_options = Options()


chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('disable-gpu')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('hide-scrollbars')
chrome_options.add_argument('headless')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel MAc OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

URL = "http://breachedu76kdyavc6szj6ppbplfqoz3pgrk3zw57my4vybgblpfeayd.onion/"
TOKEN = "--"

# 스레드 내용 획득(스크린샷)
def get_thread_png(driver, url):
    try:
        driver.get(url)
        element = driver.find_element(By.XPATH, '/html/body/div[1]/main/table[1]/tbody/tr[2]/td/div/div')
        png = element.screenshot_as_png
        
        return png
    
    except Exception as e:
        print("Error Occur : ", str(e))
        return False
    

# 새로운 스레드 정보 획득
def get_new_thread(driver, checked_threads):
    try:
        file_writer = open('checklist','a',newline='',encoding='utf-8')

        print("Connect To BreachForums")
        driver.get(URL+'Forum-Databases')
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        td_tag = soup.find('td', class_='tcat', string='Normal Threads')
        td_tags = td_tag.find_all_next(class_='inline_row')

        threads = []
        
        # 각 스레드 파싱
        print("Get Threads Info")
        for td_tag in td_tags:
            # 스레드 제목
            title_span = td_tag.find('span', class_='subject_new')
            title = title_span.text
            if title in checked_threads: # 이미 체크한 스레드인지 확인
                continue
            
            # 스레드 작성자
            author = td_tag.find('span', class_='author smalltext')
            # 작성자 칭호가 없을 경우
            if author.find('span') is None:
                author = author.text
            # 작성자 칭호가 존재할 경우
            else:
                author = author.find('span').text
            
            # 스레드 작성 날짜
            date = td_tag.find('span', class_='forum-display__thread-date').text

            # 스레드 스크린샷
            thread_url = URL + (title_span.find('a')['href'])
            png = get_thread_png(driver, thread_url)
            
            thread = {'title':title, 'author':author, 'date':date, 'png':png}

            # 확인한 스레드들을 목록화
            file_writer.writelines(thread['title']+'\n')
            threads.append(thread)
        
        file_writer.close()
        
        return threads
    
    except Exception as e:
        print("Error Occur : ", str(e))
        return False

def start_alarm():
    service = Service(executable_path="chromedriver.exe")
    
    if not os.path.exists('checklist'):
        open('checklist','w')
    
    # 이미 알림을 보낸 스레드인지 파일을 읽어서 확인
    file_reader = open('checklist','r',newline='',encoding='utf-8')
    checked_threads = []
    # 개행문자 제거
    for line in file_reader:
        checked_threads.append(line.strip())
    file_reader.close()
    
    # 슬랙 API 생성 및 연결
    token = "--"
    slack_bot = SlackAPI(token)
    channel_id = slack_bot.get_channel_id("프로젝트")
    
    # 120초 간격으로 크롤링 시도
    while(1):
        # 셀레니움 웹 드라이버 생성
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(600)
        
        print('Checking BreachForums...')
        new_threads = get_new_thread(driver, checked_threads)
        
        if new_threads:
            for new_thread in new_threads:
                # 슬랙에 보낼 메시지 생성
                post_message = f"> *{new_thread['title']}*\n> `by {new_thread['author']} | {new_thread['date']}`"
                
                # 슬랙에 파일 전송
                slack_bot.post_file(channel_id, new_thread['png'], post_message)
                
                # 확인된 스레드 리스트 추가
                checked_threads.append(new_thread['title'])
                print(f"Find New Thread : {new_thread['title']}")
        time.sleep(10)
        
        # 셀레니움 크롬 드라이버 초기화
        driver.quit()
        service.stop()
        service = Service(executable_path="chromedriver.exe")
        
start_alarm()