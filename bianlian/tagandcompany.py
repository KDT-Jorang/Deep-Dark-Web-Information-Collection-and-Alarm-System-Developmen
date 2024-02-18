import requests
from bs4 import BeautifulSoup
import json
import slack_sdk
import datetime

# Slack 토큰을 설정합니다.
slack_token = "할당 받아 사용할것"
client = slack_sdk.WebClient(token=slack_token)

# socks 프로토콜을 지원하는 requests 라이브러리를 사용
proxies = {"http": "socks5h://localhost:19050", "https": "socks5h://localhost:19051"}

# 회사 이름과 날짜를 저장할 리스트를 생성합니다.
companies = []
# 태그를 저장할 리스트를 생성합니다.
tags = []

# 회사 정보가 있는 페이지의 URL을 설정합니다.
url_companies = (
    "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/companies/"
)
# 태그가 있는 페이지의 URL을 설정합니다.
url_tags = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/tags/"

# 회사 정보 URL에 요청을 보냅니다.
response_companies = requests.get(url_companies, proxies=proxies)
# 태그 URL에 요청을 보냅니다.
response_tags = requests.get(url_tags, proxies=proxies)

# BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
soup_companies = BeautifulSoup(response_companies.text, "html.parser")
soup_tags = BeautifulSoup(response_tags.text, "html.parser")

# <li class="post"> 태그를 선택합니다.
post_elements = soup_companies.select("li.post")
# <a> 태그 중 style이 'font-size:1rem'인 것을 선택합니다.
tag_elements = soup_tags.select("a[style='font-size:1rem']")

# 각 post의 회사 이름과 날짜를 가져와 리스트에 추가합니다.
for post in post_elements:
    company_name = post.find("a").get_text()
    date = post.find("span", class_="meta").get_text()
    companies.append({"company_name": company_name, "date": date})

# 각 태그의 텍스트를 가져와 리스트에 추가합니다.
for tag in tag_elements:
    tags.append(tag.get_text())

# 현재 시간을 가져와 파일 이름에 포함합니다.
now = datetime.datetime.now()
filename = now.strftime("%Y%m%d%H%M%S") + "_jsonl.json"

# 크롤링한 회사 정보와 태그를 JSON 파일로 저장합니다.
with open(filename, "w") as f:
    json.dump({"companies": companies, "tags": tags}, f)

# Slack에 파일을 업로드합니다.
try:
    response = client.files_upload(channels="채널지정할것", file=filename)
    print(response.data)  # 응답 내용을 출력합니다.
    assert response["ok"]
    print(f"File uploaded to Slack: {filename}")
except Exception as e:
    print(f"Error uploading file to Slack: {e}")
