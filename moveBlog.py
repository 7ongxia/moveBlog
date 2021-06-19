from bs4 import BeautifulSoup
from datetime import datetime
import time
import webbrowser
import requests
import json


class Tistory:  
    def __init__(self):  
        self.outputType = "json"
        self.blogName = "SECRET"

        client_id = "SECRET"
        Secret_Key = "SECRET"
        redirect_uri = "https://SECRET"
        state_param = "RandomString"

        auth_url = f"https://www.tistory.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state_param}"
        webbrowser.open(auth_url)
        
        code = input("주소창에서 복사한 코드 값을 입력해주세요(?code=***): ")
        access_url = "https://www.tistory.com/oauth/access_token"
        params = {
            'client_id': f'{client_id}',
            'client_secret': f'{Secret_Key}',
            'redirect_uri': f'{redirect_uri}',
            'code': f"{code}",
            'grant_type': 'authorization_code'
        }
        self.accessToken = requests.get(access_url, params=params).text.replace("access_token=", "")
        
    def get_category(self):  
        url = f'https://www.tistory.com/apis/category/list'
        params = {
            'access_token': f'{self.accessToken}',
            'output': f'{self.outputType}',
            'blogName': f'{self.blogName}'
        }
        response = requests.get(url, params=params)
        print(response.json())

    def post_write(self, title, content):
        url = "https://www.tistory.com/apis/post/write"
        categoryId = "SECRET"
        data = {
            'access_token': f'{self.accessToken}',
            'output': f'{self.outputType}',
            'blogName': f'{self.blogName}',
            'title': f'{title}',
            'content': f'{content}',
            'category': f'{categoryId}'
        }
        response = requests.post(url, data=data).json()
        print(json.dumps(response, indent=4, sort_keys=True))


def getEgloosPost(i):
    req = requests.get(f"http://SECRET/page/{i}")
    soup = BeautifulSoup(req.text, 'html.parser')

    # 날짜
    s = soup.select('.published')[0].text
    # timestamp = time.mktime(datetime.strptime(s, "%Y/%m/%d %H:%M").timetuple())
    # print(timestamp)

    # 본문
    body = soup.select('.hentry')[0].get_text('\n\n')[:-20]
    # print(body, '\n')

    # 제목
    title = soup.select('.entry-title a')[0].text
    if title[:2] == '20':
        title = body.split('\n', 1)[0]
    title = f"{s[:10]} {title}"
    # print(f"{i}: {title}")

    # 이미지
    images = []
    source = soup.find_all("img", {"class": "image_mid"})
    for img in source:
        images.append(img.get("src"))
    # print(f"images: {images}", '\n')

    return {
        'title': title,
        'body': body,
        'image': images
    }


if __name__ == "__main__":
    tistory = Tistory()

    for i in range(1, 151):
        post = getEgloosPost(i)
        time.sleep(1)
        tistory.post_write(title=post['title'], content=post['body'])
        time.sleep(1)
        break

# TODO: Retreive an egloos content as a HTML format. + Image uploading function