import requests
import slack_sdk
from bs4 import BeautifulSoup
import json
import os
import base64
from PIL import Image
import io
import re

# Slack 토큰과 채널 ID를 설정합니다.
slack_token = "발급받아 사용할것"
client = slack_sdk.WebClient(token=slack_token)

# socks 프로토콜을 지원하는 requests 라이브러리를 사용
#torrc 설정값을 확인하고 적절히 수정후 사용해야합니다.
proxies = {"http": "socks5h://localhost:19050", "https": "socks5h://localhost:19051"}

start_page = 1
end_page = 2

# 사용자로부터 특정 단어를 입력받습니다.
keyword = input("Please enter a keyword: ")

matches = []

for page_num in range(start_page, end_page + 1):
    if page_num == 1:
        url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    else:
        url = f"http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/page/{page_num}/"

    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.select("h1")
    descriptions = soup.select("div.description")
    readmore_links = soup.select("a.readmore")

    for title, description, link in zip(titles, descriptions, readmore_links):
        title_text = title.get_text()
        description_text = description.get_text()

        if (
            keyword.lower() in title_text.lower()
            or keyword.lower() in description_text.lower()
        ):
            link_url = (
                "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion"
                + link["href"]
            )
            link_response = requests.get(link_url, proxies=proxies)
            link_soup = BeautifulSoup(link_response.text, "html.parser")
            paragraphs = [p.get_text() for p in link_soup.select("p")]

            # 이미지 태그를 모두 찾습니다.
            img_tags = link_soup.find_all("img")

            for i, img in enumerate(img_tags):
                img_data = img["src"].encode()

                # 이미지 데이터가 base64로 인코딩되어 있다면
                if img_data.decode().startswith(
                    "data:image/png;base64,"
                ) or img_data.decode().startswith("data:image/jpeg;base64,"):
                    # base64 데이터를 디코딩합니다.
                    img_data = (
                        img_data.decode()
                        .replace("data:image/png;base64,", "")
                        .replace("data:image/jpeg;base64,", "")
                    )
                    img_data = base64.b64decode(img_data)

                    # 이미지 파일로 저장합니다.
                    img_filename = (
                        f"{keyword}_{title_text}_{i}.png"
                        if img_data.startswith(b"data:image/png;base64,")
                        else f"{keyword}_{title_text}_{i}.jpeg"
                    )
                    with open(img_filename, "wb") as f:
                        f.write(img_data)

                    # 이미지 파일을 Slack에 업로드합니다.
                    try:
                        response = client.files_upload(
                            channels="bianlian_target", file=img_filename
                        )
                        assert response["ok"]
                        print(f"Image uploaded to Slack: {img_filename}")
                    except Exception as e:
                        print(f"Error uploading image to Slack: {e}")

            matches.append(
                {
                    "title": title_text,
                    "description": description_text,
                    "link": link_url,
                    "paragraphs": paragraphs,
                }
            )

for i, item in enumerate(matches):
    item_str = json.dumps(item, ensure_ascii=False)
    if len(item_str) >= 3000:
        safe_title = re.sub("[^a-zA-Z0-9 \n\.]", "", item["title"])
        file_path = f"{keyword}_{safe_title}.txt"
        with open(file_path, "w") as f:
            f.write(item_str + "\n")

        try:
            response = client.files_upload(
                channels="목표 채널명을 적을것", file=file_path
            )
            assert response["ok"]
            print(f"File uploaded to Slack: {file_path}")
        except Exception as e:
            print(f"Error uploading file to Slack: {e}")
