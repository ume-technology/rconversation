import json
import secrets
import requests


def post(url, data=None):
    data = json.dumps(data, ensure_ascii=False)
    data = data.encode(encoding="utf-8")
    r = requests.post(url=url, data=data)
    r = json.loads(r.text)
    return r


url_core = "http://localhost:5005/webhooks/rest/webhook"  #
url_intents = "http://localhost:5005/model/parse"  # intent

while True:
    # message = input("Your input ->  ")
    message = '你好'

    # data = {"text": "我想买一个手电筒，你们这里有吗"}
    data2intent = {"text": message}
    data2intent = json.dumps(data2intent, ensure_ascii=False)
    data2intent = data2intent.encode(encoding="utf-8")
    r = requests.post(url=url_intents, data=data2intent)
    print(json.loads(r.text))

    # print(type(secrets.token_urlsafe(16)))
    data2reply = {"sender": secrets.token_urlsafe(16), "message": message}
    # print(type(data2reply))
    print(post(url_core, data2reply))
