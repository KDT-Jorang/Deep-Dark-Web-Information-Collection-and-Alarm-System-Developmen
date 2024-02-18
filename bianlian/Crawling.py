import requests
from bs4 import BeautifulSoup
import slack_sdk
import os
import json

# Slack 토큰과 채널 ID를 설정합니다.
slack_token = "발급받은 토큰 사용할것"
client = slack_sdk.WebClient(token=slack_token)

# socks 프로토콜을 지원하는 requests 라이브러리를 사용
proxies = {"http": "socks5h://localhost:9150", "https": "socks5h://localhost:9150"}

# 시작 페이지와 끝 페이지를 설정합니다.
start_page = 1
end_page = 10

# 각 아이템을 저장할 리스트를 생성합니다.
items = []

# 각 페이지를 순회하며 크롤링을 수행합니다.
for page_num in range(start_page, end_page + 1):
    # 페이지 번호가 1이면 첫 페이지의 URL을 사용하고, 그 외에는 일반적인 URL을 사용합니다.
    if page_num == 1:
        url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    else:
        url = f"http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/page/{page_num}"

    # 해당 URL에 요청을 보냅니다.
    response = requests.get(url, proxies=proxies)

    # BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
    soup = BeautifulSoup(response.text, "html.parser")

    # 제목 가져오기
    titles = soup.select("h1")  # <h1> 태그 선택
    title_texts = [title.get_text() for title in titles]

    # 설명 가져오기
    descriptions = soup.select("div.description")  # <div class="description"> 태그 선택
    description_texts = [description.get_text() for description in descriptions]

    # 각 아이템을 리스트에 추가합니다.
    for title, description in zip(title_texts, description_texts):
        items.append((title, description))

# 이전에 크롤링한 데이터를 불러옵니다.
if os.path.exists('previous_items.json'):
    with open('previous_items.json', 'r') as f:
        previous_items = json.load(f)
else:
    previous_items = []

# 새롭게 크롤링한 데이터와 이전 데이터를 비교합니다.
new_items = [item for item in items if item not in previous_items]

# 새로운 아이템만 Slack으로 전송합니다.
for title, description in new_items:
    text = f"Title: {title}\nDescription: {description}"
    client.chat_postMessage(channel="업로드할 체널명 입력할것", text=text)

# 새롭게 크롤링한 데이터를 저장합니다.
with open('previous_items.json', 'w') as f:
    json.dump(items, f)
