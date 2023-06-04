# code reference from https://hackmd.io/@littlehsun/linechatbot

# coding: utf-8
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from private_info import Private_info

from model import *
import random

#line token
channel_access_token = Private_info.line_channel_access_token
channel_secret = Private_info.line_channel_secret
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get event id
    id = ''
    if event.source.type == 'user':
        id = event.source.user_id
    elif event.source.type == 'group':
        id = event.source.group_id
    elif event.source.type == 'room':
        id = event.source.room_id
    #echo
    msg_r= event.message.text   # 傳入的訊息
    msgs = []   # 要回覆的訊息（上限 5 則)
    # 判斷訊息是否為需回覆的
    if msg_r.strip() == "出題":
        sub = ran_sub()
        ques = ran_ques(sub)
        user_ques[id] = ques
        msg = sub.name + '\n' + str(ques).strip()
        message = TextSendMessage(text=msg)
        msgs.append(message)
    elif msg_r.strip().upper() in ['A', 'B', 'C', 'D']:
        msg = ''
        if id in user_ques:
            if user_ques[id].is_correct(msg_r):
                msg = '答對了！'
            else:
                msg = f'答錯囉～\n正確答案為({user_ques[id].get_ans()})'
            user_ques.pop(id)
        msgs.append(TextSendMessage(text=msg))
    elif msg_r.strip() == "指令":
        with open('command.txt','r') as f:
            txt = f.read()
            msgs.append(TextSendMessage(text=txt))
    elif msg_r.strip() == "考科":
        if subjects:
            msg = '目前的考科有：\n'
            for i, subject in enumerate(subjects.values()):
                msg += f'\n{i+1}. {subject.name}'
                year = '    '
                for y in subject.exams:
                    year += f'{y} '
                msg += '\n' + year
            msgs.append(TextSendMessage(text= msg.strip()))
    if msgs:
        line_bot_api.reply_message(event.reply_token,msgs)

user_ques = {}
# load 題庫
subjects = {}
with open('Subjects.json','r') as f:
    data = f.read()
    subject_list = json_to_subject_list(data)
    for subject in subject_list:
        subjects[subject.name] = subject

# 隨機選考科
def ran_sub():
    if not subjects:
        return 
    else:
        ran_sub = random.choice(list(subjects.values()))
        return ran_sub
# 隨機選題
def ran_ques(subject: Subject):
    ran_exam = random.choice(list(subject.exams.values()))
    ran_q = random.choice(list(ran_exam.questions.values()))
    return ran_q

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)