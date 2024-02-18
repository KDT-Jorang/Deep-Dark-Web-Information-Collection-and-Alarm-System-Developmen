import time
import os 
import json 
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
service = Service(executable_path="chromedriver.exe")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('disable-gpu')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('hide-scrollbars')
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150") # sock5 = dns 조회도 Tor가 한다.
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36') # 범용 에이전트를 구했다.
chrome_options.add_argument('--headless') #데몬으로 실행

#######################################################################################################################


# 슬랙 전송
def sending_slack(use_new_file):
    contents_file = os.path.dirname(os.path.abspath(__file__))

    if use_new_file:
        file_name = 'new_victim_list.txt'
    else:
        file_name = 'victim_list.txt'
    
    file_path = os.path.join(contents_file, file_name)
    
    # 웹 훅 입력
    webhook_url = "여기 채워주세요"

    try:
        # utf-8 인코딩으로 파일 열기
        with open(file_path, 'r', encoding='utf-8') as file:
            message = file.read().strip()
    except UnicodeDecodeError as e:
        print(f"파일을 읽는 중 오류 발생: {e}")
        message = "파일을 읽는 중 오류 발생"
    except Exception as e:
        print(f"오류 발생: {e}")
        message = "알 수 없는 오류 발생"
    if not message:
        print("메시지가 비어 있습니다.")
        return

    payload = {'text' : message}
    json_payload = json.dumps(payload)
    response = requests.post(webhook_url, data=json_payload, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        print("메시지가 성공적으로 전송되었습니다.")
    else:
        print(f"메시지 전송 실패: {response.status_code}, 응답: {respo채워주세요"
        payload = {'text' : message}
        json_payload = json.dumps(payload)
        response = requests.post(webhook_url, data=json_payload, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            print("메시지가 성공적으로 전송되었습니다.")
        else:
            print(f"메시지 전송 실패: {response.status_code}, 응답: {response.text}")


# 시작 부분
def root():
    user_input = input("다크롤러 작동 중입니다. 원하시는 기능을 선택해 주세요 (전체 기업 현황 / 새로운 기업): ")
     
    if user_input == "전체 기업 현황":
        result = main()
        check_news(result)  
    elif user_input == "새로운 기업":
        result = main()
        new(result)
    else:
        print ("기능 중 선택하세요.")
        

if __name__ == "__main__":
    root()
