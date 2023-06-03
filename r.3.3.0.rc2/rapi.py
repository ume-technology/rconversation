# -*- coding: utf-8 -*-
# !/user/bin/env python3
# todo-task: 封装API
import flask
from flask import Flask, jsonify, request
from zhconv import convert
import re
import json
import requests
import secrets

app = Flask(__name__)


# todo-note:该方法要第一步就调用
def translatetochcha(text):
    try:
        textchn = convert(text, 'zh-cn')
        textchn = textchn.replace(' ', '')
        cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  # 匹配不是中文、大小写、数字的其他字符
        textchn_clean = cop.sub('', textchn)
        res = {'res': '如果用户输入的数据在预处理接阶段出现问题，那么将会把这句话送入模型'} if not textchn_clean else {'res': textchn_clean}
        return res
    except:
        res = {'res': '如果用户输入的数据在预处理接阶段出现问题，那么将会把这句话送入模型'}
        return res


def post(url, data=None):
    data = json.dumps(data, ensure_ascii=False)
    data = data.encode(encoding="utf-8")
    r = requests.post(url=url, data=data)
    r = json.loads(r.text)
    return r


@app.route('/c_api', methods=['POST'])
def final_core_response():
    """
    input params:
        sender:
        text:
        metadata
    :return:
    """
    # user_idx = secrets.token_urlsafe(16) # random sender

    # todo get get function
    # sender = request.values.get('sender')
    # text = request.values.get('text')
    # metadata = request.values.get('metadata')

    # todo get post function
    sender = request.json.get('sender')
    text = request.json.get('text')
    metadata = request.json.get('metadata')

    text = translatetochcha(text)['res']

    data2intent = {"text": text}
    data2intent = json.dumps(data2intent, ensure_ascii=False)
    data2intent = data2intent.encode(encoding="utf-8")

    r_intent = requests.post("http://192.168.1.232:5005/model/parse", data2intent)
    r_intent = json.loads(r_intent.text)
    text = r_intent['text']
    intent = r_intent['intent']['name']
    entities = r_intent['entities']
    tell_codes = []
    if entities:
        for _ in entities:
            if _['entity'] == 'code':
                tell_codes.append(_['value'])
    print(tell_codes)

    print('To ensure intent:', intent)
    url_core = 'http://192.168.1.232:5005/webhooks/inputWithGoodsBox/webhook'
    if intent == 'intent_queorders':
        # 帮我查订单编号：如果用户输入的数据在预处理接阶段出现问题，那么将会把这句话送入模型
        if "+" in text:
            text = '查电话号码：' + text
        elif text.isalnum():
            text = '查订单编号:' + text

        print('==:', text)
        data2reply = {"sender": sender, "text": text, "metadata": metadata}
        final_res = {
            # 'allintents': allintents_kv,
            # 'max-conf': json.loads(rintent.text),
            'clean_text': text,
            'maybe-response': post(url_core, data2reply),
            'reg_codes': tell_codes
        }
        return jsonify(final_res)

    print('--:', text)
    data2reply = {"sender": sender, "text": text, "metadata": metadata}
    final_res = {
        # 'allintents': allintents_kv,
        # 'max-conf': json.loads(rintent.text),
        'clean_text': text,
        'maybe-response': post(url_core, data2reply),
        'reg_codes': tell_codes
    }
    return jsonify(final_res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5003)
