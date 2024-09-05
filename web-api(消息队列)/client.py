import socket
import json

# 定义发送消息的函数
def send_message(content):
    # 服务器地址和端口
    server_address = ('localhost', 8765)

    # 创建一个TCP/IP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到服务器
        client_socket.connect(server_address)

        # 发送消息到服务器
        client_socket.sendall(content.encode('utf-8'))

        # 接收服务器回应的消息
        for response in client_socket.recv(409600).decode('utf-8'):

            # 输出服务器回应的消息
            print("Received response from server:", type(response))

    finally:
        # 关闭套接字连接
        client_socket.close()

# 构造消息内容
content = {
    "userid": "xiaoxiaohong",
    "qurey": "如何充值？",
    "conversation_id": "",
    "role": "zh-CN-YunjianNeural",
}
content_json = json.dumps(content)

# 发送消息
send_message(content_json)
