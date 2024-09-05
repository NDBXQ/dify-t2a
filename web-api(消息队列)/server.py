import asyncio
import websockets
from T2A_Stream import T2A_Stream
import base64
import json
from dify import Dify
import asyncio
import socket
import threading
import ssl

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

# 创建一个TCP/IP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 设置服务器地址和端口
server_address = ('0.0.0.0', 8765)
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)

# 监听连接，最多允许5个客户端连接
server_socket.listen(5)

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


def handler(client_socket, message):
    # 这个函数会为每个客户端连接创建一个任务

    # message = json.loads(message)
    print(f"message=====>{message}")

    if message.get("userid"):
        userid = message.get("userid")
    else: 
        client_socket.sendall("未找得到userid键")

    if message.get("qurey"):
        qurey = message.get("qurey")
    else: 
        client_socket.sendall("未找得到qurey键")

    if message.get("role"):
        role = message.get("role")
    else: 
        client_socket.sendall("未找得到role键")

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
                        # base64_audio = "data:audio/mp3;base64," + base64_audio
                        response = audio_text_template(base64_audio, msg, conversation_id, role, completion_tokens, prompt_tokens, total_tokens, qurey, message_id)
                        # 将json字符串转为二进制数据
                        response = response.encode('utf-8')
                        client_socket.sendall(response)   
                        
                    if chunk_num>2:

                        base64_audio = base64.b64encode(decoded_hex).decode('utf-8')
                        response = audio_template(base64_audio)
                        response = response.encode('utf-8')
                        client_socket.sendall(response)
                elif chunk=="":
                    response = audio_template("over")
                    response = response.encode('utf-8')
                    client_socket.sendall(response)
        response = audio_template("over")
        response = response.encode('utf-8')
        client_socket.sendall(response)
    except BrokenPipeError:
        # 如果客户端断开连接，关闭客户端套接字
        print("客户端断开连接")
        client_socket.close()


# 处理客户端请求的函数
def handle_client_connection(client_socket, client_address):
    print('Accepted connection from', client_address)

    message_byte = b''

    while True:
        # 接收客户端发送的数据
        try:
            data = client_socket.recv(1024)
            message_byte += data
            print("receive data:", type(message_byte))
        except BlockingIOError:

            break

    try:
        message = message_byte.decode('utf-8')
        print("message=====>",message)
        # print("message type=====>",type(message))
            # 提取 body 部分的信息（如果有的话）
        # body = message.split('\r\n\r\n')[1]
        # print("Request Body:", body)
        # print("===============================")

        # message = json.loads(message)
        handler(client_socket, message)
        # 处理连接被重置的情况
        print("Connection with {} reset by peer".format(client_address))
        client_socket.close()

    except BrokenPipeError:
        # 如果客户端断开连接，关闭客户端套接字
        print("客户端断开连接")
        client_socket.close()
    
    # print("receive data:", type(data))

# 接受客户端连接，并创建新线程处理每个客户端请求
while True:
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()
    ssl_socket = context.wrap_socket(client_socket, server_side=True)
    client_socket.setblocking(False)
    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
    client_thread.start()
