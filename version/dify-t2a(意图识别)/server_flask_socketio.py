# -*- coding: utf-8 -*-
from threading import Thread
from flask import Flask, render_template, request
from flask_socketio import SocketIO, disconnect
from T2A_Stream import T2A_Stream
import base64
import json
from dify import Dify
import requests
from flask_cors import CORS

t2a_stream = T2A_Stream()
dify_receive = Dify()



def audio_text_template(audio, msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, qurey, message_id):
    data  = {
        "audio": audio,
        "msg": msg,
        "conversation_id": conversation_id,
        "role": role,
        "completion_tokens": completion_tokens,
        "prompt_tokens": prompt_tokens,
        "total_tokens": total_tokens,
        "qurey": qurey,
        "message_id": message_id,
    }
    json_data = json.dumps(data, ensure_ascii=False)
    return json_data
    
def audio_template(audio):
    data  = {
        "audio": audio,
    }

    json_data = json.dumps(data, ensure_ascii=False)
    return json_data


def receive_dify_msg(qurey, conversation_id="", role="", userid=""):   
    """
    input: qurey 前端发送的消息
    output: dify处理之后的消息，会话id
    """
    response, role = dify_receive.get_response_message(qurey, conversation_id, role , userid)
    msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, message_id = dify_receive.handle_sse_response(response, role)
    return msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, message_id


def handler(send, disconnect, message):
    
    # 这个函数会为每个客户端连接创建一个任务
    if message.get("userid"):
        userid = message.get("userid")
    else: 
        send('response',"未找得到userid键", room=online_users[userid])

    if message.get("qurey"):
        qurey = message.get("qurey")
    else: 
        send('response',"未找得到qurey键", room=online_users[userid])

    if message.get("role"):
        role = message.get("role")
    else: 
        send('response',"未找得到role键", room=online_users[userid])

    # 处理客户端发送的消息
    # dify处理
    if message.get("conversation_id"):
        conversation_id = message.get("conversation_id")
        msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, message_id = receive_dify_msg(qurey, conversation_id, role, userid)
    else:
        msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, message_id = receive_dify_msg(qurey, role=role, userid=userid)
        print("receive_dify_message:", msg, conversation_id, role)

    audio_chunk_iterator = t2a_stream.call_tts_stream(msg, role)
    audio_1 = b""
    chunk_num = 0
    try: 
        for chunk in audio_chunk_iterator:
            if chunk is not None:
                if  chunk!="":
                    decoded_hex = bytes.fromhex(chunk)
                    chunk_num += 1
                    if chunk_num<=2:
                        audio_1 += decoded_hex
                    if chunk_num==2:
                        # 将二进制数据转化为base64
                        base64_audio = base64.b64encode(audio_1).decode('utf-8')
                        response = audio_text_template(base64_audio, msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, qurey, message_id)
                        send('response',response, room=online_users[userid])   
                        
                    if chunk_num>2:

                        base64_audio = base64.b64encode(decoded_hex).decode('utf-8')
                        response = audio_template(base64_audio)
                        send('response',response, room=online_users[userid])
                elif chunk=="":
                    response = audio_template("over")
                    send('response',response, room=online_users[userid])
        if audio_1 == b"":
            response = audio_template("over")
            send('response',response, room=online_users[userid])
        
        print("<==========一次转换结束=========>")
        # 断开连接
        del online_users[userid]
        
    except requests.exceptions.ProxyError:
        # 将错误日志写入本地文件
        with open('nohup.out', 'a') as f:
            # 获取当前时间
            import time
            localtime = time.localtime()
            # 格式化时间
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            # 写入日志文件
            f.write(f"<==========audio process error:{format_time}==========>")
            print(f"<==========audio process error:{format_time}==========>")
        response = audio_template("error")
        send('response',response, room=online_users[userid])
        
# 将用户加入在线用户列表
online_users = {}

app = Flask(__name__)
# 允许跨域
CORS(app)
socketio = SocketIO(app, async_mode='threading', logger=True, engineio_logger=True, cors_allowed_origins="*")  # 添加 logger 参数

@app.route('/')
def index():
    return "连接成功"


@socketio.on('message')
def handle_message(message):
    print("<===========一个请求==========>")
    # 客户端连接后，将用户加入在线用户列表
    if message.get("userid"):
        userid = message.get("userid")
        if userid not in online_users:
            online_users[userid] = request.sid

    print("<====online_users=====>:",online_users)
    print("<=======userid========>:",userid)
    print(f"<==========={message}==========>")
    send = socketio.emit
    handler(send, disconnect, message)
    # Thread(target=handler, args=(send, disconnect, message)).start()

if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8765
    socketio.run(app, host=host, port=port, debug=True)  # 使用 socketio.run 替代 app.run
 