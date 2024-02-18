import requests
from bs4 import BeautifulSoup
import slack_sdk
import json
import os

# Slack 토큰과 채널 ID를 설정합니다.
slack_token = "발급받아 사용할것"
client = slack_sdk.WebClient(token=slack_token)

# socks 프로토콜을 지원하는 requests 라이브러리를 사용
proxies = {"http": "socks5h://localhost:19050", "https": "socks5h://localhost:19051"}

# 시작 페이지와 끝 페이지를 설정합니다. 
start_page = 1
end_page = 3

# 각 아이템을 저장할 리스트를 생성합니다.
items = []

# 각 페이지를 순회하며 크롤링을 수행합니다.
for page_num in range(start_page, end_page + 1):
    if page_num == 1:
        url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    else:
        url = f"http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/page/{page_num}"

    # 해당 URL에 요청을 보냅니다.
    response = requests.get(url, proxies=proxies)

    # BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.select("h1")
    title_texts = [title.get_text() for title in titles]

    descriptions = soup.select("div.description")
    description_texts = [description.get_text() for description in descriptions]

    for title, description in zip(title_texts, description_texts):
        items.append((title, description))

# 이전에 크롤링한 아이템들을 불러옵니다.
if os.path.exists("previous_items.json"):
    with open("previous_items.json", "r") as f:
        previous_items = json.load(f)
else:
    previous_items = []

# 새로운 아이템들을 찾습니다.
new_items = [item for item in items if item not in previous_items]

# 새로운 아이템들을 역순으로 정렬합니다.
new_items.reverse()

# 새로운 아이템들을 Slack에 업로드합니다.
for title, description in new_items:
    text = f"Title: {title}\nDescription: {description}"
    client.chat_postMessage(channel="bianlian", text=text)

# 모든 아이템들을 저장합니다.
with open("previous_items.json", "w") as f:
    json.dump(items, f)
