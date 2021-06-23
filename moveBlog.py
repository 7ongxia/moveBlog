from bs4 import BeautifulSoup, Comment
from decouple import config
import urllib.request
import webbrowser
import requests
import json
import time


class Tistory:  
    def __init__(self):  
        self.outputType = "json"
        self.blogName = config('blogName')

        client_id = config('client_id')
        Secret_Key = config('Secret_Key')
        redirect_uri = config('redirect_uri')
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
        categoryId = config('redirect_uri')
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
    
    def post_image(self, image):
        url = "https://www.tistory.com/apis/post/attach"
        urllib.request.urlretrieve(image, "tistory.jpg")
        
        image = open('tistory.jpg', 'rb')
        file = {'uploadedfile': image}
        data = {
            'access_token': f'{self.accessToken}',
            'output': f'{self.outputType}',
            'blogName': f'{self.blogName}'
        }
        response = requests.post(url, data=data, files=file)
        item = json.loads(response.text)
        imgUrl = item['tistory']['replacer'].replace("\"", "\"\"")
        return imgUrl


def getEgloosPost(i, tistory):
    req = requests.get(f"{config('egloosUrl')}/page/{i}")
    soup = BeautifulSoup(req.text, 'html.parser')

    # 날짜
    s = soup.select('.published')[0].text

    # 본문 (HTML)
    content = soup.find_all("div", {'class':'hentry'})[0]
    for div in content.find_all("span", {'class':'copyright_entry'}): 
        div.decompose()
    for div in content.find_all('div', attrs={'style': 'line-height:12px;padding:35px 0 5px'}):
        div.decompose()
    for comments in content.findAll(text=lambda text:isinstance(text, Comment)):
        comments.extract()
    
    # 이미지
    source = soup.find_all("div", attrs={'style': 'text-align:center'})
    for div in source:
        newImg = BeautifulSoup(f"<p>{tistory.post_image(div.find('img').get('src'))}</p>", 'html.parser')
        div.replaceWith(newImg)

    # 제목
    body = soup.select('.hentry')[0].get_text('\n\n')[:-20]
    title = soup.select('.entry-title a')[0].text
    if title[:2] == '20':
        title = body.split('\n', 1)[0]
    title = f"{s[:10]} {title}"

    return {
        'title': title,
        'body': body,
        'content': content
    }


if __name__ == "__main__":
    tistory = Tistory()

    for i in range(150, 0, -1):
        post = getEgloosPost(i, tistory)
        time.sleep(1)
        tistory.post_write(title=post['title'], content=post['content'])
        time.sleep(1)