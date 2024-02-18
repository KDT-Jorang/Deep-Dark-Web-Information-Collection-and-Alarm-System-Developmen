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
        print(f"메시지 전송 실패: {response.status_code}, 응답: {response.text}")


#######################################################################################################################

# 새로운 피해 기업이 있는지 확인
def check_news(result):
    contents_file = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(contents_file, 'victim_list.txt')
    use_new_file = None
    if not os.path.exists(contents_file):
        os.makedirs(contents_file)
    existing_titles = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f_read:
            for line in f_read:
                if line.startswith('제목 : '):
                    title = line.strip().replace('제목 : ', '')
                    existing_titles.add(title)
            
    except FileNotFoundError:
        pass
    
    # 새로운 항목 있는지 title로 확인

    new_post = ''
    for title, utime, href in result:
        if title not in existing_titles:
            new_post += '\n\n' + f'제목 : {title}\n게시날짜 : {utime}\n링크 : {href}\n\n'
            print(f"새로운 피해 기업 : {title}")
    
    if new_post:
        with open(file_path, 'w', encoding='utf-8') as f_write:
            f_write.write(new_post + '\n\n' +'################\n' + datetime.today().strftime("%Y/%m/%d %H:%M:%S") + f'\n총 피해기업 : {len(result)}\n################\n')
            print("저장완료, 슬랙으로 전송합니다.")
        sending_slack(use_new_file)
    else:
        message = "추가 피해는 없습니다."
        webhook_url = "여기 채워주세요요"
        payload = {'text' : message}
        json_payload = json.dumps(payload)
        response = requests.post(webhook_url, data=json_payload, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            print("메시지가 성공적으로 전송되었습니다.")
        else:
            print(f"메시지 전송 실패: {response.status_code}, 응답: {response.text}")


    
#######################################################################################################################

max_attempts = 5
# 블랙캣은 튕기는 경우가 너무 많아 추가 연결 구현

def load_retry(driver, URL, max_attempts, page_number):
     attempts = 0
     while attempts < max_attempts :
        try:
            driver.get(URL)
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/app-root/app-shell/div/app-blog/app-loader/div/div/div[2]/div[1]/div[2]/div[1]")))
            print(f"{page_number}페이지 연결 성공")
            break
        except (TimeoutException, NoSuchElementException) as e:
            print(f"재시도 {attempts + 1}: {e}")
            attempts +=1
            if attempts == max_attempts:
                print(f"{page_number}페이지 연결 실패, 다음 페이지로 넘어갑니다.")

#######################################################################################################################

#크롤링 메인 부분
def main():
    start_page = 1
    end_page = 7

    result = []
    try:
        for page_number in range(start_page, end_page + 1):
            URL = f"http://alphvuzxyxv6ylumd2ngp46xzq3pw6zflomrghvxeuks6kklberrbmyd.onion/?page={page_number}"
            with webdriver.Chrome(service=service, options=chrome_options) as driver:
                load_retry(driver, URL, max_attempts, page_number)
                """ driver.set_page_load_timeout(600)
                driver.get(URL)
                time.sleep(20) """
                
                for i in range(1, 10) :
                    new_post_id = f"/html/body/app-root/app-shell/div/app-blog/app-loader/div/div/div[2]/div[{i}]/div[2]/div[1]"
                    new_contents_link= f'/html/body/app-root/app-shell/div/app-blog/app-loader/div/div/div[2]/div[{i}]/div[3]/div[2]/a'
                    upload_time_xpath = f'/html/body/app-root/app-shell/div/app-blog/app-loader/div/div/div[2]/div[{i}]/div[2]/div[2]'
                                
                        # 제목만 불러오는 부분
                    try:
                        new_post_title = driver.find_element(By.XPATH, new_post_id)
                        title = new_post_title.text
                    except NoSuchElementException:
                            #print(f"NO title : {i}")
                            continue
                                    
                        # 링크 불러오는 부분
                    try:
                        new_contents= driver.find_element(By.XPATH, new_contents_link) #element와 elements 조심할 것.
                        href = new_contents.get_attribute('href')
                    except NoSuchElementException:
                            #print(f"NO link in {i}")
                            continue           
                                    
                        # 업로드 날짜 불러오는 부분
                    try:
                        upload_time = driver.find_element(By.XPATH, upload_time_xpath)
                        utime = upload_time.text
                    except NoSuchElementException:
                            #print(f"NO time info : {i}")
                            continue
                        
                    result.append((title, utime, href))
                    

                     
    except (NoSuchElementException, TimeoutException):
            print(f"Error {page_number}")                              
    
    return result
    



# 전체 피해 확인 후 이후에 새로운 피해 기업이 있는지 확인하는 함수 
def new(result):
    contents_file = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(contents_file, 'victim_list.txt')
    new_file_path = os.path.join(contents_file, 'new_victim_list.txt')
    use_new_file = 'new_victim_list.txt'
    
    if not os.path.exists(contents_file):
        os.makedirs(contents_file)
    
    existing_titles = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f_read:
            for line in f_read:
                if line.startswith('제목 : '):
                    title = line.strip().replace('제목 : ', '')
                    existing_titles.add(title.strip())
            
    except FileNotFoundError:
        pass
    
    new_post = ''

    for title, utime, href in result:
        if title.strip() not in existing_titles:
            new_post += '\n\n' + f'제목 : {title}\n게시날짜 : {utime}\n링크 : {href}\n\n'
            print(f"새로운 피해 기업 : {title}")
    
    if new_post:
        with open(new_file_path, 'w', encoding='utf-8') as f_write:
            f_write.write(new_post + '\n\n' +'################\n' + datetime.today().strftime("%Y/%m/%d %H:%M:%S") + f'\n새로운 피해기업 : {len(result)}\n################\n')
            print("저장완료, 슬랙으로 전송합니다.")
        sending_slack(use_new_file)
    else:
        message = "추가 피해는 없습니다."
        webhook_url = "여기 채워주세요"
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
