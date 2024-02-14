import requests
from bs4 import BeautifulSoup
import json
import os
import slack_sdk

# Slack 토큰과 채널 ID를 설정합니다.
slack_token = "각자 발급받은 토큰삽입할것"
client = slack_sdk.WebClient(token=slack_token)

# socks 프로토콜을 지원하는 requests 라이브러리를 사용
proxies = {"http": "socks5h://localhost:9150", "https": "socks5h://localhost:9150"}

# 시작 페이지와 끝 페이지를 설정합니다.
start_page = 1
end_page = 10

# 각 페이지를 순회하며 크롤링을 수행합니다.
for page_num in range(start_page, end_page + 1):
    # 페이지 번호를 URL에 포함시킵니다.
    url = f"http://각자원하는 사이트지정할것/page/{page_num}"

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

    # 각 아이템을 슬랙에 메시지로 보냅니다.
    for title, description in zip(title_texts, description_texts):
        text = f"Title: {title}\nDescription: {description}"
        client.chat_postMessage(channel="bianlian", text=text)
